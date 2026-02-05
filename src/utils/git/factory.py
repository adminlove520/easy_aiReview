from src.utils.git.gitea import GiteaGitClient
from src.utils.git.github import GitHubGitClient
from src.utils.git.gitlab import GitLabGitClient
from src.utils.log import logger


class GitClientFactory:
    """Git客户端工厂类"""

    # 服务类型到客户端类的映射
    _client_map = {
        'gitea': GiteaGitClient,
        'github': GitHubGitClient,
        'gitlab': GitLabGitClient
    }

    @classmethod
    def get_client(cls, service_type: str, credentials: dict = None) -> object:
        """获取Git客户端实例

        Args:
            service_type: Git服务类型，支持 'gitea', 'github', 'gitlab'
            credentials: 认证信息字典

        Returns:
            Git客户端实例
        """
        if service_type not in cls._client_map:
            logger.error(f"不支持的Git服务类型: {service_type}")
            return None

        try:
            # 创建客户端实例
            client_class = cls._client_map[service_type]
            client = client_class()

            # 设置认证信息
            if credentials:
                client.set_credentials(credentials)

            logger.info(f"成功创建{service_type} Git客户端实例")
            return client
        except Exception as e:
            logger.error(f"创建Git客户端失败: {e}")
            return None
