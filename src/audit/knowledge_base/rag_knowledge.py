"""
RAG知识库
基于检索增强生成的知识库系统
"""

import logging
from typing import Dict, List, Optional, Tuple

from .base import KnowledgeCategory, KnowledgeDocument
from .loader import knowledge_loader

logger = logging.getLogger(__name__)


class RAGKnowledgeBase:
    """
    RAG知识库
    基于检索增强生成的知识库系统
    """
    
    def __init__(self):
        """
        初始化RAG知识库
        """
        self.loader = knowledge_loader
        self.loader.initialize()
        logger.info("RAGKnowledgeBase initialized")
    
    def search(self, query: str, limit: int = 10) -> List[KnowledgeDocument]:
        """
        搜索知识库
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            知识文档列表
        """
        try:
            results = self.loader.search_knowledge(query, limit)
            logger.info(f"Search for '{query}' returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []
    
    def get_by_category(self, category: KnowledgeCategory, limit: int = 50) -> List[KnowledgeDocument]:
        """
        根据类别获取知识
        
        Args:
            category: 知识类别
            limit: 返回结果数量限制
            
        Returns:
            知识文档列表
        """
        try:
            results = self.loader.get_knowledge_by_category(category)
            logger.info(f"Get by category '{category.value}' returned {len(results)} results")
            return results[:limit]
        except Exception as e:
            logger.error(f"Get by category failed: {e}")
            return []
    
    def get_by_tags(self, tags: List[str], limit: int = 20) -> List[KnowledgeDocument]:
        """
        根据标签获取知识
        
        Args:
            tags: 标签列表
            limit: 返回结果数量限制
            
        Returns:
            知识文档列表
        """
        try:
            results = self.loader.get_knowledge_by_tags(tags)
            logger.info(f"Get by tags {tags} returned {len(results)} results")
            return results[:limit]
        except Exception as e:
            logger.error(f"Get by tags failed: {e}")
            return []
    
    def get_by_id(self, knowledge_id: str) -> Optional[KnowledgeDocument]:
        """
        根据ID获取知识
        
        Args:
            knowledge_id: 知识ID
            
        Returns:
            知识文档或None
        """
        try:
            result = self.loader.get_knowledge_by_id(knowledge_id)
            if result:
                logger.info(f"Get by ID '{knowledge_id}' found: {result.title}")
            else:
                logger.info(f"Get by ID '{knowledge_id}' not found")
            return result
        except Exception as e:
            logger.error(f"Get by ID failed: {e}")
            return None
    
    def get_vulnerability_knowledge(self, vulnerability_type: str) -> List[KnowledgeDocument]:
        """
        获取特定类型漏洞的知识
        
        Args:
            vulnerability_type: 漏洞类型
            
        Returns:
            知识文档列表
        """
        try:
            # 首先尝试直接加载特定类型的漏洞知识
            try:
                module_path = f".vulnerabilities.{vulnerability_type}_knowledge"
                module = __import__(module_path, fromlist=["*"], level=1)
                vuln_knowledge = getattr(module, f"{vulnerability_type}_knowledge")
                logger.info(f"Loaded {len(vuln_knowledge)} knowledge items for vulnerability type '{vulnerability_type}'")
                return vuln_knowledge
            except Exception as e:
                logger.warning(f"Failed to load specific vulnerability knowledge: {e}")
                
            # 回退到搜索方法
            query = vulnerability_type
            results = self.search(query, limit=20)
            
            # 过滤出与漏洞相关的知识
            filtered_results = [
                result for result in results 
                if result.category == KnowledgeCategory.VULNERABILITY
            ]
            
            logger.info(f"Found {len(filtered_results)} vulnerability knowledge items for '{vulnerability_type}'")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Get vulnerability knowledge failed: {e}")
            return []
    
    def get_framework_knowledge(self, framework: str) -> List[KnowledgeDocument]:
        """
        获取特定框架的知识
        
        Args:
            framework: 框架名称
            
        Returns:
            知识文档列表
        """
        try:
            # 首先尝试直接加载特定框架的知识
            try:
                module_path = f".frameworks.{framework}_knowledge"
                module = __import__(module_path, fromlist=["*"], level=1)
                framework_knowledge = getattr(module, f"{framework}_knowledge")
                logger.info(f"Loaded {len(framework_knowledge)} knowledge items for framework '{framework}'")
                return framework_knowledge
            except Exception as e:
                logger.warning(f"Failed to load specific framework knowledge: {e}")
                
            # 回退到搜索方法
            query = framework
            results = self.search(query, limit=20)
            
            # 过滤出与框架相关的知识
            filtered_results = [
                result for result in results 
                if result.category == KnowledgeCategory.FRAMEWORK
            ]
            
            logger.info(f"Found {len(filtered_results)} framework knowledge items for '{framework}'")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Get framework knowledge failed: {e}")
            return []
    
    def get_project_security_knowledge(self, project_info: Dict[str, str]) -> List[KnowledgeDocument]:
        """
        根据项目信息获取相关安全知识
        
        Args:
            project_info: 项目信息字典，包含language、framework、database等
            
        Returns:
            知识文档列表
        """
        try:
            relevant_knowledge = []
            
            # 根据语言获取相关知识
            language = project_info.get("language")
            if language:
                language_results = self.search(language, limit=10)
                relevant_knowledge.extend(language_results)
            
            # 根据框架获取相关知识
            framework = project_info.get("framework")
            if framework:
                framework_results = self.get_framework_knowledge(framework)
                relevant_knowledge.extend(framework_results)
            
            # 根据数据库获取相关知识
            database = project_info.get("database")
            if database:
                database_results = self.search(database, limit=10)
                relevant_knowledge.extend(database_results)
            
            # 去重
            unique_knowledge = []
            seen_ids = set()
            
            for knowledge in relevant_knowledge:
                if knowledge.id not in seen_ids:
                    seen_ids.add(knowledge.id)
                    unique_knowledge.append(knowledge)
            
            logger.info(f"Found {len(unique_knowledge)} relevant security knowledge items for project")
            return unique_knowledge[:30]  # 限制返回数量
            
        except Exception as e:
            logger.error(f"Get project security knowledge failed: {e}")
            return []
    
    def generate_contextual_prompt(self, query: str, context: Dict[str, any] = None) -> str:
        """
        生成上下文相关的提示词
        
        Args:
            query: 查询
            context: 上下文信息
            
        Returns:
            上下文相关的提示词
        """
        try:
            # 搜索相关知识
            search_results = self.search(query, limit=5)
            
            # 构建上下文
            context_parts = [f"# 查询: {query}"]
            
            if context:
                context_parts.append("## 上下文信息")
                for key, value in context.items():
                    context_parts.append(f"- {key}: {value}")
            
            if search_results:
                context_parts.append("## 相关知识")
                for i, result in enumerate(search_results, 1):
                    context_parts.append(f"### {i}. {result.title}")
                    context_parts.append(f"**类别**: {result.category.value}")
                    if result.tags:
                        context_parts.append(f"**标签**: {', '.join(result.tags)}")
                    context_parts.append(f"**内容**: {result.content[:500]}...")
                    context_parts.append("")
            
            prompt = "\n".join(context_parts)
            logger.info(f"Generated contextual prompt for query '{query}'")
            return prompt
            
        except Exception as e:
            logger.error(f"Generate contextual prompt failed: {e}")
            return f"# 查询: {query}"


# 全局RAG知识库实例
rag_knowledge_base = RAGKnowledgeBase()
