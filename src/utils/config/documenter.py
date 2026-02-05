"""配置文档生成模块"""
import os
from typing import Dict, List

from src.utils.config import config_manager


class ConfigDocumenter:
    """配置文档生成器类"""

    # 配置项说明
    _config_descriptions = {
        # 服务配置
        'SERVER_PORT': '服务端口号',
        
        # 大模型配置
        'LLM_PROVIDER': '大模型供应商',
        'DEEPSEEK_API_KEY': 'DeepSeek API密钥',
        'DEEPSEEK_API_BASE_URL': 'DeepSeek API基础URL',
        'DEEPSEEK_API_MODEL': 'DeepSeek API模型',
        'OPENAI_API_KEY': 'OpenAI API密钥',
        'OPENAI_API_BASE_URL': 'OpenAI API基础URL',
        'OPENAI_API_MODEL': 'OpenAI API模型',
        'ZHIPUAI_API_KEY': '智谱AI API密钥',
        'ZHIPUAI_API_BASE_URL': '智谱AI API基础URL',
        'ZHIPUAI_API_MODEL': '智谱AI API模型',
        'MINIMAX_API_KEY': 'MiniMax API密钥',
        'MINIMAX_API_BASE_URL': 'MiniMax API基础URL',
        'MINIMAX_API_MODEL': 'MiniMax API模型',
        'QWEN_API_KEY': '通义千问 API密钥',
        'QWEN_API_BASE_URL': '通义千问 API基础URL',
        'QWEN_API_MODEL': '通义千问 API模型',
        'OLLAMA_API_BASE_URL': 'Ollama API基础URL',
        'OLLAMA_API_MODEL': 'Ollama API模型',
        
        # 代码审查配置
        'SUPPORTED_EXTENSIONS': '支持审查的文件类型',
        'REVIEW_MAX_TOKENS': '每次审查的最大Token限制',
        'REVIEW_STYLE': '审查风格',
        
        # 通知配置
        'DINGTALK_ENABLED': '是否启用钉钉通知',
        'DINGTALK_WEBHOOK_URL': '钉钉Webhook URL',
        'DINGTALK_SECRET': '钉钉Webhook密钥',
        'WECOM_ENABLED': '是否启用企业微信通知',
        'WECOM_WEBHOOK_URL': '企业微信Webhook URL',
        'FEISHU_ENABLED': '是否启用飞书通知',
        'FEISHU_WEBHOOK_URL': '飞书Webhook URL',
        'EXTRA_WEBHOOK_ENABLED': '是否启用自定义Webhook',
        'EXTRA_WEBHOOK_URL': '自定义Webhook URL',
        
        # 日志配置
        'LOG_FILE': '日志文件路径',
        'LOG_MAX_BYTES': '日志文件最大字节数',
        'LOG_BACKUP_COUNT': '日志文件备份数量',
        'LOG_LEVEL': '日志级别',
        
        # 日报配置
        'REPORT_CRONTAB_EXPRESSION': '日报发送时间（Crontab表达式）',
        'GIT_SERVICE_TYPE': 'Git服务类型',
        'GIT_REPO_NAME': '日报存储仓库名称',
        
        # Git服务配置
        # GitLab
        'GITLAB_URL': 'GitLab基础URL',
        'GITLAB_ACCESS_TOKEN': 'GitLab访问令牌',
        'GITLAB_REPO_OWNER': 'GitLab仓库所有者',
        
        # GitHub
        'GITHUB_URL': 'GitHub基础URL',
        'GITHUB_ACCESS_TOKEN': 'GitHub访问令牌',
        'GITHUB_REPO_OWNER': 'GitHub仓库所有者',
        
        # Gitea
        'GITEA_URL': 'Gitea基础URL',
        'GITEA_ACCESS_TOKEN': 'Gitea访问令牌',
        'GITEA_REPO_OWNER': 'Gitea仓库所有者',
        'GITEA_WEBHOOK_SECRET': 'Gitea Webhook密钥',
        
        # 其他配置
        'PUSH_REVIEW_ENABLED': '是否启用Push事件触发审查',
        'MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED': '是否仅在合并到受保护分支时审查',
        'DASHBOARD_USER': 'Dashboard登录用户名',
        'DASHBOARD_PASSWORD': 'Dashboard登录密码',
        'QUEUE_DRIVER': '队列驱动',
        'WORKER_QUEUE': '工作队列名称'
    }

    # 配置项默认值
    _config_defaults = {
        # 服务配置
        'SERVER_PORT': '5001',
        
        # 大模型配置
        'LLM_PROVIDER': 'minimax',
        'DEEPSEEK_API_BASE_URL': 'https://api.deepseek.com',
        'DEEPSEEK_API_MODEL': 'deepseek-chat',
        'OPENAI_API_BASE_URL': 'https://api.openai.com/v1',
        'OPENAI_API_MODEL': 'gpt-4o-mini',
        'ZHIPUAI_API_BASE_URL': 'https://open.bigmodel.cn/api/paas/v4/',
        'ZHIPUAI_API_MODEL': 'glm-4.7',
        'MINIMAX_API_BASE_URL': 'https://api.minimaxi.com/v1',
        'MINIMAX_API_MODEL': 'MiniMax-M2.1',
        'QWEN_API_BASE_URL': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
        'QWEN_API_MODEL': 'qwen-coder-plus',
        'OLLAMA_API_BASE_URL': 'http://host.docker.internal:11434',
        'OLLAMA_API_MODEL': 'deepseek-r1:latest',
        
        # 代码审查配置
        'SUPPORTED_EXTENSIONS': '.c,.cc,.cpp,.css,.go,.h,.java,.js,.jsx,.ts,.tsx,.md,.php,.py,.sql,.vue,.yml',
        'REVIEW_MAX_TOKENS': '10000',
        'REVIEW_STYLE': 'professional',
        
        # 通知配置
        'DINGTALK_ENABLED': '1',
        'WECOM_ENABLED': '0',
        'FEISHU_ENABLED': '0',
        'EXTRA_WEBHOOK_ENABLED': '0',
        
        # 日志配置
        'LOG_FILE': 'log/app.log',
        'LOG_MAX_BYTES': '10485760',
        'LOG_BACKUP_COUNT': '3',
        'LOG_LEVEL': 'DEBUG',
        
        # 日报配置
        'REPORT_CRONTAB_EXPRESSION': '0 18 * * 1-5',
        'GIT_SERVICE_TYPE': 'gitea',
        'GIT_REPO_NAME': 'aiReview_dailyReport',
        
        # Git服务配置
        # GitLab
        'GITLAB_URL': 'https://gitlab.com',
        
        # GitHub
        'GITHUB_URL': 'https://github.com',
        
        # Gitea
        'GITEA_URL': 'https://git.nxwysoft.com',
        
        # 其他配置
        'PUSH_REVIEW_ENABLED': '1',
        'MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED': '0',
        'DASHBOARD_USER': 'admin',
        'DASHBOARD_PASSWORD': 'admin',
        'QUEUE_DRIVER': 'async',
        'WORKER_QUEUE': 'git_test_com'
    }

    @classmethod
    def generate_documentation(cls, output_file: str = None) -> str:
        """生成配置文档

        Args:
            output_file: 输出文件路径，None表示返回文档内容

        Returns:
            str: 配置文档内容
        """
        documentation = "# 配置文档\n\n"
        documentation += "## 配置项说明\n\n"

        # 按类别组织配置项
        categories = {
            '服务配置': [
                'SERVER_PORT'
            ],
            '大模型配置': [
                'LLM_PROVIDER',
                'DEEPSEEK_API_KEY',
                'DEEPSEEK_API_BASE_URL',
                'DEEPSEEK_API_MODEL',
                'OPENAI_API_KEY',
                'OPENAI_API_BASE_URL',
                'OPENAI_API_MODEL',
                'ZHIPUAI_API_KEY',
                'ZHIPUAI_API_BASE_URL',
                'ZHIPUAI_API_MODEL',
                'MINIMAX_API_KEY',
                'MINIMAX_API_BASE_URL',
                'MINIMAX_API_MODEL',
                'QWEN_API_KEY',
                'QWEN_API_BASE_URL',
                'QWEN_API_MODEL',
                'OLLAMA_API_BASE_URL',
                'OLLAMA_API_MODEL'
            ],
            '代码审查配置': [
                'SUPPORTED_EXTENSIONS',
                'REVIEW_MAX_TOKENS',
                'REVIEW_STYLE'
            ],
            '通知配置': [
                'DINGTALK_ENABLED',
                'DINGTALK_WEBHOOK_URL',
                'DINGTALK_SECRET',
                'WECOM_ENABLED',
                'WECOM_WEBHOOK_URL',
                'FEISHU_ENABLED',
                'FEISHU_WEBHOOK_URL',
                'EXTRA_WEBHOOK_ENABLED',
                'EXTRA_WEBHOOK_URL'
            ],
            '日志配置': [
                'LOG_FILE',
                'LOG_MAX_BYTES',
                'LOG_BACKUP_COUNT',
                'LOG_LEVEL'
            ],
            '日报配置': [
                'REPORT_CRONTAB_EXPRESSION',
                'GIT_SERVICE_TYPE',
                'GIT_REPO_NAME'
            ],
            'GitLab配置': [
                'GITLAB_URL',
                'GITLAB_ACCESS_TOKEN',
                'GITLAB_REPO_OWNER'
            ],
            'GitHub配置': [
                'GITHUB_URL',
                'GITHUB_ACCESS_TOKEN',
                'GITHUB_REPO_OWNER'
            ],
            'Gitea配置': [
                'GITEA_URL',
                'GITEA_ACCESS_TOKEN',
                'GITEA_REPO_OWNER',
                'GITEA_WEBHOOK_SECRET'
            ],
            '其他配置': [
                'PUSH_REVIEW_ENABLED',
                'MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED',
                'DASHBOARD_USER',
                'DASHBOARD_PASSWORD',
                'QUEUE_DRIVER',
                'WORKER_QUEUE'
            ]
        }

        for category, config_keys in categories.items():
            documentation += f"### {category}\n\n"
            documentation += "| 配置项 | 说明 | 默认值 |\n"
            documentation += "|-------|------|-------|\n"

            for key in config_keys:
                description = cls._config_descriptions.get(key, '')
                default = cls._config_defaults.get(key, '')
                documentation += f"| {key} | {description} | `{default}` |\n"

            documentation += "\n"

        # 生成配置示例
        documentation += "## 配置示例\n\n"
        documentation += "```env\n"

        for category, config_keys in categories.items():
            documentation += f"# {category}\n"
            for key in config_keys:
                default = cls._config_defaults.get(key, '')
                if default:
                    documentation += f"{key}={default}\n"
                else:
                    documentation += f"#{key}={key}\n"
            documentation += "\n"

        documentation += "```\n"

        # 输出到文件
        if output_file:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(documentation)
            print(f"配置文档已生成到: {output_file}")

        return documentation

    @classmethod
    def update_readme(cls):
        """更新README.md文件，添加配置文档"""
        readme_path = 'README.md'
        if not os.path.exists(readme_path):
            print(f"README.md文件不存在: {readme_path}")
            return

        # 读取现有README内容
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        # 生成配置文档
        config_doc = cls.generate_documentation()

        # 替换或添加配置文档部分
        if '## 配置文档' in readme_content:
            # 替换现有配置文档
            parts = readme_content.split('## 配置文档')
            new_content = parts[0] + config_doc
        else:
            # 添加新的配置文档部分
            new_content = readme_content + '\n' + config_doc

        # 写回README文件
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"README.md文件已更新，添加了配置文档")
