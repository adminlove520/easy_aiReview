import os
import shutil
import tempfile
from datetime import datetime
from typing import Optional

from src.utils.git.factory import GitClientFactory
from src.utils.log import logger


class ReportService:
    """日报存储服务"""

    def __init__(self):
        self.git_service_type = os.environ.get('GIT_SERVICE_TYPE', 'gitea').lower()
        self.repo_name = os.environ.get('GIT_REPO_NAME', 'aiReview_dailyReport')
        self.repo_description = '代码审查日报存储仓库'
        self.temp_dir = tempfile.gettempdir()
        self._local_repo_path: Optional[str] = None

    def _get_git_credentials(self) -> dict:
        """获取Git认证信息"""
        service_type = self.git_service_type.upper()
        credentials = {
            'access_token': os.environ.get(f'{service_type}_ACCESS_TOKEN', ''),
            'owner': os.environ.get(f'{service_type}_REPO_OWNER', '')
        }
        if not credentials['access_token'] or not credentials['owner']:
            logger.error(f"Git credentials incomplete: {service_type}_ACCESS_TOKEN or {service_type}_REPO_OWNER not set")
            return {}

        # 添加API URL配置
        api_url_key = f'{service_type}_API_URL'
        if os.environ.get(api_url_key):
            credentials['api_url'] = os.environ.get(api_url_key)
        else:
            # 从基础URL构建API URL
            if self.git_service_type == 'gitea' and os.environ.get('GITEA_URL'):
                credentials['api_url'] = f"{os.environ.get('GITEA_URL')}/api/v1"
            elif self.git_service_type == 'github' and os.environ.get('GITHUB_URL'):
                credentials['api_url'] = f"{os.environ.get('GITHUB_URL')}/api/v3"
            elif self.git_service_type == 'gitlab' and os.environ.get('GITLAB_URL'):
                credentials['api_url'] = f"{os.environ.get('GITLAB_URL')}/api/v4"

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

    def _cleanup_local_repo(self):
        """清理本地仓库目录"""
        if self._local_repo_path and os.path.exists(self._local_repo_path):
            try:
                shutil.rmtree(self._local_repo_path)
                logger.info(f"清理临时目录: {self._local_repo_path}")
            except Exception as e:
                logger.warning(f"清理临时目录失败: {e}")
            finally:
                self._local_repo_path = None

    def _ensure_directory(self, directory: str):
        """确保目录存在"""
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"创建目录: {directory}")

    def save_report_to_git(self, report_content: str) -> bool:
        """保存日报到Git仓库

        Args:
            report_content: 日报内容

        Returns:
            bool: 是否保存成功
        """
        # 获取日期路径和文件路径
        date_dir, report_file_path = self._get_date_path()
        date_str = date_dir

        try:
            credentials = self._get_git_credentials()
            if not credentials:
                logger.error("获取Git认证信息失败")
                return False

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

            # 生成唯一临时目录名并克隆
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            self._local_repo_path = os.path.join(self.temp_dir, f'{self.repo_name}_{timestamp}')

            if not git_client.clone_repository(repo_url, self._local_repo_path):
                logger.error("克隆仓库失败")
                return False

            # 写入日报内容
            full_file_path = os.path.join(self._local_repo_path, report_file_path)
            date_dir_full = os.path.join(self._local_repo_path, date_dir)
            self._ensure_directory(date_dir_full)

            with open(full_file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"写入日报文件: {full_file_path}")

            # 生成 commit message，包含链接
            link_text = f'{date_str}_开发日报'
            commit_message = f'更新日报 {report_file_path}\n\n📄 {link_text}'

            if not git_client.commit_and_push(self._local_repo_path, commit_message):
                logger.error("提交并推送代码失败")
                return False

            logger.info(f"日报保存到Git仓库成功: {link_text}")
            return True

        except Exception as e:
            logger.error(f"保存日报到Git仓库异常: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False
        finally:
            # 确保清理临时目录
            self._cleanup_local_repo()
