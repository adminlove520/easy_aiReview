import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 自定义 Logger 类，重写 warn 和 error 方法
class CustomLogger(logging.Logger):
    def warn(self, msg, *args, **kwargs):
        # 在 warn 消息前添加 ⚠️
        msg_with_emoji = f"⚠️ {msg}"
        super().warning(msg_with_emoji, *args, **kwargs)  # 注意：warn 是 warning 的别名

    def error(self, msg, *args, **kwargs):
        # 在 error 消息前添加 ❌
        msg_with_emoji = f"❌ {msg}"
        super().error(msg_with_emoji, *args, **kwargs)


log_file = os.environ.get("LOG_FILE", "logs/app.log")
# 兼容旧路径：如果路径中包含 log/app.log，自动转换为 logs/app.log
if "log/app.log" in log_file and "logs/app.log" not in log_file:
    log_file = log_file.replace("log/app.log", "logs/app.log")
# 确保日志目录存在
log_path = Path(log_file)
log_path.parent.mkdir(parents=True, exist_ok=True)
log_max_bytes = int(os.environ.get("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 默认10MB
log_backup_count = int(os.environ.get("LOG_BACKUP_COUNT", 5))  # 默认保留5个备份文件
# 设置日志级别
log_level = os.environ.get("LOG_LEVEL", "INFO")
LOG_LEVEL = getattr(logging, log_level.upper(), logging.INFO)

file_handler = RotatingFileHandler(
    filename=log_file,
    mode='a',
    maxBytes=log_max_bytes,
    backupCount=log_backup_count,
    encoding='utf-8',
    delay=False
)
# 自定义Formatter，使用本地时区（UTC+8）
class LocalTimeFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        import datetime
        import time
        # 强制使用UTC+8时区
        utc_time = datetime.datetime.utcfromtimestamp(record.created)
        local_time = utc_time + datetime.timedelta(hours=8)
        if datefmt:
            return local_time.strftime(datefmt)
        else:
            return local_time.strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]

file_handler.setFormatter(LocalTimeFormatter('%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'))
file_handler.setLevel(LOG_LEVEL)

console_handler = logging.StreamHandler()
console_handler.setFormatter(LocalTimeFormatter('%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s'))
console_handler.setLevel(LOG_LEVEL)


# 使用自定义的 Logger 类
logger = CustomLogger(__name__)
logger.setLevel(LOG_LEVEL)  # 设置 Logger 的日志级别
logger.addHandler(file_handler)
logger.addHandler(console_handler)
