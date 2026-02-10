# CLI使用说明

## 概述
OpenRA提供了强大的命令行界面（CLI），支持代码审计和审查功能。通过CLI，用户可以快速分析本地或远程代码仓库，生成专业的审计报告。

## 基本语法

```bash
python -m src.cli.main [全局选项] <模式> [模式选项]
```

## 全局选项

| 选项 | 描述 | 默认值 |
|------|------|--------|
| `--output <format>` | 输出格式，支持 md、pdf、json | md |
| `--help`, `-h` | 显示帮助信息 | - |

## 支持的模式

### 1. audit 模式
**描述**：执行代码审计，检测安全漏洞、性能问题、代码质量等

**模式选项**：

| 选项 | 描述 |
|------|------|
| `--local` | 审计本地仓库（当前workspace下的repo目录） |
| `--repo <url>` | 审计远程仓库（指定仓库URL） |
| `--sandbox` | 启用沙箱验证（使用Docker容器验证漏洞） |
| `--help`, `-h` | 显示audit模式的帮助信息 |

### 2. review 模式
**描述**：执行代码审查，分析代码结构、复杂度、命名等

**模式选项**：

| 选项 | 描述 |
|------|------|
| `--local` | 审查本地仓库（当前workspace下的repo目录） |
| `--repo <url>` | 审查远程仓库（指定仓库URL） |
| `--help`, `-h` | 显示review模式的帮助信息 |

## 示例命令

### 审计本地仓库

```bash
# 基本审计（Markdown格式）
python -m src.cli.main audit --local

# 带沙箱验证的审计
python -m src.cli.main audit --local --sandbox

# 生成PDF格式报告
python -m src.cli.main --output pdf audit --local

# 生成JSON格式报告
python -m src.cli.main --output json audit --local
```

### 审计远程仓库

```bash
# 审计GitHub仓库
python -m src.cli.main audit --repo https://github.com/example/repo.git

# 审计GitLab仓库
python -m src.cli.main audit --repo https://gitlab.com/example/repo.git

# 审计Gitea仓库
python -m src.cli.main audit --repo https://gitea.example.com/example/repo.git

# 带沙箱验证和PDF报告
python -m src.cli.main --output pdf audit --repo https://github.com/example/repo.git --sandbox
```

### 审查本地仓库

```bash
# 基本审查（Markdown格式）
python -m src.cli.main review --local

# 生成PDF格式报告
python -m src.cli.main --output pdf review --local

# 生成JSON格式报告
python -m src.cli.main --output json review --local
```

### 审查远程仓库

```bash
# 审查GitHub仓库
python -m src.cli.main review --repo https://github.com/example/repo.git

# 审查GitLab仓库
python -m src.cli.main review --repo https://gitlab.com/example/repo.git

# 审查Gitea仓库
python -m src.cli.main review --repo https://gitea.example.com/example/repo.git

# 生成PDF格式报告
python -m src.cli.main --output pdf review --repo https://github.com/example/repo.git
```

## 工作流程

### 本地仓库流程
1. **分析代码**：扫描本地repo目录中的代码文件
2. **执行审计/审查**：根据选择的模式执行相应的分析
3. **生成报告**：创建指定格式的报告文件
4. **保存报告**：将报告保存到当前目录

### 远程仓库流程
1. **克隆仓库**：从指定URL克隆远程仓库到临时目录
2. **分析代码**：扫描克隆的代码文件
3. **执行审计/审查**：根据选择的模式执行相应的分析
4. **生成报告**：创建指定格式的报告文件
5. **推送报告**：将报告推送到远程仓库的report_<type>目录
6. **清理**：删除临时目录

## 配置文件

可以通过`config/.env`文件配置CLI的默认行为：

```env
# 大模型配置
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=your_api_key

# 默认输出格式
DEFAULT_OUTPUT_FORMAT=md

# 默认提示词模板
DEFAULT_PROMPT_TEMPLATE="默认代码审计"

# 默认规则集
DEFAULT_RULE_SET="OWASP Top 10"

# 启用的规则集
ENABLED_RULE_SETS="OWASP Top 10,代码质量规则"

# 沙箱配置
SANDBOX_ENABLED=true

# Git配置
GITHUB_ACCESS_TOKEN=your_github_token
GITLAB_ACCESS_TOKEN=your_gitlab_token
GITEA_ACCESS_TOKEN=your_gitea_token
```

