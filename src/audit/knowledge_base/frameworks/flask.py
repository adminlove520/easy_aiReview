from ..base import KnowledgeCategory, KnowledgeDocument

flask_knowledge = [
    KnowledgeDocument(
        id="flask-1",
        title="Flask 安全最佳实践",
        content="""# Flask 安全最佳实践

## 核心安全配置

### 1. 使用 Flask-Security 或 Flask-Login
对于用户认证，使用成熟的扩展如 Flask-Security 或 Flask-Login。

```python
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-secret-key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 验证用户
        user = User(1)
        login_user(user)
        return redirect(url_for('protected'))
    return render_template('login.html')

@app.route('/protected')
@login_required
def protected():
    return 'Protected area'
```

### 2. 配置安全的会话设置

```python
app.config['SESSION_COOKIE_SECURE'] = True  # 只通过 HTTPS 发送
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止 JavaScript 访问
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'  # 防止 CSRF 攻击
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # 会话超时
```

### 3. 使用 Flask-Talisman 增强安全
Flask-Talisman 可以帮助设置安全的 HTTP 头。

```python
from flask_talisman import Talisman

Talisman(app)
```

## 输入验证

### 1. 使用 Flask-WTF 进行表单验证

```python
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Log In')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 处理登录
        return redirect(url_for('home'))
    return render_template('login.html', form=form)
```

### 2. 手动验证 JSON 数据

```python
@app.route('/api/data', methods=['POST'])
def api_data():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    # 验证必填字段
    if 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 验证数据格式
    if not isinstance(data['username'], str) or len(data['username']) < 3:
        return jsonify({'error': 'Invalid username'}), 400
    
    return jsonify({'message': 'Data received successfully'})
```

## 数据库安全

### 1. 使用 ORM 防止 SQL 注入
使用 SQLAlchemy 等 ORM 来防止 SQL 注入攻击。

```python
from flask_sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

# 安全的查询方式
user = User.query.filter_by(username=request.form['username']).first()

# 避免直接拼接 SQL
# 错误示例: db.session.execute(f"SELECT * FROM user WHERE username = '{request.form['username']}'")
```

### 2. 密码加密
使用 Werkzeug 的安全密码哈希功能。

```python
from werkzeug.security import generate_password_hash, check_password_hash

# 加密密码
password_hash = generate_password_hash('password123')

# 验证密码
if check_password_hash(password_hash, 'password123'):
    # 密码正确
    pass
```

## CSRF 保护

### 1. 使用 Flask-WTF 的 CSRF 保护

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# 在表单中包含 CSRF 令牌
<form method="post">
    {{ form.hidden_tag() }}
    <!-- 表单字段 -->
</form>

# 对于 AJAX 请求
<meta name="csrf-token" content="{{ csrf_token() }}">

<script>
    $.ajax({
        url: '/api/data',
        type: 'POST',
        headers: {
            'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
        },
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function(response) {
            console.log(response);
        }
    });
</script>
```

## 文件上传安全

### 1. 限制上传文件类型

```python
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    
    # 检查文件扩展名
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return 'Invalid file type', 400
    
    # 安全地保存文件
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return 'File uploaded successfully'
```

### 2. 配置上传文件夹

```python
import os
from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB 限制

# 确保上传文件夹存在
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
```

## 错误处理

### 1. 自定义错误页面

```python
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    # 记录错误
    app.logger.error(f"Server Error: {e}, {traceback.format_exc()}")
    return render_template('500.html'), 500
```

### 2. 避免信息泄露
在生产环境中，不要向用户显示详细的错误信息。

```python
app.config['DEBUG'] = False  # 生产环境中设置为 False

@app.route('/debug')
def debug():
    # 错误示例：在生产环境中显示调试信息
    # return f"Debug info: {request.args}"
    
    # 正确做法：只在开发环境中显示
    if app.debug:
        return f"Debug info: {request.args}"
    return "Access denied"
```

## API 安全

### 1. 使用 API 密钥或令牌

```python
from functools import wraps

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != app.config['API_KEY']:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/protected')
@require_api_key
def api_protected():
    return jsonify({'message': 'Protected API endpoint'})
```

### 2. 实现速率限制

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/data')
@limiter.limit("10 per minute")
def api_data():
    return jsonify({'message': 'Rate limited endpoint'})
```

## 部署安全

### 1. 使用环境变量

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['API_KEY'] = os.environ.get('API_KEY')
```

### 2. 使用 HTTPS
在生产环境中，始终使用 HTTPS。

```python
# 在 Flask 中启用 HTTPS 重定向
@app.before_request
def before_request():
    if not request.is_secure and app.env == 'production':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
```

### 3. 使用 Gunicorn 或 uWSGI
在生产环境中，使用 WSGI 服务器如 Gunicorn 或 uWSGI。

```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## 监控和日志

### 1. 配置日志

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置文件日志
file_handler = RotatingFileHandler('app.log', maxBytes=1024 * 1024 * 100, backupCount=10)
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

# 配置控制台日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
app.logger.addHandler(console_handler)

app.logger.setLevel(logging.INFO)
app.logger.info('App started')
```

### 2. 监控异常
使用 Sentry 等服务来监控应用程序异常。

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

## 依赖管理

### 1. 定期更新依赖
使用 pip-audit 来检查依赖中的安全漏洞。

```bash
pip install pip-audit
pip-audit
```

### 2. 使用虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 总结

Flask 应用程序的安全需要多层防御策略，包括：

1. **认证和授权**：使用 Flask-Login 或 Flask-Security
2. **输入验证**：使用 Flask-WTF 或手动验证
3. **数据库安全**：使用 ORM，密码加密
4. **CSRF 保护**：使用 Flask-WTF 的 CSRF 保护
5. **文件上传安全**：限制文件类型和大小
6. **错误处理**：自定义错误页面，避免信息泄露
7. **API 安全**：使用 API 密钥，实现速率限制
8. **部署安全**：使用环境变量，HTTPS，WSGI 服务器
9. **监控和日志**：配置日志，监控异常
10. **依赖管理**：定期更新依赖，使用虚拟环境

通过实施这些最佳实践，可以显著提高 Flask 应用程序的安全性。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["flask", "python", "security", "best-practice"],
        severity="medium",
        cwe_ids=["CWE-614", "CWE-352", "CWE-79"],
        owasp_ids=["A1", "A2", "A3"]
    ),
    KnowledgeDocument(
        id="flask-2",
        title="Flask 性能优化",
        content="""# Flask 性能优化

## 代码级优化

### 1. 使用蓝图组织路由
蓝图可以帮助组织大型应用程序的路由，提高代码可读性和性能。

```python
from flask import Blueprint

api_bp = Blueprint('api', __name__)

@api_bp.route('/users')
def get_users():
    return jsonify({'users': []})

app.register_blueprint(api_bp, url_prefix='/api')
```

### 2. 使用缓存
缓存频繁访问的数据可以显著提高性能。

```python
from flask_caching import Cache

config = {
    "DEBUG": True,
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 300
}

app.config.from_mapping(config)
cache = Cache(app)

@cache.cached(timeout=60)
@app.route('/expensive')
def expensive_operation():
    # 执行昂贵的操作
    time.sleep(2)
    return jsonify({'result': 'Expensive operation completed'})
```

### 3. 使用异步处理
对于 I/O 密集型操作，使用异步处理可以提高性能。

```python
import asyncio
from flask import Flask

app = Flask(__name__)

async def async_task():
    # 执行异步任务
    await asyncio.sleep(2)
    return 'Task completed'

@app.route('/async')
async def async_route():
    result = await async_task()
    return jsonify({'result': result})
```

## 数据库优化

### 1. 使用连接池
SQLAlchemy 支持连接池，可以减少数据库连接开销。

```python
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 30
app.config['SQLALCHEMY_POOL_RECYCLE'] = 1800  # 30分钟
```

### 2. 优化查询

```python
# 避免 N+1 查询
# 不好的做法
users = User.query.all()
for user in users:
    # 每次循环都会执行新的查询
    posts = user.posts

# 好的做法（使用预加载）
from sqlalchemy.orm import joinedload
users = User.query.options(joinedload(User.posts)).all()
for user in users:
    # 使用预加载的数据，不会执行新的查询
    posts = user.posts

# 限制结果集大小
@app.route('/users')
def get_users():
    # 限制返回 100 条记录
    users = User.query.limit(100).all()
    return jsonify({'users': [user.to_dict() for user in users]})
```

### 3. 使用原生 SQL 进行复杂查询
对于复杂查询，使用原生 SQL 可以提高性能。

```python
from sqlalchemy import text

@app.route('/stats')
def get_stats():
    sql = text('SELECT COUNT(*) as count, status FROM users GROUP BY status')
    result = db.session.execute(sql).fetchall()
    return jsonify({'stats': [dict(row) for row in result]})
```

## 部署优化

### 1. 使用 Gunicorn 或 uWSGI

```bash
# 使用 Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# 使用 uWSGI
uwsgi --http 0.0.0.0:8000 --wsgi-file app.py --callable app --processes 4 --threads 2
```

### 2. 启用 GZIP 压缩

```python
from flask_compress import Compress

Compress(app)
```

### 3. 使用 CDN 分发静态资源

```python
app.config['CDN_DOMAIN'] = 'https://your-cdn-domain.com'

# 在模板中使用 CDN
<script src="{{ url_for('static', filename='js/app.js') }}"></script>
```

### 4. 优化静态文件服务
在生产环境中，使用 Nginx 或 Apache 来服务静态文件。

```nginx
server {
    listen 80;
    server_name example.com;
    
    location /static/ {
        alias /path/to/app/static/;
        expires 30d;
    }
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 内存优化

### 1. 避免内存泄漏

```python
# 不好的做法：全局变量累积数据
global_data = []

@app.route('/add')
def add_data():
    global_data.append({'data': request.args.get('data')})
    return jsonify({'message': 'Data added'})

# 好的做法：使用数据库或缓存
@app.route('/add')
def add_data():
    data = Data(value=request.args.get('data'))
    db.session.add(data)
    db.session.commit()
    return jsonify({'message': 'Data added'})
```

### 2. 使用生成器处理大文件

```python
@app.route('/download')
def download_large_file():
    def generate():
        with open('large_file.txt', 'r') as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                yield chunk
    return Response(generate(), mimetype='text/plain')
```

## 监控和分析

### 1. 使用 Flask-DebugToolbar
在开发环境中，使用 Flask-DebugToolbar 来分析性能。

```python
from flask_debugtoolbar import DebugToolbarExtension

app.config['DEBUG_TB_ENABLED'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)
```

### 2. 实现健康检查端点

```python
@app.route('/health')
def health_check():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()})
```

### 3. 使用 Prometheus 监控

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('request_count', 'Total request count')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')

@app.before_request
def before_request():
    REQUEST_COUNT.inc()
    g.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(g, 'start_time'):
        latency = time.time() - g.start_time
        REQUEST_LATENCY.observe(latency)
    return response

@app.route('/metrics')
def metrics():
    return Response(generate_latest(), mimetype='text/plain')
```

