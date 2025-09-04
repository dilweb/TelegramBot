import requests
from core.config import GEMINI_API, GEMINI_URL


def ask_gemini(word: str) -> str:
    instruction = 'Write ONE short sentence in English without quotes and extra text up to 15 words. With the word '
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': GEMINI_API
    }
    body = {
        'contents': [{'parts': [{'text': instruction + word}]}]
    }
    r = requests.post(GEMINI_URL, headers=headers, json=body, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

# print(ask_gemini("mile"))