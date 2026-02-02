# 常见问题解答 (FAQ)

本文档收集了使用 AI 代码审查系统时可能遇到的常见问题及解决方案。

## 目录

- [部署相关问题](#部署相关问题)
- [配置相关问题](#配置相关问题)
- [Webhook 配置问题](#webhook-配置问题)
- [消息推送问题](#消息推送问题)
- [代码审查问题](#代码审查问题)
- [大模型相关问题](#大模型相关问题)
- [队列相关问题](#队列相关问题)
- [其他问题](#其他问题)

---

## 部署相关问题

### 问题 1: Docker 容器部署时，更新 .env 文件后配置不生效

**问题描述**

修改了 `.env` 配置文件后，容器内的配置没有更新。

**原因分析**

Docker 的文件映射机制是将宿主机的文件挂载到容器内，但环境变量的加载发生在容器启动时。如果容器已经运行，修改 `.env` 文件不会自动重新加载环境变量。

**解决方案**

1. **方法一：重启容器（推荐）**
   ```bash
   # 停止并删除现有容器
   docker-compose down
   
   # 重新创建并启动容器
   docker-compose up -d
   ```

2. **方法二：仅重启服务**
   ```bash
   # 重启特定服务
   docker-compose restart app
   ```

3. **方法三：使用 docker-compose 重新创建**
   ```bash
   # 强制重新创建容器
   docker-compose up -d --force-recreate
   ```

**注意事项**

- 确保 `.env` 文件路径正确（默认位置：`config/.env`）
- 检查文件权限，确保容器可以读取
- 修改配置后建议查看容器日志确认配置已生效

---

### 问题 2: 端口被占用导致服务启动失败

**问题描述**

启动服务时提示端口 5001 或 5002 已被占用。

**解决方案**

1. **检查端口占用情况**
   ```bash
   # Linux/Mac
   lsof -i :5001
   lsof -i :5002
   
   # 或使用 netstat
   netstat -tuln | grep 5001
   ```

2. **修改端口配置**
   
   在 `docker-compose.yml` 中修改端口映射：
   ```yaml
   ports:
     - "5003:5001"  # 将宿主机端口改为 5003
     - "5004:5002"   # 将宿主机端口改为 5004
   ```
   
   或在 `.env` 文件中配置：
   ```bash
   SERVER_PORT=5003
   ```

3. **停止占用端口的进程**
   ```bash
   # 找到占用端口的进程 ID (PID)
   # 然后终止进程
   kill -9 <PID>
   ```

---

### 问题 3: 数据库初始化失败

**问题描述**

服务启动时提示数据库相关错误，或 Dashboard 无法显示历史记录。

**解决方案**

1. **检查数据目录权限**
   ```bash
   # 确保 data 目录存在且可写
   mkdir -p data
   chmod 755 data
   ```

2. **检查数据库文件**
   ```bash
   # 查看数据库文件是否存在
   ls -la data/data.db
   
   # 如果文件损坏，可以删除后重新创建（会丢失历史数据）
   rm data/data.db
   ```

3. **查看日志排查问题**
   ```bash
   # 查看应用日志
   tail -f logs/app.log
   ```

---

## 配置相关问题

### 问题 4: 环境变量配置检查失败

**问题描述**

启动服务时提示缺少必要的环境变量或配置错误。

**解决方案**

1. **检查必需的环境变量**
   
   系统启动时会自动检查以下必需配置：
   - `LLM_PROVIDER`: 大模型供应商（openai/deepseek/qwen）
   - 对应供应商的 API 密钥和模型名称

2. **验证配置文件位置**
   
   确保 `.env` 文件位于正确路径：
   - Docker 部署：`config/.env`
   - 本地部署：`config/.env` 或项目根目录

3. **检查环境变量格式**
   ```bash
   # 正确的格式（无引号，无空格）
   LLM_PROVIDER=deepseek
   DEEPSEEK_API_KEY=sk-xxxxx
   
   # 错误的格式
   LLM_PROVIDER="deepseek"  # 不要加引号
   DEEPSEEK_API_KEY = sk-xxxxx  # 等号前后不要有空格
   ```

4. **使用配置检查工具**
   
   系统启动时会自动执行配置检查，查看日志输出：
   ```bash
   docker-compose logs app | grep -i "配置"
   ```

---

### 问题 5: 配置文件路径错误

**问题描述**

服务无法找到配置文件或提示配置文件不存在。

**解决方案**

1. **确认配置文件路径**
   
   - 默认路径：`config/.env`
   - 确保文件存在：`ls -la config/.env`

2. **检查 Docker 挂载配置**
   
   在 `docker-compose.yml` 中确认挂载配置：
   ```yaml
   volumes:
     - ./config/.env:/app/config/.env
   ```

3. **使用绝对路径（可选）**
   
   在代码中修改配置文件路径，或使用环境变量指定：
   ```bash
   ENV_FILE_PATH=/path/to/.env
   ```

---

## Webhook 配置问题

### 问题 6: GitLab 配置 Webhook 时提示 "Invalid url given"

**问题描述**

在 GitLab 中配置 Webhook 时，系统提示 URL 无效。

**原因分析**

GitLab 默认禁止 Webhooks 访问本地网络地址（如 127.0.0.1、localhost、内网 IP 等），这是出于安全考虑。

**解决方案**

1. **启用本地网络访问（推荐用于内网环境）**
   
   - 进入 GitLab 管理区域：**Admin Area → Settings → Network**
   - 在 **Outbound requests** 部分，勾选 **Allow requests to the local network from webhooks and integrations**
   - 点击 **Save changes** 保存

2. **使用公网地址（推荐用于生产环境）**
   
   - 将服务部署在公网可访问的服务器上
   - 使用域名或公网 IP 配置 Webhook URL
   - 确保防火墙规则允许访问

3. **使用内网穿透工具（开发测试环境）**
   
   - 使用 ngrok、frp 等工具将本地服务暴露到公网
   - 使用生成的公网地址配置 Webhook

---

### 问题 7: Webhook 请求未触发代码审查

**问题描述**

配置了 Webhook 后，提交代码或创建 Merge Request 时没有触发代码审查。

**排查步骤**

1. **检查 Webhook 配置**
   - 确认 Webhook URL 正确：`http://your-server-ip:5001/review/webhook`
   - 确认触发事件已勾选：**Push Events** 和 **Merge Request Events**
   - 确认 Webhook 状态为 "Enabled"

2. **检查服务是否运行**
   ```bash
   # 检查容器状态
   docker-compose ps
   
   # 检查服务日志
   docker-compose logs app | tail -50
   ```

3. **检查网络连通性**
   ```bash
   # 从 GitLab 服务器测试连接
   curl http://your-server-ip:5001/
   ```

4. **查看 Webhook 日志**
   - 在 GitLab 项目设置中查看 Webhook 的 Recent events
   - 检查请求状态码和响应内容
   - 查看系统日志：`tail -f logs/app.log`

5. **验证 Access Token**
   - 确认 `GITLAB_ACCESS_TOKEN` 配置正确
   - 确认 Token 具有足够的权限（api、read_repository 等）

---

### 问题 8: GitHub Webhook 配置问题

**问题描述**

GitHub Webhook 配置后无法正常工作。

**解决方案**

1. **检查 Webhook URL 格式**
   ```
   http://your-server-ip:5001/review/webhook
   ```

2. **确认事件类型**
   - 必须勾选 **Push** 和 **Pull request** 事件
   - Content type 选择 **application/json**

3. **配置 Access Token**
   
   在 `.env` 文件中配置：
   ```bash
   GITHUB_ACCESS_TOKEN=your_github_token_here
   GITHUB_URL=https://api.github.com  # 可选，默认为 GitHub 官方 API
   ```

4. **验证 Token 权限**
   
   Token 需要以下权限：
   - `repo` (完整仓库访问权限)
   - 或至少包含：`Contents`、`Pull requests`、`Commit statuses`、`Issues`、`Metadata`

5. **检查 Secret Token（可选）**
   
   如果配置了 Webhook Secret，需要在代码中实现签名验证。

---

### 问题 9: Gitea Webhook 配置问题

**问题描述**

Gitea Webhook 配置后无法正常工作。

**解决方案**

1. **配置 Access Token**
   ```bash
   GITEA_ACCESS_TOKEN=your_gitea_token_here
   GITEA_URL=https://your-gitea-instance.com
   ```

2. **配置 Issue 模式（可选）**
   
   Gitea 支持将审查结果写入 Issue 而不是直接评论：
   ```bash
   # 启用 Issue 模式
   GITEA_USE_ISSUE_MODE=1
   
   # 配置 Issue 标签（可选）
   GITEA_REVIEW_ISSUE_LABELS=ai-review,code-review
   ```
   
   **注意**：标签需要先在 Gitea 仓库中创建。

3. **检查 Webhook 事件**
   - 确保勾选了 **Push** 和 **Pull Request** 事件
   - Gitea 会发送 `issue_comment` 事件（系统自动生成的评论），这些事件会被自动忽略

---

## 消息推送问题

### 问题 10: 钉钉消息推送失败

**问题描述**

代码审查完成后，钉钉群没有收到消息通知。

**排查步骤**

1. **检查钉钉配置**
   ```bash
   # 确认已启用钉钉推送
   DINGTALK_ENABLED=1
   
   # 确认 Webhook URL 正确
   DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=xxx
   ```

2. **验证 Webhook URL**
   ```bash
   # 测试 Webhook 是否可用
   curl -X POST "https://oapi.dingtalk.com/robot/send?access_token=xxx" \
        -H "Content-Type: application/json" \
        -d '{"msgtype":"text","text":{"content":"测试消息"}}'
   ```

3. **检查机器人状态**
   - 确认钉钉机器人未被禁用
   - 确认机器人仍在群内
   - 检查机器人安全设置（IP 白名单、关键词等）

4. **查看日志**
   ```bash
   # 查看推送相关日志
   grep -i "dingtalk" logs/app.log
   ```

---

### 问题 11: 如何为不同项目配置不同的消息推送群

**问题描述**

希望不同 GitLab 项目的代码审查结果发送到不同的钉钉/企业微信/飞书群。

**解决方案**

**方法一：按项目名称匹配（推荐）**

在 `.env` 文件中配置项目特定的 Webhook URL，格式为：`{PLATFORM}_WEBHOOK_URL_{PROJECT_NAME}`

以钉钉为例：
```bash
DINGTALK_ENABLED=1

# 项目 A 的 Webhook（项目名称为 project-a）
DINGTALK_WEBHOOK_URL_PROJECT_A=https://oapi.dingtalk.com/robot/send?access_token=token_a

# 项目 B 的 Webhook（项目名称为 project-b）
DINGTALK_WEBHOOK_URL_PROJECT_B=https://oapi.dingtalk.com/robot/send?access_token=token_b

# 默认 Webhook（其他项目或日报使用）
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=default_token
```

**方法二：按 GitLab 服务器地址匹配**

如果使用多个 GitLab 服务器，可以按服务器地址配置：

```bash
DINGTALK_ENABLED=1

# GitLab 服务器 A (http://192.168.30.164)
DINGTALK_WEBHOOK_192_168_30_164=https://oapi.dingtalk.com/robot/send?access_token=token_a

# GitLab 服务器 B (http://example.gitlab.com)
DINGTALK_WEBHOOK_example_gitlab_com=https://oapi.dingtalk.com/robot/send?access_token=token_b

# 默认 Webhook
DINGTALK_WEBHOOK_URL=https://oapi.dingtalk.com/robot/send?access_token=default_token
```

**匹配优先级**

1. 优先匹配项目名称（`{PLATFORM}_WEBHOOK_URL_{PROJECT_NAME}`）
2. 其次匹配 GitLab 服务器地址（`{PLATFORM}_WEBHOOK_{URL_SLUG}`）
3. 最后使用默认 Webhook URL（`{PLATFORM}_WEBHOOK_URL`）

**注意事项**

- 项目名称和 URL 中的特殊字符会被转换为下划线
- 企业微信和飞书的配置方式相同，只需将 `DINGTALK` 替换为 `WECOM` 或 `FEISHU`

---

### 问题 12: 企业微信和飞书消息推送配置

**问题描述**

如何配置企业微信和飞书的消息推送。

**解决方案**

**1. 配置企业微信推送**

1. 在企业微信群中添加自定义机器人，获取 Webhook URL
2. 在 `.env` 文件中配置：
   ```bash
   # 企业微信配置
   WECOM_ENABLED=1  # 0=禁用，1=启用
   WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx
   ```

**2. 配置飞书推送**

1. 在飞书群中添加自定义机器人，获取 Webhook URL
2. 在 `.env` 文件中配置：
   ```bash
   # 飞书配置
   FEISHU_ENABLED=1  # 0=禁用，1=启用
   FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx
   ```

**3. 多项目配置**

企业微信和飞书同样支持按项目名称或服务器地址配置不同的 Webhook，配置方式与钉钉相同。

---

## 代码审查问题

### 问题 13: 代码审查结果为空或不完整

**问题描述**

代码审查后返回的结果为空，或审查内容不完整。

**可能原因及解决方案**

1. **Token 限制导致内容被截断**
   
   检查 `REVIEW_MAX_TOKENS` 配置：
   ```bash
   # 增加 Token 限制（默认 10000）
   REVIEW_MAX_TOKENS=15000
   ```
   
   **注意**：过大的值可能导致 API 调用失败或超时。

2. **代码变更过大**
   
   如果代码变更超过 Token 限制，系统会自动截断。建议：
   - 将大的变更拆分为多个小的 Merge Request
   - 增加 `REVIEW_MAX_TOKENS` 值（需考虑 API 限制）

3. **大模型 API 返回错误**
   
   查看日志确认 API 调用是否成功：
   ```bash
   grep -i "api error" logs/app.log
   ```

4. **文件类型过滤**
   
   确认文件扩展名在支持列表中：
   ```bash
   SUPPORTED_EXTENSIONS=.java,.py,.php,.yml,.vue,.go,.c,.cpp,.h,.js,.css,.md,.sql,.ts,.jsx,.tsx
   ```

---

### 问题 14: 某些文件类型未被审查

**问题描述**

提交的代码文件没有被审查。

**解决方案**

1. **检查文件扩展名配置**
   
   在 `.env` 文件中确认 `SUPPORTED_EXTENSIONS` 包含需要的文件类型：
   ```bash
   SUPPORTED_EXTENSIONS=.java,.py,.php,.yml,.vue,.go,.c,.cpp,.h,.js,.css,.md,.sql,.ts,.jsx,.tsx
   ```
   
   **注意**：扩展名必须以点（.）开头，多个扩展名用逗号分隔。

2. **检查文件是否被删除**
   
   系统默认不审查已删除的文件。如果需要审查删除的文件，需要修改代码逻辑。

3. **查看日志确认过滤原因**
   ```bash
   grep -i "filter" logs/app.log
   ```

---

### 问题 15: 代码审查语言检测不准确

**问题描述**

系统没有使用正确的语言特定审查提示词，导致审查质量不佳。

**解决方案**

1. **确认语言检测功能已启用**
   ```bash
   ENABLE_LANGUAGE_DETECTION=1
   ```

2. **检查支持的语言**
   
   系统支持自动检测以下语言：
   - Python (.py)
   - JavaScript/TypeScript (.js, .ts, .jsx, .tsx)
   - Java (.java)
   - Go (.go)
   - PHP (.php)
   - C/C++ (.c, .cpp, .h, .hpp)
   - Vue (.vue)
   - 其他语言使用通用审查提示词

3. **查看语言检测日志**
   ```bash
   grep -i "检测到" logs/app.log
   ```

4. **手动指定语言（高级）**
   
   如果需要，可以修改代码强制使用特定语言的审查提示词。

---

### 问题 16: Push 事件未触发代码审查

**问题描述**

Push 代码后没有进行代码审查。

**解决方案**

1. **检查 Push Review 功能是否启用**
   ```bash
   # 启用 Push 事件审查
   PUSH_REVIEW_ENABLED=1  # 0=禁用，1=启用
   ```

2. **检查分支保护设置**
   
   如果启用了 `MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED`，只有受保护分支的 Push 才会触发审查：
   ```bash
   MERGE_REVIEW_ONLY_PROTECTED_BRANCHES_ENABLED=0  # 0=所有分支，1=仅受保护分支
   ```

3. **确认 Webhook 事件配置**
   
   在 GitLab/GitHub/Gitea 中确认已勾选 **Push Events**。

---

## 大模型相关问题

### 问题 17: 大模型 API 调用失败

**问题描述**

代码审查时提示 API 调用失败或认证错误。

**排查步骤**

1. **检查 API 密钥配置**
   ```bash
   # DeepSeek
   DEEPSEEK_API_KEY=sk-xxxxx
   
   # OpenAI
   OPENAI_API_KEY=sk-xxxxx
   
   # 通义千问
   QWEN_API_KEY=sk-xxxxx
   ```

2. **验证 API 密钥有效性**
   ```bash
   # 测试 DeepSeek API（示例）
   curl https://api.deepseek.com/v1/models \
        -H "Authorization: Bearer sk-xxxxx"
   ```

3. **检查 API 地址配置**
   ```bash
   # 确认 API 地址正确
   DEEPSEEK_API_BASE_URL=https://api.deepseek.com
   OPENAI_API_BASE_URL=https://api.openai.com
   QWEN_API_BASE_URL=https://dashscope.aliyuncs.com
   ```

4. **检查模型名称**
   ```bash
   # 确认模型名称正确
   DEEPSEEK_API_MODEL=deepseek-chat
   OPENAI_API_MODEL=gpt-4
   QWEN_API_MODEL=qwen-turbo
   ```

5. **查看详细错误日志**
   ```bash
   grep -i "api error" logs/app.log
   ```

**常见错误码**

- **401**: API 密钥无效或过期
- **404**: API 地址错误或模型不存在
- **429**: 请求频率过高，需要限流
- **500**: 服务器内部错误，稍后重试

---

### 问题 18: 如何切换大模型供应商

**问题描述**

需要从当前使用的大模型切换到另一个（如从 DeepSeek 切换到 OpenAI）。

**解决方案**

1. **修改 LLM_PROVIDER 配置**
   ```bash
   # 在 .env 文件中修改
   LLM_PROVIDER=deepseek  # 可选: openai, deepseek, qwen
   ```

2. **配置对应供应商的 API 信息**
   
   **切换到 OpenAI：**
   ```bash
   LLM_PROVIDER=openai
   OPENAI_API_KEY=sk-xxxxx
   OPENAI_API_BASE_URL=https://api.openai.com
   OPENAI_API_MODEL=gpt-4
   ```
   
   **切换到 DeepSeek：**
   ```bash
   LLM_PROVIDER=deepseek
   DEEPSEEK_API_KEY=sk-xxxxx
   DEEPSEEK_API_BASE_URL=https://api.deepseek.com
   DEEPSEEK_API_MODEL=deepseek-chat
   ```
   
   **切换到通义千问：**
   ```bash
   LLM_PROVIDER=qwen
   QWEN_API_KEY=sk-xxxxx
   QWEN_API_BASE_URL=https://dashscope.aliyuncs.com
   QWEN_API_MODEL=qwen-turbo
   ```

3. **重启服务使配置生效**
   ```bash
   docker-compose restart app
   ```

4. **验证配置**
   
   查看启动日志，确认配置检查通过：
   ```bash
   docker-compose logs app | grep -i "LLM"
   ```

---

### 问题 19: API 调用超时或响应慢

**问题描述**

代码审查响应时间过长，或出现超时错误。

**解决方案**

1. **增加请求超时时间**
   ```bash
   REQUEST_TIMEOUT=60  # 默认 30 秒，可根据需要调整
   ```

2. **检查网络连接**
   ```bash
   # 测试 API 服务器连通性
   ping api.deepseek.com
   curl -I https://api.deepseek.com
   ```

3. **减少审查代码量**
   - 将大的变更拆分为多个小的 Merge Request
   - 调整 `REVIEW_MAX_TOKENS` 限制

4. **使用异步队列处理**
   
   启用 Redis Queue 进行异步处理，避免阻塞 Webhook 响应：
   ```bash
   QUEUE_DRIVER=rq
   ```

5. **检查 API 服务状态**
   
   某些 API 服务可能在高峰期响应较慢，可以：
   - 使用更高性能的模型
   - 在非高峰期进行审查
   - 联系 API 服务商了解服务状态

---

### 问题 20: 如何配置审查风格

**问题描述**

希望修改代码审查的语调风格（如专业型、毒舌型、绅士型、幽默型）。

**解决方案**

在 `.env` 文件中配置 `REVIEW_STYLE`：

```bash
# 可选值: professional, sarcastic, gentle, humorous
REVIEW_STYLE=professional
```

**风格说明**

| 风格值 | 描述 | 适用场景 |
|--------|------|----------|
| `professional` | 专业严谨风格 | 正式项目、企业环境 |
| `sarcastic` | 毒舌吐槽风格 | 内部项目、轻松氛围 |
| `gentle` | 温和建议风格 | 新手友好、学习项目 |
| `humorous` | 幽默风趣风格 | 活跃团队、趣味项目 |

**修改后重启服务**
```bash
docker-compose restart app
```

---

## 队列相关问题

### 问题 21: 如何配置和使用 Redis Queue

**问题描述**

希望使用 Redis Queue 进行异步任务处理，提高系统性能。

**解决方案**

**1. 启动 Redis Queue 服务**

开发调试模式：
```bash
docker compose -f docker-compose.rq.yml up -d
```

生产模式（如果存在）：
```bash
docker compose -f docker-compose.prod.yml up -d
```

**2. 配置队列驱动**

在 `.env` 文件中配置：
```bash
# 使用 Redis Queue
QUEUE_DRIVER=rq

# Redis 连接配置
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

**3. 配置队列名称**

为不同的 GitLab 服务器配置不同的队列（可选）：
```bash
# 将 GitLab 域名中的点替换为下划线
# 例如: gitlab.test.cn -> gitlab_test_cn
WORKER_QUEUE=gitlab_test_cn
```

**4. 验证队列工作状态**

查看队列日志：
```bash
docker-compose logs worker
```

**优势**

- 异步处理，不阻塞 Webhook 响应
- 支持任务重试
- 更好的错误处理和日志记录
- 支持多 Worker 并发处理

---

### 问题 22: Redis 连接失败

**问题描述**

使用 Redis Queue 时提示无法连接 Redis。

**解决方案**

1. **检查 Redis 服务状态**
   ```bash
   # 检查 Redis 容器是否运行
   docker-compose ps redis
   
   # 测试 Redis 连接
   redis-cli -h 127.0.0.1 -p 6379 ping
   ```

2. **检查 Redis 配置**
   ```bash
   REDIS_HOST=127.0.0.1  # 或 Redis 容器的服务名
   REDIS_PORT=6379
   ```

3. **检查网络连接**
   
   如果 Redis 在 Docker 网络中，使用服务名而非 localhost：
   ```bash
   REDIS_HOST=redis  # Docker Compose 服务名
   ```

4. **查看 Redis 日志**
   ```bash
   docker-compose logs redis
   ```

---

## 其他问题

### 问题 23: 如何查看系统日志

**问题描述**

需要查看系统运行日志以排查问题。

**解决方案**

1. **查看应用日志**
   ```bash
   # 实时查看日志
   tail -f logs/app.log
   
   # 查看最近 100 行
   tail -n 100 logs/app.log
   
   # Docker 环境
   docker-compose logs -f app
   ```

2. **查看特定内容**
   ```bash
   # 查看错误日志
   grep -i "error" logs/app.log
   
   # 查看 Webhook 相关日志
   grep -i "webhook" logs/app.log
   
   # 查看 API 调用日志
   grep -i "api" logs/app.log
   ```

3. **配置日志级别**
   ```bash
   # 在 .env 文件中配置
   LOG_LEVEL=DEBUG  # 可选: DEBUG, INFO, WARNING, ERROR
   ```

---

### 问题 24: 如何配置定时日报任务

**问题描述**

希望配置自动生成和发送代码提交日报。

**解决方案**

1. **配置 Cron 表达式**

   在 `.env` 文件中配置：
   ```bash
   # Cron 表达式格式: 分 时 日 月 星期
   # 示例: 每天 18:00 (工作日)
   REPORT_CRONTAB_EXPRESSION=0 18 * * 1-5
   
   # 示例: 每天 20:00
   REPORT_CRONTAB_EXPRESSION=0 20 * * *
   ```

2. **Cron 表达式说明**

   ```
   分 时 日 月 星期
   *  *  *  *  *
   │  │  │  │  │
   │  │  │  │  └── 星期 (0-7, 0和7都表示周日)
   │  │  │  └───── 月 (1-12)
   │  │  └─────── 日 (1-31)
   │  └────────── 时 (0-23)
   └──────────── 分 (0-59)
   ```

3. **验证定时任务**

   查看日志确认定时任务已启动：
   ```bash
   grep -i "scheduler" logs/app.log
   ```

4. **手动触发日报**

   也可以通过 API 手动触发：
   ```bash
   curl http://localhost:5001/review/daily_report
   ```

---

### 问题 25: Dashboard 无法访问或显示异常

**问题描述**

无法访问 Dashboard 页面，或页面显示异常。

**解决方案**

1. **检查服务状态**
   ```bash
   # 确认服务运行
   docker-compose ps
   
   # 检查端口
   netstat -tuln | grep 5002
   ```

2. **检查数据库**

   Dashboard 依赖数据库存储审查历史：
   ```bash
   # 确认数据库文件存在
   ls -la data/data.db
   ```

3. **查看 Dashboard 日志**
   ```bash
   docker-compose logs app | grep -i "dashboard"
   ```

4. **访问 Dashboard**

   浏览器访问：`http://your-server-ip:5002`

5. **检查防火墙规则**

   确保端口 5002 未被防火墙阻止。

---

### 问题 26: 如何对整个代码库进行审查

**问题描述**

希望对整个代码库进行一次性审查，而不仅仅是增量变更。

**解决方案**

使用命令行工具进行全量审查：

```bash
python -m src.cmd.review
```

运行后按照命令行提示操作：

1. 选择审查类型（代码、目录结构、数据库、分支等）
2. 输入代码库路径
3. 等待审查完成

**注意事项**

- 全量审查可能消耗大量 API 调用
- 建议先在小范围测试
- 大代码库可能需要较长时间

---

### 问题 27: 系统性能优化建议

**问题描述**

系统响应慢，希望优化性能。

**优化建议**

1. **使用 Redis Queue**
   ```bash
   QUEUE_DRIVER=rq
   ```

2. **调整并发数**
   ```bash
   MAX_CONCURRENT_REVIEWS=5  # 根据服务器性能调整
   ```

3. **优化 Token 限制**
   ```bash
   # 平衡审查详细程度和性能
   REVIEW_MAX_TOKENS=10000  # 不要设置过大
   ```

4. **使用更快的模型**
   - 选择响应速度更快的模型
   - 考虑使用本地部署的模型

5. **数据库优化**
   - 定期清理历史数据
   - 考虑使用更快的数据库（如 PostgreSQL）

6. **网络优化**
   - 使用离 API 服务器更近的部署位置
   - 配置 CDN（如果适用）

---

### 问题 28: 如何备份和恢复数据

**问题描述**

需要备份审查历史数据，或在迁移后恢复数据。

**解决方案**

1. **备份数据库**
   ```bash
   # 备份 SQLite 数据库
   cp data/data.db data/data.db.backup
   
   # 或使用 SQLite 工具
   sqlite3 data/data.db ".backup data/data.db.backup"
   ```

2. **备份配置文件**
   ```bash
   # 备份 .env 文件
   cp config/.env config/.env.backup
   ```

3. **恢复数据**
   ```bash
   # 恢复数据库
   cp data/data.db.backup data/data.db
   
   # 恢复配置
   cp config/.env.backup config/.env
   ```

4. **定期备份（建议）**

   可以设置定时任务自动备份：
   ```bash
   # 每天备份一次
   0 2 * * * cp /path/to/data/data.db /path/to/backup/data.db.$(date +\%Y\%m\%d)
   ```

---

## 获取帮助

如果以上问题无法解决您的问题，可以通过以下方式获取帮助：

1. **查看项目文档**
   - README.md: 项目基本说明
   - PROCESS.md: 系统流程说明

2. **查看日志文件**
   - `logs/app.log`: 应用运行日志

3. **提交 Issue**
   - GitHub: [项目 Issues 页面]
   - Gitee: [项目 Issues 页面]

4. **检查配置**
   - 运行配置检查：查看启动日志中的配置检查结果

---
