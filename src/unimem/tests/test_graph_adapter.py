"""
图适配器测试

测试 adapters/graph_adapter.py 中的图结构适配器功能
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from unimem.adapters.graph_adapter import GraphAdapter, RequestMetrics
from unimem.memory_types import Entity, Relation, Memory, MemoryType
from unimem.adapters.base import AdapterConfigurationError, AdapterNotAvailableError


class TestRequestMetrics(unittest.TestCase):
    """RequestMetrics 测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        metrics = RequestMetrics()
        self.assertEqual(metrics.total_requests, 0)
        self.assertEqual(metrics.successful_requests, 0)
        self.assertEqual(metrics.average_latency, 0.0)
        self.assertEqual(metrics.success_rate, 0.0)
    
    def test_average_latency(self):
        """测试平均延迟计算"""
        metrics = RequestMetrics()
        metrics.total_requests = 2
        metrics.total_latency = 0.2  # 0.2秒
        self.assertAlmostEqual(metrics.average_latency, 100.0, places=1)  # 100毫秒
    
    def test_success_rate(self):
        """测试成功率计算"""
        metrics = RequestMetrics()
        metrics.total_requests = 10
        metrics.successful_requests = 8
        self.assertEqual(metrics.success_rate, 0.8)
    
    def test_reset(self):
        """测试重置"""
        metrics = RequestMetrics()
        metrics.total_requests = 10
        metrics.successful_requests = 8
        metrics.reset()
        self.assertEqual(metrics.total_requests, 0)
        self.assertEqual(metrics.successful_requests, 0)


class TestGraphAdapter(unittest.TestCase):
    """GraphAdapter 测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.config = {
            "api_base_url": "http://localhost:8000",
            "timeout": 30.0
        }
        self.adapter = GraphAdapter(config=self.config)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsNotNone(self.adapter)
        self.assertEqual(self.adapter.config.get("api_base_url"), "http://localhost:8000")
    
    def test_init_missing_api_base_url(self):
        """测试缺少 api_base_url 配置"""
        with self.assertRaises(AdapterConfigurationError):
            GraphAdapter(config={})
    
    @patch('unimem.adapters.graph_adapter.requests')
    def test_entity_search_success(self, mock_requests):
        """测试成功实体搜索"""
        # Mock 响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "entities": [
                {"id": "e1", "name": "Entity1", "type": "type1"}
            ]
        }
        mock_requests.Session.return_value.__enter__.return_value.get.return_value = mock_response
        
        results = self.adapter.entity_search("query", top_k=10)
        self.assertIsNotNone(results)
    
    @patch('unimem.adapters.graph_adapter.requests')
    def test_entity_search_api_error(self, mock_requests):
        """测试 API 错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_requests.Session.return_value.__enter__.return_value.get.return_value = mock_response
        
        # 应该不抛出异常，而是返回空列表或处理错误
        results = self.adapter.entity_search("query", top_k=10)
        self.assertIsNotNone(results)
    
    @patch('unimem.adapters.graph_adapter.requests')
    def test_add_entity_success(self, mock_requests):
        """测试成功添加实体"""
        entity = Entity(
            id="e1",
            name="Entity1",
            entity_type="type1",
            description="Description"
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_requests.Session.return_value.__enter__.return_value.post.return_value = mock_response
        
        result = self.adapter.add_entity(entity)
        self.assertTrue(result)
    
    @patch('unimem.adapters.graph_adapter.requests')
    def test_add_relation_success(self, mock_requests):
        """测试成功添加关系"""
        relation = Relation(
            source="e1",
            target="e2",
            relation_type="related_to"
        )
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_requests.Session.return_value.__enter__.return_value.post.return_value = mock_response
        
        result = self.adapter.add_relation(relation)
        self.assertTrue(result)
    
    def test_get_metrics(self):
        """测试获取指标"""
        metrics = self.adapter.get_metrics()
        self.assertIn("total_requests", metrics)
        self.assertIn("success_rate", metrics)
    
    def test_health_check(self):
        """测试健康检查"""
        # Mock 健康检查响应
        with patch.object(self.adapter, '_make_api_request') as mock_request:
            mock_request.return_value = {"status": "healthy"}
            
            health = self.adapter.health_check()
            self.assertIn("status", health)


if __name__ == "__main__":
    unittest.main()

