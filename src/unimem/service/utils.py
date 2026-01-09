"""
UniMem Service 工具函数

处理数据类型转换（dataclass <-> dict）

工业级特性：
- 统一异常处理
- 输入验证
- 类型安全转换
"""

import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, Optional
from enum import Enum

from ..memory_types import Experience, Context, Task, Memory, RetrievalResult, MemoryType, MemoryLayer

logger = logging.getLogger(__name__)


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
    """将字典转换为 Experience 对象（带验证）"""
    if not data or not isinstance(data, dict):
        raise ValueError("data must be a non-empty dict")
    
    # 处理 timestamp
    if "timestamp" in data and isinstance(data["timestamp"], str):
        try:
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        except ValueError as e:
            logger.warning(f"Invalid timestamp format: {data['timestamp']}, using current time")
            data["timestamp"] = datetime.now()
    elif "timestamp" not in data:
        data["timestamp"] = datetime.now()
    
    try:
        return Experience(**data)
    except Exception as e:
        raise ValueError(f"Failed to create Experience: {e}") from e


def dict_to_context(data: Optional[Dict[str, Any]]) -> Context:
    """将字典转换为 Context 对象"""
    if data is None:
        return Context()
    return Context(**data)


def dict_to_task(data: Dict[str, Any]) -> Task:
    """将字典转换为 Task 对象"""
    return Task(**data)


def dict_to_memory(data: Dict[str, Any]) -> Memory:
    """将字典转换为 Memory 对象（带验证）"""
    if not data or not isinstance(data, dict):
        raise ValueError("data must be a non-empty dict")
    
    # 处理 timestamp
    if "timestamp" in data and isinstance(data["timestamp"], str):
        try:
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        except ValueError:
            logger.warning(f"Invalid timestamp format: {data.get('timestamp')}, using current time")
            data["timestamp"] = datetime.now()
    
    # 处理 last_accessed
    if "last_accessed" in data and isinstance(data["last_accessed"], str):
        try:
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        except ValueError:
            logger.warning(f"Invalid last_accessed format: {data.get('last_accessed')}")
            data["last_accessed"] = None
    
    # 处理 memory_type
    if "memory_type" in data and isinstance(data["memory_type"], str):
        try:
            data["memory_type"] = MemoryType(data["memory_type"])
        except ValueError:
            logger.warning(f"Invalid memory_type: {data['memory_type']}")
            data["memory_type"] = None
    
    # 处理 layer
    if "layer" in data and isinstance(data["layer"], str):
        try:
            data["layer"] = MemoryLayer(data["layer"])
        except ValueError:
            logger.warning(f"Invalid layer: {data.get('layer')}, using LTM")
            data["layer"] = MemoryLayer.LTM
    
    # 处理 links (set)
    if "links" in data and isinstance(data["links"], list):
        data["links"] = set(data["links"])
    
    try:
        return Memory(**data)
    except Exception as e:
        raise ValueError(f"Failed to create Memory: {e}") from e


def serialize_retrieval_result(result: RetrievalResult) -> Dict[str, Any]:
    """序列化 RetrievalResult 对象"""
    return {
        "memory": dataclass_to_dict(result.memory),
        "score": result.score,
        "retrieval_method": result.retrieval_method,
        "metadata": result.metadata,
    }

