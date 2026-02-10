"""
DeepAudit 后端 API
按照真实的 DeepAudit 实现，确保所有前端需要的接口都存在
"""
from flask import Blueprint, jsonify, request, send_file
from datetime import datetime
import os

# 创建 Blueprint
deepaudit_api = Blueprint('deepaudit_api', __name__)

# 模拟数据
current_user = {
    "id": 1,
    "email": "demo@example.com",
    "full_name": "Demo User",
    "is_active": True,
    "is_superuser": False,
    "created_at": "2026-02-10T00:00:00Z",
    "updated_at": "2026-02-10T00:00:00Z"
}

projects = [
    {
        "id": 1,
        "name": "测试项目",
        "description": "这是一个测试项目",
        "source_type": "local",
        "repo_url": "",
        "local_path": "C:/test",
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z",
        "is_active": True,
        "created_by": 1
    }
]

tasks = [
    {
        "id": 1,
        "project_id": 1,
        "name": "测试审计任务",
        "status": "completed",
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z",
        "completed_at": "2026-02-10T00:00:00Z",
        "created_by": 1
    }
]

issues = [
    {
        "id": 1,
        "task_id": 1,
        "title": "测试问题",
        "description": "这是一个测试问题",
        "severity": "low",
        "status": "open",
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z"
    }
]

scan_history = [
    {
        "id": 1,
        "title": "测试即时分析",
        "status": "completed",
        "created_at": "2026-02-10T00:00:00Z",
        "completed_at": "2026-02-10T00:00:00Z"
    }
]

ssh_keys = []

agent_tasks = []

prompts = [
    {
        "id": 1,
        "name": "代码分析提示词",
        "content": "请分析以下代码，找出可能的问题",
        "is_active": True,
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z"
    }
]

rules = [
    {
        "id": 1,
        "name": "安全审计规则",
        "description": "安全相关的审计规则",
        "is_active": True,
        "created_at": "2026-02-10T00:00:00Z",
        "updated_at": "2026-02-10T00:00:00Z",
        "rules": [
            {
                "id": 1,
                "rule_set_id": 1,
                "name": "SQL注入检测",
                "pattern": "SELECT.*FROM.*WHERE.*=.*",
                "description": "检测可能的SQL注入漏洞",
                "severity": "high",
                "is_active": True
            }
        ]
    }
]

config = {
    "id": 1,
    "user_id": 1,
    "llm_provider": "minimax",
    "llm_model": "abab5.5-chat",
    "api_key": "",
    "created_at": "2026-02-10T00:00:00Z",
    "updated_at": "2026-02-10T00:00:00Z"
}

# 健康检查
@deepaudit_api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"})

# 根路径
@deepaudit_api.route('/', methods=['GET'])
def root():
    return jsonify({
        "message": "Welcome to DeepAudit API",
        "docs": "/docs",
        "demo_account": {
            "email": "demo@example.com",
            "password": "demo123"
        }
    })

# 认证相关接口
@deepaudit_api.route('/auth/login', methods=['POST'])
def login():
    """
    OAuth2 compatible token login, get an access token for future requests.
    Username field should contain the email address.
    """
    # 支持多种格式：表单数据、JSON 和 URL 编码的表单数据
    username = None
    password = None
    
    # 尝试获取表单数据
    if request.form:
        username = request.form.get('username') or request.form.get('email')
        password = request.form.get('password')
    # 尝试获取 JSON 数据
    elif request.is_json:
        data = request.json
        username = data.get('username') or data.get('email')
        password = data.get('password')
    # 尝试获取 URL 编码的表单数据
    elif request.data:
        import urllib.parse
        form_data = urllib.parse.parse_qs(request.data.decode('utf-8'))
        username = form_data.get('username', [None])[0] or form_data.get('email', [None])[0]
        password = form_data.get('password', [None])[0]
    
    if username == 'demo@example.com' and password == 'demo123':
        return jsonify({
            "access_token": "test-access-token",
            "token_type": "bearer"
        })
    return jsonify({"detail": "邮箱或密码错误"}), 400

@deepaudit_api.route('/auth/register', methods=['POST'])
def register():
    data = request.json
    return jsonify({
        "id": 2,
        "email": data.get('email', 'newuser@example.com'),
        "full_name": data.get('full_name', 'New User'),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "updated_at": datetime.utcnow().isoformat() + 'Z'
    })

