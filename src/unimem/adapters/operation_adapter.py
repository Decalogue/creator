"""
操作接口适配器

实现 UniMem 的 Retain/Recall/Reflect 三大操作
参考架构：Hindsight（三操作范式 + 四大逻辑网络）

核心思路迁移自 Hindsight Python Client：
1. RETAIN: 支持批量存储，MemoryItem 结构（content, timestamp, context, metadata, document_id）
2. RECALL: 支持类型过滤、预算控制、max_tokens、时间查询、实体和块包含
3. REFLECT: 基于 Agent Profile（background + disposition），支持预算控制和上下文
4. 四大记忆类型：world, experience, opinion, observation
5. Disposition Traits：skepticism, literalism, empathy（1-5 分）

工业级特性：
- 完善的类型提示和验证
- 统一的错误处理
- 配置验证
- 性能监控
"""

from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
import logging
import time

from .base import (
    BaseAdapter,
    AdapterConfigurationError,
    AdapterError
)
from ..types import Experience, Memory, Task, Context, MemoryType
from ..chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


class Budget(str, Enum):
    """
    预算级别（参考 Hindsight）
    
    用于控制 RECALL 和 REFLECT 操作的资源消耗
    """
    LOW = "low"    ***REMOVED*** 低预算：快速、基础检索
    MID = "mid"    ***REMOVED*** 中等预算：平衡质量和速度
    HIGH = "high"  ***REMOVED*** 高预算：全面、深度检索


