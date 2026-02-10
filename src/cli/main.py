import sys
import os
from datetime import datetime

from src.core.cli_utils import parse_cli_arguments, validate_arguments, print_header, print_footer, get_current_time, get_elapsed_time
from src.core.repository_manager import RepositoryManager
from src.core.report_generator import ReportGenerator


def main():
    """
    CLI主入口函数
    """
    try:
        # 解析命令行参数
        args = parse_cli_arguments()
        
        # 验证参数
        if not validate_arguments(args):
            return 1
        
        print_header(f"OpenRA {args.mode.capitalize()} Tool")
        print(f"Start time: {get_current_time()}")
        
        start_time = datetime.now()
        
        # 初始化组件
        repo_manager = RepositoryManager()
        report_generator = ReportGenerator()
        
        # 根据模式执行相应的操作
        if args.mode == 'audit':
            result = handle_audit(args, repo_manager, report_generator)
        elif args.mode == 'review':
            result = handle_review(args, repo_manager, report_generator)
        else:
            print(f"Unknown mode: {args.mode}")
            result = 1
        
        end_time = datetime.now()
        print(f"End time: {get_current_time()}")
        print(f"Elapsed time: {get_elapsed_time(start_time, end_time)}")
        
        print_footer(f"Operation {'completed successfully' if result == 0 else 'failed'}")
        
        return result
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1


def handle_audit(args, repo_manager, report_generator):
    """
    处理audit模式
    """
    print("Processing audit...")
    
    # 导入audit模块（延迟导入以减少启动时间）
    from src.audit.audit_manager import AuditManager
    
    audit_manager = AuditManager(sandbox=args.sandbox)
    
    if args.local:
        # 处理本地仓库
        repo_path = repo_manager.get_local_repository_path()
        print(f"Auditing local repository: {repo_path}")
        
    elif args.repo:
        # 处理远程仓库
        print(f"Auditing remote repository: {args.repo}")
        repo_path = repo_manager.clone_repository(args.repo)
        print(f"Repository cloned to: {repo_path}")
    
    # 执行审计
    audit_result = audit_manager.audit_sync(repo_path)
    
    # 生成报告（默认中文）
    report_content = generate_report(audit_result, 'audit', args.output, report_generator)
    
    # 保存报告到目标仓库
    report_dir = f"report_audit"
    output_dir = os.path.join(repo_path, report_dir)
    report_path = report_generator.save_report(report_content, 'audit', args.output, output_dir)
    print(f"Report saved to: {report_path}")
    
    # 如果是远程仓库，推送报告
    if args.repo:
        print("Pushing report to repository...")
        # 推送最新的报告（中文）
        latest_report_path = report_generator.save_report(report_content, 'audit', args.output, 'zh', output_dir)
        success = repo_manager.push_report(repo_path, latest_report_path, 'audit')
        if success:
            print("Report pushed successfully")
        else:
            print("Failed to push report")
        
        # 清理临时目录
        repo_manager.cleanup(repo_path)
    
    return 0


def handle_review(args, repo_manager, report_generator):
    """
    处理review模式
    """
    print("Processing review...")
    
    # 导入review模块（延迟导入以减少启动时间）
    from src.review.review_manager import ReviewManager
    
    review_manager = ReviewManager()
    
    if args.local:
        # 处理本地仓库
        repo_path = repo_manager.get_local_repository_path()
        print(f"Reviewing local repository: {repo_path}")
        
    elif args.repo:
        # 处理远程仓库
        print(f"Reviewing remote repository: {args.repo}")
        repo_path = repo_manager.clone_repository(args.repo)
        print(f"Repository cloned to: {repo_path}")
    
    # 执行审查
    review_result = review_manager.review(repo_path)
    
    # 生成报告（默认中文）
    report_content = generate_report(review_result, 'review', args.output, report_generator)
    
    # 保存报告到目标仓库
    report_dir = f"report_review"
    output_dir = os.path.join(repo_path, report_dir)
    report_path = report_generator.save_report(report_content, 'review', args.output, output_dir)
    print(f"Report saved to: {report_path}")
    
    # 如果是远程仓库，推送报告
    if args.repo:
        print("Pushing report to repository...")
        success = repo_manager.push_report(repo_path, report_path, 'review')
        if success:
            print("Report pushed successfully")
        else:
            print("Failed to push report")
        
        # 清理临时目录
        repo_manager.cleanup(repo_path)
    
    return 0


def generate_report(result, report_type, output_format, report_generator):
    """
    生成报告
    
    Args:
        result: 审计或审查结果
        report_type: 报告类型
        output_format: 输出格式
        report_generator: 报告生成器实例
        
    Returns:
        str or bytes: 报告内容
    """
    if output_format == 'md':
        return report_generator.generate_markdown_report(result, report_type)
    elif output_format == 'json':
        return report_generator.generate_json_report(result)
    elif output_format == 'pdf':
        pdf_path = report_generator.generate_pdf_report(result, report_type)
        if pdf_path:
            with open(pdf_path, 'rb') as f:
                return f.read()
        else:
            # 如果PDF生成失败，回退到markdown
            return report_generator.generate_markdown_report(result, report_type)
    else:
        return report_generator.generate_markdown_report(result, report_type)


if __name__ == '__main__':
    sys.exit(main())
