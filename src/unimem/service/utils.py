"""
UniMem Service 工具函数

处理数据类型转换（dataclass <-> dict）
"""

from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum
import json

from ..types import Experience, Context, Task, Memory, RetrievalResult, MemoryType, MemoryLayer


def dataclass_to_dict(obj: Any) -> Dict[str, Any]:
    """
    将 dataclass 对象转换为字典
    
    处理 datetime 和 Enum 类型的序列化
    """
    if obj is None:
        return None
    
    if is_dataclass(obj):
        result = {}
        for key, value in asdict(obj).items():
            result[key] = _serialize_value(value)
        return result
    elif isinstance(obj, (list, tuple)):
        return [_serialize_value(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: _serialize_value(v) for k, v in obj.items()}
    else:
        return _serialize_value(obj)


def _serialize_value(value: Any) -> Any:
    """序列化单个值"""
    if value is None:
        return None
    elif isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, Enum):
        return value.value
    elif isinstance(value, (set, frozenset)):
        return list(value)
    elif is_dataclass(value):
        return dataclass_to_dict(value)
    elif isinstance(value, (list, tuple)):
        return [_serialize_value(item) for item in value]
    elif isinstance(value, dict):
        return {k: _serialize_value(v) for k, v in value.items()}
    else:
        return value


def dict_to_experience(data: Dict[str, Any]) -> Experience:
    """将字典转换为 Experience 对象"""
    ***REMOVED*** 处理 timestamp
    if "timestamp" in data and isinstance(data["timestamp"], str):
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
    elif "timestamp" not in data:
        data["timestamp"] = datetime.now()
    
    return Experience(**data)


def dict_to_context(data: Optional[Dict[str, Any]]) -> Context:
    """将字典转换为 Context 对象"""
    if data is None:
        return Context()
    return Context(**data)


def dict_to_task(data: Dict[str, Any]) -> Task:
    """将字典转换为 Task 对象"""
    return Task(**data)


def dict_to_memory(data: Dict[str, Any]) -> Memory:
    """将字典转换为 Memory 对象"""
    ***REMOVED*** 处理 timestamp
    if "timestamp" in data and isinstance(data["timestamp"], str):
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
    
    ***REMOVED*** 处理 last_accessed
    if "last_accessed" in data and isinstance(data["last_accessed"], str):
        data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
    
    ***REMOVED*** 处理 memory_type
    if "memory_type" in data and isinstance(data["memory_type"], str):
        try:
            data["memory_type"] = MemoryType(data["memory_type"])
        except ValueError:
            data["memory_type"] = None
    
    ***REMOVED*** 处理 layer
    if "layer" in data and isinstance(data["layer"], str):
        try:
            data["layer"] = MemoryLayer(data["layer"])
        except ValueError:
            data["layer"] = MemoryLayer.LTM
    
    ***REMOVED*** 处理 links (set)
    if "links" in data and isinstance(data["links"], list):
        data["links"] = set(data["links"])
    
    return Memory(**data)


def serialize_retrieval_result(result: RetrievalResult) -> Dict[str, Any]:
    """序列化 RetrievalResult 对象"""
    return {
        "memory": dataclass_to_dict(result.memory),
        "score": result.score,
        "retrieval_method": result.retrieval_method,
        "metadata": result.metadata,
    }

