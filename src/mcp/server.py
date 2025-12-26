"""
MCP 服务器基类
实现 Model Context Protocol 服务器端
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path

from .protocol import (
    MCPRequest, MCPResponse, MCPTool, MCPResource, MCPPrompt,
    MCPMethod
)


class MCPServer(ABC):
    """
    MCP 服务器基类
    子类需要实现工具、资源和提示的具体逻辑
    """
    
    def __init__(self, name: str, version: str = "1.0.0"):
        """
        初始化 MCP 服务器
        
        Args:
            name: 服务器名称
            version: 服务器版本
        """
        self.name = name
        self.version = version
        self._initialized = False
        self._capabilities: Dict[str, Any] = {
            "tools": {},
            "resources": {},
            "prompts": {}
        }
    
    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """
        处理 MCP 请求
        
        Args:
            request: MCP 请求对象
            
        Returns:
            MCP 响应对象
        """
        try:
            ***REMOVED*** 处理初始化
            if request.method == MCPMethod.INITIALIZE:
                return self._handle_initialize(request)
            
            ***REMOVED*** 检查是否已初始化
            if not self._initialized and request.method != MCPMethod.INITIALIZE:
                return MCPResponse.error(
                    request.id,
                    -32002,
                    "Server not initialized"
                )
            
            ***REMOVED*** 路由到具体处理方法
            method_handlers = {
                MCPMethod.TOOLS_LIST: self._handle_tools_list,
                MCPMethod.TOOLS_CALL: self._handle_tools_call,
                MCPMethod.RESOURCES_LIST: self._handle_resources_list,
                MCPMethod.RESOURCES_READ: self._handle_resources_read,
                MCPMethod.PROMPTS_LIST: self._handle_prompts_list,
                MCPMethod.PROMPTS_GET: self._handle_prompts_get,
            }
            
            handler = method_handlers.get(request.method)
            if handler:
                return handler(request)
            else:
                return MCPResponse.error(
                    request.id,
                    -32601,
                    f"Method not found: {request.method}"
                )
        
        except Exception as e:
            return MCPResponse.error(
                request.id,
                -32603,
                f"Internal error: {str(e)}"
            )
    
    def _handle_initialize(self, request: MCPRequest) -> MCPResponse:
        """处理初始化请求"""
        client_info = request.params.get("clientInfo", {})
        capabilities = request.params.get("capabilities", {})
        
        ***REMOVED*** 初始化服务器
        self._initialized = True
        
        ***REMOVED*** 返回服务器信息
        result = {
            "protocolVersion": "2024-11-05",
            "version": self.version,
            "capabilities": self._capabilities,
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
        
        return MCPResponse.success(request.id, result)
    
    def _handle_tools_list(self, request: MCPRequest) -> MCPResponse:
        """处理工具列表请求"""
        tools = self.list_tools()
        return MCPResponse.success(request.id, {"tools": [tool.to_dict() for tool in tools]})
    
    def _handle_tools_call(self, request: MCPRequest) -> MCPResponse:
        """处理工具调用请求"""
        tool_name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if not tool_name:
            return MCPResponse.error(request.id, -32602, "Missing tool name")
        
        try:
            result = self.call_tool(tool_name, arguments)
            return MCPResponse.success(request.id, {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            })
        except ValueError as e:
            return MCPResponse.error(request.id, -32602, f"Invalid arguments: {str(e)}")
        except Exception as e:
            return MCPResponse.error(request.id, -32603, f"Tool execution error: {str(e)}")
    
    def _handle_resources_list(self, request: MCPRequest) -> MCPResponse:
        """处理资源列表请求"""
        resources = self.list_resources()
        return MCPResponse.success(request.id, {"resources": [r.to_dict() for r in resources]})
    
    def _handle_resources_read(self, request: MCPRequest) -> MCPResponse:
        """处理资源读取请求"""
        uri = request.params.get("uri")
        
        if not uri:
            return MCPResponse.error(request.id, -32602, "Missing resource URI")
        
        try:
            content = self.read_resource(uri)
            return MCPResponse.success(request.id, {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/plain",
                        "text": content
                    }
                ]
            })
        except FileNotFoundError:
            return MCPResponse.error(request.id, -32602, f"Resource not found: {uri}")
        except Exception as e:
            return MCPResponse.error(request.id, -32603, f"Resource read error: {str(e)}")
    
    def _handle_prompts_list(self, request: MCPRequest) -> MCPResponse:
        """处理提示列表请求"""
        prompts = self.list_prompts()
        return MCPResponse.success(request.id, {"prompts": [p.to_dict() for p in prompts]})
    
    def _handle_prompts_get(self, request: MCPRequest) -> MCPResponse:
        """处理提示获取请求"""
        name = request.params.get("name")
        arguments = request.params.get("arguments", {})
        
        if not name:
            return MCPResponse.error(request.id, -32602, "Missing prompt name")
        
        try:
            prompt = self.get_prompt(name, arguments)
            return MCPResponse.success(request.id, prompt)
        except ValueError as e:
            return MCPResponse.error(request.id, -32602, str(e))
        except Exception as e:
            return MCPResponse.error(request.id, -32603, f"Prompt error: {str(e)}")
    
    ***REMOVED*** ==================== 抽象方法（子类需要实现）====================
    
    @abstractmethod
    def list_tools(self) -> List[MCPTool]:
        """列出所有可用的工具"""
        pass
    
    @abstractmethod
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """调用指定的工具"""
        pass
    
    @abstractmethod
    def list_resources(self) -> List[MCPResource]:
        """列出所有可用的资源"""
        pass
    
    @abstractmethod
    def read_resource(self, uri: str) -> str:
        """读取指定的资源"""
        pass
    
    def list_prompts(self) -> List[MCPPrompt]:
        """列出所有可用的提示（可选）"""
        return []
    
    def get_prompt(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """获取指定的提示（可选）"""
        raise ValueError(f"Prompt not found: {name}")
