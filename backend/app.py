import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import plotly.express as px
import pandas as pd
import json

from data.snowflake_connector import start_periodic_fetch
from data.cache import cache

from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.query_agent import QueryAgent
from agents.analysis_agent import AnalysisAgent
from agents.insight_agent import InsightAgent

app = FastAPI(title="snowiq-backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # asyncio.create_task(start_periodic_fetch(interval_sec=10))
    return

@app.get("/chart")
def get_chart():
    df = cache.get("live_df")
    if df is None:
        return { "error":"데이터 로딩 중.." }
    
    # todo: agent가 fig 생성
    fig = px.line(df, x="date", y="sales", title="실시간 매출 추이")
    return json.loads(fig.to_json())

@app.post("/insight")
async def get_insight(request: Request):
    body = await request.json()
    user_question = body["prompt"] # 아무 내용도 없으면 그냥 반환하도록 하자.

    if not user_question:
        return {}

    # 더미 데이터
    df = pd.DataFrame({
        "category": ["A", "B", "A", "C", "B", "C", "A"],
        "sales": [100, 200, 150, 50, 300, 120, 180],
        "date": pd.date_range("2025-10-01", periods=7),
    })
    cache.set("live_df", df)

    # llm 초기화
    api_key = os.getenv("GEMINI_API_KEY")
    llm = OpenAIChatCompletionClient(model="gemini-2.5-flash", api_key=api_key)

    query_agent = QueryAgent(llm)
    analysis_agent = AnalysisAgent(llm)
    insight_agent = InsightAgent(llm)

    query_response = await query_agent.run(user_question)
    analysis_result = await analysis_agent.run(df, query_response)
    insight_result = await insight_agent.run(analysis_result)

    return {
        "query": query_response,
        "analysis": analysis_result,
        "insight": insight_result
    }
