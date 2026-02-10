# RAG管理器，集成DeepAudit的RAG功能

import os
from typing import List, Optional, Dict, Any
from src.audit.rag.embeddings import EmbeddingService
from src.audit.rag.indexer import CodeIndexer
from src.audit.rag.retriever import CodeRetriever
from src.audit.knowledge.rag_knowledge import SecurityKnowledgeRAG

class RAGManager:
    """RAG管理器，负责协调RAG相关的功能"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化RAG管理器
        
        Args:
            config: RAG配置参数
        """
        self.config = config or {}
        self.embedding_service = None
        self.code_indexer = None
        self.code_retriever = None
        self.security_knowledge_rag = None
        
    async def initialize(self):
        """初始化RAG服务"""
        # 初始化嵌入服务
        self.embedding_service = EmbeddingService()
        
        # 初始化代码索引器和检索器
        self.code_indexer = CodeIndexer(collection_name="code_review", embedding_service=self.embedding_service)
        self.code_retriever = CodeRetriever(collection_name="code_review", embedding_service=self.embedding_service)
        
        # 异步初始化code_indexer
        await self.code_indexer.initialize()
        
        # 初始化安全知识RAG
        self.security_knowledge_rag = SecurityKnowledgeRAG()
        await self.security_knowledge_rag.initialize()
        
    async def index_repository(self, repo_path: str, **kwargs):
        """索引代码仓库
        
        Args:
            repo_path: 仓库路径
            **kwargs: 额外参数
        """
        if not self.code_indexer:
            await self.initialize()
        
        # 异步索引仓库
        async for progress in self.code_indexer.smart_index_directory(repo_path, **kwargs):
            print(f"Indexing progress: {progress.processed_files}/{progress.total_files} files, {progress.indexed_chunks}/{progress.total_chunks} chunks")
        
        return True
    
    async def index_files(self, files: List[str], **kwargs):
        """索引指定文件
        
        Args:
            files: 文件列表
            **kwargs: 额外参数
        """
        if not self.code_indexer:
            await self.initialize()
        
        # 异步索引文件
        async for progress in self.code_indexer.index_files(files, **kwargs):
            print(f"Indexing progress: {progress.processed_files}/{progress.total_files} files, {progress.indexed_chunks}/{progress.total_chunks} chunks")
        
        return True
    
    async def retrieve(self, query: str, **kwargs):
        """检索相关代码
        
        Args:
            query: 查询语句
            **kwargs: 额外参数
        """
        if not self.code_retriever:
            await self.initialize()
        
        return await self.code_retriever.retrieve(query, **kwargs)
    
    async def search_security_knowledge(self, query: str, **kwargs):
        """搜索安全知识
        
        Args:
            query: 查询语句
            **kwargs: 额外参数
        """
        if not self.security_knowledge_rag:
            await self.initialize()
        
        return await self.security_knowledge_rag.search(query, **kwargs)
    
    async def get_vulnerability_knowledge(self, vulnerability_type: str, **kwargs):
        """获取漏洞知识
        
        Args:
            vulnerability_type: 漏洞类型
            **kwargs: 额外参数
        """
        if not self.security_knowledge_rag:
            await self.initialize()
        
        return await self.security_knowledge_rag.get_vulnerability_knowledge(vulnerability_type, **kwargs)

# 全局RAG管理器实例
rag_manager = RAGManager()
