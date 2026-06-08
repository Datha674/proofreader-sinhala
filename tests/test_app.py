# -*- coding: utf-8 -*-
"""
Offline (no network) tests for the Gemini + LAN-proxy + self-learning client.

Covers: config, CorrectionsDB (self-learning), and the orchestrator's
direct/lan_proxy/no-key paths with a mocked engine. LIVE Gemini tests are in
tests/test_engine.py.

Run:  python tests/test_app.py     (PYTHONUTF8=1 recommended on Windows)
"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config import Config, DEFAULT_CONFIG
from engine.corrections_db import CorrectionsDB
from engine.proofreader import SinhalaProofreader
from engine.gemini_engine import GeminiError

_PASS = _FAIL = 0


def check(name, cond):
    global _PASS, _FAIL
    if cond:
        _PASS += 1; print("  PASS  " + name)
    else:
        _FAIL += 1; print("  FAIL  " + name)


class FakeConfig:
    def __init__(self, **o):
        self.data = DEFAULT_CONFIG.copy(); self.data.update(o)
    def get(self, k, d=None): return self.data.get(k, d)
    def set(self, k, v): self.data[k] = v
    def save(self): return True
    def get_transport(self): return self.data.get("api_transport", "rest")
    def resolve_api_key(self): return self.data.get("gemini_api_key", "").strip()
    def has_api_key(self): return bool(self.resolve_api_key())


class MockEngine:
    def proofread(self, text, corrections_db=None, on_progress=None):
        self.saw_db = corrections_db
        return {"mode": "online", "ok": True, "error_found": True,
                "errors": [{"original": "ප්‍රශ්ණ", "correction": "ප්‍රශ්න",
                            "type": "spelling", "confidence": 0.95,
                            "start": text.find("ප්‍රශ්ණ"), "end": text.find("ප්‍රශ්ණ") + 6}],
                "corrected_text": text.replace("ප්‍රශ්ණ", "ප්‍රශ්න"),
                "original": text, "original_text": text, "pre_fixed_count": 0,
                "summary_si": "ok", "summary_en": "ok",
                "stats": {"total_words": len(text.split()), "errors_found": 1,
                          "spell_errors": 1, "grammar_errors": 0,
                          "encoding_errors": 0, "pre_fixed": 0}}


def run():
    # ===== TEST 1 — Corrections DB dedup + count =====
    tmp = os.path.join(tempfile.gettempdir(), "test_corrections.json")
    if os.path.exists(tmp):
        os.remove(tmp)
    db = CorrectionsDB(tmp)
    db.record_correction("නෑහැ", "නැහැ", "spelling", "", "test", "manual")
    db.record_correction("නෑහැ", "නැහැ", "spelling", "", "test", "manual")
    check("TEST 1 dedup -> total 1", db.get_stats()["total"] == 1)
    check("TEST 1 count incremented to 2", db.data["corrections"][0]["count"] == 2)

    # ===== TEST 2 — Pre-check layer =====
    db.set_mode("c00001", "precheck", confirm=True)
    pmap = db.get_precheck_map()
    check("TEST 2 precheck map has entry", "නෑහැ" in pmap)
    t = "ඔහු නෑහැ කීවා"
    for w, c in pmap.items():
        t = t.replace(w, c)
    check("TEST 2 precheck applied", "නැහැ" in t)
    check("inject block built", "HUMAN-VERIFIED" in db.export_for_injection(5))

    # ===== Orchestrator — direct mode, no key -> error result =====
    pr = SinhalaProofreader(FakeConfig(connection_mode="direct"))
    r = pr.proofread("මම නෑහැ කියනවා")
    check("direct no-key -> ok=False", r["ok"] is False and r["error_kind"] == "no_key")

    # ===== Orchestrator — direct mode with mock engine, passes corrections_db =====
    pr2 = SinhalaProofreader(FakeConfig(connection_mode="direct",
                                        gemini_api_key="AIza" + "x" * 35))
    mock = MockEngine()
    pr2.engine = mock
    pr2._refresh_engine = lambda: None
    pr2.mode = "direct"
    r = pr2.proofread("ඔහු ප්‍රශ්ණ ඇසීය")
    check("direct mock ok=True", r["ok"] is True)
    check("corrections_db forwarded to engine", mock.saw_db is pr2.corrections_db)
    check("direct mock corrected applied", "ප්‍රශ්න" in r["corrected_text"])

    # ===== Orchestrator — lan_proxy mode selects LanProxyProofreader =====
    pr3 = SinhalaProofreader(FakeConfig(connection_mode="lan_proxy",
                                        proxy_url="http://127.0.0.1:1"))
    check("lan mode selected", pr3.mode == "lan_proxy"
          and type(pr3.engine).__name__ == "LanProxyProofreader")
    r = pr3.proofread("මම යනවා")  # proxy down -> graceful error result
    check("lan proxy-down -> ok=False network", r["ok"] is False and r["error_kind"] == "network")

    # ===== Orchestrator — engine raising GeminiError -> error result =====
    class Boom:
        def proofread(self, text, corrections_db=None, on_progress=None):
            raise GeminiError("දෝෂය", "boom", kind="quota")
    pr2.engine = Boom()
    r = pr2.proofread("මම යනවා")
    check("engine error -> ok=False quota", r["ok"] is False and r["error_kind"] == "quota")

    # ===== Config =====
    check("default connection_mode direct", FakeConfig().get("connection_mode") == "direct")
    check("default transport rest", FakeConfig().get_transport() == "rest")
    check("modern key accepted", Config.validate_api_key_format("AQ.Ab8RN6KiP_" + "x" * 12))
    check("short key rejected", not Config.validate_api_key_format("AQ.1"))

    os.remove(tmp)
    print("\n%d passed, %d failed" % (_PASS, _FAIL))
    return _FAIL == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
