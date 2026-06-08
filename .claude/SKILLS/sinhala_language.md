# Sinhala Language Rules for AI Proofreading

## What is VALID Sinhala (never flag these)
- Colloquial forms: ඕනේ, නෙවේ, කරලා, ගිහිල්ල, නිහඬයි, ගේනවා
- Inflected nouns: රටම, රටට, රටෙන්, රටේ, කාගේ, ඔහුගේ, බලයේ
- Compound words: ජනජීවිතය, ආරක්ෂාව, ප්‍රචණ්ඩත්වය, ජනාධිපති
- Postpositional forms: ගෙදරට, පාසලේ, ගස් යටට
- Verbal nouns + particles: කරන්නේ, ගියේ, ආවේ, දෙන්න

## Common REAL Errors (flag these)
| Wrong | Correct | Type |
|---|---|---|
| නෑහැ | නැහැ | Spelling |
| ශිෂ්‍ය → ෂිෂ්‍ය | ශිෂ්‍ය | ශ/ෂ confusion |
| නිවාන | නිර්වාණ | Missing ර් |
| ප්‍රචණ්ඩලත්වය | ප්‍රචණ්ඩත්වය | Extra ල |

## Gemini Prompt Tips
- Always tell Gemini: colloquial Sinhala IS valid
- Always tell Gemini: inflected forms ARE valid  
- Ask for JSON only — no markdown
- Use temperature 0.1 for consistency
- Request confidence scores to filter low-confidence flags