"""
UniMem 配置管理

按照功能适配器结构组织配置
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path


class UniMemConfig:
    """UniMem 配置类"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_default_config()
        
        if config_file and Path(config_file).exists():
            self._load_from_file(config_file)
        
        self._load_from_env()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            ***REMOVED*** 存储后端配置
            "storage": {
                "foa_backend": "redis",
                "da_backend": "redis",
                "ltm_backend": "postgresql",
            },
            ***REMOVED*** 图数据库配置
            "graph": {
                "backend": "neo4j",
                "workspace": "./lightrag_workspace",
                "llm_model": "gpt-4o-mini",
                "embedding_model": "text-embedding-3-small",
            },
            ***REMOVED*** 向量数据库配置
            "vector": {
                "backend": "qdrant",
            },
            ***REMOVED*** 功能适配器配置（按照功能模块组织）
            "operation": {
                "llm_provider": "openai",
                "llm_model": "gpt-4o-mini",
            },
            "layered_storage": {
                ***REMOVED*** CogMem 相关配置
            },
            "memory_type": {
                ***REMOVED*** MemMachine 相关配置
            },
            "network": {
                ***REMOVED*** A-Mem 相关配置
                "model_name": "all-MiniLM-L6-v2",
                "local_model_path": "/root/data/AI/pretrain/all-MiniLM-L6-v2",  ***REMOVED*** 本地模型路径
                "llm_backend": "openai",
                "llm_model": "gpt-4o-mini",
                "qdrant_host": "localhost",
                "qdrant_port": 6333,
                "collection_name": "unimem_memories",
            },
            "retrieval": {
                "top_k": 10,
                "rrf_k": 60,
            },
            "update": {
                "sleep_interval": 3600,  ***REMOVED*** 1小时
            },
            ***REMOVED*** 涟漪效应配置
            "ripple": {
                "max_depth": 3,
                "decay_factor": 0.5,
            },
        }
    
    def _load_from_file(self, config_file: str):
        """从文件加载配置"""
        import json
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self._merge_config(self.config, file_config)
        except Exception as e:
            print(f"Warning: Failed to load config from {config_file}: {e}")
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        ***REMOVED*** LLM 配置
        if os.getenv("OPENAI_API_KEY"):
            self.config["operation"]["api_key"] = os.getenv("OPENAI_API_KEY")
            self.config["network"]["api_key"] = os.getenv("OPENAI_API_KEY")
            self.config["graph"]["api_key"] = os.getenv("OPENAI_API_KEY")
        
        ***REMOVED*** 存储后端
        if os.getenv("UNIMEM_STORAGE_BACKEND"):
            self.config["storage"]["foa_backend"] = os.getenv("UNIMEM_STORAGE_BACKEND")
            self.config["storage"]["da_backend"] = os.getenv("UNIMEM_STORAGE_BACKEND")
        
        if os.getenv("UNIMEM_LTM_BACKEND"):
            self.config["storage"]["ltm_backend"] = os.getenv("UNIMEM_LTM_BACKEND")
        
        ***REMOVED*** 图数据库
        if os.getenv("UNIMEM_GRAPH_BACKEND"):
            self.config["graph"]["backend"] = os.getenv("UNIMEM_GRAPH_BACKEND")
        
        ***REMOVED*** 向量数据库
        if os.getenv("UNIMEM_VECTOR_BACKEND"):
            self.config["vector"]["backend"] = os.getenv("UNIMEM_VECTOR_BACKEND")
    
    def _merge_config(self, base: Dict, override: Dict):
        """合并配置"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        支持点号分隔的键，如 "operation.llm_model"
        """
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        return value
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config.copy()
