# 使用官方的 Python 基础镜像
FROM python:3.10-slim AS base

# 设置工作目录
WORKDIR /app

# 安装 supervisord 作为进程管理工具
RUN apt-get update && apt-get install -y --no-install-recommends supervisor && rm -rf /var/lib/apt/lists/*

# 复制项目文件&创建必要的文件夹
COPY requirements.txt .

# 使用国内镜像源安装依赖，增加超时时间和重试机制
RUN pip install --no-cache-dir --timeout 300 --retries 3 -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

RUN mkdir -p logs data config web
COPY src ./src
COPY api.py ./api.py
COPY ui.py ./ui.py
COPY ui_server.py ./ui_server.py
COPY web ./web
COPY config/prompt_templates.yml ./config/prompt_templates.yml

# 使用 supervisord 作为启动命令
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

FROM base AS app
COPY config/supervisord.app.conf /etc/supervisor/conf.d/supervisord.conf
# 暴露 Flask 和 Streamlit 的端口
EXPOSE 5001 5002

FROM base AS worker
COPY ./config/supervisord.worker.conf /etc/supervisor/conf.d/supervisord.conf