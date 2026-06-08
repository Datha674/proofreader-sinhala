# Tech Stack for Sinhala Proofreader

## Core Libraries
| Library | Version | Purpose |
|---|---|---|
| customtkinter | >=5.2.0 | Modern GUI (dark/light theme) |
| python-Levenshtein | >=0.21.0 | Fast edit-distance for spell suggestions |
| pyinstaller | >=6.0.0 | Package to .exe |
| foma | system tool | Compile SinMorphy .foma files (optional) |

## Optional Enhancements
| Library | Purpose |
|---|---|
| rapidfuzz | Faster fuzzy matching than Levenshtein |
| pyspellchecker | Base spell checker (can train on custom dict) |
| tqdm | Progress bars during dictionary loading |

## sinmorph Python API Usage
```python
# sinmorph/python/ contains the wrapper
import sys
sys.path.insert(0, 'sinmorph/python')
from sinmorph import SinMorph  # or check actual class name in source

analyzer = SinMorph()
result = analyzer.analyze("ගෙදර")
# result returns morphological tags: lemma, POS, case, etc.
```

## Levenshtein for Sinhala Suggestions
```python
from Levenshtein import distance, editops

def suggest_sinhala(word, dictionary, max_dist=2, top_n=5):
    candidates = []
    for dict_word in dictionary:
        d = distance(word, dict_word)
        if d <= max_dist:
            candidates.append((d, dict_word))
    candidates.sort()
    return [w for _, w in candidates[:top_n]]
```

## Sinhala Unicode Tokenizer
```python
import re

def tokenize_sinhala(text):
    # Match Sinhala words (including vowel signs and hal kirima)
    pattern = r'[\u0D80-\u0DFF\u200D]+'
    words = re.finditer(pattern, text)
    return [(m.group(), m.start(), m.end()) for m in words]
```

## CustomTkinter Highlighted Text
```python
# Use tkinter Text widget with tags for colored highlights
text_widget.tag_config("spell_error", background="#FF4444", foreground="white")
text_widget.tag_config("grammar_error", background="#FF8C00", foreground="white")
text_widget.tag_add("spell_error", f"1.{start}", f"1.{end}")
```

## PyInstaller Command
```bash
pyinstaller --onefile --windowed \
  --add-data "data;data" \
  --add-data "sinmorph/python;sinmorph/python" \
  --add-data "sinmorph/lexicons;sinmorph/lexicons" \
  --name SinhalaProofreader \
  sinhala_proofreader.py
```

## requirements.txt template
```
customtkinter>=5.2.0
python-Levenshtein>=0.21.0
rapidfuzz>=3.0.0
pyinstaller>=6.0.0
```