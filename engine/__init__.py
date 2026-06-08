# -*- coding: utf-8 -*-
"""Sinhala Proofreader engine package (Direct Gemini + LAN proxy)."""

from .proofreader import SinhalaProofreader
from .gemini_engine import GeminiProofreader, GeminiError
from .corrections_db import CorrectionsDB

__all__ = [
    "SinhalaProofreader",
    "GeminiProofreader",
    "GeminiError",
    "CorrectionsDB",
]
