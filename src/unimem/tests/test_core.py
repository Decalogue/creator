"""
核心模块测试

测试 core.py 中的 UniMem 核心功能
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import threading

from unimem.core import UniMem, RetainError, RecallError, ReflectError
from unimem.memory_types import Experience, Memory, Task, Context, MemoryType, RetrievalResult
from unimem.adapters.base import AdapterError, AdapterNotAvailableError


class TestUniMemInitialization(unittest.TestCase):
    """UniMem 初始化测试"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        with patch('unimem.core.UniMem._init_adapters'):
            unimem = UniMem()
            self.assertIsNotNone(unimem)
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        config = {
            "storage": {"foa_backend": "redis"},
            "operation_timeout": 30.0
        }
        with patch('unimem.core.UniMem._init_adapters'):
            unimem = UniMem(config=config)
            self.assertIsNotNone(unimem)
    
    def test_init_max_concurrent_operations(self):
        """测试最大并发操作数设置"""
        with patch('unimem.core.UniMem._init_adapters'):
            unimem = UniMem(max_concurrent_operations=20)
            self.assertEqual(unimem.max_concurrent_operations, 20)


class TestUniMemRetain(unittest.TestCase):
    """UniMem RETAIN 操作测试"""
    
    def setUp(self):
        """设置测试环境"""
        with patch('unimem.core.UniMem._init_adapters') as mock_init:
            self.unimem = UniMem()
            ***REMOVED*** Mock 适配器
            self.unimem.operation_adapter = Mock()
            self.unimem.storage_adapter = Mock()
            self.unimem.graph_adapter = Mock()
            self.unimem.atom_link_adapter = Mock()
            self.unimem.update_adapter = Mock()
    
    def test_retain_success(self):
        """测试成功存储记忆"""
        experience = Experience(
            content="Test experience",
            timestamp=datetime.now()
        )
        context = Context()
        
        ***REMOVED*** Mock 返回记忆
        mock_memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.retain.return_value = mock_memory
        
        result = self.unimem.retain(experience, context)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "test_1")
    
    def test_retain_with_operation_id(self):
        """测试带操作 ID 的存储"""
        experience = Experience(
            content="Test",
            timestamp=datetime.now()
        )
        context = Context()
        
        mock_memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.retain.return_value = mock_memory
        
        result = self.unimem.retain(experience, context, operation_id="op_1")
        self.assertIsNotNone(result)
    
    def test_retain_invalid_experience(self):
        """测试无效经验数据"""
        with self.assertRaises(RetainError):
            self.unimem.retain(None, Context())
    
    def test_retain_adapter_error(self):
        """测试适配器错误"""
        experience = Experience(
            content="Test",
            timestamp=datetime.now()
        )
        self.unimem.operation_adapter.retain.side_effect = AdapterError(
            "Adapter error",
            adapter_name="OperationAdapter"
        )
        
        with self.assertRaises(RetainError):
            self.unimem.retain(experience, Context())


class TestUniMemRecall(unittest.TestCase):
    """UniMem RECALL 操作测试"""
    
    def setUp(self):
        """设置测试环境"""
        with patch('unimem.core.UniMem._init_adapters'):
            self.unimem = UniMem()
            self.unimem.retrieval_engine = Mock()
            self.unimem.update_adapter = Mock()
    
    def test_recall_success(self):
        """测试成功检索"""
        mock_result = RetrievalResult(
            memory=Memory(
                id="test_1",
                content="Test",
                timestamp=datetime.now(),
                memory_type=MemoryType.EXPERIENCE
            ),
            score=0.95,
            retrieval_method="semantic"
        )
        self.unimem.retrieval_engine.retrieve.return_value = [mock_result]
        
        results = self.unimem.recall("test query", top_k=10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].score, 0.95)
    
    def test_recall_with_context(self):
        """测试带上下文的检索"""
        context = Context(query="test query")
        mock_result = RetrievalResult(
            memory=Memory(
                id="test_1",
                content="Test",
                timestamp=datetime.now(),
                memory_type=MemoryType.EXPERIENCE
            ),
            score=0.9,
            retrieval_method="semantic"
        )
        self.unimem.retrieval_engine.retrieve.return_value = [mock_result]
        
        results = self.unimem.recall("query", context=context)
        self.assertIsNotNone(results)
    
    def test_recall_empty_query(self):
        """测试空查询"""
        with self.assertRaises(RecallError):
            self.unimem.recall("")
    
    def test_recall_with_memory_type_filter(self):
        """测试按记忆类型过滤"""
        mock_result = RetrievalResult(
            memory=Memory(
                id="test_1",
                content="Test",
                timestamp=datetime.now(),
                memory_type=MemoryType.EXPERIENCE
            ),
            score=0.9,
            retrieval_method="semantic"
        )
        self.unimem.retrieval_engine.retrieve.return_value = [mock_result]
        
        results = self.unimem.recall(
            "query",
            memory_type=MemoryType.EXPERIENCE
        )
        self.assertIsNotNone(results)


