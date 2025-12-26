***REMOVED*** MCP (Model Context Protocol) 系统

***REMOVED******REMOVED*** 简介

MCP (Model Context Protocol) 是一个开放标准，用于连接大型语言模型（LLM）与外部工具、数据源和服务。本实现提供了完整的 MCP 架构，类似于 `skills` 和 `tools` 系统。

**核心特点**：
- **标准化协议**：基于 JSON-RPC 2.0 的 MCP 协议
- **服务器-客户端架构**：清晰的职责分离
- **工具集成**：无缝集成现有的 Tool 系统
- **资源管理**：支持文件系统和内存资源
- **统一管理**：MCPManager 管理多个服务器

***REMOVED******REMOVED*** 核心概念

***REMOVED******REMOVED******REMOVED*** 架构组件

1. **MCPServer**：MCP 服务器，提供工具、资源和提示
2. **MCPClient**：MCP 客户端，连接和管理与服务器的通信
3. **MCPManager**：管理器，统一管理多个服务器
4. **MCPResourceProvider**：资源提供者，管理资源访问

***REMOVED******REMOVED******REMOVED*** 协议层

- **MCPRequest**：请求对象
- **MCPResponse**：响应对象
- **MCPTool**：工具定义
- **MCPResource**：资源定义
- **MCPPrompt**：提示定义

***REMOVED******REMOVED*** 目录结构

```
mcp/
├── __init__.py              ***REMOVED*** 模块导出
├── protocol.py              ***REMOVED*** MCP 协议定义
├── server.py                ***REMOVED*** MCP 服务器基类
├── client.py                ***REMOVED*** MCP 客户端
├── manager.py               ***REMOVED*** MCP 管理器
├── resource.py              ***REMOVED*** 资源管理
├── tool_adapter.py          ***REMOVED*** 工具适配器
├── example.py               ***REMOVED*** 使用示例（包含 ExampleMCPServer）
├── test.py                  ***REMOVED*** 测试代码
└── README.md                ***REMOVED*** 本文档
```

***REMOVED******REMOVED*** 快速开始

***REMOVED******REMOVED******REMOVED*** 1. 基本使用

```python
from mcp import MCPManager
from mcp.example import ExampleMCPServer
from pathlib import Path

***REMOVED*** 创建管理器
manager = MCPManager()

***REMOVED*** 创建并注册服务器
resource_path = Path("path/to/resources")
server = ExampleMCPServer(resource_path)
manager.register_server("example", server)

***REMOVED*** 列出所有工具
all_tools = manager.get_all_tools()
for server_name, tools in all_tools.items():
    print(f"{server_name}: {len(tools)} 个工具")

***REMOVED*** 调用工具
result = manager.call_tool("example", "calculator", {"expression": "2 + 2"})
print(f"结果: {result}")
```

***REMOVED******REMOVED******REMOVED*** 2. 创建自定义服务器

```python
from mcp.server import MCPServer
from mcp.protocol import MCPTool, MCPResource
from typing import List, Dict, Any

class MyServer(MCPServer):
    """自定义 MCP 服务器"""
    
    def list_tools(self) -> List[MCPTool]:
        return [
            MCPTool(
                name="my_tool",
                description="我的工具",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "param": {"type": "string"}
                    }
                }
            )
        ]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        if name == "my_tool":
            return f"处理: {arguments.get('param')}"
        raise ValueError(f"Unknown tool: {name}")
    
    def list_resources(self) -> List[MCPResource]:
        return []
    
    def read_resource(self, uri: str) -> str:
        raise FileNotFoundError(f"Resource not found: {uri}")
```

***REMOVED******REMOVED******REMOVED*** 3. 使用资源提供者

```python
from mcp.resource import FileSystemResourceProvider, MemoryResourceProvider
from pathlib import Path

***REMOVED*** 文件系统资源
fs_provider = FileSystemResourceProvider(
    base_path=Path("/path/to/resources"),
    uri_prefix="file://"
)

***REMOVED*** 内存资源
memory_provider = MemoryResourceProvider()
memory_provider.register_resource(
    uri="memory://data",
    name="数据",
    content="资源内容",
    description="内存中的资源"
)
```

***REMOVED******REMOVED******REMOVED*** 4. 工具集成

```python
from mcp.tool_adapter import MCPToolAdapter
from tools import default_registry

***REMOVED*** 将现有的 Tool 系统适配为 MCP
adapter = MCPToolAdapter(default_registry)
mcp_tools = adapter.to_mcp_tools()

***REMOVED*** 现在可以在 MCP 服务器中使用这些工具
for tool in mcp_tools:
    print(f"{tool.name}: {tool.description}")
```

***REMOVED******REMOVED*** API 参考

***REMOVED******REMOVED******REMOVED*** MCPManager

管理多个 MCP 服务器的统一接口。

