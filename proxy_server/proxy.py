# -*- coding: utf-8 -*-
"""
proxy.py — Sinhala Proofreader Control PC proxy server.

LAN clients POST text here; this server calls Gemini (the only machine that needs
internet) with the shared self-learning corrections DB applied, and returns
structured results. Also serves an /admin web panel.

Run:  python proxy.py     (or START_PROXY.bat)
"""

import os
import re
import csv
import json
import time
import threading
import unicodedata
from datetime import datetime

from flask import Flask, request, jsonify

import google.generativeai as genai

from config_proxy import (
    ProxyConfig, BASE_DIR, DATA_DIR, CORRECTIONS_PATH, LOG_PATH,
)
from corrections_db import CorrectionsDB
from usage_logger import UsageLogger
from admin_panel import admin_bp

CONFIDENCE_THRESHOLD = 0.75
MAX_ERRORS = 10
_VALID_TYPES = ("spelling", "grammar", "grammar_discord", "encoding_error")


class ProxyState:
    """Shared, hot-reloadable server state used by routes + admin panel."""

    def __init__(self):
        self.cfg = ProxyConfig()
        self.db = CorrectionsDB(CORRECTIONS_PATH)
        self.logger = UsageLogger(LOG_PATH)
        self.prompt = self.cfg.get_prompt()
        self.model = None
        self.model_error = ""
        self.sem = threading.Semaphore(int(self.cfg.get("max_concurrent", 4)))
        self.reload_model()

    def reload_model(self):
        """(Re)configure the Gemini client from the current key + model."""
        key = self.cfg.get_api_key()
        self.prompt = self.cfg.get_prompt()
        self.sem = threading.Semaphore(int(self.cfg.get("max_concurrent", 4)))
        if not key:
            self.model = None
            self.model_error = "No API key set (edit api_key.txt or use the admin panel)"
            return
        try:
            genai.configure(api_key=key, transport=self.cfg.get("api_transport", "rest"))
            self.model = genai.GenerativeModel(self.cfg.get("model", "gemini-2.0-flash"))
            self.model_error = ""
        except Exception as e:
            self.model = None
            self.model_error = str(e)

    # ----- core proofreading --------------------------------------------
    def proofread(self, text):
        text = unicodedata.normalize("NFC", (text or "").strip())
        if not text:
            return {"errors": [], "corrected_text": "", "summary_si": "",
                    "summary_en": "", "pre_fixed_count": 0,
                    "stats": _stats(text, [])}
        if self.model is None:
            raise RuntimeError(self.model_error or "Gemini model not ready")

        # LAYER 1 — pre-check from the human corrections DB.
        pre_fixed = []
        for wrong, correct in self.db.get_precheck_map().items():
            if wrong and wrong in text:
                text = text.replace(wrong, correct)
                pre_fixed.append({
                    "original": wrong, "correction": correct, "type": "spelling",
                    "confidence": 1.0, "source": "human_db",
                    "explanation_si": "මිනිස් සමාලෝචකයෙකු විසින් නිවැරදි කළ දෝෂයකි",
                    "explanation_en": "Previously corrected by a human reviewer",
                })

        # LAYER 2 — inject top corrections + protect English.
        inject_block = self.db.export_for_injection(int(self.cfg.get("inject_top_n", 40)))
        english = sorted(set(re.findall(r"[A-Za-z]+", text)))
        english_note = ""
        if english:
            english_note = ("\n\nCRITICAL: These English words appear in the text. "
                            "They are ALL valid. NEVER flag them: " + ", ".join(english))
        prompt = self.prompt + inject_block + english_note + "\n\nSinhala text to proofread:\n" + text

        # LAYER 3 — Gemini.
        gen_config = genai.types.GenerationConfig(
            temperature=0.05, response_mime_type="application/json"
        )
        with self.sem:
            resp = self.model.generate_content(prompt, generation_config=gen_config)
        data = _parse_json(getattr(resp, "text", "") or "", text)

        raw_errors = data.get("errors")
        if raw_errors is None:
            raw_errors = data.get("corrections")
        raw_errors = raw_errors or []
        gemini_errors = []
        for e in raw_errors:
            if not isinstance(e, dict):
                continue
            conf = _clamp(e.get("confidence", 1.0))
            if conf < CONFIDENCE_THRESHOLD:
                continue
            etype = e.get("type", "spelling")
            if etype not in _VALID_TYPES:
                etype = "spelling"
            gemini_errors.append({
                "original": str(e.get("original", "")),
                "correction": str(e.get("correction", "")),
                "type": etype,
                "explanation_si": str(e.get("explanation_si", "")),
                "explanation_en": str(e.get("explanation_en", "")),
                "confidence": conf,
            })

        all_errors = pre_fixed + gemini_errors
        all_errors.sort(key=lambda x: x.get("confidence", 1), reverse=True)
        all_errors = all_errors[:MAX_ERRORS]

        return {
            "errors": all_errors,
            "corrected_text": str(data.get("corrected_text", text)) or text,
            "summary_si": str(data.get("summary_si", "")),
            "summary_en": str(data.get("summary_en", "")),
            "pre_fixed_count": len(pre_fixed),
            "stats": _stats(text, all_errors, len(pre_fixed)),
        }


