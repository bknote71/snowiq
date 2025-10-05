import asyncio
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

from autogen_ext.models.openai import OpenAIChatCompletionClient
from agents.query_agent import QueryAgent
from agents.analysis_agent import AnalysisAgent
from agents.insight_agent import InsightAgent
from data.cache import cache


async def main():
    # 1️⃣ 더미 데이터프레임 생성
    df = pd.DataFrame(
        {
            "category": ["A", "B", "A", "C", "B", "C", "A"],
            "sales": [100, 200, 150, 50, 300, 120, 180],
            "date": pd.date_range("2025-10-01", periods=7),
        }
    )
    cache.set("live_df", df)
    print("✅ Dummy DataFrame loaded into cache\n", df.head(), "\n")

    # 2️⃣ LLM 클라이언트 초기화
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"api_key is {api_key}")

    llm = OpenAIChatCompletionClient(model="gemini-2.5-flash", api_key=api_key)  # 테스트용 빠른 모델

    # 3️⃣ 에이전트 초기화
    query_agent = QueryAgent(llm)
    analysis_agent = AnalysisAgent(llm)
    insight_agent = InsightAgent(llm)

    # 4️⃣ 테스트 입력
    user_question = "Which category has the highest total sales?"

    print(f"🧠 User question: {user_question}\n")

    # 5️⃣ QueryAgent 실행 (DataFrame 기반 reasoning)
    query_response = await query_agent.run(user_question)
    print("🤖 QueryAgent Response:\n", query_response, "\n")

    # 6️⃣ AnalysisAgent 실행
    analysis_result = await analysis_agent.run(df)
    print("📊 AnalysisAgent Result:\n", analysis_result, "\n")

    # 7️⃣ InsightAgent 실행
    insight_result = await insight_agent.run(analysis_result)
    print("💡 InsightAgent Result:\n", insight_result, "\n")


if __name__ == "__main__":
    asyncio.run(main())
