"""
MCP 工具适配器
将现有的 Tool 系统集成到 MCP
"""
from typing import Any, Dict, List, Optional

from .protocol import MCPTool

***REMOVED*** 可选导入 Tool 系统
try:
    from tools import Tool, ToolRegistry
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False
    Tool = None
    ToolRegistry = None


class MCPToolAdapter:
    """
    MCP 工具适配器
    将 ToolRegistry 中的工具适配为 MCP 工具
    """
    
    def __init__(self, tool_registry: Optional[Any] = None):
        """
        初始化工具适配器
        
        Args:
            tool_registry: Tool 注册表（如果为 None，尝试导入默认注册表）
        """
        if not HAS_TOOLS:
            raise ImportError("Tool system not available. Install tools module first.")
        
        if tool_registry is None:
            from tools import default_registry
            tool_registry = default_registry
        
        self.tool_registry = tool_registry
    
    def to_mcp_tools(self) -> List[MCPTool]:
        """
        将注册表中的所有工具转换为 MCP 工具
        
        Returns:
            MCP 工具列表
        """
        mcp_tools = []
        
        for tool_name in self.tool_registry.list_tools():
            tool = self.tool_registry.get_tool(tool_name)
            if tool:
                mcp_tool = self._convert_tool(tool)
                mcp_tools.append(mcp_tool)
        
        return mcp_tools
    
    def _convert_tool(self, tool: Tool) -> MCPTool:
        """
        将 Tool 转换为 MCPTool
        
        Args:
            tool: Tool 实例
            
        Returns:
            MCPTool 实例
        """
        ***REMOVED*** 获取工具的函数定义
        schema = tool.get_function_schema()
        
        ***REMOVED*** 转换为 MCP 格式
        input_schema = {
            "type": "object",
            "properties": schema.get("parameters", {}).get("properties", {}),
            "required": schema.get("parameters", {}).get("required", [])
        }
        
        return MCPTool(
            name=tool.name,
            description=tool.description,
            inputSchema=input_schema
        )
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        调用工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            执行结果
        """
        return self.tool_registry.execute_tool(name, arguments)