# ----- helpers -----------------------------------------------------------
def _clamp(v):
    try:
        return max(0.0, min(1.0, float(v)))
    except (TypeError, ValueError):
        return 0.8


def _stats(text, errors, pre_fixed=0):
    return {
        "total_words": len(text.split()),
        "errors_found": len(errors),
        "spell_errors": sum(1 for e in errors if e.get("type") == "spelling"),
        "grammar_errors": sum(1 for e in errors if e.get("type") in ("grammar", "grammar_discord")),
        "encoding_errors": sum(1 for e in errors if e.get("type") == "encoding_error"),
        "pre_fixed": pre_fixed,
    }


def _parse_json(raw, fallback_text):
    cleaned = raw.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except ValueError:
        pass
    m = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except ValueError:
            pass
    return {"errors": [], "corrected_text": fallback_text,
            "summary_si": "ප්‍රතිචාරය විග්‍රහ කළ නොහැකි විය",
            "summary_en": "Could not parse the model response"}


# ----- Flask app ---------------------------------------------------------
STATE = ProxyState()

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = os.urandom(24)
app.config["STATE"] = STATE
app.register_blueprint(admin_bp, url_prefix="/admin")


@app.route("/status")
def status():
    return jsonify({
        "status": "online",
        "model": STATE.cfg.get("model"),
        "corrections_total": STATE.db.get_stats()["total"],
        "model_ready": STATE.model is not None,
        "version": 2,
    })


@app.route("/proofread", methods=["POST"])
def proofread():
    t0 = time.time()
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "")
    client_ip = request.remote_addr or "?"
    try:
        result = STATE.proofread(text)
        latency = int((time.time() - t0) * 1000)
        STATE.logger.log(client_ip, result["stats"]["total_words"],
                         result["stats"]["errors_found"],
                         result.get("pre_fixed_count", 0), latency, "ok")
        return jsonify(result)
    except Exception as e:
        latency = int((time.time() - t0) * 1000)
        STATE.logger.log(client_ip, len(text.split()), 0, 0, latency, "error")
        return jsonify({
            "errors": [], "corrected_text": text,
            "summary_si": "Proxy දෝෂයකි", "summary_en": "Proxy error: %s" % str(e)[:160],
            "pre_fixed_count": 0, "stats": _stats(text, [])
        }), 500


@app.route("/corrections")
def corrections():
    """Full corrections DB — used by clients to sync their local cache."""
    return jsonify(STATE.db.data)


@app.route("/record_correction", methods=["POST"])
def record_correction():
    payload = request.get_json(silent=True) or {}
    items = payload.get("corrections", [])
    saved = 0
    for c in items:
        res = STATE.db.record_correction(
            wrong=c.get("wrong", ""), correct=c.get("correct", ""),
            error_type=c.get("type", "spelling"),
            added_by=request.remote_addr or "client", source="client_edit",
            precheck_threshold=int(STATE.cfg.get("precheck_threshold", 5)),
        )
        if res.get("status") in ("added", "updated"):
            saved += 1
    return jsonify({"status": "ok", "saved": saved,
                    "total": STATE.db.get_stats()["total"]})


def main():
    host = STATE.cfg.get("host", "0.0.0.0")
    port = int(STATE.cfg.get("port", 8765))
    print("=" * 50)
    print(" Sinhala Proofreader Proxy Server")
    print(" Model:", STATE.cfg.get("model"),
          "| Key:", "SET" if STATE.cfg.get_api_key() else "MISSING")
    print(" Corrections:", STATE.db.get_stats()["total"])
    print(" Listening on http://%s:%d   (admin: /admin)" % (host, port))
    if STATE.model_error:
        print(" WARNING:", STATE.model_error)
    print("=" * 50)
    app.run(host=host, port=port, threaded=True)


if __name__ == "__main__":
    main()
