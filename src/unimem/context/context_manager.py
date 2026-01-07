"""
上下文管理器

统一管理上下文的压缩、融合、检索和缓存。
"""

import logging
from typing import List, Optional, Dict, Any

from .context_compressor import ContextCompressor
from .context_fusion import ContextFusion
from .context_cache import ContextCache
from ..storage.hierarchical import HierarchicalStorage, ContentLevel

logger = logging.getLogger(__name__)


class ContextManager:
    """上下文管理器
    
    统一管理上下文的压缩、融合、检索和缓存。
    """
    
    def __init__(
        self,
        hierarchical_storage: Optional[HierarchicalStorage] = None,
        llm_func=None,
        cache_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化上下文管理器
        
        Args:
            hierarchical_storage: 分层存储实例（用于检索）
            llm_func: LLM 调用函数
            cache_config: 缓存配置
        """
        self.storage = hierarchical_storage
        self.compressor = ContextCompressor(llm_func=llm_func)
        self.fusion = ContextFusion(llm_func=llm_func)
        
        cache_config = cache_config or {}
        self.cache = ContextCache(
            max_size=cache_config.get("max_size", 1000),
            ttl_seconds=cache_config.get("ttl_seconds", 3600),
            enable_lru=cache_config.get("enable_lru", True)
        )
        
        logger.info("ContextManager initialized")
    
    def compress(self, content: str, target_length: int) -> str:
        """
        压缩上下文
        
        Args:
            content: 要压缩的内容
            target_length: 目标长度
            
        Returns:
            压缩后的内容
        """
        return self.compressor.compress(content, target_length)
    
    def fuse(self, contexts: List[str], max_length: Optional[int] = None) -> str:
        """
        融合多个上下文
        
        Args:
            contexts: 上下文列表
            max_length: 最大长度限制
            
        Returns:
            融合后的上下文
        """
        return self.fusion.fuse(contexts, max_length=max_length)
    
    def retrieve_context(
        self,
        query: str,
        levels: List[ContentLevel],
        top_k: int = 10,
        use_cache: bool = True
    ) -> str:
        """
        检索上下文
        
        Args:
            query: 查询文本
            levels: 要检索的层级列表
            top_k: 每个层级返回的前K个结果
            use_cache: 是否使用缓存
            
        Returns:
            检索到的上下文（融合后）
        """
        ***REMOVED*** 1. 检查缓存
        if use_cache:
            cached = self.cache.get(query, [l.value for l in levels])
            if cached:
                logger.debug("Context retrieved from cache")
                return cached
        
        ***REMOVED*** 2. 从分层存储检索
        contexts = []
        if self.storage:
            for level in levels:
                memories = self.storage.retrieve(query, level, top_k=top_k)
                for memory in memories:
                    contexts.append(memory.content)
        
        ***REMOVED*** 3. 融合上下文
        if contexts:
            fused = self.fusion.fuse(contexts)
            
            ***REMOVED*** 4. 缓存结果
            if use_cache:
                self.cache.put(
                    query,
                    fused,
                    levels=[l.value for l in levels],
                    metadata={"top_k": top_k}
                )
            
            return fused
        else:
            return ""
    
    def cache_context(self, key: str, context: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        缓存上下文
        
        Args:
            key: 缓存键
            context: 上下文内容
            metadata: 元数据
        """
        self.cache.put(key, context, metadata=metadata)
    
    def get_cached_context(self, key: str) -> Optional[str]:
        """
        获取缓存的上下文
        
        Args:
            key: 缓存键
            
        Returns:
            缓存的上下文，如果不存在则返回 None
        """
        return self.cache.get(key)
    
    def clear_cache(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "cache": self.cache.get_statistics()
        }

