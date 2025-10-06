from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from utils.prompt_templates import prompt_templates
from utils.logger import logger
from core.cache import cache

import pandas as pd
import io


class QueryAgent(AssistantAgent):
    def __init__(self, llm_client: OpenAIChatCompletionClient):
        super().__init__(name="QueryAgent", model_client=llm_client)
        self.llm_cliet = llm_client

    async def run(self, user_question: str, schema_info: str = ""):
        try:
            df: pd.DataFrame = cache.get("live_df")
            if df is None or df.empty:
                return "⚠️ No live data available yet."

            buffer = io.StringIO()
            summary = (
                f"Columns: {list(df.columns)}\n\n"
                f"Sample rows:\n{df.head(5).to_string(index=False)}\n\n"
                f"Summary statistics:\n{df.describe(include="all").to_string()}"
            )

            buffer.write(summary)

            prompt = prompt_templates["df_query"].format(user_question=user_question, data_overview=buffer.getvalue())
            message = TextMessage(content=prompt, source="user")

            logger.info("🤖 [QueryAgent] Running DataFrame-based reasoning...")
            response = await self.on_messages([message], cancellation_token=None)
            return response.chat_message.content

        except Exception as e:
            logger.error(f"[QueryAgent] Error: {e}")
            return "An error occurred while analyzing the data."
