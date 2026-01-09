"""
UniMem Redis 数据库操作

提供与 UniMem 相关的 Redis 操作函数：
- FoA (Focus of Attention) 层操作 - 工作记忆
- DA (Direct Access) 层操作 - 快速访问层
- 会话管理
- 记忆的 CRUD 操作
- 过期时间管理（TTL）

工业级特性：
- 连接池管理（ConnectionPool）
- 重试机制（指数退避）
- 健康检查（ping）
- 线程安全（连接池线程安全）
- 统一异常处理（使用适配器异常体系）
- 性能监控（操作耗时统计）
"""

import os
import json
import time
import logging
import threading
from typing import List, Optional, Dict, Any, Set
from datetime import datetime
from dataclasses import asdict, is_dataclass, dataclass, field
from enum import Enum

try:
    import redis
    from redis.connection import ConnectionPool
    from redis.exceptions import RedisError, ConnectionError, TimeoutError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None
    ConnectionPool = None
    RedisError = Exception
    ConnectionError = Exception
    TimeoutError = Exception

from .memory_types import Memory, MemoryType, MemoryLayer, Context
from .adapters.base import (
    AdapterError,
    AdapterNotAvailableError,
    AdapterConfigurationError,
)

logger = logging.getLogger(__name__)

***REMOVED*** Redis 连接配置
_redis_client: Optional[Any] = None
_connection_pool: Optional[Any] = None
_client_lock = threading.Lock()
_max_retries = 3
_retry_delay = 0.1


@dataclass
class RedisStats:
    """Redis 操作统计"""
    operations: int = 0
    successes: int = 0
    failures: int = 0
    total_time: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.operations == 0:
            return 0.0
        return self.successes / self.operations
    
    @property
    def average_time(self) -> float:
        """平均耗时"""
        if self.operations == 0:
            return 0.0
        return self.total_time / self.operations


def get_redis_client(
    host: Optional[str] = None,
    port: Optional[int] = None,
    db: Optional[int] = None,
    password: Optional[str] = None,
    decode_responses: bool = True,
    max_connections: int = 50,
    connection_pool: Optional[Any] = None
) -> Optional[Any]:
    """
    获取 Redis 客户端（使用连接池，线程安全）
    
    支持环境变量配置：
    - REDIS_HOST: Redis 主机地址（默认: localhost）
    - REDIS_PORT: Redis 端口（默认: 6379）
    - REDIS_DB: 数据库编号（默认: 0）
    - REDIS_PASSWORD: 密码（可选）
    - REDIS_MAX_CONNECTIONS: 最大连接数（默认: 50）
    
    Args:
        host: Redis 主机地址（可选，从环境变量读取）
        port: Redis 端口（可选，从环境变量读取）
        db: 数据库编号（可选，从环境变量读取）
        password: 密码（可选，从环境变量读取）
        decode_responses: 是否自动解码响应为字符串
        max_connections: 连接池最大连接数
        connection_pool: 已有的连接池（可选）
        
    Returns:
        Redis 客户端实例，如果连接失败则返回 None
        
    Raises:
        AdapterConfigurationError: 如果配置无效
        AdapterNotAvailableError: 如果 Redis 库不可用
    """
    global _redis_client, _connection_pool
    
    if not REDIS_AVAILABLE:
        raise AdapterNotAvailableError("Redis library not available", adapter_name="RedisClient")
    
    ***REMOVED*** 读取配置（简化版）
    host = host or os.getenv("REDIS_HOST", "localhost")
    port = port or int(os.getenv("REDIS_PORT", "6379"))
    db = db or int(os.getenv("REDIS_DB", "0"))
    password = password or os.getenv("REDIS_PASSWORD")
    max_connections = max_connections or int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
    
    ***REMOVED*** 验证配置
    if not (1 <= port <= 65535):
        raise AdapterConfigurationError(f"Invalid Redis port: {port}", adapter_name="RedisClient")
    if db < 0:
        raise AdapterConfigurationError(f"Invalid Redis db: {db}", adapter_name="RedisClient")
    
    with _client_lock:
        if _redis_client is None or connection_pool:
            try:
                ***REMOVED*** 使用连接池（线程安全，支持连接复用）
                pool = connection_pool or redis.ConnectionPool(
                    host=host,
                    port=port,
                    db=db,
                    password=password,
                    decode_responses=decode_responses,
                    max_connections=max_connections,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )
                if not connection_pool:
                    _connection_pool = pool
                
                _redis_client = redis.Redis(connection_pool=pool)
                
                ***REMOVED*** 测试连接（带重试）
                for attempt in range(3):
                    try:
                        _redis_client.ping()
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise ConnectionError(f"Failed to connect after 3 attempts: {e}")
                        time.sleep(0.1 * (2 ** attempt))
                
                logger.info(f"Redis connected: {host}:{port}/{db}")
            except (ConnectionError, TimeoutError) as e:
                _redis_client = _connection_pool = None
                raise AdapterNotAvailableError(f"Failed to connect to Redis: {e}", adapter_name="RedisClient", cause=e) from e
            except Exception as e:
                _redis_client = _connection_pool = None
                raise AdapterError(f"Failed to initialize Redis: {e}", adapter_name="RedisClient", cause=e) from e
    
    return _redis_client




