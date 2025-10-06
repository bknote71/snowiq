from datetime import datetime
import uuid
from core.model.thread_model import ThreadModel
from core.repository.thread_repository import thread_repository


class ThreadService:
    def create_thread(schema: str, table_name: str) -> ThreadModel:
        if not schema or not table_name:
            return ValueError("schema와 table_name은 필수입니다.")

        new_thread = ThreadModel(thread_id=uuid.uuid4(), schema_name=schema, table_name=table_name, created_at=datetime.utcnow())
        thread_repository.save(new_thread)

        return new_thread
