"""
图适配器测试

测试 adapters/graph_adapter.py 中的图结构适配器（占位实现）
"""

import unittest

from unimem.adapters.graph_adapter import GraphAdapter
from unimem.memory_types import Entity, Relation, Memory


class TestGraphAdapter(unittest.TestCase):
    """GraphAdapter 占位实现测试"""

    def setUp(self):
        """设置测试环境"""
        self.adapter = GraphAdapter(config={})
        self.adapter.initialize()

    def test_init(self):
        """测试初始化：占位实现会完成初始化，可正常调用"""
        self.assertIsNotNone(self.adapter)
        self.assertTrue(self.adapter.is_available())

    def test_extract_entities_relations(self):
        """测试提取实体和关系：占位返回空"""
        entities, relations = self.adapter.extract_entities_relations("测试文本")
        self.assertEqual(entities, [])
        self.assertEqual(relations, [])

    def test_add_entities_empty(self):
        """测试添加空实体列表：视为成功"""
        self.assertTrue(self.adapter.add_entities([]))

    def test_add_entities_non_empty(self):
        """测试添加实体：占位返回 False"""
        entity = Entity(
            id="e1",
            name="Entity1",
            entity_type="type1",
            description="Description",
        )
        self.assertFalse(self.adapter.add_entities([entity]))

    def test_add_relations_empty(self):
        """测试添加空关系列表：视为成功"""
        self.assertTrue(self.adapter.add_relations([]))

    def test_add_relations_non_empty(self):
        """测试添加关系：占位返回 False"""
        relation = Relation(
            source="e1",
            target="e2",
            keywords=["related"],
            description="related to",
        )
        self.assertFalse(self.adapter.add_relations([relation]))

    def test_entity_retrieval(self):
        """测试实体检索：占位返回空列表"""
        results = self.adapter.entity_retrieval("query", top_k=10)
        self.assertEqual(results, [])

    def test_abstract_retrieval(self):
        """测试抽象检索：占位返回空列表"""
        results = self.adapter.abstract_retrieval("query", top_k=10)
        self.assertEqual(results, [])

    def test_get_entities_for_memory(self):
        """测试获取记忆关联实体：占位返回空列表"""
        entities = self.adapter.get_entities_for_memory("mem_1")
        self.assertEqual(entities, [])

    def test_update_entity_description(self):
        """测试更新实体描述：占位返回 False"""
        self.assertFalse(
            self.adapter.update_entity_description("e1", "new description")
        )

    def test_health_check(self):
        """测试健康检查：占位实现完成初始化"""
        status = self.adapter.health_check()
        self.assertTrue(status.initialized)


if __name__ == "__main__":
    unittest.main()
