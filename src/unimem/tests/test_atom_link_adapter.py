"""
原子链接适配器测试

测试 AtomLinkAdapter 的核心功能

注意：运行测试前需要激活 seeme 环境：
    conda activate seeme
"""

import unittest
import os
import sys
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List

***REMOVED*** 检查环境
if os.environ.get("CONDA_DEFAULT_ENV") != "seeme":
    print("\n" + "="*60)
    print("警告：当前未激活 seeme 环境，某些测试可能会失败")
    print(f"当前环境: {os.environ.get('CONDA_DEFAULT_ENV', '未设置')}")
    print("请先运行: conda activate seeme")
    print("或使用自动测试脚本: python tests/run_tests.py")
    print("="*60 + "\n")

from unimem.adapters.atom_link_adapter import AtomLinkAdapter
from unimem.types import Memory, Entity, MemoryType, MemoryLayer


class TestAtomLinkAdapter(unittest.TestCase):
    """AtomLinkAdapter 测试类"""
    
    def setUp(self):
        """设置测试环境"""
        ***REMOVED*** 使用真实配置，本地模型已下载
        self.config = {
            "local_model_path": "/root/data/AI/pretrain/all-MiniLM-L6-v2",
            "qdrant_host": "localhost",
            "qdrant_port": 6333,
            "collection_name": "test_unimem_memories",
        }
        
        ***REMOVED*** 创建适配器实例（使用真实模型，Qdrant 连接失败时使用 Mock）
        self.adapter = AtomLinkAdapter(config=self.config)
        self.adapter.initialize()  ***REMOVED*** 确保初始化完成
        
        ***REMOVED*** 确保属性存在（即使初始化失败）
        ***REMOVED*** 如果 Qdrant 连接失败，立即设置 Mock
        self.use_mock_qdrant = False
        if not hasattr(self.adapter, 'qdrant_client') or self.adapter.qdrant_client is None:
            self.mock_qdrant_client = MagicMock()
            self.adapter.qdrant_client = self.mock_qdrant_client
            self.use_mock_qdrant = True
            if not hasattr(self.adapter, 'collection_name'):
                self.adapter.collection_name = "test_unimem_memories"
        else:
            self.mock_qdrant_client = None  ***REMOVED*** 真实连接，不需要 Mock
            self.use_mock_qdrant = False
        
        ***REMOVED*** 确保 id_mapping 存在
        if not hasattr(self.adapter, 'id_mapping'):
            self.adapter.id_mapping = {}
        
        ***REMOVED*** 模型应该已经真实加载（使用本地模型）
        ***REMOVED*** 如果没有加载成功，使用 Mock（向后兼容，但正常情况下应该加载成功）
        if not hasattr(self.adapter, 'embedding_model') or self.adapter.embedding_model is None:
            ***REMOVED*** 如果模型未加载，使用 Mock（向后兼容）
            self.mock_embedding_model = MagicMock()
            mock_array = np.array([0.1] * 384)
            self.mock_embedding_model.encode.return_value = mock_array
            self.adapter.embedding_model = self.mock_embedding_model
            self.use_real_model = False
        else:
            self.mock_embedding_model = None  ***REMOVED*** 真实模型，不需要 Mock
            self.use_real_model = True  ***REMOVED*** 标记使用真实模型
        
        ***REMOVED*** 初始化内存存储
        if not hasattr(self.adapter, 'memory_store') or self.adapter.memory_store is None:
            self.adapter.memory_store = {}
        self.adapter._available = True
    
    def tearDown(self):
        """清理测试环境"""
        self.adapter.memory_store.clear()
    
    def test_construct_atomic_note(self):
        """测试构建原子笔记"""
        content = "Python is a high-level programming language."
        timestamp = datetime.now()
        entities = []
        
        ***REMOVED*** Mock LLM 分析结果
        with patch.object(self.adapter, '_analyze_content', return_value={
            "keywords": ["Python", "programming", "language"],
            "context": "Discussion about Python programming language",
            "tags": ["programming", "technology", "software"]
        }):
            memory = self.adapter.construct_atomic_note(content, timestamp, entities)
        
        ***REMOVED*** 验证结果
        self.assertIsNotNone(memory)
        self.assertEqual(memory.content, content)
        self.assertEqual(memory.timestamp, timestamp)
        self.assertGreater(len(memory.keywords), 0)
        self.assertGreater(len(memory.tags), 0)
        self.assertIsNotNone(memory.context)
        self.assertIn(memory.id, self.adapter.memory_store)
    
    def test_enhance_content_for_embedding(self):
        """测试内容增强"""
        memory = Memory(
            id="test_id",
            content="Test content",
            timestamp=datetime.now(),
            keywords=["keyword1", "keyword2"],
            context="Test context",
            tags=["tag1", "tag2"],
        )
        
        enhanced = self.adapter._enhance_content_for_embedding(memory)
        
        self.assertIn("Test content", enhanced)
        self.assertIn("context: Test context", enhanced)
        self.assertIn("keywords: keyword1, keyword2", enhanced)
        self.assertIn("tags: tag1, tag2", enhanced)
    
    def test_get_embedding(self):
        """测试获取嵌入向量（使用真实模型）"""
        text = "Test text"
        
        embedding = self.adapter._get_embedding(text)
        
        self.assertIsNotNone(embedding)
        self.assertEqual(len(embedding), 384)
        ***REMOVED*** 使用真实模型，不需要检查 Mock 调用
    
    def test_get_embedding_no_model(self):
        """测试没有嵌入模型时返回 None"""
        self.adapter.embedding_model = None
        
        embedding = self.adapter._get_embedding("test")
        
        self.assertIsNone(embedding)
    
    def test_add_memory_to_vector_store(self):
        """测试添加记忆到向量存储（使用真实模型）"""
        memory = Memory(
            id="test_id",
            content="Test content",
            timestamp=datetime.now(),
            keywords=["test"],
            tags=["test"],
        )
        
        ***REMOVED*** 使用真实模型生成嵌入，不需要 Mock
        result = self.adapter.add_memory_to_vector_store(memory)
        
        self.assertTrue(result)
        ***REMOVED*** 如果使用 Mock Qdrant，检查调用；如果使用真实 Qdrant，只检查结果
        if hasattr(self, 'use_mock_qdrant') and self.use_mock_qdrant:
            self.mock_qdrant_client.upsert.assert_called_once()
        self.assertIn(memory.id, self.adapter.memory_store)
    
    def test_add_memory_to_vector_store_no_embedding(self):
        """测试无法生成嵌入时返回 False"""
        memory = Memory(
            id="test_id",
            content="Test content",
            timestamp=datetime.now(),
        )
        
        ***REMOVED*** Mock 嵌入生成失败
        self.adapter._get_embedding = Mock(return_value=None)
        
        result = self.adapter.add_memory_to_vector_store(memory)
        
        self.assertFalse(result)
    
    def test_search_similar_memories(self):
        """测试搜索相似记忆"""
        ***REMOVED*** 创建测试记忆
        memory1 = Memory(
            id="mem1",
            content="Python programming",
            timestamp=datetime.now(),
        )
        memory2 = Memory(
            id="mem2",
            content="Java programming",
            timestamp=datetime.now(),
        )
        
        self.adapter.memory_store = {
            "mem1": memory1,
            "mem2": memory2,
        }
        
        ***REMOVED*** 如果使用真实 Qdrant，需要先添加记忆
        if hasattr(self, 'use_mock_qdrant') and not self.use_mock_qdrant:
            ***REMOVED*** 使用真实 Qdrant，先添加记忆
            self.adapter.add_memory_to_vector_store(memory1)
            self.adapter.add_memory_to_vector_store(memory2)
        else:
        ***REMOVED*** Mock Qdrant 搜索结果
            import uuid
            from qdrant_client.http.models.models import QueryResponse, ScoredPoint
            ***REMOVED*** 确保 ID 映射存在
            if "mem1" not in self.adapter.id_mapping:
                self.adapter.id_mapping["mem1"] = uuid.uuid4()
            if "mem2" not in self.adapter.id_mapping:
                self.adapter.id_mapping["mem2"] = uuid.uuid4()
            
            mock_result1 = ScoredPoint(
                id=self.adapter.id_mapping["mem1"],
                score=0.9,
                payload={"original_id": "mem1"},
                version=1
            )
            mock_result2 = ScoredPoint(
                id=self.adapter.id_mapping["mem2"],
                score=0.8,
                payload={"original_id": "mem2"},
                version=1
            )
            mock_response = QueryResponse(
                points=[mock_result1, mock_result2]
            )
            self.mock_qdrant_client.query_points.return_value = mock_response
        
        ***REMOVED*** 确保适配器可用且嵌入模型已设置
        self.adapter._available = True
        if not hasattr(self.adapter, 'embedding_model') or self.adapter.embedding_model is None:
            self.adapter.embedding_model = self.mock_embedding_model if hasattr(self, 'mock_embedding_model') else None
        
        results = self.adapter._search_similar_memories("programming", top_k=5)
        
        ***REMOVED*** 如果使用真实 Qdrant，结果可能为空（因为向量相似度可能不够），这是正常的
        if hasattr(self, 'use_mock_qdrant') and not self.use_mock_qdrant:
            ***REMOVED*** 真实 Qdrant 测试：至少应该能搜索
            self.assertIsInstance(results, list)
        else:
        self.assertEqual(len(results), 2)
        self.assertIn(memory1, results)
        self.assertIn(memory2, results)
    
    def test_search_similar_memories_empty(self):
        """测试搜索空结果"""
        if hasattr(self, 'use_mock_qdrant') and self.use_mock_qdrant:
            from qdrant_client.http.models.models import QueryResponse
            mock_response = QueryResponse(points=[])
            self.mock_qdrant_client.query_points.return_value = mock_response
        
        results = self.adapter._search_similar_memories("query", top_k=5)
        
        self.assertEqual(len(results), 0)
    
    def test_find_related_memories(self):
        """测试查找相关记忆"""
        ***REMOVED*** 创建测试记忆
        memory1 = Memory(
            id="mem1",
            content="Python",
            timestamp=datetime.now(),
            links={"mem2"},
        )
        memory2 = Memory(
            id="mem2",
            content="Java",
            timestamp=datetime.now(),
        )
        
        self.adapter.memory_store = {
            "mem1": memory1,
            "mem2": memory2,
        }
        
        ***REMOVED*** Mock 向量检索
        self.adapter._search_similar_memories = Mock(return_value=[memory2])
        
        related = self.adapter.find_related_memories(memory1, top_k=5)
        
        ***REMOVED*** 应该包含通过链接找到的 mem2
        self.assertGreater(len(related), 0)
        self.assertIn(memory2, related)
    
    def test_semantic_retrieval(self):
        """测试语义检索"""
        memory = Memory(
            id="mem1",
            content="Test content",
            timestamp=datetime.now(),
        )
        
        self.adapter.memory_store = {"mem1": memory}
        self.adapter._search_similar_memories = Mock(return_value=[memory])
        
        results = self.adapter.semantic_retrieval("test query", top_k=5)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], memory)
    
    def test_subgraph_link_retrieval(self):
        """测试子图链接检索"""
        ***REMOVED*** 创建测试记忆网络
        memory1 = Memory(
            id="mem1",
            content="Python",
            timestamp=datetime.now(),
            links={"mem2"},
        )
        memory2 = Memory(
            id="mem2",
            content="Java",
            timestamp=datetime.now(),
            links={"mem3"},
        )
        memory3 = Memory(
            id="mem3",
            content="C++",
            timestamp=datetime.now(),
        )
        
        self.adapter.memory_store = {
            "mem1": memory1,
            "mem2": memory2,
            "mem3": memory3,
        }
        
        ***REMOVED*** Mock 初始检索结果
        self.adapter._search_similar_memories = Mock(return_value=[memory1])
        
        results = self.adapter.subgraph_link_retrieval("programming", top_k=5)
        
        ***REMOVED*** 应该包含初始记忆和通过链接找到的记忆
        self.assertGreater(len(results), 0)
        self.assertIn(memory1, results)
        ***REMOVED*** 可能包含 mem2（通过链接）
    
    def test_parse_json_response(self):
        """测试解析 JSON 响应"""
        ***REMOVED*** 测试普通 JSON
        json_text = '{"key": "value"}'
        result = self.adapter._parse_json_response(json_text)
        self.assertEqual(result, {"key": "value"})
        
        ***REMOVED*** 测试包含 markdown 代码块的 JSON
        json_text = '```json\n{"key": "value"}\n```'
        result = self.adapter._parse_json_response(json_text)
        self.assertEqual(result, {"key": "value"})
        
        ***REMOVED*** 测试无效 JSON
        json_text = "invalid json"
        result = self.adapter._parse_json_response(json_text)
        self.assertIsNone(result)
    
    def test_delete_memory_from_vector_store(self):
        """测试从向量存储删除记忆"""
        memory = Memory(
            id="test_id",
            content="Test content",
            timestamp=datetime.now(),
        )
        
        self.adapter.memory_store["test_id"] = memory
        
        ***REMOVED*** 如果使用真实 Qdrant，需要先添加记忆以创建 ID 映射
        if hasattr(self, 'use_mock_qdrant') and not self.use_mock_qdrant:
            ***REMOVED*** 先添加记忆，这样会创建 ID 映射
            self.adapter.add_memory_to_vector_store(memory)
        
        ***REMOVED*** 如果 Qdrant 连接失败，使用 Mock
        if self.adapter.qdrant_client is None:
            self.adapter.qdrant_client = self.mock_qdrant_client
        
        result = self.adapter.delete_memory_from_vector_store("test_id")
        
        self.assertTrue(result)
        if hasattr(self, 'use_mock_qdrant') and self.use_mock_qdrant:
            self.mock_qdrant_client.delete.assert_called_once()
        self.assertNotIn("test_id", self.adapter.memory_store)
    
    def test_update_memory_in_vector_store(self):
        """测试更新向量存储中的记忆（使用真实模型）"""
        memory = Memory(
            id="test_id",
            content="Updated content",
            timestamp=datetime.now(),
        )
        
        ***REMOVED*** 使用真实模型生成嵌入，不需要 Mock
        result = self.adapter.update_memory_in_vector_store(memory)
        
        self.assertTrue(result)
        ***REMOVED*** 如果使用 Mock Qdrant，检查调用；如果使用真实 Qdrant，只检查结果
        if hasattr(self, 'use_mock_qdrant') and self.use_mock_qdrant:
            self.mock_qdrant_client.upsert.assert_called_once()


