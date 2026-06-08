# Sinhala Language Knowledge for NLP

## Script & Encoding
- Unicode block: U+0D80–U+0DFF
- Always use UTF-8. Never use legacy encodings (Wijesekara, etc.)
- Sinhala has 18 vowels, 41 consonants
- Vowel signs (matras) attach to consonants — treat consonant+matra as one unit when tokenizing

## Tokenization Rules
- Word boundary = space or punctuation
- Do NOT split on zero-width joiner (U+200D) — it joins letters within a word
- Sentence endings: ය, . (period), ? , ! , ෴ (Sinhala paragraph mark U+0DF4)
- Common punctuation used in Sinhala text: , . ? ! " " ' ' ( ) ් ා

## Common Error Patterns (for spell checker)
| Error Type | Example Wrong | Example Correct |
|---|---|---|
| Vowel length | දිවය | දිවයිනේ |
| ශ vs ෂ confusion | ශිෂ්‍ය | ශිෂ්‍ය ✓ / ෂිෂ්‍ය ✗ |
| ණ vs න confusion | නිවාණ | නිර්වාණ |
| ල vs ළ confusion | කාළය | කාලය or කාළය (depends) |
| Missing ් (hal kirima) | කරනවා → කරන්නේ | context-dependent |
| Encoding artifacts | â€" instead of — | fix encoding first |

## Grammar Rules (Sinhala-specific)
- SOV language: Subject → Object → Verb
- Verb comes at END of sentence
- Negation: add නෑ / නැහැ / නොවේ after verb
- Tense markers attach to verb stem (no separate tense word)
- Postpositions (not prepositions): ගෙදරට (home+to), not "to home"
- Honorifics change verb form: යනවා (he goes) vs යනවා (you go - informal)

## Morphology
- Highly agglutinative: stems + suffixes
- Noun cases: nominative, accusative, dative, genitive, instrumental, locative, ablative, vocative
- Verb forms: present/past/future + causative + passive
- SinMorphy handles: nouns (26 classes), verbs, adjectives, adverbs, particles

## POS Tags from SinMorphy
- NN = Noun, VB = Verb, JJ = Adjective, RB = Adverb
- PP = Postposition, CC = Conjunction, RP = Particle

## Fonts to Use in GUI
- Iskoola Pota (built into Windows)
- Noto Sans Sinhala (Google Fonts, free)
- Font size minimum 14px for readability