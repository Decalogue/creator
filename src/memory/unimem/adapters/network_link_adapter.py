"""
网络链接适配器

实现 UniMem 的原子笔记网络和动态链接生成
参考架构：A-Mem（原子笔记网络 + 记忆演化）
"""

import json
import uuid
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
from abc import abstractmethod

from .base import BaseAdapter
from ..types import Entity, Memory
from ..chat import ark_deepseek_v3_2
import logging

logger = logging.getLogger(__name__)


class NetworkLinkAdapter(BaseAdapter):
    """
    网络链接适配器
    
    功能需求：原子笔记网络和动态链接生成
    参考架构：A-Mem（原子笔记网络 + 记忆演化）
    
    核心功能：
    1. 原子笔记构建：使用 LLM 分析内容，提取语义元数据
    2. 动态链接生成：基于语义相似度生成记忆链接
    3. 记忆演化：使用 LLM 判断并执行记忆演化
    4. 语义检索：基于向量相似度的语义检索
    5. 子图链接检索：通过链接网络的子图进行检索
    """
    
    def _do_initialize(self):
        """初始化网络链接适配器"""
        ***REMOVED*** 初始化记忆存储
        self.memory_store: Dict[str, Memory] = {}
        
        ***REMOVED*** 初始化属性（确保即使失败也有默认值）
        self.qdrant_client = None
        self.embedding_model = None
        self.collection_name = None
        
        ***REMOVED*** 向量存储：使用 Qdrant（已在配置中指定）
        qdrant_host = self.config.get("qdrant_host", "localhost")
        qdrant_port = self.config.get("qdrant_port", 6333)
        collection_name = self.config.get("collection_name", "unimem_memories")
        
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            
            self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
            
            ***REMOVED*** 创建集合（如果不存在）
            try:
                self.qdrant_client.get_collection(collection_name)
            except Exception:
                ***REMOVED*** 集合不存在，创建它
                self.qdrant_client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=384,  ***REMOVED*** all-MiniLM-L6-v2 的维度
                        distance=Distance.COSINE,
                    ),
                )
            
            self.collection_name = collection_name
            logger.info(f"Qdrant client connected: {qdrant_host}:{qdrant_port}")
        except Exception as e:
            logger.warning(f"Failed to connect to Qdrant: {e}. Vector operations will be limited.")
            self.qdrant_client = None
            self.collection_name = collection_name
        
        ***REMOVED*** 嵌入模型：使用 sentence-transformers（独立于 Qdrant）
        try:
            from sentence_transformers import SentenceTransformer
            import os
            
            ***REMOVED*** 优先使用本地模型路径（如果配置了）
            local_model_path = self.config.get("local_model_path", "/root/data/AI/pretrain/all-MiniLM-L6-v2")
            
            if os.path.exists(local_model_path):
                logger.info(f"Loading embedding model from local path: {local_model_path}")
                self.embedding_model = SentenceTransformer(local_model_path)
            else:
                logger.info("Local model not found, loading from HuggingFace: all-MiniLM-L6-v2")
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            logger.info(f"Embedding model loaded successfully (dimension: {self.embedding_model.get_sentence_embedding_dimension()})")
        except ImportError:
            logger.warning("sentence-transformers not available, semantic retrieval will be limited")
            self.embedding_model = None
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        
        logger.info("Network link adapter initialized (using A-Mem principles)")
    
    @abstractmethod
    def construct_atomic_note(self, content: str, timestamp: datetime, entities: List[Entity]) -> Memory:
        """
        构建原子笔记
        
        参考 A-Mem 的原子笔记构建思路
        """
        pass
    
    @abstractmethod
    def generate_links(self, new_note: Memory, top_k: int = 10) -> Set[str]:
        """
        为新记忆生成动态链接
        
        参考 A-Mem 的链接生成思路
        """
        pass
    
    @abstractmethod
    def find_related_memories(self, memory: Memory, top_k: int = 10) -> List[Memory]:
        """
        通过链接网络查找相关记忆
        
        参考 A-Mem 的网络遍历思路
        """
        pass
    
    @abstractmethod
    def evolve_memory(self, memory: Memory, related: List[Memory], new_context: str) -> Memory:
        """
        演化记忆
        
        参考 A-Mem 的记忆演化思路
        """
        pass
    
    def semantic_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        语义检索
        
        参考 A-Mem 的语义检索思路：
        使用向量相似度进行语义检索
        """
        return self._search_similar_memories(query, top_k=top_k)
    
    def subgraph_link_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        子图链接检索
        
        通过链接网络的子图进行检索：
        1. 先进行语义检索找到初始记忆
        2. 通过链接网络遍历子图，找到相关记忆
        """
        if not self.is_available():
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
        
        return all_memories[:top_k]
    
    def _parse_json_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        解析 LLM 返回的 JSON 响应
        
        支持从 markdown 代码块中提取 JSON
        
        Args:
            response_text: LLM 返回的文本
            
        Returns:
            解析后的 JSON 字典，如果解析失败返回 None
        """
        try:
            ***REMOVED*** 提取 JSON 部分（可能包含 markdown 代码块）
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            return json.loads(response_text)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            return None
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """
        使用 LLM 分析内容，提取语义元数据
        
        参考 A-Mem 的 analyze_content 方法
        
        Args:
            content: 要分析的内容
            
        Returns:
            包含 keywords, context, tags 的字典
        """
        prompt = """Generate a structured analysis of the following content by:
1. Identifying the most salient keywords (focus on nouns, verbs, and key concepts)
2. Extracting core themes and contextual elements
3. Creating relevant categorical tags

