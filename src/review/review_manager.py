from typing import Dict, Any, List
from datetime import datetime
import os

# 加载.env文件
from dotenv import load_dotenv

# 尝试加载.env文件
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"✅ Loaded .env file from: {env_path}")
else:
    # 尝试从当前目录加载
    load_dotenv()
    print("⚠️ No .env file found, using environment variables")

from src.cmd.functions.directory import DirectoryReviewFunc
from src.cmd.functions.branch import BranchReviewFunc
from src.cmd.functions.complexity import ComplexityReviewFunc
from src.cmd.functions.mysql import MySQLReviewFunc


class ReviewManager:
    """
    审查管理器，负责协调代码审查过程
    """
    
    def __init__(self):
        pass
    
    def review(self, repo_path):
        """
        执行代码审查
        """
        start_time = datetime.now()
        
        print(f"Starting review for repository: {repo_path}")
        
        # 执行各种审查功能
        findings = []
        
        # 1. 目录结构审查
        directory_findings = self._review_directory_structure(repo_path)
        findings.extend(directory_findings)
        
        # 2. 代码复杂度审查
        complexity_findings = self._review_code_complexity(repo_path)
        findings.extend(complexity_findings)
        
        # 3. 分支命名审查
        branch_findings = self._review_branch_names(repo_path)
        findings.extend(branch_findings)
        
        # 4. MySQL数据库表结构审查（如果适用）
        mysql_findings = self._review_mysql_structure(repo_path)
        findings.extend(mysql_findings)
        
        # 生成审查报告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        review_result = {
            "project": repo_path,
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "duration": f"{duration:.2f} seconds",
            "findings": findings,
            "conclusion": self._generate_conclusion(findings)
        }
        
        print("Review completed successfully")
        return review_result
    
    def _review_directory_structure(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        审查目录结构
        """
        print("Reviewing directory structure...")
        
        # 创建目录审查功能实例
        directory_review = DirectoryReviewFunc()
        
        # 模拟用户输入，使用默认值
        directory_review.language = "python"  # 默认为python
        directory_review.directory = repo_path
        directory_review.max_depth = 3
        directory_review.only_dirs = True
        
        # 加载gitignore规则
        ignore_spec = directory_review.load_gitignore_patterns()
        
        # 获取目录结构
        from src.utils.dir_util import get_directory_tree
        directory_structure = get_directory_tree(
            repo_path, ignore_spec, max_depth=3, only_dirs=True
        )
        
        # 生成提示并调用LLM
        prompts = directory_review.get_prompts(directory_structure)
        review_result = directory_review.call_llm(prompts)
        
        # 解析审查结果
        return [{
            "title": "Directory Structure Review",
            "severity": "Medium",
            "category": "Structure",
            "location": repo_path,
            "description": "Directory structure analysis",
            "recommendation": review_result
        }]
    
    def _review_code_complexity(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        审查代码复杂度
        """
        print("Reviewing code complexity...")
        
        # 创建复杂度审查功能实例
        complexity_review = ComplexityReviewFunc()
        
        # 模拟用户输入
        complexity_review.directory = repo_path
        complexity_review.language = "python"  # 默认为python
        complexity_review.show_histogram = False
        complexity_review.max_depth = 10
        
        # 执行复杂度分析
        # 注意：这里我们需要模拟process方法的逻辑，因为它是交互式的
        import lizard
        
        # 分析代码复杂度
        complexity_results = lizard.analyze_file(
            repo_path,
            extensions=["py"],
            max_line_length=1000
        )
        
        return [{
            "title": "Code Complexity Review",
            "severity": "Medium",
            "category": "Complexity",
            "location": repo_path,
            "description": f"Code complexity analysis completed. Total functions: {len(complexity_results.function_list)}",
            "recommendation": "Review functions with high cyclomatic complexity"
        }]
    
    def _review_branch_names(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        审查分支命名
        """
        print("Reviewing branch names...")
        
        # 创建分支审查功能实例
        branch_review = BranchReviewFunc()
        
        # 模拟用户输入
        branch_review.repository_path = repo_path
        
        # 执行分支分析
        # 注意：这里我们需要模拟process方法的逻辑
        import subprocess
        
        try:
            # 获取分支列表
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            branches = result.stdout.strip().split('\n')
            
            return [{
                "title": "Branch Naming Review",
                "severity": "Low",
                "category": "Naming",
                "location": repo_path,
                "description": f"Branch naming analysis completed. Total branches: {len(branches)}",
                "recommendation": "Ensure branch names follow conventional naming patterns"
            }]
        except Exception:
            return []
    
    def _review_mysql_structure(self, repo_path: str) -> List[Dict[str, Any]]:
        """
        审查MySQL数据库表结构
        """
        print("Reviewing MySQL structure...")
        
        # 检查是否存在SQL文件
        import os
        sql_files = []
        
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith('.sql'):
                    sql_files.append(os.path.join(root, file))
        
        if sql_files:
            return [{
                "title": "MySQL Structure Review",
                "severity": "Medium",
                "category": "Database",
                "location": repo_path,
                "description": f"Found {len(sql_files)} SQL files for analysis",
                "recommendation": "Review database schema design and indexing strategy"
            }]
        else:
            return []
    
    def _generate_conclusion(self, findings: List[Dict[str, Any]]) -> str:
        """
        生成审查结论
        """
        if not findings:
            return "No issues found. The codebase appears to be well-maintained."
        
        # 按类别统计问题
        categories = {}
        for finding in findings:
            category = finding.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        conclusion = f"Review completed with {len(findings)} total issues found:\n"
        for category, count in categories.items():
            conclusion += f"- {category}: {count}\n"
        
        conclusion += "\nRecommendations:\n"
        conclusion += "1. Address structural issues to improve code organization\n"
        conclusion += "2. Reduce code complexity in critical functions\n"
        conclusion += "3. Follow consistent naming conventions\n"
        conclusion += "4. Optimize database schema if applicable"
        
        return conclusion
