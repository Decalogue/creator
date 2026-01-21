"""
Agent 智能缓存系统

提供缓存层，减少重复计算和 LLM 调用
"""
import hashlib
import json
import time
from typing import Dict, Any, Optional, Callable, TypeVar, ParamSpec, List
from functools import wraps
from datetime import datetime, timedelta
from collections import OrderedDict
import threading
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')
P = ParamSpec('P')


class LRUCache:
    """
    LRU 缓存实现（线程安全）
    """
    
    def __init__(self, max_size: int = 1000, ttl: Optional[float] = None):
        """
        初始化 LRU 缓存
        
        Args:
            max_size: 最大缓存条目数
            ttl: 缓存过期时间（秒），None 表示不过期
        """
        self.max_size = max_size
        self.ttl = ttl
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            
            ***REMOVED*** 检查是否过期
            if self.ttl and (time.time() - entry['timestamp']) > self.ttl:
                del self._cache[key]
                return None
            
            ***REMOVED*** 移动到末尾（LRU）
            self._cache.move_to_end(key)
            return entry['value']
    
    def set(self, key: str, value: Any):
        """设置缓存值"""
        with self._lock:
            ***REMOVED*** 如果已存在，先删除
            if key in self._cache:
                del self._cache[key]
            ***REMOVED*** 如果超过最大大小，删除最旧的
            elif len(self._cache) >= self.max_size:
                self._cache.popitem(last=False)
            
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        with self._lock:
            return len(self._cache)
    
    def stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._lock:
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl": self.ttl,
            }


class AgentCache:
    """
    Agent 智能缓存系统
    
    提供多种缓存策略：
    - 实体上下文缓存
    - 质量检查结果缓存
    - Prompt 模板缓存
    - 工具结果缓存
    """
    
    def __init__(self):
        """初始化缓存系统"""
        ***REMOVED*** 不同用途的缓存
        self.entity_context_cache = LRUCache(max_size=500, ttl=3600)  ***REMOVED*** 1小时
        self.quality_check_cache = LRUCache(max_size=1000, ttl=1800)  ***REMOVED*** 30分钟
        self.prompt_cache = LRUCache(max_size=100, ttl=86400)  ***REMOVED*** 24小时
        self.tool_result_cache = LRUCache(max_size=200, ttl=600)  ***REMOVED*** 10分钟
        
        ***REMOVED*** 缓存统计
        self._stats = {
            "entity_context": {"hits": 0, "misses": 0},
            "quality_check": {"hits": 0, "misses": 0},
            "prompt": {"hits": 0, "misses": 0},
            "tool_result": {"hits": 0, "misses": 0},
        }
        self._stats_lock = threading.Lock()
    
    def get_entity_context(self, entities: List[str]) -> Optional[str]:
        """
        获取实体上下文（带缓存）
        
        Args:
            entities: 实体列表
        
        Returns:
            缓存的实体上下文，如果不存在则返回 None
        """
        key = self._make_key("entity_context", sorted(entities))
        result = self.entity_context_cache.get(key)
        
        with self._stats_lock:
            if result:
                self._stats["entity_context"]["hits"] += 1
            else:
                self._stats["entity_context"]["misses"] += 1
        
        return result
    
    def set_entity_context(self, entities: List[str], context: str):
        """设置实体上下文缓存"""
        key = self._make_key("entity_context", sorted(entities))
        self.entity_context_cache.set(key, context)
    
    def get_quality_check(self, chapter_content: str) -> Optional[Dict[str, Any]]:
        """
        获取质量检查结果（带缓存）
        
        Args:
            chapter_content: 章节内容
        
        Returns:
            缓存的检查结果，如果不存在则返回 None
        """
        ***REMOVED*** 使用内容哈希作为 key（避免内容过长）
        content_hash = hashlib.md5(chapter_content.encode()).hexdigest()
        key = f"quality_check_{content_hash}"
        result = self.quality_check_cache.get(key)
        
        with self._stats_lock:
            if result:
                self._stats["quality_check"]["hits"] += 1
            else:
                self._stats["quality_check"]["misses"] += 1
        
        return result
    
    def set_quality_check(self, chapter_content: str, result: Dict[str, Any]):
        """设置质量检查结果缓存"""
        content_hash = hashlib.md5(chapter_content.encode()).hexdigest()
        key = f"quality_check_{content_hash}"
        self.quality_check_cache.set(key, result)
    
    def get_prompt(self, prompt_template: str, params: Dict[str, Any]) -> Optional[str]:
        """获取生成的 prompt（带缓存）"""
        key = self._make_key("prompt", prompt_template, params)
        result = self.prompt_cache.get(key)
        
        with self._stats_lock:
            if result:
                self._stats["prompt"]["hits"] += 1
            else:
                self._stats["prompt"]["misses"] += 1
        
        return result
    
    def set_prompt(self, prompt_template: str, params: Dict[str, Any], prompt: str):
        """设置生成的 prompt 缓存"""
        key = self._make_key("prompt", prompt_template, params)
        self.prompt_cache.set(key, prompt)
    
    def _make_key(self, prefix: str, *args) -> str:
        """生成缓存 key"""
        key_str = json.dumps(args, sort_keys=True, ensure_ascii=False)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"{prefix}_{key_hash}"
    
    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        with self._stats_lock:
            stats = {}
            for cache_type, counts in self._stats.items():
                total = counts["hits"] + counts["misses"]
                hit_rate = counts["hits"] / total if total > 0 else 0.0
                stats[cache_type] = {
                    "hits": counts["hits"],
                    "misses": counts["misses"],
                    "hit_rate": hit_rate,
                }
            
            ***REMOVED*** 添加各缓存的容量信息
            stats["entity_context"]["size"] = self.entity_context_cache.size()
            stats["quality_check"]["size"] = self.quality_check_cache.size()
            stats["prompt"]["size"] = self.prompt_cache.size()
            stats["tool_result"]["size"] = self.tool_result_cache.size()
            
            return stats
    
    def clear_all(self):
        """清空所有缓存"""
        self.entity_context_cache.clear()
        self.quality_check_cache.clear()
        self.prompt_cache.clear()
        self.tool_result_cache.clear()
        logger.info("所有缓存已清空")


