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

DICT_BASE_URL = 'https://dictionaryapi.com/api/v3/references/collegiate/json/'
THE_BASE_URL = 'https://dictionaryapi.com/api/v3/references/thesaurus/json/'

