"""
前端服务 - 在 5002 端口提供前端页面和 API
"""
from flask import Flask, send_from_directory, request, jsonify
import os
import sys
from datetime import datetime
import pandas as pd

# 导入 API 相关模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.service.review_service import ReviewService
from src.utils.log import logger
from src.api.deepaudit_api import deepaudit_api

# 创建 Flask 应用
# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')
DEEPAUDIT_DIR = os.path.join(WEB_DIR, 'deepaudit', 'dist')
ui_app = Flask(__name__, static_folder=WEB_DIR, static_url_path='')



# 注册 DeepAudit API 蓝图
ui_app.register_blueprint(deepaudit_api, url_prefix='/api/v1')

# API 路由
@ui_app.route('/api/review/logs', methods=['GET'])
def get_review_logs():
    """获取审查日志数据"""
    try:
        # 获取查询参数
        review_type = request.args.get('type', 'mr')  # 'mr' 或 'push'
        authors = request.args.getlist('authors') if request.args.get('authors') else None
        project_names = request.args.getlist('project_names') if request.args.get('project_names') else None
        
        # 时间范围
        updated_at_gte = request.args.get('updated_at_gte')
        updated_at_lte = request.args.get('updated_at_lte')
        
        if updated_at_gte:
            updated_at_gte = int(updated_at_gte)
        else:
            updated_at_gte = None
            
        if updated_at_lte:
            updated_at_lte = int(updated_at_lte)
        else:
            updated_at_lte = None
        
        # 根据类型获取数据
        if review_type == 'push':
            df = ReviewService().get_push_review_logs(
                authors=authors,
                project_names=project_names,
                updated_at_gte=updated_at_gte,
                updated_at_lte=updated_at_lte
            )
        else:
            df = ReviewService().get_mr_review_logs(
                authors=authors,
                project_names=project_names,
                updated_at_gte=updated_at_gte,
                updated_at_lte=updated_at_lte
            )
        
        # 转换数据格式
        if df.empty:
            return jsonify({
                'data': [],
                'total': 0,
                'average_score': 0
            })
        
        # 格式化时间戳
        if 'updated_at' in df.columns:
            df['updated_at'] = df['updated_at'].apply(
                lambda ts: datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                if isinstance(ts, (int, float)) else ts
            )
        
        # 格式化代码变更
        if 'additions' in df.columns and 'deletions' in df.columns:
            df['delta'] = df.apply(
                lambda row: f"+{int(row['additions'])}  -{int(row['deletions'])}"
                if not pd.isna(row['additions']) and not pd.isna(row['deletions'])
                else "",
                axis=1
            )
        
        # 转换为字典列表
        records = df.to_dict(orient='records')
        
        # 计算统计信息
        total = len(records)
        average_score = df['score'].mean() if 'score' in df.columns and not df.empty else 0
        
        return jsonify({
            'data': records,
            'total': total,
            'average_score': float(average_score) if not pd.isna(average_score) else 0
        })
    except Exception as e:
        logger.error(f"Failed to get review logs: {e}")
        return jsonify({'error': str(e)}), 500


