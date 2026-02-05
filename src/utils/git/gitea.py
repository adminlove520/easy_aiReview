"""Gitea Git操作模块"""
import os
import subprocess
import shutil

import requests

from src.utils.git.base import BaseGitClient
from src.utils.log import logger


class GiteaGitClient(BaseGitClient):
    """Gitea Git操作类"""

    def __init__(self):
        self.api_url = None
        self.access_token = None
        self.owner = None

    def set_credentials(self, credentials):
        """设置认证信息"""
        self.api_url = credentials.get('api_url')
        self.access_token = credentials.get('access_token')
        self.owner = credentials.get('owner')
        # 尝试从API获取当前用户信息作为owner
        if self.api_url and self.access_token and not self.owner:
            self._fetch_user_info()

    def clone_repository(self, repo_url, local_path):
        """克隆仓库"""
        try:
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
            cmd = ['git', 'clone', repo_url, local_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if result.returncode != 0:
                logger.error(f"克隆仓库失败: {result.stderr}")
                return False
            logger.info(f"仓库克隆成功: {repo_url} -> {local_path}")
            return True
        except Exception as e:
            logger.error(f"克隆仓库异常: {e}")
            return False

    def commit_and_push(self, local_path, message):
        """提交并推送代码"""
        try:
            original_cwd = os.getcwd()
            os.chdir(local_path)
            
            # 配置 git 用户信息（Docker 容器中可能未配置）
            subprocess.run(['git', 'config', 'user.name', 'AI Review Bot'], capture_output=True, check=False)
            subprocess.run(['git', 'config', 'user.email', 'bot@aireview.local'], capture_output=True, check=False)
            
            subprocess.run(['git', 'add', '.'], capture_output=True, check=False)
            status_result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True, check=False)
            if not status_result.stdout.strip():
                logger.info("没有更改需要提交")
                os.chdir(original_cwd)
                return True
            commit_result = subprocess.run(['git', 'commit', '-m', message], capture_output=True, text=True, check=False)
            if commit_result.returncode != 0:
                logger.error(f"提交失败: {commit_result.stderr}")
                os.chdir(original_cwd)
                return False
            push_result = subprocess.run(['git', 'push'], capture_output=True, text=True, check=False)
            if push_result.returncode != 0:
                logger.error(f"推送失败: {push_result.stderr}")
                os.chdir(original_cwd)
                return False
            logger.info("代码提交并推送成功")
            os.chdir(original_cwd)
            return True
        except Exception as e:
            logger.error(f"提交并推送异常: {e}")
            os.chdir(original_cwd)
            return False

    def create_repository(self, repo_name, description=""):
        """创建仓库"""
        try:
            if not self.api_url or not self.access_token:
                logger.error("Gitea API配置不完整")
                return False
            url = f"{self.api_url}/user/repos"
            headers = {
                'Authorization': f'token {self.access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                'name': repo_name,
                'description': description,
                'private': False,
                'auto_init': True
            }
            response = requests.post(url, headers=headers, json=data, timeout=30)
            if response.status_code == 201:
                logger.info(f"仓库创建成功: {repo_name}")
                return True
            logger.error(f"仓库创建失败: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"创建仓库异常: {e}")
            return False

    def repository_exists(self, repo_name):
        """检查仓库是否存在"""
        try:
            if not self.api_url or not self.access_token:
                logger.error("Gitea API配置不完整")
                return False
            url = f"{self.api_url}/repos/{self.owner}/{repo_name}"
            headers = {
                'Authorization': f'token {self.access_token}'
            }
            response = requests.get(url, headers=headers, timeout=30)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"检查仓库异常: {e}")
            return False

    def _fetch_user_info(self):
        """从API获取用户信息"""
        try:
            url = f"{self.api_url}/user"
            headers = {
                'Authorization': f'token {self.access_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                user_info = response.json()
                self.owner = user_info.get('login') or user_info.get('username')
                logger.info(f"从Gitea API获取用户信息成功: {self.owner}")
            else:
                logger.error(f"获取用户信息失败: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")

    def get_repository_url(self, repo_name):
        """获取仓库URL"""
        if not self.owner:
            logger.error("Gitea owner未配置")
            return ""
        # 从api_url提取基础URL
        base_url = self.api_url.replace('/api/v1', '') if self.api_url else 'https://git.nxwysoft.com'
        # 返回包含认证令牌的 URL，用于 clone 操作
        if self.access_token:
            return f"https://{self.access_token}@{base_url.replace('https://', '')}/{self.owner}/{repo_name}.git"
        else:
            return f"{base_url}/{self.owner}/{repo_name}.git"
