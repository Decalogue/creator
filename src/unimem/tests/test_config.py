"""
配置管理测试

测试 config.py 中的配置管理、验证和环境变量支持
"""

import unittest
import os
from unittest.mock import patch
from tempfile import NamedTemporaryFile
import json

from unimem.config import UniMemConfig
from unimem.adapters.base import AdapterConfigurationError


class TestUniMemConfig(unittest.TestCase):
    """UniMemConfig 测试类"""
    
    def setUp(self):
        """设置测试环境"""
        ***REMOVED*** 保存原始环境变量
        self.original_env = {}
        for key in os.environ:
            if key.startswith("UNIMEM_") or key.startswith("NEO4J_") or key.startswith("REDIS_"):
                self.original_env[key] = os.environ[key]
    
    def tearDown(self):
        """清理测试环境"""
        ***REMOVED*** 恢复原始环境变量
        for key in list(os.environ.keys()):
            if key.startswith("UNIMEM_") or key.startswith("NEO4J_") or key.startswith("REDIS_"):
                if key not in self.original_env:
                    del os.environ[key]
                else:
                    os.environ[key] = self.original_env[key]
    
    def test_default_config(self):
        """测试默认配置"""
        config = UniMemConfig()
        self.assertIsNotNone(config.get("storage.foa_backend"))
        self.assertIsNotNone(config.get("graph.backend"))
    
    def test_config_from_file(self):
        """测试从文件加载配置"""
        config_data = {
            "storage": {
                "foa_backend": "redis",
                "foa_max_tokens": 1000
            }
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            config = UniMemConfig(config_file=config_file)
            self.assertEqual(config.get("storage.foa_backend"), "redis")
            self.assertEqual(config.get("storage.foa_max_tokens"), 1000)
        finally:
            os.unlink(config_file)
    
    def test_config_from_env(self):
        """测试从环境变量加载配置"""
        os.environ["UNIMEM_STORAGE_BACKEND"] = "redis"
        os.environ["UNIMEM_FOA_MAX_TOKENS"] = "2000"
        
        config = UniMemConfig()
        self.assertEqual(config.get("storage.foa_backend"), "redis")
        self.assertEqual(config.get("storage.foa_max_tokens"), 2000)
    
    def test_config_neo4j_from_env(self):
        """测试 Neo4j 配置从环境变量加载"""
        os.environ["NEO4J_URI"] = "bolt://localhost:7680"
        os.environ["NEO4J_USER"] = "neo4j"
        os.environ["NEO4J_PASSWORD"] = "test_password"
        
        config = UniMemConfig()
        self.assertEqual(config.get("graph.neo4j_uri"), "bolt://localhost:7680")
        self.assertEqual(config.get("graph.neo4j_user"), "neo4j")
        self.assertEqual(config.get("graph.neo4j_password"), "test_password")
    
    def test_config_redis_from_env(self):
        """测试 Redis 配置从环境变量加载"""
        os.environ["REDIS_HOST"] = "localhost"
        os.environ["REDIS_PORT"] = "6380"
        os.environ["REDIS_DB"] = "1"
        
        config = UniMemConfig()
        self.assertEqual(config.get("storage.redis_host"), "localhost")
        self.assertEqual(config.get("storage.redis_port"), 6380)
        self.assertEqual(config.get("storage.redis_db"), 1)
    
    def test_config_validation_valid(self):
        """测试有效配置验证"""
        config = UniMemConfig()
        ***REMOVED*** 应该不抛出异常
        config.validate()
    
    def test_config_get_nested(self):
        """测试嵌套键获取"""
        config = UniMemConfig()
        value = config.get("storage.foa_backend")
        self.assertIsNotNone(value)
    
    def test_config_get_default(self):
        """测试获取不存在的键返回默认值"""
        config = UniMemConfig()
        value = config.get("non_existent.key", default="default_value")
        self.assertEqual(value, "default_value")
    
    def test_config_set(self):
        """测试设置配置值"""
        config = UniMemConfig()
        config.set("test.key", "test_value")
        self.assertEqual(config.get("test.key"), "test_value")
    
    def test_config_to_dict(self):
        """测试转换为字典"""
        config = UniMemConfig()
        config_dict = config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertIn("storage", config_dict)
    
    def test_config_validation_invalid_backend(self):
        """测试无效后端配置验证"""
        config = UniMemConfig()
        config.set("storage.foa_backend", "invalid_backend")
        
        with self.assertRaises(AdapterConfigurationError):
            config.validate()
    
    def test_config_validation_timeout_range(self):
        """测试超时范围验证"""
        config = UniMemConfig()
        config.set("operation_timeout", -1)  ***REMOVED*** 负数
        
        with self.assertRaises(AdapterConfigurationError):
            config.validate()
    
    def test_config_validation_neo4j_uri_required(self):
        """测试 Neo4j URI 必填验证"""
        config = UniMemConfig()
        config.set("graph.backend", "neo4j")
        config.set("graph.neo4j_uri", None)
        
        with self.assertRaises(AdapterConfigurationError):
            config.validate()
    
    def test_config_validation_neo4j_uri_format(self):
        """测试 Neo4j URI 格式验证"""
        config = UniMemConfig()
        config.set("graph.backend", "neo4j")
        config.set("graph.neo4j_uri", "invalid_uri")  ***REMOVED*** 无效格式
        
        with self.assertRaises(AdapterConfigurationError):
            config.validate()


if __name__ == "__main__":
    unittest.main()

