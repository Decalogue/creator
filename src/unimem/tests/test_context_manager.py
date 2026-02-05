"""
上下文管理器测试

测试 context/context_manager.py 中的上下文管理功能
"""

import unittest
from unittest.mock import Mock, MagicMock

from unimem.context.context_manager import ContextManager
from unimem.adapters.base import AdapterError


class TestContextManager(unittest.TestCase):
    """ContextManager 测试"""
    
    def setUp(self):
        """设置测试环境"""
        # Mock LLM 函数
        self.mock_llm = Mock(return_value="Compressed content")
        
        # Mock 存储
        self.mock_storage = Mock()
        
        self.manager = ContextManager(
            hierarchical_storage=self.mock_storage,
            llm_func=self.mock_llm
        )
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.storage, self.mock_storage)
    
    def test_compress_success(self):
        """测试成功压缩"""
        content = "This is a long content that needs to be compressed"
        compressed = self.manager.compress(content, target_length=20)
        self.assertIsNotNone(compressed)
    
    def test_compress_empty_content(self):
        """测试空内容压缩"""
        with self.assertRaises(AdapterError):
            self.manager.compress("", target_length=20)
    
    def test_compress_invalid_target_length(self):
        """测试无效目标长度"""
        with self.assertRaises(AdapterError):
            self.manager.compress("content", target_length=0)
    
    def test_fuse_success(self):
        """测试成功融合"""
        contexts = ["Context 1", "Context 2", "Context 3"]
        fused = self.manager.fuse(contexts)
        self.assertIsNotNone(fused)
    
    def test_fuse_empty_list(self):
        """测试空列表融合"""
        with self.assertRaises(AdapterError):
            self.manager.fuse([])
    
    def test_fuse_invalid_max_length(self):
        """测试无效最大长度"""
        with self.assertRaises(AdapterError):
            self.manager.fuse(["context"], max_length=0)
    
    def test_retrieve_context(self):
        """测试检索上下文"""
        # Mock 存储返回结果
        from unimem.memory_types import Memory, MemoryType
        from datetime import datetime
        
        memory = Memory(
            id="test_1",
            content="Test memory",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.mock_storage.retrieve.return_value = [memory]
        
        result = self.manager.retrieve_context("query", top_k=10)
        self.assertIsNotNone(result)
    
    def test_get_cached_context(self):
        """测试获取缓存的上下文"""
        # 先设置缓存
        query = "test query"
        context = "cached context"
        
        # 通过检索设置缓存
        from unimem.memory_types import Memory, MemoryType
        from datetime import datetime
        
        memory = Memory(
            id="test_1",
            content=context,
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.mock_storage.retrieve.return_value = [memory]
        
        # 第一次检索（会缓存）
        result1 = self.manager.retrieve_context(query, top_k=10)
        
        # 第二次检索（应该使用缓存）
        result2 = self.manager.retrieve_context(query, top_k=10)
        self.assertIsNotNone(result2)
    
    def test_clear_cache(self):
        """测试清理缓存"""
        self.manager.clear_cache()
        # 应该不抛出异常


if __name__ == "__main__":
    unittest.main()

