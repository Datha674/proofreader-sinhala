# -*- coding: utf-8 -*-
"""
test_engine.py — LIVE Gemini engine tests for the production prompt.

These call the real Gemini API, so they need a key. The key is taken from
(in order): the GEMINI_API_KEY environment variable, or the saved app config
(~/.sinhala_proofreader/config.json). If no key is available the tests SKIP
cleanly (exit 0) instead of failing.

Run:
    $env:GEMINI_API_KEY="AQ...."; python tests/test_engine.py
    # or simply, if you've saved a key in the app:
    python tests/test_engine.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Spacing between live calls to stay under free-tier requests-per-minute limits.
CALL_SPACING_SEC = 8
MAX_RETRIES = 3

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from config import Config
from engine.gemini_engine import GeminiProofreader, GeminiError


# (name, text, expectation) — expectation is "zero" or "nonzero" errors, and an
# optional required type for the flagged errors.
TESTS = [
    ("Test 1: colloquial + English (expect 0)",
     "මම software project deadline එකට වැඩ කරනවා. ගොඩක් වෙහෙසයි.", "zero", None),
    ("Test 2: real spelling errors (expect >=1 spelling)",
     "ලංකාවේ අද්‍යාපන ප්‍රශ්ණ ගොඩක් තිබේ.", "nonzero", "spelling"),
    ("Test 3: dative subject + involitive (expect 0)",
     "මට ගෙදර යන්න හිතුනා. ළමයාට සෙල්ලම් කරන්න ආසයි.", "zero", None),
    ("Test 4: valid reduplication (expect 0)",
     "ඔහු යන යන තැන් ගැන කිව්වා.", "zero", None),
    ("Test 5: repeated word (expect >=1 grammar)",
     "ඔහු ගෙදර ගෙදර ගියා.", "nonzero", "grammar"),
]


def _resolve_key():
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if key:
        return key, "AQ.flash-2.0"  # model decided below
    cfg = Config()
    return cfg.get_api_key().strip(), cfg.get("gemini_model", "gemini-2.0-flash")


def run():
    key, _ = _resolve_key()
    if not key:
        print("SKIP: no Gemini API key found (set GEMINI_API_KEY or save one in the app).")
        return True

    cfg = Config()
    model = cfg.get("gemini_model", "gemini-2.0-flash") if cfg.get_api_key() else "gemini-2.0-flash"
    print("Using model:", model)
    try:
        engine = GeminiProofreader(key, model)
    except GeminiError as exc:
        print("SKIP: could not init engine —", exc.message_en)
        return True

    passed = failed = 0
    for i, (name, text, expect, req_type) in enumerate(TESTS):
        if i:
            time.sleep(CALL_SPACING_SEC)  # pace calls to avoid 429 rate limits
        result = None
        for attempt in range(MAX_RETRIES):
            try:
                result = engine.proofread(text)
                break
            except GeminiError as exc:
                if exc.kind == "quota" and attempt < MAX_RETRIES - 1:
                    time.sleep(CALL_SPACING_SEC * (attempt + 2))  # backoff
                    continue
                print("  FAIL  %s  (API error: %s)" % (name, exc.message_en))
                failed += 1
                break
        if result is None:
            continue

        errors = result.get("errors", [])
        flagged = [e["original"] for e in errors]
        n = len(errors)

        if expect == "zero":
            ok = (n == 0)
        else:
            ok = (n >= 1)
            if ok and req_type:
                kinds = {e["type"] for e in errors}
                if req_type == "grammar":
                    ok = bool(kinds & {"grammar", "grammar_discord"})
                else:
                    ok = req_type in kinds

        print("  %s  %s  | errors=%d %s"
              % ("PASS" if ok else "FAIL", name, n, flagged))
        passed += ok
        failed += (not ok)

    print("\n%d passed, %d failed" % (passed, failed))
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
