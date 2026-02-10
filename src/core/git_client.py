from typing import Optional
import subprocess
import os


class GitClient:
    """
    Git客户端，处理基本的Git操作
    """
    
    def clone_repository(self, repo_url: str, local_path: str) -> bool:
        """
        克隆仓库
        """
        try:
            print(f"Cloning repository from {repo_url} to {local_path}")
            result = subprocess.run(
                ['git', 'clone', repo_url, local_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Repository cloned successfully: {result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to clone repository: {e.stderr}")
            return False
    
    def commit_and_push(self, local_path: str, message: str) -> bool:
        """
        提交并推送代码
        """
        try:
            # 确保在正确的目录中
            original_cwd = os.getcwd()
            os.chdir(local_path)
            
            # 检查是否有更改
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True
            )
            
            if not status_result.stdout.strip():
                print("No changes to commit")
                os.chdir(original_cwd)
                return True
            
            # 添加更改
            add_result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True,
                text=True,
                check=True
            )
            
            # 提交更改
            commit_result = subprocess.run(
                ['git', 'commit', '-m', message],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Changes committed: {commit_result.stdout}")
            
            # 推送更改
            push_result = subprocess.run(
                ['git', 'push'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Changes pushed: {push_result.stdout}")
            
            os.chdir(original_cwd)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to commit and push: {e.stderr}")
            try:
                os.chdir(original_cwd)
            except:
                pass
            return False
        except Exception as e:
            print(f"Error during git operations: {str(e)}")
            try:
                os.chdir(original_cwd)
            except:
                pass
            return False
    
    def get_repository_url(self, local_path: str) -> Optional[str]:
        """
        获取仓库的远程URL
        """
        try:
            original_cwd = os.getcwd()
            os.chdir(local_path)
            
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True,
                text=True,
                check=True
            )
            
            os.chdir(original_cwd)
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None
        except Exception:
            return None
