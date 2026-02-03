import os
from typing import Dict, List, Optional, Union

from openai import OpenAI

from src.llm.client.base import BaseClient
from src.llm.types import NotGiven, NOT_GIVEN
from src.utils.log import logger


class ZhipuClient(BaseClient):
    """Zhipu client for chat models."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("ZHIPUAI_API_KEY")
        # 默认使用 Claude API 兼容接口
        self.api_type = os.getenv("ZHIPUAI_API_TYPE", "claude")  # claude 或 openai
        
        # 根据 API 类型设置对应的 baseurl
        if self.api_type == "openai":
            self.base_url = os.getenv("ZHIPUAI_API_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
        else:  # 默认使用 Claude API
            self.base_url = os.getenv("ZHIPUAI_API_BASE_URL", "https://open.bigmodel.cn/api/anthropic")
            
        if not self.api_key:
            raise ValueError("API key is required. Please provide it or set it in the environment variables.")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.default_model = os.getenv("ZHIPUAI_API_MODEL", "glm-4.7")
        logger.info(f"Zhipu client initialized with API type: {self.api_type}, base_url: {self.base_url}, model: {self.default_model}")

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
            return completion.choices[0].message.content
        else:
            logger.error("LLM returned no response")
            raise Exception("LLM returned no response")
