# OpenRA CLI 使用文档

本文档详细介绍如何使用 OpenRA (OpenAI Code Review Assistant) 的命令行工具进行代码审计和审查。

## 目录

- [OpenRA CLI 使用文档](#openra-cli-使用文档)
  - [目录](#目录)
  - [1. 概述](#1-概述)
  - [2. 安装和配置](#2-安装和配置)
    - [2.1 依赖安装](#21-依赖安装)
    - [2.2 环境配置](#22-环境配置)
  - [3. 基本用法](#3-基本用法)
    - [3.1 命令结构](#31-命令结构)
    - [3.2 模式说明](#32-模式说明)
  - [4. Audit 模式](#4-audit-模式)
    - [4.1 功能说明](#41-功能说明)
    - [4.2 使用方法](#42-使用方法)
    - [4.3 示例](#43-示例)
    - [4.4 沙箱验证](#44-沙箱验证)
  - [5. Review 模式](#5-review-模式)
    - [5.1 功能说明](#51-功能说明)
    - [5.2 使用方法](#52-使用方法)
    - [5.3 示例](#53-示例)
  - [6. 输出格式](#6-输出格式)
  - [7. 常见问题](#7-常见问题)
  - [8. 故障排除](#8-故障排除)

## 1. 概述

OpenRA CLI 工具提供两种主要模式：

- **audit 模式**：全面的代码审计，使用 DeepAudit 核心逻辑，包括多 Agent 协作、五维检测和沙箱验证
- **review 模式**：代码审查，分析仓库目录中的代码，生成详细的审查报告

两种模式都支持本地仓库和远程仓库操作，带有 `--local` 和 `--repo` 命令行参数。

## 2. 安装和配置

### 2.1 依赖安装

确保安装了所有必要的依赖：

```bash
# 使用国内镜像源安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或分批安装以避免依赖解析问题
pip install Flask fastapi pydantic -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install openai tiktoken langchain -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2.2 环境配置

在项目根目录的 `config/.env` 文件中配置 LLM 提供商和 API 密钥：

```env
# 大模型供应商配置,支持 deepseek, openai,zhipuai,qwen,Minimax 和 ollama
LLM_PROVIDER=minimax

# MiniMax settings
MINIMAX_API_KEY=sk-cp-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
MINIMAX_API_BASE_URL=https://api.minimaxi.com/v1
MINIMAX_API_MODEL=MiniMax-M2.1

# OpenAI settings
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-4o-mini

# ZhipuAI settings
ZHIPUAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ZHIPUAI_API_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPUAI_API_MODEL=glm-4.7

# DeepSeek settings
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_MODEL=deepseek-chat

# Review 配置
REVIEW_MAX_TOKENS=800000
```

## 3. 基本用法

### 3.1 命令结构

```bash
python -m src.cli.main <mode> [options]
```

### 3.2 模式说明

- **audit**：执行代码审计，支持以下选项：
  - `--local`：审计本地仓库
  - `--repo <url>`：审计远程仓库（指定 URL）
  - `--sandbox`：启用沙箱验证

- **review**：执行代码审查，支持以下选项：
  - `--local`：审查本地仓库
  - `--repo <url>`：审查远程仓库（指定 URL）

- **通用选项**：
  - `--output <format>`：指定输出格式（md, pdf, json），默认为 md

## 4. Audit 模式

### 4.1 功能说明

Audit 模式是基于 DeepAudit 的核心逻辑实现的全面代码审计功能，包括：

- **多 Agent 协作架构**：由编排 Agent 协调多个专业 Agent 进行深度分析
- **五维检测**：检查代码中的 bug、安全漏洞、性能问题、代码风格和可维护性
- **RAG 增强**：使用检索增强生成技术，提高分析准确性
- **沙箱验证**：在 Docker 沙箱环境中验证漏洞的真实性
- **详细报告**：生成包含漏洞详情、修复建议的专业报告

### 4.2 使用方法

#### 审计本地仓库

```bash
python -m src.cli.main audit --local
```

#### 审计远程仓库

```bash
python -m src.cli.main audit --repo https://github.com/username/repository.git
```

#### 启用沙箱验证

```bash
python -m src.cli.main audit --local --sandbox
```

#### 指定输出格式

```bash
python -m src.cli.main audit --local --output pdf
```

### 4.3 示例

#### 示例 1：审计本地仓库并生成 PDF 报告

```bash
python -m src.cli.main audit --local --output pdf
```

**输出**：

```
================================================================================
                               OpenRA Audit Tool
================================================================================

Start time: 2026-02-10 18:30:00
Processing audit...

🚀 Starting DeepAudit for repository: D:\PROJECT\Easy-AI-CodeReview\repo
📋 Audit configuration: sandbox=False
📚 Initializing RAG system...
🔍 Indexing repository: D:\PROJECT\Easy-AI-CodeReview\repo
Indexing progress: 100/100 files, 500/500 chunks
🔧 Initializing Agent system...
✅ Agent system initialized
🤖 Creating Orchestrator Agent...
✅ Added RAG tools
✅ Orchestrator Agent created

🎉 Audit completed successfully in 120.5 seconds
📊 Found 15 issues

End time: 2026-02-10 18:32:00
Elapsed time: 120.50 seconds

================================================================================
                      Operation completed successfully
================================================================================

Report saved to: reports/audit_20260210_183200.pdf
```

#### 示例 2：审计远程仓库

```bash
python -m src.cli.main audit --repo https://github.com/openai/openai-python.git
```

**输出**：

```
================================================================================
                               OpenRA Audit Tool
================================================================================

Start time: 2026-02-10 18:35:00
Processing audit...

🚀 Starting DeepAudit for repository: https://github.com/openai/openai-python.git
📋 Audit configuration: sandbox=False
Cloning repository...
Repository cloned to: /tmp/openai-python
📚 Initializing RAG system...
🔍 Indexing repository: /tmp/openai-python
Indexing progress: 500/500 files, 2000/2000 chunks
🔧 Initializing Agent system...
✅ Agent system initialized
🤖 Creating Orchestrator Agent...
✅ Added RAG tools
✅ Orchestrator Agent created

🎉 Audit completed successfully in 300.2 seconds
📊 Found 25 issues

End time: 2026-02-10 18:40:00
Elapsed time: 300.20 seconds

================================================================================
                      Operation completed successfully
================================================================================

Report saved to: reports/audit_20260210_184000.md
Pushing report to repository...
Report pushed successfully
```

### 4.4 沙箱验证

使用 `--sandbox` 选项可以在 Docker 沙箱环境中验证发现的漏洞：

```bash
python -m src.cli.main audit --local --sandbox
```

**注意**：使用沙箱验证需要 Docker 环境正常运行。如果 Docker 不可用，系统会自动降级为不使用沙箱。

## 5. Review 模式

### 5.1 功能说明

Review 模式提供代码审查功能，主要包括：

- **目录结构审查**：分析项目的目录结构，评估组织逻辑和命名规范性
- **代码复杂度审查**：使用 lizard 库分析代码复杂度，识别高复杂度函数
- **分支命名审查**：检查 Git 分支命名是否符合最佳实践
- **MySQL 结构审查**：分析 SQL 文件中的数据库表结构
- **详细报告**：生成包含发现问题和改进建议的审查报告

### 5.2 使用方法

#### 审查本地仓库

```bash
python -m src.cli.main review --local
```

#### 审查远程仓库

```bash
python -m src.cli.main review --repo https://github.com/username/repository.git
```

#### 指定输出格式

```bash
python -m src.cli.main review --local --output json
```

### 5.3 示例

#### 示例：审查本地仓库

```bash
python -m src.cli.main review --local
```

**输出**：

```
================================================================================
                               OpenRA Review Tool
================================================================================

Start time: 2026-02-10 18:45:00
Processing review...
✅ Loaded .env file from: D:\PROJECT\Easy-AI-CodeReview\config\.env
Reviewing local repository: D:\PROJECT\Easy-AI-CodeReview\repo
Starting review for repository: D:\PROJECT\Easy-AI-CodeReview\repo
Reviewing directory structure...
向 AI请求, messages: [...]
收到 AI 返回结果: <think>...</think> 根据您提供的目录结构，我作为资深软件架构师进行了详细审查...
Reviewing code complexity...
Reviewing branch names...
Reviewing MySQL structure...
Review completed successfully

End time: 2026-02-10 18:46:30
Elapsed time: 90.30 seconds

================================================================================
                      Operation completed successfully
================================================================================

Report saved to: reports/review_20260210_184630.md
```

## 6. 输出格式

OpenRA 支持三种输出格式：

- **Markdown (md)**：默认格式，适合在 GitHub 等平台查看
- **PDF**：使用 WeasyPrint 生成，适合正式报告
- **JSON**：结构化格式，适合与其他系统集成

使用 `--output` 选项指定输出格式：

```bash
# Markdown 格式
python -m src.cli.main audit --local --output md

# PDF 格式
python -m src.cli.main audit --local --output pdf

# JSON 格式
python -m src.cli.main audit --local --output json
```

## 7. 常见问题

### Q1: 执行命令时提示 "API key is required"？

**解决方法**：确保在 `config/.env` 文件中正确配置了 LLM 提供商的 API 密钥。

### Q2: 执行 audit 命令时提示 "tree-sitter-languages not installed"？

**解决方法**：安装 tree-sitter-language-pack：

```bash
pip install tree-sitter-language-pack>=0.13.0
```

### Q3: 执行命令时卡住不动？

**解决方法**：
- 使用国内镜像源安装依赖
- 分批安装依赖以减少依赖解析复杂度
- 检查网络连接是否正常
- 确保系统资源充足

### Q4: 审计结果不准确？

**解决方法**：
- 确保 LLM 提供商配置正确
- 使用更强大的模型（如 gpt-4o 而不是 gpt-3.5-turbo）
- 启用沙箱验证以提高漏洞检测准确性

## 8. 故障排除

### 检查依赖

```bash
# 检查核心依赖是否安装
pip list | grep -E "openai|langchain|tree-sitter"

# 检查是否有依赖冲突
pip check
```

### 检查配置

```bash
# 检查 .env 文件是否存在
ls -la config/.env

# 验证 LLM API 密钥是否设置
python -c "from dotenv import load_dotenv; load_dotenv('config/.env'); import os; print('OPENAI_API_KEY' in os.environ); print('MINIMAX_API_KEY' in os.environ)"
```

### 检查 Docker 状态（使用沙箱时）

```bash
# 检查 Docker 是否运行
docker info

# 检查 Docker 容器状态
docker ps
```

### 查看日志

系统执行过程中的日志会直接输出到控制台，可以根据日志信息定位问题。

## 总结

OpenRA CLI 工具提供了强大的代码审计和审查功能，可以帮助开发团队发现和解决代码中的问题。通过本文档的指导，您应该能够熟练使用 `audit` 和 `review` 模式进行代码分析，生成专业的审计报告。

如果您在使用过程中遇到任何问题，请参考本文档的故障排除部分，或联系技术支持团队。

---

**版本**：v1.0.0
**最后更新**：2026-02-10
**作者**：OpenRA Team