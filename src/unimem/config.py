"""
UniMem 配置管理

按照功能适配器结构组织配置

工业级特性：
- 配置验证（类型检查、范围验证）
- 环境变量支持
- 配置合并和覆盖
- 默认值管理
"""

from typing import Dict, Any, Optional, List
import os
import logging
from pathlib import Path

from .adapters.base import AdapterConfigurationError

logger = logging.getLogger(__name__)


class UniMemConfig:
    """UniMem 配置类"""
    
    def __init__(self, config_file: Optional[str] = None, validate: bool = True):
        """
        初始化配置
        
        Args:
            config_file: 配置文件路径
            validate: 是否在加载后验证配置（默认 True）
            
        Raises:
            AdapterConfigurationError: 如果配置验证失败
        """
        self.config = self._load_default_config()
        
        if config_file and Path(config_file).exists():
            self._load_from_file(config_file)
        
        self._load_from_env()
        
        if validate:
            self.validate()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            # 存储后端配置
            "storage": {
                "foa_backend": "redis",
                "da_backend": "redis",
                "ltm_backend": "neo4j",
            },
            # 图数据库配置
            "graph": {
                "backend": "neo4j",
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "embedding_model": "text-embedding-3-small",
            },
            # 向量数据库配置
            "vector": {
                "backend": "qdrant",
            },
            # 功能适配器配置（按照功能模块组织）
            "operation": {
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "llm_func": "ark_deepseek_v3_2",  # 使用 chat.py 中的函数
            },
            "layered_storage": {
                # CogMem 相关配置
            },
            "memory_type": {
                # MemMachine 相关配置
            },
            "network": {
                # A-Mem 相关配置
                "model_name": "all-MiniLM-L6-v2",
                "local_model_path": "/root/data/AI/pretrain/all-MiniLM-L6-v2",  # 本地模型路径
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "llm_func": "ark_deepseek_v3_2",  # 使用 chat.py 中的函数
                "qdrant_host": "localhost",
                "qdrant_port": 6333,
                "collection_name": "unimem_memories",
            },
            "retrieval": {
                "top_k": 10,
                "rrf_k": 60,
                # 记忆重要性评分（用于 recall 重排序）
                "importance_weight": 0.3,   # 与检索分数融合时重要性权重，0=仅检索分，1=仅重要性
                "importance_decay_days": 30, # 时间衰减：超过 N 天未访问的记忆重要性衰减
            },
            "update": {
                "sleep_interval": 3600,  # 1小时
            },
            # 涟漪效应配置
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
        # LLM 配置 - 使用 ARK API（deepseek）
        if os.getenv("ARK_API_KEY"):
            self.config["operation"]["api_key"] = os.getenv("ARK_API_KEY")
            self.config["network"]["api_key"] = os.getenv("ARK_API_KEY")
            self.config["graph"]["api_key"] = os.getenv("ARK_API_KEY")
        elif os.getenv("OPENAI_API_KEY"):
            # 向后兼容，但建议使用 ARK_API_KEY
            self.config["operation"]["api_key"] = os.getenv("OPENAI_API_KEY")
            self.config["network"]["api_key"] = os.getenv("OPENAI_API_KEY")
            self.config["graph"]["api_key"] = os.getenv("OPENAI_API_KEY")
        
        # Neo4j 配置
        if os.getenv("NEO4J_URI"):
            self.config["graph"]["neo4j_uri"] = os.getenv("NEO4J_URI")
        else:
            # 默认配置
            self.config["graph"]["neo4j_uri"] = "bolt://localhost:7680"
        
        if os.getenv("NEO4J_USER"):
            self.config["graph"]["neo4j_user"] = os.getenv("NEO4J_USER")
        else:
            # 默认用户
            self.config["graph"]["neo4j_user"] = "neo4j"
        
        if os.getenv("NEO4J_PASSWORD"):
            self.config["graph"]["neo4j_password"] = os.getenv("NEO4J_PASSWORD")
        else:
            # 默认密码
            self.config["graph"]["neo4j_password"] = "seeme_db"
        
        # Neo4j 数据库名称
        if os.getenv("NEO4J_DATABASE"):
            self.config["graph"]["neo4j_database"] = os.getenv("NEO4J_DATABASE")
        else:
            self.config["graph"]["neo4j_database"] = "neo4j"
        
        # 存储后端
        if os.getenv("UNIMEM_STORAGE_BACKEND"):
            self.config["storage"]["foa_backend"] = os.getenv("UNIMEM_STORAGE_BACKEND")
            self.config["storage"]["da_backend"] = os.getenv("UNIMEM_STORAGE_BACKEND")
        
        if os.getenv("UNIMEM_LTM_BACKEND"):
            self.config["storage"]["ltm_backend"] = os.getenv("UNIMEM_LTM_BACKEND")
        
        # 图数据库
        if os.getenv("UNIMEM_GRAPH_BACKEND"):
            self.config["graph"]["backend"] = os.getenv("UNIMEM_GRAPH_BACKEND")
        
        # 向量数据库
        if os.getenv("UNIMEM_VECTOR_BACKEND"):
            self.config["vector"]["backend"] = os.getenv("UNIMEM_VECTOR_BACKEND")
        
        # Qdrant 配置
        if os.getenv("QDRANT_HOST"):
            self.config["network"]["qdrant_host"] = os.getenv("QDRANT_HOST")
        if os.getenv("QDRANT_PORT"):
            try:
                self.config["network"]["qdrant_port"] = int(os.getenv("QDRANT_PORT"))
            except ValueError:
                logger.warning(f"Invalid QDRANT_PORT value: {os.getenv('QDRANT_PORT')}")
    
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
    
    def validate(self) -> None:
        """
        验证配置的有效性
        
        Raises:
            AdapterConfigurationError: 如果配置无效
        """
        errors: List[str] = []
        
        # 验证必需配置
        required_sections = ["graph", "vector"]
        for section in required_sections:
            if section not in self.config:
                errors.append(f"Missing required config section: {section}")
        
        # 验证 graph 配置
        if "graph" in self.config:
            graph_config = self.config["graph"]
            valid_backends = ["neo4j", "networkx"]
            if graph_config.get("backend") not in valid_backends:
                errors.append(f"Invalid graph backend: {graph_config.get('backend')}. Must be one of {valid_backends}")
            
            # Neo4j 配置验证
            if graph_config.get("backend") == "neo4j":
                if "neo4j_uri" in graph_config:
                    uri = graph_config["neo4j_uri"]
                    if not isinstance(uri, str) or not uri.startswith(("bolt://", "neo4j://")):
                        errors.append(f"Invalid neo4j_uri format: {uri}. Must start with 'bolt://' or 'neo4j://'")
        
        # 验证 vector 配置
        if "vector" in self.config:
            vector_config = self.config["vector"]
            valid_backends = ["qdrant", "faiss", "milvus"]
            if vector_config.get("backend") not in valid_backends:
                errors.append(f"Invalid vector backend: {vector_config.get('backend')}. Must be one of {valid_backends}")
        
        # 验证 network 配置
        if "network" in self.config:
            network_config = self.config["network"]
            # 验证 Qdrant 端口
            if "qdrant_port" in network_config:
                port = network_config["qdrant_port"]
                if not isinstance(port, int) or not (1 <= port <= 65535):
                    errors.append(f"Invalid qdrant_port: {port}. Must be an integer between 1 and 65535")
            # 验证 Qdrant 主机
            if "qdrant_host" in network_config:
                host = network_config["qdrant_host"]
                if not isinstance(host, str) or not host.strip():
                    errors.append(f"Invalid qdrant_host: {host}. Must be a non-empty string")
        
        # 验证 update 配置
        if "update" in self.config:
            update_config = self.config["update"]
            if "sleep_interval" in update_config:
                interval = update_config["sleep_interval"]
                if not isinstance(interval, (int, float)) or interval <= 0:
                    errors.append(f"Invalid sleep_interval: {interval}. Must be a positive number")
        
        # 验证 retrieval 配置
        if "retrieval" in self.config:
            retrieval_config = self.config["retrieval"]
            if "top_k" in retrieval_config:
                top_k = retrieval_config["top_k"]
                if not isinstance(top_k, int) or top_k <= 0:
                    errors.append(f"Invalid top_k: {top_k}. Must be a positive integer")
            if "rrf_k" in retrieval_config:
                rrf_k = retrieval_config["rrf_k"]
                if not isinstance(rrf_k, int) or rrf_k <= 0:
                    errors.append(f"Invalid rrf_k: {rrf_k}. Must be a positive integer")
            if "importance_weight" in retrieval_config:
                w = retrieval_config["importance_weight"]
                if not isinstance(w, (int, float)) or not (0.0 <= w <= 1.0):
                    errors.append(f"Invalid importance_weight: {w}. Must be between 0.0 and 1.0")
            if "importance_decay_days" in retrieval_config:
                d = retrieval_config["importance_decay_days"]
                if not isinstance(d, (int, float)) or d <= 0:
                    errors.append(f"Invalid importance_decay_days: {d}. Must be positive")
        
        # 验证 ripple 配置
        if "ripple" in self.config:
            ripple_config = self.config["ripple"]
            if "max_depth" in ripple_config:
                max_depth = ripple_config["max_depth"]
                if not isinstance(max_depth, int) or max_depth < 1:
                    errors.append(f"Invalid max_depth: {max_depth}. Must be a positive integer")
            if "decay_factor" in ripple_config:
                decay_factor = ripple_config["decay_factor"]
                if not isinstance(decay_factor, (int, float)) or not (0.0 <= decay_factor <= 1.0):
                    errors.append(f"Invalid decay_factor: {decay_factor}. Must be between 0.0 and 1.0")
        
        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            raise AdapterConfigurationError(error_msg, adapter_name="UniMemConfig")
        
        logger.debug("Configuration validation passed")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config.copy()
