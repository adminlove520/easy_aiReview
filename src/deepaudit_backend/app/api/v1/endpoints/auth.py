"""
认证相关 API 端点
"""
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel, EmailStr

from app.api import deps
from app.core import security
from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import User as UserSchema, UserCreate


router = APIRouter()


class RegisterRequest(BaseModel):
    """注册请求模式"""
    email: EmailStr
    password: str
    full_name: str


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    request: Request = None
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username field should contain the email address.
    """
    username = None
    password = None
    
    # 尝试从请求体中获取数据
    if request and request.method == "POST":
        # 尝试解析 JSON 格式的请求
        try:
            json_data = await request.json()
            if json_data:
                username = json_data.get("username") or json_data.get("email")
                password = json_data.get("password")
        except:
            # 尝试解析表单数据格式的请求
            try:
                form_data = await request.form()
                if form_data:
                    username = form_data.get("username") or form_data.get("email")
                    password = form_data.get("password")
            except:
                # 尝试获取原始请求体数据
                try:
                    body = await request.body()
                    if body:
                        # 尝试解析 URL 编码的表单数据
                        from urllib.parse import parse_qs
                        parsed_data = parse_qs(body.decode('utf-8'))
                        if parsed_data:
                            username = parsed_data.get("username", [None])[0] or parsed_data.get("email", [None])[0]
                            password = parsed_data.get("password", [None])[0]
                except:
                    pass
    
    # 验证用户名和密码
    if not username or not password:
        raise HTTPException(status_code=400, detail="用户名和密码不能为空")
    
    result = await db.execute(select(User).where(User.email == username))
    user = result.scalars().first()
    
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="邮箱或密码错误")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserSchema)
async def register(
    *, 
    db: AsyncSession = Depends(get_db),
    user_in: RegisterRequest,
) -> Any:
    """
    Register a new user.
    """
    # 检查用户是否已存在
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalars().first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="该邮箱已被注册",
        )
    
    # 检查是否是第一个用户（设为管理员）
    count_result = await db.execute(select(User))
    is_first_user = count_result.scalars().all() == []
    
    # 创建新用户
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
        is_active=True,
        is_superuser=is_first_user,
        role="admin" if is_first_user else "member",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
