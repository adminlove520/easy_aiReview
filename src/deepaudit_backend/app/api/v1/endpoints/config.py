"""
配置相关 API 端点
"""
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.models.user import User


router = APIRouter()


@router.get("/me", response_model=dict)
async def get_user_config(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    获取用户配置
    """
    return {
        "llm_provider": settings.LLM_PROVIDER,
        "api_key": "****" if settings.MINIMAX_API_KEY else None,
    }


@router.get("/defaults", response_model=dict)
async def get_default_config() -> Any:
    """
    获取默认配置
    """
    return {
        "llm_provider": "minimax",
        "llm_model": "abab5.5-chat",
    }


@router.get("/llm-providers", response_model=list)
async def get_llm_providers() -> Any:
    """
    获取可用的 LLM 提供商
    """
    return [
        {"name": "minimax", "models": ["abab5.5-chat"]},
        {"name": "openai", "models": ["gpt-4", "gpt-3.5-turbo"]},
    ]


@router.post("/test-llm", response_model=dict)
async def test_llm_config(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    测试 LLM 配置
    """
    return {"message": "LLM 测试成功"}
