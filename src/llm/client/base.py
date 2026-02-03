from abc import abstractmethod
from typing import List, Dict, Optional, Union

from src.llm.types import NotGiven, NOT_GIVEN
from src.utils.log import logger


class BaseClient:
    """ Base class for chat models client. """

    def ping(self) -> bool:
        """Ping the model to check connectivity."""
        try:
            result = self.completions(messages=[{"role": "user", "content": '请仅返回 "ok"。'}])
            return result and result == 'ok'
        except Exception as e:
            logger.error(f"尝试连接LLM失败， {e}")
            return False

    @abstractmethod
    def completions(self,
                    messages: List[Dict[str, str]],
                    model: Union[Optional[str], NotGiven] = NOT_GIVEN,
                    ) -> str:
        """Chat with the model.
        """
