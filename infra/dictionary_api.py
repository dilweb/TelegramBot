import requests
from core.config import DICT_API_KEY, THE_API_KEY, DICT_BASE_URL, THE_BASE_URL


def fetch_definition(word: str):
    url = f'{DICT_BASE_URL}{word.lower()}'
    try:
        r = requests.get(url, params={'key': DICT_API_KEY}, timeout=10)
        r.raise_for_status()
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

    entry = next((e for e in data if isinstance(e, dict) and e.get('shortdef')), None)
    if not entry:
        return {"error": "no-definitions"}

    hw = (entry.get("hwi", {}).get("hw") or word).title()
    pos = entry.get("fl") or ""
    pron = (entry.get("hwi", {}).get("prs", [{}])[0].get("mw"))
    sdef = entry["shortdef"][:3]

    sdef_list = []
    for defs in sdef:
        if defs.endswith(": such as"):
            defs = defs[:-9].strip()
        sdef_list.append(defs)

    return {"word": hw, "pos": pos, "pron": pron, "shortdef": sdef_list}


def fetch_thesaurus(word: str):
    url = f'{THE_BASE_URL}{word.lower()}'
    try:
        r = requests.get(url, params={'key': THE_API_KEY}, timeout=10)
        r.raise_for_status()
    except requests.RequestException as e:
        return {'error': f'network: {e}'}

    try:
        data = r.json()
    except ValueError:
        return {'error': 'bad-json'}

    if not data:
        return {"error": "no-results"}

    syns_set, ants_set = set(), set()
    entry = next((e for e in data if isinstance(e, dict)), None)
    if not entry:
        return {"error": "no-synonyms"}

    meta = entry.get("meta", {})
    for group in meta.get("syns", []):
        for w in group:
            if w and w.lower() != word.lower():
                syns_set.add(w)
    for group in meta.get("ants", []):
        for w in group:
            if w and w.lower() != word.lower():
                ants_set.add(w)

    syns = list(syns_set)[:5]
    ants = list(ants_set)[:5]

    if not syns and not ants:
        return {"error": "no-thesaurus-terms"}

    if not ants:
        ants = None

    return {"synonyms": syns, "antonyms": ants}



# print(fetch_definition("car"))
