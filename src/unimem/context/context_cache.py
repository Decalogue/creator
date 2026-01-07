"""
上下文缓存

实现上下文的缓存机制，提升检索性能。
"""

import logging
import hashlib
import time
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: str
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def access(self):
        """记录访问"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class ContextCache:
    """上下文缓存
    
    实现上下文的缓存机制，支持：
    - LRU 淘汰策略
    - TTL 过期策略
    - 大小限制
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: Optional[int] = None,
        enable_lru: bool = True
    ):
        """
        初始化上下文缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl_seconds: TTL（秒），如果为 None 则不过期
            enable_lru: 是否启用 LRU 淘汰
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.enable_lru = enable_lru
        
        ***REMOVED*** 缓存存储
        self._cache: Dict[str, CacheEntry] = {}
        
        logger.info(f"ContextCache initialized: max_size={max_size}, ttl={ttl_seconds}")
    
    def _generate_key(self, query: str, levels: Optional[list] = None) -> str:
        """生成缓存键"""
        key_parts = [query]
        if levels:
            key_parts.append("|".join(sorted(levels)))
        
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query: str, levels: Optional[list] = None) -> Optional[str]:
        """
        获取缓存的上下文
        
        Args:
            query: 查询文本
            levels: 层级列表
            
        Returns:
            缓存的上下文，如果不存在或已过期则返回 None
        """
        key = self._generate_key(query, levels)
        entry = self._cache.get(key)
        
        if not entry:
            return None
        
        ***REMOVED*** 检查是否过期
        if self.ttl_seconds:
            age = (datetime.now() - entry.created_at).total_seconds()
            if age > self.ttl_seconds:
                del self._cache[key]
                logger.debug(f"Cache entry expired: {key}")
                return None
        
        ***REMOVED*** 记录访问
        entry.access()
        return entry.value
    
    def put(
        self,
        query: str,
        context: str,
        levels: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        缓存上下文
        
        Args:
            query: 查询文本
            context: 上下文内容
            levels: 层级列表
            metadata: 元数据
        """
        if not context:
            return
        
        key = self._generate_key(query, levels)
        
        ***REMOVED*** 检查是否需要淘汰
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict()
        
        ***REMOVED*** 创建缓存条目
        entry = CacheEntry(
            key=key,
            value=context,
            metadata=metadata or {}
        )
        
        self._cache[key] = entry
        logger.debug(f"Cached context: {key}")
    
    def _evict(self) -> None:
        """淘汰缓存条目"""
        if not self._cache:
            return
        
        if self.enable_lru:
            ***REMOVED*** LRU 策略：淘汰最久未访问的
            lru_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].last_accessed or self._cache[k].created_at
            )
            del self._cache[lru_key]
            logger.debug(f"Evicted LRU entry: {lru_key}")
        else:
            ***REMOVED*** FIFO 策略：淘汰最早创建的
            fifo_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].created_at
            )
            del self._cache[fifo_key]
            logger.debug(f"Evicted FIFO entry: {fifo_key}")
    
    def clear(self) -> None:
        """清空缓存"""
        self._cache.clear()
        logger.info("Context cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        total_size = sum(len(entry.value) for entry in self._cache.values())
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "total_bytes": total_size,
            "hit_rate": 0.0  ***REMOVED*** 需要记录命中率
        }

