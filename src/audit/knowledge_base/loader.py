"""
知识库加载器
负责加载和管理安全知识库
"""

import json
import logging
from typing import Dict, List, Optional, Tuple

from .base import KnowledgeCategory, KnowledgeDocument

logger = logging.getLogger(__name__)


class KnowledgeLoader:
    """
    知识库加载器
    负责从文件系统加载安全知识库
    """
    
    def __init__(self, knowledge_dir: Optional[str] = None):
        """
        初始化知识库加载器
        
        Args:
            knowledge_dir: 知识库目录路径
        """
        self.knowledge_dir = knowledge_dir
        self._knowledge_cache: Dict[str, List[KnowledgeDocument]] = {}
        self._initialized = False
    
    def initialize(self):
        """
        初始化知识库
        """
        if self._initialized:
            return
        
        logger.info("Initializing knowledge base...")
        
        # 加载框架知识
        self._load_framework_knowledge()
        
        # 加载漏洞知识
        self._load_vulnerability_knowledge()
        
        self._initialized = True
        logger.info("Knowledge base initialized successfully")
    
    def _load_framework_knowledge(self):
        """
        加载框架相关知识
        """
        try:
            from .frameworks import (
                django_knowledge,
                express_knowledge,
                fastapi_knowledge,
                flask_knowledge,
                react_knowledge,
                supabase_knowledge
            )
            
            framework_knowledge = []
            
            # 加载各框架知识
            framework_knowledge.extend(django_knowledge)
            framework_knowledge.extend(express_knowledge)
            framework_knowledge.extend(fastapi_knowledge)
            framework_knowledge.extend(flask_knowledge)
            framework_knowledge.extend(react_knowledge)
            framework_knowledge.extend(supabase_knowledge)
            
            self._knowledge_cache["frameworks"] = framework_knowledge
            logger.info(f"Loaded {len(framework_knowledge)} framework knowledge items")
            
        except Exception as e:
            logger.error(f"Failed to load framework knowledge: {e}")
    
    def _load_vulnerability_knowledge(self):
        """
        加载漏洞相关知识
        """
        try:
            from .vulnerabilities import (
                auth_knowledge,
                business_logic_knowledge,
                crypto_knowledge,
                csrf_knowledge,
                deserialization_knowledge,
                injection_knowledge,
                open_redirect_knowledge,
                path_traversal_knowledge,
                race_condition_knowledge,
                ssrf_knowledge,
                xss_knowledge,
                xxe_knowledge
            )
            
            vulnerability_knowledge = []
            
            # 加载各类型漏洞知识
            vulnerability_knowledge.extend(auth_knowledge)
            vulnerability_knowledge.extend(business_logic_knowledge)
            vulnerability_knowledge.extend(crypto_knowledge)
            vulnerability_knowledge.extend(csrf_knowledge)
            vulnerability_knowledge.extend(deserialization_knowledge)
            vulnerability_knowledge.extend(injection_knowledge)
            vulnerability_knowledge.extend(open_redirect_knowledge)
            vulnerability_knowledge.extend(path_traversal_knowledge)
            vulnerability_knowledge.extend(race_condition_knowledge)
            vulnerability_knowledge.extend(ssrf_knowledge)
            vulnerability_knowledge.extend(xss_knowledge)
            vulnerability_knowledge.extend(xxe_knowledge)
            
            self._knowledge_cache["vulnerabilities"] = vulnerability_knowledge
            logger.info(f"Loaded {len(vulnerability_knowledge)} vulnerability knowledge items")
            
        except Exception as e:
            logger.error(f"Failed to load vulnerability knowledge: {e}")
    
    def get_knowledge_by_category(self, category: KnowledgeCategory) -> List[KnowledgeDocument]:
        """
        根据类别获取知识
        
        Args:
            category: 知识类别
            
        Returns:
            知识文档列表
        """
        if not self._initialized:
            self.initialize()
        
        # 根据类别映射到相应的缓存键
        category_map = {
            KnowledgeCategory.FRAMEWORK: "frameworks",
            KnowledgeCategory.VULNERABILITY: "vulnerabilities"
        }
        
        cache_key = category_map.get(category)
        if cache_key and cache_key in self._knowledge_cache:
            return self._knowledge_cache[cache_key]
        
        return []
    
    def get_knowledge_by_tags(self, tags: List[str]) -> List[KnowledgeDocument]:
        """
        根据标签获取知识
        
        Args:
            tags: 标签列表
            
        Returns:
            知识文档列表
        """
        if not self._initialized:
            self.initialize()
        
        result = []
        
        # 遍历所有缓存的知识
        for knowledge_list in self._knowledge_cache.values():
            for knowledge in knowledge_list:
                if any(tag in knowledge.tags for tag in tags):
                    result.append(knowledge)
        
        return result
    
    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[KnowledgeDocument]:
        """
        根据ID获取知识
        
        Args:
            knowledge_id: 知识ID
            
        Returns:
            知识文档或None
        """
        if not self._initialized:
            self.initialize()
        
        # 遍历所有缓存的知识
        for knowledge_list in self._knowledge_cache.values():
            for knowledge in knowledge_list:
                if knowledge.id == knowledge_id:
                    return knowledge
        
        return None
    
    def search_knowledge(self, query: str, limit: int = 20) -> List[KnowledgeDocument]:
        """
        搜索知识
        
        Args:
            query: 搜索查询
            limit: 返回结果数量限制
            
        Returns:
            知识文档列表
        """
        if not self._initialized:
            self.initialize()
        
        result = []
        query_lower = query.lower()
        
        # 遍历所有缓存的知识
        for knowledge_list in self._knowledge_cache.values():
            for knowledge in knowledge_list:
                # 检查标题和内容是否包含查询
                if (query_lower in knowledge.title.lower() or 
                    query_lower in knowledge.content.lower()):
                    result.append(knowledge)
        
        return result[:limit]
    
    def build_system_prompt_with_modules(self, base_prompt: str, knowledge_modules: List[str]) -> str:
        """
        使用知识模块构建系统提示词
        
        Args:
            base_prompt: 基础提示词
            knowledge_modules: 知识模块列表
            
        Returns:
            增强后的提示词
        """
        if not knowledge_modules:
            return base_prompt
        
        # 获取相关知识
        relevant_knowledge = []
        
        for module in knowledge_modules:
            if module == "all":
                # 加载所有知识
                for knowledge_list in self._knowledge_cache.values():
                    relevant_knowledge.extend(knowledge_list)
            elif module == "frameworks":
                # 加载框架知识
                if "frameworks" in self._knowledge_cache:
                    relevant_knowledge.extend(self._knowledge_cache["frameworks"])
            elif module == "vulnerabilities":
                # 加载漏洞知识
                if "vulnerabilities" in self._knowledge_cache:
                    relevant_knowledge.extend(self._knowledge_cache["vulnerabilities"])
            else:
                # 尝试加载特定框架或漏洞类型的知识
                try:
                    if module in ["django", "express", "fastapi", "flask", "react", "supabase"]:
                        # 加载特定框架知识
                        module_path = f".frameworks.{module}_knowledge"
                        module = __import__(module_path, fromlist=["*"], level=1)
                        framework_knowledge = getattr(module, f"{module}_knowledge")
                        relevant_knowledge.extend(framework_knowledge)
                    elif module in ["auth", "business_logic", "crypto", "csrf", "deserialization", 
                                   "injection", "open_redirect", "path_traversal", "race_condition", 
                                   "ssrf", "xss", "xxe"]:
                        # 加载特定漏洞类型知识
                        module_path = f".vulnerabilities.{module}_knowledge"
                        module = __import__(module_path, fromlist=["*"], level=1)
                        vuln_knowledge = getattr(module, f"{module}_knowledge")
                        relevant_knowledge.extend(vuln_knowledge)
                except Exception as e:
                    logger.warning(f"Failed to load knowledge module {module}: {e}")
        
        # 构建知识部分
        knowledge_section = "\n\n## 安全知识库\n\n"
        
        # 按类别组织知识
        by_category = {}
        for knowledge in relevant_knowledge:
            if knowledge.category not in by_category:
                by_category[knowledge.category] = []
            by_category[knowledge.category].append(knowledge)
        
        # 添加各类别知识
        for category, items in by_category.items():
            knowledge_section += f"### {category.value}\n\n"
            
            for item in items[:10]:  # 每个类别最多10个
                knowledge_section += f"#### {item.title}\n"
                knowledge_section += f"{item.content}\n\n"
        
        return base_prompt + knowledge_section


# 全局知识库加载器实例
knowledge_loader = KnowledgeLoader()
