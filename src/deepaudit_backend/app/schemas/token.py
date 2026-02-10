"""
令牌模式
"""
from pydantic import BaseModel


class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """令牌载荷"""
    sub: str = None
    exp: int = None
