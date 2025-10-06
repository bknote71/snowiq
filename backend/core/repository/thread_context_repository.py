import sqlite3
import json
from datetime import datetime

from core.model.thread_context_model import ThreadContextModel, MessageModel

DB_PATH = "threads.db"


class ThreadContextRepository:
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

    def upsert(self, context: ThreadContextModel):
        with self._connect() as conn:
            messages_json = json.dumps([m.dict() for m in context.messages], ensure_ascii=False)
            conn.execute(
                """
                INSERT INTO thread_contexts (thread_id, summary, messages, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(thread_id) DO UPDATE SET
                    summary = excluded.summary,
                    messages = excluded.messages,
                    updated_at = excluded.updated_at
            """,
                (context.thread_id, context.summary, messages_json, context.updated_at.isoformat()),
            )
            conn.commit()

    def find_by_thread_id(self, thread_id: str) -> ThreadContextModel | None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT thread_id, summary, messages, updated_at FROM thread_contexts WHERE thread_id = ?", (thread_id,))
            row = cur.fetchone()
            if not row:
                return None

            messages_data = json.loads(row[2] or "[]")
            messages = [MessageModel(**m) for m in messages_data]

            return ThreadContextModel(
                thread_id=row[0],
                summary=row[1],
                messages=messages,
                updated_at=datetime.fromisoformat(row[3]) if row[3] else datetime.utcnow(),
            )


thread_context_repository = ThreadContextRepository()
