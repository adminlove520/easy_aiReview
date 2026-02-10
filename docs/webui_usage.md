# WebUI 使用指南

本文档详细说明如何启动后端和前端服务，以及如何使用 Easy-AI-CodeReview 的 WebUI 界面。

## 目录结构

```
Easy-AI-CodeReview/
├── src/                 # 后端源代码
│   ├── deepaudit_backend/ # 统一后端服务（集成了所有功能）
│   └── ...
├── web/                # 前端代码
│   └── deepaudit/      # 前端应用
└── README.md           # 项目说明
```

## 1. 启动后端服务

### 1.1 环境准备

1. **安装 Python 依赖**
   ```bash
   # 在项目根目录执行
   pip install -r requirements.txt
   
   # 安装 DeepAudit 后端依赖
   cd src/deepaudit_backend
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   # 复制配置文件模板
   cd src/deepaudit_backend
   cp env.example .env
   
   # 编辑配置文件，设置必要的参数
   # 至少需要配置大模型 API 密钥
   ```

### 1.2 启动统一后端服务

现在我们使用统一的后端服务，集成了所有功能，包括 API 服务和 DeepAudit 功能。

```bash
# 在 src/deepaudit_backend 目录执行
python -m app.main
```

**默认配置**：
- 端口：8000
- 访问地址：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 健康检查：http://localhost:8000/health

## 2. 启动前端服务

### 2.1 环境准备

1. **安装 Node.js 依赖**
   ```bash
   # 在前端目录执行
   cd web/deepaudit
   npm install
   ```

### 2.2 启动前端开发服务器

```bash
# 在 web/deepaudit 目录执行
npm run dev
```

**默认配置**：
- 端口：5173
- 访问地址：http://localhost:5173/deepaudit/

### 2.3 构建生产版本

如果需要部署到生产环境，可以构建前端代码：

```bash
# 在 web/deepaudit 目录执行
npm run build

# 构建完成后，静态文件会生成在 dist 目录
```

## 3. 使用 WebUI

### 3.1 访问 WebUI

启动服务后，通过以下地址访问 WebUI：

- **前端开发服务器**：http://localhost:5173/deepaudit/
- **生产环境**：根据部署配置的地址访问

### 3.2 登录系统

1. **默认测试账号**：
   - 邮箱：demo@example.com
   - 密码：demo123

2. **登录流程**：
   - 打开登录页面
   - 输入邮箱和密码
   - 点击「登录」按钮
   - 登录成功后会自动跳转到 Dashboard 页面

### 3.3 主要功能模块

#### 3.3.1 Dashboard（仪表盘）
- 显示项目整体统计数据
- 展示成员贡献分析
- 提供代码审查历史记录

#### 3.3.2 Instant Analysis（即时分析）
- 上传代码文件进行即时审查
- 选择不同的审查模板
- 查看审查结果和建议

#### 3.3.3 Audit Tasks（审查任务）
- 管理代码审查任务
- 查看任务状态和进度
- 处理待审查的代码变更

#### 3.3.4 Audit Rules（审查规则）
- 配置代码审查规则
- 管理规则集
- 自定义审查标准

#### 3.3.5 Prompt Manager（提示词管理）
- 管理代码审查提示词模板
- 创建和编辑提示词
- 测试提示词效果

### 3.4 系统设置

- **个人设置**：修改个人信息和密码
- **系统配置**：配置大模型参数和审查选项
- **SSH 密钥管理**：配置和测试 SSH 密钥，用于访问私有 Git 仓库

## 4. 常见问题排查

### 4.1 登录失败

**可能原因**：
- 后端服务未启动
- 前端代理配置错误
- 账号密码错误

**解决方案**：
1. 检查后端服务是否正常运行
2. 确认前端代理配置指向正确的后端端口
3. 使用正确的测试账号登录

### 4.2 前端页面加载失败

**可能原因**：
- 前端开发服务器未启动
- 网络连接问题
- 浏览器缓存问题

**解决方案**：
1. 检查前端开发服务器状态
2. 清除浏览器缓存
3. 检查网络连接

### 4.3 API 调用失败

**可能原因**：
- 后端服务未启动
- 环境变量配置错误
- 大模型 API 密钥无效

**解决方案**：
1. 检查后端服务状态
2. 验证环境变量配置
3. 确认大模型 API 密钥有效

### 4.4 代码审查无结果

**可能原因**：
- 大模型 API 调用失败
- 代码文件类型不支持
- 代码文件过大

**解决方案**：
1. 检查大模型 API 配置
2. 确认代码文件类型在支持列表中
3. 尝试审查较小的代码文件

## 5. 开发模式

### 5.1 前端开发

```bash
# 启动前端开发服务器（支持热更新）
npm run dev

# 运行类型检查
npm run type-check

# 运行代码 lint
npm run lint
```

### 5.2 后端开发

```bash
# 启动后端服务（开发模式）
cd src/deepaudit_backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 6. 部署建议

### 6.1 开发环境
- 启动顺序：后端服务 → 前端开发服务器
- 访问地址：http://localhost:5173/deepaudit/

### 6.2 生产环境
- 使用 Docker 容器化部署
- 配置反向代理（如 Nginx）
- 启用 HTTPS
- 配置适当的安全措施

## 7. 技术栈

### 7.1 后端
- **Python 3.10+**：核心编程语言
- **FastAPI**：后端框架
- **SQLAlchemy**：ORM 数据库操作
- **Pydantic**：数据验证
- **JWT**：用户认证

### 7.2 前端
- **React 18+**：前端框架
- **TypeScript**：类型安全
- **TailwindCSS**：样式框架
- **Radix UI**：组件库
- **Vite**：构建工具

## 8. 联系我们

如果您在使用过程中遇到任何问题，请通过以下方式联系我们：

- **GitHub Issues**：https://github.com/adminlove520/easy_aiReview/issues
- **邮箱**：admin@example.com

---

**版本**：v3.1.0
**最后更新**：2026-02-10
