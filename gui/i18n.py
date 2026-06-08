# -*- coding: utf-8 -*-
"""
i18n.py — tiny translation table for the GUI.

t(lang, key) returns the string for "en" or "si"; falls back to English, then
to the key itself. Used so the UI Language setting actually switches the app.
"""

STRINGS = {
    # window / header
    "app_title":     {"en": "🔤  Sinhala Word & Grammar Checker", "si": "🔤  සිංහල වචන හා ව්‍යාකරණ පරීක්ෂකය"},
    "app_subtitle":  {"en": "Sinhala Proofreader", "si": "සිංහල වචන පරීක්ෂකය"},
    "settings_btn":  {"en": "⚙️ Settings", "si": "⚙️ සැකසීම්"},

    # mode bar
    "api_key_btn":   {"en": "🔑 API Key", "si": "🔑 API යතුර"},
    "lan_mode":      {"en": "LAN mode", "si": "LAN ආකාරය"},
    "key_ready":     {"en": "API key set (ready)", "si": "API යතුර සකසා ඇත (සූදානම්)"},
    "key_missing":   {"en": "No API key — Settings", "si": "API යතුරක් නැත — සැකසීම්"},

    # input panel
    "input_label":   {"en": "📝 Enter your text  (Input)", "si": "📝 ඔබේ පාඨය ඇතුළු කරන්න  (Input)"},
    "check_btn":     {"en": "🔍 Check  (Ctrl+Enter)", "si": "🔍 පරීක්ෂා කරන්න  (Ctrl+Enter)"},
    "checking_btn":  {"en": "⏳ Checking...", "si": "⏳ පරීක්ෂා කරමින්..."},
    "clear_btn":     {"en": "🗑️ Clear", "si": "🗑️ හිස් කරන්න"},
    "errors_label":  {"en": "Errors Found", "si": "දෝෂ ලැයිස්තුව"},

    # results panel
    "results_label": {"en": "🔍 Results  —  🟥 spelling   🟧 grammar", "si": "🔍 ප්‍රතිඵල  —  🟥 spelling   🟧 grammar"},
    "corrected_label": {"en": "✅ Corrected Text", "si": "✅ නිවැරදි කළ පාඨය"},
    "open_corrected": {"en": "✅ Open Corrected Text", "si": "✅ නිවැරදි කළ පාඨය විවෘත කරන්න"},
    "corrected_title": {"en": "Corrected Text — Sinhala Proofreader", "si": "නිවැරදි කළ පාඨය — සිංහල වචන පරීක්ෂකය"},
    "corrected_hint": {"en": "Edit the text below, then Save My Corrections to teach the app.",
                       "si": "පහත පාඨය සංස්කරණය කර, යෙදුමට උගැන්වීමට \"නිවැරදිකිරීම් සුරකින්න\" ඔබන්න."},
    "close_btn":     {"en": "Close", "si": "වසන්න"},
    "copy_btn":      {"en": "📋 Copy Corrected", "si": "📋 පිටපත් කරන්න"},
    "export_btn":    {"en": "💾 Export Report", "si": "💾 වාර්තාව"},
    "save_corr_btn": {"en": "✍️ Save My Corrections", "si": "✍️ නිවැරදිකිරීම් සුරකින්න"},

    # status messages
    "ready":         {"en": "Ready", "si": "සූදානම්"},
    "enter_text":    {"en": "📝 Please enter some text", "si": "📝 කරුණාකර පාඨය ඇතුළු කරන්න"},
    "need_key":      {"en": "🔑 A Gemini API key is required — opening Settings", "si": "🔑 Gemini API යතුරක් අවශ්‍යයි — සැකසීම් විවෘත වෙමින්"},
    "checking_direct": {"en": "⏱️ Checking with Gemini...", "si": "⏱️ Gemini සමඟ පරීක්ෂා කරමින්..."},
    "checking_lan":  {"en": "⏱️ Checking via Control PC...", "si": "⏱️ Control PC සමඟ පරීක්ෂා කරමින්..."},
    "no_errors":     {"en": "✅ No errors found", "si": "✅ දෝෂ හමු නොවීය"},
    "no_errors_row": {"en": "✅ No errors found", "si": "✅ දෝෂ හමු නොවීය  (no errors found)"},
    "settings_saved": {"en": "Settings saved", "si": "සැකසීම් සුරැකිණි"},
    "nothing_copy":  {"en": "Nothing to copy", "si": "පිටපත් කිරීමට කිසිවක් නැත"},
    "copied":        {"en": "📋 Corrected text copied", "si": "📋 නිවැරදි කළ පාඨය පිටපත් විය"},
    "run_first":     {"en": "Run a check first", "si": "මුලින් පරීක්ෂා කරන්න"},
    "no_edits":      {"en": "✅ No edits — nothing to learn", "si": "✅ වෙනස්කම් නොමැත"},
    "saved_local":   {"en": "✅ %d correction(s) saved to local DB", "si": "✅ නිවැරදිකිරීම් %d ක් local DB වෙත සුරකිණා"},
    "saved_proxy":   {"en": "✅ %d correction(s) saved to Control PC", "si": "✅ නිවැරදිකිරීම් %d ක් Control PC වෙත සුරකිණා"},

    # totals
    "total_errors":  {"en": "Total: %d errors", "si": "මුළු දෝෂ: %d"},
}


def t(lang, key, *args):
    entry = STRINGS.get(key, {})
    s = entry.get(lang) or entry.get("en") or key
    if args:
        try:
            return s % args
        except Exception:
            return s
    return s
