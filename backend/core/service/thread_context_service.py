from datetime import datetime

from core.model.thread_context_model import ThreadContextModel, MessageModel
from core.repository.thread_context_repository import thread_context_repository
from agents.summary_agent import SummaryAgent
from utils.prompt_templates import prompt_templates

MAX_RECENT_MESSAGES = 10


class ThreadContextService:
    def __init__(self, summary_agent: SummaryAgent):
        self.summary_agent = summary_agent

    def get_context(self, thread_id: str) -> ThreadContextModel:
        return thread_context_repository.find_by_thread_id(thread_id)

    async def update_context(self, thread_id: str, user_msg: str, assistant_msg: str):
        context = self.get_context(thread_id)

        context.messages.append(MessageModel(role="user", content=user_msg, timestamp=datetime.utcnow()))
        context.messages.append(MessageModel(role="assistant", content=assistant_msg, timestamp=datetime.utcnow()))

        old_summary = context.summary or "(none)"
        recent_subset = context.messages[-MAX_RECENT_MESSAGES:]
        recent_text = "\n".join([f"{m.role}: {m.content}" for m in recent_subset])

        new_summary = await self.summary_agent.run(old_summary, recent_text)
        context.summary = new_summary

        context.updated_at = datetime.utcnow()
        thread_context_repository.upsert(context)

        return context
