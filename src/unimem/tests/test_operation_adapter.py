"""
操作适配器测试

测试 adapters/operation_adapter.py 中的操作适配器功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from unimem.adapters.operation_adapter import OperationAdapter, Budget
from unimem.memory_types import Experience, Memory, Task, Context, MemoryType
from unimem.adapters.base import AdapterConfigurationError, AdapterError


class TestOperationAdapter(unittest.TestCase):
    """OperationAdapter 测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = {
            "llm_provider": "deepseek",
            "llm_model": "deepseek-v3.2"
        }
        self.adapter = OperationAdapter(config=self.config)
        self.adapter.initialize()
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.adapter)
        self.assertEqual(self.adapter.config.get("llm_provider"), "deepseek")
    
    def test_init_missing_llm_config(self):
        """测试缺少 LLM 配置"""
        with self.assertRaises(AdapterConfigurationError):
            adapter = OperationAdapter(config={})
            adapter.initialize()
    
    def test_retain_success(self):
        """测试成功存储记忆"""
        experience = Experience(
            content="Test experience",
            timestamp=datetime.now()
        )
        context = Context()
        
        ***REMOVED*** Mock LLM 调用（如果使用）
        memory = self.adapter.retain(experience, context)
        self.assertIsNotNone(memory)
        self.assertEqual(memory.content, experience.content)
    
    def test_retain_invalid_experience(self):
        """测试无效经验数据"""
        with self.assertRaises(AdapterError):
            self.adapter.retain(None, Context())
    
    def test_retain_empty_content(self):
        """测试空内容"""
        experience = Experience(
            content="",
            timestamp=datetime.now()
        )
        with self.assertRaises(AdapterError):
            self.adapter.retain(experience, Context())
    
    @patch('unimem.adapters.operation_adapter.ark_deepseek_v3_2')
    def test_recall_success(self, mock_llm):
        """测试成功检索"""
        ***REMOVED*** Mock LLM 响应
        mock_llm.return_value = "Mocked recall results"
        
        results = self.adapter.recall(
            query="test query",
            context=Context(),
            top_k=10
        )
        self.assertIsNotNone(results)
    
    def test_recall_empty_query(self):
        """测试空查询"""
        with self.assertRaises(AdapterError):
            self.adapter.recall("", Context())
    
    def test_recall_with_memory_type(self):
        """测试按记忆类型过滤"""
        results = self.adapter.recall(
            query="query",
            context=Context(),
            memory_type=MemoryType.EXPERIENCE,
            top_k=10
        )
        self.assertIsNotNone(results)
    
    @patch('unimem.adapters.operation_adapter.ark_deepseek_v3_2')
    def test_reflect_success(self, mock_llm):
        """测试成功优化记忆"""
        memory = Memory(
            id="test_1",
            content="Original content",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        task = Task(
            id="task_1",
            description="Test task",
            context="Context"
        )
        
        ***REMOVED*** Mock LLM 响应
        mock_llm.return_value = "Reflected content"
        
        updated_memories = self.adapter.reflect([memory], task, Context())
        self.assertIsNotNone(updated_memories)
        self.assertGreater(len(updated_memories), 0)
    
    def test_reflect_empty_memories(self):
        """测试空记忆列表"""
        task = Task(
            id="task_1",
            description="Task",
            context="Context"
        )
        with self.assertRaises(AdapterError):
            self.adapter.reflect([], task, Context())
    
    def test_reflect_invalid_task(self):
        """测试无效任务"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        with self.assertRaises(AdapterError):
            self.adapter.reflect([memory], None, Context())


class TestBudget(unittest.TestCase):
    """Budget 枚举测试"""
    
    def test_budget_values(self):
        """测试预算值"""
        self.assertEqual(Budget.LOW, "low")
        self.assertEqual(Budget.MID, "mid")
        self.assertEqual(Budget.HIGH, "high")


if __name__ == "__main__":
    unittest.main()

