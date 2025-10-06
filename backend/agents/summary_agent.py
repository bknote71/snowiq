from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
from utils.prompt_templates import prompt_templates
from utils.logger import logger


class SummaryAgent(AssistantAgent):
    def __init__(self, llm_client: OpenAIChatCompletionClient):
        super().__init__(name="SummaryAgent", model_client=llm_client)
        self.llm_cliet = llm_client

    async def run(self):
        pass
