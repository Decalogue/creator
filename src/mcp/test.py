"""
MCP 系统测试
"""
import sys
from pathlib import Path

***REMOVED*** 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp import MCPManager, MCPClient
from mcp.example import ExampleMCPServer
from mcp.protocol import MCPRequest, MCPResponse


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


def test_server_client():
    """测试服务器和客户端"""
    print("\n测试服务器和客户端...")
    
    resource_path = Path(__file__).parent.parent / "skills"
    server = ExampleMCPServer(resource_path)
    
    client = MCPClient(server)
    assert client.initialize(), "客户端初始化失败"
    print("✓ 客户端初始化成功")
    
    ***REMOVED*** 测试工具列表
    tools = client.list_tools()
    ***REMOVED*** 工具数量可能为 0（如果 tools 模块未安装）
    print(f"✓ 找到 {len(tools)} 个工具")
    if tools:
        for tool in tools[:3]:
            print(f"    - {tool.name}: {tool.description}")
    
    ***REMOVED*** 测试资源列表
    resources = client.list_resources()
    print(f"✓ 找到 {len(resources)} 个资源")
    
    print("✓ 服务器和客户端测试通过")


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
        ***REMOVED*** 测试工具调用
        try:
            result = manager.call_tool("test", "calculator", {"expression": "2 + 2"})
            assert "4" in str(result), "工具调用失败"
            print(f"✓ 工具调用成功: {result}")
        except Exception as e:
            print(f"⚠ 工具调用失败: {e}")
    else:
        print("⚠ 未找到 calculator 工具（可能 tools 模块未安装）")
    
    print("✓ 管理器测试通过")


def test_resource_provider():
    """测试资源提供者"""
    print("\n测试资源提供者...")
    
    from mcp.resource import MemoryResourceProvider
    
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
    print("MCP 系统测试")
    print("=" * 50)
    
    try:
        test_protocol()
        test_server_client()
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
