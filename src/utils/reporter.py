import json
import hashlib
import time
from src.llm.factory import Factory
from src.utils.log import logger
from src.utils.config import get


class Reporter:
    def __init__(self):
        self.default_client = Factory().getClient()
        self.llm_provider = get('LLM_PROVIDER', 'minimax')
        self.model_info = self._get_model_info()
        self.max_input_tokens = self.model_info.get('max_input_tokens', 2000)
        self.safety_margin = 0.8  # 安全系数
        self.available_tokens = int(self.max_input_tokens * self.safety_margin)
        self.cache = {}  # 简单内存缓存
        self.cache_ttl = 3600  # 缓存有效期（秒）
        self.report_client = self._get_report_client()

    def _get_model_info(self) -> dict:
        """获取模型信息，包括最大token限制"""
        model_info = {
            'minimax': {'max_input_tokens': 4096},
            'deepseek': {'max_input_tokens': 8192},
            'openai': {'max_input_tokens': 4096},
            'zhipuai': {'max_input_tokens': 4096},
            'qwen': {'max_input_tokens': 4096},
            'ollama': {'max_input_tokens': 8192}
        }
        return model_info.get(self.llm_provider, {'max_input_tokens': 4096})

    def _get_report_client(self):
        """获取用于生成日报的客户端，优先使用更大token限制的模型"""
        # 检查是否需要使用更大token限制的模型
        current_max_tokens = self.model_info.get('max_input_tokens', 4096)
        
        # 如果当前模型的token限制较小（<=4096），尝试使用更大token限制的模型
        if current_max_tokens <= 4096:
            # 检查是否配置了其他更大token限制的模型
            if get('DEEPSEEK_API_KEY'):
                logger.info("使用DeepSeek模型生成日报（更大的token限制）")
                # 临时修改环境变量来使用DeepSeek
                import os
                original_provider = os.environ.get('LLM_PROVIDER')
                os.environ['LLM_PROVIDER'] = 'deepseek'
                
                try:
                    # 创建DeepSeek客户端
                    deepseek_client = Factory().getClient()
                    # 恢复原始设置
                    if original_provider:
                        os.environ['LLM_PROVIDER'] = original_provider
                    else:
                        del os.environ['LLM_PROVIDER']
                    return deepseek_client
                except Exception as e:
                    logger.warning(f"创建DeepSeek客户端失败: {e}")
                    # 恢复原始设置
                    if original_provider:
                        os.environ['LLM_PROVIDER'] = original_provider
                    else:
                        del os.environ['LLM_PROVIDER']
            
            elif get('OLLAMA_API_BASE_URL'):
                logger.info("使用Ollama模型生成日报（更大的token限制）")
                # 临时修改环境变量来使用Ollama
                import os
                original_provider = os.environ.get('LLM_PROVIDER')
                os.environ['LLM_PROVIDER'] = 'ollama'
                
                try:
                    # 创建Ollama客户端
                    ollama_client = Factory().getClient()
                    # 恢复原始设置
                    if original_provider:
                        os.environ['LLM_PROVIDER'] = original_provider
                    else:
                        del os.environ['LLM_PROVIDER']
                    return ollama_client
                except Exception as e:
                    logger.warning(f"创建Ollama客户端失败: {e}")
                    # 恢复原始设置
                    if original_provider:
                        os.environ['LLM_PROVIDER'] = original_provider
                    else:
                        del os.environ['LLM_PROVIDER']
        
        # 如果没有更大token限制的模型可用，使用默认客户端
        logger.info(f"使用默认模型 {self.llm_provider} 生成日报")
        return self.default_client

    def generate_report(self, data: str) -> str:
        """生成日报报告

        Args:
            data: 提交记录数据（JSON字符串）

        Returns:
            str: 报告内容
        """
        try:
            # 生成缓存键
            cache_key = hashlib.md5(data.encode()).hexdigest()
            
            # 检查缓存
            cached_report = self._get_cached_report(cache_key)
            if cached_report:
                logger.info("使用缓存的报告")
                return cached_report

            # 解析数据
            commits = json.loads(data)
            logger.info(f"原始提交记录数量: {len(commits)}")

            # 预处理数据，减少信息量
            processed_commits = self._process_commits(commits)
            logger.info(f"处理后提交记录数量: {len(processed_commits)}")

            # 智能采样，确保覆盖更多维度
            sampled_commits = self._sample_commits(processed_commits)
            logger.info(f"采样后提交记录数量: {len(sampled_commits)}")

            # 转换回JSON字符串
            processed_data = json.dumps(sampled_commits, ensure_ascii=False)
            logger.info(f"处理后数据长度: {len(processed_data)} 字符")

            # 计算token使用量
            token_count = self._estimate_tokens(processed_data)
            logger.info(f"估计token使用量: {token_count}")

            # 检查token使用量
            if token_count > self.available_tokens:
                # 进一步减少数据量
                reduced_commits = sampled_commits[:15]  # 进一步减少到15条
                processed_data = json.dumps(reduced_commits, ensure_ascii=False)
                logger.warning(f"token使用量过大，仅处理前15条记录")

            # 优化提示词
            prompt = self._get_optimized_prompt(processed_data)

            # 调用大模型生成报告
            report = self.report_client.completions(
                messages=[
                    {"role": "user", "content": prompt},
                ],
            )

            # 缓存结果
            self._cache_report(cache_key, report)

            return report

        except json.JSONDecodeError as e:
            logger.error(f"解析提交数据失败: {e}")
            return "# 日报生成失败\n\n数据格式错误，无法解析提交记录。"
        except Exception as e:
            logger.error(f"生成日报失败: {e}")
            return "# 日报生成失败\n\n生成日报时发生错误，请稍后重试。"

    def _process_commits(self, commits: list) -> list:
        """预处理提交记录，减少信息量

        Args:
            commits: 原始提交记录列表

        Returns:
            list: 处理后的提交记录列表
        """
        processed_commits = []

        for commit in commits:
            # 只保留必要的字段
            processed_commit = {
                "author": commit.get("author", "Unknown"),
                "project_name": commit.get("project_name", "Unknown"),
                "branch": commit.get("branch", "Unknown"),
                "commit_messages": self._compress_commit_message(commit.get("commit_messages", "No message")),
                "additions": commit.get("additions", 0),
                "deletions": commit.get("deletions", 0),
                "timestamp": commit.get("timestamp", 0)
            }
            processed_commits.append(processed_commit)

        return processed_commits

    def _sample_commits(self, commits: list, max_count: int = 20) -> list:
        """智能采样提交记录，确保覆盖更多维度

        Args:
            commits: 处理后的提交记录列表
            max_count: 最大记录数

        Returns:
            list: 采样后的提交记录列表
        """
        if len(commits) <= max_count:
            return commits

        # 按项目和作者分组
        project_author_map = {}
        for commit in commits:
            key = f"{commit['project_name']}_{commit['author']}"
            if key not in project_author_map:
                project_author_map[key] = []
            project_author_map[key].append(commit)

        # 从每个组中均匀采样
        sampled_commits = []
        per_group_limit = max(1, max_count // len(project_author_map))

        for group_commits in project_author_map.values():
            # 对每个组按提交时间排序
            group_commits.sort(key=lambda x: x.get('timestamp', 0), reverse=True)

            # 取最新的几个提交
            sampled_commits.extend(group_commits[:per_group_limit])

            # 检查是否达到上限
            if len(sampled_commits) >= max_count:
                break

        return sampled_commits[:max_count]

    def _compress_commit_message(self, message: str, max_length: int = 150) -> str:
        """智能压缩提交信息

        Args:
            message: 原始提交信息
            max_length: 最大长度

        Returns:
            str: 压缩后的提交信息
        """
        if len(message) <= max_length:
            return message

        # 保留开头和结尾，中间用省略号
        half = (max_length - 3) // 2
        return message[:half] + "..." + message[-half:]

    def _estimate_tokens(self, text: str) -> int:
        """估算文本的token数量

        Args:
            text: 文本内容

        Returns:
            int: 估算的token数量
        """
        # 粗略估算，1token≈4字符
        return len(text) // 4

    def _get_optimized_prompt(self, data: str) -> str:
        """获取优化后的提示词

        Args:
            data: 处理后的数据

        Returns:
            str: 优化后的提示词
        """
        return f"""# 今日工作日报

## YEQub

**工作概览**
交友留言功能完善

**项目贡献**
- yc-union-mobile: 交友留言完善 (+8, -2)
- yc-union-server: 留言页面交友详情增加内容 (+10, -2)

**代码变更统计**
新增18行，删除4行

---

## dangtt

**工作概览**
个人申报预审服务和在线申报功能开发

**项目贡献**
- gov-integrated-server-nx: 实现预审服务接口和业务逻辑 (+1944, -204)
- gov-integrated-web-nx: 实现在线申报完整功能模块 (+800, -10)

**代码变更统计**
新增2744行，删除214行

---

生成以上格式的日报：

{data}"""

    def _get_cached_report(self, cache_key: str) -> str:
        """获取缓存的报告

        Args:
            cache_key: 缓存键

        Returns:
            str: 缓存的报告内容，或None
        """
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data['timestamp'] < self.cache_ttl:
                return cached_data['report']
            else:
                del self.cache[cache_key]
        return None

    def _cache_report(self, cache_key: str, report: str) -> None:
        """缓存报告

        Args:
            cache_key: 缓存键
            report: 报告内容
        """
        self.cache[cache_key] = {
            'report': report,
            'timestamp': time.time()
        }
        # 限制缓存大小
        if len(self.cache) > 10:
            # 删除最旧的缓存
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]