```python
manager = MCPManager()

***REMOVED*** 注册服务器
manager.register_server(name: str, server: MCPServer) -> None

***REMOVED*** 获取客户端
client = manager.get_client(name: str) -> Optional[MCPClient]

***REMOVED*** 列出所有服务器
servers = manager.list_servers() -> List[str]

***REMOVED*** 获取所有工具
all_tools = manager.get_all_tools() -> Dict[str, List[MCPTool]]

***REMOVED*** 调用工具
result = manager.call_tool(server_name: str, tool_name: str, arguments: Dict) -> Any

***REMOVED*** 查找工具
tool_info = manager.find_tool(tool_name: str) -> Optional[tuple[str, MCPTool]]
```

***REMOVED******REMOVED******REMOVED*** MCPClient

管理与单个 MCP 服务器的连接。

```python
client = MCPClient(server: MCPServer)

***REMOVED*** 初始化
client.initialize() -> bool

***REMOVED*** 列出工具
tools = client.list_tools() -> List[MCPTool]

***REMOVED*** 调用工具
result = client.call_tool(name: str, arguments: Dict) -> Any

***REMOVED*** 列出资源
resources = client.list_resources() -> List[MCPResource]

***REMOVED*** 读取资源
content = client.read_resource(uri: str) -> str
```

***REMOVED******REMOVED******REMOVED*** MCPServer

MCP 服务器基类，子类需要实现抽象方法。

```python
class MyServer(MCPServer):
    def list_tools(self) -> List[MCPTool]:
        """列出所有工具"""
        pass
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用工具"""
        pass
    
    def list_resources(self) -> List[MCPResource]:
        """列出所有资源"""
        pass
    
    def read_resource(self, uri: str) -> str:
        """读取资源"""
        pass
```

***REMOVED******REMOVED*** 与 Skills 和 Tools 的集成

***REMOVED******REMOVED******REMOVED*** 与 Tools 集成

MCP 系统通过 `MCPToolAdapter` 自动集成现有的 Tool 系统：

```python
from mcp.tool_adapter import MCPToolAdapter
from tools import default_registry

adapter = MCPToolAdapter(default_registry)
mcp_tools = adapter.to_mcp_tools()
```

***REMOVED******REMOVED******REMOVED*** 与 Skills 集成

可以通过资源提供者访问 Skills：

```python
from mcp.resource import FileSystemResourceProvider
from pathlib import Path

***REMOVED*** Skills 目录作为资源
skills_path = Path(__file__).parent.parent / "skills"
provider = FileSystemResourceProvider(skills_path, uri_prefix="skill://")
```

***REMOVED******REMOVED*** 运行示例

```bash
***REMOVED*** 运行示例
cd /root/data/AI/creator/src
python -m mcp.example

***REMOVED*** 运行测试
python -m mcp.test
```

***REMOVED******REMOVED*** 设计模式

***REMOVED******REMOVED******REMOVED*** 1. 服务器-客户端模式

- **服务器**：提供工具、资源和提示
- **客户端**：连接服务器，发送请求，接收响应
- **管理器**：统一管理多个服务器

***REMOVED******REMOVED******REMOVED*** 2. 适配器模式

- **MCPToolAdapter**：将 Tool 系统适配为 MCP 工具
- **ResourceProvider**：统一资源访问接口

***REMOVED******REMOVED******REMOVED*** 3. 工厂模式

- **MCPManager**：统一创建和管理服务器和客户端

***REMOVED******REMOVED*** 扩展性

***REMOVED******REMOVED******REMOVED*** 添加新的资源提供者

```python
from mcp.resource import MCPResourceProvider

class DatabaseResourceProvider(MCPResourceProvider):
    """数据库资源提供者"""
    
    def get_resource(self, uri: str) -> str:
        ***REMOVED*** 从数据库读取资源
        pass
    
    def list_resources(self) -> List[MCPResource]:
        ***REMOVED*** 列出数据库中的资源
        pass
```

***REMOVED******REMOVED******REMOVED*** 添加新的传输层

当前实现使用内存通信，可以扩展为：
- **Stdio Transport**：标准输入输出
- **HTTP Transport**：HTTP 通信
- **WebSocket Transport**：WebSocket 通信

***REMOVED******REMOVED*** 与标准 MCP 的兼容性

本实现遵循 MCP 标准协议：
- JSON-RPC 2.0 消息格式
- 标准的请求/响应结构
- 工具、资源、提示的标准定义

可以轻松扩展为支持完整的 MCP 传输层（stdio、HTTP 等）。

***REMOVED******REMOVED*** 参考

- [Model Context Protocol 官方文档](https://modelcontextprotocol.io/)
- [MCP 架构说明](https://modelcontextprotocol.io/docs/learn/architecture)

---

**最后更新**: 2025-12-26
