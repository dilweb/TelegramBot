import requests

from config import DICT_API_KEY, THE_API_KEY, DICT_BASE_URL, THE_BASE_URL


def definition(word: str):
    # делаем базовую ссылку
    url = f'{DICT_BASE_URL}{word.lower()}'
    try:
        r = requests.get(url, params={'key': DICT_API_KEY}, timeout=10)
        r.raise_for_status() # проверяем статус если не 200 - ошибка
    except requests.RequestException as e:
        return {'error': f'network: {e}'}

    # проверим пришел ли список/словарь, если нет выдаем красивую ошибку
    try:
        data = r.json()
    except ValueError:
        return {'error': 'bad-json'}

    if not data:
        return {"error": "no-results"}

    # если список строк, то Merriam-Webster дал нам подсказки [str, str, str...] (юзер написал слово неправильно)
    if all(isinstance(x, str) for x in data):
        return {"suggestions": data[:5]}

    # ищем краткую статью: она должна быть диктом с ключом shortdef
    entry = next((e for e in data if isinstance(e, dict) and e.get('shortdef')),  None)
    if not entry:
        return {"error": "no-definitions"}

    hw = entry.get("hwi", {}).get("hw") or word
    hw = hw.title()
    pos = entry.get("fl") or ""
    # если "prs" нет вернем список с одним пустым словарём [{}] иначе IndexError
    pron = (entry.get("hwi", {}).get("prs", [{}])[0].get("mw"))
    sdef = entry["shortdef"][0]
    sdef = sdef[0].upper() + sdef[1:]
    sdef = sdef.strip()
    if sdef.endswith(": such as"):
        sdef = sdef[:-9].strip() + "…"

    return {"word": hw, "pos": pos, "pron": pron, "shortdef": sdef}


def thesaurus(word: str):
    # делаем базовую ссылку
    url = f'{THE_BASE_URL}{word.lower()}'
    try:
        r = requests.get(url, params={'key': THE_API_KEY}, timeout=10)
        r.raise_for_status() # проверяем статус если не 200 - ошибка
    except requests.RequestException as e:
        return {'error': f'network: {e}'}

    try:
        data = r.json()
    except ValueError:
        return {'error': 'bad-json'}

    if not data:
        return {"error": "no-results"}

    if all(isinstance(x, str) for x in data):
        return {"suggestions": data[:5]}

    syns_set, ants_set = set(), set()
    pos = None
    headword = None

    entry = next((e for e in data if isinstance(e, dict)), None)
    if not entry:
        return {"error": "no-synonyms"}



# print(lookup('car'))