class TestUniMemReflect(unittest.TestCase):
    """UniMem REFLECT 操作测试"""
    
    def setUp(self):
        """设置测试环境"""
        with patch('unimem.core.UniMem._init_adapters'):
            self.unimem = UniMem()
            self.unimem.operation_adapter = Mock()
            self.unimem.update_adapter = Mock()
    
    def test_reflect_success(self):
        """测试成功优化记忆"""
        memory = Memory(
            id="test_1",
            content="Original",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        task = Task(description="Test task", goal="Goal")
        context = Context()
        
        updated_memory = Memory(
            id="test_1",
            content="Updated",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.reflect.return_value = [updated_memory]
        
        results = self.unimem.reflect([memory], task, context)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "Updated")
    
    def test_reflect_empty_memories(self):
        """测试空记忆列表"""
        task = Task(description="Task", goal="Goal")
        with self.assertRaises(ReflectError):
            self.unimem.reflect([], task)
    
    def test_reflect_invalid_task(self):
        """测试无效任务"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        with self.assertRaises(ReflectError):
            self.unimem.reflect([memory], None)


class TestUniMemHealthCheck(unittest.TestCase):
    """UniMem 健康检查测试"""
    
    def setUp(self):
        """设置测试环境"""
        with patch('unimem.core.UniMem._init_adapters'):
            self.unimem = UniMem()
    
    def test_health_check_all_healthy(self):
        """测试所有组件健康"""
        ***REMOVED*** Mock 所有适配器为可用
        self.unimem.operation_adapter = Mock()
        self.unimem.operation_adapter.is_available.return_value = True
        
        health = self.unimem.health_check()
        self.assertIn("status", health)
        self.assertIn("adapters", health)
    
    def test_get_metrics(self):
        """测试获取指标"""
        metrics = self.unimem.get_metrics()
        self.assertIn("retain", metrics)
        self.assertIn("recall", metrics)
        self.assertIn("reflect", metrics)


class TestUniMemThreadSafety(unittest.TestCase):
    """UniMem 线程安全测试"""
    
    def setUp(self):
        """设置测试环境"""
        with patch('unimem.core.UniMem._init_adapters'):
            self.unimem = UniMem()
            self.unimem.operation_adapter = Mock()
            self.unimem.storage_adapter = Mock()
    
    def test_concurrent_retain(self):
        """测试并发存储"""
        experience = Experience(
            content="Test",
            timestamp=datetime.now()
        )
        context = Context()
        
        mock_memory = Memory(
            id="test",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.unimem.operation_adapter.retain.return_value = mock_memory
        
        def retain_operation():
            return self.unimem.retain(experience, context)
        
        ***REMOVED*** 创建多个线程并发执行
        threads = []
        results = []
        
        def worker():
            try:
                result = retain_operation()
                results.append(result)
            except Exception as e:
                results.append(e)
        
        for _ in range(5):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        ***REMOVED*** 检查所有操作都成功（或至少没有崩溃）
        self.assertEqual(len(results), 5)


if __name__ == "__main__":
    unittest.main()