***REMOVED*** 全局缓存实例
_cache_instance: Optional[AgentCache] = None
_cache_lock = threading.Lock()


def get_agent_cache() -> AgentCache:
    """获取全局 Agent 缓存实例（单例模式）"""
    global _cache_instance
    
    with _cache_lock:
        if _cache_instance is None:
            _cache_instance = AgentCache()
        return _cache_instance


def cached(cache_type: str = "default", ttl: Optional[float] = None):
    """
    缓存装饰器
    
    Args:
        cache_type: 缓存类型（entity_context, quality_check, prompt, tool_result）
        ttl: 缓存过期时间（秒）
    
    Usage:
        @cached(cache_type="entity_context")
        def get_entity_context(entities: List[str]) -> str:
            ...
    """
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        cache = get_agent_cache()
        
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            ***REMOVED*** 生成缓存 key
            key_parts = [func.__name__] + list(args) + [json.dumps(kwargs, sort_keys=True)]
            key = cache._make_key(cache_type, *key_parts)
            
            ***REMOVED*** 尝试从缓存获取
            if cache_type == "entity_context":
                cached_value = cache.entity_context_cache.get(key)
            elif cache_type == "quality_check":
                cached_value = cache.quality_check_cache.get(key)
            elif cache_type == "prompt":
                cached_value = cache.prompt_cache.get(key)
            else:
                cached_value = None
            
            if cached_value is not None:
                logger.debug(f"缓存命中: {func.__name__}")
                return cached_value
            
            ***REMOVED*** 缓存未命中，执行函数
            result = func(*args, **kwargs)
            
            ***REMOVED*** 存入缓存
            if cache_type == "entity_context":
                cache.entity_context_cache.set(key, result)
            elif cache_type == "quality_check":
                cache.quality_check_cache.set(key, result)
            elif cache_type == "prompt":
                cache.prompt_cache.set(key, result)
            
            return result
        
        return wrapper
    return decorator
