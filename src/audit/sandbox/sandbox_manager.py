import os
import subprocess
from typing import Optional, Dict, Any


class SandboxManager:
    """
    沙箱管理器，负责管理Docker沙箱环境
    """
    
    def __init__(self):
        self.docker_available = self._check_docker_available()
    
    def _check_docker_available(self) -> bool:
        """
        检查Docker是否可用
        """
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def create_sandbox(self, image: str = 'python:3.11-slim') -> Optional[str]:
        """
        创建沙箱容器
        """
        if not self.docker_available:
            print("Docker is not available, sandbox verification disabled")
            return None
        
        try:
            # 拉取镜像
            print(f"Pulling Docker image: {image}")
            pull_result = subprocess.run(
                ['docker', 'pull', image],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Image pulled successfully: {pull_result.stdout}")
            
            # 创建容器
            container_name = f"audit-sandbox-{os.getpid()}"
            print(f"Creating sandbox container: {container_name}")
            create_result = subprocess.run(
                ['docker', 'run', '--name', container_name, '-d', image, 'sleep', '3600'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Container created successfully: {create_result.stdout}")
            
            return container_name
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to create sandbox: {e.stderr}")
            return None
    
    def execute_in_sandbox(self, container_name: str, command: str) -> Optional[Dict[str, Any]]:
        """
        在沙箱中执行命令
        """
        if not self.docker_available or not container_name:
            return None
        
        try:
            print(f"Executing in sandbox {container_name}: {command}")
            result = subprocess.run(
                ['docker', 'exec', container_name, 'bash', '-c', command],
                capture_output=True,
                text=True
            )
            
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to execute in sandbox: {e.stderr}")
            return None
    
    def copy_to_sandbox(self, container_name: str, local_path: str, sandbox_path: str) -> bool:
        """
        复制文件到沙箱
        """
        if not self.docker_available or not container_name:
            return False
        
        try:
            print(f"Copying {local_path} to sandbox {container_name}:{sandbox_path}")
            result = subprocess.run(
                ['docker', 'cp', local_path, f"{container_name}:{sandbox_path}"],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"File copied successfully: {result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to copy to sandbox: {e.stderr}")
            return False
    
    def cleanup_sandbox(self, container_name: str) -> bool:
        """
        清理沙箱容器
        """
        if not self.docker_available or not container_name:
            return False
        
        try:
            print(f"Cleaning up sandbox container: {container_name}")
            # 停止容器
            stop_result = subprocess.run(
                ['docker', 'stop', container_name],
                capture_output=True,
                text=True
            )
            
            # 删除容器
            rm_result = subprocess.run(
                ['docker', 'rm', container_name],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"Container cleaned up successfully: {rm_result.stdout}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to cleanup sandbox: {e.stderr}")
            return False