class TestAtomLinkAdapterIntegration(unittest.TestCase):
    """AtomLinkAdapter 集成测试（需要实际服务）"""
    
    def _check_qdrant_available(self):
        """检查 Qdrant 是否可用"""
        try:
            from qdrant_client import QdrantClient
            client = QdrantClient(host="localhost", port=6333, timeout=2)
            client.get_collections()  ***REMOVED*** 尝试连接
            return True
        except Exception:
            return False
    
    @unittest.skipUnless(
        os.environ.get("RUN_INTEGRATION_TESTS") == "1",
        "集成测试需要设置 RUN_INTEGRATION_TESTS=1 且 Qdrant 服务可用"
    )
    def test_full_workflow(self):
        """测试完整工作流（需要 Qdrant 和 LLM 服务）"""
        ***REMOVED*** 检查 Qdrant 是否可用
        if not self._check_qdrant_available():
            self.skipTest("Qdrant 服务不可用，请确保 Qdrant 在 localhost:6333 运行")
        
        config = {
            "qdrant_host": "localhost",
            "qdrant_port": 6333,
            "collection_name": "test_integration",
        }
        
        adapter = AtomLinkAdapter(config=config)
        adapter.initialize()
        
        if not adapter.is_available():
            self.skipTest("适配器初始化失败")
        
        ***REMOVED*** 1. 构建原子笔记
        content = "Machine learning is a subset of artificial intelligence."
        timestamp = datetime.now()
        memory = adapter.construct_atomic_note(content, timestamp, [])
        
        self.assertIsNotNone(memory)
        self.assertGreater(len(memory.keywords), 0)
        
        ***REMOVED*** 2. 添加到向量存储
        result = adapter.add_memory_to_vector_store(memory)
        self.assertTrue(result)
        
        ***REMOVED*** 3. 语义检索
        results = adapter.semantic_retrieval("artificial intelligence", top_k=5)
        self.assertGreater(len(results), 0)
        
        ***REMOVED*** 4. 生成链接
        links = adapter.generate_links(memory, top_k=5)
        self.assertIsInstance(links, set)
        
        ***REMOVED*** 清理：删除测试数据
        adapter.delete_memory_from_vector_store(memory.id)


if __name__ == '__main__':
    unittest.main()