class OperationAdapter(BaseAdapter):
    """
    操作接口适配器
    
    功能需求：实现 Retain/Recall/Reflect 三大操作
    参考架构：HindSight（三操作范式）
    """
    
    def _do_initialize(self) -> None:
        """
        初始化操作适配器
        
        参考 Hindsight 的初始化思路。
        这里可以集成 Hindsight 的客户端，但接口按照 UniMem 的需求定义。
        
        Raises:
            AdapterConfigurationError: 如果配置无效
        """
        ***REMOVED*** 验证 LLM 配置（如果使用）
        llm_provider = self.config.get("llm_provider", "openai")
        llm_model = self.config.get("llm_model", "gpt-4o-mini")
        
        if not llm_provider or not isinstance(llm_provider, str):
            raise AdapterConfigurationError(
                "Invalid llm_provider configuration",
                adapter_name=self.__class__.__name__
            )
        
        if not llm_model or not isinstance(llm_model, str):
            raise AdapterConfigurationError(
                "Invalid llm_model configuration",
                adapter_name=self.__class__.__name__
            )
        
        logger.info(
            f"Operation adapter initialized "
            f"(using Hindsight principles, LLM: {llm_provider}/{llm_model})"
        )
    
    def retain(
        self,
        experience: Experience,
        context: Context,
        document_id: Optional[str] = None,
    ) -> Memory:
        """
        存储新记忆（RETAIN 操作）
        
        参考 Hindsight 的 retain 思路：
        - 将经验转换为结构化的记忆单元（叙事性事实提取）
        - 提取事实、生成嵌入、实体解析、构建链接
        - 支持 document_id 分组（参考 Hindsight MemoryItem）
        
        Args:
            experience: 经验对象
            context: 上下文信息
            document_id: 文档ID（用于分组相关记忆，参考 Hindsight）
            
        Returns:
            创建的 Memory 对象
        
        Raises:
            ValueError: 如果输入参数无效
            AdapterError: 如果操作失败
        """
        if not experience or not experience.content:
            raise ValueError("Experience content cannot be empty")
        
        if not context:
            raise ValueError("Context cannot be None")
        
        start_time = time.time()
        logger.debug(f"RETAIN: Storing experience: {experience.content[:50]}...")
        
        try:
            ***REMOVED*** 参考 Hindsight 的 retain 逻辑：
            ***REMOVED*** 1. 事实提取（what, when, where, who, why）
            ***REMOVED*** 2. 生成嵌入
            ***REMOVED*** 3. 实体解析
            ***REMOVED*** 4. 构建链接（时间、语义、实体、因果）
            
            ***REMOVED*** 创建基础 Memory 对象
            ***REMOVED*** 注意：实际的记忆类型分类和结构化处理会在 core.py 的 retain 方法中完成
            ***REMOVED*** 这里只返回基础结构
            memory_id = f"mem_{datetime.now().timestamp()}_{id(experience)}"
            memory = Memory(
                id=memory_id,
                content=experience.content,
                timestamp=experience.timestamp or datetime.now(),
                context=experience.context or context.metadata.get("context", ""),
                metadata=experience.metadata.copy() if experience.metadata else {},
            )
            
            ***REMOVED*** 添加 document_id 到 metadata（参考 Hindsight）
            if document_id:
                memory.metadata["document_id"] = str(document_id)
            
            duration = time.time() - start_time
            logger.debug(f"RETAIN: Created memory {memory_id} ({duration:.3f}s)")
            return memory
        except Exception as e:
            logger.error(f"Error in retain operation: {e}", exc_info=True)
            raise AdapterError(
                f"Failed to retain experience: {e}",
                adapter_name=self.__class__.__name__,
                cause=e
            ) from e
    
    def retain_batch(
        self,
        experiences: List[Experience],
        context: Context,
        document_id: Optional[str] = None,
        retain_async: bool = False,
    ) -> List[Memory]:
        """
        批量存储记忆（RETAIN 批量操作）
        
        参考 Hindsight 的 retain_batch 思路：
        - 支持批量处理多个经验
        - 支持统一的 document_id 分组
        - 支持异步处理选项
        
        Args:
            experiences: 经验对象列表
            context: 上下文信息
            document_id: 文档ID（用于分组相关记忆）
            retain_async: 是否异步处理（默认 False）
            
        Returns:
            创建的 Memory 对象列表
        """
        logger.debug(f"RETAIN_BATCH: Storing {len(experiences)} experiences...")
        
        memories = []
        for experience in experiences:
            memory = self.retain(
                experience=experience,
                context=context,
                document_id=document_id,
            )
            memories.append(memory)
        
        logger.debug(f"RETAIN_BATCH: Created {len(memories)} memories")
        return memories
    
    def recall(
        self,
        query: str,
        context: Context,
        top_k: int = 10,
        memory_types: Optional[List[MemoryType]] = None,
        budget: Union[Budget, str] = Budget.MID,
        max_tokens: int = 4096,
        query_timestamp: Optional[datetime] = None,
        include_entities: bool = False,
        include_chunks: bool = False,
        abstraction_level: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        检索相关记忆（RECALL 操作）
        
        参考 Hindsight 的 recall 思路：
        - 四路并行检索：语义、BM25、图、时间
        - RRF 融合和重排序
        - Token 预算过滤
        - 支持类型过滤、预算控制、时间查询
        - 支持抽象层级过滤（MemMachine 维度）
        
        Args:
            query: 查询字符串
            context: 上下文信息
            top_k: 返回结果数量
            memory_types: 记忆类型过滤（可选，支持 Hindsight 的四大类型：world, experience, opinion, observation）
            budget: 预算级别（low/mid/high，参考 Hindsight）
            max_tokens: 最大 token 数（默认 4096）
            query_timestamp: 查询时间戳（用于时间相关检索）
            include_entities: 是否包含实体信息（默认 False）
            include_chunks: 是否包含原始文本块（默认 False）
            abstraction_level: 抽象层级过滤（可选，"episodic" | "semantic" | "user_profile"）
                - episodic: 具体事件、交互细节（适合时间相关查询）
                - semantic: 抽象概念、知识结构（适合概念查询）
                - user_profile: 用户偏好、行为模式（适合个性化查询）
            
        Returns:
            检索结果字典（参考 Hindsight RecallResponse）：
            {
                "results": List[Memory],  ***REMOVED*** 检索到的记忆列表
                "trace": Optional[Dict],  ***REMOVED*** 调试追踪信息（如果启用）
                "entities": Optional[Dict],  ***REMOVED*** 实体信息（如果 include_entities=True）
                "chunks": Optional[Dict],  ***REMOVED*** 原始文本块（如果 include_chunks=True）
            }
        """
        logger.debug(f"RECALL: Query: {query[:50]}..., budget: {budget}, max_tokens: {max_tokens}, "
                    f"abstraction_level: {abstraction_level}")
        
        ***REMOVED*** 参考 Hindsight 的 recall 逻辑：
        ***REMOVED*** 1. 四路并行检索（语义、BM25、图、时间）
        ***REMOVED*** 2. RRF 融合
        ***REMOVED*** 3. 重排序
        ***REMOVED*** 4. Token 预算过滤
        
        ***REMOVED*** 注意：实际的检索逻辑在 retrieval_engine.py 中实现
        ***REMOVED*** 这里只是接口定义，返回空结果表示需要由上层调用检索引擎
        
        ***REMOVED*** 转换 memory_types 为字符串列表（如果提供）
        type_filters = None
        if memory_types:
            type_filters = [mt.value for mt in memory_types]
        
        ***REMOVED*** 转换 budget 为字符串
        budget_str = budget.value if isinstance(budget, Budget) else str(budget)
        
        ***REMOVED*** 验证 abstraction_level 参数
        if abstraction_level and abstraction_level not in ("episodic", "semantic", "user_profile"):
            logger.warning(f"Invalid abstraction_level '{abstraction_level}', ignoring filter")
            abstraction_level = None
        
        ***REMOVED*** 临时实现：返回空结果，实际检索由 core.py 调用 retrieval_engine
        ***REMOVED*** 注意：abstraction_level 过滤应该在检索引擎中实现
        return {
            "results": [],
            "trace": None,
            "entities": None if not include_entities else {},
            "chunks": None if not include_chunks else {},
        }
    
    def reflect(
        self,
        memories: List[Memory],
        task: Task,
        agent_disposition: Optional[Dict[str, Any]] = None,
        agent_background: Optional[str] = None,
        budget: Union[Budget, str] = Budget.LOW,
    ) -> Dict[str, Any]:
        """
        更新和优化记忆（REFLECT 操作）
        
        参考 Hindsight 的 reflect 思路（CARA: Coherent Adaptive Reasoning Agents）：
        - 基于检索到的事实（experience, world, opinion, observation）进行推理
        - 使用 Agent Profile（Disposition + Background）进行个性化生成
        - 生成答案并更新信念（Opinion）
        - 支持预算控制
        
        Args:
            memories: 要反思的记忆列表
            task: 任务上下文
            agent_disposition: Agent 性格配置（参考 Hindsight DispositionTraits）：
                - skepticism: int (1-5) - 怀疑度（1=信任，5=怀疑）
                - literalism: int (1-5) - 字面度（1=灵活，5=字面）
                - empathy: int (1-5) - 同理心（1=超然，5=共情）
            agent_background: Agent 背景信息（参考 Hindsight Bank background）
            budget: 预算级别（low/mid/high，默认 low，参考 Hindsight）
            
        Returns:
            包含答案和更新后记忆的字典（参考 Hindsight ReflectResponse）：
            {
                "answer": str,  ***REMOVED*** 生成的答案文本
                "based_on": List[Dict],  ***REMOVED*** 基于的事实列表（参考 Hindsight ReflectFact）
                "updated_memories": List[Memory],  ***REMOVED*** 更新后的记忆
                "new_opinions": List[Memory],  ***REMOVED*** 新形成的观点
            }
        """
        logger.debug(f"REFLECT: Reflecting on {len(memories)} memories for task: {task.description[:50]}..., budget: {budget}")
        
        ***REMOVED*** 转换 budget 为字符串
        budget_str = budget.value if isinstance(budget, Budget) else str(budget)
        
        ***REMOVED*** 参考 Hindsight 的 reflect 逻辑（CARA）：
        ***REMOVED*** 1. 按类型分组记忆（world, experience, opinion, observation）
        ***REMOVED*** 2. 构建上下文（包含事实和 Agent Profile）
        ***REMOVED*** 3. 使用 LLM 生成答案（带 Disposition Conditioning）
        ***REMOVED*** 4. 提取新观点并更新置信度
        ***REMOVED*** 5. 记录基于的事实（based_on）
        
        ***REMOVED*** 按 Hindsight 类型分组记忆（认知属性维度）
        world_facts = [m for m in memories if m.memory_type == MemoryType.WORLD]
        experience_facts = [m for m in memories if m.memory_type == MemoryType.EXPERIENCE]
        opinion_facts = [m for m in memories if m.memory_type == MemoryType.OPINION]
        observation_facts = [m for m in memories if m.memory_type == MemoryType.OBSERVATION]
        
        ***REMOVED*** 按抽象层级分组记忆（MemMachine 维度）- 用于优化推理策略
        episodic_memories = self._filter_by_abstraction_level(memories, "episodic")
        semantic_memories = self._filter_by_abstraction_level(memories, "semantic")
        user_profile_memories = self._filter_by_abstraction_level(memories, "user_profile")
        
        logger.debug(f"Memory breakdown (cognitive): World={len(world_facts)}, Experience={len(experience_facts)}, "
                    f"Opinion={len(opinion_facts)}, Observation={len(observation_facts)}")
        logger.debug(f"Memory breakdown (abstraction): Episodic={len(episodic_memories)}, "
                    f"Semantic={len(semantic_memories)}, UserProfile={len(user_profile_memories)}")
        
        ***REMOVED*** 根据预算调整使用的记忆数量（参考 Hindsight）
        max_facts_per_type = self._get_max_facts_by_budget(budget_str)
        world_facts = world_facts[:max_facts_per_type]
        experience_facts = experience_facts[:max_facts_per_type]
        opinion_facts = opinion_facts[:max_facts_per_type]
        observation_facts = observation_facts[:max_facts_per_type]
        
        ***REMOVED*** 构建反思提示词（考虑抽象层级优化）
        prompt = self._build_reflect_prompt(
            query=task.description,
            world_facts=world_facts,
            experience_facts=experience_facts,
            opinion_facts=opinion_facts,
            observation_facts=observation_facts,
            episodic_memories=episodic_memories,
            semantic_memories=semantic_memories,
            user_profile_memories=user_profile_memories,
            agent_disposition=agent_disposition,
            agent_background=agent_background,
            context=task.context,
        )
        
        ***REMOVED*** 调用 LLM 生成答案
        try:
            system_message = self._build_reflect_system_message(agent_disposition)
            
            ***REMOVED*** 根据预算调整 max_new_tokens（参考 Hindsight）
            max_tokens = self._get_max_tokens_by_budget(budget_str)
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            _, answer_text = ark_deepseek_v3_2(messages, max_new_tokens=max_tokens)
            
            ***REMOVED*** 提取新观点（如果有）
            new_opinions = self._extract_new_opinions(answer_text, memories)
            
            ***REMOVED*** 更新记忆的置信度（如果有观点记忆）
            updated_memories = self._update_confidence(memories, answer_text)
            
            ***REMOVED*** 构建 based_on 事实列表（参考 Hindsight ReflectFact）
            based_on = self._build_based_on_facts(
                world_facts + experience_facts + opinion_facts + observation_facts
            )
            
            return {
                "answer": answer_text.strip(),
                "based_on": based_on,
                "updated_memories": updated_memories,
                "new_opinions": new_opinions,
            }
            
        except Exception as e:
            logger.error(f"Error in reflect operation: {e}", exc_info=True)
            return {
                "answer": "",
                "based_on": [],
                "updated_memories": memories,
                "new_opinions": [],
            }
    
    def _build_reflect_prompt(
        self,
        query: str,
        world_facts: List[Memory],
        experience_facts: List[Memory],
        opinion_facts: List[Memory],
        observation_facts: List[Memory],
        episodic_memories: List[Memory],
        semantic_memories: List[Memory],
        user_profile_memories: List[Memory],
        agent_disposition: Optional[Dict[str, Any]] = None,
        agent_background: Optional[str] = None,
        context: str = "",
    ) -> str:
        """
        构建反思提示词
        
        综合考虑认知属性（Hindsight 类型）和抽象层级（MemMachine 维度）
        """
        
        ***REMOVED*** 格式化事实
        def format_facts(facts: List[Memory], fact_type: str) -> str:
            if not facts:
                return f"无{fact_type}相关记忆"
            text = f"\n【{fact_type}事实】\n"
            for i, fact in enumerate(facts[:10], 1):  ***REMOVED*** 限制数量
                text += f"{i}. {fact.content}\n"
                if fact.context:
                    text += f"   上下文: {fact.context}\n"
            return text
        
        world_text = format_facts(world_facts, "世界")
        experience_text = format_facts(experience_facts, "经历")
        opinion_text = format_facts(opinion_facts, "观点")
        observation_text = format_facts(observation_facts, "观察")
        
        ***REMOVED*** 添加抽象层级信息（如果相关记忆较多，提供优化建议）
        abstraction_hint = ""
        if len(episodic_memories) > len(semantic_memories) * 2:
            abstraction_hint = "\n提示：本次查询主要涉及具体事件记忆（episodic），建议优先考虑时间序列和因果关系。"
        elif len(semantic_memories) > len(episodic_memories) * 2:
            abstraction_hint = "\n提示：本次查询主要涉及抽象概念记忆（semantic），建议优先考虑概念关联和知识结构。"
        
        if user_profile_memories:
            abstraction_hint += f"\n提示：包含 {len(user_profile_memories)} 条用户画像记忆，请考虑个性化因素。"
        
        ***REMOVED*** Agent 配置
        disposition_text = ""
        if agent_disposition:
            skepticism = agent_disposition.get("skepticism", 3)
            literalism = agent_disposition.get("literalism", 3)
            empathy = agent_disposition.get("empathy", 3)
            disposition_text = f"""
Agent 性格配置：
- 怀疑度 (Skepticism): {skepticism}/5
- 字面度 (Literalism): {literalism}/5
- 同理心 (Empathy): {empathy}/5
"""
        
        background_text = f"\nAgent 背景: {agent_background}\n" if agent_background else ""
        
        prompt = f"""你是一个智能 Agent，需要基于记忆库中的事实回答问题，并形成新的观点。

{background_text}{disposition_text}
任务上下文: {context}
{abstraction_hint}

{world_text}
{experience_text}
{opinion_text}
{observation_text}

问题: {query}

请基于以上事实回答问题，并：
1. 提供清晰、准确的答案
2. 如果形成了新的观点或信念，请在答案末尾用【新观点】标记
3. 考虑 Agent 的性格配置，调整回答风格
4. 注意记忆的抽象层级：具体事件（episodic）用于时间序列推理，抽象概念（semantic）用于概念推理

答案："""
        
        return prompt
    
    def _build_reflect_system_message(self, agent_disposition: Optional[Dict[str, Any]] = None) -> str:
        """构建反思的系统消息"""
        base_message = "你是一个专业的推理助手，擅长基于事实进行逻辑推理和观点形成。"
        
        if agent_disposition:
            skepticism = agent_disposition.get("skepticism", 3)
            literalism = agent_disposition.get("literalism", 3)
            empathy = agent_disposition.get("empathy", 3)
            
            ***REMOVED*** 根据性格调整系统消息
            if skepticism >= 4:
                base_message += "你对信息持怀疑态度，会仔细验证事实。"
            if literalism >= 4:
                base_message += "你倾向于字面理解，注重精确性。"
            if empathy >= 4:
                base_message += "你具有同理心，会考虑情感和人际关系。"
        
        return base_message
    
    def _extract_new_opinions(self, answer_text: str, original_memories: List[Memory]) -> List[Memory]:
        """从答案中提取新观点"""
        new_opinions = []
        
        ***REMOVED*** 检查是否包含【新观点】标记
        if "【新观点】" in answer_text or "[新观点]" in answer_text:
            try:
                ***REMOVED*** 提取新观点部分
                if "【新观点】" in answer_text:
                    opinion_text = answer_text.split("【新观点】")[-1].strip()
                else:
                    opinion_text = answer_text.split("[新观点]")[-1].strip()
                
                if opinion_text:
                    ***REMOVED*** 创建新观点记忆
                    opinion_memory = Memory(
                        id=f"opinion_{datetime.now().timestamp()}",
                        content=opinion_text,
                        timestamp=datetime.now(),
                        memory_type=MemoryType.OPINION,
                        context="通过反思形成的新观点",
                        metadata={"confidence": 0.7, "source": "reflect"},
                    )
                    new_opinions.append(opinion_memory)
            except Exception as e:
                logger.warning(f"Failed to extract new opinions: {e}")
        
        return new_opinions
    
    def _update_confidence(self, memories: List[Memory], answer_text: str) -> List[Memory]:
        """更新记忆的置信度"""
        ***REMOVED*** 简单实现：如果有新证据支持，可以更新置信度
        ***REMOVED*** 实际应该使用更复杂的逻辑
        updated = []
        for memory in memories:
            if memory.memory_type == MemoryType.OPINION:
                ***REMOVED*** 如果答案中提到了这个观点，可以稍微提高置信度
                if memory.content[:50] in answer_text:
                    if "confidence" not in memory.metadata:
                        memory.metadata["confidence"] = 0.7
                    else:
                        memory.metadata["confidence"] = min(1.0, memory.metadata["confidence"] + 0.1)
                updated.append(memory)
            else:
                updated.append(memory)
        
        return updated
    
    def _get_max_facts_by_budget(self, budget: str) -> int:
        """
        根据预算级别返回每个类型最多使用的事实数量（参考 Hindsight）
        
        Args:
            budget: 预算级别（low/mid/high）
            
        Returns:
            每个类型最多使用的事实数量
        """
        budget_map = {
            "low": 5,   ***REMOVED*** 低预算：每个类型最多5个事实
            "mid": 10,  ***REMOVED*** 中等预算：每个类型最多10个事实
            "high": 20, ***REMOVED*** 高预算：每个类型最多20个事实
        }
        return budget_map.get(budget.lower(), 10)
    
    def _get_max_tokens_by_budget(self, budget: str) -> int:
        """
        根据预算级别返回最大 token 数（参考 Hindsight）
        
        Args:
            budget: 预算级别（low/mid/high）
            
        Returns:
            最大 token 数
        """
        budget_map = {
            "low": 512,   ***REMOVED*** 低预算：512 tokens
            "mid": 1024,  ***REMOVED*** 中等预算：1024 tokens
            "high": 2048, ***REMOVED*** 高预算：2048 tokens
        }
        return budget_map.get(budget.lower(), 1024)
    
    def _filter_by_abstraction_level(self, memories: List[Memory], level: str) -> List[Memory]:
        """
        按抽象层级过滤记忆（MemMachine 维度）
        
        Args:
            memories: 记忆列表
            level: 抽象层级（"episodic" | "semantic" | "user_profile"）
            
        Returns:
            过滤后的记忆列表
        """
        if not memories:
            return []
        
        filtered = []
        for memory in memories:
            if not memory.metadata:
                continue
            
            ***REMOVED*** 检查 abstraction_level
            memory_level = memory.metadata.get("abstraction_level")
            if memory_level == level:
                filtered.append(memory)
            ***REMOVED*** 特殊处理：user_profile 标记
            elif level == "user_profile" and memory.metadata.get("is_user_profile", False):
                filtered.append(memory)
        
        return filtered
    
    def _build_based_on_facts(self, facts: List[Memory]) -> List[Dict[str, Any]]:
        """
        构建基于的事实列表（参考 Hindsight ReflectFact）
        
        Args:
            facts: 事实记忆列表
            
        Returns:
            事实字典列表，每个包含：
            - id: 记忆ID
            - text: 事实文本
            - type: 记忆类型
            - context: 上下文
            - occurred_start: 发生开始时间
            - occurred_end: 发生结束时间
        """
        based_on = []
        for fact in facts:
            fact_dict = {
                "id": fact.id,
                "text": fact.content,
                "type": fact.memory_type.value if fact.memory_type else None,
                "context": fact.context,
            }
            
            ***REMOVED*** 从 metadata 中提取时间信息（如果有）
            if fact.metadata:
                if "occurred_start" in fact.metadata:
                    fact_dict["occurred_start"] = fact.metadata["occurred_start"]
                if "occurred_end" in fact.metadata:
                    fact_dict["occurred_end"] = fact.metadata["occurred_end"]
            
            based_on.append(fact_dict)
        
        return based_on
