from ..base import KnowledgeCategory, KnowledgeDocument

express_knowledge = [
    KnowledgeDocument(
        id="express-1",
        title="Express.js 安全最佳实践",
        content="""# Express.js 安全最佳实践

## 核心安全配置

### 1. 使用 helmet 中间件
Helmet 可以帮助设置各种 HTTP 头，防止常见的 Web 漏洞。

```javascript
const helmet = require('helmet');
app.use(helmet());
```

### 2. 实施 CORS 策略
使用 cors 包来正确配置跨域资源共享。

```javascript
const cors = require('cors');
// 允许所有来源（不推荐用于生产环境）
app.use(cors());
// 或配置特定来源
app.use(cors({
  origin: 'https://yourdomain.com'
}));
```

### 3. 防止 CSRF 攻击
使用 csurf 中间件来防止跨站请求伪造攻击。

```javascript
const csrf = require('csurf');
const csrfProtection = csrf({ cookie: true });
app.use(csrfProtection);
```

## 路由安全

### 1. 验证输入
始终验证用户输入，使用 express-validator。

```javascript
const { body, validationResult } = require('express-validator');

app.post('/user', [
  body('username').isLength({ min: 3 }),
  body('email').isEmail()
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  // 处理请求
});
```

### 2. 使用参数化查询
防止 SQL 注入攻击。

```javascript
// 错误示例
const sql = `SELECT * FROM users WHERE username = '${req.body.username}'`;

// 正确示例
const sql = 'SELECT * FROM users WHERE username = ?';
db.query(sql, [req.body.username], (err, results) => {
  // 处理结果
});
```

### 3. 限制请求速率
使用 express-rate-limit 来防止暴力攻击。

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15分钟
  max: 100 // 每个IP限制100个请求
});

app.use(limiter);
```

## 认证和授权

### 1. 使用 bcrypt 加密密码

```javascript
const bcrypt = require('bcrypt');
const saltRounds = 10;

// 加密密码
bcrypt.hash(password, saltRounds, (err, hash) => {
  // 存储哈希值
});

// 验证密码
bcrypt.compare(password, hash, (err, result) => {
  // 结果为 true 或 false
});
```

### 2. 使用 JWT 进行身份验证

```javascript
const jwt = require('jsonwebtoken');

// 生成令牌
const token = jwt.sign({ userId: user.id }, process.env.JWT_SECRET, {
  expiresIn: '1h'
});

// 验证令牌
const verifyToken = (req, res, next) => {
  const token = req.headers.authorization;
  if (!token) return res.status(401).send('Access denied');
  
  try {
    const verified = jwt.verify(token, process.env.JWT_SECRET);
    req.user = verified;
    next();
  } catch (err) {
    res.status(400).send('Invalid token');
  }
};

app.use('/protected', verifyToken);
```

### 3. 实现正确的会话管理

```javascript
const session = require('express-session');
const MongoDBStore = require('connect-mongodb-session')(session);

const store = new MongoDBStore({
  uri: process.env.MONGODB_URI,
  collection: 'sessions'
});

app.use(session({
  secret: process.env.SESSION_SECRET,
  resave: false,
  saveUninitialized: false,
  store: store,
  cookie: {
    secure: process.env.NODE_ENV === 'production',
    httpOnly: true,
    sameSite: 'strict'
  }
}));
```

## 错误处理

### 1. 实现全局错误处理

```javascript
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});
```

### 2. 避免在生产环境中泄露错误细节

```javascript
app.use((err, req, res, next) => {
  if (process.env.NODE_ENV === 'production') {
    res.status(500).send('Internal Server Error');
  } else {
    console.error(err.stack);
    res.status(500).send(err.message);
  }
});
```

## 依赖管理

### 1. 定期更新依赖
使用 npm audit 来检查依赖中的安全漏洞。

```bash
npm audit
npm audit fix
```

### 2. 使用 npm ci 进行部署
在生产环境中使用 npm ci 而不是 npm install 来确保依赖版本的一致性。

```bash
npm ci
```

## 部署安全

### 1. 使用环境变量
使用 dotenv 包来管理环境变量，不要在代码中硬编码敏感信息。

```javascript
require('dotenv').config();
const dbPassword = process.env.DB_PASSWORD;
```

### 2. 禁用 X-Powered-By 头

```javascript
app.disable('x-powered-by');
```

### 3. 配置 HTTPS
在生产环境中始终使用 HTTPS。

```javascript
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};

https.createServer(options, app).listen(443);
```

## 常见漏洞防护

### 1. 防止路径遍历攻击
使用 path.resolve 和 path.normalize 来确保路径安全。

```javascript
const path = require('path');

app.get('/files/:filename', (req, res) => {
  const filename = req.params.filename;
  const safePath = path.resolve('./uploads', filename);
  
  // 验证路径是否在预期目录内
  if (!safePath.startsWith(path.resolve('./uploads'))) {
    return res.status(403).send('Access denied');
  }
  
  res.sendFile(safePath);
});
```

### 2. 防止命令注入攻击
避免使用 child_process.exec，使用 child_process.execFile 或 spawn 代替。

```javascript
const { execFile } = require('child_process');

// 安全的方式
execFile('ls', ['-la'], (error, stdout, stderr) => {
  console.log(stdout);
});
```

### 3. 防止 XSS 攻击
对用户输入进行适当的转义和验证。

```javascript
// 使用模板引擎的自动转义
// 或手动转义
const escapeHtml = (unsafe) => {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};
```

## 监控和日志

### 1. 实现结构化日志

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

if (process.env.NODE_ENV !== 'production') {
  logger.add(new winston.transports.Console({
    format: winston.format.simple()
  }));
}

app.use((req, res, next) => {
  logger.info(`${req.method} ${req.url}`);
  next();
});
```

### 2. 监控异常和安全事件
使用 Sentry 或类似服务来监控应用程序异常。

```javascript
const Sentry = require('@sentry/node');

Sentry.init({
  dsn: process.env.SENTRY_DSN
});

app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.errorHandler());
```

## 总结

Express.js 应用程序的安全需要多层防御策略，包括：

1. **正确配置中间件**：helmet, cors, csurf 等
2. **输入验证**：使用 express-validator
3. **安全认证**：bcrypt 加密，JWT 令牌
4. **防止常见漏洞**：SQL 注入，XSS，CSRF 等
5. **依赖管理**：定期更新，npm audit
6. **部署安全**：HTTPS，环境变量
7. **监控和日志**：结构化日志，异常监控

通过实施这些最佳实践，可以显著提高 Express.js 应用程序的安全性。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["express", "node.js", "security", "best-practice"],
        severity="medium",
        cwe_ids=["CWE-614", "CWE-352", "CWE-79"],
        owasp_ids=["A1", "A2", "A3"]
    ),
    KnowledgeDocument(
        id="express-2",
        title="Express.js 性能优化",
        content="""# Express.js 性能优化

## 代码级优化

### 1. 使用异步处理
避免阻塞事件循环，使用异步函数和 Promise。

```javascript
// 同步版本（慢）
app.get('/sync', (req, res) => {
  const result = slowFunction(); // 阻塞事件循环
  res.send(result);
});

// 异步版本（快）
app.get('/async', async (req, res) => {
  const result = await slowFunction(); // 非阻塞
  res.send(result);
});
```

### 2. 实现中间件顺序优化
将频繁使用的中间件放在前面，减少不必要的处理。

```javascript
// 正确的顺序
app.use(helmet()); // 安全中间件
app.use(express.json()); // 解析请求体
app.use('/api', apiRoutes); // API 路由
app.use(express.static('public')); // 静态文件
app.use(errorHandler); // 错误处理
```

### 3. 避免在路由处理程序中进行昂贵操作
将数据库连接、缓存初始化等操作移到应用程序启动时。

```javascript
// 启动时初始化
const db = require('./db');
const cache = require('./cache');

// 路由处理程序中使用
app.get('/data', (req, res) => {
  const data = cache.get('key') || db.query('SELECT * FROM table');
  res.send(data);
});
```

## 缓存策略

### 1. 使用 Redis 进行缓存

```javascript
const redis = require('redis');
const client = redis.createClient();

app.get('/api/data', async (req, res) => {
  const cacheKey = `data:${req.query.id}`;
  
  // 尝试从缓存获取
  client.get(cacheKey, async (err, cachedData) => {
    if (cachedData) {
      return res.send(JSON.parse(cachedData));
    }
    
    // 缓存未命中，从数据库获取
    const data = await db.query('SELECT * FROM table WHERE id = ?', [req.query.id]);
    
    // 存入缓存
    client.set(cacheKey, JSON.stringify(data), 'EX', 3600); // 1小时过期
    
    res.send(data);
  });
});
```

### 2. 实现 HTTP 缓存
设置适当的缓存头来减少重复请求。

```javascript
app.get('/static/*', (req, res) => {
  res.set('Cache-Control', 'public, max-age=31536000'); // 1年
  res.sendFile(path.join(__dirname, 'public', req.path));
});
```

## 数据库优化

### 1. 使用连接池

```javascript
const mysql = require('mysql2');

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});

app.get('/users', (req, res) => {
  pool.execute('SELECT * FROM users', (err, results) => {
    res.send(results);
  });
});
```

### 2. 优化查询
使用索引，避免 SELECT *，限制结果集大小。

```javascript
// 不好的查询
app.get('/users', (req, res) => {
  db.query('SELECT * FROM users', (err, results) => {
    res.send(results);
  });
});

// 优化的查询
app.get('/users', (req, res) => {
  db.query('SELECT id, name, email FROM users LIMIT 100', (err, results) => {
    res.send(results);
  });
});
```

## 部署优化

### 1. 使用 PM2 进行进程管理
PM2 可以帮助管理 Node.js 进程，提供负载均衡和自动重启。

```bash
npm install -g pm2
pm start # 或 pm2 start app.js
```

### 2. 启用 GZIP 压缩

```javascript
const compression = require('compression');
app.use(compression());
```

### 3. 使用 CDN 分发静态资源
将静态资源（CSS，JavaScript，图片）托管在 CDN 上。

### 4. 实现负载均衡
使用 Nginx 作为反向代理和负载均衡器。

```nginx
upstream express_app {
  server localhost:3000;
  server localhost:3001;
  server localhost:3002;
}

server {
  listen 80;
  server_name example.com;
  
  location / {
    proxy_pass http://express_app;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
  }
}
```

## 监控和分析

### 1. 使用 New Relic 或类似工具
监控应用程序性能，识别瓶颈。

### 2. 实现健康检查端点

```javascript
app.get('/health', (req, res) => {
  res.status(200).send('OK');
});
```

### 3. 分析内存使用
使用 Node.js 的内置工具或第三方库来监控内存使用。

```javascript
app.get('/memory', (req, res) => {
  const memory = process.memoryUsage();
  res.json({
    heapTotal: memory.heapTotal,
    heapUsed: memory.heapUsed,
    external: memory.external
  });
});
```

## 总结

Express.js 性能优化的关键策略包括：

1. **代码级优化**：异步处理，中间件顺序，避免昂贵操作
2. **缓存策略**：Redis 缓存，HTTP 缓存
3. **数据库优化**：连接池，查询优化
4. **部署优化**：PM2，GZIP 压缩，CDN，负载均衡
5. **监控和分析**：性能监控，健康检查，内存分析

通过实施这些优化策略，可以显著提高 Express.js 应用程序的性能和可靠性。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["express", "node.js", "performance", "optimization"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    ),
    KnowledgeDocument(
        id="express-3",
        title="Express.js 错误处理最佳实践",
        content="""# Express.js 错误处理最佳实践

## 基础错误处理

### 1. 内置错误处理中间件
Express 提供了内置的错误处理中间件，它会捕获并处理应用程序中的错误。

```javascript
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).send('Something broke!');
});
```

### 2. 错误处理中间件位置
错误处理中间件必须放在所有其他中间件和路由之后。

```javascript
// 其他中间件和路由
app.use(express.json());
app.use('/api', apiRoutes);

// 错误处理中间件（最后）
app.use(errorHandler);
```

## 高级错误处理

### 1. 自定义错误类
创建自定义错误类来处理不同类型的错误。

```javascript
class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.status = `${statusCode}`.startsWith('4') ? 'fail' : 'error';
    this.isOperational = true;
    
    Error.captureStackTrace(this, this.constructor);
  }
}

// 使用
app.get('/api/users/:id', async (req, res, next) => {
  const user = await User.findById(req.params.id);
  if (!user) {
    return next(new AppError('User not found', 404));
  }
  res.send(user);
});
```

### 2. 全局错误处理中间件
实现一个统一的全局错误处理中间件。

```javascript
const globalErrorHandler = (err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';
  
  if (process.env.NODE_ENV === 'development') {
    // 开发环境：详细错误信息
    res.status(err.statusCode).json({
      status: err.status,
      error: err,
      message: err.message,
      stack: err.stack
    });
  } else if (process.env.NODE_ENV === 'production') {
    // 生产环境：简化错误信息
    let error = { ...err };
    error.message = err.message;
    
    // 处理特定类型的错误
    if (err.name === 'CastError') {
      error = new AppError(`Invalid ${err.path}: ${err.value}`, 400);
    }
    if (err.code === 11000) {
      error = new AppError('Duplicate field value', 400);
    }
    if (err.name === 'ValidationError') {
      const errors = Object.values(err.errors).map(el => el.message);
      error = new AppError(`Validation error: ${errors.join('. ')}`, 400);
    }
    
    res.status(error.statusCode).json({
      status: error.status,
      message: error.message || 'Internal Server Error'
    });
  }
};

app.use(globalErrorHandler);
```

### 3. 异步错误处理
处理异步操作中的错误。

```javascript
// 方法 1：使用 try-catch
app.get('/api/data', async (req, res, next) => {
  try {
    const data = await someAsyncOperation();
    res.send(data);
  } catch (err) {
    next(err); // 传递给错误处理中间件
  }
});

// 方法 2：使用错误处理包装器
const catchAsync = fn => {
  return (req, res, next) => {
    fn(req, res, next).catch(next);
  };
};

app.get('/api/data', catchAsync(async (req, res, next) => {
  const data = await someAsyncOperation();
  res.send(data);
}));
```

## 错误日志

### 1. 结构化日志
使用 winston 或 bunyan 进行结构化日志记录。

```javascript
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' })
  ]
});

// 在错误处理中间件中使用
const globalErrorHandler = (err, req, res, next) => {
  logger.error(err.message, err);
  // 其他错误处理逻辑
};
```

### 2. 错误监控
集成 Sentry 或类似服务进行错误监控。

```javascript
const Sentry = require('@sentry/node');
const Tracing = require('@sentry/tracing');

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  integrations: [
    new Tracing.Integrations.Express({ app })
  ],
  tracesSampleRate: 1.0
});

// 请求处理
app.use(Sentry.Handlers.requestHandler());
app.use(Sentry.Handlers.tracingHandler());

// 错误处理
app.use(Sentry.Handlers.errorHandler({
  shouldHandleError(error) {
    return error.statusCode >= 500;
  }
}));
```

## 常见错误类型处理

### 1. 404 错误
处理未找到的路由。

```javascript
app.all('*', (req, res, next) => {
  next(new AppError(`Can't find ${req.originalUrl} on this server!`, 404));
});
```

### 2. 数据库错误
处理数据库连接和查询错误。

```javascript
const db = require('./db');

db.on('error', (err) => {
  logger.error('Database connection error:', err);
  // 可能的恢复策略
});

app.get('/api/users', catchAsync(async (req, res, next) => {
  try {
    const users = await db.query('SELECT * FROM users');
    res.send(users);
  } catch (err) {
    if (err.code === 'ECONNREFUSED') {
      return next(new AppError('Database connection failed', 503));
    }
    next(err);
  }
}));
```

### 3. 验证错误
处理请求数据验证错误。

```javascript
const { body, validationResult } = require('express-validator');

app.post('/api/users', [
  body('name').notEmpty().withMessage('Name is required'),
  body('email').isEmail().withMessage('Invalid email address')
], (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    const errorMessages = errors.array().map(error => error.msg);
    return next(new AppError(errorMessages.join('. '), 400));
  }
  // 处理请求
});
```

## 生产环境错误处理

### 1. 避免泄露敏感信息
在生产环境中，不要向客户端返回详细的错误信息。

```javascript
if (process.env.NODE_ENV === 'production') {
  // 不返回错误堆栈
  res.status(error.statusCode).json({
    status: error.status,
    message: error.message || 'Internal Server Error'
  });
}
```

### 2. 优雅关闭
实现优雅关闭，确保在应用程序关闭时处理完所有请求。

```javascript
const server = app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

process.on('unhandledRejection', (err) => {
  console.error('Unhandled Rejection:', err);
  server.close(() => {
    process.exit(1);
  });
});

process.on('SIGTERM', () => {
  console.log('SIGTERM received. Shutting down gracefully.');
  server.close(() => {
    console.log('Server exited.');
  });
});
```

## 总结

Express.js 错误处理的最佳实践包括：

1. **基础错误处理**：使用内置错误处理中间件，正确放置中间件
2. **高级错误处理**：自定义错误类，全局错误处理中间件
3. **异步错误处理**：try-catch，错误处理包装器
4. **错误日志**：结构化日志，错误监控
5. **常见错误类型**：404 错误，数据库错误，验证错误
6. **生产环境处理**：避免泄露敏感信息，优雅关闭

通过实施这些最佳实践，可以构建更健壮、更可靠的 Express.js 应用程序。""",
        category=KnowledgeCategory.FRAMEWORK,
        tags=["express", "node.js", "error-handling", "best-practice"],
        severity="low",
        cwe_ids=[],
        owasp_ids=[]
    )
]
