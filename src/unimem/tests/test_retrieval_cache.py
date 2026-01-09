"""
检索缓存测试

测试 retrieval/retrieval_cache.py 中的缓存功能
"""

import unittest
from unittest.mock import Mock
from datetime import datetime, timedelta

from unimem.retrieval.retrieval_cache import RetrievalCache, CacheEntry
from unimem.memory_types import Memory, MemoryType, RetrievalResult


class TestCacheEntry(unittest.TestCase):
    """CacheEntry 测试"""
    
    def test_create_entry(self):
        """测试创建缓存条目"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(memory=memory, score=0.9, retrieval_method="test")
        
        entry = CacheEntry(
            query_hash="hash123",
            results=[result]
        )
        self.assertEqual(entry.query_hash, "hash123")
        self.assertEqual(len(entry.results), 1)
        self.assertEqual(entry.access_count, 0)
    
    def test_access(self):
        """测试访问记录"""
        entry = CacheEntry(query_hash="hash123", results=[])
        entry.access()
        self.assertEqual(entry.access_count, 1)
        self.assertIsNotNone(entry.last_accessed)


class TestRetrievalCache(unittest.TestCase):
    """RetrievalCache 测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.cache = RetrievalCache(max_size=10, ttl_seconds=3600)
    
    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.cache.max_size, 10)
        self.assertEqual(self.cache.ttl_seconds, 3600)
        self.assertTrue(self.cache.enable_lru)
    
    def test_set_and_get(self):
        """测试设置和获取缓存"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(memory=memory, score=0.9, retrieval_method="test")
        results = [result]
        
        # 设置缓存
        self.cache.set("test query", results)
        
        # 获取缓存
        cached = self.cache.get("test query")
        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0].score, 0.9)
    
    def test_cache_miss(self):
        """测试缓存未命中"""
        cached = self.cache.get("nonexistent query")
        self.assertIsNone(cached)
    
    def test_cache_ttl_expiry(self):
        """测试 TTL 过期"""
        cache = RetrievalCache(max_size=10, ttl_seconds=1)  # 1秒过期
        
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(memory=memory, score=0.9, retrieval_method="test")
        
        cache.set("test query", [result])
        
        # 立即获取应该命中
        cached = cache.get("test query")
        self.assertIsNotNone(cached)
        
        # 等待过期（这里简化处理，实际测试中可以用 time.sleep）
        # 或者直接修改 created_at 时间
        import time
        time.sleep(1.1)
        
        # 过期后应该未命中
        cached = cache.get("test query")
        self.assertIsNone(cached)
    
    def test_lru_eviction(self):
        """测试 LRU 淘汰"""
        cache = RetrievalCache(max_size=2, enable_lru=True)
        
        # 添加两个条目
        for i in range(2):
            memory = Memory(
                id=f"test_{i}",
                content=f"Test {i}",
                timestamp=datetime.now(),
                memory_type=MemoryType.EXPERIENCE
            )
            result = RetrievalResult(memory=memory, score=0.9, retrieval_method="test")
            cache.set(f"query_{i}", [result])
        
        # 添加第三个条目，应该淘汰最旧的
        memory = Memory(
            id="test_2",
            content="Test 2",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(memory=memory, score=0.9, retrieval_method="test")
        cache.set("query_2", [result])
        
        # 第一个应该被淘汰
        cached = cache.get("query_0")
        self.assertIsNone(cached)
    
    def test_clear(self):
        """测试清空缓存"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(memory=memory, score=0.9, retrieval_method="test")
        
        self.cache.set("test query", [result])
        self.cache.clear()
        
        cached = self.cache.get("test query")
        self.assertIsNone(cached)
    
    def test_get_stats(self):
        """测试获取统计信息"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(memory=memory, score=0.9, retrieval_method="test")
        
        # 设置并获取（命中）
        self.cache.set("test query", [result])
        self.cache.get("test query")
        
        # 获取不存在的（未命中）
        self.cache.get("nonexistent")
        
        stats = self.cache.get_stats()
        self.assertIn("hits", stats)
        self.assertIn("misses", stats)
        self.assertGreater(stats["hits"], 0)
        self.assertGreater(stats["misses"], 0)


if __name__ == "__main__":
    unittest.main()