# 用户相关接口
@deepaudit_api.route('/users/me', methods=['GET'])
def get_current_user():
    return jsonify(current_user)

@deepaudit_api.route('/users/', methods=['GET'])
def get_users():
    return jsonify([current_user])

@deepaudit_api.route('/users/<int:id>', methods=['PATCH'])
def update_user(id):
    data = request.json
    return jsonify({
        "id": id,
        "email": data.get('email', current_user['email']),
        "full_name": data.get('full_name', current_user['full_name']),
        "is_active": data.get('is_active', current_user['is_active']),
        "is_superuser": data.get('is_superuser', current_user['is_superuser']),
        "created_at": current_user['created_at'],
        "updated_at": datetime.utcnow().isoformat() + 'Z'
    })

# 项目相关接口
@deepaudit_api.route('/projects/', methods=['GET'])
def get_projects():
    return jsonify(projects)

@deepaudit_api.route('/projects/<int:id>', methods=['GET'])
def get_project(id):
    project = next((p for p in projects if p['id'] == id), None)
    if project:
        return jsonify(project)
    return jsonify({"detail": "Project not found"}), 404

@deepaudit_api.route('/projects/', methods=['POST'])
def create_project():
    data = request.json
    new_project = {
        "id": len(projects) + 1,
        "name": data.get('name', 'New Project'),
        "description": data.get('description', ''),
        "source_type": data.get('source_type', 'local'),
        "repo_url": data.get('repo_url', ''),
        "local_path": data.get('local_path', ''),
        "is_active": True,
        "created_by": 1,
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "updated_at": datetime.utcnow().isoformat() + 'Z'
    }
    projects.append(new_project)
    return jsonify(new_project), 201

@deepaudit_api.route('/projects/<int:id>', methods=['PUT'])
def update_project(id):
    data = request.json
    project = next((p for p in projects if p['id'] == id), None)
    if project:
        project.update({
            "name": data.get('name', project['name']),
            "description": data.get('description', project['description']),
            "source_type": data.get('source_type', project['source_type']),
            "repo_url": data.get('repo_url', project['repo_url']),
            "local_path": data.get('local_path', project['local_path']),
            "is_active": data.get('is_active', project['is_active']),
            "updated_at": datetime.utcnow().isoformat() + 'Z'
        })
        return jsonify(project)
    return jsonify({"detail": "Project not found"}), 404

@deepaudit_api.route('/projects/<int:id>', methods=['DELETE'])
def delete_project(id):
    project = next((p for p in projects if p['id'] == id), None)
    if project:
        projects.remove(project)
        return jsonify({"message": "Project deleted"})
    return jsonify({"detail": "Project not found"}), 404

@deepaudit_api.route('/projects/deleted', methods=['GET'])
def get_deleted_projects():
    return jsonify([])

@deepaudit_api.route('/projects/<int:id>/restore', methods=['POST'])
def restore_project(id):
    return jsonify({"message": "Project restored"})

@deepaudit_api.route('/projects/<int:id>/permanent', methods=['DELETE'])
def permanent_delete_project(id):
    return jsonify({"message": "Project permanently deleted"})

@deepaudit_api.route('/projects/<int:id>/files', methods=['GET'])
def get_project_files(id):
    return jsonify([])

@deepaudit_api.route('/projects/<int:id>/branches', methods=['GET'])
def get_project_branches(id):
    return jsonify([{"name": "main"}])

@deepaudit_api.route('/projects/<int:id>/zip', methods=['GET'])
def get_project_zip(id):
    return jsonify({"message": "Zip file retrieved"})

@deepaudit_api.route('/projects/<int:id>/zip', methods=['POST'])
def create_project_zip(id):
    return jsonify({"message": "Zip file created"})

@deepaudit_api.route('/projects/<int:id>/zip', methods=['DELETE'])
def delete_project_zip(id):
    return jsonify({"message": "Zip file deleted"})

@deepaudit_api.route('/projects/<int:id>/members', methods=['GET'])
def get_project_members(id):
    return jsonify([])

@deepaudit_api.route('/projects/<int:id>/members', methods=['POST'])
def add_project_member(id):
    return jsonify({"message": "Member added"})

@deepaudit_api.route('/projects/<int:id>/members/<int:member_id>', methods=['DELETE'])
def remove_project_member(id, member_id):
    return jsonify({"message": "Member removed"})

