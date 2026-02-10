from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import asyncio
import os

from src.audit.agent_system.agents.orchestrator import OrchestratorAgent
from src.audit.agent_system.core.registry import agent_registry
from src.audit.agent_system.core.message import message_bus
from src.audit.agent_system.config import get_agent_config
from src.audit.agent_system.tools import (
    RAGQueryTool,
    SecurityCodeSearchTool,
    FunctionContextTool,
    PatternMatchTool,
    CodeAnalysisTool,
    DataFlowAnalysisTool,
    VulnerabilityValidationTool,
    FileReadTool,
    FileSearchTool,
    ListFilesTool,
    SandboxTool,
    SandboxHttpTool,
    VulnerabilityVerifyTool,
    ThinkTool,
    ReflectTool,
    CreateVulnerabilityReportTool,
    FinishScanTool,
    SmartScanTool,
    QuickAuditTool
)
from src.audit.sandbox.vulnerability_verifier import VulnerabilityVerifier
from src.audit.rag.rag_manager import rag_manager
from src.audit.llm.service import llm_service


class AuditManager:
    """
    审计管理器，负责协调DeepAudit核心逻辑的执行
    完全基于DeepAudit的agent协作架构
    """
    
    def __init__(self, sandbox=False):
        """
        初始化审计管理器
        
        Args:
            sandbox: 是否启用沙箱验证
        """
        self.sandbox = sandbox
        self.verifier = VulnerabilityVerifier() if sandbox else None
        self.config = get_agent_config()
    
    async def audit(self, repo_path: str, **kwargs) -> Dict[str, Any]:
        """
        执行完整的审计流程
        基于DeepAudit的agent协作架构
        
        Args:
            repo_path: 仓库路径
            **kwargs: 额外参数
                - file_paths: 要分析的特定文件路径列表
                - scan_config: 扫描配置
                - user_config: 用户配置
        
        Returns:
            审计结果
        """
        start_time = datetime.now(timezone.utc)
        
        print(f"🚀 Starting DeepAudit for repository: {repo_path}")
        print(f"📋 Audit configuration: sandbox={self.sandbox}")
        
        # 1. 初始化RAG系统
        print("📚 Initializing RAG system...")
        try:
            await rag_manager.initialize()
            
            # 2. 索引代码仓库
            print(f"🔍 Indexing repository: {repo_path}")
            await rag_manager.index_repository(repo_path)
        except Exception as e:
            print(f"⚠️ RAG initialization failed: {e}")
            print("⚠️ Using fallback mode without RAG")
        
        # 3. 初始化Agent系统
        await self._initialize_agent_system()
        
        # 2. 创建并配置编排Agent
        orchestrator = await self._create_orchestrator_agent(repo_path, **kwargs)
        
        # 3. 执行审计流程
        input_data = {
            "project_info": {
                "root": repo_path,
                "name": os.path.basename(repo_path)
            },
            "config": kwargs.get('scan_config', {}),
            "project_root": repo_path
        }
        result = await orchestrator.run(input_data)
        audit_result = result.data if result.success else {"findings": []}
        
        # 4. 如果启用了沙箱，验证漏洞
        if self.sandbox and self.verifier and audit_result.get('findings'):
            verified_findings = await self._verify_vulnerabilities(audit_result['findings'])
            audit_result['findings'] = verified_findings
            audit_result['verified_count'] = len(verified_findings)
            print(f"✅ Verified {len(verified_findings)} actual vulnerabilities")
        
        # 5. 生成最终报告
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        final_result = {
            "project": repo_path,
            "date": end_time.strftime('%Y-%m-%d %H:%M:%S'),
            "duration": f"{duration:.2f} seconds",
            "findings": audit_result.get('findings', []),
            "conclusion": audit_result.get('conclusion', self._generate_conclusion(audit_result.get('findings', []))),
            "agent_stats": audit_result.get('agent_stats', {}),
            "verified_count": audit_result.get('verified_count', 0)
        }
        
        print(f"🎉 Audit completed successfully in {duration:.2f} seconds")
        print(f"📊 Found {len(final_result['findings'])} issues")
        
        # 清理Agent系统
        await self._cleanup_agent_system()
        
        return final_result
    
    async def _initialize_agent_system(self):
        """
        初始化Agent系统
        """
        print("🔧 Initializing Agent system...")
        
        # 重置Agent注册表
        agent_registry.clear()
        
        # 重置消息总线
        message_bus.clear_all()
        
        print("✅ Agent system initialized")
    
    async def _create_orchestrator_agent(self, repo_path: str, **kwargs) -> OrchestratorAgent:
        """
        创建编排Agent
        """
        print("🤖 Creating Orchestrator Agent...")
        
        # 初始化工具
        tools = {
            "pattern_match": PatternMatchTool(),
            "code_analysis": CodeAnalysisTool(llm_service),
            "data_flow_analysis": DataFlowAnalysisTool(llm_service),
            "vulnerability_validation": VulnerabilityValidationTool(llm_service),
            "file_read": FileReadTool(repo_path),
            "file_search": FileSearchTool(repo_path),
            "list_files": ListFilesTool(repo_path),
            "think": ThinkTool(),
            "reflect": ReflectTool(),
            "create_vulnerability_report": CreateVulnerabilityReportTool(),
            "finish_scan": FinishScanTool(),
            "smart_scan": SmartScanTool(repo_path),
            "quick_audit": QuickAuditTool(repo_path)
        }
        
        # 尝试添加RAG相关工具
        try:
            if rag_manager.code_retriever:
                tools.update({
                    "rag_query": RAGQueryTool(retriever=rag_manager.code_retriever),
                    "security_code_search": SecurityCodeSearchTool(retriever=rag_manager.code_retriever),
                    "function_context": FunctionContextTool(retriever=rag_manager.code_retriever)
                })
                print("✅ Added RAG tools")
            else:
                print("⚠️ RAG not available, skipping RAG tools")
        except Exception as e:
            print(f"⚠️ Failed to add RAG tools: {e}")
        
        # 如果启用了沙箱，添加沙箱工具
        if self.sandbox:
            try:
                tools.update({
                    "sandbox": SandboxTool(),
                    "sandbox_http": SandboxHttpTool(),
                    "vulnerability_verify": VulnerabilityVerifyTool()
                })
                print("✅ Added sandbox tools")
            except Exception as e:
                print(f"⚠️ Failed to add sandbox tools: {e}")
        
        # 初始化子Agent
        try:
            from src.audit.agent_system.agents.recon import ReconAgent
            from src.audit.agent_system.agents.analysis import AnalysisAgent
            from src.audit.agent_system.agents.verification import VerificationAgent
            
            # 创建子Agent
            recon_agent = ReconAgent(llm_service, tools)
            analysis_agent = AnalysisAgent(llm_service, tools)
            verification_agent = VerificationAgent(llm_service, tools)
            
            # 注册子Agent
            sub_agents = {
                "recon": recon_agent,
                "analysis": analysis_agent,
                "verification": verification_agent
            }
            
            print("✅ Added sub-agents: recon, analysis, verification")
        except Exception as e:
            print(f"⚠️ Failed to add sub-agents: {e}")
            sub_agents = {}
        
        # 创建编排Agent
        orchestrator = OrchestratorAgent(
            llm_service=llm_service,
            tools=tools,
            sub_agents=sub_agents
        )
        
        print("✅ Orchestrator Agent created")
        return orchestrator
    
    async def _verify_vulnerabilities(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        验证漏洞
        """
        print("🔍 Verifying vulnerabilities in sandbox...")
        
        verified_findings = []
        
        for i, finding in enumerate(findings, 1):
            print(f"📋 Verifying vulnerability {i}/{len(findings)}: {finding.get('title')}")
            
            try:
                verification_result = self.verifier.verify_vulnerability(finding)
                if verification_result['verified']:
                    finding['verified'] = True
                    finding['verification_details'] = verification_result
                    verified_findings.append(finding)
                    print("✅ Vulnerability verified")
                else:
                    print("❌ Vulnerability not verified")
            except Exception as e:
                print(f"⚠️ Error verifying vulnerability: {e}")
        
        return verified_findings
    
    async def _cleanup_agent_system(self):
        """
        清理Agent系统
        """
        print("🧹 Cleaning up Agent system...")
        
        # 清理Agent注册表
        agent_registry.clear()
        
        # 清理消息总线
        message_bus.clear_all()
        
        print("✅ Agent system cleaned up")
    
    def _generate_conclusion(self, findings: List[Dict[str, Any]]) -> str:
        """
        生成审计结论
        """
        if not findings:
            return "No issues found. The codebase appears to be well-maintained."
        
        severity_counts = {
            "high": len([f for f in findings if f.get('severity') == 'High']),
            "medium": len([f for f in findings if f.get('severity') == 'Medium']),
            "low": len([f for f in findings if f.get('severity') == 'Low'])
        }
        
        verified_count = len([f for f in findings if f.get('verified')])
        
        conclusion = f"Audit completed with {len(findings)} total issues found:\n"
        conclusion += f"- High severity: {severity_counts['high']}\n"
        conclusion += f"- Medium severity: {severity_counts['medium']}\n"
        conclusion += f"- Low severity: {severity_counts['low']}\n"
        conclusion += f"- Verified vulnerabilities: {verified_count}\n"
        conclusion += "\nRecommendations:\n"
        conclusion += "1. Address high severity issues immediately\n"
        conclusion += "2. Review medium severity issues in the next sprint\n"
        conclusion += "3. Implement code style guidelines to address low severity issues\n"
        conclusion += "4. Verify all high severity vulnerabilities in sandbox environment"
        
        return conclusion
    
    def audit_sync(self, repo_path: str, **kwargs) -> Dict[str, Any]:
        """
        同步执行审计（用于CLI模式）
        
        Args:
            repo_path: 仓库路径
            **kwargs: 额外参数
        
        Returns:
            审计结果
        """
        return asyncio.run(self.audit(repo_path, **kwargs))
    
    def _collect_files(self, repo_path: str) -> List[str]:
        """
        收集代码文件
        基于DeepAudit的文件收集逻辑
        """
        import os
        files = []
        
        # 支持的文件扩展名（与DeepAudit保持一致）
        supported_extensions = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rb", ".php",
            ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt", ".rs", ".scala",
            ".vue", ".svelte", ".html", ".css", ".scss", ".sass", ".less",
            ".json", ".yaml", ".yml", ".xml", ".toml", ".ini", ".conf",
            ".sql", ".graphql", ".proto", ".sh", ".bash", ".zsh", ".ps1",
            ".md", ".txt", ".rst", ".env.example", ".gitignore"
        }
        
        # 排除的目录（与DeepAudit保持一致）
        blocked_directories = {
            "node_modules", "__pycache__", ".git", ".svn", ".hg",
            "venv", ".venv", "env", ".env", "virtualenv",
            "dist", "build", "target", "out", "bin", "obj",
            ".idea", ".vscode", ".vs", ".pytest_cache", ".mypy_cache",
            "coverage", ".coverage", "htmlcov", ".tox", ".nox"
        }
        
        for root, dirs, filenames in os.walk(repo_path):
            # 过滤掉被阻止的目录
            dirs[:] = [d for d in dirs if d not in blocked_directories]
            
            for filename in filenames:
                if any(filename.endswith(ext) for ext in supported_extensions):
                    file_path = os.path.join(root, filename)
                    # 检查文件大小
                    if os.path.getsize(file_path) <= self.config.max_file_size_bytes:
                        files.append(file_path)
        
        return files
    
    def _should_exclude(self, path: str) -> bool:
        """
        检查是否应该排除该文件
        """
        blocked_directories = {
            "node_modules", "__pycache__", ".git", ".svn", ".hg",
            "venv", ".venv", "env", ".env", "virtualenv",
            "dist", "build", "target", "out", "bin", "obj",
            ".idea", ".vscode", ".vs", ".pytest_cache", ".mypy_cache",
            "coverage", ".coverage", "htmlcov", ".tox", ".nox"
        }
        
        return any(bd in path for bd in blocked_directories)
