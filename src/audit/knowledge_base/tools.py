"""
知识库工具
提供与知识库交互的Agent工具
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from ..tools.base import AgentTool, ToolResult
from .base import KnowledgeCategory, KnowledgeDocument
from .rag_knowledge import rag_knowledge_base

logger = logging.getLogger(__name__)


@dataclass
class SecurityKnowledgeQueryInput:
    """
    安全知识查询输入
    """
    query: str
    limit: int = 10
    categories: Optional[List[str]] = None


class SecurityKnowledgeQueryTool(AgentTool):
    """
    安全知识查询工具
    用于查询安全知识库中的信息
    """
    
    name = "query_security_knowledge"
    description = "查询安全知识库中的信息，用于获取安全相关的知识和建议"
    args_schema = SecurityKnowledgeQueryInput
    
    async def execute(self, query: str, limit: int = 10, categories: Optional[List[str]] = None) -> ToolResult:
        """
        执行安全知识查询
        
        Args:
            query: 查询字符串
            limit: 返回结果数量限制
            categories: 知识类别过滤
            
        Returns:
            工具执行结果
        """
        try:
            logger.info(f"Executing security knowledge query: {query}")
            
            # 搜索知识库
            results = rag_knowledge_base.search(query, limit=limit)
            
            # 如果指定了类别，进行过滤
            if categories:
                filtered_results = []
                for result in results:
                    if result.category.value in categories:
                        filtered_results.append(result)
                results = filtered_results
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "title": result.title,
                    "content": result.content,
                    "category": result.category.value,
                    "tags": result.tags,
                    "severity": result.severity,
                    "cwe_ids": result.cwe_ids,
                    "owasp_ids": result.owasp_ids
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Query returned {len(formatted_results)} results")
            
            return ToolResult(
                success=True,
                data={
                    "query": query,
                    "results": formatted_results,
                    "total": len(formatted_results)
                },
                metadata={
                    "query": query,
                    "results_count": len(formatted_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Security knowledge query failed: {e}")
            return ToolResult(
                success=False,
                error=f"查询安全知识失败: {str(e)}"
            )


@dataclass
class VulnerabilityKnowledgeInput:
    """
    漏洞知识获取输入
    """
    vulnerability_type: str
    limit: int = 20


class GetVulnerabilityKnowledgeTool(AgentTool):
    """
    获取漏洞知识工具
    用于获取特定类型漏洞的详细知识
    """
    
    name = "get_vulnerability_knowledge"
    description = "获取特定类型漏洞的详细知识，包括检测方法、修复建议等"
    args_schema = VulnerabilityKnowledgeInput
    
    async def execute(self, vulnerability_type: str, limit: int = 20) -> ToolResult:
        """
        执行漏洞知识获取
        
        Args:
            vulnerability_type: 漏洞类型
            limit: 返回结果数量限制
            
        Returns:
            工具执行结果
        """
        try:
            logger.info(f"Getting vulnerability knowledge for: {vulnerability_type}")
            
            # 获取漏洞知识
            results = rag_knowledge_base.get_vulnerability_knowledge(vulnerability_type)
            
            # 格式化结果
            formatted_results = []
            for result in results[:limit]:
                formatted_result = {
                    "id": result.id,
                    "title": result.title,
                    "content": result.content,
                    "category": result.category.value,
                    "tags": result.tags,
                    "severity": result.severity,
                    "cwe_ids": result.cwe_ids,
                    "owasp_ids": result.owasp_ids,
                    "metadata": result.metadata
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Got {len(formatted_results)} vulnerability knowledge items")
            
            return ToolResult(
                success=True,
                data={
                    "vulnerability_type": vulnerability_type,
                    "results": formatted_results,
                    "total": len(formatted_results)
                },
                metadata={
                    "vulnerability_type": vulnerability_type,
                    "results_count": len(formatted_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Get vulnerability knowledge failed: {e}")
            return ToolResult(
                success=False,
                error=f"获取漏洞知识失败: {str(e)}"
            )


@dataclass
class SecurityRuleMatchInput:
    """
    安全规则匹配输入
    """
    code: str
    language: str
    rules: Optional[List[str]] = None


class SecurityRuleMatchTool(AgentTool):
    """
    安全规则匹配工具
    用于在代码中匹配安全规则
    """
    
    name = "match_security_rules"
    description = "在代码中匹配安全规则，检测潜在的安全问题"
    args_schema = SecurityRuleMatchInput
    
    async def execute(self, code: str, language: str, rules: Optional[List[str]] = None) -> ToolResult:
        """
        执行安全规则匹配
        
        Args:
            code: 代码文本
            language: 代码语言
            rules: 要匹配的规则列表
            
        Returns:
            工具执行结果
        """
        try:
            logger.info(f"Matching security rules for {language} code")
            
            # 这里可以实现更复杂的规则匹配逻辑
            # 暂时使用简单的模式匹配
            matches = []
            
            # 检测SQL注入
            if "sql" in (rules or []) or not rules:
                if "execute" in code and ("select" in code.lower() or "insert" in code.lower()):
                    matches.append({
                        "rule": "sql_injection",
                        "severity": "high",
                        "message": "潜在的SQL注入漏洞",
                        "confidence": 0.7
                    })
            
            # 检测XSS
            if "xss" in (rules or []) or not rules:
                if "innerHTML" in code or "document.write" in code:
                    matches.append({
                        "rule": "xss",
                        "severity": "medium",
                        "message": "潜在的XSS漏洞",
                        "confidence": 0.6
                    })
            
            # 检测命令注入
            if "command_injection" in (rules or []) or not rules:
                if "exec" in code or "system" in code:
                    matches.append({
                        "rule": "command_injection",
                        "severity": "high",
                        "message": "潜在的命令注入漏洞",
                        "confidence": 0.8
                    })
            
            logger.info(f"Found {len(matches)} security rule matches")
            
            return ToolResult(
                success=True,
                data={
                    "language": language,
                    "matches": matches,
                    "total": len(matches)
                },
                metadata={
                    "language": language,
                    "matches_count": len(matches)
                }
            )
            
        except Exception as e:
            logger.error(f"Security rule match failed: {e}")
            return ToolResult(
                success=False,
                error=f"匹配安全规则失败: {str(e)}"
            )


class KnowledgeBaseTool(AgentTool):
    """
    知识库工具
    提供对知识库的完整访问
    """
    
    name = "knowledge_base"
    description = "提供对安全知识库的完整访问，包括搜索、获取特定知识等功能"
    
    async def execute(self, action: str, **kwargs) -> ToolResult:
        """
        执行知识库操作
        
        Args:
            action: 操作类型 (search, get_by_id, get_by_category, get_framework_knowledge, get_project_security_knowledge)
            **kwargs: 操作参数
            
        Returns:
            工具执行结果
        """
        try:
            logger.info(f"Executing knowledge base action: {action}")
            
            if action == "search":
                query = kwargs.get("query")
                limit = kwargs.get("limit", 10)
                
                results = rag_knowledge_base.search(query, limit=limit)
                
                formatted_results = []
                for result in results:
                    formatted_result = {
                        "id": result.id,
                        "title": result.title,
                        "content": result.content,
                        "category": result.category.value,
                        "tags": result.tags
                    }
                    formatted_results.append(formatted_result)
                
                return ToolResult(
                    success=True,
                    data={
                        "action": "search",
                        "query": query,
                        "results": formatted_results
                    }
                )
                
            elif action == "get_by_id":
                knowledge_id = kwargs.get("knowledge_id")
                
                result = rag_knowledge_base.get_by_id(knowledge_id)
                
                if result:
                    formatted_result = {
                        "id": result.id,
                        "title": result.title,
                        "content": result.content,
                        "category": result.category.value,
                        "tags": result.tags,
                        "severity": result.severity,
                        "cwe_ids": result.cwe_ids,
                        "owasp_ids": result.owasp_ids
                    }
                    return ToolResult(
                        success=True,
                        data={
                            "action": "get_by_id",
                            "result": formatted_result
                        }
                    )
                else:
                    return ToolResult(
                        success=False,
                        error=f"知识ID不存在: {knowledge_id}"
                    )
                
            elif action == "get_by_category":
                category = kwargs.get("category")
                limit = kwargs.get("limit", 50)
                
                # 转换类别
                category_map = {
                    "vulnerability": KnowledgeCategory.VULNERABILITY,
                    "framework": KnowledgeCategory.FRAMEWORK,
                    "best_practice": KnowledgeCategory.BEST_PRACTICE,
                    "remediation": KnowledgeCategory.REMEDIATION,
                    "code_pattern": KnowledgeCategory.CODE_PATTERN,
                    "compliance": KnowledgeCategory.COMPLIANCE
                }
                
                if category not in category_map:
                    return ToolResult(
                        success=False,
                        error=f"无效的知识类别: {category}"
                    )
                
                results = rag_knowledge_base.get_by_category(category_map[category], limit=limit)
                
                formatted_results = []
                for result in results:
                    formatted_result = {
                        "id": result.id,
                        "title": result.title,
                        "content": result.content,
                        "category": result.category.value,
                        "tags": result.tags
                    }
                    formatted_results.append(formatted_result)
                
                return ToolResult(
                    success=True,
                    data={
                        "action": "get_by_category",
                        "category": category,
                        "results": formatted_results
                    }
                )
                
            elif action == "get_framework_knowledge":
                framework = kwargs.get("framework")
                
                results = rag_knowledge_base.get_framework_knowledge(framework)
                
                formatted_results = []
                for result in results:
                    formatted_result = {
                        "id": result.id,
                        "title": result.title,
                        "content": result.content,
                        "category": result.category.value,
                        "tags": result.tags
                    }
                    formatted_results.append(formatted_result)
                
                return ToolResult(
                    success=True,
                    data={
                        "action": "get_framework_knowledge",
                        "framework": framework,
                        "results": formatted_results
                    }
                )
                
            elif action == "get_project_security_knowledge":
                project_info = kwargs.get("project_info", {})
                
                results = rag_knowledge_base.get_project_security_knowledge(project_info)
                
                formatted_results = []
                for result in results:
                    formatted_result = {
                        "id": result.id,
                        "title": result.title,
                        "content": result.content,
                        "category": result.category.value,
                        "tags": result.tags
                    }
                    formatted_results.append(formatted_result)
                
                return ToolResult(
                    success=True,
                    data={
                        "action": "get_project_security_knowledge",
                        "project_info": project_info,
                        "results": formatted_results
                    }
                )
                
            elif action == "list_modules":
                # 列出所有可用的知识模块
                modules = {
                    "frameworks": ["django", "express", "fastapi", "flask", "react", "supabase"],
                    "vulnerabilities": ["auth", "business_logic", "crypto", "csrf", "deserialization", 
                                        "injection", "open_redirect", "path_traversal", "race_condition", 
                                        "ssrf", "xss", "xxe"]
                }
                
                return ToolResult(
                    success=True,
                    data={
                        "action": "list_modules",
                        "modules": modules
                    }
                )
                
            else:
                return ToolResult(
                    success=False,
                    error=f"无效的知识库操作: {action}"
                )
                
        except Exception as e:
            logger.error(f"Knowledge base action failed: {e}")
            return ToolResult(
                success=False,
                error=f"知识库操作失败: {str(e)}"
            )


@dataclass
class ProjectSecurityQueryInput:
    """
    项目安全查询输入
    """
    project_info: Dict[str, str]


class ProjectSecurityQueryTool(AgentTool):
    """
    项目安全查询工具
    用于根据项目信息查询相关安全知识
    """
    
    name = "project_security_query"
    description = "根据项目信息查询相关安全知识，包括语言、框架、数据库等"
    args_schema = ProjectSecurityQueryInput
    
    async def execute(self, project_info: Dict[str, str]) -> ToolResult:
        """
        执行项目安全查询
        
        Args:
            project_info: 项目信息字典
            
        Returns:
            工具执行结果
        """
        try:
            logger.info(f"Executing project security query: {project_info}")
            
            # 获取项目相关安全知识
            results = rag_knowledge_base.get_project_security_knowledge(project_info)
            
            # 格式化结果
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result.id,
                    "title": result.title,
                    "content": result.content,
                    "category": result.category.value,
                    "tags": result.tags,
                    "severity": result.severity
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Project security query returned {len(formatted_results)} results")
            
            return ToolResult(
                success=True,
                data={
                    "project_info": project_info,
                    "results": formatted_results,
                    "total": len(formatted_results)
                },
                metadata={
                    "project_info": project_info,
                    "results_count": len(formatted_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Project security query failed: {e}")
            return ToolResult(
                success=False,
                error=f"项目安全查询失败: {str(e)}"
            )


@dataclass
class VulnerabilityDataInput:
    """
    漏洞数据输入
    """
    vulnerability_type: Optional[str] = None
    severity: Optional[str] = None
    language: Optional[str] = None
    database: Optional[str] = None
    limit: int = 20


class VulnerabilityDataTool(AgentTool):
    """
    漏洞数据工具
    用于获取漏洞数据
    """
    
    name = "get_vulnerability_data"
    description = "获取漏洞数据，可根据类型、严重程度、语言等过滤"
    args_schema = VulnerabilityDataInput
    
    async def execute(self, vulnerability_type: Optional[str] = None, severity: Optional[str] = None, 
                      language: Optional[str] = None, database: Optional[str] = None, 
                      limit: int = 20) -> ToolResult:
        """
        执行漏洞数据获取
        
        Args:
            vulnerability_type: 漏洞类型
            severity: 严重程度
            language: 编程语言
            database: 数据库类型
            limit: 返回结果数量限制
            
        Returns:
            工具执行结果
        """
        try:
            logger.info(f"Getting vulnerability data: type={vulnerability_type}, severity={severity}")
            
            # 构建查询
            query_parts = []
            if vulnerability_type:
                query_parts.append(vulnerability_type)
            if language:
                query_parts.append(language)
            if database:
                query_parts.append(database)
            
            query = " ".join(query_parts) if query_parts else "vulnerability"
            
            # 搜索知识库
            results = rag_knowledge_base.search(query, limit=limit)
            
            # 过滤结果
            filtered_results = []
            for result in results:
                # 只保留漏洞类别
                if result.category != KnowledgeCategory.VULNERABILITY:
                    continue
                
                # 过滤严重程度
                if severity and result.severity != severity:
                    continue
                
                filtered_results.append(result)
            
            # 格式化结果
            formatted_results = []
            for result in filtered_results[:limit]:
                formatted_result = {
                    "id": result.id,
                    "title": result.title,
                    "content": result.content,
                    "category": result.category.value,
                    "severity": result.severity,
                    "cwe_ids": result.cwe_ids,
                    "owasp_ids": result.owasp_ids,
                    "tags": result.tags
                }
                formatted_results.append(formatted_result)
            
            logger.info(f"Got {len(formatted_results)} vulnerability data items")
            
            return ToolResult(
                success=True,
                data={
                    "vulnerability_type": vulnerability_type,
                    "severity": severity,
                    "language": language,
                    "database": database,
                    "results": formatted_results,
                    "total": len(formatted_results)
                },
                metadata={
                    "results_count": len(formatted_results)
                }
            )
            
        except Exception as e:
            logger.error(f"Get vulnerability data failed: {e}")
            return ToolResult(
                success=False,
                error=f"获取漏洞数据失败: {str(e)}"
            )
