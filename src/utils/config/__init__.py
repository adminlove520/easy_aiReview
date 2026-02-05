"""配置管理模块"""
from src.utils.config.manager import ConfigManager

# 配置管理器实例
config_manager = ConfigManager()

# 导出配置获取函数
get = config_manager.get
get_bool = config_manager.get_bool
get_int = config_manager.get_int
