import json
import logging
from typing import Optional, Dict, Any
from core.db import get_conn, now, normalize_key, maybe_cleanup

logger = logging.getLogger(__name__)
TABLE = 'thesaurus_cache'

def get_syn_ant(word: str) -> Optional[Dict[str, Any]]:
    key = normalize_key(word)
    cur = get_conn().execute(f'SELECT payload FROM {TABLE} WHERE word = ?', (key,))
    row = cur.fetchone()
    if not row:
        logger.info('DB MISS(thesaurus_cache) for key="%s"', key)
        return None
    try:
        payload = json.loads(row['payload'])
        logger.info('DB HIT(thesaurus_cache) for key="%s"', key)
        return payload
    except Exception as e:
        logger.info('bad JSON in thesaurus_cache for key="%s : %s"', key, e)

def save_syn_ant(word: str, payload: Dict[str, Any]) -> None:
    key = normalize_key(word)
    data = json.dumps(payload, ensure_ascii=False)
    get_conn().execute(
        f"""
        INSERT INTO {TABLE} (word, payload, created_at)
        VALUES (?, ?, ?)
        ON CONFLICT (word) DO UPDATE SET
            payload = excluded.payload,
            created_at = excluded.created_at
        """,
        (key, data, now())
    )
    get_conn().commit()
    cnt = get_conn().execute(f'SELECT COUNT(*) AS c FROM {TABLE}').fetchone()["c"]
    logger.info("Saved(thesaurus) key='%s'. Total rows: %s", key, cnt)
    maybe_cleanup(ttl_days=30)  # чистка если есть что чистить