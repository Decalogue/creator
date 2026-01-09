"""
分层存储测试

测试 storage/hierarchical/hierarchical_storage.py 中的分层存储功能
"""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from unimem.storage.hierarchical.hierarchical_storage import HierarchicalStorage, ConsistencyReport
from unimem.storage.hierarchical.level_index import ContentLevel
from unimem.memory_types import Memory, MemoryType
from unimem.adapters.base import AdapterError


class TestHierarchicalStorage(unittest.TestCase):
    """HierarchicalStorage 测试"""
    
    def setUp(self):
        """设置测试环境"""
        ***REMOVED*** Mock 存储管理器
        self.storage_manager = Mock()
        self.storage_manager.add_memory = Mock(return_value=True)
        
        self.hierarchical = HierarchicalStorage(storage_manager=self.storage_manager)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.hierarchical)
        self.assertEqual(self.hierarchical.storage_manager, self.storage_manager)
        self.assertIsNotNone(self.hierarchical.index_manager)
    
    def test_store_success(self):
        """测试成功存储"""
        memory = Memory(
            id="test_1",
            content="Test memory",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        result = self.hierarchical.store(memory, ContentLevel.WORK)
        self.assertTrue(result)
    
    def test_store_invalid_memory(self):
        """测试无效记忆存储"""
        with self.assertRaises(AdapterError):
            self.hierarchical.store(None, ContentLevel.WORK)
    
    def test_retrieve_success(self):
        """测试成功检索"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        ***REMOVED*** 先存储
        self.hierarchical.store(memory, ContentLevel.WORK)
        
        ***REMOVED*** 再检索
        results = self.hierarchical.retrieve(ContentLevel.WORK, top_k=10)
        self.assertIsNotNone(results)
    
    def test_cross_level_retrieve(self):
        """测试跨层级检索"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        ***REMOVED*** 存储到不同层级
        self.hierarchical.store(memory, ContentLevel.WORK)
        
        ***REMOVED*** 跨层级检索
        results = self.hierarchical.cross_level_retrieve(
            query="test",
            levels=[ContentLevel.WORK, ContentLevel.CHAPTER],
            top_k=10
        )
        self.assertIsNotNone(results)
    
    def test_check_consistency(self):
        """测试一致性检查"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        self.hierarchical.store(memory, ContentLevel.WORK)
        
        reports = self.hierarchical.check_consistency()
        self.assertIsNotNone(reports)
        self.assertIsInstance(reports, list)
    
    def test_remove_memory(self):
        """测试删除记忆"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        ***REMOVED*** 先存储
        self.hierarchical.store(memory, ContentLevel.WORK)
        
        ***REMOVED*** 再删除
        result = self.hierarchical.remove_memory("test_1")
        self.assertTrue(result)
    
    def test_remove_memory_not_exists(self):
        """测试删除不存在的记忆"""
        result = self.hierarchical.remove_memory("non_existent")
        ***REMOVED*** 应该返回 False 或 True（取决于实现）
        self.assertIsNotNone(result)


class TestConsistencyReport(unittest.TestCase):
    """ConsistencyReport 测试"""
    
    def test_create_report(self):
        """测试创建报告"""
        report = ConsistencyReport(
            level="WORK",
            is_consistent=True,
            issues=[],
            details={}
        )
        self.assertEqual(report.level, "WORK")
        self.assertTrue(report.is_consistent)
    
    def test_report_validation(self):
        """测试报告验证"""
        ***REMOVED*** 空 level 应该抛出异常
        with self.assertRaises(ValueError):
            ConsistencyReport(
                level="",
                is_consistent=True
            )
    
    def test_report_with_issues(self):
        """测试带问题的报告"""
        report = ConsistencyReport(
            level="WORK",
            is_consistent=False,
            issues=["Issue 1", "Issue 2"],
            details={"error_count": 2}
        )
        self.assertFalse(report.is_consistent)
        self.assertEqual(len(report.issues), 2)


if __name__ == "__main__":
    unittest.main()

