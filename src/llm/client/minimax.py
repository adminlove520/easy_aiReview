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
                    include_reasoning: bool = False,
                    ) -> str:
        model = model or self.default_model
        
        # 调用API时关闭思维链返回，减少推理内容
        try:
            # 构建API调用参数
            api_params = {
                "model": model,
                "messages": messages,
            }
            
            # 只有当明确要求包含reasoning时才传递参数
            if include_reasoning:
                api_params["extra_body"] = {"include_reasoning": include_reasoning}
            
            completion = self.client.chat.completions.create(**api_params)
        except Exception as e:
            # 如果参数不支持，回退到不带参数的调用
            logger.warning(f"include_reasoning参数不被支持，回退到默认调用: {e}")
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )
            
        if completion and completion.choices and len(completion.choices) > 0:
            raw_content = completion.choices[0].message.content
            
            # 过滤thinking内容（如果返回的是包含thinking的字典）
            if isinstance(raw_content, dict):
                content = raw_content.get("content", str(raw_content))
                thinking = raw_content.get("thinking") or raw_content.get("reasoning_details")
                if thinking:
                    logger.debug("已过滤模型的thinking内容")
                return content
            elif isinstance(raw_content, str):
                # 处理ping请求：如果消息是"请仅返回 'ok'。"，确保返回的内容只包含"ok"
                if messages and len(messages) > 0:
                    user_content = messages[0].get('content', '')
                    if '请仅返回 "ok"' in user_content or "请仅返回 'ok'" in user_content:
                        if 'ok' in raw_content:
                            return 'ok'
                
                return raw_content
            else:
                return str(raw_content)
        else:
            logger.error("LLM returned no response")
            raise Exception("LLM returned no response")