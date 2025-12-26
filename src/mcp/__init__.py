"""
MCP (Model Context Protocol) 系统
提供统一的接口连接和管理 MCP 服务器
"""
from .protocol import (
    MCPRequest, MCPResponse, MCPTool, MCPResource, MCPPrompt,
    MCPMethod
)
from .server import MCPServer
from .client import MCPClient
from .manager import MCPManager, default_manager
from .resource import (
    MCPResourceProvider, FileSystemResourceProvider, MemoryResourceProvider
)
from .tool_adapter import MCPToolAdapter

__all__ = [
    ***REMOVED*** 协议
    "MCPRequest",
    "MCPResponse",
    "MCPTool",
    "MCPResource",
    "MCPPrompt",
    "MCPMethod",
    ***REMOVED*** 服务器和客户端
    "MCPServer",
    "MCPClient",
    ***REMOVED*** 管理器
    "MCPManager",
    "default_manager",
    ***REMOVED*** 资源
    "MCPResourceProvider",
    "FileSystemResourceProvider",
    "MemoryResourceProvider",
    ***REMOVED*** 工具适配器
    "MCPToolAdapter",
]
