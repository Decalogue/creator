"""
检索性能优化器

优化向量检索和图检索的性能，包括批量检索、索引优化等。

工业级特性：
- 参数验证和输入检查
- 统一异常处理
- 线程安全（并发控制）
"""

import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .retrieval_cache import RetrievalCache, RetrievalPrefetcher
from ..memory_types import RetrievalResult
from ..adapters.base import AdapterError

logger = logging.getLogger(__name__)


class RetrievalOptimizer:
    """检索性能优化器
    
    优化检索性能，包括：
    - 批量检索优化
    - 检索结果缓存
    - 检索预取
    - 并行检索
    """
    
    def __init__(
        self,
        retrieval_engine: Any = None,
        enable_cache: bool = True,
        enable_prefetch: bool = True,
        cache_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化检索优化器
        
        Args:
            retrieval_engine: 检索引擎实例
            enable_cache: 是否启用缓存
            enable_prefetch: 是否启用预取
            cache_config: 缓存配置
        """
        self.retrieval_engine = retrieval_engine
        
        # 初始化缓存
        if enable_cache:
            cache_config = cache_config or {}
            self.cache = RetrievalCache(
                max_size=cache_config.get("max_size", 1000),
                ttl_seconds=cache_config.get("ttl_seconds", 3600),
                enable_lru=cache_config.get("enable_lru", True)
            )
        else:
            self.cache = None
        
        # 初始化预取器
        if enable_prefetch and self.cache:
            self.prefetcher = RetrievalPrefetcher(
                cache=self.cache,
                retrieval_func=self._retrieval_wrapper
            )
        else:
            self.prefetcher = None
        
        logger.info(f"RetrievalOptimizer initialized: cache={enable_cache}, prefetch={enable_prefetch}")
    
    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        use_cache: bool = True,
        enable_prefetch: bool = True
    ) -> List[RetrievalResult]:
        """
        优化后的检索方法
        
        Args:
            query: 查询文本（不能为空）
            top_k: Top-K 参数（必须 > 0，默认 10）
            use_cache: 是否使用缓存（默认 True）
            enable_prefetch: 是否启用预取（默认 True）
            
        Returns:
            检索结果列表
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not query or not query.strip():
            raise AdapterError("query must be a non-empty string", adapter_name="RetrievalOptimizer")
        if top_k <= 0:
            raise AdapterError(f"top_k must be positive, got {top_k}", adapter_name="RetrievalOptimizer")
        
        # 1. 检查缓存
        if use_cache and self.cache:
            cached_results = self.cache.get(query, top_k=top_k)
            if cached_results is not None:
                logger.debug(f"Cache hit for query: {query[:50]}")
                return cached_results
        
        # 2. 执行检索
        if self.retrieval_engine:
            results = self.retrieval_engine.multi_dimensional_retrieval(
                query=query,
                top_k=top_k
            )
        else:
            # 降级：返回空结果
            logger.warning("Retrieval engine not available")
            results = []
        
        # 3. 缓存结果
        if use_cache and self.cache:
            self.cache.put(query, results, top_k=top_k)
        
        # 4. 预取相关查询
        if enable_prefetch and self.prefetcher:
            self.prefetcher.prefetch_related(query)
        
        return results
    
    def batch_retrieve(
        self,
        queries: List[str],
        top_k: int = 10,
        use_cache: bool = True,
        parallel: bool = True,
        max_workers: int = 5
    ) -> Dict[str, List[RetrievalResult]]:
        """
        批量检索
        
        Args:
            queries: 查询列表（不能为空）
            top_k: Top-K 参数（必须 > 0，默认 10）
            use_cache: 是否使用缓存（默认 True）
            parallel: 是否并行执行（默认 True）
            max_workers: 最大并发数（必须 > 0，默认 5）
            
        Returns:
            检索结果字典，key 为查询文本，value 为检索结果列表
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not queries or not isinstance(queries, list):
            raise AdapterError("queries must be a non-empty list", adapter_name="RetrievalOptimizer")
        if top_k <= 0:
            raise AdapterError(f"top_k must be positive, got {top_k}", adapter_name="RetrievalOptimizer")
        if max_workers <= 0:
            raise AdapterError(f"max_workers must be positive, got {max_workers}", adapter_name="RetrievalOptimizer")
        
        results = {}
        
        if parallel and len(queries) > 1:
            # 并行执行
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.retrieve, query, top_k, use_cache, False): query
                    for query in queries
                }
                
                for future in as_completed(futures):
                    query = futures[future]
                    try:
                        results[query] = future.result()
                    except Exception as e:
                        logger.error(f"Error retrieving query '{query}': {e}", exc_info=True)
                        results[query] = []
        else:
            # 串行执行
            for query in queries:
                results[query] = self.retrieve(query, top_k, use_cache, False)
        
        return results
    
    def _retrieval_wrapper(self, query: str, **kwargs) -> List[RetrievalResult]:
        """检索函数包装器（用于预取器）"""
        if self.retrieval_engine:
            return self.retrieval_engine.multi_dimensional_retrieval(
                query=query,
                top_k=kwargs.get("top_k", 10)
            )
        return []
    
    def optimize_vector_retrieval(
        self,
        query: str,
        top_k: int = 10,
        batch_size: int = 100
    ) -> List[RetrievalResult]:
        """
        优化向量检索
        
        Args:
            query: 查询文本
            top_k: Top-K 参数
            batch_size: 批量处理大小
            
        Returns:
            检索结果列表
        """
        # 简化实现：使用缓存和批量处理
        return self.retrieve(query, top_k=top_k)
    
    def optimize_graph_retrieval(
        self,
        query: str,
        top_k: int = 10,
        max_depth: int = 2
    ) -> List[RetrievalResult]:
        """
        优化图检索
        
        Args:
            query: 查询文本
            top_k: Top-K 参数
            max_depth: 最大搜索深度
            
        Returns:
            检索结果列表
        """
        # 简化实现：使用缓存
        return self.retrieve(query, top_k=top_k)
    
    def clear_cache(self) -> None:
        """清空缓存"""
        if self.cache:
            self.cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {}
        
        if self.cache:
            stats["cache"] = self.cache.get_statistics()
        
        if self.retrieval_engine:
            # 可以添加检索引擎的统计信息
            pass
        
        return stats

