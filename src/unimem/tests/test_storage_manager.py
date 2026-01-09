"""
存储管理器测试

测试 storage/storage_manager.py 中的存储管理功能
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from unimem.storage.storage_manager import StorageManager, OperationStats
from unimem.memory_types import Memory, MemoryType, MemoryLayer, Context
from unimem.adapters.base import AdapterError, AdapterNotAvailableError


class TestOperationStats(unittest.TestCase):
    """OperationStats 测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        stats = OperationStats()
        self.assertEqual(stats.count, 0)
        self.assertEqual(stats.success_count, 0)
        self.assertEqual(stats.failure_count, 0)
        self.assertEqual(stats.success_rate, 0.0)
        self.assertEqual(stats.average_time, 0.0)
    
    def test_record_success(self):
        """测试记录成功操作"""
        stats = OperationStats()
        stats.record(0.1, success=True)
        self.assertEqual(stats.count, 1)
        self.assertEqual(stats.success_count, 1)
        self.assertEqual(stats.failure_count, 0)
        self.assertEqual(stats.success_rate, 1.0)
    
    def test_record_failure(self):
        """测试记录失败操作"""
        stats = OperationStats()
        stats.record(0.1, success=False)
        self.assertEqual(stats.count, 1)
        self.assertEqual(stats.success_count, 0)
        self.assertEqual(stats.failure_count, 1)
        self.assertEqual(stats.success_rate, 0.0)
    
    def test_average_time(self):
        """测试平均耗时计算"""
        stats = OperationStats()
        stats.record(0.1, success=True)
        stats.record(0.2, success=True)
        stats.record(0.3, success=True)
        self.assertAlmostEqual(stats.average_time, 0.2, places=2)
    
    def test_min_max_time(self):
        """测试最小最大耗时"""
        stats = OperationStats()
        stats.record(0.3, success=True)
        stats.record(0.1, success=True)
        stats.record(0.2, success=True)
        self.assertEqual(stats.min_time, 0.1)
        self.assertEqual(stats.max_time, 0.3)


class TestStorageManager(unittest.TestCase):
    """StorageManager 测试"""
    
    def setUp(self):
        """设置测试环境"""
        ***REMOVED*** Mock 适配器
        self.storage_adapter = Mock()
        self.storage_adapter.is_available.return_value = True
        self.storage_adapter.add_memory = Mock()
        self.storage_adapter.search_foa = Mock(return_value=[])
        self.storage_adapter.search_da = Mock(return_value=[])
        self.storage_adapter.search_ltm = Mock(return_value=[])
        
        self.type_adapter = Mock()
        self.type_adapter.is_available.return_value = True
        
        self.manager = StorageManager(
            storage_adapter=self.storage_adapter,
            type_adapter=self.type_adapter
        )
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.storage_adapter, self.storage_adapter)
        self.assertEqual(self.manager.type_adapter, self.type_adapter)
    
    def test_add_memory_success(self):
        """测试成功添加记忆"""
        memory = Memory(
            id="test_1",
            content="Test memory",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        self.storage_adapter.add_memory.return_value = memory
        
        result = self.manager.add_memory(memory)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "test_1")
    
    def test_add_memory_invalid(self):
        """测试添加无效记忆"""
        with self.assertRaises(AdapterError):
            self.manager.add_memory(None)
    
    def test_search_foa(self):
        """测试 FoA 层搜索"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE,
            layer=MemoryLayer.FOA
        )
        self.storage_adapter.search_foa.return_value = [memory]
        
        results = self.manager.search_foa("query", top_k=10)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "test_1")
    
    def test_search_da(self):
        """测试 DA 层搜索"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE,
            layer=MemoryLayer.DA
        )
        self.storage_adapter.search_da.return_value = [memory]
        
        results = self.manager.search_da("query", top_k=10)
        self.assertEqual(len(results), 1)
    
    def test_search_ltm(self):
        """测试 LTM 层搜索"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE,
            layer=MemoryLayer.LTM
        )
        self.storage_adapter.search_ltm.return_value = [memory]
        
        results = self.manager.search_ltm("query", top_k=10)
        self.assertEqual(len(results), 1)
    
    def test_update_memory(self):
        """测试更新记忆"""
        memory = Memory(
            id="test_1",
            content="Updated",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.storage_adapter.update_memory = Mock(return_value=memory)
        
        result = self.manager.update_memory(memory)
        self.assertIsNotNone(result)
    
    def test_cleanup(self):
        """测试清理操作"""
        self.storage_adapter.cleanup_foa = Mock()
        
        self.manager.cleanup(max_age_hours=24)
        self.storage_adapter.cleanup_foa.assert_called_once()
    
    def test_get_metrics(self):
        """测试获取指标"""
        ***REMOVED*** 执行一些操作
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.manager.add_memory(memory)
        
        metrics = self.manager.get_metrics()
        self.assertIn("add_memory", metrics)
        self.assertIn("search_foa", metrics)
    
    def test_health_check(self):
        """测试健康检查"""
        health = self.manager.health_check()
        self.assertIn("status", health)
        self.assertIn("storage_adapter", health)
    
    def test_adapter_not_available(self):
        """测试适配器不可用"""
        self.storage_adapter.is_available.return_value = False
        
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        ***REMOVED*** 应该抛出异常或返回 None（取决于实现）
        with self.assertRaises(AdapterNotAvailableError):
            self.manager.add_memory(memory)


if __name__ == "__main__":
    unittest.main()

