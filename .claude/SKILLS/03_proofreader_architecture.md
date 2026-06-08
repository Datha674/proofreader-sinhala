# Proofreader App Architecture

## Component Map

sinhala_proofreader.py (GUI)
└── engine/proofreader.py (orchestrator)
├── engine/spell_checker.py
│       ├── data/sinhala_dictionary.txt
│       └── data/common_errors.json
└── engine/grammar_checker.py
└── sinmorph Python API (optional)

## Error Object Schema
```python
{
  "word": "වැරදි",
  "start": 14,
  "end": 19,
  "error_type": "spelling",  # or "grammar"
  "suggestions": ["නිවැරදි", "..."],
  "confidence": 0.95,
  "explanation": "වචනය ශබ්ද කෝෂයේ නොමැත"  # in Sinhala
}
```

## Spell Check Algorithm
1. Tokenize → list of (word, start, end)
2. For each word:
   a. Strip punctuation
   b. Normalize Unicode (NFC)
   c. Check if in dictionary set → O(1)
   d. If not found:
      - Check common_errors.json first (exact match)
      - Else compute Levenshtein to find closest words
      - Return top 5 suggestions sorted by distance then frequency
3. Return all flagged words with positions

## Grammar Check Algorithm
1. If sinmorph available: POS tag sentence
2. Apply rule checks:
   - Repeated word: re.search(r'(\b\S+\b)\s+\1', text)
   - Missing end punctuation: not text.rstrip().endswith(('.','?','!','෴'))
   - Common particle errors: regex patterns for ද/දැ/දී misuse
3. If sinmorph available:
   - Check verb is sentence-final (SOV order)
   - Check noun case agreement with postpositions
4. Return grammar issues with position + explanation

## Dictionary Building Strategy
Priority order for merging:
1. CydexCode DictionaryCreation/ files (already curated for this task)
2. sinmorph/lexicons/ (morphologically verified stems)
3. Expand stems with common suffixes using SinMorphy rules
4. Total target: 50,000–200,000 unique word forms

## Fallback Strategy
- If sinmorph import fails → set SINMORPH_AVAILABLE = False
- Grammar checker runs rule-based only
- Show warning in status bar: "Grammar check: basic mode"
- App still fully functional for spell checking
