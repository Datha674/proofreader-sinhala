# -*- coding: utf-8 -*-
"""
settings_dialog.py — connection mode, API key & preferences popup.
"""

import threading
import webbrowser

import customtkinter as ctk

from .widgets import font, StatusIndicator
from engine.gemini_engine import GeminiProofreader, GeminiError

AISTUDIO_URL = "https://aistudio.google.com/app/apikey"


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, config, on_saved=None):
        super().__init__(master)
        self.config_obj = config
        self.on_saved = on_saved

        self.title("⚙️ සැකසීම් / Settings")
        self.geometry("560x720")
        self.minsize(520, 560)
        self.transient(master)
        self.grab_set()  # modal

        self._show_key = False
        self._build()
        self.after(120, self.lift)

    # ----- layout --------------------------------------------------------
    def _build(self):
        # Save / Cancel pinned to the bottom (outside the scroll area).
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(side="bottom", fill="x", padx=20, pady=14)
        ctk.CTkButton(btns, text="💾 සුරකින්න / Save", command=self._save).pack(
            side="left", expand=True, fill="x", padx=(0, 6)
        )
        ctk.CTkButton(
            btns, text="අවලංගු / Cancel", fg_color="gray40", hover_color="gray30",
            command=self.destroy,
        ).pack(side="left", expand=True, fill="x", padx=(6, 0))

        body = ctk.CTkScrollableFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True)
        pad = {"padx": 16, "pady": (10, 0)}

        ctk.CTkLabel(body, text="⚙️ සැකසීම් / Settings", font=font(20, True)).pack(
            anchor="w", **pad
        )

        # ── CONNECTION MODE ──────────────────────────────────────────────
        ctk.CTkLabel(
            body, text="🌐 Connection Mode / සම්බන්ධතා ආකාරය", font=font(15, True)
        ).pack(anchor="w", **pad)
        self.mode_var = ctk.StringVar(
            value=self.config_obj.get("connection_mode", "direct")
        )
        for value, label in [
            ("direct", "● Direct — API key on this PC (Online)"),
            ("lan_proxy", "● LAN Proxy — via Control PC (no key needed here)"),
        ]:
            ctk.CTkRadioButton(
                body, text=label, variable=self.mode_var, value=value,
                font=font(13), command=self._toggle_mode_fields,
            ).pack(anchor="w", padx=30, pady=2)

        # Common frame anchors the position of the mode-specific frames.
        self.common_frame = ctk.CTkFrame(body, fg_color="transparent")
        self.common_frame.pack(fill="x", side="bottom")

        # ── DIRECT-mode widgets ──────────────────────────────────────────
        self.direct_frame = ctk.CTkFrame(body, fg_color="transparent")

        ctk.CTkLabel(self.direct_frame, text="🔑 Gemini API Key", font=font(15, True)).pack(
            anchor="w", padx=4, pady=(10, 0)
        )
        key_row = ctk.CTkFrame(self.direct_frame, fg_color="transparent")
        key_row.pack(fill="x", padx=4, pady=(2, 0))
        self.key_entry = ctk.CTkEntry(
            key_row, placeholder_text="AIza... / AQ...", show="•", font=font(14)
        )
        self.key_entry.pack(side="left", fill="x", expand=True)
        self.key_entry.insert(0, self.config_obj.get_api_key())
        ctk.CTkButton(key_row, text="👁️", width=40, command=self._toggle_show).pack(
            side="left", padx=(6, 0)
        )

        test_row = ctk.CTkFrame(self.direct_frame, fg_color="transparent")
        test_row.pack(fill="x", padx=4, pady=(8, 0))
        self.test_btn = ctk.CTkButton(
            test_row, text="සම්බන්ධතාව පරීක්ෂා කරන්න / Test Connection",
            command=self._test_connection,
        )
        self.test_btn.pack(side="left")
        self.test_status = StatusIndicator(self.direct_frame, font=font(13))
        self.test_status.pack(anchor="w", padx=4, pady=(6, 0))

        help_box = ctk.CTkFrame(self.direct_frame)
        help_box.pack(fill="x", padx=4, pady=(12, 0))
        ctk.CTkLabel(
            help_box, text="🔗 API Key ලබා ගන්නේ කෙසේද? / How to get a key",
            font=font(13, True), anchor="w", justify="left",
        ).pack(anchor="w", padx=10, pady=(8, 2))
        ctk.CTkLabel(
            help_box,
            text="1. aistudio.google.com වෙත යන්න\n"
            "2. \"Get API Key\" ක්ලික් කරන්න\n"
            "3. Key එක copy කර මෙහි paste කරන්න",
            font=font(13), anchor="w", justify="left",
        ).pack(anchor="w", padx=10, pady=(0, 6))
        ctk.CTkButton(
            help_box, text="🌐 aistudio.google.com විවෘත කරන්න",
            fg_color="gray30", hover_color="gray25",
            command=lambda: webbrowser.open(AISTUDIO_URL),
        ).pack(anchor="w", padx=10, pady=(0, 10))

        ctk.CTkLabel(self.direct_frame, text="Gemini Model:", font=font(14, True)).pack(
            anchor="w", padx=4, pady=(10, 0)
        )
        self.model_var = ctk.StringVar(
            value=self.config_obj.get("gemini_model", "gemini-2.5-flash")
        )
        for value, label in [
            ("gemini-2.5-flash", "gemini-2.5-flash  (Fast, Free — Recommended)"),
            ("gemini-flash-latest", "gemini-flash-latest  (Always newest flash)"),
            ("gemini-2.5-pro", "gemini-2.5-pro  (Best quality, low free quota)"),
        ]:
            ctk.CTkRadioButton(
                self.direct_frame, text=label, variable=self.model_var, value=value,
                font=font(13),
            ).pack(anchor="w", padx=24, pady=2)

        # ── LAN-PROXY widgets ────────────────────────────────────────────
        self.proxy_frame = ctk.CTkFrame(body, fg_color="transparent")
        ctk.CTkLabel(self.proxy_frame, text="Control PC URL:", font=font(14, True)).pack(
            anchor="w", padx=4, pady=(10, 0)
        )
        self.proxy_url_entry = ctk.CTkEntry(
            self.proxy_frame, placeholder_text="http://192.168.1.100:8765", font=font(13)
        )
        self.proxy_url_entry.pack(fill="x", padx=4, pady=3)
        self.proxy_url_entry.insert(
            0, self.config_obj.get("proxy_url", "http://192.168.1.100:8765")
        )
        ctk.CTkButton(
            self.proxy_frame, text="📡 Test Proxy Connection", command=self._test_proxy
        ).pack(anchor="w", padx=4, pady=5)
        self.proxy_status_label = StatusIndicator(self.proxy_frame, font=font(13))
        self.proxy_status_label.pack(anchor="w", padx=4)
        ctk.CTkLabel(
            self.proxy_frame,
            text="මෙම PC එකේ API Key අවශ්‍ය නැත — Control PC හරහා ක්‍රියා කරයි.",
            font=font(12), text_color="gray", anchor="w", justify="left", wraplength=480,
        ).pack(anchor="w", padx=4, pady=(6, 0))

        # ── COMMON: theme + language ─────────────────────────────────────
        row = ctk.CTkFrame(self.common_frame, fg_color="transparent")
        row.pack(fill="x", padx=4, pady=(14, 0))
        theme_col = ctk.CTkFrame(row, fg_color="transparent")
        theme_col.pack(side="left", expand=True, anchor="w")
        ctk.CTkLabel(theme_col, text="Theme:", font=font(14, True)).pack(anchor="w")
        self.theme_var = ctk.StringVar(value=self.config_obj.get("theme", "dark"))
        for value, label in [("dark", "Dark"), ("light", "Light")]:
            ctk.CTkRadioButton(theme_col, text=label, variable=self.theme_var,
                               value=value, font=font(13)).pack(anchor="w", pady=1)
        lang_col = ctk.CTkFrame(row, fg_color="transparent")
        lang_col.pack(side="left", expand=True, anchor="w")
        ctk.CTkLabel(lang_col, text="UI Language:", font=font(14, True)).pack(anchor="w")
        self.lang_var = ctk.StringVar(value=self.config_obj.get("language", "si"))
        for value, label in [("si", "සිංහල"), ("en", "English")]:
            ctk.CTkRadioButton(lang_col, text=label, variable=self.lang_var,
                               value=value, font=font(13)).pack(anchor="w", pady=1)

        self._toggle_mode_fields()

    # ----- behaviour -----------------------------------------------------
    def _toggle_mode_fields(self):
        mode = self.mode_var.get()
        self.direct_frame.pack_forget()
        self.proxy_frame.pack_forget()
        if mode == "lan_proxy":
            self.proxy_frame.pack(fill="x", padx=16, before=self.common_frame)
        else:
            self.direct_frame.pack(fill="x", padx=16, before=self.common_frame)

    def _toggle_show(self):
        self._show_key = not self._show_key
        self.key_entry.configure(show="" if self._show_key else "•")

    def _test_connection(self):
        key = self.key_entry.get().strip()
        if not self.config_obj.validate_api_key_format(key):
            self.test_status.set_status(False, "API Key හිස් ය — Key ඇතුළු කර Save කරන්න")
            return
        self.test_btn.configure(state="disabled", text="⏳ පරීක්ෂා කරමින්...")
        self.test_status.configure(text="⏳ ...", text_color="gray")

        def run():
            try:
                ok, msg = GeminiProofreader(key, self.model_var.get()).test_connection()
            except GeminiError as exc:
                ok, msg = False, exc.message_si
            except Exception as exc:  # pragma: no cover
                ok, msg = False, str(exc)
            self.after(0, lambda: self._test_done(ok, msg))

        threading.Thread(target=run, daemon=True).start()

    def _test_done(self, ok, msg):
        self.test_btn.configure(
            state="normal", text="සම්බන්ධතාව පරීක්ෂා කරන්න / Test Connection"
        )
        self.test_status.set_status(ok, msg)

    def _test_proxy(self):
        url = self.proxy_url_entry.get().strip()
        if not url:
            self.proxy_status_label.set_status(False, "Proxy URL ඇතුළත් කරන්න")
            return
        self.proxy_status_label.configure(text="⏳ ...", text_color="gray")

        def run():
            try:
                from engine.lan_proxy_engine import LanProxyProofreader
                ok, msg = LanProxyProofreader(url).test_connection()
            except Exception as exc:  # pragma: no cover
                ok, msg = False, str(exc)[:100]
            self.after(0, lambda: self.proxy_status_label.set_status(ok, msg))

        threading.Thread(target=run, daemon=True).start()

    def _save(self):
        key = self.key_entry.get().strip()
        if key and not self.config_obj.validate_api_key_format(key):
            self.test_status.set_status(False, "API Key හිස් ය — Key ඇතුළු කර Save කරන්න")
            return
        self.config_obj.set("connection_mode", self.mode_var.get())
        self.config_obj.set("proxy_url", self.proxy_url_entry.get().strip())
        self.config_obj.set("gemini_api_key", key)
        self.config_obj.set("gemini_model", self.model_var.get())
        self.config_obj.set("theme", self.theme_var.get())
        self.config_obj.set("language", self.lang_var.get())
        self.config_obj.save()
        ctk.set_appearance_mode(self.theme_var.get())
        if self.on_saved:
            self.on_saved()
        self.destroy()
