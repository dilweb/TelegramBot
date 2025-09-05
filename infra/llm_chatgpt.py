import requests
from core.config import CHAT_API, CHAT_URL

def ask_gpt(word):
    instruction = ("You are an ESL example-sentence generator. "
        "Return ONE neutral, non-violent, non-actionable sentence (5–15 words) "
        "that includes the target word exactly once. "
        "Use lawful, fictional, news, or academic context. No quotes. No extra text.")


    headers = {"Authorization": f"Bearer {CHAT_API}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": instruction},
            {"role": "user", "content": word}
        ]
    }
    response = requests.post(CHAT_URL, headers=headers, json=data).json()
    return response["choices"][0]["message"]["content"].strip('"')

# print(ask_gpt('murderer'))