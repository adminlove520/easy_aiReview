import argparse
import os
import sys
from datetime import datetime


def parse_cli_arguments():
    """
    解析命令行参数
    """
    parser = argparse.ArgumentParser(description='OpenRA Code Review and Audit Tool')
    
    # 子命令
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # audit 命令
    audit_parser = subparsers.add_parser('audit', help='Perform code audit')
    audit_parser.add_argument('--local', action='store_true', help='Audit local repository')
    audit_parser.add_argument('--repo', type=str, help='Audit remote repository (URL)')
    audit_parser.add_argument('--sandbox', action='store_true', help='Enable sandbox verification')
    audit_parser.add_argument('--output', type=str, choices=['md', 'pdf', 'json'], default='md', help='Output format')
    
    # review 命令
    review_parser = subparsers.add_parser('review', help='Perform code review')
    review_parser.add_argument('--local', action='store_true', help='Review local repository')
    review_parser.add_argument('--repo', type=str, help='Review remote repository (URL)')
    review_parser.add_argument('--output', type=str, choices=['md', 'pdf', 'json'], default='md', help='Output format')
    
    return parser.parse_args()


def validate_arguments(args):
    """
    验证命令行参数
    """
    if not args.mode:
        print('Error: Please specify a mode (audit or review)')
        return False
    
    if args.mode in ['audit', 'review']:
        if not args.local and not args.repo:
            print(f'Error: Please specify either --local or --repo for {args.mode} mode')
            return False
        
        if args.local and args.repo:
            print(f'Error: Please specify only one of --local or --repo for {args.mode} mode')
            return False
    
    return True


def get_current_time():
    """
    获取当前时间
    """
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def get_elapsed_time(start_time, end_time):
    """
    计算经过的时间
    """
    elapsed = end_time - start_time
    return f"{elapsed.total_seconds():.2f} seconds"


def print_header(message):
    """
    打印标题
    """
    print(f"\n{'=' * 80}")
    print(f"{message:^80}")
    print(f"{'=' * 80}\n")


def print_footer(message):
    """
    打印页脚
    """
    print(f"\n{'=' * 80}")
    print(f"{message:^80}")
    print(f"{'=' * 80}\n")


def check_docker_available():
    """
    检查Docker是否可用
    """
    try:
        import subprocess
        result = subprocess.run(
            ['docker', 'info'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except Exception:
        return False


def ensure_directory(directory):
    """
    确保目录存在
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def get_repo_name(repo_url):
    """
    从仓库URL获取仓库名称
    """
    import re
    match = re.search(r'/([^/]+)\.git$', repo_url)
    if match:
        return match.group(1)
    # 处理没有 .git 后缀的情况
    match = re.search(r'/([^/]+)$', repo_url)
    if match:
        return match.group(1)
    return 'unknown_repo'
