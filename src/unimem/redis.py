"""
UniMem Redis 数据库操作

提供与 UniMem 相关的 Redis 操作函数：
- FoA (Focus of Attention) 层操作 - 工作记忆
- DA (Direct Access) 层操作 - 快速访问层
- 会话管理
- 记忆的 CRUD 操作
- 过期时间管理（TTL）
"""

import json
import time
import logging
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from dataclasses import asdict, is_dataclass
from enum import Enum

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from .types import Memory, MemoryType, MemoryLayer, Context

logger = logging.getLogger(__name__)

***REMOVED*** Redis 连接配置
_redis_client: Optional[Any] = None


def get_redis_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    db: Optional[int] = None,
    password: Optional[str] = None,
    decode_responses: bool = True
) -> Optional[Any]:
    """
    获取 Redis 客户端（单例模式）
    
    支持环境变量配置：
    - REDIS_HOST: Redis 主机地址（默认: localhost）
    - REDIS_PORT: Redis 端口（默认: 6379）
    - REDIS_DB: 数据库编号（默认: 0）
    - REDIS_PASSWORD: 密码（可选）
    
    Args:
        host: Redis 主机地址（可选，从环境变量读取）
        port: Redis 端口（可选，从环境变量读取）
        db: 数据库编号（可选，从环境变量读取）
        password: 密码（可选，从环境变量读取）
        decode_responses: 是否自动解码响应为字符串
        
    Returns:
        Redis 客户端实例，如果连接失败则返回 None
    """
    global _redis_client
    
    if not REDIS_AVAILABLE:
        logger.warning("Redis library not available")
        return None
    
    ***REMOVED*** 从环境变量读取配置（如果未提供参数）
    import os
    if host is None:
        host = os.getenv("REDIS_HOST", "localhost")
    if port is None:
        port = int(os.getenv("REDIS_PORT", "6379"))
    if db is None:
        db = int(os.getenv("REDIS_DB", "0"))
    if password is None:
        password = os.getenv("REDIS_PASSWORD")
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
            )
            ***REMOVED*** 测试连接
            _redis_client.ping()
            logger.info(f"Redis connected: {host}:{port}/{db}")
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Redis connection failed: {host}:{port}/{db} - {e}. Redis operations will be unavailable.")
            _redis_client = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            _redis_client = None
    
    return _redis_client


def get_current_time() -> str:
    """获取当前时间字符串（ISO格式）"""
    return datetime.now().isoformat()


def _memory_to_dict(memory: Memory) -> Dict[str, Any]:
    """将 Memory 对象转换为字典（用于 JSON 序列化）"""
    result = {}
    for key, value in asdict(memory).items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, (set, frozenset)):
            result[key] = list(value)
        elif isinstance(value, Enum):
            result[key] = value.value
        elif is_dataclass(value):
            result[key] = _memory_to_dict(value)
        else:
            result[key] = value
    return result


def _dict_to_memory(data: Dict[str, Any]) -> Memory:
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
    
    ***REMOVED*** 处理 links (list -> set)
    if "links" in data and isinstance(data["links"], list):
        data["links"] = set(data["links"])
    
    return Memory(**data)


***REMOVED*** ==================== FoA (Focus of Attention) 层操作 ====================

