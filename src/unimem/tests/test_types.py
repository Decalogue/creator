"""
类型系统测试

测试 types.py 中的核心数据类及其验证逻辑
"""

import unittest
from datetime import datetime
from typing import List

from unimem.memory_types import (
    Experience, Memory, Task, Context,
    RetrievalResult, Entity, Relation,
    MemoryType, MemoryLayer
)
from unimem.adapters.base import AdapterError


class TestExperience(unittest.TestCase):
    """Experience 数据类测试"""
    
    def test_create_experience(self):
        """测试创建 Experience"""
        exp = Experience(
            content="Test content",
            timestamp=datetime.now()
        )
        self.assertEqual(exp.content, "Test content")
        self.assertIsNotNone(exp.timestamp)
    
    def test_experience_validation_empty_content(self):
        """测试空内容验证"""
        with self.assertRaises(AdapterError):
            Experience(content="", timestamp=datetime.now())
    
    def test_experience_validation_none_content(self):
        """测试 None 内容验证"""
        with self.assertRaises(AdapterError):
            Experience(content=None, timestamp=datetime.now())
    
    def test_experience_serialization(self):
        """测试序列化"""
        exp = Experience(
            content="Test",
            timestamp=datetime(2024, 1, 1, 12, 0, 0)
        )
        data = exp.to_dict()
        self.assertIn("content", data)
        self.assertIn("timestamp", data)
        
        # 测试反序列化
        exp2 = Experience.from_dict(data)
        self.assertEqual(exp2.content, exp.content)


class TestMemory(unittest.TestCase):
    """Memory 数据类测试"""
    
    def test_create_memory(self):
        """测试创建 Memory"""
        memory = Memory(
            id="test_1",
            content="Test memory",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        self.assertEqual(memory.id, "test_1")
        self.assertEqual(memory.content, "Test memory")
        self.assertEqual(memory.memory_type, MemoryType.EXPERIENCE)
    
    def test_memory_validation_empty_id(self):
        """测试空 ID 验证"""
        with self.assertRaises(AdapterError):
            Memory(
                id="",
                content="Test",
                timestamp=datetime.now(),
                memory_type=MemoryType.EXPERIENCE
            )
    
    def test_memory_validation_empty_content(self):
        """测试空内容验证"""
        with self.assertRaises(AdapterError):
            Memory(
                id="test_1",
                content="",
                timestamp=datetime.now(),
                memory_type=MemoryType.EXPERIENCE
            )
    
    def test_memory_serialization(self):
        """测试序列化"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE,
            layer=MemoryLayer.FOA
        )
        data = memory.to_dict()
        self.assertIn("id", data)
        self.assertIn("content", data)
        self.assertIn("memory_type", data)
        self.assertIn("layer", data)
        
        # 测试反序列化
        memory2 = Memory.from_dict(data)
        self.assertEqual(memory2.id, memory.id)
        self.assertEqual(memory2.memory_type, memory.memory_type)


class TestTask(unittest.TestCase):
    """Task 数据类测试"""
    
    def test_create_task(self):
        """测试创建 Task"""
        task = Task(
            description="Test task",
            goal="Complete test"
        )
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.goal, "Complete test")
    
    def test_task_validation_empty_description(self):
        """测试空描述验证"""
        with self.assertRaises(AdapterError):
            Task(description="", goal="Test")
    
    def test_task_serialization(self):
        """测试序列化"""
        task = Task(
            description="Test",
            goal="Goal"
        )
        data = task.to_dict()
        self.assertIn("description", data)
        self.assertIn("goal", data)


class TestContext(unittest.TestCase):
    """Context 数据类测试"""
    
    def test_create_context(self):
        """测试创建 Context"""
        ctx = Context(
            current_task="task1",
            relevant_memories=["mem1", "mem2"]
        )
        self.assertEqual(ctx.current_task, "task1")
        self.assertEqual(len(ctx.relevant_memories), 2)
    
    def test_context_default_values(self):
        """测试默认值"""
        ctx = Context()
        self.assertEqual(ctx.current_task, "")
        self.assertEqual(ctx.relevant_memories, [])
        self.assertEqual(ctx.query, "")
    
    def test_context_serialization(self):
        """测试序列化"""
        ctx = Context(
            current_task="task1",
            query="test query"
        )
        data = ctx.to_dict()
        self.assertIn("current_task", data)
        self.assertIn("query", data)


class TestRetrievalResult(unittest.TestCase):
    """RetrievalResult 数据类测试"""
    
    def test_create_retrieval_result(self):
        """测试创建 RetrievalResult"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        result = RetrievalResult(
            memory=memory,
            score=0.95,
            retrieval_method="semantic"
        )
        self.assertEqual(result.score, 0.95)
        self.assertEqual(result.retrieval_method, "semantic")
    
    def test_retrieval_result_validation_negative_score(self):
        """测试负数分数验证"""
        memory = Memory(
            id="test_1",
            content="Test",
            timestamp=datetime.now(),
            memory_type=MemoryType.EXPERIENCE
        )
        # 允许负数分数（可能是相关性分数）
        result = RetrievalResult(
            memory=memory,
            score=-0.5,
            retrieval_method="test"
        )
        self.assertEqual(result.score, -0.5)


class TestEntity(unittest.TestCase):
    """Entity 数据类测试"""
    
    def test_create_entity(self):
        """测试创建 Entity"""
        entity = Entity(
            name="Python",
            entity_type="technology",
            description="Programming language"
        )
        self.assertEqual(entity.name, "Python")
        self.assertEqual(entity.entity_type, "technology")
    
    def test_entity_validation_empty_name(self):
        """测试空名称验证"""
        with self.assertRaises(AdapterError):
            Entity(name="", entity_type="type")


class TestRelation(unittest.TestCase):
    """Relation 数据类测试"""
    
    def test_create_relation(self):
        """测试创建 Relation"""
        relation = Relation(
            source="entity1",
            target="entity2",
            relation_type="related_to",
            strength=0.8
        )
        self.assertEqual(relation.source, "entity1")
        self.assertEqual(relation.target, "entity2")
        self.assertEqual(relation.relation_type, "related_to")
        self.assertEqual(relation.strength, 0.8)
    
    def test_relation_validation_invalid_strength(self):
        """测试强度范围验证"""
        with self.assertRaises(AdapterError):
            Relation(
                source="e1",
                target="e2",
                relation_type="type",
                strength=1.5  # 超出范围 [0, 1]
            )
    
    def test_relation_validation_empty_source(self):
        """测试空源验证"""
        with self.assertRaises(AdapterError):
            Relation(
                source="",
                target="e2",
                relation_type="type"
            )


if __name__ == "__main__":
    unittest.main()

