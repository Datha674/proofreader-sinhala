# -*- coding: utf-8 -*-
"""
CorrectionsDB — shared by the client engine AND the proxy server.

Thread-safe read/write of a corrections JSON file. Self-learning:
  * captures human corrections (manual edits),
  * promotes frequently-seen + confirmed ones to "precheck" (instant local fix),
  * injects the top corrections into the Gemini prompt as few-shot examples.

The proxy server uses an identical copy of this file with a different DB path.
"""

import os
import json
import threading
import unicodedata
from datetime import datetime

EMPTY_DB = {
    "version": 2,
    "created": "",
    "last_updated": "",
    "corrections": [],
}


class CorrectionsDB:
    def __init__(self, db_path):
        self.db_path = db_path
        self.lock = threading.Lock()
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self.data = self._load()
        if not self.data.get("created"):
            self.data["created"] = datetime.now().isoformat()
            self._save()

    # ----- persistence ---------------------------------------------------
    def _load(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "corrections" in data:
                    return data
            except Exception:
                pass
        db = dict(EMPTY_DB)
        db["corrections"] = []
        db["created"] = datetime.now().isoformat()
        return db

    def _save(self):
        self.data["last_updated"] = datetime.now().isoformat()
        tmp = self.db_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.db_path)  # atomic on Windows + POSIX

    @staticmethod
    def _norm(text):
        return unicodedata.normalize("NFC", (text or "").strip())

    # ----- recording -----------------------------------------------------
    def record_correction(self, wrong, correct, error_type="spelling",
                          context="", added_by="unknown", source="manual",
                          precheck_threshold=5):
        wrong = self._norm(wrong)
        correct = self._norm(correct)
        if not wrong or not correct or wrong == correct:
            return {"status": "skipped"}

        with self.lock:
            existing = next(
                (c for c in self.data["corrections"] if c["wrong"] == wrong), None
            )
            if existing:
                existing["count"] += 1
                existing["last_seen"] = datetime.now().isoformat()
                existing["correct"] = correct
                existing["confidence"] = min(
                    0.99, existing.get("confidence", 0.75) + 0.05
                )
                if existing["count"] >= precheck_threshold and existing.get("confirmed"):
                    existing["mode"] = "precheck"
                status = "updated"
            else:
                new_id = "c%05d" % (len(self.data["corrections"]) + 1)
                self.data["corrections"].append({
                    "id": new_id,
                    "wrong": wrong,
                    "correct": correct,
                    "type": error_type,
                    "count": 1,
                    "confidence": 0.75,
                    "mode": "inject_only",
                    "context": context,
                    "added_by": added_by,
                    "source": source,
                    "confirmed": False,
                    "added_date": datetime.now().isoformat(),
                    "last_seen": datetime.now().isoformat(),
                })
                status = "added"
            self._save()
        return {"status": status, "wrong": wrong, "correct": correct}

    # ----- moderation ----------------------------------------------------
    def set_mode(self, correction_id, mode, confirm=False):
        valid = {"precheck", "inject_only", "disabled"}
        if mode not in valid:
            return False
        with self.lock:
            entry = next(
                (c for c in self.data["corrections"] if c["id"] == correction_id), None
            )
            if entry:
                entry["mode"] = mode
                if confirm or mode == "precheck":
                    entry["confirmed"] = True
                self._save()
                return True
        return False

    def confirm(self, correction_id):
        with self.lock:
            entry = next(
                (c for c in self.data["corrections"] if c["id"] == correction_id), None
            )
            if entry:
                entry["confirmed"] = True
                self._save()
                return True
        return False

    def delete(self, correction_id):
        with self.lock:
            before = len(self.data["corrections"])
            self.data["corrections"] = [
                c for c in self.data["corrections"] if c["id"] != correction_id
            ]
            changed = len(self.data["corrections"]) < before
            if changed:
                self._save()
            return changed

    # ----- consumption ---------------------------------------------------
    def get_precheck_map(self):
        """Return {wrong: correct} for instant local fixing."""
        return {
            c["wrong"]: c["correct"]
            for c in self.data["corrections"]
            if c["mode"] == "precheck" and c.get("confirmed")
        }

    def get_inject_examples(self, top_n=40):
        """Top N corrections for few-shot prompt injection."""
        injectable = [
            c for c in self.data["corrections"]
            if c["mode"] in ("precheck", "inject_only")
        ]
        injectable.sort(key=lambda x: x["count"], reverse=True)
        return injectable[:top_n]

    def export_for_injection(self, top_n=40):
        """Formatted block appended to the Gemini system prompt."""
        examples = self.get_inject_examples(top_n)
        if not examples:
            return ""
        lines = [
            '  "%s" → "%s" (%s, verified %dx)'
            % (e["wrong"], e["correct"], e["type"], e["count"])
            for e in examples
        ]
        return (
            "\n\n=== HUMAN-VERIFIED SINHALA CORRECTIONS ===\n"
            "Confirmed errors from human reviewers — flag with confidence 1.0:\n"
            + "\n".join(lines)
            + "\n=== END VERIFIED CORRECTIONS ==="
        )

    # ----- reporting -----------------------------------------------------
    def get_stats(self):
        corrections = self.data.get("corrections", [])
        return {
            "total": len(corrections),
            "precheck": sum(1 for c in corrections if c["mode"] == "precheck"),
            "inject": sum(1 for c in corrections if c["mode"] == "inject_only"),
            "disabled": sum(1 for c in corrections if c["mode"] == "disabled"),
            "confirmed": sum(1 for c in corrections if c.get("confirmed")),
            "top_errors": sorted(
                corrections, key=lambda x: x["count"], reverse=True
            )[:10],
        }

    def search(self, query):
        q = (query or "").strip().lower()
        if not q:
            return list(self.data["corrections"])
        return [
            c for c in self.data["corrections"]
            if q in c.get("wrong", "").lower()
            or q in c.get("correct", "").lower()
            or q in c.get("type", "").lower()
        ]
