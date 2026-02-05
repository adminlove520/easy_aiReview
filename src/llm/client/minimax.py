import os
from typing import Dict, List, Optional, Union

from openai import OpenAI

from src.llm.client.base import BaseClient
from src.llm.types import NotGiven, NOT_GIVEN
from src.utils.log import logger


class MiniMaxClient(BaseClient):
    """MiniMax client for chat models."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.base_url = os.getenv("MINIMAX_API_BASE_URL", "https://api.minimaxi.com/v1")
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set it in the environment variables.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.default_model = os.getenv("MINIMAX_API_MODEL", "MiniMax-M2.1")
        logger.info(f"MiniMax client initialized with base_url: {self.base_url}, model: {self.default_model}")

    def completions(self, 
                    messages: List[Dict[str, str]], 
                    model: Union[Optional[str], NotGiven] = NOT_GIVEN,
                    ) -> str:
        model = model or self.default_model
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        if completion and completion.choices and len(completion.choices) > 0:
            content = completion.choices[0].message.content
            
            # 处理ping请求：如果消息是"请仅返回 'ok'。"，确保返回的内容只包含"ok"
            if messages and len(messages) > 0:
                user_content = messages[0].get('content', '')
                if '请仅返回 "ok"' in user_content or "请仅返回 'ok'" in user_content:
                    # 提取"ok"部分
                    if 'ok' in content:
                        return 'ok'
            
            # 其他情况直接返回响应内容
            return content
        else:
            logger.error("LLM returned no response")
            raise Exception("LLM returned no response")