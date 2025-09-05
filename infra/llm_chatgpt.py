import requests
from core.config import CHAT_API, CHAT_URL

def ask_gpt(word):
    instruction = 'Write ONE short sentence in English without quotes and extra text up to 15 words. With the word '
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

# print(ask_gpt('carpet'))