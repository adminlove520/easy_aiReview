"""配置验证模块"""
from typing import List, Dict, Optional

from src.utils.log import logger
from src.utils.config import config_manager
from src.utils.error import ConfigValidationError


class ConfigValidator:
    """配置验证器类"""

    # 必要配置项
    _required_configs = {
        'gitea': [
            'GITEA_ACCESS_TOKEN',
            'GITEA_URL'
        ],
        'github': [
            'GITHUB_ACCESS_TOKEN',
            'GITHUB_URL'
        ],
        'gitlab': [
            'GITLAB_ACCESS_TOKEN',
            'GITLAB_URL'
        ]
    }

    # 配置验证规则
    _validation_rules = {
        'SERVER_PORT': lambda x: x.isdigit() and 1 <= int(x) <= 65535,
        'LLM_PROVIDER': lambda x: x in ['deepseek', 'openai', 'zhipuai', 'qwen', 'minimax', 'ollama'],
        'LOG_LEVEL': lambda x: x in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        'GIT_SERVICE_TYPE': lambda x: x in ['gitea', 'github', 'gitlab'],
        'DINGTALK_ENABLED': lambda x: x in ['0', '1'],
        'WECOM_ENABLED': lambda x: x in ['0', '1'],
        'FEISHU_ENABLED': lambda x: x in ['0', '1'],
        'EXTRA_WEBHOOK_ENABLED': lambda x: x in ['0', '1'],
        'PUSH_REVIEW_ENABLED': lambda x: x in ['0', '1'],
        'MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED': lambda x: x in ['0', '1'],
        'QUEUE_DRIVER': lambda x: x in ['async', 'rq']
    }

    @classmethod
    def validate(cls) -> bool:
        """验证所有配置

        Returns:
            bool: 验证是否通过
        """
        try:
            # 验证通用配置
            if not cls._validate_common_configs():
                return False

            # 验证Git服务配置
            git_service_type = config_manager.get('GIT_SERVICE_TYPE', 'gitea')
            if not cls._validate_git_configs(git_service_type):
                return False

            logger.info("配置验证通过")
            return True
        except ConfigValidationError as e:
            logger.error(f"配置验证失败: {e}")
            return False
        except Exception as e:
            logger.error(f"配置验证失败: {e}")
            return False

    @classmethod
    def _validate_common_configs(cls) -> bool:
        """验证通用配置

        Returns:
            bool: 验证是否通过
        """
        all_valid = True

        for config_key, validator in cls._validation_rules.items():
            value = config_manager.get(config_key)
            if value is not None:
                try:
                    if not validator(value):
                        error_msg = f"配置验证失败: {config_key} = {value}"
                        logger.error(error_msg)
                        all_valid = False
                except Exception as e:
                    error_msg = f"配置验证错误: {config_key} - {e}"
                    logger.error(error_msg)
                    all_valid = False

        return all_valid

    @classmethod
    def _validate_git_configs(cls, service_type: str) -> bool:
        """验证Git服务配置

        Args:
            service_type: Git服务类型

        Returns:
            bool: 验证是否通过
        """
        if service_type not in cls._required_configs:
            error_msg = f"不支持的Git服务类型: {service_type}"
            logger.error(error_msg)
            return False

        all_valid = True
        required_configs = cls._required_configs[service_type]

        for config_key in required_configs:
            value = config_manager.get(config_key)
            if not value:
                error_msg = f"缺少必要配置: {config_key}"
                logger.error(error_msg)
                all_valid = False

        return all_valid

    @classmethod
    def get_missing_configs(cls, service_type: str) -> List[str]:
        """获取缺失的配置项

        Args:
            service_type: Git服务类型

        Returns:
            List[str]: 缺失的配置项列表
        """
        missing_configs = []

        if service_type in cls._required_configs:
            required_configs = cls._required_configs[service_type]
            for config_key in required_configs:
                value = config_manager.get(config_key)
                if not value:
                    missing_configs.append(config_key)

        return missing_configs

    @classmethod
    def validate_git_credentials(cls, service_type: str, credentials: Dict) -> bool:
        """验证Git认证信息

        Args:
            service_type: Git服务类型
            credentials: 认证信息字典

        Returns:
            bool: 验证是否通过
        """
        if service_type not in cls._required_configs:
            error_msg = f"不支持的Git服务类型: {service_type}"
            logger.error(error_msg)
            return False

        all_valid = True
        required_configs = cls._required_configs[service_type]

        for config_key in required_configs:
            # 从认证信息或配置管理器中获取值
            credential_key = config_key.lower().replace('_', '')
            value = credentials.get(credential_key) or config_manager.get(config_key)
            if not value:
                error_msg = f"缺少必要认证信息: {config_key}"
                logger.error(error_msg)
                all_valid = False

        return all_valid
