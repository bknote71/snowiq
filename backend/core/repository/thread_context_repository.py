from core.model.thread_context_model import ThreadContextModel, Message


class ThreadContextRepository:
    def find_by_thread_id(thread_id: str):
        return ThreadContextModel()

    def update(context: ThreadContextModel):
        pass


thread_context_repository = ThreadContextRepository()
