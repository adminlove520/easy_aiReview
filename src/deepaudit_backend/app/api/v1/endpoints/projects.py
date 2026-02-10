"""
项目管理相关 API 端点
"""
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User


router = APIRouter()


@router.get("/", response_model=List[dict])
async def get_projects(
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    获取所有项目
    """
    # 模拟数据
    projects = [
        {
            "id": 1,
            "name": "测试项目",
            "description": "这是一个测试项目",
            "source_type": "local",
            "repo_url": "",
            "local_path": "C:/test",
            "created_at": "2026-02-10T00:00:00Z",
            "updated_at": "2026-02-10T00:00:00Z",
            "is_active": True,
            "created_by": current_user.id
        }
    ]
    return projects


@router.get("/{project_id}", response_model=dict)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    获取项目详情
    """
    # 模拟数据
    project = {
        "id": project_id,
        "name": "测试项目",
        "description": "这是一个测试项目",
        "source_type": "local",
        "repo_url": "",
        "local_path": "C:/test",
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z",
        "is_active": True,
        "created_by": current_user.id
    }
    return project


@router.post("/", response_model=dict)
async def create_project(
    *, 
    db: AsyncSession = Depends(deps.get_db),
    project_in: dict,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    创建新项目
    """
    # 模拟创建
    new_project = {
        "id": 2,
        "name": project_in.get("name", "新项目"),
        "description": project_in.get("description", ""),
        "source_type": project_in.get("source_type", "local"),
        "repo_url": project_in.get("repo_url", ""),
        "local_path": project_in.get("local_path", ""),
        "is_active": True,
        "created_by": current_user.id,
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z"
    }
    return new_project


@router.put("/{project_id}", response_model=dict)
async def update_project(
    project_id: int,
    *, 
    db: AsyncSession = Depends(deps.get_db),
    project_in: dict,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    更新项目
    """
    # 模拟更新
    updated_project = {
        "id": project_id,
        "name": project_in.get("name", "测试项目"),
        "description": project_in.get("description", "这是一个测试项目"),
        "source_type": project_in.get("source_type", "local"),
        "repo_url": project_in.get("repo_url", ""),
        "local_path": project_in.get("local_path", "C:/test"),
        "is_active": project_in.get("is_active", True),
        "created_by": current_user.id,
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z"
    }
    return updated_project


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    删除项目
    """
    return {"message": "项目删除成功"}


@router.get("/{project_id}/files", response_model=List[dict])
async def get_project_files(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    获取项目文件
    """
    return []


@router.get("/{project_id}/branches", response_model=List[dict])
async def get_project_branches(
    project_id: int,
    db: AsyncSession = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    获取项目分支
    """
    return [{"name": "main"}]
