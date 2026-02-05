# 配置文档

## 配置项说明

### 服务配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| SERVER_PORT | 服务端口号 | `5001` |

### 大模型配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| LLM_PROVIDER | 大模型供应商 | `minimax` |
| DEEPSEEK_API_KEY | DeepSeek API密钥 | `` |
| DEEPSEEK_API_BASE_URL | DeepSeek API基础URL | `https://api.deepseek.com` |
| DEEPSEEK_API_MODEL | DeepSeek API模型 | `deepseek-chat` |
| OPENAI_API_KEY | OpenAI API密钥 | `` |
| OPENAI_API_BASE_URL | OpenAI API基础URL | `https://api.openai.com/v1` |
| OPENAI_API_MODEL | OpenAI API模型 | `gpt-4o-mini` |
| ZHIPUAI_API_KEY | 智谱AI API密钥 | `` |
| ZHIPUAI_API_BASE_URL | 智谱AI API基础URL | `https://open.bigmodel.cn/api/paas/v4/` |
| ZHIPUAI_API_MODEL | 智谱AI API模型 | `glm-4.7` |
| MINIMAX_API_KEY | MiniMax API密钥 | `` |
| MINIMAX_API_BASE_URL | MiniMax API基础URL | `https://api.minimaxi.com/v1` |
| MINIMAX_API_MODEL | MiniMax API模型 | `MiniMax-M2.1` |
| QWEN_API_KEY | 通义千问 API密钥 | `` |
| QWEN_API_BASE_URL | 通义千问 API基础URL | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| QWEN_API_MODEL | 通义千问 API模型 | `qwen-coder-plus` |
| OLLAMA_API_BASE_URL | Ollama API基础URL | `http://host.docker.internal:11434` |
| OLLAMA_API_MODEL | Ollama API模型 | `deepseek-r1:latest` |

### 代码审查配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| SUPPORTED_EXTENSIONS | 支持审查的文件类型 | `.c,.cc,.cpp,.css,.go,.h,.java,.js,.jsx,.ts,.tsx,.md,.php,.py,.sql,.vue,.yml` |
| REVIEW_MAX_TOKENS | 每次审查的最大Token限制 | `10000` |
| REVIEW_STYLE | 审查风格 | `professional` |

### 通知配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| DINGTALK_ENABLED | 是否启用钉钉通知 | `1` |
| DINGTALK_WEBHOOK_URL | 钉钉Webhook URL | `` |
| DINGTALK_SECRET | 钉钉Webhook密钥 | `` |
| WECOM_ENABLED | 是否启用企业微信通知 | `0` |
| WECOM_WEBHOOK_URL | 企业微信Webhook URL | `` |
| FEISHU_ENABLED | 是否启用飞书通知 | `0` |
| FEISHU_WEBHOOK_URL | 飞书Webhook URL | `` |
| EXTRA_WEBHOOK_ENABLED | 是否启用自定义Webhook | `0` |
| EXTRA_WEBHOOK_URL | 自定义Webhook URL | `` |

### 日志配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| LOG_FILE | 日志文件路径 | `log/app.log` |
| LOG_MAX_BYTES | 日志文件最大字节数 | `10485760` |
| LOG_BACKUP_COUNT | 日志文件备份数量 | `3` |
| LOG_LEVEL | 日志级别 | `DEBUG` |

### 日报配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| REPORT_CRONTAB_EXPRESSION | 日报发送时间（Crontab表达式） | `0 18 * * 1-5` |
| GIT_SERVICE_TYPE | Git服务类型 | `gitea` |
| GIT_REPO_NAME | 日报存储仓库名称 | `aiReview_dailyReport` |

### GitLab配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| GITLAB_URL | GitLab基础URL | `https://gitlab.com` |
| GITLAB_ACCESS_TOKEN | GitLab访问令牌 | `` |
| GITLAB_REPO_OWNER | GitLab仓库所有者 | `` |

### GitHub配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| GITHUB_URL | GitHub基础URL | `https://github.com` |
| GITHUB_ACCESS_TOKEN | GitHub访问令牌 | `` |
| GITHUB_REPO_OWNER | GitHub仓库所有者 | `` |

