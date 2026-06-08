# -*- coding: utf-8 -*-
"""
theme.py — modern colour palette for the Sinhala Proofreader.

Colours are CustomTkinter (light, dark) tuples so a single definition looks good
in both themes. tk.Text needs plain colours, so result_colors() resolves them
for the current appearance mode.
"""

import customtkinter as ctk

# Accent / action colours
ACCENT        = "#3b82f6"
ACCENT_HOVER  = "#2563eb"
SUCCESS       = "#16a34a"
SUCCESS_HOVER = "#15803d"
DANGER        = "#dc2626"
DANGER_HOVER  = "#b91c1c"

# Neutral (secondary) buttons
NEUTRAL       = ("#e2e8f0", "#252b36")
NEUTRAL_HOVER = ("#cbd5e1", "#323a48")

# Surfaces
WINDOW_BG = ("#eef2f8", "#0f1217")
HEADER_BG = ("#ffffff", "#171b22")
CARD_BG   = ("#ffffff", "#1a1f28")
BAR_BG    = ("#f3f6fb", "#141821")
BORDER    = ("#dbe2ec", "#2a3140")

# Text
TEXT      = ("#1f2733", "#e8edf4")
MUTED     = ("#64748b", "#9aa6b6")

# Error highlight backgrounds (white foreground)
SPELL_BG   = "#ef4444"
GRAMMAR_BG = "#f59e0b"

# Corner radii
R_CARD = 14
R_BTN = 9
R_BOX = 10


def result_colors():
    """Plain colours for the tk.Text highlight widget, per appearance mode."""
    if ctk.get_appearance_mode() == "Dark":
        return {"bg": "#161a21", "fg": "#e8edf4", "insert": "#e8edf4", "sel": "#2b5cab"}
    return {"bg": "#fbfcff", "fg": "#1f2733", "insert": "#1f2733", "sel": "#bcd3f5"}
