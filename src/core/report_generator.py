import os
import json
import io
import html
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys
import base64
from jinja2 import Template


class ReportGenerator:
    """
    报告生成器，支持多种格式的报告生成
    参考DeepAudit的实现
    """
    
    # --- HTML 模板 --- 参考DeepAudit
    _PDF_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>代码审计报告</title>
        <style>
            @page {
                size: A4;
                margin: 2.5cm 2cm;
                @top-left {
                    content: element(logoRunning);
                    vertical-align: middle;
                }
                @top-right {
                    content: "OpenRA Audit Report";
                    font-size: 8pt;
                    color: #666;
                    font-family: sans-serif;
                    vertical-align: middle;
                }
                @bottom-center {
                    content: counter(page);
                    font-size: 9pt;
                    font-family: serif;
                }
            }
            
            body {
                font-family: "Songti SC", "SimSun", "Times New Roman", serif;
                color: #000;
                line-height: 1.3;
                font-size: 10pt;
                margin: 0;
            }
            
            /* 页眉 Logo 定义 */
            .running-logo {
                position: running(logoRunning);
                height: 30px;
                width: auto;
                margin-bottom: 10px;
            }
            
            /* 头部 */
            .header {
                padding-bottom: 10px;
                display: table; 
                width: 100%;
            }
            
            .header-line {
                border-bottom: 2px solid #000;
                margin-bottom: 20px;
                margin-top: 5px;
            }
            
            .header-left {
                display: table-cell;
                vertical-align: middle;
            }
            
            .title-group {
                display: block;
                vertical-align: middle;
            }
            
            .title {
                font-size: 18pt;
                font-weight: bold;
                font-family: sans-serif;
                margin: 0 0 5px 0;
                color: #000;
                line-height: 1.1;
            }
            
            .subtitle {
                font-size: 10pt;
                color: #444;
                font-family: sans-serif;
                margin: 0;
                line-height: 1.3;
            }
            
            .meta-info {
                display: table-cell;
                text-align: right;
                vertical-align: middle;
                font-size: 9pt;
                color: #333;
                width: 250px;
            }
            
            .meta-item {
                margin-bottom: 2px;
            }
            
            /* 通用工具类 */
            .text-right { text-align: right; }
            .text-center { text-align: center; }
            .bold { font-weight: bold; }
            .mono { font-family: "Menlo", "Consolas", "Courier New", "PingFang SC", "Microsoft YaHei", monospace; }
            
            /* 概览表格 */
            .section-header {
                font-size: 11pt;
                font-weight: bold;
                font-family: sans-serif;
                border-left: 4px solid #000;
                padding-left: 8px;
                margin-top: 25px;
                margin-bottom: 10px;
                background-color: #f3f4f6;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            
            /* 评分栏 */
            .score-box {
                border: 1px solid #000;
                padding: 15px;
                margin-bottom: 20px;
                display: table;
                width: 100%;
                box-sizing: border-box;
            }
            
            .score-left {
                display: table-cell;
                vertical-align: middle;
                width: 40%;
            }
            
            .score-right {
                display: table-cell;
                vertical-align: middle;
                text-align: right;
                width: 60%;
            }
            
            .score-val {
                font-size: 24pt;
                font-weight: bold;
                font-family: sans-serif;
                line-height: 1;
            }
            
            /* 统计数据表格 */
            .stats-table {
                width: 100%;
                border-collapse: collapse;
            }
            
            .stats-table td {
                text-align: center;
                padding: 0 10px;
                border-left: 1px solid #ddd;
            }
            
            .stats-table td:first-child {
                border-left: none;
            }
            
            .stat-label {
                font-size: 8pt;
                color: #666;
                text-transform: uppercase;
                margin-bottom: 3px;
                display: block;
            }
            
            .stat-value {
                font-size: 11pt;
                font-weight: bold;
                display: block;
            }
            
            /* 问题列表 */
            .issue-item {
                border-bottom: 1px solid #e5e7eb;
                padding: 10px 0;
            }
            
            .issue-item:last-child {
                border-bottom: none;
            }
            
            .issue-title-row {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 6px;
            }
            
            .issue-title {
                font-size: 10.5pt;
                font-weight: bold;
                font-family: sans-serif;
                flex: 1;
                margin-right: 15px;
            }
            
            .issue-severity {
                font-size: 8.5pt;
                font-weight: bold;
                text-transform: uppercase;
                font-family: sans-serif;
                white-space: nowrap;
            }
            
            .issue-meta {
                font-size: 8pt;
                color: #555;
                margin-bottom: 6px;
                background: #f3f4f6;
                padding: 2px 6px;
                display: inline-block;
                border-radius: 2px;
                font-family: monospace;
            }
            
            .issue-desc {
                text-align: justify;
                margin-bottom: 8px;
                line-height: 1.4;
                font-size: 9.5pt;
            }
            
            /* 代码块 */
            .code-snippet {
                background-color: #f8f9fa;
                border: 1px solid #e5e7eb;
                border-left: 3px solid #333;
                color: #1f2937;
                padding: 8px;
                font-size: 8.5pt;
                line-height: 1.3;
                white-space: pre-wrap;
                word-break: break-all;
                margin: 8px 0;
                font-family: "Menlo", "Consolas", "Courier New", "PingFang SC", "Microsoft YaHei", monospace;
            }
            
            /* 建议 */
            .suggestion {
                margin-top: 6px;
                font-style: italic;
                color: #333;
                font-size: 9pt;
                line-height: 1.4;
            }
        </style>
    </head>
    <body>
        <!-- 定义页眉 Logo (Running Element) -->
        {% if logo_b64 %}
        <img src="data:image/png;base64,{{ logo_b64 }}" class="running-logo" alt="Logo"/>
        {% endif %}
        
        <div class="header">
            <div class="header-left">
                <div class="title-group">
                    <h1 class="title">{{ title }}</h1>
                    <div class="subtitle">{{ subtitle }}</div>
                </div>
            </div>
            <div class="meta-info">
                <div class="meta-item">报告编号: <span class="mono">{{ report_id }}</span></div>
                <div class="meta-item">生成时间: {{ generated_at }}</div>
            </div>
        </div>
        <div class="header-line"></div>
        
        <!-- 概览区域 -->
        <div class="score-box">
            <div class="score-left">
                <span style="font-size: 10pt; font-weight: bold; margin-right: 10px; vertical-align: middle;">代码质量评分</span>
                <span class="score-val" style="vertical-align: middle;">{{ score|int }}</span>
                <span style="font-size: 10pt; color: #666; margin-left: 5px; vertical-align: middle;">/ 100</span>
            </div>
            <div class="score-right">
                <table class="stats-table">
                    <tr>
                        {% for label, value in stats %}
                        <td>
                            <span class="stat-label">{{ label }}</span>
                            <span class="stat-value">{{ value }}</span>
                        </td>
                        {% endfor %}
                    </tr>
                </table>
            </div>
        </div>
        
        <!-- 问题详情 -->
        {% if issues %}
        <div class="section-header">审计发现明细 ({{ issues|length }})</div>
        
        <div class="issue-list">
            {% for issue in issues %}
            <div class="issue-item">
                <div class="issue-title-row">
                    <div class="issue-title">{{ loop.index }}. {{ issue.title }}</div>
                    <div class="issue-severity">{{ issue.severity_label }}</div>
                </div>
                
                {% if issue.location %}
                <div class="issue-meta mono">
                    {{ issue.location }}
                </div>
                {% endif %}
                
                {% if issue.description %}
                <div class="issue-desc">{{ issue.description }}</div>
                {% endif %}
                
                {% if issue.code_snippet %}
                <div class="code-snippet mono">{{ issue.code_snippet }}</div>
                {% endif %}
                
                {% if issue.suggestion %}
                <div class="suggestion">
                    <strong>建议:</strong> {{ issue.suggestion }}
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% else %}
        <div style="padding: 20px; text-align: center; border: 1px dashed #ccc; margin-top: 20px;">
            <strong>未发现代码问题</strong>
            <p style="font-size: 9pt; color: #666; margin-top: 5px;">本次扫描未发现任何违规或潜在风险，代码质量符合标准。</p>
        </div>
        {% endif %}
        
        <!-- 页脚声明 -->
        <div style="margin-top: 40px; font-size: 8pt; color: #999; text-align: center; border-top: 1px solid #eee; padding-top: 10px;">
            本报告由 OpenRA 自动生成，注意核实鉴别。
        </div>
    </body>
    </html>
    """
    
    def __init__(self):
        pass
    
    def _get_logo_base64(self) -> str:
        """读取并编码 Logo 图片"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 尝试多个可能的路径
            possible_paths = [
                # 本地开发路径
                os.path.abspath(os.path.join(current_dir, '../../DeepAudit/frontend/public/images/logo_nobg.png')),
            ]
            
            for logo_path in possible_paths:
                if os.path.exists(logo_path):
                    with open(logo_path, "rb") as image_file:
                        return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error loading logo: {e}")
            return ""
        return ""

    def _escape_html(self, text: str) -> str:
        """安全转义 HTML 特殊字符"""
        if text is None:
            return None
        return html.escape(str(text))

    def _process_issues(self, findings: List[Dict]) -> List[Dict]:
        """处理问题列表"""
        processed = []
        order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_issues = sorted(findings, key=lambda x: order.get(x.get('severity', 'low'), 4))

        sev_labels = {
            'critical': 'CRITICAL',
            'high': 'HIGH',
            'medium': 'MEDIUM',
            'low': 'LOW'
        }

        for i in sorted_issues:
            item = i.copy()
            item['severity'] = item.get('severity', 'low')
            item['severity_label'] = sev_labels.get(item['severity'], 'UNKNOWN')
            item['location'] = item.get('location') or item.get('file_path')

            # 确保代码片段存在
            code = item.get('code_snippet') or item.get('code') or item.get('context')
            if isinstance(code, list):
                code = '\n'.join(code)
            item['code_snippet'] = self._escape_html(code) if code else None

            # 确保 description 不为 None
            desc = item.get('description')
            if not desc or desc == 'None':
                desc = item.get('title', '')  # 如果没有描述，使用标题
            item['description'] = self._escape_html(desc)

            # 确保 suggestion 不为 None
            suggestion = item.get('suggestion') or item.get('recommendation')
            if suggestion == 'None' or suggestion is None:
                item['suggestion'] = None
            else:
                item['suggestion'] = self._escape_html(suggestion)

            # 转义标题和位置
            item['title'] = self._escape_html(item.get('title', ''))
            item['location'] = self._escape_html(item.get('location'))

            processed.append(item)
        return processed

    def generate_markdown_report(self, data: Dict[str, Any], report_type: str) -> str:
        """
        生成markdown格式报告
        """
        # 使用中文标题
        report = f"# {report_type.capitalize()} 报告\n\n"
        report += f"## 摘要\n"
        report += f"- **项目**: {data.get('project', 'N/A')}\n"
        report += f"- **日期**: {data.get('date', 'N/A')}\n"
        report += f"- **耗时**: {data.get('duration', 'N/A')}\n"
        report += f"- **评分**: {data.get('score', 'N/A')}/100\n"
        
        # 获取并去重问题列表
        findings = data.get('findings', [])
        # 基于标题去重
        unique_findings = []
        seen_titles = set()
        for finding in findings:
            title = finding.get('title', 'Untitled')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_findings.append(finding)
        
        report += f"- **发现问题**: {len(unique_findings)}\n\n"
        
        if unique_findings:
            report += "## 发现问题\n"
            for i, finding in enumerate(unique_findings, 1):
                report += f"### {i}. {finding.get('title', 'Untitled')}\n"
                report += f"- **严重性**: {finding.get('severity', 'N/A')}\n"
                report += f"- **类别**: {finding.get('category', 'N/A')}\n"
                # 确保位置信息正确显示
                location = finding.get('location', finding.get('file', 'N/A'))
                report += f"- **位置**: {location}\n"
                report += f"- **描述**: {finding.get('description', 'N/A')}\n"
                # 确保代码片段有实际内容
                code_snippet = finding.get('code_snippet', finding.get('code', ''))
                if code_snippet:
                    report += f"- **代码片段**:\n```\n{code_snippet}\n```\n"
                if 'recommendation' in finding:
                    report += f"- **建议**: {finding['recommendation']}\n"
                if 'suggestion' in finding:
                    report += f"- **建议**: {finding['suggestion']}\n"
                report += "\n"
        
        # 生成结论，确保统计正确
        report += "## 结论\n"
        
        # 总是使用中文结论，忽略data中的conclusion
        if not unique_findings:
            # 没有发现问题时使用中文
            report += "未发现任何问题。代码库维护良好。\n"
        else:
            # 统计各严重性级别的问题数
            severity_counts = {
                "high": 0,
                "medium": 0,
                "low": 0
            }
            for finding in unique_findings:
                severity = finding.get('severity', 'low').lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
                elif 'high' in severity:
                    severity_counts['high'] += 1
                elif 'medium' in severity:
                    severity_counts['medium'] += 1
                elif 'low' in severity:
                    severity_counts['low'] += 1
            
            report += f"审计完成，共发现 {len(unique_findings)} 个问题:\n"
            report += f"- 高严重性: {severity_counts['high']}\n"
            report += f"- 中严重性: {severity_counts['medium']}\n"
            report += f"- 低严重性: {severity_counts['low']}\n\n"
            report += "建议:\n"
            report += "1. 立即处理高严重性问题\n"
            report += "2. 在下次迭代中处理中严重性问题\n"
            report += "3. 实施代码风格指南以解决低严重性问题\n"
            report += "4. 在沙箱环境中验证所有高严重性漏洞\n"
        
        return report
    
    def generate_json_report(self, data: Dict[str, Any]) -> str:
        """
        生成JSON格式报告
        """
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def generate_pdf_report(self, data: Dict[str, Any], report_type: str) -> Optional[str]:
        """
        生成PDF格式报告
        
        Args:
            data: 报告数据
            report_type: 报告类型
            
        Returns:
            str: PDF文件路径
        """
        try:
            # 尝试导入 WeasyPrint
            from weasyprint import HTML, CSS
            from weasyprint.text.fonts import FontConfiguration
            
            # 准备数据
            score = data.get('score', 0)
            findings = data.get('findings', [])
            project = data.get('project', 'N/A')
            duration = data.get('duration', 'N/A')
            
            # 处理问题列表
            issues = self._process_issues(findings)
            
            # 准备统计数据
            stats = [
                ('问题总数', len(issues)),
                ('耗时', f"{duration}s" if isinstance(duration, (int, float)) else duration),
                ('项目', project)
            ]
            
            # 准备上下文
            context = {
                'title': f"{report_type.capitalize()} 报告",
                'subtitle': f"项目: {project}",
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'report_id': f"OPENRA-{int(datetime.now().timestamp())}",
                'score': score,
                'stats': stats,
                'issues': issues,
                'logo_b64': self._get_logo_base64()
            }
            
            # 渲染模板
            template = Template(self._PDF_TEMPLATE)
            html_content = template.render(**context)
            
            # 生成PDF
            font_config = FontConfiguration()
            temp_pdf = os.path.join(os.getcwd(), f"report_{report_type}.pdf")
            
            HTML(string=html_content).write_pdf(
                temp_pdf,
                font_config=font_config,
                presentational_hints=True
            )
            
            return temp_pdf
        except ImportError:
            print("PDF generation requires weasyprint. Please install it.")
            return None
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def save_report(self, content: str, report_type: str, format: str, output_dir=None) -> str:
        """
        保存报告到文件
        
        Args:
            content: 报告内容
            report_type: 报告类型
            format: 报告格式
            output_dir: 输出目录，默认当前目录
            
        Returns:
            str: 保存的文件路径
        """
        filename = f"report_{report_type}.{format}"
        filepath = os.path.join(output_dir or os.getcwd(), filename)
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
