"""依赖注入容器"""
from typing import Dict, Type, Any, Optional, Callable


class Container:
    """依赖注入容器类"""

    def __init__(self):
        """初始化容器"""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}

    def register(self, service_type: Type, instance: Any) -> None:
        """注册服务实例

        Args:
            service_type: 服务类型
            instance: 服务实例
        """
        self._services[service_type] = instance

    def register_factory(self, service_type: Type, factory: Callable) -> None:
        """注册服务工厂

        Args:
            service_type: 服务类型
            factory: 服务工厂函数
        """
        self._factories[service_type] = factory

    def resolve(self, service_type: Type) -> Optional[Any]:
        """解析服务

        Args:
            service_type: 服务类型

        Returns:
            Optional[Any]: 服务实例或None
        """
        # 优先从已注册的服务中获取
        if service_type in self._services:
            return self._services[service_type]

        # 从工厂中创建服务
        if service_type in self._factories:
            instance = self._factories[service_type]()
            # 缓存实例
            self._services[service_type] = instance
            return instance

        return None

    def clear(self) -> None:
        """清空容器"""
        self._services.clear()
        self._factories.clear()

    def has(self, service_type: Type) -> bool:
        """检查服务是否已注册

        Args:
            service_type: 服务类型

        Returns:
            bool: 是否已注册
        """
        return service_type in self._services or service_type in self._factories
