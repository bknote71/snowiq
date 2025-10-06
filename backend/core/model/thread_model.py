from pydantic import BaseModel
from datetime import datetime

# BaseModel: 입력값 검증 + 자동 변환 + 문서화까지 처리해주는 강력한 객체라고 함.


class ThreadModel(BaseModel):
    thread_id: str
    schema_name: str
    table_name: str
    created_at: datetime | None = None


class CreateThreadRequest(BaseModel):
    schema: str
    table_name: str
