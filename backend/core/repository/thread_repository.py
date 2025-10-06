import sqlite3
from datetime import datetime
from core.model.thread_model import ThreadModel

DB_PATH = "threads.db"


class ThreadRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS thread_contexts (
                    thread_id TEXT PRIMARY KEY,
                    summary TEXT,
                    messages TEXT,
                    updated_at TEXT
                )
            """
            )
            conn.commit()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def upsert(self, thread: ThreadModel):
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO threads (thread_id, schema_name, table_name, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    schema_name = excluded.schema_name,
                    table_name = excluded.table_name,
                    created_at = excluded.created_at
            """,
                (thread.thread_id, thread.schema_name, thread.table_name, (thread.created_at or datetime.utcnow()).isoformat()),
            )
            conn.commit()

    def find_by_id(self, thread_id: str) -> ThreadModel:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT thread_id, schema_name, table_name, created_at FROM threads WHERE thread_id = ?", (thread_id,))
            row = cur.fetchone()
            if not row:
                return None
            return ThreadModel(
                thread_id=row[0], schema_name=row[1], table_name=row[2], created_at=datetime.fromisoformat(row[3]) if row[3] else None
            )


thread_repository = ThreadRepository()
