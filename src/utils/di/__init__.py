"""依赖注入模块"""
from src.utils.di.container import Container

# 依赖注入容器实例
container = Container()

# 导出依赖注入相关功能
__all__ = ['container']