def add_to_foa(memory: Memory, client: Optional[Any] = None, ttl: int = 3600) -> bool:
    """
    添加记忆到 FoA（工作记忆层）
    
    FoA 特点：
    - 临时存储，高频访问
    - 自动过期（默认1小时）
    - 使用列表存储最近访问的记忆
    
    Args:
        memory: Memory 对象
        client: Redis 客户端（可选，使用默认客户端）
        ttl: 过期时间（秒），默认3600秒（1小时）
        
    Returns:
        是否成功添加
    """
    if not REDIS_AVAILABLE:
        logger.warning("Redis not available")
        return False
    
    client = client or get_redis_client()
    if not client:
        return False
    
    try:
        ***REMOVED*** 1. 存储记忆对象（JSON）
        memory_key = f"foa:memory:{memory.id}"
        memory_data = _memory_to_dict(memory)
        client.setex(memory_key, ttl, json.dumps(memory_data, ensure_ascii=False))
        
        ***REMOVED*** 2. 添加到 FoA 记忆列表（最近访问的记忆）
        list_key = "foa:memories"
        client.lpush(list_key, memory.id)
        client.expire(list_key, ttl)
        
        ***REMOVED*** 3. 限制列表长度（保留最近1000个）
        client.ltrim(list_key, 0, 999)
        
        ***REMOVED*** 4. 如果有关联的会话，添加到会话列表
        if memory.metadata.get("session_id"):
            session_key = f"foa:session:{memory.metadata['session_id']}"
            client.lpush(session_key, memory.id)
            client.expire(session_key, ttl)
            client.ltrim(session_key, 0, 499)  ***REMOVED*** 每个会话保留最近500个
        
        logger.debug(f"Added memory {memory.id} to FoA")
        return True
    except Exception as e:
        logger.error(f"Failed to add memory {memory.id} to FoA: {e}", exc_info=True)
        return False


def get_from_foa(memory_id: str, client: Optional[Any] = None) -> Optional[Memory]:
    """
    从 FoA 获取记忆
    
    Args:
        memory_id: 记忆ID
        client: Redis 客户端（可选）
        
    Returns:
        Memory 对象，如果不存在则返回 None
    """
    if not REDIS_AVAILABLE:
        return None
    
    client = client or get_redis_client()
    if not client:
        return None
    
    try:
        memory_key = f"foa:memory:{memory_id}"
        memory_data = client.get(memory_key)
        if not memory_data:
            return None
        
        data = json.loads(memory_data)
        memory = _dict_to_memory(data)
        
        ***REMOVED*** 更新访问统计
        memory.last_accessed = datetime.now()
        memory.retrieval_count += 1
        
        ***REMOVED*** 更新存储
        ttl = client.ttl(memory_key)
        if ttl > 0:
            client.setex(memory_key, ttl, json.dumps(_memory_to_dict(memory), ensure_ascii=False))
        
        return memory
    except Exception as e:
        logger.error(f"Failed to get memory {memory_id} from FoA: {e}", exc_info=True)
        return None


def remove_from_foa(memory_id: str, client: Optional[Any] = None) -> bool:
    """
    从 FoA 移除记忆
    
    Args:
        memory_id: 记忆ID
        client: Redis 客户端（可选）
        
    Returns:
        是否成功移除
    """
    if not REDIS_AVAILABLE:
        return False
    
    client = client or get_redis_client()
    if not client:
        return False
    
    try:
        ***REMOVED*** 删除记忆对象
        memory_key = f"foa:memory:{memory_id}"
        client.delete(memory_key)
        
        ***REMOVED*** 从列表中移除
        list_key = "foa:memories"
        client.lrem(list_key, 0, memory_id)
        
        logger.debug(f"Removed memory {memory_id} from FoA")
        return True
    except Exception as e:
        logger.error(f"Failed to remove memory {memory_id} from FoA: {e}", exc_info=True)
        return False


def get_foa_memories(limit: int = 100, client: Optional[Any] = None) -> List[Memory]:
    """
    获取 FoA 中的记忆列表（最近访问的）
    
    Args:
        limit: 返回数量限制
        client: Redis 客户端（可选）
        
    Returns:
        记忆列表
    """
    if not REDIS_AVAILABLE:
        return []
    
    client = client or get_redis_client()
    if not client:
        return []
    
    try:
        list_key = "foa:memories"
        memory_ids = client.lrange(list_key, 0, limit - 1)
        
        memories = []
        for memory_id in memory_ids:
            memory = get_from_foa(memory_id, client)
            if memory:
                memories.append(memory)
        
        return memories
    except Exception as e:
        logger.error(f"Failed to get FoA memories: {e}", exc_info=True)
        return []


