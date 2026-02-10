"""
数据库初始化
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import Base, engine
from app.models.user import User
from app.core.security import get_password_hash


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    """
    初始化数据库
    """
    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 检查是否已有用户
    result = await db.execute(User.__table__.select().limit(1))
    user = result.scalar_one_or_none()
    
    if not user:
        # 创建默认管理员用户
        admin_user = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
            role="admin"
        )
        db.add(admin_user)
        
        # 创建演示用户
        demo_user = User(
            email="demo@example.com",
            hashed_password=get_password_hash("demo123"),
            full_name="Demo User",
            is_active=True,
            is_superuser=False,
            role="member"
        )
        db.add(demo_user)
        
        await db.commit()
        logger.info("数据库初始化完成，创建了默认用户")
    else:
        logger.info("数据库已存在用户，跳过初始化")
