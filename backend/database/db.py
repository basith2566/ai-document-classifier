"""SQLite access using Python's built-in sqlite3 module (no ORM, easy to read)."""
import sqlite3
from contextlib import contextmanager

from utils.config import settings

SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    filename       TEXT    NOT NULL,
    file_type      TEXT    NOT NULL,
    file_size      INTEGER NOT NULL,
    category       TEXT    NOT NULL,     -- best guess made by the model
    confidence     REAL    NOT NULL,     -- 0.0 - 1.0
    needs_review   INTEGER NOT NULL DEFAULT 0,
    review_reason  TEXT,
    probabilities  TEXT    NOT NULL,     -- JSON list of {category, probability}
    extracted_text TEXT    NOT NULL,
    word_count     INTEGER NOT NULL,
    created_at     TEXT    NOT NULL      -- ISO-8601, UTC
);
CREATE INDEX IF NOT EXISTS idx_documents_created ON documents (created_at);
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents (category);
"""


def init_db() -> None:
    """Create the database file and tables if they do not exist yet."""
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA)


@contextmanager
def get_connection():
    conn = sqlite3.connect(settings.database_path, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
