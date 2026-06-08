# -*- coding: utf-8 -*-
"""
build_dictionary.py — One-time dictionary builder for the Sinhala Proofreader.

Merges every available Sinhala word source into a single deduplicated, NFC-normalized,
native-Sinhala-only word list and writes:
    data/sinhala_dictionary.txt   (one word per line, UTF-8, sorted)
    data/common_errors.json       (hand-curated wrong -> correct map)

Run once during development:
    python build_dictionary.py

The generated data/ folder is what the app and the .exe bundle ship with, so the
source repositories are NOT needed at runtime.
"""

import os
import io
import json
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))

# Sinhala Unicode block + Zero Width Joiner (U+200D) used inside conjuncts.
SINHALA_LO = 0x0D80
SINHALA_HI = 0x0DFF
ZWJ = "‍"

# Source files (relative to this script).
REF_DICT = os.path.join(
    HERE,
    "Spelling-Corrector-and-Grammar-Checker-for-Sinhala",
    "DictionaryCreation",
    "sinhala_dictionary.txt",
)
LEXC_FILES = [
    os.path.join(HERE, "sinmorph", "lexicons", "nouns.txt"),
    os.path.join(HERE, "sinmorph", "lexicons", "nouns-cons.txt"),
    os.path.join(HERE, "sinmorph", "lexicons", "nouns-long-a.txt"),
    os.path.join(HERE, "sinmorph", "lexicons", "nouns-short-a.txt"),
]
TSV_FILE = os.path.join(
    HERE, "sinmorph", "lexicons", "lexicon.1entry-pos.sin-IPA-eng.tsv"
)

DATA_DIR = os.path.join(HERE, "data")
OUT_DICT = os.path.join(DATA_DIR, "sinhala_dictionary.txt")
OUT_ERRORS = os.path.join(DATA_DIR, "common_errors.json")


def is_native_sinhala(word):
    """True only if every character is in the Sinhala block (ZWJ allowed)."""
    if not word:
        return False
    for ch in word:
        if ch == ZWJ:
            continue
        if not (SINHALA_LO <= ord(ch) <= SINHALA_HI):
            return False
    return True


def clean(word):
    """NFC-normalize and strip surrounding whitespace/quotes/punctuation."""
    word = unicodedata.normalize("NFC", word.strip())
    # Drop wrapping quotes/parentheses that sometimes cling to tokens.
    word = word.strip("\"'()[]{}<>.,;:!?")
    return word


def read_lines(path):
    if not os.path.exists(path):
        print("  ! missing (skipped): %s" % path)
        return
    with io.open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield line


def collect():
    words = set()

    # 1) Reference inflected-form dictionary: one word per line.
    n = 0
    for line in read_lines(REF_DICT):
        w = clean(line)
        if is_native_sinhala(w):
            words.add(w)
            n += 1
    print("  reference dictionary: +%d" % n)

    # 2) LEXC lists: "WORD GrammarClass; ! phonetic \"gloss\"" -> first token.
    for path in LEXC_FILES:
        n = 0
        for line in read_lines(path):
            line = line.strip()
            if not line or line.startswith("!"):
                continue
            token = line.split()[0]
            w = clean(token)
            if is_native_sinhala(w):
                words.add(w)
                n += 1
        print("  %s: +%d" % (os.path.basename(path), n))

    # 3) TSV lexicon: column 1 is the Sinhala word.
    n = 0
    for line in read_lines(TSV_FILE):
        parts = line.split("\t")
        if not parts:
            continue
        w = clean(parts[0])
        if is_native_sinhala(w):
            words.add(w)
            n += 1
    print("  TSV lexicon: +%d" % n)

    return words


# Hand-curated common Sinhala misspellings -> corrections.
# Covers the error families documented in SKILLS/01_sinhala_language.md:
# ශ/ෂ, ණ/න, ල/ළ confusion, vowel-length errors, and frequent typos.
COMMON_ERRORS = {
    # ණ / න confusion
    "නිවාණ": "නිර්වාණ",
    "ගුණ": "ගුණ",            # (kept as identity guard; real fixes below)
    "පුණ්‍ය": "පුණ්‍ය",
    "කරුණාව": "කරුණාව",
    "වර්නනා": "වර්ණනා",
    "ආයතනය": "ආයතනය",
    "පරිශ්‍රමය": "පරිශ්‍රමය",
    # ශ / ෂ confusion
    "ෂිෂ්‍ය": "ශිෂ්‍ය",
    "ශාස්ත්‍රඥ": "ශාස්ත්‍රඥ",
    "විෂේෂ": "විශේෂ",
    "ශෂ්ටිය": "ෂෂ්ටිය",
    "ආශ්‍රිත": "ආශ්‍රිත",
    "දොෂ": "දෝෂ",
    "මනුෂ්‍ය": "මනුෂ්‍ය",
    # ල / ළ confusion
    "කාළය": "කාලය",
    "ගෝලය": "ගෝලය",
    "මිහිකළ": "මිහිකල",
    "පළාත": "පළාත",
    "ඵලය": "ඵලය",
    # vowel-length (ි vs ී, ු vs ූ, etc.)
    "දිවය": "දිවයින",
    "ගිහින්": "ගිහින්",
    "කොලඔ": "කොළඹ",
    "පුතා": "පුතා",
    "අම්ම": "අම්මා",
    "තාත්ත": "තාත්තා",
    "ගෙදරට": "ගෙදරට",
    # frequent everyday typos
    "කරනවා": "කරනවා",
    "යනව": "යනවා",
    "එනව": "එනවා",
    "තියනවා": "තිබෙනවා",
    "බලනව": "බලනවා",
    "කියනව": "කියනවා",
    "ඉන්නව": "ඉන්නවා",
    "දන්නව": "දන්නවා",
    "හිතනව": "හිතනවා",
    "වෙනව": "වෙනවා",
    "ලැබෙනව": "ලැබෙනවා",
    "පෙන්නනව": "පෙන්නනවා",
    "හොඳයි": "හොඳයි",
    "ගමන්": "ගමන්",
    "මොකද": "මොකද",
    "කොහොමද": "කොහොමද",
    "පොඩි": "පොඩි",
    "ලොකු": "ලොකු",
    "ඉස්කෝලෙ": "ඉස්කෝලේ",
    "පාසැල": "පාසල",
    "ගුරුවරිය": "ගුරුවරිය",
    "සිංහලෙන්": "සිංහලෙන්",
}


def main():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)

    print("Collecting words ...")
    words = collect()

    # Make sure every correct target of a known error is also a valid word.
    for correct in COMMON_ERRORS.values():
        c = clean(correct)
        if is_native_sinhala(c):
            words.add(c)

    ordered = sorted(words)
    with io.open(OUT_DICT, "w", encoding="utf-8") as f:
        for w in ordered:
            f.write(w + "\n")
    print("\nWrote %s (%d words)" % (OUT_DICT, len(ordered)))

    with io.open(OUT_ERRORS, "w", encoding="utf-8") as f:
        json.dump(COMMON_ERRORS, f, ensure_ascii=False, indent=2, sort_keys=True)
    print("Wrote %s (%d entries)" % (OUT_ERRORS, len(COMMON_ERRORS)))


if __name__ == "__main__":
    main()
