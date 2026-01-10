"""
原子链接适配器

实现 UniMem 的原子笔记网络和动态链接生成
参考架构：A-Mem（原子笔记网络 + 记忆演化）

工业级特性：
- 嵌入向量缓存（减少重复计算）
- 批量操作支持（提高性能）
- 配置验证和错误处理
- 类型安全
"""

import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field

try:
    from qdrant_client.models import PointIdsList
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    PointIdsList = None

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

from .base import (
    BaseAdapter,
    AdapterConfigurationError,
    AdapterNotAvailableError,
    AdapterError
)
from ..memory_types import Entity, Memory
from ..chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingCache:
    """嵌入向量缓存"""
    cache: Dict[str, List[float]] = field(default_factory=dict)
    max_size: int = 1000
    
    def get(self, key: str) -> Optional[List[float]]:
        """获取缓存的嵌入向量"""
        return self.cache.get(key)
    
    def set(self, key: str, value: List[float]) -> None:
        """设置缓存的嵌入向量"""
        if len(self.cache) >= self.max_size:
            ***REMOVED*** 简单策略：删除最早的条目（FIFO）
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        self.cache[key] = value
    
    def clear(self) -> None:
        """清空缓存"""
        self.cache.clear()
    
    def size(self) -> int:
        """获取缓存大小"""
        return len(self.cache)


