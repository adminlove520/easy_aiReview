"""异常类定义"""


class BaseError(Exception):
    """基础异常类"""
    def __init__(self, message: str, **kwargs):
        """初始化异常

        Args:
            message: 错误信息
            **kwargs: 额外的上下文信息
        """
        self.message = message
        self.context = kwargs
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """格式化错误信息，添加上下文

        Returns:
            str: 格式化后的错误信息
        """
        context_str = ''
        if self.context:
            context_items = [f"{k}={v}" for k, v in self.context.items()]
            context_str = f" (context: {', '.join(context_items)})"
        return f"{self.message}{context_str}"


class ConfigError(BaseError):
    """配置错误基类"""
    pass


class ConfigValidationError(ConfigError):
    """配置验证错误"""
    pass


class GitError(BaseError):
    """Git操作错误基类"""
    pass


class GitAuthError(GitError):
    """Git认证错误"""
    pass


class GitApiError(GitError):
    """Git API错误"""
    pass


class LLMError(BaseError):
    """大模型错误基类"""
    pass


class LLMConfigError(LLMError):
    """大模型配置错误"""
    pass


class LLMRequestError(LLMError):
    """大模型请求错误"""
    pass


class ReviewError(BaseError):
    """代码审查错误基类"""
    pass


class ReviewConfigError(ReviewError):
    """代码审查配置错误"""
    pass


class ReviewContentError(ReviewError):
    """代码审查内容错误"""
    pass


class NotificationError(BaseError):
    """通知错误基类"""
    pass


class NotificationConfigError(NotificationError):
    """通知配置错误"""
    pass


class NotificationSendError(NotificationError):
    """通知发送错误"""
    pass


class SystemError(BaseError):
    """系统错误"""
    pass
