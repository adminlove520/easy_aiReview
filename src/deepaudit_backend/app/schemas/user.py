"""
用户模式
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模式"""
    email: EmailStr
    full_name: str
    is_active: Optional[bool] = True
    is_superuser: bool = False
    role: str = "member"


class UserCreate(UserBase):
    """用户创建模式"""
    password: str = Field(..., min_length=6)


class UserUpdate(UserBase):
    """用户更新模式"""
    password: Optional[str] = Field(None, min_length=6)


class User(UserBase):
    """用户响应模式"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