class AtomLinkAdapter(BaseAdapter):
    """
    原子链接适配器
    
    功能需求：原子笔记网络和动态链接生成
    参考架构：A-Mem（原子笔记网络 + 记忆演化）
    
    核心功能：
    1. 原子笔记构建：使用 LLM 分析内容，提取语义元数据
    2. 动态链接生成：基于语义相似度生成记忆链接
    3. 记忆演化：使用 LLM 判断并执行记忆演化
    4. 语义检索：基于向量相似度的语义检索
    5. 子图链接检索：通过链接网络的子图进行检索
    """
    
    def _do_initialize(self) -> None:
        """
        初始化原子链接适配器
        
        初始化向量存储（Qdrant）、嵌入模型（sentence-transformers）和内存存储。
        如果初始化失败，会记录警告但不会抛出异常，适配器会以降级模式运行。
        
        Raises:
            AdapterConfigurationError: 如果配置无效
        """
        ***REMOVED*** 初始化记忆存储
        self.memory_store: Dict[str, Memory] = {}
        ***REMOVED*** ID 映射：memory.id -> qdrant_point_id (用于处理非 UUID 格式的 ID)
        self.id_mapping: Dict[str, Any] = {}
        
        ***REMOVED*** 初始化嵌入缓存
        cache_size = int(self.config.get("embedding_cache_size", 1000))
        self.embedding_cache = EmbeddingCache(max_size=cache_size)
        
        ***REMOVED*** 批量操作配置
        self.batch_size = int(self.config.get("batch_size", 100))
        self.embedding_batch_size = int(self.config.get("embedding_batch_size", 32))
        
        ***REMOVED*** 初始化属性（确保即使失败也有默认值）
        self.qdrant_client = None
        self.embedding_model = None
        self.collection_name = None
        self.embedding_dimension = None
        
        ***REMOVED*** 向量存储：使用 Qdrant
        qdrant_host = str(self.config.get("qdrant_host", "localhost"))
        qdrant_port = int(self.config.get("qdrant_port", 6333))
        collection_name = str(self.config.get("collection_name", "unimem_memories"))
        
        ***REMOVED*** 配置验证
        if not qdrant_host:
            raise AdapterConfigurationError(
                "qdrant_host cannot be empty",
                adapter_name=self.__class__.__name__
            )
        if not (1 <= qdrant_port <= 65535):
            raise AdapterConfigurationError(
                f"Invalid qdrant_port: {qdrant_port} (must be 1-65535)",
                adapter_name=self.__class__.__name__
            )
        
        ***REMOVED*** 初始化 Qdrant 客户端
        if QDRANT_AVAILABLE:
            try:
                from qdrant_client import QdrantClient
                from qdrant_client.models import Distance, VectorParams
                
                self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
                
                ***REMOVED*** 创建集合（如果不存在）
                try:
                    collection_info = self.qdrant_client.get_collection(collection_name)
                    self.embedding_dimension = collection_info.config.params.vectors.size
                    logger.info(f"Using existing Qdrant collection: {collection_name} (dim={self.embedding_dimension})")
                except Exception as get_error:
                    ***REMOVED*** 集合不存在，尝试创建它
                    error_str = str(get_error).lower()
                    if "not found" in error_str or "404" in error_str:
                        ***REMOVED*** 集合确实不存在，创建它
                        try:
                            default_dim = int(self.config.get("embedding_dimension", 384))
                            self.qdrant_client.create_collection(
                                collection_name=collection_name,
                                vectors_config=VectorParams(
                                    size=default_dim,
                                    distance=Distance.COSINE,
                                ),
                            )
                            self.embedding_dimension = default_dim
                            logger.info(f"Created Qdrant collection: {collection_name} (dim={default_dim})")
                        except Exception as create_error:
                            create_error_str = str(create_error).lower()
                            ***REMOVED*** 如果创建时遇到409（集合已存在），说明集合在创建过程中被创建了，重新获取
                            if "409" in create_error_str or "already exists" in create_error_str or "conflict" in create_error_str:
                                try:
                                    collection_info = self.qdrant_client.get_collection(collection_name)
                                    self.embedding_dimension = collection_info.config.params.vectors.size
                                    logger.info(f"Qdrant collection already exists (recovered): {collection_name} (dim={self.embedding_dimension})")
                                except Exception:
                                    logger.warning(f"Collection {collection_name} exists but cannot access: {create_error}")
                                    self.embedding_dimension = default_dim
                            else:
                                ***REMOVED*** 其他创建错误
                                logger.warning(f"Failed to create Qdrant collection {collection_name}: {create_error}")
                                raise create_error
                    else:
                        ***REMOVED*** get_collection失败但不是"not found"，记录警告但使用默认维度
                        logger.warning(f"Failed to get Qdrant collection {collection_name}: {get_error}. Using default dimension.")
                        self.embedding_dimension = int(self.config.get("embedding_dimension", 384))
                
                self.collection_name = collection_name
                logger.info(f"Qdrant client connected: {qdrant_host}:{qdrant_port}")
            except Exception as e:
                logger.warning(f"Failed to connect to Qdrant: {e}. Vector operations will be limited.")
                self.qdrant_client = None
                self.collection_name = collection_name
        else:
            logger.warning("qdrant_client not available, vector operations will be limited")
            self.qdrant_client = None
        
        ***REMOVED*** 嵌入模型：使用 sentence-transformers（独立于 Qdrant）
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                local_model_path = self.config.get("local_model_path")
                model_name = self.config.get("model_name", "intfloat/multilingual-e5-small")
                
                if local_model_path and os.path.exists(local_model_path):
                    logger.info(f"Loading embedding model from local path: {local_model_path}")
                    self.embedding_model = SentenceTransformer(local_model_path)
                else:
                    logger.info(f"Loading embedding model from HuggingFace: {model_name}")
                    self.embedding_model = SentenceTransformer(model_name)
                
                self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
                logger.info(f"Embedding model loaded successfully (dimension: {self.embedding_dimension})")
                
                ***REMOVED*** 如果 Qdrant 集合维度不匹配，警告
                if self.qdrant_client and self.embedding_dimension:
                    try:
                        collection_info = self.qdrant_client.get_collection(collection_name)
                        collection_dim = collection_info.config.params.vectors.size
                        if collection_dim != self.embedding_dimension:
                            logger.warning(
                                f"Embedding dimension mismatch: model={self.embedding_dimension}, "
                                f"collection={collection_dim}"
                            )
                    except Exception:
                        pass
            except ImportError:
                logger.warning("sentence-transformers not available, semantic retrieval will be limited")
                self.embedding_model = None
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}", exc_info=True)
                self.embedding_model = None
        else:
            logger.warning("sentence-transformers not available, semantic retrieval will be limited")
            self.embedding_model = None
        
        ***REMOVED*** 检查是否有可用的组件
        if not self.qdrant_client and not self.embedding_model:
            logger.warning("Both Qdrant and embedding model unavailable, adapter will be limited")
            self._available = False
        else:
            self._available = True
        
        logger.info("Atom link adapter initialized (using A-Mem principles)")
    
    def semantic_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        语义检索
        
        参考 A-Mem 的语义检索思路：
        使用向量相似度进行语义检索
        
        Args:
            query: 查询文本
            top_k: 返回结果数量，默认 10
            
        Returns:
            相似记忆列表，按相似度从高到低排序
        """
        if not self.is_available():
            logger.warning("AtomLinkAdapter not available for semantic_retrieval")
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided for semantic_retrieval")
            return []
        
        try:
            return self._search_similar_memories(query, top_k=top_k)
        except Exception as e:
            logger.error(f"Error in semantic_retrieval: {e}", exc_info=True)
            return []
    
    def batch_semantic_retrieval(self, queries: List[str], top_k: int = 10) -> List[List[Memory]]:
        """
        批量语义检索
        
        批量执行多个查询的语义检索，使用批处理优化性能。
        
        Args:
            queries: 查询文本列表
            top_k: 每个查询返回结果数量，默认 10
            
        Returns:
            每个查询的结果列表，按输入顺序排列
        """
        if not self.is_available():
            return [[] for _ in queries]
        
        if not queries:
            return []
        
        results = []
        for query in queries:
            try:
                memories = self.semantic_retrieval(query, top_k=top_k)
                results.append(memories)
            except Exception as e:
                logger.error(f"Error in batch semantic retrieval for query '{query[:50]}...': {e}")
                results.append([])
        
        return results
    
    def get_capabilities(self) -> Dict[str, bool]:
        """
        获取适配器支持的能力
        
        Returns:
            Dict[str, bool]: 能力字典
        """
        return {
            "available": self.is_available(),
            "semantic_retrieval": self.embedding_model is not None,
            "vector_storage": self.qdrant_client is not None,
            "batch_operations": True,
            "embedding_cache": True,
            "memory_evolution": True,
        }
    
    def clear_embedding_cache(self) -> None:
        """清空嵌入向量缓存"""
        if hasattr(self, 'embedding_cache'):
            self.embedding_cache.clear()
            logger.info("Embedding cache cleared")
    
    def subgraph_link_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        子图链接检索
        
        通过链接网络的子图进行检索：
        1. 先进行语义检索找到初始记忆
        2. 通过链接网络遍历子图，找到相关记忆
        
        Args:
            query: 查询文本
            top_k: 返回结果数量，默认 10
            
        Returns:
            相关记忆列表，包括初始记忆和通过链接找到的相关记忆
        """
        if not self.is_available():
            return []
        
        if not query or not query.strip():
            logger.warning("Empty query provided for subgraph_link_retrieval")
            return []
        
        ***REMOVED*** 1. 语义检索找到初始记忆
        initial_memories = self._search_similar_memories(query, top_k=top_k)
        
        if not initial_memories:
            return []
        
        ***REMOVED*** 2. 通过链接扩散
        all_memories = []
        seen_ids = set()
        
        for mem in initial_memories:
            if mem.id not in seen_ids:
                all_memories.append(mem)
                seen_ids.add(mem.id)
            
            ***REMOVED*** 通过链接查找相关记忆
            for link_id in mem.links:
                if link_id in self.memory_store and link_id not in seen_ids:
                    all_memories.append(self.memory_store[link_id])
                    seen_ids.add(link_id)
                    if len(all_memories) >= top_k * 2:
                        break
        
        result = all_memories[:top_k]
        logger.debug(f"Subgraph link retrieval found {len(result)} memories")
        return result
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        解析 LLM 返回的 JSON 响应
        
        支持从 markdown 代码块中提取 JSON，并尝试修复常见的 JSON 格式错误。
        
        Args:
            response_text: LLM 返回的文本
            
        Returns:
            解析后的 JSON 字典，如果解析失败返回 None
        """
        if not response_text or not response_text.strip():
            logger.warning("Empty response_text provided for _parse_json_response")
            return None
        
        try:
            ***REMOVED*** 提取 JSON 部分（可能包含 markdown 代码块）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end == -1:
                    json_end = len(response_text)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                if json_end == -1:
                    json_end = len(response_text)
                response_text = response_text[json_start:json_end].strip()
            
            ***REMOVED*** 尝试直接解析
            return json.loads(response_text)
        except (json.JSONDecodeError, ValueError) as e:
            ***REMOVED*** 尝试修复常见的 JSON 错误
            try:
                ***REMOVED*** 移除可能的控制字符
                cleaned = ''.join(char for char in response_text if ord(char) >= 32 or char in '\n\r\t')
                ***REMOVED*** 尝试修复单引号（如果存在）
                if "'" in cleaned and '"' not in cleaned:
                    cleaned = cleaned.replace("'", '"')
                return json.loads(cleaned)
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to parse JSON response: {e}")
                logger.debug(f"Response text (first 500 chars): {response_text[:500]}")
                return None
    
    def _analyze_content(self, content: str, max_new_tokens: int = 1024, is_creative_content: bool = False) -> Dict[str, Any]:
        """
        使用 LLM 分析内容，提取语义元数据
        
        参考 A-Mem 的 analyze_content 方法
        增强：支持创作助手的多维度分析（文章/小说类型，写作风格，故事线，场景，人物，事件，线索等）
        
        Args:
            content: 要分析的内容（如果为空会返回默认结构）
            max_new_tokens: 最大生成 token 数，默认 1024
            is_creative_content: 是否为创作内容（小说/文章），如果是则提取创作相关维度
            
        Returns:
            包含以下字段的字典：
            - keywords: List[str] - 关键词列表
            - context: str - 一句话总结
            - tags: List[str] - 标签列表
            - creative_dimensions: Dict[str, Any] - 创作维度（仅当 is_creative_content=True 时）
            
        Note:
            如果分析失败，返回默认的空结构，不会抛出异常
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for _analyze_content")
            return {"keywords": [], "context": "General", "tags": []}
        if is_creative_content:
            ***REMOVED*** 创作内容的增强分析
            prompt = """请对以下创作内容进行结构化分析，提取语义元数据和创作维度信息。要求：

1. 识别最重要的关键词（重点关注名词、动词和核心概念）
2. 提取核心主题和上下文元素
3. 创建相关的分类标签
4. **创作维度分析**（如果适用）：
   - 文章/小说类型（如：武侠小说、科幻小说、散文、诗歌等）
   - 写作风格（如：现实主义、浪漫主义、悬疑、幽默等）
   - 故事线（主要情节线索）
   - 场景（时间、地点、环境）
   - 人物（主要角色及其特征）
   - 事件（关键事件和转折点）
   - 线索（伏笔、悬念等）

请以 JSON 格式返回结果：
{
    "keywords": [
        // 多个具体、独特的关键词，能够捕捉核心概念和术语
        // 按重要性从高到低排序
        // 至少三个关键词，但不要过于冗余
    ],
    "context": 
        // 一句话总结：
        // - 主要主题/领域
        // - 核心论点/要点
        // - 目标受众/目的
        // 请使用中文描述
    ,
    "tags": [
        // 多个广泛的分类/主题标签
        // 包括领域、格式和类型标签
        // 至少三个标签，但不要过于冗余
        // 可以使用中英文混合
    ],
    "creative_dimensions": {
        // 创作维度（如果适用，否则为 null）
        "genre": "文章/小说类型",
        "writing_style": "写作风格",
        "storyline": "故事线/主要情节",
        "scenes": ["场景1", "场景2", ...],
        "characters": ["人物1及其特征", "人物2及其特征", ...],
        "events": ["事件1", "事件2", ...],
        "clues": ["线索1", "线索2", ...]
    }
}

待分析的内容：
""" + content
        else:
            ***REMOVED*** 通用内容分析
            prompt = """请对以下内容进行结构化分析，提取语义元数据。要求：

1. 识别最重要的关键词（重点关注名词、动词和核心概念）
2. 提取核心主题和上下文元素
3. 创建相关的分类标签

请以 JSON 格式返回结果：
{
    "keywords": [
        // 多个具体、独特的关键词，能够捕捉核心概念和术语
        // 按重要性从高到低排序
        // 不要包含说话者姓名或时间相关的关键词
        // 至少三个关键词，但不要过于冗余
    ],
    "context": 
        // 一句话总结：
        // - 主要主题/领域
        // - 核心论点/要点
        // - 目标受众/目的
        // 请使用中文描述
    ,
    "tags": [
        // 多个广泛的分类/主题标签
        // 包括领域、格式和类型标签
        // 至少三个标签，但不要过于冗余
        // 可以使用中英文混合
    ]
}

待分析的内容：
""" + content
        
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的内容分析助手，擅长提取结构化元数据。请始终以有效的 JSON 格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=max_new_tokens)
            
            ***REMOVED*** 解析 JSON
            result = self._parse_json_response(response_text)
            if result:
                base_result = {
                    "keywords": result.get("keywords", []),
                    "context": result.get("context", "General"),
                    "tags": result.get("tags", []),
                }
                ***REMOVED*** 如果是创作内容，添加创作维度
                if is_creative_content and "creative_dimensions" in result:
                    base_result["creative_dimensions"] = result.get("creative_dimensions")
                return base_result
            else:
                logger.warning(f"Failed to parse LLM response as JSON: {response_text[:200]}")
                return {"keywords": [], "context": "General", "tags": []}
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {"keywords": [], "context": "General", "tags": []}
    
    def _get_embedding(self, text: str, use_cache: bool = True) -> Optional[List[float]]:
        """
        获取文本的向量嵌入（带缓存）
        
        Args:
            text: 输入文本
            use_cache: 是否使用缓存，默认 True
        
        Returns:
            向量嵌入列表，如果失败返回 None
        """
        if self.embedding_model is None:
            return None
        
        ***REMOVED*** 检查缓存
        if use_cache:
            cached_embedding = self.embedding_cache.get(text)
            if cached_embedding is not None:
                logger.debug(f"Using cached embedding for text: {text[:50]}...")
                return cached_embedding
        
        try:
            embedding = self.embedding_model.encode(text, show_progress_bar=False).tolist()
            ***REMOVED*** 保存到缓存
            if use_cache:
                self.embedding_cache.set(text, embedding)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            return None
    
    def _get_embeddings_batch(self, texts: List[str], use_cache: bool = True) -> List[Optional[List[float]]]:
        """
        批量获取文本的向量嵌入（带缓存和批处理优化）
        
        Args:
            texts: 输入文本列表
            use_cache: 是否使用缓存，默认 True
        
        Returns:
            向量嵌入列表，对应输入的每个文本（失败时为 None）
        """
        if self.embedding_model is None:
            return [None] * len(texts)
        
        if not texts:
            return []
        
        results = []
        texts_to_encode = []
        indices_to_encode = []
        
        ***REMOVED*** 检查缓存
        for idx, text in enumerate(texts):
            if use_cache:
                cached_embedding = self.embedding_cache.get(text)
                if cached_embedding is not None:
                    results.append((idx, cached_embedding))
                    continue
            
            texts_to_encode.append(text)
            indices_to_encode.append(idx)
        
        ***REMOVED*** 批量编码未缓存的文本
        if texts_to_encode:
            try:
                embeddings = self.embedding_model.encode(
                    texts_to_encode,
                    batch_size=self.embedding_batch_size,
                    show_progress_bar=False
                ).tolist()
                
                ***REMOVED*** 保存到缓存并添加到结果
                for i, (idx, embedding) in enumerate(zip(indices_to_encode, embeddings)):
                    if use_cache:
                        self.embedding_cache.set(texts_to_encode[i], embedding)
                    results.append((idx, embedding))
            except Exception as e:
                logger.error(f"Error generating embeddings batch: {e}", exc_info=True)
                ***REMOVED*** 为失败的索引添加 None
                for idx in indices_to_encode:
                    results.append((idx, None))
        
        ***REMOVED*** 按原始索引排序并返回
        results.sort(key=lambda x: x[0])
        return [embedding for _, embedding in results]
    
    def _enhance_content_for_embedding(self, memory: Memory) -> str:
        """
        增强内容用于嵌入生成
        
        参考 A-Mem 的 enhanced_document 思路
        """
        enhanced = memory.content
        
        ***REMOVED*** 添加上下文信息
        if memory.context and memory.context != "General":
            enhanced += f" context: {memory.context}"
        
        ***REMOVED*** 添加关键词信息
        if memory.keywords:
            enhanced += f" keywords: {', '.join(memory.keywords)}"
        
        ***REMOVED*** 添加标签信息
        if memory.tags:
            enhanced += f" tags: {', '.join(memory.tags)}"
        
        return enhanced
    
    def construct_atomic_note(
        self,
        content: str,
        timestamp: datetime,
        entities: Optional[List[Entity]] = None,
        generate_summary: bool = True,
        is_creative_content: bool = False
    ) -> Memory:
        """
        构建原子笔记
        
        参考 A-Mem 的原子笔记构建思路：
        1. 使用 LLM 分析内容，提取 keywords, context, tags
        2. 可选：使用 LLM 生成摘要性内容（而不是直接使用原始文本）
        3. 创建 Memory 对象
        4. 生成唯一 ID
        
        Args:
            content: 原始内容（如果为空会创建默认的 Memory 对象）
            timestamp: 时间戳，用于记录笔记创建时间
            entities: 实体列表（可选），用于关联相关实体
            generate_summary: 是否生成摘要性内容，默认 True
                - True: 使用 LLM 生成结构化摘要（100-200字）
                - False: 直接截取前1024字符作为原子内容
            is_creative_content: 是否为创作内容（小说/文章），如果是则提取创作相关维度
            
        Returns:
            Memory 对象，包含：
            - 原子内容（摘要或截取的内容）
            - 关键词、上下文、标签
            - 创作维度信息（存储在 metadata 中，仅当 is_creative_content=True 时）
            - 关联的实体 ID 列表
            
        Note:
            如果适配器不可用，仍会创建 Memory 对象，但不会生成摘要
        """
        if not content or not content.strip():
            logger.warning("Empty content provided for construct_atomic_note")
            ***REMOVED*** 返回一个默认的 Memory 对象
            memory_id = str(uuid.uuid4())
            return Memory(
                id=memory_id,
                content="",
                timestamp=timestamp,
                keywords=[],
                context="General",
                tags=[],
                entities=[e.id for e in entities] if entities else [],
            )
        ***REMOVED*** 分析内容，提取元数据（支持创作维度）
        analysis = self._analyze_content(content, is_creative_content=is_creative_content)
        
        ***REMOVED*** 如果启用摘要生成，使用 LLM 生成结构化的摘要
        if generate_summary and self.is_available():
            summary = self._generate_content_summary(content, analysis)
            atomic_content = summary
        else:
            ***REMOVED*** 否则使用原始内容（但可以截断过长的内容）
            atomic_content = content[:1024] if len(content) > 1024 else content
        
        ***REMOVED*** 构建 Memory 对象
        memory_id = str(uuid.uuid4())
        memory = Memory(
            id=memory_id,
            content=atomic_content,
            timestamp=timestamp,
            keywords=analysis.get("keywords", []),
            context=analysis.get("context", "General"),
            tags=analysis.get("tags", []),
            entities=[e.id for e in entities] if entities else [],
        )
        
        ***REMOVED*** 在 metadata 中保存原始内容的引用（如果需要）
        memory.metadata = memory.metadata or {}
        if generate_summary and len(content) > len(atomic_content):
            memory.metadata["original_length"] = len(content)
            memory.metadata["is_summary"] = True
        
        ***REMOVED*** 如果是创作内容，保存创作维度到 metadata
        if is_creative_content and "creative_dimensions" in analysis:
            memory.metadata["creative_dimensions"] = analysis["creative_dimensions"]
            ***REMOVED*** 将创作维度信息添加到 tags 中以便检索
            creative_dims = analysis["creative_dimensions"]
            if creative_dims:
                if creative_dims.get("genre"):
                    memory.tags.append(f"类型:{creative_dims['genre']}")
                if creative_dims.get("writing_style"):
                    memory.tags.append(f"风格:{creative_dims['writing_style']}")
        
        ***REMOVED*** 存储到内存中（用于快速访问）
        self.memory_store[memory_id] = memory
        
        logger.debug(f"Constructed atomic note: {memory_id} with {len(memory.keywords)} keywords, {len(memory.tags)} tags, content length: {len(atomic_content)}")
        return memory
    
    def _generate_content_summary(self, content: str, analysis: Dict[str, Any]) -> str:
        """
        使用 LLM 生成内容摘要
        
        生成一个结构化的摘要，包含：
        - 核心事件/情节
        - 关键角色/实体
        - 重要关系/冲突
        
        Args:
            content: 原始内容
            analysis: 已分析得到的元数据（keywords, context, tags）
            
        Returns:
            摘要性内容
        """
        prompt = f"""请对以下文本片段进行结构化摘要，提取核心信息。

要求：
1. 提取核心事件、情节或关键信息（2-3句话）
2. 识别主要角色、实体或对象
3. 描述重要的关系、冲突或转折
4. 保持信息的准确性和完整性
5. 使用简洁、清晰的语言
6. 摘要长度控制在100-200字左右

已提取的关键词：{', '.join(analysis.get('keywords', [])[:5])}
已提取的上下文：{analysis.get('context', '')}

原始文本：
{content[:1536]}

请直接返回摘要内容，不要包含其他格式："""
        
        try:
            messages = [
                {"role": "system", "content": "你是一个专业的内容分析助手，擅长提取文本的核心信息和关键情节。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=256)
            
            ***REMOVED*** 清理响应文本（移除可能的 markdown 格式）
            summary = response_text.strip()
            if summary.startswith("```"):
                ***REMOVED*** 移除 markdown 代码块标记
                lines = summary.split('\n')
                summary = '\n'.join([line for line in lines if not line.strip().startswith('```')])
            
            return summary[:500]  ***REMOVED*** 限制摘要长度
        except Exception as e:
            logger.error(f"Error generating content summary: {e}")
            ***REMOVED*** 如果生成摘要失败，返回一个简化的版本
            return content[:300] + "..." if len(content) > 300 else content
    
    def _search_similar_memories(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        搜索相似记忆（使用向量检索）
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            相似记忆列表
        """
        if not self.is_available() or self.embedding_model is None:
            return []
        
        ***REMOVED*** 检查 Qdrant 客户端是否可用
        if self.qdrant_client is None:
            logger.warning("Qdrant client not available, cannot search similar memories")
            return []
        
        try:
            ***REMOVED*** 获取查询向量
            query_vector = self._get_embedding(query)
            if query_vector is None:
                return []
            
            ***REMOVED*** 在 Qdrant 中搜索（使用 search API）
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,  ***REMOVED*** 查询向量
                limit=top_k,
            )
            
            ***REMOVED*** 转换为 Memory 对象
            memories = []
            ***REMOVED*** Qdrant search API 返回 ScoredPoint 列表
            points = search_results if isinstance(search_results, list) else []
            for point in points:
                ***REMOVED*** 获取 point ID（ScoredPoint 对象）
                point_id = point.id
                ***REMOVED*** Qdrant 返回的 ID 可能是 UUID 对象，需要转换为字符串
                if isinstance(point_id, uuid.UUID):
                    point_id_str = str(point_id)
                else:
                    point_id_str = str(point_id)
                
                ***REMOVED*** 查找对应的记忆
                memory = None
                ***REMOVED*** 首先尝试通过 ID 映射查找
                for mem_id, qdrant_id in self.id_mapping.items():
                    if str(qdrant_id) == point_id_str or qdrant_id == point_id:
                        if mem_id in self.memory_store:
                            memory = self.memory_store[mem_id]
                            break
                
                ***REMOVED*** 如果没找到，尝试直接匹配
                if not memory and point_id_str in self.memory_store:
                    memory = self.memory_store[point_id_str]
                
                ***REMOVED*** 如果还是没找到，尝试从 payload 中获取 original_id
                if not memory and hasattr(point, 'payload'):
                    original_id = point.payload.get('original_id') if point.payload else None
                    if original_id and original_id in self.memory_store:
                        memory = self.memory_store[original_id]
                
                if memory:
                    memories.append(memory)
            
            return memories
        except Exception as e:
            logger.error(f"Error searching similar memories: {e}")
            return []
    
    def _build_evolution_prompt(
        self,
        memory: Memory,
        neighbors_text: str,
        neighbor_count: int,
        new_context: Optional[str] = None,
    ) -> str:
        """
        构建记忆演化提示词
        
        Args:
            memory: 要演化的记忆
            neighbors_text: 邻居记忆的文本表示
            neighbor_count: 邻居数量
            new_context: 新上下文（可选）
            
        Returns:
            提示词字符串
        """
        context_part = f"\nNew context: {new_context}" if new_context else ""
        
        memory_type = "新记忆" if new_context is None else "记忆"
        context_instruction = f"和新上下文：{new_context}" if new_context else ""
        
        evolution_prompt = f"""你是一个专业的记忆演化代理，负责管理和演化知识库中的记忆。

请分析以下{memory_type}及其邻居记忆，判断是否需要演化以及应采取的行动。

{memory_type}信息：
- 上下文：{memory.context}
- 内容：{memory.content}
- 关键词：{', '.join(memory.keywords[:10])}

邻居记忆列表（每行以 memory_id 开头）：
{neighbors_text}{context_part}

请根据以上信息判断：
1. 这个记忆是否需要演化？请考虑它与其他记忆的关系{context_instruction}。
2. 应该采取什么具体行动（strengthen：加强连接，update_neighbor：更新邻居）？
   2.1 如果选择加强连接（strengthen），应该连接到哪些记忆？请使用上面邻居记忆中的 memory_id。同时，请提供这个记忆更新后的标签。
   2.2 如果选择更新邻居（update_neighbor），可以根据对这些记忆的理解更新它们的上下文和标签。如果不需要更新，新的上下文和标签应与原始值相同。请按照输入邻居的顺序生成新的上下文和标签。
   
标签应该根据记忆内容的特征来确定，以便后续检索和分类。
注意：new_tags_neighborhood 的长度必须等于输入邻居的数量，new_context_neighborhood 的长度也必须等于输入邻居的数量。
邻居数量：{neighbor_count}

请以 JSON 格式返回你的决策，结构如下：
{{
    "should_evolve": true 或 false,
    "actions": ["strengthen", "update_neighbor"],
    "suggested_connections": ["memory_id_1", "memory_id_2", ...],
    "tags_to_update": ["标签1", "标签2", ...],
    "new_context_neighborhood": ["新上下文1", "新上下文2", ...],
    "new_tags_neighborhood": [["标签1", "标签2", ...], ["标签1", "标签2", ...], ...]
}}"""

        return evolution_prompt

    def generate_links(self, new_note: Memory, top_k: int = 10) -> Set[str]:
        """
        为新记忆生成动态链接
        
        参考 A-Mem 的链接生成思路：
        1. 搜索相似记忆
        2. 使用 LLM 判断是否应该链接（process_memory 中的 strengthen 逻辑）
        3. 返回链接的记忆 ID 集合
        """
        if not self.is_available():
            return set()
        
        try:
            ***REMOVED*** 1. 搜索相似记忆
            similar_memories = self._search_similar_memories(new_note.content, top_k=top_k * 2)
            
            if not similar_memories:
                return set()
            
            ***REMOVED*** 2. 使用 LLM 判断是否应该链接
            ***REMOVED*** 构建提示词
            neighbors_text = ""
            memory_ids = []
            for mem in similar_memories[:top_k]:
                neighbors_text += f"memory_id:{mem.id}\ttimestamp:{mem.timestamp.isoformat()}\tcontent: {mem.content}\tcontext: {mem.context}\tkeywords: {str(mem.keywords)}\ttags: {str(mem.tags)}\n"
                memory_ids.append(mem.id)
            
            prompt = self._build_evolution_prompt(new_note, neighbors_text, len(memory_ids))
            
            messages = [
                {"role": "system", "content": "你是一个专业的记忆关系分析助手，擅长分析记忆之间的关联并做出演化决策。请始终以有效的 JSON 格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            
            ***REMOVED*** 解析响应
            response_json = self._parse_json_response(response_text)
            if response_json is None:
                logger.warning("Failed to parse evolution response, using fallback")
                ***REMOVED*** 回退：返回前 top_k 个相似记忆的 ID
                return set(mem.id for mem in similar_memories[:top_k])
            
            ***REMOVED*** 处理 strengthen 操作
            links = set()
            if response_json.get("should_evolve", False):
                actions = response_json.get("actions", [])
                if "strengthen" in actions:
                    suggested_connections = response_json.get("suggested_connections", [])
                    links.update(suggested_connections)
                    
                    ***REMOVED*** 更新标签
                    tags_to_update = response_json.get("tags_to_update", [])
                    if tags_to_update:
                        new_note.tags = tags_to_update
            
            return links
        except Exception as e:
            logger.error(f"Error generating links: {e}")
            return set()
    
    def find_related_memories(self, memory: Memory, top_k: int = 10) -> List[Memory]:
        """
        通过链接网络查找相关记忆
        
        参考 A-Mem 的网络遍历思路：
        1. 通过链接查找直接相关的记忆
        2. 通过向量检索查找语义相关的记忆
        """
        if not self.is_available():
            return []
        
        related = []
        seen_ids = {memory.id}
        
        ***REMOVED*** 1. 通过链接查找
        for link_id in memory.links:
            if link_id in self.memory_store and link_id not in seen_ids:
                related.append(self.memory_store[link_id])
                seen_ids.add(link_id)
        
        ***REMOVED*** 2. 通过向量检索查找语义相关的记忆
        if len(related) < top_k:
            semantic_memories = self._search_similar_memories(memory.content, top_k=top_k * 2)
            for mem in semantic_memories:
                if mem.id not in seen_ids and len(related) < top_k:
                    related.append(mem)
                    seen_ids.add(mem.id)
        
        return related[:top_k]
    
    def evolve_memory(self, memory: Memory, related: List[Memory], new_context: str) -> Memory:
        """
        演化记忆
        
        参考 A-Mem 的记忆演化思路：
        1. 使用 LLM 分析相关记忆
        2. 更新 tags, context, links
        """
        if not self.is_available() or not related:
            return memory
        
        try:
            ***REMOVED*** 构建相关记忆的文本
            neighbors_text = ""
            memory_ids = []
            for mem in related:
                neighbors_text += f"memory_id:{mem.id}\ttimestamp:{mem.timestamp.isoformat()}\tcontent: {mem.content}\tcontext: {mem.context}\tkeywords: {str(mem.keywords)}\ttags: {str(mem.tags)}\n"
                memory_ids.append(mem.id)
            
            prompt = self._build_evolution_prompt(memory, neighbors_text, len(memory_ids), new_context)
            
            messages = [
                {"role": "system", "content": "你是一个专业的记忆关系分析助手，擅长分析记忆之间的关联并做出演化决策。请始终以有效的 JSON 格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            
            ***REMOVED*** 解析响应
            response_json = self._parse_json_response(response_text)
            if response_json is None:
                logger.warning("Failed to parse evolution response, updating context only")
                memory.context = new_context
                return memory
            
            if response_json.get("should_evolve", False):
                actions = response_json.get("actions", [])
                
                ***REMOVED*** 处理 strengthen 操作
                if "strengthen" in actions:
                    suggested_connections = response_json.get("suggested_connections", [])
                    memory.links.update(suggested_connections)
                    
                    tags_to_update = response_json.get("tags_to_update", [])
                    if tags_to_update:
                        memory.tags = tags_to_update
                
                ***REMOVED*** 更新上下文
                memory.context = new_context
            
            return memory
        except Exception as e:
            logger.error(f"Error evolving memory: {e}")
            memory.context = new_context
            return memory
    
    def add_memory_to_vector_store(self, memory: Memory) -> bool:
        """
        将记忆添加到向量存储
        
        用于在 retain 操作后调用
        """
        if not self.is_available() or self.embedding_model is None:
            return False
        
        try:
            ***REMOVED*** 增强内容用于嵌入
            enhanced_content = self._enhance_content_for_embedding(memory)
            
            ***REMOVED*** 生成嵌入
            embedding = self._get_embedding(enhanced_content)
            if embedding is None:
                return False
            
            ***REMOVED*** 检查 Qdrant 客户端是否可用
            if self.qdrant_client is None:
                logger.warning("Qdrant client not available, cannot add memory to vector store")
                return False
            
            ***REMOVED*** 确保 ID 是有效的格式（Qdrant 要求字符串或整数）
            try:
                ***REMOVED*** 如果 memory.id 已在映射中，使用映射的ID
                if memory.id in self.id_mapping:
                    point_id = self.id_mapping[memory.id]
                else:
                    ***REMOVED*** 尝试将 memory.id 解析为 UUID，然后转换为字符串
                    try:
                        uuid_obj = uuid.UUID(memory.id) if isinstance(memory.id, str) else memory.id
                        ***REMOVED*** Qdrant PointStruct 要求 ID 是字符串或整数，不是 UUID 对象
                        point_id = str(uuid_obj)
                    except (ValueError, AttributeError, TypeError):
                        ***REMOVED*** 如果不是有效的 UUID，使用原始字符串
                        point_id = str(memory.id)
                    ***REMOVED*** 保存映射
                self.id_mapping[memory.id] = point_id
                original_id = None
            except Exception:
                ***REMOVED*** 如果以上都失败，生成一个新的 UUID 字符串并保存映射
                point_id = str(uuid.uuid4())
                self.id_mapping[memory.id] = point_id
                original_id = memory.id
            
            ***REMOVED*** 添加到 Qdrant
            payload = {
                "content": memory.content,
                "context": memory.context or "",
                "keywords": memory.keywords,
                "tags": memory.tags,
                "timestamp": memory.timestamp.isoformat(),
            }
            if original_id:
                payload["original_id"] = original_id
            
            ***REMOVED*** 使用PointStruct格式（Qdrant客户端要求）
            from qdrant_client.models import PointStruct
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            ***REMOVED*** 更新内存存储
            self.memory_store[memory.id] = memory
            
            logger.debug(f"Added memory {memory.id} to vector store")
            return True
        except Exception as e:
            logger.error(f"Error adding memory to vector store: {e}")
            return False
    
    def update_memory_in_vector_store(self, memory: Memory) -> bool:
        """更新向量存储中的记忆"""
        return self.add_memory_to_vector_store(memory)
    
    def delete_memory_from_vector_store(self, memory_id: str) -> bool:
        """从向量存储中删除记忆"""
        if not self.is_available():
            return False
        
        ***REMOVED*** 检查 Qdrant 客户端是否可用
        if self.qdrant_client is None:
            logger.warning("Qdrant client not available, cannot delete memory from vector store")
            return False
        
        try:
            ***REMOVED*** 查找对应的 Qdrant 点 ID
            point_id = None
            if memory_id in self.id_mapping:
                point_id = self.id_mapping[memory_id]
            else:
                ***REMOVED*** 尝试直接解析为 UUID
                try:
                    point_id = uuid.UUID(memory_id) if isinstance(memory_id, str) else memory_id
                except (ValueError, AttributeError, TypeError):
                    logger.warning(f"Memory ID {memory_id} is not a valid UUID and not in mapping, cannot delete from Qdrant")
                    ***REMOVED*** 仍然从内存存储中删除
                    if memory_id in self.memory_store:
                        del self.memory_store[memory_id]
                    if memory_id in self.id_mapping:
                        del self.id_mapping[memory_id]
                    return False
            
            ***REMOVED*** 使用正确的格式删除
            from qdrant_client.models import PointIdsList
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=PointIdsList(points=[point_id])
            )
            
            ***REMOVED*** 清理映射
            if memory_id in self.id_mapping:
                del self.id_mapping[memory_id]
            
            ***REMOVED*** 从内存存储中删除
            if memory_id in self.memory_store:
                del self.memory_store[memory_id]
            
            logger.debug(f"Deleted memory {memory_id} from vector store")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory from vector store: {e}")
            return False
    
    def optimize_prompt_and_context(
        self,
        input_text: str,
        execution_result: str,
        current_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        自动优化：根据输入和 Agent 执行结果来优化 prompt 或上下文结构
        
        根据需求文档：
        - 自动优化包括自动根据输入和 Agent 执行结果来优化 prompt 或上下文结构
        
        Args:
            input_text: 输入文本（会被截取前500字符用于分析）
            execution_result: Agent 执行结果（会被截取前500字符用于分析）
            current_prompt: 当前的 prompt（可选），如果提供会被用于优化
            
        Returns:
            优化结果字典，包含以下字段：
            - optimized_prompt: str - 优化后的 prompt
            - optimized_context: Dict[str, Any] - 优化后的上下文结构建议
            - analysis: Dict[str, Any] - 分析结果，包含：
                - satisfaction: 满足程度（"满足"/"部分满足"/"不满足"）
                - issues: 问题列表
                - suggestions: 建议列表
            
        Note:
            如果适配器不可用或发生错误，返回默认结构，不会抛出异常
        """
        if not self.is_available():
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }
        
        if not input_text or not input_text.strip():
            logger.warning("Empty input_text provided for optimize_prompt_and_context")
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }
        
        if not execution_result or not execution_result.strip():
            logger.warning("Empty execution_result provided for optimize_prompt_and_context")
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }
        
        try:
            ***REMOVED*** 限制文本长度以提高效率
            input_preview = input_text[:500] if len(input_text) > 500 else input_text
            result_preview = execution_result[:500] if len(execution_result) > 500 else execution_result
            prompt_preview = current_prompt[:500] if current_prompt and len(current_prompt) > 500 else (current_prompt or "无")
            
            prompt = f"""请分析以下输入和执行结果，优化 prompt 和上下文结构。

输入：
{input_preview}

执行结果：
{result_preview}

当前 Prompt（如果提供）：
{prompt_preview}

请分析：
1. 执行结果是否满足输入要求？
2. 如果未满足，prompt 或上下文结构需要如何优化？
3. 提供优化后的 prompt 和上下文结构建议

请以 JSON 格式返回结果：
{{
    "analysis": {{
        "satisfaction": "满足/部分满足/不满足",
        "issues": ["问题1", "问题2", ...],
        "suggestions": ["建议1", "建议2", ...]
    }},
    "optimized_prompt": "优化后的 prompt",
    "optimized_context": {{
        "structure": "上下文结构建议",
        "key_points": ["要点1", "要点2", ...]
    }}
}}"""
            
            messages = [
                {"role": "system", "content": "你是一个专业的 prompt 优化助手，擅长分析执行结果并优化 prompt 和上下文结构。请始终以有效的 JSON 格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            result = self._parse_json_response(response_text)
            
            if result:
                optimized_prompt = result.get("optimized_prompt", current_prompt or "")
                optimized_context = result.get("optimized_context", {})
                analysis = result.get("analysis", {})
                
                logger.debug(f"Optimized prompt and context: satisfaction={analysis.get('satisfaction', 'unknown')}, "
                           f"issues={len(analysis.get('issues', []))}, "
                           f"suggestions={len(analysis.get('suggestions', []))}")
                
                return {
                    "optimized_prompt": optimized_prompt,
                    "optimized_context": optimized_context,
                    "analysis": analysis
                }
            else:
                logger.warning(f"Failed to parse optimization response: {response_text[:200]}")
                return {
                    "optimized_prompt": current_prompt or "",
                    "optimized_context": {},
                    "analysis": {}
                }
        except Exception as e:
            logger.error(f"Error optimizing prompt and context: {e}", exc_info=True)
            return {
                "optimized_prompt": current_prompt or "",
                "optimized_context": {},
                "analysis": {}
            }

