import os
import tempfile
from datetime import datetime

from src.utils.git.factory import GitClientFactory
from src.utils.log import logger


class ReportService:
    """日报存储服务"""

    def __init__(self):
        self.git_service_type = os.environ.get('GIT_SERVICE_TYPE', 'gitea')
        self.repo_name = os.environ.get('GIT_REPO_NAME', 'aiReview_dailyReport')
        self.repo_description = '代码审查日报存储仓库'
        self.temp_dir = tempfile.gettempdir()

    def _get_git_credentials(self) -> dict:
        """获取Git认证信息"""
        credentials = {
            'access_token': os.environ.get(f'{self.git_service_type.upper()}_ACCESS_TOKEN'),
            'owner': os.environ.get(f'{self.git_service_type.upper()}_REPO_OWNER', 'zhangz')
        }

        # 添加API URL配置
        api_url_key = f'{self.git_service_type.upper()}_API_URL'
        if os.environ.get(api_url_key):
            credentials['api_url'] = os.environ.get(api_url_key)

        return credentials

    def _get_date_path(self, date: datetime = None) -> tuple:
        """获取日期路径

        Returns:
            tuple: (日期目录, 日报文件路径)
        """
        if date is None:
            date = datetime.now()

        date_str = date.strftime('%Y-%m-%d')
        date_dir = date_str
        file_name = f'daily_{date_str}.md'
        file_path = os.path.join(date_dir, file_name)

        return date_dir, file_path

    def _ensure_directory(self, directory: str):
        """确保目录存在"""
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"创建目录: {directory}")

    def save_report_to_git(self, report_content: str) -> bool:
        """保存日报到Git仓库

        Args:
            report_content: 日报内容

        Returns:
            bool: 是否保存成功
        """
        try:
            # 获取Git客户端
            credentials = self._get_git_credentials()
            git_client = GitClientFactory.get_client(self.git_service_type, credentials)
            if not git_client:
                logger.error("获取Git客户端失败")
                return False

            # 检查仓库是否存在，不存在则创建
            if not git_client.repository_exists(self.repo_name):
                logger.info(f"仓库 {self.repo_name} 不存在，正在创建...")
                if not git_client.create_repository(self.repo_name, self.repo_description):
                    logger.error("创建仓库失败")
                    return False

            # 获取仓库URL
            repo_url = git_client.get_repository_url(self.repo_name)
            if not repo_url:
                logger.error("获取仓库URL失败")
                return False

            # 克隆仓库到临时目录
            local_repo_path = os.path.join(self.temp_dir, f'{self.repo_name}_{datetime.now().timestamp()}')
            if not git_client.clone_repository(repo_url, local_repo_path):
                logger.error("克隆仓库失败")
                return False

            # 获取日期路径
            date_dir, report_file_path = self._get_date_path()
            full_file_path = os.path.join(local_repo_path, report_file_path)

            # 确保日期目录存在
            date_dir_full = os.path.join(local_repo_path, date_dir)
            self._ensure_directory(date_dir_full)

            # 写入日报内容
            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"写入日报文件: {full_file_path}")

            # 提交并推送代码
            commit_message = f'更新日报 {report_file_path}'
            if not git_client.commit_and_push(local_repo_path, commit_message):
                logger.error("提交并推送代码失败")
                return False

            logger.info("日报保存到Git仓库成功")
            return True

        except Exception as e:
            logger.error(f"保存日报到Git仓库异常: {e}")
            return False

    def generate_report_content(self, commits: list) -> str:
        """生成日报内容

        Args:
            commits: 提交记录列表

        Returns:
            str: 日报内容
        """
        date_str = datetime.now().strftime('%Y年%m月%d日')
        report_content = f'# 代码审查日报 - {date_str}\n\n'

        # 按作者分组
        author_commits = {}
        for commit in commits:
            author = commit.get('author', 'Unknown')
            if author not in author_commits:
                author_commits[author] = []
            author_commits[author].append(commit)

        # 生成每个作者的提交记录
        for author, author_commit_list in author_commits.items():
            report_content += f'## {author}\n\n'
            for commit in author_commit_list:
                project = commit.get('project_name', 'Unknown')
                branch = commit.get('branch', 'Unknown')
                message = commit.get('commit_messages', 'No message')
                additions = commit.get('additions', 0)
                deletions = commit.get('deletions', 0)

                report_content += f'### {project} ({branch})\n'
                report_content += f'- 提交信息: {message}\n'
                report_content += f'- 代码变更: +{additions} - {deletions}\n\n'

        report_content += f'\n---\n'
        report_content += f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'

        return report_content
