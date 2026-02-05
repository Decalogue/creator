"""
更新管理器测试

测试 update/update_manager.py 中的更新管理功能
"""

import unittest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from unimem.update.update_manager import UpdateManager
from unimem.memory_types import Memory, Entity, Relation, MemoryType
from unimem.adapters.base import AdapterError


class TestUpdateManager(unittest.TestCase):
    """UpdateManager 测试"""
    
    def setUp(self):
        """设置测试环境"""
        # Mock 适配器
        self.graph_adapter = Mock()
        self.graph_adapter.is_available.return_value = True
        
        self.atom_link_adapter = Mock()
        self.atom_link_adapter.is_available.return_value = True
        
        self.update_adapter = Mock()
        self.update_adapter.is_available.return_value = True
        
        self.manager = UpdateManager(
            graph_adapter=self.graph_adapter,
            atom_link_adapter=self.atom_link_adapter,
            update_adapter=self.update_adapter
        )
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.graph_adapter, self.graph_adapter)
        self.assertEqual(self.manager.atom_link_adapter, self.atom_link_adapter)
        self.assertEqual(self.manager.update_adapter, self.update_adapter)
        self.assertIsNotNone(self.manager.ripple_updater)
    
    def test_trigger_ripple_success(self):
        """测试成功触发涟漪效应"""
        memory = Memory(
            id="test_1",
            content="Test memory",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        entities = [
            Entity(name="Entity1", entity_type="type1")
        ]
        relations = [
            Relation(source="e1", target="e2", relation_type="related")
        ]
        links = {"link_1"}
        
        # Mock ripple_updater
        self.manager.ripple_updater.trigger_ripple = Mock(return_value=True)
        
        result = self.manager.trigger_ripple(memory, entities, relations, links)
        self.assertTrue(result)
    
    def test_trigger_ripple_invalid_center(self):
        """测试无效中心记忆"""
        with self.assertRaises(AdapterError):
            self.manager.trigger_ripple(None, [], [], set())
    
    def test_trigger_ripple_empty_params(self):
        """测试空参数（应该允许）"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        self.manager.ripple_updater.trigger_ripple = Mock(return_value=True)
        
        result = self.manager.trigger_ripple(memory, None, None, None)
        # 应该不抛出异常
        self.assertIsNotNone(result)
    
    def test_queue_sleep_update(self):
        """测试队列睡眠更新"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        
        # Mock update_adapter
        self.update_adapter.queue_update = Mock(return_value=True)
        
        result = self.manager.queue_sleep_update(memory)
        self.assertTrue(result)
    
    def test_queue_sleep_update_invalid_memory(self):
        """测试无效记忆队列"""
        with self.assertRaises(AdapterError):
            self.manager.queue_sleep_update(None)
    
    def test_run_sleep_update(self):
        """测试运行睡眠更新"""
        # Mock update_adapter
        self.update_adapter.run_sleep_update = Mock(return_value=True)
        
        result = self.manager.run_sleep_update()
        # 应该不抛出异常
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()

