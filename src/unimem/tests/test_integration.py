"""
集成测试

测试 UniMem 系统的端到端工作流程，验证多个模块的协同工作
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from unimem.core import UniMem
from unimem.memory_types import Experience, Memory, Task, Context, MemoryType
from unimem.adapters.base import AdapterError


class TestUniMemIntegration(unittest.TestCase):
    """UniMem 集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        ***REMOVED*** 创建最小配置的 UniMem 实例
        config = {
            "storage": {
                "foa_backend": "inmemory",
                "foa_max_tokens": 1000,
                "foa_max_memories": 100
            },
            "graph": {
                "backend": "none"  ***REMOVED*** 测试时禁用图数据库
            },
            "vector": {
                "backend": "none"  ***REMOVED*** 测试时禁用向量数据库
            },
            "operation_timeout": 30.0
        }
        
        with patch('unimem.core.UniMem._init_adapters'):
            self.unimem = UniMem(config=config)
            ***REMOVED*** Mock 关键适配器
            self._mock_adapters()
    
    def _mock_adapters(self):
        """Mock 适配器"""
        ***REMOVED*** Mock 操作适配器
        self.unimem.operation_adapter = Mock()
        self.unimem.operation_adapter.is_available.return_value = True
        
        ***REMOVED*** Mock 存储适配器
        self.unimem.storage_adapter = Mock()
        self.unimem.storage_adapter.is_available.return_value = True
        
        ***REMOVED*** Mock 检索引擎
        self.unimem.retrieval_engine = Mock()
        
        ***REMOVED*** Mock 更新管理器
        self.unimem.update_manager = Mock()
    
    def test_retain_recall_workflow(self):
        """测试 RETAIN -> RECALL 完整工作流"""
        ***REMOVED*** 1. RETAIN: 存储新记忆
        experience = Experience(
            content="Python is a programming language",
            timestamp=datetime.now()
        )
        context = Context()
        
        ***REMOVED*** Mock retain 返回
        memory = Memory(
            id="test_1",
            content=experience.content,
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.retain.return_value = memory
        
        stored_memory = self.unimem.retain(experience, context)
        self.assertIsNotNone(stored_memory)
        self.assertEqual(stored_memory.content, experience.content)
        
        ***REMOVED*** 2. RECALL: 检索记忆
        from unimem.memory_types import RetrievalResult
        result = RetrievalResult(
            memory=memory,
            score=0.95,
            retrieval_method="semantic"
        )
        self.unimem.retrieval_engine.retrieve.return_value = [result]
        
        retrieved = self.unimem.recall("Python", top_k=10)
        self.assertIsNotNone(retrieved)
        self.assertGreater(len(retrieved), 0)
        self.assertEqual(retrieved[0].memory.id, "test_1")
    
    def test_retain_reflect_workflow(self):
        """测试 RETAIN -> REFLECT 工作流"""
        ***REMOVED*** 1. RETAIN
        experience = Experience(
            content="Test experience",
            timestamp=datetime.now()
        )
        
        memory = Memory(
            id="test_1",
            content=experience.content,
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.retain.return_value = memory
        
        stored = self.unimem.retain(experience, Context())
        
        ***REMOVED*** 2. REFLECT: 优化记忆
        task = Task(
            id="task_1",
            description="Optimize memory",
            context="Test context"
        )
        
        updated_memory = Memory(
            id="test_1",
            content="Updated content",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.reflect.return_value = [updated_memory]
        
        reflected = self.unimem.reflect([stored], task, Context())
        self.assertIsNotNone(reflected)
        self.assertEqual(len(reflected), 1)
        self.assertEqual(reflected[0].content, "Updated content")
    
    def test_complete_workflow(self):
        """测试完整的 RETAIN -> RECALL -> REFLECT 工作流"""
        ***REMOVED*** 1. RETAIN
        experience = Experience(
            content="Learning Python programming",
            timestamp=datetime.now()
        )
        
        memory = Memory(
            id="mem_1",
            content=experience.content,
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.retain.return_value = memory
        stored = self.unimem.retain(experience, Context())
        
        ***REMOVED*** 2. RECALL
        from unimem.memory_types import RetrievalResult
        result = RetrievalResult(
            memory=memory,
            score=0.9,
            retrieval_method="semantic"
        )
        self.unimem.retrieval_engine.retrieve.return_value = [result]
        retrieved = self.unimem.recall("Python", top_k=5)
        
        ***REMOVED*** 3. REFLECT
        task = Task(
            id="task_1",
            description="Improve understanding",
            context="Learning context"
        )
        updated_memory = Memory(
            id="mem_1",
            content="Enhanced Python knowledge",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.reflect.return_value = [updated_memory]
        reflected = self.unimem.reflect([retrieved[0].memory], task, Context())
        
        ***REMOVED*** 验证整个流程
        self.assertIsNotNone(stored)
        self.assertIsNotNone(retrieved)
        self.assertIsNotNone(reflected)
        self.assertEqual(len(reflected), 1)
    
    def test_health_check_integration(self):
        """测试健康检查集成"""
        health = self.unimem.health_check()
        self.assertIn("status", health)
        self.assertIn("adapters", health)
    
    def test_metrics_collection(self):
        """测试指标收集"""
        ***REMOVED*** 执行一些操作
        experience = Experience(
            content="Test",
            timestamp=datetime.now()
        )
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.retain.return_value = memory
        self.unimem.retain(experience, Context())
        
        metrics = self.unimem.get_metrics()
        self.assertIn("retain", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("reflect", metrics)


class TestStorageRetrievalIntegration(unittest.TestCase):
    """存储和检索集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        from unimem.storage.storage_manager import StorageManager
        
        ***REMOVED*** Mock 存储适配器
        self.storage_adapter = Mock()
        self.storage_adapter.is_available.return_value = True
        self.storage_adapter.add_memory = Mock()
        self.storage_adapter.search_foa = Mock(return_value=[])
        self.storage_adapter.search_da = Mock(return_value=[])
        self.storage_adapter.search_ltm = Mock(return_value=[])
        
        ***REMOVED*** Mock 类型适配器
        self.type_adapter = Mock()
        self.type_adapter.is_available.return_value = True
        
        self.storage_manager = StorageManager(
            storage_adapter=self.storage_adapter,
            type_adapter=self.type_adapter
        )
    
    def test_store_and_retrieve(self):
        """测试存储和检索集成"""
        memory = Memory(
            id="test_1",
            content="Test memory",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        ***REMOVED*** 存储
        self.storage_adapter.add_memory.return_value = memory
        stored = self.storage_manager.add_memory(memory)
        self.assertIsNotNone(stored)
        
        ***REMOVED*** 检索
        self.storage_adapter.search_foa.return_value = [memory]
        retrieved = self.storage_manager.search_foa("test", top_k=10)
        self.assertIsNotNone(retrieved)
        self.assertEqual(len(retrieved), 1)


class TestAdapterIntegration(unittest.TestCase):
    """适配器集成测试"""
    
    def test_operation_storage_integration(self):
        """测试操作适配器和存储适配器集成"""
        from unimem.adapters.operation_adapter import OperationAdapter
        from unimem.storage.storage_manager import StorageManager
        
        ***REMOVED*** Mock 存储管理器
        storage_manager = Mock()
        storage_manager.add_memory = Mock()
        
        ***REMOVED*** 创建操作适配器
        config = {
            "llm_provider": "deepseek",
            "llm_model": "deepseek-v3.2"
        }
        op_adapter = OperationAdapter(config=config)
        
        ***REMOVED*** 创建经验
        experience = Experience(
            content="Test experience",
            timestamp=datetime.now()
        )
        context = Context()
        
        ***REMOVED*** 操作适配器应该能处理经验并返回记忆
        memory = op_adapter.retain(experience, context)
        self.assertIsNotNone(memory)
        
        ***REMOVED*** 存储管理器应该能存储记忆
        storage_manager.add_memory.return_value = memory
        stored = storage_manager.add_memory(memory)
        self.assertIsNotNone(stored)


if __name__ == "__main__":
    unittest.main()