@deepaudit_api.route('/projects/stats', methods=['GET'])
def get_project_stats():
    return jsonify({"total": len(projects), "active": len([p for p in projects if p['is_active']])})

# 任务相关接口
@deepaudit_api.route('/tasks/', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

@deepaudit_api.route('/tasks/<int:id>', methods=['GET'])
def get_task(id):
    task = next((t for t in tasks if t['id'] == id), None)
    if task:
        return jsonify(task)
    return jsonify({"detail": "Task not found"}), 404

@deepaudit_api.route('/tasks/<int:id>/cancel', methods=['POST'])
def cancel_task(id):
    return jsonify({"message": "Task cancelled"})

@deepaudit_api.route('/tasks/<int:id>/issues', methods=['GET'])
def get_task_issues(id):
    return jsonify([i for i in issues if i['task_id'] == id])

@deepaudit_api.route('/tasks/<int:id>/issues/<int:issue_id>', methods=['PATCH'])
def update_task_issue(id, issue_id):
    data = request.json
    issue = next((i for i in issues if i['id'] == issue_id and i['task_id'] == id), None)
    if issue:
        issue.update({
            "status": data.get('status', issue['status']),
            "updated_at": datetime.utcnow().isoformat() + 'Z'
        })
        return jsonify(issue)
    return jsonify({"detail": "Issue not found"}), 404

@deepaudit_api.route('/tasks/<int:id>/report/pdf', methods=['GET'])
def get_task_report_pdf(id):
    return jsonify({"message": "PDF report generated"})

# 扫描相关接口
@deepaudit_api.route('/scan/instant/history', methods=['GET'])
def get_scan_history():
    return jsonify(scan_history)

@deepaudit_api.route('/scan/instant/history/<int:id>', methods=['DELETE'])
def delete_scan_history(id):
    return jsonify({"message": "Scan history deleted"})

@deepaudit_api.route('/scan/instant/history', methods=['DELETE'])
def delete_all_scan_history():
    return jsonify({"message": "All scan history deleted"})

@deepaudit_api.route('/scan/instant/history/<int:id>/report/pdf', methods=['GET'])
def get_scan_report_pdf(id):
    return jsonify({"message": "PDF report generated"})

@deepaudit_api.route('/projects/<int:id>/scan', methods=['POST'])
def scan_project(id):
    return jsonify({"task_id": 1})

# 配置相关接口
@deepaudit_api.route('/config/me', methods=['GET'])
def get_config_me():
    return jsonify(config)

@deepaudit_api.route('/config/me', methods=['PUT'])
def update_config_me():
    data = request.json
    config.update({
        "llm_provider": data.get('llm_provider', config['llm_provider']),
        "llm_model": data.get('llm_model', config['llm_model']),
        "api_key": data.get('api_key', config['api_key']),
        "updated_at": datetime.utcnow().isoformat() + 'Z'
    })
    return jsonify(config)

@deepaudit_api.route('/config/me', methods=['DELETE'])
def delete_config_me():
    return jsonify({"message": "Config deleted"})

@deepaudit_api.route('/config/defaults', methods=['GET'])
def get_config_defaults():
    return jsonify({"llm_provider": "minimax", "llm_model": "abab5.5-chat"})

@deepaudit_api.route('/config/test-llm', methods=['POST'])
def test_llm_config():
    return jsonify({"message": "LLM test successful"})

@deepaudit_api.route('/config/llm-providers', methods=['GET'])
def get_llm_providers():
    return jsonify([
        {"name": "minimax", "models": ["abab5.5-chat"]},
        {"name": "openai", "models": ["gpt-4", "gpt-3.5-turbo"]}
    ])

# 数据库相关接口
@deepaudit_api.route('/database/export', methods=['GET'])
def export_database():
    return jsonify({"message": "Database exported"})

@deepaudit_api.route('/database/import', methods=['POST'])
def import_database():
    return jsonify({"message": "Database imported"})

@deepaudit_api.route('/database/clear', methods=['DELETE'])
def clear_database():
    return jsonify({"message": "Database cleared"})

@deepaudit_api.route('/database/stats', methods=['GET'])
def get_database_stats():
    return jsonify({"users": 1, "projects": len(projects), "tasks": len(tasks)})

@deepaudit_api.route('/database/health', methods=['GET'])
def get_database_health():
    return jsonify({"status": "healthy"})

# SSH 密钥相关接口
@deepaudit_api.route('/ssh-keys/generate', methods=['POST'])
def generate_ssh_key():
    return jsonify({"private_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...", "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC..."})

@deepaudit_api.route('/ssh-keys/', methods=['GET'])
def get_ssh_keys():
    return jsonify(ssh_keys)

@deepaudit_api.route('/ssh-keys/', methods=['DELETE'])
def delete_ssh_key():
    return jsonify({"message": "SSH key deleted"})

@deepaudit_api.route('/ssh-keys/test', methods=['POST'])
def test_ssh_key():
    return jsonify({"message": "SSH key test successful"})

@deepaudit_api.route('/ssh-keys/known-hosts', methods=['DELETE'])
def clear_known_hosts():
    return jsonify({"message": "Known hosts cleared"})

# Agent 任务相关接口
@deepaudit_api.route('/agent-tasks/', methods=['GET'])
def get_agent_tasks():
    return jsonify(agent_tasks)

@deepaudit_api.route('/agent-tasks/', methods=['POST'])
def create_agent_task():
    data = request.json
    new_task = {
        "id": len(agent_tasks) + 1,
        "project_id": data.get('project_id', 1),
        "name": data.get('name', 'New Agent Task'),
        "status": "pending",
        "created_by": 1,
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "updated_at": datetime.utcnow().isoformat() + 'Z'
    }
    agent_tasks.append(new_task)
    return jsonify(new_task), 201

@deepaudit_api.route('/agent-tasks/<int:id>', methods=['GET'])
def get_agent_task(id):
    task = next((t for t in agent_tasks if t['id'] == id), None)
    if task:
        return jsonify(task)
    return jsonify({"detail": "Agent task not found"}), 404

@deepaudit_api.route('/agent-tasks/<int:id>/start', methods=['POST'])
def start_agent_task(id):
    return jsonify({"message": "Agent task started"})

@deepaudit_api.route('/agent-tasks/<int:id>/cancel', methods=['POST'])
def cancel_agent_task(id):
    return jsonify({"message": "Agent task cancelled"})

@deepaudit_api.route('/agent-tasks/<int:id>/events/list', methods=['GET'])
def get_agent_task_events(id):
    return jsonify([])

@deepaudit_api.route('/agent-tasks/<int:id>/findings', methods=['GET'])
def get_agent_task_findings(id):
    return jsonify([])

@deepaudit_api.route('/agent-tasks/<int:id>/findings/<int:finding_id>', methods=['GET'])
def get_agent_task_finding(id, finding_id):
    return jsonify({"message": "Finding retrieved"})

@deepaudit_api.route('/agent-tasks/<int:id>/findings/<int:finding_id>', methods=['PATCH'])
def update_agent_task_finding(id, finding_id):
    return jsonify({"message": "Finding updated"})

@deepaudit_api.route('/agent-tasks/<int:id>/summary', methods=['GET'])
def get_agent_task_summary(id):
    return jsonify({"message": "Summary retrieved"})

@deepaudit_api.route('/agent-tasks/<int:id>/agent-tree', methods=['GET'])
def get_agent_task_tree(id):
    return jsonify({"message": "Agent tree retrieved"})

@deepaudit_api.route('/agent-tasks/<int:id>/checkpoints', methods=['GET'])
def get_agent_task_checkpoints(id):
    return jsonify([])

@deepaudit_api.route('/agent-tasks/<int:id>/checkpoints/<int:checkpoint_id>', methods=['GET'])
def get_agent_task_checkpoint(id, checkpoint_id):
    return jsonify({"message": "Checkpoint retrieved"})

@deepaudit_api.route('/agent-tasks/<int:id>/report', methods=['GET'])
def get_agent_task_report(id):
    return jsonify({"message": "Report retrieved"})

@deepaudit_api.route('/agent-tasks/<int:id>/stream', methods=['GET'])
def stream_agent_task(id):
    return jsonify({"event": "start", "data": {"task_id": id, "status": "running"}})

# 提示词相关接口
@deepaudit_api.route('/prompts', methods=['GET'])
def get_prompts():
    return jsonify(prompts)

@deepaudit_api.route('/prompts/<int:id>', methods=['GET'])
def get_prompt(id):
    prompt = next((p for p in prompts if p['id'] == id), None)
    if prompt:
        return jsonify(prompt)
    return jsonify({"detail": "Prompt not found"}), 404

@deepaudit_api.route('/prompts', methods=['POST'])
def create_prompt():
    data = request.json
    new_prompt = {
        "id": len(prompts) + 1,
        "name": data.get('name', 'New Prompt'),
        "content": data.get('content', ''),
        "is_active": True,
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "updated_at": datetime.utcnow().isoformat() + 'Z'
    }
    prompts.append(new_prompt)
    return jsonify(new_prompt), 201

@deepaudit_api.route('/prompts/<int:id>', methods=['PUT'])
def update_prompt(id):
    data = request.json
    prompt = next((p for p in prompts if p['id'] == id), None)
    if prompt:
        prompt.update({
            "name": data.get('name', prompt['name']),
            "content": data.get('content', prompt['content']),
            "is_active": data.get('is_active', prompt['is_active']),
            "updated_at": datetime.utcnow().isoformat() + 'Z'
        })
        return jsonify(prompt)
    return jsonify({"detail": "Prompt not found"}), 404

@deepaudit_api.route('/prompts/<int:id>', methods=['DELETE'])
def delete_prompt(id):
    prompt = next((p for p in prompts if p['id'] == id), None)
    if prompt:
        prompts.remove(prompt)
        return jsonify({"message": "Prompt deleted"})
    return jsonify({"detail": "Prompt not found"}), 404

@deepaudit_api.route('/prompts/test', methods=['POST'])
def test_prompt():
    return jsonify({"message": "Prompt test successful"})

@deepaudit_api.route('/prompts/<int:id>/set-default', methods=['POST'])
def set_default_prompt(id):
    return jsonify({"message": "Prompt set as default"})

# 规则相关接口
@deepaudit_api.route('/rules', methods=['GET'])
def get_rules():
    return jsonify(rules)

@deepaudit_api.route('/rules/<int:id>', methods=['GET'])
def get_rule(id):
    rule = next((r for r in rules if r['id'] == id), None)
    if rule:
        return jsonify(rule)
    return jsonify({"detail": "Rule not found"}), 404

@deepaudit_api.route('/rules', methods=['POST'])
def create_rule():
    data = request.json
    new_rule = {
        "id": len(rules) + 1,
        "name": data.get('name', 'New Rule'),
        "description": data.get('description', ''),
        "is_active": True,
        "rules": [],
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "updated_at": datetime.utcnow().isoformat() + 'Z'
    }
    rules.append(new_rule)
    return jsonify(new_rule), 201

@deepaudit_api.route('/rules/<int:id>', methods=['PUT'])
def update_rule(id):
    data = request.json
    rule = next((r for r in rules if r['id'] == id), None)
    if rule:
        rule.update({
            "name": data.get('name', rule['name']),
            "description": data.get('description', rule['description']),
            "is_active": data.get('is_active', rule['is_active']),
            "updated_at": datetime.utcnow().isoformat() + 'Z'
        })
        return jsonify(rule)
    return jsonify({"detail": "Rule not found"}), 404

@deepaudit_api.route('/rules/<int:id>', methods=['DELETE'])
def delete_rule(id):
    rule = next((r for r in rules if r['id'] == id), None)
    if rule:
        rules.remove(rule)
        return jsonify({"message": "Rule deleted"})
    return jsonify({"detail": "Rule not found"}), 404

@deepaudit_api.route('/rules/<int:id>/export', methods=['GET'])
def export_rule(id):
    return jsonify({"message": "Rule exported"})

@deepaudit_api.route('/rules/import', methods=['POST'])
def import_rule():
    return jsonify({"message": "Rule imported"})

@deepaudit_api.route('/rules/<int:id>/rules', methods=['POST'])
def add_rule_to_set(id):
    return jsonify({"message": "Rule added to set"})

@deepaudit_api.route('/rules/<int:id>/rules/<int:rule_id>', methods=['PUT'])
def update_rule_in_set(id, rule_id):
    return jsonify({"message": "Rule updated in set"})

@deepaudit_api.route('/rules/<int:id>/rules/<int:rule_id>', methods=['DELETE'])
def delete_rule_from_set(id, rule_id):
    return jsonify({"message": "Rule deleted from set"})

@deepaudit_api.route('/rules/<int:id>/rules/<int:rule_id>/toggle', methods=['PUT'])
def toggle_rule_in_set(id, rule_id):
    return jsonify({"message": "Rule toggled in set"})
