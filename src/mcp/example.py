"""
MCP 使用示例
演示如何使用 MCP 系统
"""
import sys
from pathlib import Path
from typing import List, Dict, Any

***REMOVED*** 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp import MCPManager, default_manager
from mcp.resource import MemoryResourceProvider, FileSystemResourceProvider
from mcp.server import MCPServer
from mcp.protocol import MCPTool, MCPResource
from mcp.tool_adapter import MCPToolAdapter

***REMOVED*** 可选导入 Tool 系统
try:
    from tools import default_registry
    HAS_TOOLS = True
except ImportError:
    HAS_TOOLS = False
    default_registry = None


class ExampleMCPServer(MCPServer):
    """
    示例 MCP 服务器
    集成工具和文件系统资源
    """
    
    def __init__(self, resource_base_path: Path):
        """
        初始化示例服务器
        
        Args:
            resource_base_path: 资源文件的基础路径
        """
        super().__init__(name="example-mcp-server", version="1.0.0")
        
        ***REMOVED*** 工具适配器（集成现有的 Tool 系统）
        if HAS_TOOLS and default_registry:
            self.tool_adapter = MCPToolAdapter(default_registry)
        else:
            self.tool_adapter = None
        
        ***REMOVED*** 资源提供者（文件系统）
        self.resource_provider = FileSystemResourceProvider(
            resource_base_path,
            uri_prefix="file://"
        )
    
    def list_tools(self) -> List[MCPTool]:
        """列出所有工具"""
        if self.tool_adapter:
            return self.tool_adapter.to_mcp_tools()
        return []
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具"""
        if self.tool_adapter:
            return self.tool_adapter.call_tool(name, arguments)
        raise ValueError(f"Tool system not available. Cannot call tool: {name}")
    
    def list_resources(self) -> List[MCPResource]:
        """列出所有资源"""
        return self.resource_provider.list_resources()
    
    def read_resource(self, uri: str) -> str:
        """读取资源"""
        return self.resource_provider.get_resource(uri)


def example_basic_usage():
    """基本使用示例"""
    print("=" * 50)
    print("MCP 基本使用示例")
    print("=" * 50)
    
    ***REMOVED*** 创建 MCP 管理器
    manager = MCPManager()
    
    ***REMOVED*** 创建并注册服务器
    resource_path = Path(__file__).parent.parent / "skills"
    server = ExampleMCPServer(resource_path)
    manager.register_server("example", server)
    
    print(f"\n✓ 已注册服务器: {manager.list_servers()}")
    
    ***REMOVED*** 获取所有工具
    print("\n所有服务器的工具:")
    all_tools = manager.get_all_tools()
    for server_name, tools in all_tools.items():
        print(f"\n  {server_name}:")
        for tool in tools:
            print(f"    - {tool.name}: {tool.description}")
    
    ***REMOVED*** 调用工具
    print("\n调用工具示例:")
    try:
        result = manager.call_tool("example", "calculator", {"expression": "10 * 5"})
        print(f"  计算器 (10 * 5): {result}")
    except Exception as e:
        print(f"  错误: {e}")
    
    ***REMOVED*** 获取资源
    print("\n可用资源:")
    all_resources = manager.get_all_resources()
    for server_name, resources in all_resources.items():
        print(f"\n  {server_name}: {len(resources)} 个资源")
        for resource in resources[:3]:  ***REMOVED*** 只显示前3个
            print(f"    - {resource.name} ({resource.uri})")
    
    ***REMOVED*** 读取资源示例
    if all_resources.get("example"):
        first_resource = all_resources["example"][0]
        print(f"\n读取资源示例: {first_resource.name}")
        try:
            content = manager.read_resource("example", first_resource.uri)
            print(f"  内容预览: {content[:100]}...")
        except Exception as e:
            print(f"  错误: {e}")


def example_find_tool():
    """查找工具示例"""
    print("\n" + "=" * 50)
    print("查找工具示例")
    print("=" * 50)
    
    ***REMOVED*** 创建新的管理器实例（因为 default_manager 可能还没有注册服务器）
    manager = MCPManager()
    resource_path = Path(__file__).parent.parent / "skills"
    server = ExampleMCPServer(resource_path)
    manager.register_server("example", server)
    
    ***REMOVED*** 查找工具
    tool_info = manager.find_tool("calculator")
    if tool_info:
        server_name, tool = tool_info
        print(f"✓ 找到工具 '{tool.name}' 在服务器 '{server_name}'")
        print(f"  描述: {tool.description}")
    else:
        print("✗ 未找到工具 'calculator'")


def example_custom_server():
    """自定义服务器示例"""
    print("\n" + "=" * 50)
    print("自定义服务器示例")
    print("=" * 50)
    
    from mcp.server import MCPServer
    from mcp.protocol import MCPTool, MCPResource
    
    class CustomServer(MCPServer):
        """自定义服务器"""
        
        def list_tools(self) -> List[MCPTool]:
            return [
                MCPTool(
                    name="greet",
                    description="打招呼工具",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "要打招呼的人的名字"
                            }
                        },
                        "required": ["name"]
                    }
                )
            ]
        
        def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
            if name == "greet":
                name = arguments.get("name", "World")
                return f"Hello, {name}!"
            raise ValueError(f"Unknown tool: {name}")
        
        def list_resources(self) -> List[MCPResource]:
            return []
        
        def read_resource(self, uri: str) -> str:
            raise FileNotFoundError(f"Resource not found: {uri}")
    
    ***REMOVED*** 使用自定义服务器
    custom_server = CustomServer("custom-server", "1.0.0")
    manager = MCPManager()
    manager.register_server("custom", custom_server)
    
    ***REMOVED*** 调用自定义工具
    result = manager.call_tool("custom", "greet", {"name": "MCP"})
    print(f"自定义工具结果: {result}")


if __name__ == "__main__":
    example_basic_usage()
    example_find_tool()
    example_custom_server()
    
    print("\n" + "=" * 50)
    print("✓ 所有示例完成")
    print("=" * 50)
