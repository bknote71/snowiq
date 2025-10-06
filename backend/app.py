import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import plotly.express as px
import pandas as pd
import threading
import json

from core.snowflake_connector import start_periodic_fetch
from core.cache import cache

from core.model.thread_model import ThreadModel, CreateThreadRequest
from core.model.thread_context_model import ThreadContextModel

app = FastAPI(title="snowiq-backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

THREAD_REGISTRY: dict[str, threading.Thread] = {}

# register agents

from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.query_agent import QueryAgent
from agents.analysis_agent import AnalysisAgent
from agents.insight_agent import InsightAgent
from agents.summary_agent import SummaryAgent

api_key = os.getenv("GEMINI_API_KEY")
end_mark = "[END]"
llm = OpenAIChatCompletionClient(model="gemini-2.5-flash", api_key=api_key)

query_agent = QueryAgent(llm)
analysis_agent = AnalysisAgent(llm)
insight_agent = InsightAgent(llm)
summary_agent = SummaryAgent(llm)

# register services

from core.service.thread_service import ThreadService
from core.service.thread_context_service import ThreadContextService

thread_service = ThreadService()
thread_context_service = ThreadContextService(summary_agent)

# todo: add router layer


@app.on_event("startup")
async def startup_event():
    # dummy data
    df = pd.DataFrame(
        {
            "category": ["A", "B", "A", "C", "B", "C", "A"],
            "sales": [100, 200, 150, 50, 300, 120, 180],
            "date": pd.date_range("2025-10-01", periods=7),
        }
    )
    cache.set("live_df", df)
    return


@app.post("/api/threads")
def create_thread(req: CreateThreadRequest):
    thread: ThreadModel = thread_service.create_thread(req.schema, req.table_name)
    return thread


@app.get("/api/threads")
def get_thread(thread_id: str):
    thread: ThreadModel = thread_service.get_therad(thread_id)
    thread_context: ThreadContextModel = thread_context_service.get_context(thread_id)

    response = {
        "thread_id": thread.thread_id,
        "schema_name": thread.schema_name,
        "table_name": thread.table_name,
        "messages": thread_context.messages,
    }

    return response


@app.get("/chart")
def get_chart():
    df = cache.get("live_df")
    if df is None:
        return {"error": "데이터 로딩 중.."}

    # todo: agent가 fig 생성
    fig = px.line(df, x="date", y="sales", title="실시간 매출 추이")
    return json.loads(fig.to_json())


@app.websocket("/chat/{thread_id}")
async def websocket_insight(websocket: WebSocket, thread_id: str):
    await websocket.accept()

    thread = thread_service.get_therad()
    first = True

    try:
        while True:
            data = await websocket.receive_text()
            user_question = data.strip()
            if not user_question:
                await websocket.send_text(json.dumps({}))
                continue

            if first:
                fetch_thread: threading.Thread = start_periodic_fetch(
                    name=thread.thread_id, query_factory=lambda: f"SELECT * FROM {thread.schema_name}.{thread.table_name};"
                )

                THREAD_REGISTRY[thread_id] = fetch_thread
                first = False

            df: pd.DataFrame = cache.get(f"live_df_{thread_id}") or cache.get("live_df")

            query_response = await query_agent.run(user_question)
            analysis_result = await analysis_agent.run(df, query_response)
            insight_result = await insight_agent.run(analysis_result)

            response = {"query": query_response, "analysis": analysis_result, "insight": insight_result}

            # update context
            assistant_message = f"Analysis Result: {analysis_result}\n\nInsight: {insight_result}"
            await thread_context_service.update_context(thread_id=thread_id, user_msg=user_question, assitant_msg=assistant_message)

            await websocket.send_text(json.dumps(response))
            await websocket.send_text(end_mark)

    except WebSocketDisconnect:
        # daemon thread의 경우 참조를 제거하면 GC에 의해서 정리된다고 합니다.
        # - 정말일까나~?
        THREAD_REGISTRY.pop(thread_id, None)
        print("WebSocket disconnected")