## 总结

Flask 性能优化的关键策略包括：

1. **代码级优化**：使用蓝图，缓存，异步处理
2. **数据库优化**：使用连接池，优化查询，使用原生 SQL
3. **部署优化**：使用 Gunicorn/uWSGI，GZIP 压缩，CDN，优化静态文件服务
4. **内存优化**：避免内存泄漏，使用生成器处理大文件
5. **监控和分析**：使用 Flask-DebugToolbar，实现健康检查，使用 Prometheus 监控

通过实施这些优化策略，可以显著提高 Flask 应用程序的性能和可靠性。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["flask", "python", "performance", "optimization"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    ),
    KnowledgeDocument(
        id="flask-3",
        title="Flask 错误处理最佳实践",
        content="""# Flask 错误处理最佳实践

## 基础错误处理

### 1. 自定义错误处理器
Flask 允许你为特定的 HTTP 状态码或异常类型注册错误处理器。

```python
from flask import Flask, render_template

app = Flask(__name__)

# 处理 404 错误
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# 处理 500 错误
@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500
```

### 2. 处理特定异常

```python
from sqlalchemy.exc import SQLAlchemyError

# 处理数据库异常
@app.errorhandler(SQLAlchemyError)
def handle_database_error(error):
    app.logger.error(f"Database error: {error}")
    return render_template('database_error.html'), 500

# 处理自定义异常
class CustomError(Exception):
    pass

@app.errorhandler(CustomError)
def handle_custom_error(error):
    return render_template('custom_error.html', error=error), 400
```

## 高级错误处理

### 1. 全局异常处理器
创建一个全局异常处理器来捕获所有未处理的异常。

```python
import traceback

@app.errorhandler(Exception)
def handle_exception(error):
    # 记录错误
    app.logger.error(f"Unhandled exception: {error}\n{traceback.format_exc()}")
    
    # 在开发环境中显示详细错误
    if app.debug:
        return f"{error}\n{traceback.format_exc()}", 500
    
    # 在生产环境中显示友好错误页面
    return render_template('500.html'), 500
```

### 2. 自定义错误类
创建自定义错误类来处理不同类型的错误。

```python
class AppError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

@app.errorhandler(AppError)
def handle_app_error(error):
    response = {
        'error': error.message,
        'status_code': error.status_code
    }
    return jsonify(response), error.status_code

# 使用自定义错误
@app.route('/api/data')
def api_data():
    if not request.args.get('id'):
        raise AppError('Missing required parameter: id', 400)
    return jsonify({'data': 'success'})
```

## API 错误处理

### 1. 统一 API 错误响应

```python
def api_error(message, status_code=400):
    response = {
        'error': message,
        'status_code': status_code,
        'timestamp': datetime.utcnow().isoformat()
    }
    return jsonify(response), status_code

@app.route('/api/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return api_error('User not found', 404)
    return jsonify(user.to_dict())
```

### 2. 使用 Flask-RESTful 的错误处理

```python
from flask_restful import Api, Resource

api = Api(app)

# 自定义错误处理
@api.errorhandler
ndef handle_error(error):
    response = {
        'error': str(error),
        'status_code': getattr(error, 'code', 500)
    }
    return response, getattr(error, 'code', 500)

class UserResource(Resource):
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user.to_dict()

api.add_resource(UserResource, '/api/users/<int:user_id>')
```

## 日志记录

### 1. 配置详细日志

```python
import logging
from logging.handlers import RotatingFileHandler

# 配置文件日志
file_handler = RotatingFileHandler(
    'app.log',
    maxBytes=1024 * 1024 * 100,  # 100MB
    backupCount=10
)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# 配置控制台日志
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))

# 添加处理器
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.DEBUG)

# 在错误处理器中使用
@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.error(f"Unhandled exception: {error}", exc_info=True)
    return render_template('500.html'), 500
```

### 2. 记录请求信息

```python
@app.before_request
def log_request():
    app.logger.info(f"Request: {request.method} {request.url}")

@app.after_request
def log_response(response):
    app.logger.info(f"Response: {response.status} for {request.method} {request.url}")
    return response
```

## 生产环境错误处理

### 1. 避免信息泄露
在生产环境中，不要向用户显示详细的错误信息。

```python
app.config['DEBUG'] = False
app.config['TESTING'] = False

@app.errorhandler(Exception)
def handle_exception(error):
    # 记录错误
    app.logger.error(f"Unhandled exception: {error}", exc_info=True)
    
    # 只返回基本错误信息
    return render_template('500.html'), 500
```

### 2. 实现优雅关闭

```python
import signal
import sys

def signal_handler(sig, frame):
    app.logger.info('Shutting down gracefully...')
    # 清理资源
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
```

### 3. 使用 Sentry 监控错误

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment=app.config.get('ENVIRONMENT', 'development')
)
```

## 表单验证错误处理

### 1. 使用 Flask-WTF 的错误处理

```python
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # 处理表单提交
        return redirect(url_for('success'))
    # 表单验证失败，显示错误信息
    return render_template('contact.html', form=form)

# 在模板中显示错误
# contact.html
{% if form.errors %}
    <div class="alert alert-danger">
        {% for field, errors in form.errors.items() %}
            {% for error in errors %}
                {{ field }}: {{ error }}<br>
            {% endfor %}
        {% endfor %}
    </div>
{% endif %}
```

### 2. 自定义表单验证

```python
from wtforms import validators

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[DataRequired(), 
                                               validators.EqualTo('password', message='Passwords must match')])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists')
```

## 总结

Flask 错误处理的最佳实践包括：

1. **基础错误处理**：自定义错误处理器，处理特定异常
2. **高级错误处理**：全局异常处理器，自定义错误类
3. **API 错误处理**：统一 API 错误响应，使用 Flask-RESTful 的错误处理
4. **日志记录**：配置详细日志，记录请求信息
5. **生产环境错误处理**：避免信息泄露，实现优雅关闭，使用 Sentry 监控错误
6. **表单验证错误处理**：使用 Flask-WTF 的错误处理，自定义表单验证

通过实施这些最佳实践，可以构建更健壮、更可靠的 Flask 应用程序。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["flask", "python", "error-handling", "best-practice"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    )
]
