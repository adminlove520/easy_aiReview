import os
import tempfile
from typing import Optional

from src.utils.git.factory import GitClientFactory as GitFactory


class RepositoryManager:
    """
    仓库管理器，处理本地和远程仓库操作
    """
    
    def __init__(self):
        self.git_factory = GitFactory()
    
    def get_local_repository_path(self) -> str:
        """
        获取本地仓库路径
        如果 repo 目录下有子目录，返回第一个子目录
        """
        repo_base = os.path.join(os.getcwd(), "repo")
        # 检查 repo 目录是否存在
        if not os.path.exists(repo_base):
            return repo_base
        
        # 查找 repo 目录下的子目录
        subdirs = [d for d in os.listdir(repo_base) if os.path.isdir(os.path.join(repo_base, d))]
        if subdirs:
            # 返回第一个子目录
            return os.path.join(repo_base, subdirs[0])
        return repo_base
    
    def clone_repository(self, repo_url: str, temp_dir: Optional[str] = None) -> str:
        """
        克隆远程仓库
        """
        if not temp_dir:
            temp_dir = tempfile.mkdtemp()
        
        # 检测仓库类型
        service_type = self._detect_service_type(repo_url)
        
        # 获取Git客户端
        git_client = self.git_factory.get_client(service_type)
        if git_client:
            success = git_client.clone_repository(repo_url, temp_dir)
            if success:
                return temp_dir
        
        # 如果没有匹配的服务类型，使用通用Git客户端
        from src.core.git_client import GitClient
        generic_client = GitClient()
        if generic_client.clone_repository(repo_url, temp_dir):
            return temp_dir
        
        raise Exception(f"Failed to clone repository: {repo_url}")
    
    def _detect_service_type(self, repo_url: str) -> str:
        """
        检测仓库服务类型
        """
        if 'github.com' in repo_url:
            return 'github'
        elif 'gitlab.com' in repo_url or 'gitlab' in repo_url:
            return 'gitlab'
        elif 'gitea' in repo_url:
            return 'gitea'
        else:
            return 'github'  # 默认值
    
    def push_report(self, repo_path: str, report_path: str, report_type: str) -> bool:
        """
        推送报告到仓库
        """
        # 创建报告目录
        report_dir = os.path.join(repo_path, f"report_{report_type}")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)
        
        # 复制报告文件
        report_filename = os.path.basename(report_path)
        dest_path = os.path.join(report_dir, report_filename)
        
        import shutil
        shutil.copy2(report_path, dest_path)
        
        # 提交并推送
        from src.core.git_client import GitClient
        generic_client = GitClient()
        message = f"Add {report_type} report: {report_filename}"
        return generic_client.commit_and_push(repo_path, message)
    
    def cleanup(self, temp_dir: str):
        """
        清理临时目录
        """
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
