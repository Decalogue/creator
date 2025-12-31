"""
操作接口适配器

实现 UniMem 的 Retain/Recall/Reflect 三大操作
参考架构：Hindsight（三操作范式 + 四大逻辑网络）
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import abstractmethod

***REMOVED*** 添加 Hindsight 到路径（用于参考实现）
hindsight_path = Path(__file__).parent.parent.parent.parent / "hindsight"
if str(hindsight_path) not in sys.path:
    sys.path.insert(0, str(hindsight_path))

try:
    ***REMOVED*** 参考 Hindsight 的实现思路
    ***REMOVED*** from hindsight import HindsightClient
    pass
except ImportError:
    pass

from .base import BaseAdapter
from ..types import Experience, Memory, Task, Context, MemoryType
from ..chat import ark_deepseek_v3_2
import logging

logger = logging.getLogger(__name__)


class OperationAdapter(BaseAdapter):
    """
    操作接口适配器
    
    功能需求：实现 Retain/Recall/Reflect 三大操作
    参考架构：HindSight（三操作范式）
    """
    
    def _do_initialize(self):
        """初始化操作适配器"""
        ***REMOVED*** 参考 Hindsight 的初始化思路
        ***REMOVED*** 这里可以集成 Hindsight 的客户端，但接口按照 UniMem 的需求定义
        logger.info("Operation adapter initialized (using Hindsight principles)")
    
    def retain(self, experience: Experience, context: Context) -> Memory:
        """
        存储新记忆（RETAIN 操作）
        
        参考 Hindsight 的 retain 思路：
        - 将经验转换为结构化的记忆单元（叙事性事实提取）
        - 提取事实、生成嵌入、实体解析、构建链接
        - 存储到记忆库中
        
        但接口按照 UniMem 的需求定义
        
        Args:
            experience: 经验对象
            context: 上下文信息
            
        Returns:
            创建的 Memory 对象
        """
        logger.debug(f"RETAIN: Storing experience: {experience.content[:50]}...")
        
        ***REMOVED*** 参考 Hindsight 的 retain 逻辑：
        ***REMOVED*** 1. 事实提取（what, when, where, who, why）
        ***REMOVED*** 2. 生成嵌入
        ***REMOVED*** 3. 实体解析
        ***REMOVED*** 4. 构建链接（时间、语义、实体、因果）
        
        ***REMOVED*** 创建基础 Memory 对象
        ***REMOVED*** 注意：实际的记忆类型分类和结构化处理会在 core.py 的 retain 方法中完成
        ***REMOVED*** 这里只返回基础结构
        memory = Memory(
            id=f"mem_{datetime.now().timestamp()}",
            content=experience.content,
            timestamp=experience.timestamp,
            context=experience.context or context.metadata.get("context", ""),
            metadata=experience.metadata.copy() if experience.metadata else {},
        )
        
        return memory
    
    def recall(self, query: str, context: Context, top_k: int = 10, memory_types: Optional[List[MemoryType]] = None) -> List[Memory]:
        """
        检索相关记忆（RECALL 操作）
        
        参考 Hindsight 的 recall 思路：
        - 四路并行检索：语义、BM25、图、时间
        - RRF 融合和重排序
        - Token 预算过滤
        
        但接口按照 UniMem 的需求定义
        
        Args:
            query: 查询字符串
            context: 上下文信息
            top_k: 返回结果数量
            memory_types: 记忆类型过滤（可选，支持 Hindsight 的四大类型）
            
        Returns:
            检索到的记忆列表
        """
        logger.debug(f"RECALL: Query: {query[:50]}...")
        
        ***REMOVED*** 参考 Hindsight 的 recall 逻辑：
        ***REMOVED*** 1. 四路并行检索（语义、BM25、图、时间）
        ***REMOVED*** 2. RRF 融合
        ***REMOVED*** 3. 重排序
        ***REMOVED*** 4. Token 预算过滤
        
        ***REMOVED*** 注意：实际的检索逻辑在 retrieval_engine.py 中实现
        ***REMOVED*** 这里只是接口定义，返回空列表表示需要由上层调用检索引擎
        
        ***REMOVED*** 临时实现：返回空列表，实际检索由 core.py 调用 retrieval_engine
        return []
    
    def reflect(
        self, 
        memories: List[Memory], 
        task: Task,
        agent_disposition: Optional[Dict[str, Any]] = None,
        agent_background: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        更新和优化记忆（REFLECT 操作）
        
        参考 Hindsight 的 reflect 思路（CARA: Coherent Adaptive Reasoning Agents）：
        - 基于检索到的事实（experience, world, opinion）进行推理
        - 使用 Agent Profile（Disposition + Background）进行个性化生成
        - 生成答案并更新信念（Opinion）
        
        但接口按照 UniMem 的需求定义
        
        Args:
            memories: 要反思的记忆列表
            task: 任务上下文
            agent_disposition: Agent 性格配置（Skepticism, Literalism, Empathy）
            agent_background: Agent 背景信息
            
        Returns:
            包含答案和更新后记忆的字典：
            {
                "answer": str,  ***REMOVED*** 生成的答案
                "updated_memories": List[Memory],  ***REMOVED*** 更新后的记忆
                "new_opinions": List[Memory],  ***REMOVED*** 新形成的观点
            }
        """
        logger.debug(f"REFLECT: Reflecting on {len(memories)} memories for task: {task.description[:50]}...")
        
        ***REMOVED*** 参考 Hindsight 的 reflect 逻辑（CARA）：
        ***REMOVED*** 1. 按类型分组记忆（world, experience, opinion, observation）
        ***REMOVED*** 2. 构建上下文（包含事实和 Agent Profile）
        ***REMOVED*** 3. 使用 LLM 生成答案（带 Disposition Conditioning）
        ***REMOVED*** 4. 提取新观点并更新置信度
        
        ***REMOVED*** 按 Hindsight 类型分组记忆
        world_facts = [m for m in memories if m.memory_type == MemoryType.WORLD]
        experience_facts = [m for m in memories if m.memory_type == MemoryType.EXPERIENCE]
        opinion_facts = [m for m in memories if m.memory_type == MemoryType.OPINION]
        observation_facts = [m for m in memories if m.memory_type == MemoryType.OBSERVATION]
        
        logger.debug(f"Memory breakdown: World={len(world_facts)}, Experience={len(experience_facts)}, "
                    f"Opinion={len(opinion_facts)}, Observation={len(observation_facts)}")
        
        ***REMOVED*** 构建反思提示词
        prompt = self._build_reflect_prompt(
            query=task.description,
            world_facts=world_facts,
            experience_facts=experience_facts,
            opinion_facts=opinion_facts,
            observation_facts=observation_facts,
            agent_disposition=agent_disposition,
            agent_background=agent_background,
            context=task.context,
        )
        
        ***REMOVED*** 调用 LLM 生成答案
        try:
            system_message = self._build_reflect_system_message(agent_disposition)
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            _, answer_text = ark_deepseek_v3_2(messages, max_new_tokens=1024)
            
            ***REMOVED*** 提取新观点（如果有）
            new_opinions = self._extract_new_opinions(answer_text, memories)
            
            ***REMOVED*** 更新记忆的置信度（如果有观点记忆）
            updated_memories = self._update_confidence(memories, answer_text)
            
            return {
                "answer": answer_text.strip(),
                "updated_memories": updated_memories,
                "new_opinions": new_opinions,
            }
            
        except Exception as e:
            logger.error(f"Error in reflect operation: {e}")
            return {
                "answer": "",
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
        agent_disposition: Optional[Dict[str, Any]] = None,
        agent_background: Optional[str] = None,
        context: str = "",
    ) -> str:
        """构建反思提示词"""
        
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

{world_text}
{experience_text}
{opinion_text}
{observation_text}

问题: {query}

请基于以上事实回答问题，并：
1. 提供清晰、准确的答案
2. 如果形成了新的观点或信念，请在答案末尾用【新观点】标记
3. 考虑 Agent 的性格配置，调整回答风格

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
