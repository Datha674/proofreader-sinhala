# Master Skillset — Sinhala Proofreader Project

## Prime Directives
1. ALWAYS read existing repo files before writing any code
2. NEVER assume dictionary format — inspect actual files first
3. ALWAYS use UTF-8 encoding when reading/writing any Sinhala text
4. Handle sinmorph import failure gracefully — never crash
5. Test with actual Sinhala Unicode text before packaging

## Development Order (strict)
1. Explore → 2. Build dictionary → 3. Build engine → 4. Build GUI → 5. Package → 6. Test

## Critical Gotchas
- Sinhala chars are multi-byte in UTF-8 — use character positions not byte positions
- tkinter Text widget position is "line.char" not absolute index
- PyInstaller: always use os.path relative to sys._MEIPASS for bundled data files:
```python
  import sys, os
  def resource_path(relative):
      base = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
      return os.path.join(base, relative)
```
- CustomTkinter requires tkinter as base — it's bundled with Python
- foma .foma files need the `foma` binary to compile — may not be available on Windows;
  use pre-compiled transducer or skip SinMorphy foma integration on Windows

## Accuracy Improvement Checklist
- [ ] Unicode normalization (NFC) before all comparisons
- [ ] Dictionary contains both stems AND inflected forms
- [ ] Common errors JSON covers top 50 known Sinhala typos
- [ ] Suggestion scoring = (levenshtein_distance * 0.7) + (1/frequency * 0.3)
- [ ] Grammar rules tested on 20+ sample sentences
- [ ] Edge cases: empty input, pure English text, mixed Sinhala+English

## Quality Gates Before .exe Build
- [ ] App launches without errors
- [ ] Sinhala text renders correctly (not as boxes)
- [ ] At least 5 spelling errors correctly detected in test paragraph
- [ ] At least 1 grammar error detected (repeated word)
- [ ] Corrected text generates successfully
- [ ] Copy button works
- [ ] .exe launches on clean machine (no Python installed)