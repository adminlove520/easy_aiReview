import os

from src.llm.client.base import BaseClient
from src.llm.client.deepseek import DeepSeekClient
from src.llm.client.openai import OpenAIClient
from src.llm.client.qwen import QwenClient
from src.llm.client.zhipu import ZhipuClient
from src.llm.client.minimax import MiniMaxClient
from src.utils.log import logger



class Factory:
    @staticmethod
    def getClient(provider: str = None) -> BaseClient:
        provider = provider or os.getenv("LLM_PROVIDER", "openai")
        chat_model_providers = {
            'openai': lambda: OpenAIClient(),
            'deepseek': lambda: DeepSeekClient(),
            'qwen': lambda: QwenClient(),
            'zhipu': lambda: ZhipuClient(),
            'zhipuai': lambda: ZhipuClient(),
            'minimax': lambda: MiniMaxClient(),
        }

        provider_func = chat_model_providers.get(provider)
        if provider_func:
            return provider_func()
        else:
            raise Exception(f'Unknown chat model provider: {provider}')
