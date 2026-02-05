from abc import ABC, abstractmethod
from typing import Optional


class BaseGitClient(ABC):
    """Git操作抽象基类"""

    @abstractmethod
    def clone_repository(self, repo_url: str, local_path: str) -> bool:
        """克隆仓库"""
        pass

    @abstractmethod
    def commit_and_push(self, local_path: str, message: str) -> bool:
        """提交并推送代码"""
        pass

    @abstractmethod
    def create_repository(self, repo_name: str, description: str = "") -> bool:
        """创建仓库"""
        pass

    @abstractmethod
    def repository_exists(self, repo_name: str) -> bool:
        """检查仓库是否存在"""
        pass

    @abstractmethod
    def get_repository_url(self, repo_name: str) -> str:
        """获取仓库URL"""
        pass

    @abstractmethod
    def set_credentials(self, credentials: dict) -> None:
        """设置认证信息"""
        pass
