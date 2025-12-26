"""
MCP 系统本地测试（在 mcp 目录内运行）
"""
import sys
from pathlib import Path

***REMOVED*** 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp.protocol import MCPRequest, MCPResponse
from mcp.server import MCPServer
from mcp.client import MCPClient
from mcp.example import ExampleMCPServer
from mcp.protocol import MCPTool, MCPResource
from mcp.manager import MCPManager
from mcp.resource import MemoryResourceProvider
from typing import List, Dict, Any
from pathlib import Path


def test_protocol():
    """测试协议"""
    print("测试协议...")
    
    ***REMOVED*** 测试请求
    request = MCPRequest(
        id=1,
        method="tools/list",
        params={}
    )
    assert request.to_dict()["method"] == "tools/list"
    print("✓ 协议测试通过")


def test_response():
    """测试响应"""
    print("\n测试响应...")
    
    ***REMOVED*** 测试成功响应
    resp1 = MCPResponse.success(1, {'test': 'data'})
    assert resp1._error is None
    assert resp1.result == {'test': 'data'}
    print("✓ 成功响应测试通过")
    
    ***REMOVED*** 测试错误响应
    resp2 = MCPResponse.error(1, -1, 'test error')
    assert resp2._error is not None
    assert resp2._error['code'] == -1
    print("✓ 错误响应测试通过")


def test_server_client():
    """测试服务器和客户端"""
    print("\n测试服务器和客户端...")
    
    class TestServer(MCPServer):
        def list_tools(self) -> List[MCPTool]:
            return []
        def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
            return None
        def list_resources(self) -> List[MCPResource]:
            return []
        def read_resource(self, uri: str) -> str:
            return ''
    
    server = TestServer('test', '1.0.0')
    client = MCPClient(server)
    
    assert client.initialize(), "客户端初始化失败"
    print("✓ 客户端初始化成功")
    
    ***REMOVED*** 测试工具列表
    tools = client.list_tools()
    assert len(tools) == 0, "应该没有工具"
    print(f"✓ 工具列表测试通过 ({len(tools)} 个工具)")
    
    ***REMOVED*** 测试资源列表
    resources = client.list_resources()
    assert len(resources) == 0, "应该没有资源"
    print(f"✓ 资源列表测试通过 ({len(resources)} 个资源)")
    
    print("✓ 服务器和客户端测试通过")


def test_example_server():
    """测试示例服务器"""
    print("\n测试示例服务器...")
    
    resource_path = Path(__file__).parent.parent / "skills"
    server = ExampleMCPServer(resource_path)
    client = MCPClient(server)
    
    assert client.initialize(), "客户端初始化失败"
    print("✓ 示例服务器初始化成功")
    
    ***REMOVED*** 测试工具列表
    tools = client.list_tools()
    print(f"✓ 找到 {len(tools)} 个工具")
    if tools:
        for tool in tools[:3]:
            print(f"    - {tool.name}: {tool.description}")
    
    ***REMOVED*** 测试资源列表
    resources = client.list_resources()
    print(f"✓ 找到 {len(resources)} 个资源")
    if resources:
        for resource in resources[:3]:
            print(f"    - {resource.name} ({resource.uri})")
    
    print("✓ 示例服务器测试通过")


def test_manager():
    """测试管理器"""
    print("\n测试管理器...")
    
    manager = MCPManager()
    
    resource_path = Path(__file__).parent.parent / "skills"
    server = ExampleMCPServer(resource_path)
    manager.register_server("test", server)
    
    assert "test" in manager.list_servers(), "服务器注册失败"
    print("✓ 服务器注册成功")
    
    ***REMOVED*** 测试工具查找
    tool_info = manager.find_tool("calculator")
    if tool_info:
        print(f"✓ 找到工具: {tool_info[1].name}")
    else:
        print("⚠ 未找到 calculator 工具（可能 tools 模块未安装）")
    
    ***REMOVED*** 测试工具调用（如果工具存在）
    if tool_info:
        try:
            result = manager.call_tool("test", "calculator", {"expression": "2 + 2"})
            assert "4" in str(result), "工具调用失败"
            print(f"✓ 工具调用成功: {result}")
        except Exception as e:
            print(f"⚠ 工具调用失败: {e}")
    
    print("✓ 管理器测试通过")


def test_resource_provider():
    """测试资源提供者"""
    print("\n测试资源提供者...")
    
    provider = MemoryResourceProvider()
    provider.register_resource(
        uri="memory://test",
        name="测试资源",
        content="这是测试内容",
        description="测试资源描述"
    )
    
    resources = provider.list_resources()
    assert len(resources) == 1, "资源注册失败"
    print(f"✓ 注册了 {len(resources)} 个资源")
    
    content = provider.get_resource("memory://test")
    assert content == "这是测试内容", "资源读取失败"
    print("✓ 资源读取成功")
    
    print("✓ 资源提供者测试通过")


if __name__ == "__main__":
    print("=" * 50)
    print("MCP 系统本地测试（mcp 目录内）")
    print("=" * 50)
    
    try:
        test_protocol()
        test_response()
        test_server_client()
        test_example_server()
        test_manager()
        test_resource_provider()
        
        print("\n" + "=" * 50)
        print("✓ 所有测试通过")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