def get_foa_memories_by_session(session_id: str, limit: int = 100, client: Optional[Any] = None) -> List[Memory]:
    """
    根据会话ID获取 FoA 中的记忆
    
    Args:
        session_id: 会话ID
        limit: 返回数量限制
        client: Redis 客户端（可选）
        
    Returns:
        记忆列表
    """
    if not REDIS_AVAILABLE:
        return []
    
    client = client or get_redis_client()
    if not client:
        return []
    
    try:
        session_key = f"foa:session:{session_id}"
        memory_ids = client.lrange(session_key, 0, limit - 1)
        
        memories = []
        for memory_id in memory_ids:
            memory = get_from_foa(memory_id, client)
            if memory:
                memories.append(memory)
        
        return memories
    except Exception as e:
        logger.error(f"Failed to get FoA memories for session {session_id}: {e}", exc_info=True)
        return []


def clear_foa(session_id: Optional[str] = None, client: Optional[Any] = None) -> bool:
    """
    清空 FoA（工作记忆）
    
    Args:
        session_id: 如果提供，只清空该会话的记忆；否则清空所有
        client: Redis 客户端（可选）
        
    Returns:
        是否成功清空
    """
    if not REDIS_AVAILABLE:
        return False
    
    client = client or get_redis_client()
    if not client:
        return False
    
    try:
        if session_id:
            ***REMOVED*** 清空会话记忆
            session_key = f"foa:session:{session_id}"
            memory_ids = client.lrange(session_key, 0, -1)
            for memory_id in memory_ids:
                remove_from_foa(memory_id, client)
            client.delete(session_key)
            logger.info(f"Cleared FoA for session {session_id}")
        else:
            ***REMOVED*** 清空所有 FoA 记忆
            pattern = "foa:memory:*"
            keys = client.keys(pattern)
            if keys:
                client.delete(*keys)
            client.delete("foa:memories")
            logger.info("Cleared all FoA memories")
        return True
    except Exception as e:
        logger.error(f"Failed to clear FoA: {e}", exc_info=True)
        return False


***REMOVED*** ==================== DA (Direct Access) 层操作 ====================

def add_to_da(memory: Memory, client: Optional[Any] = None, ttl: int = 86400) -> bool:
    """
    添加记忆到 DA（快速访问层）
    
    DA 特点：
    - 会话关键记忆
    - 比 FoA 更长生命周期（默认24小时）
    - 支持按类型和标签索引
    
    Args:
        memory: Memory 对象
        client: Redis 客户端（可选）
        ttl: 过期时间（秒），默认86400秒（24小时）
        
    Returns:
        是否成功添加
    """
    if not REDIS_AVAILABLE:
        return False
    
    client = client or get_redis_client()
    if not client:
        return False
    
    try:
        ***REMOVED*** 1. 存储记忆对象
        memory_key = f"da:memory:{memory.id}"
        memory_data = _memory_to_dict(memory)
        client.setex(memory_key, ttl, json.dumps(memory_data, ensure_ascii=False))
        
        ***REMOVED*** 2. 添加到 DA 记忆集合
        set_key = "da:memories"
        client.sadd(set_key, memory.id)
        client.expire(set_key, ttl)
        
        ***REMOVED*** 3. 如果有关联的会话，添加到会话集合
        if memory.metadata.get("session_id"):
            session_key = f"da:session:{memory.metadata['session_id']}"
            client.sadd(session_key, memory.id)
            client.expire(session_key, ttl)
        
        ***REMOVED*** 4. 按记忆类型索引
        if memory.memory_type:
            type_key = f"da:type:{memory.memory_type.value}"
            client.sadd(type_key, memory.id)
            client.expire(type_key, ttl)
        
        ***REMOVED*** 5. 按标签索引
        for tag in memory.tags:
            tag_key = f"da:tag:{tag}"
            client.sadd(tag_key, memory.id)
            client.expire(tag_key, ttl)
        
        logger.debug(f"Added memory {memory.id} to DA")
        return True
    except Exception as e:
        logger.error(f"Failed to add memory {memory.id} to DA: {e}", exc_info=True)
        return False


