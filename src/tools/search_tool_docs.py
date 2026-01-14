"""
搜索工具文档的工具
让 Agent 可以主动查找工具文档
"""
from typing import Any, Dict
from .base import Tool
from .discovery import get_discovery


class SearchToolDocsTool(Tool):
    """
    搜索工具文档的工具
    让 Agent 可以主动查找工具文档（Discovery Layer）
    """
    
    def __init__(self):
        super().__init__(
            name="search_tool_docs",
            description="在工具文档中搜索相关工具。当需要了解工具的详细使用方法时，使用此工具搜索。"
        )
    
    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "search_tool_docs",
                "description": "在工具文档中搜索相关工具。当需要了解工具的详细描述、参数定义和使用方法时，使用此工具搜索工具文档。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "搜索查询，可以是工具名称、功能描述或关键词"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "最多返回的结果数，默认5",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """验证参数"""
        if "query" not in arguments:
            return False
        query = str(arguments.get("query", "")).strip()
        return len(query) > 0
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        """执行搜索"""
        query = str(arguments.get("query", "")).strip()
        max_results = arguments.get("max_results", 5)
        
        discovery = get_discovery()
        return discovery.search_tool_docs(query, max_results=max_results)


class ReadToolDocTool(Tool):
    """
    读取工具文档的工具
    让 Agent 可以读取完整的工具文档
    """
    
    def __init__(self):
        super().__init__(
            name="read_tool_doc",
            description="读取指定工具的完整文档。当需要了解工具的详细使用方法时，使用此工具读取完整文档。"
        )
    
    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "read_tool_doc",
                "description": "读取指定工具的完整文档。当需要了解工具的详细描述、参数定义和使用方法时，使用此工具读取完整文档。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool_name": {
                            "type": "string",
                            "description": "工具名称，例如：calculator、get_weather"
                        }
                    },
                    "required": ["tool_name"]
                }
            }
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """验证参数"""
        if "tool_name" not in arguments:
            return False
        tool_name = str(arguments.get("tool_name", "")).strip()
        return len(tool_name) > 0
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        """读取文档"""
        tool_name = str(arguments.get("tool_name", "")).strip()
        
        discovery = get_discovery()
        doc_content = discovery.get_tool_doc(tool_name)
        
        if doc_content:
            return f"工具文档：{tool_name}\n\n{doc_content}"
        else:
            available_docs = discovery.list_tool_docs()
            return f"未找到工具 '{tool_name}' 的文档。\n可用工具: {', '.join(available_docs)}"