## 环境变量

CLI也支持通过环境变量配置：

| 环境变量 | 描述 |
|---------|------|
| `LLM_PROVIDER` | 大模型提供商 |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 |
| `OPENAI_API_KEY` | OpenAI API密钥 |
| `ZHIPUAI_API_KEY` | 智谱AI API密钥 |
| `MINIMAX_API_KEY` | MiniMax API密钥 |
| `QWEN_API_KEY` | 通义千问API密钥 |
| `DEFAULT_OUTPUT_FORMAT` | 默认输出格式 |
| `DEFAULT_PROMPT_TEMPLATE` | 默认提示词模板 |
| `DEFAULT_RULE_SET` | 默认规则集 |
| `SANDBOX_ENABLED` | 是否启用沙箱 |
| `GITHUB_ACCESS_TOKEN` | GitHub访问令牌 |
| `GITLAB_ACCESS_TOKEN` | GitLab访问令牌 |
| `GITEA_ACCESS_TOKEN` | Gitea访问令牌 |

## 常见问题

### 1. API密钥错误
**症状**：`Error: API key is required. Please provide it or set it in the environment variables.`

**解决方法**：
- 在`config/.env`文件中设置API密钥
- 或通过环境变量设置API密钥
- 确保选择了正确的LLM提供商

### 2. Docker不可用
**症状**：`Docker is not available, sandbox verification disabled`

**解决方法**：
- 安装并启动Docker服务
- 确保当前用户有权限使用Docker
- 或不使用`--sandbox`选项

### 3. 远程仓库克隆失败
**症状**：`Failed to clone repository: <url>`

**解决方法**：
- 确保网络连接正常
- 确保仓库URL正确
- 提供正确的访问令牌（如果仓库是私有的）

### 4. 报告推送失败
**症状**：`Failed to push report`

**解决方法**：
- 确保有推送权限
- 确保访问令牌有正确的权限
- 检查网络连接

### 5. PDF生成失败
**症状**：`PDF generation requires reportlab. Please install it.`

**解决方法**：
- 安装所需依赖：`pip install weasyprint reportlab`
- 或使用其他输出格式

## 性能优化

### 大型项目处理

对于大型项目，建议：

1. **使用Markdown格式**：生成速度快，占用资源少
2. **分批处理**：将项目分成多个模块，分别审计
3. **调整内存限制**：增加Python的内存限制
4. **禁用沙箱**：对于非常大的项目，考虑禁用沙箱验证

### 远程仓库处理

对于远程仓库，建议：

1. **选择合适的分支**：只分析必要的分支
2. **设置合理的超时**：对于大型仓库，增加克隆和分析的超时时间
3. **使用浅克隆**：对于只需要最新代码的场景，使用浅克隆

## 高级使用

### 自定义提示词模板

1. 创建自定义提示词模板（参考`docs/prompt_templates.md`）
2. 在配置文件中设置默认模板：
   ```env
   DEFAULT_PROMPT_TEMPLATE="我的自定义模板"
   ```

### 自定义审计规则

1. 创建自定义审计规则（参考`docs/audit_rules.md`）
2. 在配置文件中设置启用的规则集：
   ```env
   ENABLED_RULE_SETS="OWASP Top 10,我的自定义规则集"
   ```

### 集成到CI/CD

可以将CLI集成到CI/CD流程中：

```yaml
# GitHub Actions示例
name: Code Audit

on: [push, pull_request]

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements/audit.txt
      - name: Run audit
        run: python -m src.cli.main --output md audit --local
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: audit-report
          path: report_audit.md
```

## 与DeepAudit的关系

OpenRA的CLI功能参考了DeepAudit的实现，主要特点包括：

- **多模式支持**：支持audit和review两种模式
- **多格式输出**：支持Markdown、PDF、JSON格式
- **沙箱验证**：使用Docker容器验证漏洞
- **远程仓库支持**：支持GitHub、GitLab、Gitea

主要改进包括：

- **统一CLI**：单一入口点支持所有功能
- **简化配置**：通过环境变量和配置文件配置
- **优化性能**：针对大型项目的性能优化
- **易用性**：更简洁的命令语法和更详细的帮助信息