def get_from_da(memory_id: str, client: Optional[Any] = None) -> Optional[Memory]:
    """
    从 DA 获取记忆
    
    Args:
        memory_id: 记忆ID
        client: Redis 客户端（可选）
        
    Returns:
        Memory 对象，如果不存在则返回 None
    """
    if not REDIS_AVAILABLE:
        return None
    
    client = client or get_redis_client()
    if not client:
        return None
    
    try:
        memory_key = f"da:memory:{memory_id}"
        memory_data = client.get(memory_key)
        if not memory_data:
            return None
        
        data = json.loads(memory_data)
        memory = _dict_to_memory(data)
        
        ***REMOVED*** 更新访问统计
        memory.last_accessed = datetime.now()
        memory.retrieval_count += 1
        
        ***REMOVED*** 更新存储
        ttl = client.ttl(memory_key)
        if ttl > 0:
            client.setex(memory_key, ttl, json.dumps(_memory_to_dict(memory), ensure_ascii=False))
        
        return memory
    except Exception as e:
        logger.error(f"Failed to get memory {memory_id} from DA: {e}", exc_info=True)
        return None


def remove_from_da(memory_id: str, client: Optional[Any] = None) -> bool:
    """
    从 DA 移除记忆
    
    Args:
        memory_id: 记忆ID
        client: Redis 客户端（可选）
        
    Returns:
        是否成功移除
    """
    if not REDIS_AVAILABLE:
        return False
    
    client = client or get_redis_client()
    if not client:
        return False
    
    try:
        ***REMOVED*** 获取记忆信息（用于清理索引）
        memory = get_from_da(memory_id, client)
        
        ***REMOVED*** 删除记忆对象
        memory_key = f"da:memory:{memory_id}"
        client.delete(memory_key)
        
        ***REMOVED*** 从集合中移除
        set_key = "da:memories"
        client.srem(set_key, memory_id)
        
        ***REMOVED*** 清理索引
        if memory:
            if memory.metadata.get("session_id"):
                session_key = f"da:session:{memory.metadata['session_id']}"
                client.srem(session_key, memory_id)
            if memory.memory_type:
                type_key = f"da:type:{memory.memory_type.value}"
                client.srem(type_key, memory_id)
            for tag in memory.tags:
                tag_key = f"da:tag:{tag}"
                client.srem(tag_key, memory_id)
        
        logger.debug(f"Removed memory {memory_id} from DA")
        return True
    except Exception as e:
        logger.error(f"Failed to remove memory {memory_id} from DA: {e}", exc_info=True)
        return False


def get_da_memories_by_type(memory_type: MemoryType, limit: int = 100, client: Optional[Any] = None) -> List[Memory]:
    """
    根据记忆类型获取 DA 中的记忆
    
    Args:
        memory_type: 记忆类型
        limit: 返回数量限制
        client: Redis 客户端（可选）
        
    Returns:
        记忆列表
    """
    if not REDIS_AVAILABLE:
        return []
    
    client = client or get_redis_client()
    if not client:
        return []
    
    try:
        type_key = f"da:type:{memory_type.value}"
        memory_ids = list(client.smembers(type_key))[:limit]
        
        memories = []
        for memory_id in memory_ids:
            memory = get_from_da(memory_id, client)
            if memory:
                memories.append(memory)
        
        return memories
    except Exception as e:
        logger.error(f"Failed to get DA memories by type {memory_type}: {e}", exc_info=True)
        return []


