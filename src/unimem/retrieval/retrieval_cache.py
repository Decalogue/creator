"""
检索缓存

实现检索结果的缓存和预取，提升检索性能。

工业级特性：
- 线程安全（使用锁保护缓存）
- LRU/TTL 淘汰策略
- 缓存统计和监控
"""

import logging
import hashlib
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from ..memory_types import RetrievalResult

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    query_hash: str
    results: List[RetrievalResult]
    created_at: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def access(self):
        """记录访问"""
        self.access_count += 1
        self.last_accessed = datetime.now()


class RetrievalCache:
    """检索缓存
    
    缓存检索结果，支持：
    - 查询结果缓存
    - LRU 淘汰策略
    - TTL 过期策略
    - 缓存预取
    """
    
    def __init__(
        self,
        max_size: int = 1000,
        ttl_seconds: Optional[int] = 3600,
        enable_lru: bool = True
    ):
        """
        初始化检索缓存
        
        Args:
            max_size: 最大缓存条目数（默认 1000）
            ttl_seconds: TTL（秒），如果为 None 则不过期（默认 3600）
            enable_lru: 是否启用 LRU 淘汰（默认 True）
        """
        self.max_size = max(max_size, 1)  # 确保至少为 1
        self.ttl_seconds = ttl_seconds
        self.enable_lru = enable_lru
        
        # 线程安全锁
        self._lock = threading.RLock()
        
        # 缓存存储（线程安全）
        self._cache: Dict[str, CacheEntry] = {}
        
        # 统计信息（线程安全）
        self._hits = 0
        self._misses = 0
        
        logger.info(f"RetrievalCache initialized: max_size={self.max_size}, ttl={ttl_seconds}")
    
    def _generate_key(self, query: str, **kwargs) -> str:
        """生成缓存键"""
        key_parts = [query]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}={v}")
        
        key_str = "|".join(key_parts)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(
        self,
        query: str,
        top_k: Optional[int] = None,
        **kwargs
    ) -> Optional[List[RetrievalResult]]:
        """
        获取缓存的检索结果（线程安全）
        
        Args:
            query: 查询文本
            top_k: Top-K 参数
            **kwargs: 其他检索参数
            
        Returns:
            缓存的检索结果，如果不存在或已过期则返回 None
        """
        if not query or not query.strip():
            return None
        
        key = self._generate_key(query, top_k=top_k, **kwargs)
        
        with self._lock:
            entry = self._cache.get(key)
            
            if not entry:
                self._misses += 1
                return None
            
            # 检查是否过期
            if self.ttl_seconds:
                age = (datetime.now() - entry.created_at).total_seconds()
                if age > self.ttl_seconds:
                    del self._cache[key]
                    self._misses += 1
                    logger.debug(f"Cache entry expired: {key}")
                    return None
            
            # 记录访问
            entry.access()
            self._hits += 1
            
            # 如果 top_k 不同，需要截取
            if top_k and len(entry.results) > top_k:
                return entry.results[:top_k]
            
            return entry.results
    
    def put(
        self,
        query: str,
        results: List[RetrievalResult],
        top_k: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """
        缓存检索结果（线程安全）
        
        Args:
            query: 查询文本
            results: 检索结果列表
            top_k: Top-K 参数
            metadata: 元数据
            **kwargs: 其他检索参数
        """
        if not query or not query.strip() or not results:
            return
        
        key = self._generate_key(query, top_k=top_k, **kwargs)
        
        with self._lock:
            # 检查是否需要淘汰
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._evict()
            
            # 创建缓存条目
            entry = CacheEntry(
                query_hash=key,
                results=results,
                metadata=metadata or {}
            )
            
            self._cache[key] = entry
            logger.debug(f"Cached retrieval result: {key}")
    
    def _evict(self) -> None:
        """淘汰缓存条目"""
        if not self._cache:
            return
        
        if self.enable_lru:
            # LRU 策略：淘汰最久未访问的
            lru_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].last_accessed or self._cache[k].created_at
            )
            del self._cache[lru_key]
            logger.debug(f"Evicted LRU entry: {lru_key}")
        else:
            # FIFO 策略：淘汰最早创建的
            fifo_key = min(
                self._cache.keys(),
                key=lambda k: self._cache[k].created_at
            )
            del self._cache[fifo_key]
            logger.debug(f"Evicted FIFO entry: {fifo_key}")
    
    def prefetch(
        self,
        queries: List[str],
        retrieval_func: callable,
        **kwargs
    ) -> None:
        """
        预取检索结果
        
        Args:
            queries: 查询列表
            retrieval_func: 检索函数
            **kwargs: 检索参数
        """
        for query in queries:
            # 检查是否已缓存
            if self.get(query, **kwargs) is None:
                try:
                    # 执行检索
                    results = retrieval_func(query, **kwargs)
                    # 缓存结果
                    self.put(query, results, **kwargs)
                    logger.debug(f"Prefetched query: {query}")
                except Exception as e:
                    logger.warning(f"Prefetch failed for query '{query}': {e}")
    
    def clear(self) -> None:
        """清空缓存（线程安全）"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            logger.info("Retrieval cache cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取缓存统计信息（线程安全）"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0.0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }


class RetrievalPrefetcher:
    """检索预取器
    
    基于查询模式预测可能的查询，提前执行检索并缓存结果。
    """
    
    def __init__(
        self,
        cache: RetrievalCache,
        retrieval_func: callable
    ):
        """
        初始化检索预取器
        
        Args:
            cache: 检索缓存实例
            retrieval_func: 检索函数
        """
        self.cache = cache
        self.retrieval_func = retrieval_func
        
        # 查询模式统计
        self._query_patterns: Dict[str, int] = {}
        
        logger.info("RetrievalPrefetcher initialized")
    
    def record_query(self, query: str) -> None:
        """记录查询模式"""
        # 提取查询关键词（简化实现）
        keywords = query.split()[:3]  # 取前3个词
        for keyword in keywords:
            self._query_patterns[keyword] = self._query_patterns.get(keyword, 0) + 1
    
    def predict_queries(self, current_query: str, top_n: int = 5) -> List[str]:
        """
        预测可能的查询
        
        Args:
            current_query: 当前查询
            top_n: 返回前N个预测查询
            
        Returns:
            预测的查询列表
        """
        # 简化实现：基于当前查询的关键词预测
        keywords = current_query.split()[:3]
        predicted = []
        
        for keyword in keywords:
            # 查找包含此关键词的常见查询模式
            similar_queries = [
                f"{keyword} {k}" for k in self._query_patterns.keys()
                if k != keyword
            ][:top_n]
            predicted.extend(similar_queries)
        
        return predicted[:top_n]
    
    def prefetch_related(self, query: str) -> None:
        """
        预取相关查询
        
        Args:
            query: 当前查询
        """
        # 记录查询
        self.record_query(query)
        
        # 预测相关查询
        predicted_queries = self.predict_queries(query)
        
        # 预取
        if predicted_queries:
            self.cache.prefetch(predicted_queries, self.retrieval_func)
            logger.debug(f"Prefetched {len(predicted_queries)} related queries")

