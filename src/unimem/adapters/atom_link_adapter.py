"""
原子链接适配器

实现 UniMem 的原子笔记网络和动态链接生成
参考架构：A-Mem（原子笔记网络 + 记忆演化）
"""
import os
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Set
from qdrant_client.models import PointIdsList

from .base import BaseAdapter
from ..types import Entity, Memory
from ..chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


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
    
    def _do_initialize(self):
        """初始化原子链接适配器"""
        ***REMOVED*** 初始化记忆存储
        self.memory_store: Dict[str, Memory] = {}
        ***REMOVED*** ID 映射：memory.id -> qdrant_point_id (用于处理非 UUID 格式的 ID)
        self.id_mapping: Dict[str, Any] = {}
        
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
                        size=384,  ***REMOVED*** multilingual-e5-small 的维度
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
            
            ***REMOVED*** 优先使用本地模型路径（如果配置了）
            ***REMOVED*** 默认使用 multilingual-e5-small（支持中文）
            local_model_path = self.config.get("local_model_path", "/root/data/AI/pretrain/multilingual-e5-small")
            
            if os.path.exists(local_model_path):
                logger.info(f"Loading embedding model from local path: {local_model_path}")
                self.embedding_model = SentenceTransformer(local_model_path)
            else:
                logger.info("Local model not found, loading from HuggingFace: multilingual-e5-small")
                self.embedding_model = SentenceTransformer('intfloat/multilingual-e5-small')
            
            logger.info(f"Embedding model loaded successfully (dimension: {self.embedding_model.get_sentence_embedding_dimension()})")
        except ImportError:
            logger.warning("sentence-transformers not available, semantic retrieval will be limited")
            self.embedding_model = None
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        
        logger.info("Atom link adapter initialized (using A-Mem principles)")
    
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
    
    def _analyze_content(self, content: str, max_new_tokens: int = 1024, is_creative_content: bool = False) -> Dict[str, Any]:
        """
        使用 LLM 分析内容，提取语义元数据
        
        参考 A-Mem 的 analyze_content 方法
        增强：支持创作助手的多维度分析（文章/小说类型，写作风格，故事线，场景，人物，事件，线索等）
        
        Args:
            content: 要分析的内容
            is_creative_content: 是否为创作内容（小说/文章），如果是则提取创作相关维度
            
        Returns:
            包含 keywords, context, tags 的字典，如果是创作内容还包含创作相关维度
        """
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
    
    def construct_atomic_note(self, content: str, timestamp: datetime, entities: List[Entity], generate_summary: bool = True, is_creative_content: bool = False) -> Memory:
        """
        构建原子笔记
        
        参考 A-Mem 的原子笔记构建思路：
        1. 使用 LLM 分析内容，提取 keywords, context, tags
        2. 可选：使用 LLM 生成摘要性内容（而不是直接使用原始文本）
        3. 创建 Memory 对象
        4. 生成唯一 ID
        
        Args:
            content: 原始内容
            timestamp: 时间戳
            entities: 实体列表
            generate_summary: 是否生成摘要性内容（True：生成摘要，False：使用原始内容）
            is_creative_content: 是否为创作内容（小说/文章），如果是则提取创作相关维度
        """
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
            
            ***REMOVED*** 在 Qdrant 中搜索（使用 query_points API）
            ***REMOVED*** query 参数可以直接接受列表，Qdrant 会自动处理
            search_results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,  ***REMOVED*** 直接使用列表，Qdrant 会自动转换为向量查询
                limit=top_k,
            )
            
            ***REMOVED*** 转换为 Memory 对象
            memories = []
            ***REMOVED*** Qdrant 返回的是 QueryResponse 对象，需要访问 points
            points = search_results.points if hasattr(search_results, 'points') else []
            for point in points:
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
            
            ***REMOVED*** 确保 ID 是有效的 UUID 格式（Qdrant 要求）
            try:
                ***REMOVED*** 尝试将 memory.id 解析为 UUID
                point_id = uuid.UUID(memory.id) if isinstance(memory.id, str) else memory.id
                ***REMOVED*** 如果已经是 UUID，直接使用
                if memory.id in self.id_mapping:
                    point_id = self.id_mapping[memory.id]
                else:
                    self.id_mapping[memory.id] = point_id
            except (ValueError, AttributeError, TypeError):
                ***REMOVED*** 如果不是有效的 UUID，生成一个新的 UUID 并保存映射
                point_id = uuid.uuid4()
                self.id_mapping[memory.id] = point_id
                original_id = memory.id
            else:
                original_id = None
            
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
            
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": point_id,
                    "vector": embedding,
                    "payload": payload
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
    
    ***REMOVED*** ==================== 创作助手增强功能 ====================
    
    def structure_content_hierarchy(self, chapters: List[str], level: str = "summary") -> Dict[str, Any]:
        """
        多层级结构化：章节->摘要->大纲->简介
        
        根据需求文档：
        - 流程：章节->摘要->大纲->简介
        - 维度：文章/小说类型，写作风格，故事线，场景，人物，事件，线索等
        
        Args:
            chapters: 章节内容列表
            level: 结构化层级 ("summary" | "outline" | "synopsis")
            
        Returns:
            结构化结果字典，包含层级内容和元数据
        """
        if not self.is_available():
            logger.warning("AtomLinkAdapter not available, cannot perform structure_content_hierarchy")
            return {}
        
        try:
            ***REMOVED*** 根据层级选择不同的 prompt
            if level == "summary":
                ***REMOVED*** 章节 -> 摘要
                prompt = f"""请对以下章节内容进行结构化摘要，提取关键信息。

要求：
1. 提取核心事件、情节和关键信息
2. 识别主要角色、场景和重要关系
3. 保持信息的准确性和完整性
4. 摘要长度控制在200-300字左右

章节内容：
{chr(10).join([f"章节{i+1}: {ch[:500]}" for i, ch in enumerate(chapters[:10])])}

请以 JSON 格式返回结果：
{{
    "summaries": ["摘要1", "摘要2", ...],
    "metadata": {{
        "total_chapters": {len(chapters)},
        "extracted_info": {{
            "characters": ["角色1", "角色2", ...],
            "scenes": ["场景1", "场景2", ...],
            "events": ["事件1", "事件2", ...]
        }}
    }}
}}"""
            elif level == "outline":
                ***REMOVED*** 摘要 -> 大纲
                prompt = f"""请根据以下摘要内容生成故事大纲。

要求：
1. 提取主要故事线和情节结构
2. 识别关键转折点和冲突
3. 整理时间线和因果关系
4. 大纲应该清晰、层次分明

摘要内容：
{chr(10).join([f"摘要{i+1}: {ch[:300]}" for i, ch in enumerate(chapters[:20])])}

请以 JSON 格式返回结果：
{{
    "outline": {{
        "main_storyline": "主要故事线",
        "plot_points": ["情节点1", "情节点2", ...],
        "conflicts": ["冲突1", "冲突2", ...],
        "turning_points": ["转折点1", "转折点2", ...]
    }},
    "metadata": {{
        "structure_type": "故事结构类型",
        "themes": ["主题1", "主题2", ...]
    }}
}}"""
            else:  ***REMOVED*** level == "synopsis"
                ***REMOVED*** 大纲 -> 简介
                prompt = f"""请根据以下大纲内容生成作品简介。

要求：
1. 概括整个作品的核心内容
2. 突出主要角色和关键冲突
3. 吸引读者兴趣
4. 简介长度控制在150-200字左右

大纲内容：
{chr(10).join([f"{ch[:400]}" for ch in chapters[:5]])}

请以 JSON 格式返回结果：
{{
    "synopsis": "作品简介内容",
    "metadata": {{
        "genre": "作品类型",
        "writing_style": "写作风格",
        "target_audience": "目标受众"
    }}
}}"""
            
            messages = [
                {"role": "system", "content": "你是一个专业的创作助手，擅长对内容进行多层级结构化分析。请始终以有效的 JSON 格式返回结果。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
            result = self._parse_json_response(response_text)
            
            if result:
                return result
            else:
                logger.warning(f"Failed to parse structure hierarchy response: {response_text[:200]}")
                return {}
        except Exception as e:
            logger.error(f"Error structuring content hierarchy: {e}")
            return {}
    
    def retrieve_with_reward(self, query: str, original_contents: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        根据结构化结果检索原内容，并计算奖励
        
        根据需求文档：
        - 奖励 = 1 - index/N，其中 index 为索引，N 为原内容列表
        - 例如对于原章节结构化的摘要，使用摘要在所有章节(N)中检索原章节，索引越靠前奖励越高
        
        Args:
            query: 查询文本（通常是结构化后的摘要/大纲/简介）
            original_contents: 原始内容列表（如原章节列表）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表，每个结果包含 memory、score 和 reward
        """
        if not self.is_available():
            return []
        
        try:
            ***REMOVED*** 1. 使用结构化查询检索相似记忆
            similar_memories = self._search_similar_memories(query, top_k=top_k * 2)
            
            ***REMOVED*** 2. 匹配到原始内容并计算奖励
            results = []
            N = len(original_contents)
            
            for idx, memory in enumerate(similar_memories[:top_k]):
                ***REMOVED*** 尝试匹配到原始内容
                matched_index = None
                for orig_idx, orig_content in enumerate(original_contents):
                    ***REMOVED*** 简单的匹配逻辑：检查记忆内容是否与原始内容相似
                    if memory.content[:100] in orig_content or orig_content[:100] in memory.content:
                        matched_index = orig_idx
                        break
                
                ***REMOVED*** 计算奖励：reward = 1 - index/N
                if matched_index is not None:
                    reward = 1.0 - (matched_index / N) if N > 0 else 1.0
                else:
                    ***REMOVED*** 如果无法匹配，使用检索排名计算奖励
                    reward = 1.0 - (idx / top_k) if top_k > 0 else 1.0
                
                results.append({
                    "memory": memory,
                    "score": memory.metadata.get("similarity_score", 1.0 - idx / top_k),
                    "reward": reward,
                    "original_index": matched_index,
                    "retrieval_rank": idx + 1
                })
            
            ***REMOVED*** 按奖励排序
            results.sort(key=lambda x: x["reward"], reverse=True)
            return results[:top_k]
        except Exception as e:
            logger.error(f"Error retrieving with reward: {e}")
            return []
    
    def generate_from_hierarchy(self, synopsis: str, target_level: str = "chapter", context_memories: List[Memory] = None) -> str:
        """
        生成流程：简介->大纲->摘要->章节
        
        根据需求文档：
        - 流程：简介->大纲->摘要->章节
        - 上下文：与当前生成目标相关的原子笔记
        
        Args:
            synopsis: 简介内容
            target_level: 目标层级 ("outline" | "summary" | "chapter")
            context_memories: 相关的原子笔记（用于提供上下文）
            
        Returns:
            生成的内容
        """
        if not self.is_available():
            logger.warning("AtomLinkAdapter not available, cannot perform generate_from_hierarchy")
            return ""
        
        try:
            ***REMOVED*** 构建上下文信息
            context_text = ""
            if context_memories:
                context_text = "\n相关原子笔记：\n"
                for mem in context_memories[:5]:
                    context_text += f"- {mem.content[:200]}\n"
                    if mem.metadata.get("creative_dimensions"):
                        dims = mem.metadata["creative_dimensions"]
                        if dims.get("characters"):
                            context_text += f"  人物: {', '.join(dims['characters'][:3])}\n"
                        if dims.get("scenes"):
                            context_text += f"  场景: {', '.join(dims['scenes'][:3])}\n"
            
            ***REMOVED*** 根据目标层级选择不同的 prompt
            if target_level == "outline":
                prompt = f"""请根据以下作品简介生成详细的故事大纲。

要求：
1. 扩展主要故事线和情节结构
2. 设计关键转折点和冲突
3. 规划时间线和因果关系
4. 大纲应该详细、层次分明

作品简介：
{synopsis}

{context_text}

请以 JSON 格式返回结果：
{{
    "outline": {{
        "main_storyline": "主要故事线",
        "plot_points": ["情节点1", "情节点2", ...],
        "conflicts": ["冲突1", "冲突2", ...],
        "turning_points": ["转折点1", "转折点2", ...]
    }}
}}"""
            elif target_level == "summary":
                prompt = f"""请根据以下故事大纲生成章节摘要。

要求：
1. 为每个主要情节点生成摘要
2. 保持与大纲的一致性
3. 摘要应该清晰、连贯

故事大纲：
{synopsis}

{context_text}

请以 JSON 格式返回结果：
{{
    "summaries": ["摘要1", "摘要2", ...]
}}"""
            else:  ***REMOVED*** target_level == "chapter"
                prompt = f"""请根据以下内容生成具体的章节内容。

要求：
1. 扩展摘要为完整的章节内容
2. 包含对话、场景描写和情节推进
3. 保持风格一致性和连贯性
4. 章节长度控制在1000-2000字左右

内容：
{synopsis}

{context_text}

请直接返回章节内容，不要包含其他格式："""
            
            messages = [
                {"role": "system", "content": "你是一个专业的创作助手，擅长根据结构化内容生成创作内容。请保持风格一致性和连贯性。"},
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
            
            ***REMOVED*** 清理响应文本
            if target_level in ["outline", "summary"]:
                result = self._parse_json_response(response_text)
                if result:
                    if target_level == "outline":
                        return json.dumps(result.get("outline", {}), ensure_ascii=False, indent=2)
                    else:
                        return "\n".join(result.get("summaries", []))
            
            ***REMOVED*** 对于章节，直接返回文本
            return response_text.strip()
        except Exception as e:
            logger.error(f"Error generating from hierarchy: {e}")
            return ""
    
    def optimize_prompt_and_context(self, input_text: str, execution_result: str, current_prompt: str = None) -> Dict[str, Any]:
        """
        自动优化：根据输入和 Agent 执行结果来优化 prompt 或上下文结构
        
        根据需求文档：
        - 自动优化包括自动根据输入和 Agent 执行结果来优化 prompt 或上下文结构
        
        Args:
            input_text: 输入文本
            execution_result: Agent 执行结果
            current_prompt: 当前的 prompt（可选）
            
        Returns:
            优化后的 prompt 和上下文结构
        """
        if not self.is_available():
            return {"optimized_prompt": current_prompt or "", "optimized_context": {}}
        
        try:
            prompt = f"""请分析以下输入和执行结果，优化 prompt 和上下文结构。

输入：
{input_text[:500]}

执行结果：
{execution_result[:500]}

当前 Prompt（如果提供）：
{current_prompt[:500] if current_prompt else "无"}

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
                return {
                    "optimized_prompt": result.get("optimized_prompt", current_prompt or ""),
                    "optimized_context": result.get("optimized_context", {}),
                    "analysis": result.get("analysis", {})
                }
            else:
                logger.warning(f"Failed to parse optimization response: {response_text[:200]}")
                return {"optimized_prompt": current_prompt or "", "optimized_context": {}, "analysis": {}}
        except Exception as e:
            logger.error(f"Error optimizing prompt and context: {e}")
            return {"optimized_prompt": current_prompt or "", "optimized_context": {}, "analysis": {}}

