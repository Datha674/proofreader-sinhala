# -*- coding: utf-8 -*-
"""
Shared utilities for the Sinhala Proofreader engine:
  - resource_path : locate bundled data both in dev and inside a PyInstaller .exe
  - normalize     : NFC Unicode normalization (run before every comparison)
  - tokenize      : split Sinhala text into (word, start, end) by CHARACTER position
"""

import os
import re
import sys
import unicodedata

# Sinhala block U+0D80-U+0DFF, plus Zero Width Joiner (U+200D) used inside
# conjunct clusters. We deliberately do NOT split on the ZWJ.
SINHALA_WORD_RE = re.compile(r"[඀-෿‍]+")

# Sentence-ending marks valid in Sinhala text.
SENTENCE_ENDINGS = (".", "?", "!", "෴")  # ෴ = ෴ kunddaliya


def resource_path(relative):
    """Return absolute path to a bundled resource.

    Works in development (relative to the project root) and inside a
    PyInstaller one-file build (relative to the extracted sys._MEIPASS dir).
    """
    base = getattr(sys, "_MEIPASS", None)
    if base is None:
        # project root = parent of this engine/ package
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relative)


def normalize(text):
    """NFC-normalize text so visually identical strings compare equal."""
    if text is None:
        return ""
    return unicodedata.normalize("NFC", text)


def tokenize(text):
    """Tokenize into a list of (word, start, end) using CHARACTER offsets.

    Character (not byte) offsets are required so positions map correctly onto
    a tkinter Text widget, where Sinhala glyphs are single index units.
    """
    text = normalize(text)
    return [(m.group(), m.start(), m.end()) for m in SINHALA_WORD_RE.finditer(text)]


def contains_sinhala(text):
    """True if the text has at least one Sinhala character."""
    return bool(SINHALA_WORD_RE.search(normalize(text or "")))
