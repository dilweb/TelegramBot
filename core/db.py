import sqlite3
import time
import logging
from core.config import DB_PATH
from typing import Optional

# чистим кэш каждые 30 дней
_CLEANUP_PERIOD_SECONDS = 20 * 24 * 3600
_last_cleanup_ts = 0 # время последней чистки

def clear_old_cache(days: int = 30) -> None:
    """Удалить записи старше N дней из двух таблиц"""
    cutoff = int(time.time()) - days * 24 * 60 * 60
    conn = get_conn()
    g_del = conn.execute('DELETE FROM glossary_cache WHERE created_at < ?', (cutoff,)).rowcount
    t_del = conn.execute('DELETE FROM thesaurus_cache WHERE created_at < ?', (cutoff,)).rowcount
    conn.commit()
    logger.info(
        'Cache cleanup: glossary -%s, thesaurus -%s (older than %s days)',
        g_del, t_del, days
    )

def maybe_cleanup(ttl_days: int = 30, period_seconds: int = _CLEANUP_PERIOD_SECONDS) -> None:
    """
    Если с последней чистки прошло >= period_seconds,
    запускаем clear_old_cache(ttl_days).
    """
    global _last_cleanup_ts
    now_ts = time.time()
    if now_ts - _last_cleanup_ts < period_seconds:
        return
    _last_cleanup_ts = now_ts
    try:
        clear_old_cache(days=ttl_days)
    except Exception as e:
        logger.warning('Cache cleanup failed: %s', e)

logger = logging.getLogger(__name__)

def normalize_key(word: str) -> str:
    return (word or '').strip().lower()

# один конекшен на процесс
_conn: Optional[sqlite3.Connection] = None

def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        logger.info("Opening SQLite DB at %s", DB_PATH)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row # обращаемся к колонкам по имени, как к словарю
    return _conn


def init_db() -> None:
    """Кэш для определений и тезарусов"""
    # кэш определений
    conn = get_conn()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS glossary_cache (
        word TEXT PRIMARY KEY,
        payload TEXT NOT NULL,
        created_at INTEGER NOT NULL
        ) 
    """)

    # создаем индексы по колонке, в которой записывается дата комита. пригодится для удаления записей старше N сек
    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_glossary_cache_created_at ON glossary_cache (created_at)
    """)

    # кэш тезарусов
    conn.execute("""
    CREATE TABLE IF NOT EXISTS thesaurus_cache (
    word TEXT PRIMARY KEY,
    payload TEXT NOT NULL,
    created_at INTEGER NOT NULL
    )
    """)

    conn.execute("""
    CREATE INDEX IF NOT EXISTS idx_thesaurus_cache_created_at ON thesaurus_cache (created_at)
    """)

    conn.commit()
    logger.info('DB initialized, tables glossary_cache & thesaurus_cache are ready')


def fetchone_dict(cur: sqlite3.Cursor) -> Optional[dict]:
    row = cur.fetchone()
    return dict(row) if row else None

def now() -> int:
    return int(time.time())