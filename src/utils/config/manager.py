"""配置管理核心模块"""
import os
from typing import Any, Optional

from src.utils.log import logger
from src.utils.error import ConfigError


class ConfigManager:
    """配置管理器类"""

    def __init__(self):
        """初始化配置管理器"""
        self._config = {}
        self._loaded = False
        self._load_config()

    def _load_config(self):
        """加载配置"""
        if self._loaded:
            return

        try:
            # 加载环境变量配置
            self._load_from_env()
            self._loaded = True
            logger.info("配置加载成功")
        except ConfigError as e:
            logger.error(f"配置加载失败: {e}")
            self._loaded = False
        except Exception as e:
            logger.error(f"配置加载失败: {e}")
            self._loaded = False

    def _load_from_env(self):
        """从环境变量加载配置"""
        # 服务配置
        self._config['SERVER_PORT'] = os.environ.get('SERVER_PORT', '5001')
        
        # 大模型配置
        self._config['LLM_PROVIDER'] = os.environ.get('LLM_PROVIDER', 'minimax')
        self._config['DEEPSEEK_API_KEY'] = os.environ.get('DEEPSEEK_API_KEY', '')
        self._config['DEEPSEEK_API_BASE_URL'] = os.environ.get('DEEPSEEK_API_BASE_URL', 'https://api.deepseek.com')
        self._config['DEEPSEEK_API_MODEL'] = os.environ.get('DEEPSEEK_API_MODEL', 'deepseek-chat')
        self._config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')
        self._config['OPENAI_API_BASE_URL'] = os.environ.get('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
        self._config['OPENAI_API_MODEL'] = os.environ.get('OPENAI_API_MODEL', 'gpt-4o-mini')
        self._config['ZHIPUAI_API_KEY'] = os.environ.get('ZHIPUAI_API_KEY', '')
        self._config['ZHIPUAI_API_BASE_URL'] = os.environ.get('ZHIPUAI_API_BASE_URL', 'https://open.bigmodel.cn/api/paas/v4/')
        self._config['ZHIPUAI_API_MODEL'] = os.environ.get('ZHIPUAI_API_MODEL', 'glm-4.7')
        self._config['MINIMAX_API_KEY'] = os.environ.get('MINIMAX_API_KEY', '')
        self._config['MINIMAX_API_BASE_URL'] = os.environ.get('MINIMAX_API_BASE_URL', 'https://api.minimaxi.com/v1')
        self._config['MINIMAX_API_MODEL'] = os.environ.get('MINIMAX_API_MODEL', 'MiniMax-M2.1')
        self._config['QWEN_API_KEY'] = os.environ.get('QWEN_API_KEY', '')
        self._config['QWEN_API_BASE_URL'] = os.environ.get('QWEN_API_BASE_URL', 'https://dashscope.aliyuncs.com/compatible-mode/v1')
        self._config['QWEN_API_MODEL'] = os.environ.get('QWEN_API_MODEL', 'qwen-coder-plus')
        self._config['OLLAMA_API_BASE_URL'] = os.environ.get('OLLAMA_API_BASE_URL', 'http://host.docker.internal:11434')
        self._config['OLLAMA_API_MODEL'] = os.environ.get('OLLAMA_API_MODEL', 'deepseek-r1:latest')
        
        # 代码审查配置
        self._config['SUPPORTED_EXTENSIONS'] = os.environ.get('SUPPORTED_EXTENSIONS', '.c,.cc,.cpp,.css,.go,.h,.java,.js,.jsx,.ts,.tsx,.md,.php,.py,.sql,.vue,.yml')
        self._config['REVIEW_MAX_TOKENS'] = os.environ.get('REVIEW_MAX_TOKENS', '10000')
        self._config['REVIEW_STYLE'] = os.environ.get('REVIEW_STYLE', 'professional')
        
        # 通知配置
        self._config['DINGTALK_ENABLED'] = os.environ.get('DINGTALK_ENABLED', '1')
        self._config['DINGTALK_WEBHOOK_URL'] = os.environ.get('DINGTALK_WEBHOOK_URL', '')
        self._config['DINGTALK_SECRET'] = os.environ.get('DINGTALK_SECRET', '')
        self._config['WECOM_ENABLED'] = os.environ.get('WECOM_ENABLED', '0')
        self._config['WECOM_WEBHOOK_URL'] = os.environ.get('WECOM_WEBHOOK_URL', '')
        self._config['FEISHU_ENABLED'] = os.environ.get('FEISHU_ENABLED', '0')
        self._config['FEISHU_WEBHOOK_URL'] = os.environ.get('FEISHU_WEBHOOK_URL', '')
        self._config['EXTRA_WEBHOOK_ENABLED'] = os.environ.get('EXTRA_WEBHOOK_ENABLED', '0')
        self._config['EXTRA_WEBHOOK_URL'] = os.environ.get('EXTRA_WEBHOOK_URL', '')
        
        # 日志配置
        self._config['LOG_FILE'] = os.environ.get('LOG_FILE', 'log/app.log')
        self._config['LOG_MAX_BYTES'] = os.environ.get('LOG_MAX_BYTES', '10485760')
        self._config['LOG_BACKUP_COUNT'] = os.environ.get('LOG_BACKUP_COUNT', '3')
        self._config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'DEBUG')
        
        # 日报配置
        self._config['REPORT_CRONTAB_EXPRESSION'] = os.environ.get('REPORT_CRONTAB_EXPRESSION', '0 18 * * 1-5')
        self._config['GIT_SERVICE_TYPE'] = os.environ.get('GIT_SERVICE_TYPE', 'gitea')
        self._config['GIT_REPO_NAME'] = os.environ.get('GIT_REPO_NAME', 'aiReview_dailyReport')
        
        # Git服务配置
        # GitLab
        self._config['GITLAB_URL'] = os.environ.get('GITLAB_URL', 'https://gitlab.com')
        self._config['GITLAB_ACCESS_TOKEN'] = os.environ.get('GITLAB_ACCESS_TOKEN', '')
        self._config['GITLAB_REPO_OWNER'] = os.environ.get('GITLAB_REPO_OWNER', '')
        
        # GitHub
        self._config['GITHUB_URL'] = os.environ.get('GITHUB_URL', 'https://github.com')
        self._config['GITHUB_ACCESS_TOKEN'] = os.environ.get('GITHUB_ACCESS_TOKEN', '')
        self._config['GITHUB_REPO_OWNER'] = os.environ.get('GITHUB_REPO_OWNER', '')
        
        # Gitea
        self._config['GITEA_URL'] = os.environ.get('GITEA_URL', 'https://git.nxwysoft.com')
        self._config['GITEA_ACCESS_TOKEN'] = os.environ.get('GITEA_ACCESS_TOKEN', '')
        self._config['GITEA_REPO_OWNER'] = os.environ.get('GITEA_REPO_OWNER', '')
        self._config['GITEA_WEBHOOK_SECRET'] = os.environ.get('GITEA_WEBHOOK_SECRET', '')
        
        # 其他配置
        self._config['PUSH_REVIEW_ENABLED'] = os.environ.get('PUSH_REVIEW_ENABLED', '1')
        self._config['MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED'] = os.environ.get('MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED', '0')
        self._config['DASHBOARD_USER'] = os.environ.get('DASHBOARD_USER', 'admin')
        self._config['DASHBOARD_PASSWORD'] = os.environ.get('DASHBOARD_PASSWORD', 'admin')
        self._config['QUEUE_DRIVER'] = os.environ.get('QUEUE_DRIVER', 'async')
        self._config['WORKER_QUEUE'] = os.environ.get('WORKER_QUEUE', 'git_test_com')

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            配置值或默认值
        """
        if not self._loaded:
            self._load_config()
        return self._config.get(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔类型配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            布尔类型配置值
        """
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'y', 'on')
        return bool(value)

    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数类型配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            整数类型配置值
        """
        value = self.get(key, default)
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                return int(value)
            except ValueError:
                return default
        return int(value)

    def reload(self):
        """重新加载配置"""
        self._loaded = False
        self._load_config()
        logger.info("配置重新加载成功")
