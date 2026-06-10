# -*- coding: utf-8 -*-
"""
Tests for the SQLite-backed CorrectionsDB: JSON->SQLite migration + the full
public interface (which must behave identically to the old JSON version).

Run:  python tests/test_corrections_db.py     (PYTHONUTF8=1 on Windows)
"""

import os
import sys
import json
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from engine.corrections_db import CorrectionsDB

_PASS = _FAIL = 0


def check(name, cond):
    global _PASS, _FAIL
    if cond:
        _PASS += 1; print("  PASS  " + name)
    else:
        _FAIL += 1; print("  FAIL  " + name)


def main():
    tmp = tempfile.mkdtemp(prefix="corrdb_")
    try:
        json_path = os.path.join(tmp, "corrections.json")
        db_path = os.path.join(tmp, "corrections.db")

        old = {
            "version": 2,
            "created": "2025-01-01T00:00:00",
            "last_updated": "2025-02-02T00:00:00",
            "corrections": [
                {"id": "c00001", "wrong": "ජිවිතය", "correct": "ජීවිතය",
                 "type": "spelling", "count": 7, "confidence": 0.95,
                 "mode": "precheck", "confirmed": True, "added_by": "admin",
                 "source": "manual", "added_date": "2025-01-01T00:00:00",
                 "last_seen": "2025-01-05T00:00:00"},
                {"id": "c00002", "wrong": "ප්‍රශ්ණ", "correct": "ප්‍රශ්න",
                 "type": "spelling", "count": 3, "confidence": 0.80,
                 "mode": "inject_only", "confirmed": False},
                {"id": "c00003", "wrong": "තීරන", "correct": "තීරණ",
                 "type": "spelling", "count": 1, "confidence": 0.75,
                 "mode": "inject_only", "confirmed": False},
            ],
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(old, f, ensure_ascii=False, indent=2)

        # ---- MIGRATION ----
        db = CorrectionsDB(db_path)

        check("all 3 entries migrated (total=3)", db.get_stats()["total"] == 3)
        check("db file created", os.path.exists(db_path))
        check("old json renamed to .bak", not os.path.exists(json_path)
              and os.path.exists(json_path + ".bak"))
        check("created date preserved from json", db.data["created"] == "2025-01-01T00:00:00")

        pm = db.get_precheck_map()
        check("precheck map size = 1", len(pm) == 1)
        check("precheck map maps ජිවිතය -> ජීවිතය", pm.get("ජිවිතය") == "ජීවිතය")

        # confirmed flag round-trips as a real bool
        c1 = next(c for c in db.data["corrections"] if c["id"] == "c00001")
        check("confirmed migrated as bool True", c1["confirmed"] is True)
        check("count migrated as int", c1["count"] == 7)

        # ---- LIVE INTERFACE ----
        r = db.record_correction("අධ්‍යයනය", "අධ්‍යාපනය", "spelling")
        check("record new -> added", r["status"] == "added")
        check("total now 4", db.get_stats()["total"] == 4)

        r2 = db.record_correction("තීරන", "තීරණ", "spelling")
        check("record existing -> updated", r2["status"] == "updated")
        c3 = next(c for c in db.data["corrections"] if c["wrong"] == "තීරන")
        check("existing count incremented 1->2", c3["count"] == 2)

        r3 = db.record_correction("සම", "සම", "spelling")
        check("no-op (wrong==correct) -> skipped", r3["status"] == "skipped")

        # moderation
        check("confirm() returns True", db.confirm("c00002") is True)
        check("confirm() unknown id -> False", db.confirm("zzz") is False)
        check("set_mode precheck auto-confirms",
              db.set_mode("c00002", "precheck") is True
              and db.get_precheck_map().get("ප්‍රශ්ණ") == "ප්‍රශ්න")
        check("set_mode invalid mode -> False", db.set_mode("c00002", "bogus") is False)

        # search + injection
        check("search('තීර') finds තීරන", any(c["wrong"] == "තීරන" for c in db.search("තීර")))
        check("search('') returns all", len(db.search("")) == db.get_stats()["total"])
        block = db.export_for_injection(40)
        check("export_for_injection is non-empty str", isinstance(block, str) and "VERIFIED" in block)

        # delete
        check("delete() returns True", db.delete("c00003") is True)
        check("delete() unknown id -> False", db.delete("nope") is False)
        total_after_delete = db.get_stats()["total"]

        # ---- PERSISTENCE / NO RE-MIGRATION ----
        db2 = CorrectionsDB(db_path)
        check("reopened db persists rows", db2.get_stats()["total"] == total_after_delete)
        check("no json left to re-migrate", not os.path.exists(json_path))

        print("\n%d passed, %d failed" % (_PASS, _FAIL))
        print("RESULT:", "PASS" if _FAIL == 0 else "FAIL")
        return 0 if _FAIL == 0 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
