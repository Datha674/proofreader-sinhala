# -*- coding: utf-8 -*-
"""
widgets.py — reusable UI components and font helpers for the Sinhala Proofreader.
"""

import customtkinter as ctk
import tkinter.font as tkfont

_PREFERRED_FONTS = ["Iskoola Pota", "Noto Sans Sinhala", "Nirmala UI"]
_resolved_family = None


def sinhala_family():
    """Pick the best available Sinhala font family (cached). Needs a live root."""
    global _resolved_family
    if _resolved_family is None:
        try:
            available = set(tkfont.families())
        except Exception:
            available = set()
        _resolved_family = next(
            (f for f in _PREFERRED_FONTS if f in available), _PREFERRED_FONTS[0]
        )
    return _resolved_family


def font(size=16, bold=False):
    return (sinhala_family(), size, "bold") if bold else (sinhala_family(), size)


# Colours (shared with the highlight tags).
SPELL_BG = "#CC0000"
GRAMMAR_BG = "#CC6600"
OK_GREEN = "#00AA00"
ERR_RED = "#CC0000"


class StatusIndicator(ctk.CTkLabel):
    """A ✅ / ❌ connection-status label."""

    def __init__(self, master, **kw):
        super().__init__(master, text="", anchor="w", **kw)

    def set_status(self, connected, message):
        icon = "✅" if connected else "❌"
        self.configure(text="%s %s" % (icon, message),
                       text_color=OK_GREEN if connected else ERR_RED)


def confidence_badge(conf):
    """Return a short label like '90%+' for an error's confidence."""
    pct = int(round(conf * 100))
    if pct >= 90:
        return "90%+"
    if pct >= 70:
        return "70%+"
    return "<70%"


class ErrorRow(ctk.CTkFrame):
    """A clickable error row with icon, original→correction, and a confidence badge."""

    def __init__(self, master, error, on_click=None, **kw):
        super().__init__(master, fg_color="transparent", corner_radius=6, **kw)
        self.error = error
        self.on_click = on_click
        self._base = "transparent"
        self._hover = "gray25"

        is_spell = error.get("type") == "spelling"
        icon = "❌" if is_spell else "⚠️"
        tag = "SPELL" if is_spell else "GRAMMAR"
        original = error.get("original", "")
        correction = error.get("correction", "")
        arrow = "  →  %s" % correction if correction else ""
        label = "%s [%s] \"%s\"%s" % (icon, tag, original, arrow)

        self.text_label = ctk.CTkLabel(
            self, text=label, anchor="w", justify="left", font=font(14)
        )
        self.text_label.pack(side="left", fill="x", expand=True, padx=(8, 4), pady=4)

        badge = ctk.CTkLabel(
            self,
            text=confidence_badge(error.get("confidence", 0.0)),
            font=font(11),
            fg_color="gray30",
            corner_radius=8,
            width=46,
        )
        badge.pack(side="right", padx=8)

        for w in (self, self.text_label):
            w.bind("<Button-1>", self._clicked)
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)

    def _clicked(self, _e=None):
        if self.on_click:
            self.on_click(self.error)

    def _enter(self, _e=None):
        self.configure(fg_color=self._hover)

    def _leave(self, _e=None):
        self.configure(fg_color=self._base)
