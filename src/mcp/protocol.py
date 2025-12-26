"""
MCP 协议定义
基于 JSON-RPC 2.0 的 Model Context Protocol
"""
import json
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum


class MCPMethod(str, Enum):
    """MCP 协议方法"""
    ***REMOVED*** 生命周期
    INITIALIZE = "initialize"
    INITIALIZED = "initialized"
    
    ***REMOVED*** 工具
    TOOLS_LIST = "tools/list"
    TOOLS_CALL = "tools/call"
    
    ***REMOVED*** 资源
    RESOURCES_LIST = "resources/list"
    RESOURCES_READ = "resources/read"
    
    ***REMOVED*** 提示
    PROMPTS_LIST = "prompts/list"
    PROMPTS_GET = "prompts/get"
    
    ***REMOVED*** 通知
    NOTIFICATIONS = "notifications"


@dataclass
class MCPRequest:
    """MCP 请求"""
    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None
    method: str = ""
    params: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "jsonrpc": self.jsonrpc,
            "method": self.method,
        }
        if self.id is not None:
            result["id"] = self.id
        if self.params:
            result["params"] = self.params
        return result
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPRequest":
        """从字典创建"""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            method=data.get("method", ""),
            params=data.get("params", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "MCPRequest":
        """从 JSON 字符串创建"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class MCPResponse:
    """MCP 响应"""
    jsonrpc: str = "2.0"
    id: Optional[Union[int, str]] = None
    result: Optional[Any] = None
    _error: Optional[Dict[str, Any]] = None  ***REMOVED*** 错误信息字典（使用私有字段避免冲突）
    
    @property
    def error(self) -> Optional[Dict[str, Any]]:
        """获取错误信息"""
        return self._error
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "jsonrpc": self.jsonrpc,
        }
        if self.id is not None:
            result["id"] = self.id
        if self._error is not None:
            result["error"] = self._error
        else:
            result["result"] = self.result
        return result
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def success(cls, request_id: Optional[Union[int, str]], result: Any) -> "MCPResponse":
        """创建成功响应"""
        return cls(
            jsonrpc="2.0",
            id=request_id,
            result=result
        )
    
    @classmethod
    def error(cls, request_id: Optional[Union[int, str]], code: int, message: str, data: Optional[Any] = None) -> "MCPResponse":
        """创建错误响应"""
        error_dict = {
            "code": code,
            "message": message
        }
        if data is not None:
            error_dict["data"] = data
        return cls(
            jsonrpc="2.0",
            id=request_id,
            _error=error_dict
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MCPResponse":
        """从字典创建"""
        return cls(
            jsonrpc=data.get("jsonrpc", "2.0"),
            id=data.get("id"),
            result=data.get("result"),
            _error=data.get("error")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "MCPResponse":
        """从 JSON 字符串创建"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class MCPTool:
    """MCP 工具定义"""
    name: str
    description: str
    inputSchema: Dict[str, Any]  ***REMOVED*** JSON Schema
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.inputSchema
        }


@dataclass
class MCPResource:
    """MCP 资源定义"""
    uri: str
    name: str
    description: Optional[str] = None
    mimeType: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "uri": self.uri,
            "name": self.name
        }
        if self.description:
            result["description"] = self.description
        if self.mimeType:
            result["mimeType"] = self.mimeType
        return result


@dataclass
class MCPPrompt:
    """MCP 提示定义"""
    name: str
    description: Optional[str] = None
    arguments: Optional[List[Dict[str, Any]]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "name": self.name
        }
        if self.description:
            result["description"] = self.description
        if self.arguments:
            result["arguments"] = self.arguments
        return result