def _execute_with_retry(operation: callable, operation_name: str = "operation", max_retries: int = None) -> Any:
    """带重试的操作执行"""
    if max_retries is None:
        max_retries = _max_retries
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except (ConnectionError, TimeoutError) as e:
            last_error = e
            if attempt < max_retries:
                wait_time = _retry_delay * (2 ** attempt)  ***REMOVED*** 指数退避
                logger.warning(f"{operation_name} failed (attempt {attempt + 1}/{max_retries + 1}): {e}, retrying in {wait_time:.3f}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"{operation_name} failed after {max_retries + 1} attempts: {e}")
        except RedisError as e:
            ***REMOVED*** Redis 其他错误不重试
            logger.error(f"{operation_name} failed with Redis error: {e}")
            raise AdapterError(
                f"{operation_name} failed: {e}",
                adapter_name="RedisClient",
                cause=e
            ) from e
        except Exception as e:
            ***REMOVED*** 未知错误不重试
            logger.error(f"{operation_name} failed with unexpected error: {e}", exc_info=True)
            raise AdapterError(
                f"{operation_name} failed: {e}",
                adapter_name="RedisClient",
                cause=e
            ) from e
    
    if last_error:
        raise AdapterNotAvailableError(
            f"{operation_name} failed after retries: {last_error}",
            adapter_name="RedisClient",
            cause=last_error
        ) from last_error
    
    return None


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
    添加记忆到 FoA（工作记忆层，带重试）
    
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
        
    Raises:
        AdapterError: 如果操作失败
    """
    if not REDIS_AVAILABLE:
        raise AdapterNotAvailableError(
            "Redis not available",
            adapter_name="RedisClient"
        )
    
    if not memory:
        raise AdapterError(
            "memory cannot be None",
            adapter_name="RedisClient"
        )
    
    start_time = time.time()
    client = client or get_redis_client()
    if not client:
        raise AdapterNotAvailableError(
            "Redis client not available",
            adapter_name="RedisClient"
        )
    
    try:
        def add_operation():
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
        
        _execute_with_retry(add_operation, operation_name="add_to_foa")
        
        duration = time.time() - start_time
        logger.debug(f"Added memory {memory.id} to FoA (time: {duration:.3f}s)")
        return True
    except (AdapterError, AdapterNotAvailableError):
        raise
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Failed to add memory {memory.id} to FoA: {e}", exc_info=True)
        raise AdapterError(
            f"Failed to add memory {memory.id} to FoA: {e}",
            adapter_name="RedisClient",
            cause=e
        ) from e


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
    检查 Redis 连接是否正常（带重试）
    
    Args:
        client: Redis 客户端（可选）
        
    Returns:
        是否连接正常
    """
    if not REDIS_AVAILABLE:
        return False
    
    try:
        client = client or get_redis_client()
        if not client:
            return False
        
        return _execute_with_retry(
            lambda: client.ping(),
            operation_name="ping",
            max_retries=2
        )
    except Exception:
        return False


def get_stats(client: Optional[Any] = None) -> Dict[str, Any]:
    """
    获取 Redis 存储统计信息（带重试）
    
    Args:
        client: Redis 客户端（可选）
        
    Returns:
        统计信息字典
    """
    if not REDIS_AVAILABLE:
        return {}
    
    try:
        client = client or get_redis_client()
        if not client:
            return {}
        
        def get_stats_internal():
            stats = {
                "foa_memory_count": client.llen("foa:memories"),
                "da_memory_count": client.scard("da:memories"),
                "foa_keys": len(client.keys("foa:memory:*")),
                "da_keys": len(client.keys("da:memory:*")),
            }
            ***REMOVED*** 获取连接池信息
            if _connection_pool:
                stats["connection_pool"] = {
                    "created_connections": _connection_pool.created_connections,
                    "available_connections": _connection_pool.available_connections,
                }
            return stats
        
        return _execute_with_retry(
            get_stats_internal,
            operation_name="get_stats",
            max_retries=2
        ) or {}
    except Exception as e:
        logger.error(f"Failed to get stats: {e}", exc_info=True)
        return {}


def health_check(client: Optional[Any] = None) -> Dict[str, Any]:
    """
    健康检查（带连接状态和统计信息）
    
    Args:
        client: Redis 客户端（可选）
        
    Returns:
        健康状态字典
    """
    if not REDIS_AVAILABLE:
        return {
            "available": False,
            "error": "Redis library not available",
            "timestamp": datetime.now().isoformat(),
        }
    
    try:
        client = client or get_redis_client()
        if not client:
            return {
                "available": False,
                "error": "Redis client not available",
                "timestamp": datetime.now().isoformat(),
            }
        
        ***REMOVED*** 检查连接
        is_alive = ping(client)
        
        ***REMOVED*** 获取统计信息
        stats = get_stats(client)
        
        ***REMOVED*** 获取连接池信息
        pool_info = {}
        if _connection_pool:
            try:
                pool_info = {
                    "created_connections": _connection_pool.created_connections,
                    "available_connections": _connection_pool.available_connections,
                    "max_connections": _connection_pool.max_connections,
                }
            except Exception:
                pass
        
        return {
            "available": is_alive,
            "status": "healthy" if is_alive else "unhealthy",
            "stats": stats,
            "connection_pool": pool_info,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "available": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }

