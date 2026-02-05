# LLM API 使用说明

本文档介绍如何在项目中使用 LLM（大语言模型）API，包括支持的模型、配置方法和使用示例。

## 支持的模型

目前项目支持以下大语言模型：

- **OpenAI**：GPT-4o-mini 等
- **DeepSeek**：deepseek-chat 等
- **Qwen**：qwen-coder-plus 等
- **ZhipuAI**：glm-4.7 等

## 配置方法

### 1. 环境变量配置

在 `.env` 文件中配置相应的环境变量：

#### OpenAI 配置

```bash
# 大模型供应商配置
LLM_PROVIDER=openai

# OpenAI 设置
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-4o-mini
```

#### DeepSeek 配置

```bash
# 大模型供应商配置
LLM_PROVIDER=deepseek

# DeepSeek 设置
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_API_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_MODEL=deepseek-chat
```

#### Qwen 配置

```bash
# 大模型供应商配置
LLM_PROVIDER=qwen

# Qwen 设置
QWEN_API_KEY=your_api_key
QWEN_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_API_MODEL=qwen-coder-plus
```

#### ZhipuAI 配置

```bash
# 大模型供应商配置
LLM_PROVIDER=zhipu

# ZhipuAI 设置
ZHIPUAI_API_KEY=your_api_key
ZHIPUAI_API_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
ZHIPUAI_API_MODEL=glm-4.7
```

## 使用示例

### 1. 通过工厂方法获取客户端

```python
from src.llm.factory import Factory

# 获取默认客户端（根据 LLM_PROVIDER 环境变量）
client = Factory.getClient()

# 或者指定模型供应商
client = Factory.getClient('openai')  # 使用 OpenAI
client = Factory.getClient('deepseek')  # 使用 DeepSeek
client = Factory.getClient('qwen')  # 使用 Qwen
client = Factory.getClient('zhipu')  # 使用 ZhipuAI
```

### 2. 调用 completions 方法

```python
messages = [
    {"role": "system", "content": "你是一位资深的软件开发工程师，专注于代码的规范性、功能性、安全性和稳定性。"},
    {"role": "user", "content": "请审查以下代码并提供改进建议：\n\ndef calculate_sum(a, b):\n    return a + b"}
]

# 调用模型获取回复
response = client.completions(messages)
print(response)
```

## 客户端实现

### 1. 基础客户端

所有 LLM 客户端都继承自 `BaseClient` 类，该类定义了基本的接口：

```python
class BaseClient:
    def completions(self, messages, model=None):
        """
        调用模型获取回复
        :param messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
        :param model: 模型名称（可选，默认为配置的默认模型）
        :return: 模型回复内容
        """
        raise NotImplementedError
```

### 2. 具体实现

- **OpenAIClient**：使用 OpenAI SDK 调用 OpenAI 模型
- **DeepSeekClient**：使用 OpenAI SDK 调用 DeepSeek 模型（API 兼容 OpenAI）
- **QwenClient**：使用 Qwen SDK 调用 Qwen 模型
- **ZhipuClient**：使用 OpenAI SDK 调用 ZhipuAI 模型（使用 OpenAI 兼容接口）

## 常见问题

### 1. 如何切换模型供应商？

修改 `.env` 文件中的 `LLM_PROVIDER` 环境变量，例如：

```bash
LLM_PROVIDER=deepseek  # 切换到 DeepSeek 模型
```

### 2. 如何修改模型参数？

在 `.env` 文件中修改相应模型的配置，例如：

```bash
OPENAI_API_MODEL=gpt-4  # 使用 GPT-4 模型
```

### 3. 如何处理 API 调用失败的情况？

在调用 `completions` 方法时，建议使用 try-except 捕获异常：

```python
try:
    response = client.completions(messages)
    print(response)
except Exception as e:
    print(f"API 调用失败：{str(e)}")
```



## 代码示例

### 完整使用示例

```python
from src.llm.factory import Factory

# 获取客户端
client = Factory.getClient()

# 构建消息
messages = [
    {"role": "system", "content": "你是一位资深的软件开发工程师，专注于代码的规范性、功能性、安全性和稳定性。"},
    {"role": "user", "content": "请审查以下 Python 代码并提供改进建议：\n\ndef calculate_sum(a, b):\n    return a + b"}
]

# 调用模型
print("正在调用模型...")
try:
    response = client.completions(messages)
    print("\n模型回复：")
    print(response)
except Exception as e:
    print(f"\nAPI 调用失败：{str(e)}")
```

## 注意事项

1. **API Key 安全**：不要将 API Key 提交到版本控制系统，应通过环境变量或配置文件管理。
2. **网络连接**：确保服务器能够访问模型 API 的网络地址。
3. **模型限制**：不同模型有不同的输入输出限制，请根据实际情况调整输入内容。
4. **错误处理**：在生产环境中，建议添加完善的错误处理机制。

---

通过以上配置和示例，您可以在项目中灵活使用各种大语言模型进行代码审查和其他任务。
