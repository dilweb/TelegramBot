import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if BOT_TOKEN is None:
    exit('BOT_TOKEN отсутствует в переменных окружения')

DICT_API_KEY = os.getenv('DICT_API_KEY')
if DICT_API_KEY is None:
    exit('DICT_API_KEY отсутствует в переменных окружения')

THE_API_KEY = os.getenv('THE_API_KEY')
if THE_API_KEY is None:
    exit('THE_API_KEY отсутствует в переменных окружения')

DB_PATH = os.getenv('DB_PATH')
if DB_PATH is None:
    exit('DB_PATH отсутствует в переменных окружения')

GEMINI_API = os.getenv('GEMINI_API')
if GEMINI_API is None:
    exit('GEMINI_API отсутствует в переменных окружения')

CHAT_API = os.getenv('CHAT_API')
if CHAT_API is None:
    exit('CHAT_API отсутствует в переменных окружения')

DICT_BASE_URL = 'https://dictionaryapi.com/api/v3/references/collegiate/json/'
THE_BASE_URL = 'https://dictionaryapi.com/api/v3/references/thesaurus/json/'
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent'
CHAT_URL = 'https://api.openai.com/v1/chat/completions'

