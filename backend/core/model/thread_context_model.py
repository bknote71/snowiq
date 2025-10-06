from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class MessageModel(BaseModel):
    """단일 대화 메시지"""

    role: str  # 'user' 또는 'assistant'
    content: str  # 메시지 내용
    timestamp: datetime  # 메시지 생성 시각


class ThreadContextModel(BaseModel):
    """스레드별 대화 컨텍스트 (요약 + 최근 대화)"""

    thread_id: str
    summary: Optional[str] = None  # 전체 대화 요약 (summary_agent 가 업데이트)
    recent_messages: list[MessageModel] = []  # 최근 메시지 N개
    updated_at: datetime = datetime.utcnow()  # 마지막 업데이트 시각
