from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from utils.prompt_templates import prompt_templates
from utils.logger import logger

import pandas as pd
import io


class AnalysisAgent(AssistantAgent):
    def __init__(self, llm_client: OpenAIChatCompletionClient):
        super().__init__(name="AnalysisAgent", model_client=llm_client)
        self.llm_client = llm_client

    async def run(self, df: pd.DataFrame, query_context: str):
        try:
            if df is None or df.empty:
                return "⚠️ No data available for analysis."

            buffer = io.StringIO()
            summary = (
                f"Columns: {list(df.columns)}\n\n"
                f"Sample rows:\n{df.head(5).to_string(index=False)}\n\n"
                f"Summary statistics:\n{df.describe(include='all').to_string()}"
            )
            buffer.write(summary)

            prompt = (
                prompt_templates["data_analysis"].format(data_description=buffer.getvalue())
                + 
                f"\n\nIMPORTANT:\n"
                f"Use the following reasoning or query context as your primary guide for analysis.\n"
                f"Focus strictly on this context when interpreting the data.\n"
                f"Query context:\n{query_context}"
            )

            message = TextMessage(content=prompt, source="user")
            logger.info("📈 [AnalysisAgent] Running analysis...")
            response = await self.on_messages([message], cancellation_token=None)
            return response.chat_message.content

        except Exception as e:
            logger.error(f"[AnalysisAgent] Error: {e}")
            return "An error occurred during analysis."
