import json
import logging
from typing import Optional, Dict, Any
from core.db import get_conn, now, normalize_key, maybe_cleanup


logger = logging.getLogger(__name__)
TABLE = 'glossary_cache'


def get_word(word: str) -> Optional[Dict[str, Any]]:
    """Вернуть из БД payload или None"""
    key = normalize_key(word)
    # взять подключение, выполнить скл и вернуть курсор
    cur = get_conn().execute(f'SELECT payload FROM {TABLE} WHERE word = ?', (key,))
    row = cur.fetchone()
    if not row:
        logging.info("DB MISS for key='%s'", key)
        return None
    try:
        payload = json.loads(row['payload'])
        logging.info("DB HIT for key='%s'", key)
        return payload
    except Exception as e:
        logging.warning("DB row for key='%s' has bad JSON: %s", key, e)
        return None


def save_word(word: str, payload: Dict[str, Any]) -> None:
    """Сохранить/обновить JSON под ключом word"""
    key = normalize_key(word)
    data = json.dumps(payload, ensure_ascii=False) # сериализуем
    get_conn().execute(
        """
        INSERT INTO glossary_cache(word, payload, created_at)
        VALUES(?, ?, ?)
        ON CONFLICT(word) DO UPDATE SET
            payload = excluded.payload,
            created_at = excluded.created_at
        """,
        (key, data, now()),
    )
    get_conn().commit()
    # достаем количество строк из таблицы для логов
    cnt = get_conn().execute("SELECT COUNT(*) AS c FROM glossary_cache").fetchone()["c"]
    logger.info("Saved key='%s'. Total rows: %s", key, cnt)
    get_conn().commit()
    maybe_cleanup(ttl_days=30) # чистка если есть что чистить
