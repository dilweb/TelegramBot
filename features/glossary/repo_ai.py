import logging
from typing import Optional, Dict, Any
from core.db import get_conn, now, normalize_key, maybe_cleanup


logger = logging.getLogger(__name__)


def get_sentence(word: str) -> Optional[Dict[str, Any]]:
    """Вернуть из БД payload или None"""
    key = normalize_key(word)
    # взять подключение, выполнить скл и вернуть курсор
    cur = get_conn().execute('SELECT sentence FROM ai_cache WHERE word = ?', (key,))
    if not cur:
        logger.info("DB ai_repo MISS for key='%s'", key)
        return None
    try:
        row = cur.fetchone()
        logger.info("DB ai_repo HIT for key='%s'", key)
        return row # отдаем результат, если повезет

    except Exception as e:
        logger.warning("DB row for key='%s' has bad JSON: %s", key, e)
        return None


def save_sentence(word: str, sentence: str) -> None:
    """Сохранить/обновить JSON под ключом word"""
    key = normalize_key(word)
    get_conn().execute(
        """
        INSERT INTO ai_cache(word, sentence, created_at)
        VALUES(?, ?, ?)
        ON CONFLICT(word) DO UPDATE SET
            sentence = excluded.sentence,
            created_at = excluded.created_at
        """,
        (key, sentence, now()),
    )
    get_conn().commit()
    # достаем количество строк из таблицы для логов
    cnt = get_conn().execute("SELECT COUNT(*) AS c FROM ai_cache").fetchone()["c"]
    logger.info("Saved key='%s'. Total rows: %s", key, cnt)
    get_conn().commit()
    maybe_cleanup(ttl_days=30) # чистка если есть что чистить
