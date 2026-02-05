"""
工具动态发现系统
实现 Cursor 风格的 Index Layer + Discovery Layer 架构

核心思想：
- Index Layer: 系统提示词中只包含工具名称列表（轻量级）
- Discovery Layer: 详细描述同步到文件，Agent 按需查找
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Any
from .base import ToolRegistry, Tool


class ToolDiscovery:
    """
    工具发现系统
    实现 Index Layer + Discovery Layer 架构
    """
    
    def __init__(self, registry: ToolRegistry, docs_dir: Optional[Path] = None):
        """
        初始化工具发现系统
        
        Args:
            registry: 工具注册表
            docs_dir: 工具文档目录，默认为 tools/docs/
        """
        self.registry = registry
        if docs_dir is None:
            # 默认使用 tools/docs/ 目录
            current_dir = Path(__file__).parent
            docs_dir = current_dir / "docs"
        self.docs_dir = Path(docs_dir)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        # 同步工具文档
        self.sync_tool_docs()
    
    def sync_tool_docs(self) -> None:
        """
        同步所有工具的详细定义到文档目录
        每个工具一个 Markdown 文件
        """
        tools = self.registry.get_all_functions()
        
        for tool_def in tools:
            func = tool_def.get("function", {})
            tool_name = func.get("name", "")
            if not tool_name:
                continue
            
            # 生成工具文档
            doc_content = self._generate_tool_doc(func)
            
            # 保存到文件
            doc_file = self.docs_dir / f"{tool_name}.md"
            doc_file.write_text(doc_content, encoding="utf-8")
    
    def _generate_tool_doc(self, func: Dict[str, Any]) -> str:
        """
        生成工具的 Markdown 文档
        
        Args:
            func: 工具函数定义
            
        Returns:
            Markdown 格式的文档内容
        """
        name = func.get("name", "")
        description = func.get("description", "")
        parameters = func.get("parameters", {}).get("properties", {})
        required = func.get("parameters", {}).get("required", [])
        
        doc_lines = [
            f"# {name}",
            "",
            f"**描述**: {description}",
            "",
            "## 参数",
            ""
        ]
        
        if parameters:
            for param_name, param_def in parameters.items():
                param_type = param_def.get("type", "string")
                param_desc = param_def.get("description", "")
                is_required = param_name in required
                required_mark = "（必需）" if is_required else "（可选）"
                
                doc_lines.append(f"- `{param_name}` ({param_type}){required_mark}: {param_desc}")
        else:
            doc_lines.append("无参数")
        
        doc_lines.extend([
            "",
            "## 使用示例",
            ""
        ])
        
        # 生成示例参数
        example_args = {}
        for param_name, param_def in parameters.items():
            param_type = param_def.get("type", "string")
            if param_type == "string":
                example_args[param_name] = "示例值"
            elif param_type == "number":
                example_args[param_name] = 0
            elif param_type == "boolean":
                example_args[param_name] = True
            elif param_type == "array":
                example_args[param_name] = []
            elif param_type == "object":
                example_args[param_name] = {}
        
        if example_args:
            example_json = json.dumps(example_args, ensure_ascii=False, indent=2)
            doc_lines.extend([
                "```json",
                example_json,
                "```",
                ""
            ])
        else:
            doc_lines.extend([
                "```json",
                "{}",
                "```",
                ""
            ])
        
        return "\n".join(doc_lines)
    
    def get_index_layer(self) -> str:
        """
        获取 Index Layer 内容（轻量级工具名称列表）
        用于系统提示词
        
        Returns:
            工具名称列表的文本描述
        """
        tool_names = self.registry.list_tools()
        
        if not tool_names:
            return "没有可用的工具。"
        
        lines = [
            "可用工具列表：",
            ""
        ]
        
        for name in tool_names:
            # 获取工具的简短描述（从注册表中）
            tool = self.registry.get_tool(name)
            if tool:
                short_desc = tool.description[:50]  # 只取前50字符
                lines.append(f"- {name}: {short_desc}...")
            else:
                lines.append(f"- {name}")
        
        lines.extend([
            "",
            "注意：如需查看工具的详细描述、参数定义和使用方法，请使用 `search_tool_docs` 工具搜索工具文档。"
        ])
        
        return "\n".join(lines)
    
    def search_tool_docs(self, query: str, max_results: int = 5) -> str:
        """
        在工具文档中搜索（模拟 grep 或语义搜索）
        
        Args:
            query: 搜索查询
            max_results: 最多返回的结果数
            
        Returns:
            搜索结果
        """
        query_lower = query.lower()
        results = []
        
        # 遍历所有工具文档
        for doc_file in self.docs_dir.glob("*.md"):
            tool_name = doc_file.stem
            content = doc_file.read_text(encoding="utf-8")
            content_lower = content.lower()
            
            # 简单的关键词匹配
            score = 0
            matched_lines = []
            
            # 检查工具名称
            if query_lower in tool_name.lower():
                score += 10
                matched_lines.append(f"工具名称: {tool_name}")
            
            # 检查描述
            if query_lower in content_lower:
                # 找到匹配的行
                for line in content.split("\n"):
                    if query_lower in line.lower():
                        matched_lines.append(line.strip())
                        score += 1
                        if len(matched_lines) >= 3:  # 最多3行
                            break
            
            if score > 0:
                results.append({
                    "tool_name": tool_name,
                    "score": score,
                    "matched_lines": matched_lines[:3],
                    "file_path": str(doc_file)
                })
        
        # 按分数排序
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:max_results]
        
        if not results:
            return f"未找到与 '{query}' 相关的工具文档。"
        
        # 格式化结果
        output_lines = [
            f"找到 {len(results)} 个相关工具：",
            ""
        ]
        
        for i, result in enumerate(results, 1):
            output_lines.append(f"### {i}. {result['tool_name']}")
            output_lines.append(f"文件路径: {result['file_path']}")
            output_lines.append("匹配内容:")
            for line in result['matched_lines']:
                output_lines.append(f"  - {line}")
            output_lines.append("")
        
        output_lines.append("提示：可以使用 `read_file` 工具读取完整的工具文档。")
        
        return "\n".join(output_lines)
    
    def get_tool_doc(self, tool_name: str) -> Optional[str]:
        """
        获取指定工具的完整文档
        
        Args:
            tool_name: 工具名称
            
        Returns:
            工具文档内容，如果不存在返回 None
        """
        doc_file = self.docs_dir / f"{tool_name}.md"
        if doc_file.exists():
            return doc_file.read_text(encoding="utf-8")
        return None
    
    def list_tool_docs(self) -> List[str]:
        """
        列出所有工具文档
        
        Returns:
            工具名称列表
        """
        return [f.stem for f in self.docs_dir.glob("*.md")]


# 全局工具发现实例（延迟初始化）
_discovery_instance: Optional[ToolDiscovery] = None


def get_discovery(registry: Optional[ToolRegistry] = None) -> ToolDiscovery:
    """
    获取全局工具发现实例
    
    Args:
        registry: 工具注册表，如果为 None 则使用 default_registry
        
    Returns:
        ToolDiscovery 实例
    """
    global _discovery_instance
    
    if _discovery_instance is None:
        from . import default_registry
        _discovery_instance = ToolDiscovery(registry or default_registry)
    
    return _discovery_instance