Format the response as a JSON object:
{
    "keywords": [
        // several specific, distinct keywords that capture key concepts and terminology
        // Order from most to least important
        // Don't include keywords that are the name of the speaker or time
        // At least three keywords, but don't be too redundant.
    ],
    "context": 
        // one sentence summarizing:
        // - Main topic/domain
        // - Key arguments/points
        // - Intended audience/purpose
    ,
    "tags": [
        // several broad categories/themes for classification
        // Include domain, format, and type tags
        // At least three tags, but don't be too redundant.
    ]
}

Content for analysis:
""" + content
        
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant that analyzes content and extracts structured metadata. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=1024)
            
            ***REMOVED*** 解析 JSON
            result = self._parse_json_response(response_text)
            if result:
                return {
                    "keywords": result.get("keywords", []),
                    "context": result.get("context", "General"),
                    "tags": result.get("tags", []),
                }
            else:
                logger.warning(f"Failed to parse LLM response as JSON: {response_text[:200]}")
                return {"keywords": [], "context": "General", "tags": []}
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return {"keywords": [], "context": "General", "tags": []}
    
    def _get_embedding(self, text: str) -> Optional[List[float]]:
        """获取文本的向量嵌入"""
        if self.embedding_model is None:
            return None
        try:
            return self.embedding_model.encode(text).tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
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
    
    def construct_atomic_note(self, content: str, timestamp: datetime, entities: List[Entity]) -> Memory:
        """
        构建原子笔记
        
        参考 A-Mem 的原子笔记构建思路：
        1. 使用 LLM 分析内容，提取 keywords, context, tags
        2. 创建 Memory 对象
        3. 生成唯一 ID
        """
        ***REMOVED*** 分析内容
        analysis = self._analyze_content(content)
        
        ***REMOVED*** 构建 Memory 对象
        memory_id = str(uuid.uuid4())
        memory = Memory(
            id=memory_id,
            content=content,
            timestamp=timestamp,
            keywords=analysis.get("keywords", []),
            context=analysis.get("context", "General"),
            tags=analysis.get("tags", []),
            entities=[e.id for e in entities] if entities else [],
        )
        
        ***REMOVED*** 存储到内存中（用于快速访问）
        self.memory_store[memory_id] = memory
        
        logger.debug(f"Constructed atomic note: {memory_id} with {len(memory.keywords)} keywords, {len(memory.tags)} tags")
        return memory
    
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
            
            ***REMOVED*** 在 Qdrant 中搜索
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
            )
            
            ***REMOVED*** 转换为 Memory 对象
            memories = []
            for result in search_results:
                memory_id = result.id
                if memory_id in self.memory_store:
                    memories.append(self.memory_store[memory_id])
            
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
        
        return f"""You are an AI memory evolution agent responsible for managing and evolving a knowledge base.
Analyze the {'new ' if new_context is None else ''}memory note according to keywords and context, also with their several nearest neighbors memory.
Make decisions about its evolution.

The {'new ' if new_context is None else ''}memory context:
context: {memory.context}
content: {memory.content}
keywords: {memory.keywords}

The nearest neighbors memories (each line starts with memory_id):
{neighbors_text}{context_part}

Based on this information, determine:
1. Should this memory be evolved? Consider its relationships with other memories{' and the new context' if new_context else ''}.
2. What specific actions should be taken (strengthen, update_neighbor)?
   2.1 If choose to strengthen the connection, which memory should it be connected to? Use the memory_id from the neighbors above. Can you give the updated tags of this memory?
   2.2 If choose to update_neighbor, you can update the context and tags of these memories based on the understanding of these memories. If the context and the tags are not updated, the new context and tags should be the same as the original ones. Generate the new context and tags in the sequential order of the input neighbors.
Tags should be determined by the content of these characteristic of these memories, which can be used to retrieve them later and categorize them.
Note that the length of new_tags_neighborhood must equal the number of input neighbors, and the length of new_context_neighborhood must equal the number of input neighbors.
The number of neighbors is {neighbor_count}.
Return your decision in JSON format with the following structure:
{{
    "should_evolve": true or false,
    "actions": ["strengthen", "update_neighbor"],
    "suggested_connections": ["memory_id_1", "memory_id_2", ...],
    "tags_to_update": ["tag_1",..."tag_n"],
    "new_context_neighborhood": ["new context",...,"new context"],
    "new_tags_neighborhood": [["tag_1",...,"tag_n"],...["tag_1",...,"tag_n"]],
}}"""
    
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
                {"role": "system", "content": "You are a helpful assistant that analyzes memory relationships. Always respond with valid JSON."},
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
                {"role": "system", "content": "You are a helpful assistant that analyzes memory relationships. Always respond with valid JSON."},
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
            
            ***REMOVED*** 添加到 Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": memory.id,
                    "vector": embedding,
                    "payload": {
                        "content": memory.content,
                        "context": memory.context or "",
                        "keywords": memory.keywords,
                        "tags": memory.tags,
                        "timestamp": memory.timestamp.isoformat(),
                    }
                }]
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
        
        ***REMOVED*** 检查 Qdrant 客户端是否可用
        if self.qdrant_client is None:
            logger.warning("Qdrant client not available, cannot delete memory from vector store")
            return False
        
        try:
            self.qdrant_client.delete(
                collection_name=self.collection_name,
                points_selector=[memory_id]
            )
            
            ***REMOVED*** 从内存存储中删除
            if memory_id in self.memory_store:
                del self.memory_store[memory_id]
            
            logger.debug(f"Deleted memory {memory_id} from vector store")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory from vector store: {e}")
            return False