def get_da_memories_by_session(session_id: str, limit: int = 100, client: Optional[Any] = None) -> List[Memory]:
    """
    根据会话ID获取 DA 中的记忆
    
    Args:
        session_id: 会话ID
        limit: 返回数量限制
        client: Redis 客户端（可选）
        
    Returns:
        记忆列表
    """
    if not REDIS_AVAILABLE:
        return []
    
    client = client or get_redis_client()
    if not client:
        return []
    
    try:
        session_key = f"da:session:{session_id}"
        memory_ids = list(client.smembers(session_key))[:limit]
        
        memories = []
        for memory_id in memory_ids:
            memory = get_from_da(memory_id, client)
            if memory:
                memories.append(memory)
        
        return memories
    except Exception as e:
        logger.error(f"Failed to get DA memories for session {session_id}: {e}", exc_info=True)
        return []


def get_da_memories_by_tag(tag: str, limit: int = 100, client: Optional[Any] = None) -> List[Memory]:
    """
    根据标签获取 DA 中的记忆
    
    Args:
        tag: 标签
        limit: 返回数量限制
        client: Redis 客户端（可选）
        
    Returns:
        记忆列表
    """
    if not REDIS_AVAILABLE:
        return []
    
    client = client or get_redis_client()
    if not client:
        return []
    
    try:
        tag_key = f"da:tag:{tag}"
        memory_ids = list(client.smembers(tag_key))[:limit]
        
        memories = []
        for memory_id in memory_ids:
            memory = get_from_da(memory_id, client)
            if memory:
                memories.append(memory)
        
        return memories
    except Exception as e:
        logger.error(f"Failed to get DA memories by tag {tag}: {e}", exc_info=True)
        return []


***REMOVED*** ==================== 批量操作 ====================

def add_to_foa_batch(memories: List[Memory], client: Optional[Any] = None, ttl: int = 3600) -> int:
    """
    批量添加记忆到 FoA
    
    Args:
        memories: 记忆列表
        client: Redis 客户端（可选）
        ttl: 过期时间（秒）
        
    Returns:
        成功添加的数量
    """
    success_count = 0
    for memory in memories:
        if add_to_foa(memory, client, ttl):
            success_count += 1
    logger.info(f"Added {success_count}/{len(memories)} memories to FoA")
    return success_count


def add_to_da_batch(memories: List[Memory], client: Optional[Any] = None, ttl: int = 86400) -> int:
    """
    批量添加记忆到 DA
    
    Args:
        memories: 记忆列表
        client: Redis 客户端（可选）
        ttl: 过期时间（秒）
        
    Returns:
        成功添加的数量
    """
    success_count = 0
    for memory in memories:
        if add_to_da(memory, client, ttl):
            success_count += 1
    logger.info(f"Added {success_count}/{len(memories)} memories to DA")
    return success_count


***REMOVED*** ==================== 工具函数 ====================

def ping(client: Optional[Any] = None) -> bool:
    """
    检查 Redis 连接是否正常
    
    Args:
        client: Redis 客户端（可选）
        
    Returns:
        是否连接正常
    """
    if not REDIS_AVAILABLE:
        return False
    
    client = client or get_redis_client()
    if not client:
        return False
    
    try:
        return client.ping()
    except Exception:
        return False


def get_stats(client: Optional[Any] = None) -> Dict[str, Any]:
    """
    获取 Redis 存储统计信息
    
    Args:
        client: Redis 客户端（可选）
        
    Returns:
        统计信息字典
    """
    if not REDIS_AVAILABLE:
        return {}
    
    client = client or get_redis_client()
    if not client:
        return {}
    
    try:
        stats = {
            "foa_memory_count": client.llen("foa:memories"),
            "da_memory_count": client.scard("da:memories"),
            "foa_keys": len(client.keys("foa:memory:*")),
            "da_keys": len(client.keys("da:memory:*")),
        }
        return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        return {}