@ui_app.route('/api/review/stats', methods=['GET'])
def get_review_stats():
    """获取统计数据用于图表"""
    try:
        review_type = request.args.get('type', 'mr')
        authors = request.args.getlist('authors') if request.args.get('authors') else None
        project_names = request.args.getlist('project_names') if request.args.get('project_names') else None
        updated_at_gte = request.args.get('updated_at_gte')
        updated_at_lte = request.args.get('updated_at_lte')
        
        if updated_at_gte:
            updated_at_gte = int(updated_at_gte)
        else:
            updated_at_gte = None
            
        if updated_at_lte:
            updated_at_lte = int(updated_at_lte)
        else:
            updated_at_lte = None
        
        if review_type == 'push':
            df = ReviewService().get_push_review_logs(
                authors=authors,
                project_names=project_names,
                updated_at_gte=updated_at_gte,
                updated_at_lte=updated_at_lte
            )
        else:
            df = ReviewService().get_mr_review_logs(
                authors=authors,
                project_names=project_names,
                updated_at_gte=updated_at_gte,
                updated_at_lte=updated_at_lte
            )
        
        if df.empty:
            return jsonify({
                'project_counts': [],
                'project_scores': [],
                'author_counts': [],
                'author_scores': [],
                'author_code_lines': []
            })
        
        # 项目提交次数
        project_counts = df['project_name'].value_counts().reset_index()
        project_counts.columns = ['name', 'count']
        
        # 项目平均分数
        project_scores = df.groupby('project_name')['score'].mean().reset_index()
        project_scores.columns = ['name', 'average_score']
        
        # 人员提交次数
        author_counts = df['author'].value_counts().reset_index()
        author_counts.columns = ['name', 'count']
        
        # 人员平均分数
        author_scores = df.groupby('author')['score'].mean().reset_index()
        author_scores.columns = ['name', 'average_score']
        
        # 人员代码行数
        author_code_lines = []
        if 'additions' in df.columns and 'deletions' in df.columns:
            df['total_lines'] = df['additions'] + df['deletions']
            author_code_lines_df = df.groupby('author')['total_lines'].sum().reset_index()
            author_code_lines_df.columns = ['name', 'code_lines']
            author_code_lines = author_code_lines_df.to_dict(orient='records')
        
        return jsonify({
            'project_counts': project_counts.to_dict(orient='records'),
            'project_scores': project_scores.to_dict(orient='records'),
            'author_counts': author_counts.to_dict(orient='records'),
            'author_scores': author_scores.to_dict(orient='records'),
            'author_code_lines': author_code_lines
        })
    except Exception as e:
        logger.error(f"Failed to get review stats: {e}")
        return jsonify({'error': str(e)}), 500


@ui_app.route('/api/review/filter-options', methods=['GET'])
def get_filter_options():
    """获取所有可用的筛选选项（用户名和项目名）"""
    try:
        review_type = request.args.get('type', 'mr')
        
        # 获取所有数据（不应用任何筛选条件）
        if review_type == 'push':
            df = ReviewService().get_push_review_logs()
        else:
            df = ReviewService().get_mr_review_logs()
        
        # 提取唯一的用户名和项目名
        authors = []
        project_names = []
        
        if not df.empty:
            authors = sorted(df['author'].dropna().unique().tolist())
            project_names = sorted(df['project_name'].dropna().unique().tolist())
        
        return jsonify({
            'authors': authors,
            'project_names': project_names
        })
    except Exception as e:
        logger.error(f"Failed to get filter options: {e}")
        return jsonify({'error': str(e)}), 500


# DeepAudit 路由
@ui_app.route('/deepaudit')
def deepaudit_index():
    """提供DeepAudit前端页面"""
    return send_from_directory(DEEPAUDIT_DIR, 'index.html')

@ui_app.route('/deepaudit/<path:path>')
def serve_deepaudit_static(path):
    """提供DeepAudit静态文件"""
    # 确保路径安全
    if '..' in path or path.startswith('/'):
        return None
    return send_from_directory(DEEPAUDIT_DIR, path)

# 前端路由 - 必须在 API 路由之后定义，避免冲突
@ui_app.route('/')
def index():
    """提供前端页面"""
    return send_from_directory(WEB_DIR, 'index.html')

@ui_app.route('/<path:path>')
def serve_static(path):
    """提供静态文件"""
    # 排除 API 路由
    if path.startswith('api/'):
        return None
    # 确保路径安全
    if '..' in path or path.startswith('/'):
        return None
    return send_from_directory(WEB_DIR, path)

if __name__ == '__main__':
    port = int(os.environ.get('UI_PORT', 5002))
    ui_app.run(host='0.0.0.0', port=port, debug=False)