### Gitea配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| GITEA_URL | Gitea基础URL | `https://git.nxwysoft.com` |
| GITEA_ACCESS_TOKEN | Gitea访问令牌 | `` |
| GITEA_REPO_OWNER | Gitea仓库所有者 | `` |
| GITEA_WEBHOOK_SECRET | Gitea Webhook密钥 | `` |

### 其他配置

| 配置项 | 说明 | 默认值 |
|-------|------|-------|
| PUSH_REVIEW_ENABLED | 是否启用Push事件触发审查 | `1` |
| MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED | 是否仅在合并到受保护分支时审查 | `0` |
| DASHBOARD_USER | Dashboard登录用户名 | `admin` |
| DASHBOARD_PASSWORD | Dashboard登录密码 | `admin` |
| QUEUE_DRIVER | 队列驱动 | `async` |
| WORKER_QUEUE | 工作队列名称 | `git_test_com` |

## 配置示例

```env
# 服务配置
SERVER_PORT=5001

# 大模型配置
LLM_PROVIDER=minimax
#DEEPSEEK_API_KEY=DEEPSEEK_API_KEY
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_MODEL=deepseek-chat
#OPENAI_API_KEY=OPENAI_API_KEY
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-4o-mini
#ZHIPUAI_API_KEY=ZHIPUAI_API_KEY
ZHIPUAI_API_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPUAI_API_MODEL=glm-4.7
#MINIMAX_API_KEY=MINIMAX_API_KEY
MINIMAX_API_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_API_MODEL=MiniMax-M2.1
#QWEN_API_KEY=QWEN_API_KEY
QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_MODEL=qwen-coder-plus
OLLAMA_API_BASE_URL=http://host.docker.internal:11434
OLLAMA_API_MODEL=deepseek-r1:latest

# 代码审查配置
SUPPORTED_EXTENSIONS=.c,.cc,.cpp,.css,.go,.h,.java,.js,.jsx,.ts,.tsx,.md,.php,.py,.sql,.vue,.yml
REVIEW_MAX_TOKENS=10000
REVIEW_STYLE=professional

# 通知配置
DINGTALK_ENABLED=1
#DINGTALK_WEBHOOK_URL=DINGTALK_WEBHOOK_URL
#DINGTALK_SECRET=DINGTALK_SECRET
WECOM_ENABLED=0
#WECOM_WEBHOOK_URL=WECOM_WEBHOOK_URL
FEISHU_ENABLED=0
#FEISHU_WEBHOOK_URL=FEISHU_WEBHOOK_URL
EXTRA_WEBHOOK_ENABLED=0
#EXTRA_WEBHOOK_URL=EXTRA_WEBHOOK_URL

# 日志配置
LOG_FILE=log/app.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=3
LOG_LEVEL=DEBUG

# 日报配置
REPORT_CRONTAB_EXPRESSION=0 18 * * 1-5
GIT_SERVICE_TYPE=gitea
GIT_REPO_NAME=aiReview_dailyReport

# GitLab配置
GITLAB_URL=https://gitlab.com
#GITLAB_ACCESS_TOKEN=GITLAB_ACCESS_TOKEN
#GITLAB_REPO_OWNER=GITLAB_REPO_OWNER

# GitHub配置
GITHUB_URL=https://github.com
#GITHUB_ACCESS_TOKEN=GITHUB_ACCESS_TOKEN
#GITHUB_REPO_OWNER=GITHUB_REPO_OWNER

# Gitea配置
GITEA_URL=https://git.nxwysoft.com
#GITEA_ACCESS_TOKEN=GITEA_ACCESS_TOKEN
#GITEA_REPO_OWNER=GITEA_REPO_OWNER
#GITEA_WEBHOOK_SECRET=GITEA_WEBHOOK_SECRET

# 其他配置
PUSH_REVIEW_ENABLED=1
MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED=0
DASHBOARD_USER=admin
DASHBOARD_PASSWORD=admin
QUEUE_DRIVER=async
WORKER_QUEUE=git_test_com

```
