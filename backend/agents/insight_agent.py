from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from utils.prompt_templates import prompt_templates
from utils.logger import logger


class InsightAgent(AssistantAgent):
    def __init__(self, llm_client: OpenAIChatCompletionClient):
        super().__init__(name="InsightAgent", model_client=llm_client)
        self.llm_client = llm_client

    async def run(self, analysis_summary: str):
        try:
            prompt = prompt_templates["insight_generation"].format(analysis_summary=analysis_summary)
            message = TextMessage(content=prompt, source="user")
            logger.info("💡 [InsightAgent] Generating insights...")
            response = await self.on_messages([message], cancellation_token=None)
            return response.chat_message.content
        except Exception as e:
            logger.error(f"[InsightAgent] Error: {e}")
            return "Insight generation failed."
