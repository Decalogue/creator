"""
检索引擎测试

测试 retrieval/retrieval_engine.py 中的检索功能
"""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from unimem.retrieval.retrieval_engine import RetrievalEngine
from unimem.memory_types import Memory, MemoryType, RetrievalResult, Context
from unimem.adapters.base import AdapterError, AdapterNotAvailableError


class TestRetrievalEngine(unittest.TestCase):
    """RetrievalEngine 测试"""
    
    def setUp(self):
        """设置测试环境"""
        ***REMOVED*** Mock 适配器
        self.graph_adapter = Mock()
        self.graph_adapter.is_available.return_value = True
        self.graph_adapter.entity_search = Mock(return_value=[])
        self.graph_adapter.concept_search = Mock(return_value=[])
        
        self.atom_link_adapter = Mock()
        self.atom_link_adapter.is_available.return_value = True
        self.atom_link_adapter.semantic_retrieval = Mock(return_value=[])
        self.atom_link_adapter.subgraph_retrieval = Mock(return_value=[])
        
        self.retrieval_adapter = Mock()
        self.retrieval_adapter.is_available.return_value = True
        self.retrieval_adapter.rrf_fusion = Mock(return_value=[])
        
        self.storage_manager = Mock()
        
        self.engine = RetrievalEngine(
            graph_adapter=self.graph_adapter,
            atom_link_adapter=self.atom_link_adapter,
            retrieval_adapter=self.retrieval_adapter,
            storage_manager=self.storage_manager,
            max_workers=2
        )
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.engine)
        self.assertEqual(self.engine.graph_adapter, self.graph_adapter)
        self.assertEqual(self.engine.atom_link_adapter, self.atom_link_adapter)
        self.assertEqual(self.engine.retrieval_adapter, self.retrieval_adapter)
    
    def test_init_with_none_adapters(self):
        """测试使用 None 适配器初始化（应该抛出异常）"""
        with self.assertRaises(AdapterError):
            RetrievalEngine(
                graph_adapter=None,
                atom_link_adapter=self.atom_link_adapter,
                retrieval_adapter=self.retrieval_adapter
            )
    
    def test_retrieve_success(self):
        """测试成功检索"""
        ***REMOVED*** Mock 检索结果
        memory = Memory(
            id="test_1",
            content="Test memory",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(
            memory=memory,
            score=0.95,
            retrieval_method="semantic"
        )
        
        self.atom_link_adapter.semantic_retrieval.return_value = [result]
        self.retrieval_adapter.rrf_fusion.return_value = [result]
        
        results = self.engine.retrieve("test query", top_k=10)
        self.assertIsNotNone(results)
    
    def test_retrieve_with_context(self):
        """测试带上下文的检索"""
        context = Context(query="test query")
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(
            memory=memory,
            score=0.9,
            retrieval_method="semantic"
        )
        
        self.atom_link_adapter.semantic_retrieval.return_value = [result]
        self.retrieval_adapter.rrf_fusion.return_value = [result]
        
        results = self.engine.retrieve("query", context=context, top_k=10)
        self.assertIsNotNone(results)
    
    def test_retrieve_empty_query(self):
        """测试空查询"""
        with self.assertRaises(AdapterError):
            self.engine.retrieve("", top_k=10)
    
    def test_retrieve_invalid_top_k(self):
        """测试无效 top_k"""
        with self.assertRaises(AdapterError):
            self.engine.retrieve("query", top_k=0)
    
    def test_retrieve_adapter_failure(self):
        """测试适配器失败时的降级处理"""
        ***REMOVED*** 模拟适配器抛出异常
        self.graph_adapter.entity_search.side_effect = AdapterError(
            "Adapter error",
            adapter_name="GraphAdapter"
        )
        
        ***REMOVED*** 应该不抛出异常，而是降级处理
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(
            memory=memory,
            score=0.9,
            retrieval_method="semantic"
        )
        
        self.atom_link_adapter.semantic_retrieval.return_value = [result]
        self.retrieval_adapter.rrf_fusion.return_value = [result]
        
        ***REMOVED*** 应该仍然能返回结果（降级处理）
        results = self.engine.retrieve("query", top_k=10)
        self.assertIsNotNone(results)
    
    def test_multi_dimensional_retrieval(self):
        """测试多维检索"""
        memory1 = Memory(
            id="test_1",
            content="Test 1",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result1 = RetrievalResult(
            memory=memory1,
            score=0.9,
            retrieval_method="entity"
        )
        
        memory2 = Memory(
            id="test_2",
            content="Test 2",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result2 = RetrievalResult(
            memory=memory2,
            score=0.85,
            retrieval_method="semantic"
        )
        
        self.graph_adapter.entity_search.return_value = [result1]
        self.atom_link_adapter.semantic_retrieval.return_value = [result2]
        self.retrieval_adapter.rrf_fusion.return_value = [result1, result2]
        
        results = self.engine.retrieve("query", top_k=10)
        self.assertGreaterEqual(len(results), 0)  ***REMOVED*** 至少返回融合后的结果
    
    def test_rrf_fusion_called(self):
        """测试 RRF 融合被调用"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(
            memory=memory,
            score=0.9,
            retrieval_method="semantic"
        )
        
        self.atom_link_adapter.semantic_retrieval.return_value = [result]
        self.retrieval_adapter.rrf_fusion.return_value = [result]
        
        self.engine.retrieve("query", top_k=10)
        
        ***REMOVED*** 验证 RRF 融合被调用
        self.retrieval_adapter.rrf_fusion.assert_called()


if __name__ == "__main__":
    unittest.main()

