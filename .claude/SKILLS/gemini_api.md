# Gemini API Usage for Sinhala Proofreading

## Setup
```python
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")
```

## Best Model Choice
- gemini-1.5-flash: Free tier, fast, good for proofreading
- gemini-1.5-pro: Better accuracy, has cost

## Reliable JSON Response Pattern
```python
generation_config = genai.types.GenerationConfig(
    temperature=0.1,        # low = consistent output
    response_mime_type="application/json"  # force JSON
)
response = model.generate_content(prompt, generation_config=generation_config)
result = json.loads(response.text)
```

## Error Handling
```python
import google.api_core.exceptions as gexc

try:
    response = model.generate_content(prompt)
except gexc.InvalidArgument:
    return error("API Key වැරදියි")
except gexc.ResourceExhausted:
    return error("දෛනික සීමාව ඉක්මවා ඇත")
except gexc.ServiceUnavailable:
    return error("Gemini සේවාව නොමැත")
except Exception as e:
    return error(f"දෝෂයකි: {str(e)}")
```

## API Key Storage (Secure)
```python
# Store in user home — NOT in app folder
import os
config_dir = os.path.join(os.path.expanduser("~"), ".sinhala_proofreader")
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, "config.json")
```

## Rate Limits (Free Tier)
- 15 requests/minute
- 1 million tokens/day
- Add 1-second delay between rapid requests