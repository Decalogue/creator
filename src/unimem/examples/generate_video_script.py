"""
短视频剧本生成示例

演示如何使用 VideoAdapter 和 UniMem 生成短视频剧本，
并支持通过用户输入不断优化记忆与剧本。

功能：
1. 创建 Word 模板供用户填写
2. 解析用户填写的 Word 文档
3. 生成短视频剧本
4. 支持用户反馈优化
5. 将优化后的记忆和剧本存储到 UniMem
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem import UniMem
from unimem.adapters import VideoAdapter
from unimem.memory_types import Experience, Context, Task, MemoryType
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoScriptGenerator:
    """短视频剧本生成器"""
    
    def __init__(
        self,
        unimem_config: Optional[Dict[str, Any]] = None,
        skip_unimem: bool = False,
        use_service: bool = True,
        service_url: Optional[str] = None
    ):
        """
        初始化生成器
        
        Args:
            unimem_config: UniMem 配置，如果为 None 则使用最小配置（仅在 use_service=False 时使用）
            skip_unimem: 如果为 True，跳过 UniMem 初始化（仅用于创建模板等简单操作）
            use_service: 如果为 True，使用 UniMem HTTP 服务；如果为 False，使用本地实例
            service_url: UniMem 服务 URL（默认: http://localhost:9622）
        """
        self.unimem = None
        self.use_service = use_service and not skip_unimem
        
        if not skip_unimem:
            if self.use_service:
                # 使用 HTTP 服务
                try:
                    from ..service.client import UniMemServiceClient
                    service_url = service_url or os.getenv("UNIMEM_SERVICE_URL", "http://localhost:9622")
                    self.unimem = UniMemServiceClient(base_url=service_url)
                    logger.info(f"VideoScriptGenerator initialized with UniMem HTTP service: {service_url}")
                except Exception as e:
                    logger.error(f"Failed to connect to UniMem service: {e}")
                    logger.warning("Falling back to local instance...")
                    self.use_service = False
            
            if not self.use_service:
                # 使用本地实例
                try:
                    if unimem_config:
                        self.unimem = UniMem(config=unimem_config)
                    else:
                        # 使用生产配置（连接到 Redis、Neo4j、Qdrant）
                        production_config = self._get_production_unimem_config()
                        self.unimem = UniMem(config=production_config)
                    logger.info("VideoScriptGenerator initialized with UniMem local instance")
                except Exception as e:
                    logger.warning(f"UniMem initialization failed: {e}, using standalone mode")
                    self.unimem = None
        
        # 初始化 VideoAdapter（传入 UniMem 实例以启用深度集成）
        self.adapter = VideoAdapter(
            config={},
            unimem_instance=self.unimem
        )
        
        if skip_unimem or self.unimem is None:
            logger.info("VideoScriptGenerator initialized (standalone mode)")
        elif self.use_service:
            logger.info("VideoScriptGenerator initialized with UniMem HTTP service")
        else:
            logger.info("VideoScriptGenerator initialized with UniMem local instance")
    
    @staticmethod
    def _get_production_unimem_config() -> Dict[str, Any]:
        """
        获取 UniMem 生产配置（连接到 Redis、Neo4j、Qdrant）
        
        这个配置使用外部服务，提供完整的持久化和检索功能
        """
        return {
            # 图数据库配置（使用 Neo4j）
            "graph": {
                "backend": "neo4j",
                "workspace": "./unimem_workspace",
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "embedding_model": "text-embedding-3-small",
                "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7680"),
                "neo4j_user": os.getenv("NEO4J_USER", "neo4j"),
                "neo4j_password": os.getenv("NEO4J_PASSWORD", "seeme_db"),
                "neo4j_database": os.getenv("NEO4J_DATABASE", "neo4j"),
            },
            # 向量数据库配置（使用 Qdrant）
            "vector": {
                "backend": "qdrant"
            },
            # 存储配置（使用 Redis）
            "storage": {
                "foa_backend": "redis",
                "da_backend": "redis",
                "ltm_backend": "neo4j",
            },
            # 操作配置
            "operation": {
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "llm_func": "ark_deepseek_v3_2",
            },
            # 网络配置（使用本地模型和 Qdrant）
            "network": {
                "model_name": "all-MiniLM-L6-v2",
                "local_model_path": "/root/data/AI/pretrain/all-MiniLM-L6-v2",
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "llm_func": "ark_deepseek_v3_2",
                "qdrant_host": os.getenv("QDRANT_HOST", "localhost"),
                "qdrant_port": int(os.getenv("QDRANT_PORT", "6333")),
                "collection_name": "unimem_memories",
            },
            # 检索配置
            "retrieval": {
                "top_k": 10,
                "rrf_k": 60,
            },
            # 更新配置
            "update": {
                "sleep_interval": 3600,
            },
        }
    
    @staticmethod
    def _get_minimal_unimem_config() -> Dict[str, Any]:
        """
        获取 UniMem 最小配置（降级模式）
        
        这个配置允许 UniMem 运行，即使外部服务不可用也会优雅降级
        """
        return {
            # 图数据库配置（使用 networkx 作为降级选项）
            "graph": {
                "backend": "networkx",  # 即使不可用，也会优雅降级
                "workspace": "./unimem_workspace",
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "embedding_model": "text-embedding-3-small",
            },
            # 向量数据库配置（即使不可用，也会优雅降级）
            "vector": {
                "backend": "qdrant"  # 即使不可用，也会优雅降级
            },
            # 存储配置（使用内存存储）
            "storage": {
                "foa_backend": "memory",
                "da_backend": "memory",
                "ltm_backend": "memory",
            },
            # 操作配置
            "operation": {
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "llm_func": "ark_deepseek_v3_2",
            },
            # 网络配置（使用本地模型）
            "network": {
                "model_name": "all-MiniLM-L6-v2",
                "local_model_path": "/root/data/AI/pretrain/all-MiniLM-L6-v2",
                "llm_provider": "ark_deepseek",
                "llm_model": "deepseek-v3-2",
                "llm_func": "ark_deepseek_v3_2",
                "qdrant_host": "localhost",
                "qdrant_port": 6333,
                "collection_name": "unimem_memories",
            },
            # 检索配置
            "retrieval": {
                "top_k": 10,
                "rrf_k": 60,
            },
            # 更新配置
            "update": {
                "sleep_interval": 3600,
            },
        }
        
        # 初始化 VideoAdapter（传入 UniMem 实例以启用深度集成）
        self.adapter = VideoAdapter(
            config={},
            unimem_instance=self.unimem
        )
        
        if skip_unimem:
            logger.info("VideoScriptGenerator initialized (UniMem skipped)")
        else:
            logger.info("VideoScriptGenerator initialized with UniMem integration")
    
    def create_template(self, output_path: str) -> str:
        """
        创建 Word 模板文件
        
        Args:
            output_path: 模板文件保存路径
            
        Returns:
            模板文件路径
        """
        logger.info(f"Creating Word template at: {output_path}")
        self.adapter.create_word_template(output_path)
        logger.info(f"Template created successfully: {output_path}")
        return output_path
    
    def parse_word_document(self, doc_path: str) -> Dict[str, Any]:
        """
        解析 Word 文档
        
        Args:
            doc_path: Word 文档路径
            
        Returns:
            解析结果字典
        """
        logger.info(f"Parsing Word document: {doc_path}")
        result = self.adapter.parse_word_document(doc_path)
        logger.info(f"Parsed successfully: video_type={result.get('video_type')}, "
                   f"platform={result.get('platform')}, "
                   f"duration={result.get('duration_seconds')}s")
        return result
    
    def generate_script(self, doc_data: Dict[str, Any], use_unimem: bool = None) -> Dict[str, Any]:
        """
        生成短视频剧本
        
        Args:
            doc_data: 从 Word 文档解析的数据
            use_unimem: 是否使用 UniMem（None 时自动判断：如果有 UniMem 实例则使用，否则不使用）
            
        Returns:
            生成的剧本字典
        """
        logger.info("Generating video script...")
        
        # 自动判断是否使用 UniMem
        if use_unimem is None:
            use_unimem = self.unimem is not None
        
        script = self.adapter.generate_video_script(
            task_memories=doc_data.get("task_memories", []),
            modification_memories=doc_data.get("modification_memories", []),
            general_memories=doc_data.get("general_memories", []),
            user_preferences=doc_data.get("user_preferences", {}),
            product_info=doc_data.get("product_info", {}),
            shot_materials=doc_data.get("shot_materials", []),
            video_type=doc_data.get("video_type", "ecommerce"),
            duration_seconds=doc_data.get("duration_seconds", 60),
            platform=doc_data.get("platform", "douyin"),
            use_unimem_retrieval=use_unimem,  # 根据是否有 UniMem 实例决定
            store_to_unimem=use_unimem  # 根据是否有 UniMem 实例决定
        )
        
        if script:
            logger.info(f"Script generated successfully: {len(script.get('segments', []))} segments")
            if "unimem_memory_id" in script:
                logger.info(f"Script stored to UniMem: memory_id={script['unimem_memory_id']}")
        else:
            logger.warning("Script generation failed")
        
        return script
    
    def extract_modification_feedback(
        self, 
        user_input: str, 
        existing_modifications: Optional[list] = None
    ) -> list:
        """
        从用户输入中提取修改需求
        
        支持多次对话累积：如果提供了已有的修改需求，会避免重复提取。
        
        Args:
            user_input: 用户输入的反馈文本
            existing_modifications: 已有的修改需求列表（可选），用于避免重复提取
            
        Returns:
            修改需求列表（只包含新增的）
        """
        logger.info("Extracting modification feedback from user input...")
        modifications = self.adapter.extract_modification_memories_from_conversation(
            user_input, 
            existing_modifications=existing_modifications
        )
        logger.info(f"Extracted {len(modifications)} new modification requirements")
        return modifications
    
    def optimize_and_regenerate(
        self,
        original_doc_data: Dict[str, Any],
        modification_feedback: list,
        original_script: Optional[Dict[str, Any]] = None,
        accumulated_modifications: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        基于用户反馈优化并重新生成剧本
        
        支持多次对话累积修改需求：每次对话的修改需求会被累积到已有的修改需求列表中。
        
        增强功能：
        1. 在优化前检索相关的历史反馈和成功模式（RECALL增强）
        2. 提取结构化的修改需求（优先级、类型、影响范围）
        3. 优化后评估改进效果，形成反馈循环
        
        Args:
            original_doc_data: 原始文档数据
            modification_feedback: 本次用户反馈的修改需求（新增的）
            original_script: 原始剧本（可选）
            accumulated_modifications: 已累积的修改需求列表（可选），如果提供，会将新的修改需求追加到该列表中
            
        Returns:
            优化后的剧本（包含优化效果评估）
        """
        logger.info("Optimizing script based on user feedback...")
        
        # ========== 增强1：在优化前检索相关的历史反馈和成功模式 ==========
        if self.unimem and original_script:
            video_type = original_doc_data.get("video_type", "ecommerce")
            platform = original_doc_data.get("platform", "douyin")
            
            # 检索相关的历史反馈和成功模式
            feedback_query = f"{video_type} {platform} 用户反馈 修改需求 优化经验"
            try:
                if hasattr(self.unimem, 'base_url'):
                    feedback_results = self.unimem.recall(
                        query=feedback_query,
                        memory_type=MemoryType.EXPERIENCE,  # 优先检索经验类型
                        top_k=5
                    )
                else:
                    feedback_results = self.unimem.recall(
                        query=feedback_query,
                        context=Context(metadata={"video_type": video_type, "platform": platform}),
                        memory_type=MemoryType.EXPERIENCE,
                        top_k=5
                    )
                
                if feedback_results:
                    logger.info(f"Retrieved {len(feedback_results)} relevant feedback memories for optimization")
                    # 将历史反馈经验加入到修改需求中（作为参考，但不强制执行）
                    historical_feedback = [
                        f"[历史经验参考] {r.memory.content[:100]}"
                        for r in feedback_results[:3]
                        if r.memory and r.score > 0.6  # 只使用相似度较高的
                    ]
                    if historical_feedback:
                        modification_feedback = historical_feedback + modification_feedback
                        logger.info(f"Added {len(historical_feedback)} historical feedback references")
            except Exception as e:
                logger.warning(f"Failed to retrieve historical feedback: {e}")
        
        # ========== 增强2：提取结构化的修改需求 ==========
        structured_feedback = self._extract_structured_feedback(modification_feedback)
        if structured_feedback:
            logger.info(f"Extracted structured feedback: {len(structured_feedback.get('high_priority', []))} high, "
                       f"{len(structured_feedback.get('medium_priority', []))} medium, "
                       f"{len(structured_feedback.get('low_priority', []))} low")
            # 按照优先级排序修改需求
            modification_feedback = (
                structured_feedback.get("high_priority", []) +
                structured_feedback.get("medium_priority", []) +
                structured_feedback.get("low_priority", [])
            )
        
        # 累积修改需求：将本次的修改需求添加到已有的修改需求中
        if accumulated_modifications is not None:
            # 如果提供了已累积的修改需求，使用它并追加新的
            all_modifications = accumulated_modifications + modification_feedback
        else:
            # 否则从原始文档数据中获取已有的修改需求，并追加新的
            all_modifications = (
                original_doc_data.get("modification_memories", []) + modification_feedback
            )
        
        # 将累积的修改需求添加到文档数据中
        optimized_doc_data = original_doc_data.copy()
        optimized_doc_data["modification_memories"] = all_modifications
        
        logger.info(f"Total accumulated modifications: {len(all_modifications)} "
                   f"(existing: {len(all_modifications) - len(modification_feedback)}, "
                   f"new: {len(modification_feedback)})")
        
        # 如果提供了原始剧本，使用优化方法
        if original_script:
            # 传递所有累积的修改需求作为反馈，并包含结构化信息
            feedback_text = "\n".join(all_modifications)
            if structured_feedback:
                feedback_text = f"[优先级排序的修改需求]\n{feedback_text}"
            
            optimized_script = self.adapter.optimize_script_for_editing(
                script_data=original_script,
                feedback=feedback_text
            )
            
            # 改进：将优化后的脚本存储到UniMem（如果UniMem可用）
            if optimized_script and self.unimem and self.adapter:
                try:
                    # 获取原始脚本的memory_id（如果有）
                    original_script_memory_id = original_script.get("unimem_memory_id")
                    
                    # 存储优化后的脚本到UniMem
                    video_type = original_doc_data.get("video_type", "ecommerce")
                    platform = original_doc_data.get("platform", "douyin")
                    task_memories = original_doc_data.get("task_memories", [])
                    
                    # 构建包含反馈信息的decision_trace
                    optimized_decision_trace = {
                        "inputs": task_memories[:5] + all_modifications[:3],  # 任务记忆 + 反馈
                        "rules_applied": [
                            f"{platform}平台规则",
                            f"{video_type}类型脚本规范",
                            "用户反馈优先原则",
                            "脚本优化规范"
                        ],
                        "exceptions": [],
                        "approvals": ["用户反馈确认"],
                        "timestamp": datetime.now().isoformat(),
                        "operation_id": f"optimize_{original_script_memory_id}_{datetime.now().timestamp()}" if original_script_memory_id else f"optimize_{datetime.now().timestamp()}",
                        "based_on_script": original_script_memory_id  # 记录基于哪个脚本优化
                    }
                    
                    # 创建Experience和Context
                    from unimem.memory_types import Experience, Context
                    experience = Experience(
                        content=f"优化后的脚本（基于用户反馈）：{optimized_script.get('summary', {}).get('title', '')}",
                        timestamp=datetime.now()
                    )
                    
                    context = Context(
                        metadata={
                            "source": "script_optimization",
                            "task_description": f"基于用户反馈优化{video_type}类型脚本",
                            "video_type": video_type,
                            "platform": platform,
                            "optimization_feedback": all_modifications[:5],
                            "original_script_id": original_script_memory_id,
                            "reasoning": f"基于{len(all_modifications)}条用户反馈优化脚本，提升用户体验和转化率",
                            "decision_trace": optimized_decision_trace
                        }
                    )
                    
                    # 存储优化后的脚本
                    optimized_memory = self.unimem.retain(experience, context)
                    optimized_script["unimem_memory_id"] = optimized_memory.id
                    logger.info(f"Stored optimized script to UniMem: memory_id={optimized_memory.id}")
                    
                    # 建立与原始脚本的关系
                    if original_script_memory_id:
                        optimized_memory.links.add(original_script_memory_id)
                        if hasattr(self.unimem, 'storage') and hasattr(self.unimem.storage, 'update_memory'):
                            self.unimem.storage.update_memory(optimized_memory)
                    
                    # 为优化后的脚本创建DecisionEvent
                    if optimized_memory.decision_trace:
                        from unimem.neo4j import create_decision_event
                        if create_decision_event(
                            memory_id=optimized_memory.id,
                            decision_trace=optimized_memory.decision_trace,
                            reasoning=optimized_memory.reasoning or context.metadata.get("reasoning", ""),
                            related_entity_ids=optimized_memory.entities if optimized_memory.entities else []
                        ):
                            logger.info(f"Created DecisionEvent for optimized script memory {optimized_memory.id}")
                except Exception as e:
                    logger.warning(f"Failed to store optimized script to UniMem: {e}")
        else:
            # 否则重新生成
            optimized_script = self.generate_script(optimized_doc_data)
        
        # ========== 增强3：优化后评估改进效果 ==========
        if optimized_script and original_script:
            improvement_assessment = self._assess_improvement(original_script, optimized_script, all_modifications)
            if improvement_assessment:
                optimized_script["improvement_assessment"] = improvement_assessment
                logger.info(f"Improvement assessment: {improvement_assessment.get('overall_score', 'N/A')}/10")
                # 如果改进效果显著，存储为成功经验
                if improvement_assessment.get("overall_score", 0) >= 7:
                    self._store_optimization_experience(
                        all_modifications, original_script, optimized_script, improvement_assessment
                    )
        
        logger.info("Script optimized successfully")
        return optimized_script
    
    def store_feedback_to_unimem(
        self,
        feedback: str,
        script_memory_id: Optional[str] = None
    ) -> Optional[str]:
        """
        将用户反馈存储到 UniMem
        
        Args:
            feedback: 用户反馈文本
            script_memory_id: 相关剧本的 memory_id（可选）
            
        Returns:
            存储的记忆 ID
        """
        try:
            experience = Experience(
                content=f"用户反馈：{feedback}",
                timestamp=datetime.now()
            )
            
            # 改进1：从关联的脚本Memory继承decision_trace
            inherited_decision_trace = None
            if script_memory_id:
                try:
                    from unimem.neo4j import get_memory
                    script_memory = get_memory(script_memory_id)
                    if script_memory and script_memory.decision_trace:
                        # 继承脚本Memory的decision_trace，但更新inputs和operation_id
                        inherited_decision_trace = script_memory.decision_trace.copy()
                        inherited_decision_trace["inputs"] = [feedback]  # 更新为当前反馈
                        inherited_decision_trace["operation_id"] = f"feedback_{script_memory_id}_{datetime.now().timestamp()}"
                        inherited_decision_trace["timestamp"] = datetime.now().isoformat()
                        # 添加反馈相关的规则
                        if "rules_applied" in inherited_decision_trace:
                            inherited_decision_trace["rules_applied"].extend([
                                "用户反馈优先原则",
                                "脚本优化规范",
                                "用户体验改进要求"
                            ])
                        else:
                            inherited_decision_trace["rules_applied"] = [
                                "用户反馈优先原则",
                                "脚本优化规范",
                                "用户体验改进要求"
                            ]
                        logger.debug(f"Inherited decision_trace from script memory {script_memory_id}")
                except Exception as e:
                    logger.warning(f"Failed to inherit decision_trace from script memory {script_memory_id}: {e}")
            
            # 如果没有继承到decision_trace，创建新的
            if not inherited_decision_trace:
                inherited_decision_trace = {
                    "inputs": [feedback],
                    "rules_applied": [
                        "用户反馈优先原则",
                        "脚本优化规范",
                        "用户体验改进要求"
                    ],
                    "exceptions": [],
                    "approvals": ["用户确认"],
                    "timestamp": datetime.now().isoformat(),
                    "operation_id": f"feedback_{script_memory_id}_{datetime.now().timestamp()}" if script_memory_id else f"feedback_{datetime.now().timestamp()}",
                }
            
            context = Context(
                metadata={
                    "source": "user_feedback",  # 明确标识来源
                    "task_description": "用户对视频剧本的反馈和修改需求",
                    "feedback_type": "script_modification",
                    "related_script_id": script_memory_id,
                    # 决策痕迹（Context Graph增强）
                    "inputs": [feedback],  # 用户反馈作为输入
                    "rules": [
                        "用户反馈优先原则",
                        "脚本优化规范",
                        "用户体验改进要求"
                    ],
                    "exceptions": [],  # 可以记录特殊反馈情况
                    "approvals": ["用户确认"],  # 用户反馈本身就是一种确认
                    "reasoning": f"用户反馈要求：{feedback[:100]}，需要据此优化脚本",
                    # 使用继承或新建的decision_trace
                    "decision_trace": inherited_decision_trace
                }
            )
            
            # 在retain之前设置links，确保关系被正确建立
            # 注意：需要在retain之前通过context.metadata传递links信息
            if script_memory_id:
                if not context.metadata:
                    context.metadata = {}
                # 将脚本Memory ID添加到metadata中，retain方法会处理
                context.metadata["related_script_id"] = script_memory_id
                # 同时设置links（如果retain方法支持从metadata读取）
                if "links" not in context.metadata:
                    context.metadata["links"] = [script_memory_id]
            
            memory = self.unimem.retain(experience, context)
            logger.info(f"Feedback stored to UniMem: memory_id={memory.id}")
            
            # 建立与脚本Memory的关系（改进：建立Memory关系网络）
            if script_memory_id and memory.id:
                try:
                    # 确保links被设置
                    if not memory.links:
                        memory.links = set()
                    memory.links.add(script_memory_id)
                    # 更新Memory以建立RELATED_TO关系
                    if hasattr(self.unimem, 'storage') and hasattr(self.unimem.storage, 'update_memory'):
                        self.unimem.storage.update_memory(memory)
                        logger.debug(f"Established relationship: feedback memory {memory.id} -> script memory {script_memory_id}")
                    else:
                        logger.warning(f"Storage.update_memory not available, relationship may not be created")
                except Exception as e:
                    logger.warning(f"Failed to establish relationship with script memory {script_memory_id}: {e}")
            
            # 改进2：为反馈Memory创建DecisionEvent
            if memory.decision_trace:
                try:
                    from unimem.neo4j import create_decision_event
                    if create_decision_event(
                        memory_id=memory.id,
                        decision_trace=memory.decision_trace,
                        reasoning=memory.reasoning or context.metadata.get("reasoning", ""),
                        related_entity_ids=memory.entities if memory.entities else []
                    ):
                        logger.info(f"Created DecisionEvent for feedback memory {memory.id}")
                    else:
                        logger.warning(f"Failed to create DecisionEvent for feedback memory {memory.id}")
                except Exception as e:
                    logger.warning(f"Failed to create DecisionEvent for feedback memory {memory.id}: {e}")
            
            return memory.id
        except Exception as e:
            logger.warning(f"Failed to store feedback to UniMem: {e}")
            return None
    
    def _extract_structured_feedback(self, feedback_list: List[str]) -> Optional[Dict[str, List[str]]]:
        """
        提取结构化的修改需求（优先级、类型、影响范围）
        
        Args:
            feedback_list: 修改需求列表
            
        Returns:
            结构化反馈字典，包含按优先级分类的修改需求
        """
        if not feedback_list or not self.unimem:
            return None
        
        try:
            feedback_text = "\n".join(feedback_list)
            prompt = f"""请分析以下修改需求，按照优先级和类型进行分类：

修改需求：
{feedback_text[:1500]}

请将修改需求分类为：
1. 高优先级（必须立即执行，影响核心功能）
2. 中优先级（重要但不紧急，影响用户体验）
3. 低优先级（可选优化，锦上添花）

请以 JSON 格式返回结果：
{{
    "high_priority": ["高优先级需求1", "高优先级需求2", ...],
    "medium_priority": ["中优先级需求1", "中优先级需求2", ...],
    "low_priority": ["低优先级需求1", "低优先级需求2", ...]
}}"""
            
            from unimem.chat import ark_deepseek_v3_2
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的需求分析师，擅长对修改需求进行分类和优先级排序。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=512)
            result = self._parse_json_response(response_text)
            
            if result and ("high_priority" in result or "medium_priority" in result or "low_priority" in result):
                return {
                    "high_priority": result.get("high_priority", []),
                    "medium_priority": result.get("medium_priority", []),
                    "low_priority": result.get("low_priority", [])
                }
        except Exception as e:
            logger.warning(f"Failed to extract structured feedback: {e}")
        
        return None
    
    def _assess_improvement(
        self,
        original_script: Dict[str, Any],
        optimized_script: Dict[str, Any],
        modifications: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        评估优化后的改进效果
        
        Args:
            original_script: 原始剧本
            optimized_script: 优化后的剧本
            modifications: 修改需求列表
            
        Returns:
            改进效果评估字典
        """
        if not original_script or not optimized_script:
            return None
        
        try:
            original_segments = original_script.get("segments", [])
            optimized_segments = optimized_script.get("segments", [])
            
            prompt = f"""请评估以下剧本优化的改进效果：

修改需求：
{chr(10).join(f"- {mod}" for mod in modifications[:10])}

原始剧本段落数：{len(original_segments)}
优化后剧本段落数：{len(optimized_segments)}

请从以下维度评估改进效果（1-10分）：
1. 需求满足度：优化后的剧本是否满足所有修改需求
2. 质量提升：整体质量是否提升
3. 用户体验：是否更符合用户期望
4. 结构优化：结构是否更合理

请以 JSON 格式返回结果：
{{
    "demand_satisfaction": 8,  // 需求满足度（1-10）
    "quality_improvement": 7,  // 质量提升（1-10）
    "user_experience": 8,      // 用户体验（1-10）
    "structure_optimization": 7,  // 结构优化（1-10）
    "overall_score": 7.5,      // 综合评分（1-10）
    "key_improvements": ["改进点1", "改进点2", ...],  // 关键改进点
    "remaining_issues": ["待改进点1", "待改进点2", ...]  // 仍需改进的地方
}}"""
            
            from unimem.chat import ark_deepseek_v3_2
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的视频剧本评估专家，擅长评估剧本优化的改进效果。"
                },
                {"role": "user", "content": prompt}
            ]
            
            _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=512)
            result = self._parse_json_response(response_text)
            
            if result and "overall_score" in result:
                return result
        except Exception as e:
            logger.warning(f"Failed to assess improvement: {e}")
        
        return None
    
    def _store_optimization_experience(
        self,
        modifications: List[str],
        original_script: Dict[str, Any],
        optimized_script: Dict[str, Any],
        assessment: Dict[str, Any]
    ) -> None:
        """
        存储成功的优化经验到UniMem
        
        Args:
            modifications: 修改需求列表
            original_script: 原始剧本
            optimized_script: 优化后的剧本
            assessment: 改进效果评估
        """
        if not self.unimem:
            return
        
        try:
            experience_content = f"""成功的剧本优化经验：
修改需求：{chr(10).join(f"- {mod}" for mod in modifications[:5])}
综合评分：{assessment.get('overall_score', 'N/A')}/10
关键改进点：{', '.join(assessment.get('key_improvements', [])[:3])}"""
            
            experience = Experience(
                content=experience_content,
                timestamp=datetime.now()
            )
            
            context = Context(
                metadata={
                    "source": "optimization_experience",
                    "task_description": "视频剧本优化成功经验总结",
                    "overall_score": assessment.get("overall_score", 0),
                    "video_type": original_script.get("metadata", {}).get("video_type", "unknown"),
                    "platform": original_script.get("metadata", {}).get("platform", "unknown"),
                    "reasoning": f"优化效果显著（评分{assessment.get('overall_score', 'N/A')}），值得总结为可复用经验",
                    "decision_trace": {
                        "inputs": modifications[:5],
                        "rules_applied": ["需求优先级排序", "质量评估标准"],
                        "exceptions": [],
                        "approvals": ["系统评估确认"],
                        "timestamp": datetime.now().isoformat(),
                    }
                }
            )
            
            self.unimem.retain(experience, context)
            logger.info(f"Stored successful optimization experience (score: {assessment.get('overall_score', 'N/A')})")
        except Exception as e:
            logger.warning(f"Failed to store optimization experience: {e}")
    
    def _parse_json_response(self, text: str) -> Optional[Dict[str, Any]]:
        """解析JSON响应"""
        import json
        import re
        
        try:
            # 尝试直接解析
            return json.loads(text)
        except json.JSONDecodeError:
            # 尝试提取JSON代码块
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    pass
        return None
    
    def reflect_on_script_creation(
        self,
        script_memory_ids: List[str],
        video_type: str,
        platform: str,
        iteration_count: int = 0
    ) -> Optional[List[str]]:
        """
        对剧本创作过程进行 REFLECT 操作，总结成功模式和经验
        
        在以下场景触发：
        1. 多次优化后（3次以上）
        2. 用户满意度高时
        3. 定期批量优化
        
        Args:
            script_memory_ids: 相关剧本的记忆 ID 列表
            video_type: 视频类型
            platform: 平台类型
            iteration_count: 优化迭代次数
            
        Returns:
            演化后的记忆 ID 列表，如果失败返回 None
        """
        if not self.unimem or not script_memory_ids:
            logger.debug("UniMem not available or no script memories to reflect")
            return None
        
        try:
            # 通过 recall 检索相关的剧本创作记忆
            # 使用视频类型和平台作为查询，这样可以检索到相关的所有记忆
            query = f"{video_type} {platform} 短视频脚本 剧本创作"
            # 检查是否是 HTTP 服务客户端（不需要 context 参数）
            if hasattr(self.unimem, 'base_url'):
                results = self.unimem.recall(
                    query=query,
                    top_k=min(10, len(script_memory_ids) * 2)  # 检索足够多的相关记忆
                )
            else:
                results = self.unimem.recall(
                    query=query,
                    context=Context(),
                    top_k=min(10, len(script_memory_ids) * 2)  # 检索足够多的相关记忆
                )
            
            # 筛选出与当前剧本相关的记忆
            memories_to_reflect = []
            memory_id_set = set(script_memory_ids)
            
            for result in results:
                memory = result.memory
                # 检查是否是我们要反思的记忆，或者与这些记忆相关
                if (memory.id in memory_id_set or 
                    any(linked_id in memory_id_set for linked_id in memory.links) or
                    memory.metadata.get("video_type") == video_type and 
                    memory.metadata.get("platform") == platform):
                    memories_to_reflect.append(memory)
            
            # 如果通过 recall 没有找到足够的记忆，尝试直接使用存储适配器获取
            if len(memories_to_reflect) < len(script_memory_ids):
                # 尝试从存储中直接获取记忆（如果存储适配器支持）
                logger.info(f"Recall found {len(memories_to_reflect)} memories, trying direct retrieval from storage")
                if hasattr(self.unimem, 'storage') and hasattr(self.unimem.storage, 'get_memory'):
                    for memory_id in script_memory_ids[:5]:
                        if memory_id not in [m.id for m in memories_to_reflect]:
                            try:
                                memory = self.unimem.storage.get_memory(memory_id)
                                if memory:
                                    memories_to_reflect.append(memory)
                                    logger.info(f"Retrieved memory {memory_id} directly from storage")
                            except Exception as e:
                                logger.debug(f"Could not get memory {memory_id} directly: {e}")
                else:
                    # 如果存储适配器不支持直接获取，尝试从 operation_adapter 中获取
                    # 由于刚存储的记忆可能还没被索引，我们直接使用我们已知的 memory_ids
                    # 创建一个简化的 Memory 对象用于 REFLECT
                    logger.info("Storage adapter doesn't support direct retrieval, using script memory IDs directly")
                    # 这里我们至少可以尝试 REFLECT，即使没有完整的记忆对象
                    # REFLECT 操作应该能够处理这种情况
            
            # 如果仍然没有记忆，但提供了 script_memory_ids，我们至少记录这些 IDs
            if not memories_to_reflect and script_memory_ids:
                logger.warning(f"No memories found for reflection, but we have {len(script_memory_ids)} memory IDs: {script_memory_ids}")
                # 尝试创建一个简化的任务，即使没有完整的记忆对象
                # 这种情况下，REFLECT 可能无法完成，但我们至少尝试了
                return None
            
            # 创建 REFLECT 任务（增强版：更具体的总结要求）
            task = Task(
                id=f"reflect_script_{video_type}_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                description=f"总结{video_type}类型{platform}平台短视频剧本创作的成功模式和经验",
                context=f"""
视频类型：{video_type}
平台：{platform}
优化迭代次数：{iteration_count}
相关剧本数量：{len(script_memory_ids)}

请深入总结以下内容（重点关注可复用的经验和模式）：
1. 成功的创作模式和技巧（具体可执行的模式）
2. 用户偏好的变化趋势（哪些偏好被反复强调）
3. 有效的修改策略（哪些修改需求通常能带来显著改进）
4. 需要避免的问题（常见的错误和改进失败的原因）
5. 可复用的经验（可以应用到未来创作的通用经验）
6. 优化效果评估（不同修改类型的成功率）

请特别关注：
- 哪些类型的修改需求最容易被满足
- 哪些优化策略效果最好
- 用户的偏好模式（如果有多轮优化，观察偏好变化）
- 镜头素材的使用模式（如果有镜头信息）
                """.strip()
            )
            
            # 创建上下文（包含 Agent Profile）
            context = Context(
                metadata={
                    "task_description": "短视频剧本创作经验总结",
                    "video_type": video_type,
                    "platform": platform,
                    "iteration_count": iteration_count,
                    "agent_background": "专业的短视频创作助手，擅长总结创作经验和优化策略",
                    "agent_disposition": {
                        "skepticism": 2,  # 适度怀疑，但信任成功经验
                        "literalism": 3,  # 平衡字面和灵活理解
                        "empathy": 4  # 高同理心，理解用户需求
                    }
                }
            )
            
            # 执行 REFLECT 操作
            logger.info(f"REFLECT: Reflecting on {len(memories_to_reflect)} script memories")
            evolved_memories = self.unimem.reflect(memories_to_reflect, task, context)
            
            evolved_memory_ids = [mem.id for mem in evolved_memories]
            logger.info(f"REFLECT completed: {len(evolved_memories)} memories evolved")
            
            return evolved_memory_ids
            
        except Exception as e:
            logger.warning(f"Failed to reflect on script creation: {e}", exc_info=True)
            return None


def interactive_mode(generator: VideoScriptGenerator):
    """交互式模式：支持多次优化"""
    
    print("\n" + "="*60)
    print("短视频剧本生成器 - 交互式模式")
    print("="*60 + "\n")
    
    # 1. 创建或选择 Word 模板
    template_path = "video_script_template.docx"
    if not os.path.exists(template_path):
        print(f"正在创建 Word 模板: {template_path}")
        generator.create_template(template_path)
        print(f"模板已创建，请填写后重新运行此脚本。")
        print(f"或者直接提供已填写的 Word 文档路径。")
        return
    
    # 2. 解析 Word 文档
    doc_path = input(f"请输入 Word 文档路径（直接回车使用 {template_path}）: ").strip()
    if not doc_path:
        doc_path = template_path
    
    if not os.path.exists(doc_path):
        print(f"错误：文件不存在: {doc_path}")
        return
    
    print(f"\n正在解析文档: {doc_path}")
    doc_data = generator.parse_word_document(doc_path)
    
    # 显示解析结果
    print("\n解析结果：")
    print(f"  视频类型: {doc_data.get('video_type')}")
    print(f"  目标平台: {doc_data.get('platform')}")
    print(f"  目标时长: {doc_data.get('duration_seconds')}秒")
    print(f"  任务需求: {len(doc_data.get('task_memories', []))} 条")
    print(f"  通用记忆: {len(doc_data.get('general_memories', []))} 条")
    
    # 3. 生成初始剧本
    print("\n正在生成初始剧本...")
    script = generator.generate_script(doc_data)
    
    if not script:
        print("错误：剧本生成失败")
        return
    
    # 显示剧本摘要
    print("\n" + "="*60)
    print("生成的剧本摘要：")
    print("="*60)
    summary = script.get("summary", {})
    print(f"开头亮点: {summary.get('hook', 'N/A')}")
    print(f"核心内容: {summary.get('core_content', 'N/A')}")
    print(f"结尾类型: {summary.get('ending_type', 'N/A')}")
    print(f"目标受众: {summary.get('target_audience', 'N/A')}")
    print(f"段数: {len(script.get('segments', []))}")
    
    if "unimem_memory_id" in script:
        print(f"UniMem记忆ID: {script['unimem_memory_id']}")
    
    # 保存剧本到文件
    script_path = "generated_script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"\n完整剧本已保存到: {script_path}")
    
    # 4. 交互式优化循环（支持多次对话累积修改需求）
    script_memory_id = script.get("unimem_memory_id")
    iteration = 0
    accumulated_modifications = doc_data.get("modification_memories", []).copy()  # 累积所有修改需求
    script_memory_ids = [script_memory_id] if script_memory_id else []  # 累积所有剧本记忆 ID
    
    # 显示初始的修改需求（如果有）
    if accumulated_modifications:
        print(f"\n初始文档中的修改需求（{len(accumulated_modifications)} 条）：")
        for i, mod in enumerate(accumulated_modifications, 1):
            print(f"  {i}. {mod}")
    
    # REFLECT 触发条件：每3次优化后自动触发
    REFLECT_INTERVAL = 3
    
    while True:
        iteration += 1
        print("\n" + "="*60)
        print(f"优化迭代 #{iteration}")
        print("="*60)
        
        # 显示已累积的修改需求
        if accumulated_modifications:
            print(f"\n已累积的修改需求（共 {len(accumulated_modifications)} 条）：")
            for i, mod in enumerate(accumulated_modifications[-5:], 1):  # 只显示最近5条
                print(f"  {i}. {mod}")
            if len(accumulated_modifications) > 5:
                print(f"  ... 还有 {len(accumulated_modifications) - 5} 条修改需求")
        
        user_input = input("\n请输入您的反馈和修改要求（直接回车跳过优化，输入 'quit' 退出）:\n").strip()
        
        if not user_input or user_input.lower() == 'quit':
            break
        
        # 提取修改需求（传入已有的修改需求，避免重复提取）
        modifications = generator.extract_modification_feedback(
            user_input, 
            existing_modifications=accumulated_modifications
        )
        
        if not modifications:
            print("未能从输入中提取到明确的修改需求，请重新输入。")
            continue
        
        print(f"\n本次提取到 {len(modifications)} 条新的修改需求：")
        for i, mod in enumerate(modifications, 1):
            print(f"  {i}. {mod}")
        
        # 将新的修改需求添加到累积列表中
        accumulated_modifications.extend(modifications)
        print(f"\n累积修改需求总数：{len(accumulated_modifications)} 条")
        
        # 存储反馈到 UniMem
        feedback_memory_id = generator.store_feedback_to_unimem(
            feedback=user_input,
            script_memory_id=script_memory_id
        )
        
        # 优化并重新生成（传入累积的修改需求）
        print("\n正在基于所有累积的反馈优化剧本...")
        optimized_script = generator.optimize_and_regenerate(
            original_doc_data=doc_data,
            modification_feedback=modifications,  # 本次新增的修改需求
            original_script=script,
            accumulated_modifications=accumulated_modifications  # 所有累积的修改需求
        )
        
        if not optimized_script:
            print("优化失败，请重试。")
            # 如果优化失败，回退本次添加的修改需求
            accumulated_modifications = accumulated_modifications[:-len(modifications)]
            continue
        
        # 显示优化后的摘要
        print("\n优化后的剧本摘要：")
        optimized_summary = optimized_script.get("summary", {})
        print(f"开头亮点: {optimized_summary.get('hook', 'N/A')}")
        print(f"核心内容: {optimized_summary.get('core_content', 'N/A')}")
        
        # 保存优化后的剧本
        optimized_script_path = f"generated_script_optimized_v{iteration}.json"
        with open(optimized_script_path, "w", encoding="utf-8") as f:
            json.dump(optimized_script, f, ensure_ascii=False, indent=2)
        print(f"\n优化后的剧本已保存到: {optimized_script_path}")
        
        # 更新当前剧本
        script = optimized_script
        if "unimem_memory_id" in script:
            new_memory_id = script["unimem_memory_id"]
            if new_memory_id and new_memory_id not in script_memory_ids:
                script_memory_ids.append(new_memory_id)
            script_memory_id = new_memory_id
        
        # 更新文档数据中的修改需求（用于下次优化）
        doc_data["modification_memories"] = accumulated_modifications.copy()
        
        # ========== 增强：每轮优化后自动评估并总结 ==========
        if iteration > 0 and iteration % 2 == 0:  # 每2轮优化后评估
            logger.info(f"触发自动REFLECT操作（已优化{iteration}轮）...")
            if script_memory_ids:
                evolved_ids = self.reflect_on_script_creation(
                    script_memory_ids=script_memory_ids,
                    video_type=doc_data.get("video_type", "ecommerce"),
                    platform=doc_data.get("platform", "douyin"),
                    iteration_count=iteration
                )
                if evolved_ids:
                    logger.info(f"REFLECT完成，生成{len(evolved_ids)}个演化记忆")
        
        # 每 REFLECT_INTERVAL 次优化后，自动触发 REFLECT 操作
        if iteration % REFLECT_INTERVAL == 0 and iteration > 0:
            print(f"\n{'='*60}")
            print(f"触发 REFLECT 操作（已优化 {iteration} 次）")
            print(f"{'='*60}")
            print("正在总结创作经验和成功模式...")
            
            evolved_ids = generator.reflect_on_script_creation(
                script_memory_ids=script_memory_ids,
                video_type=doc_data.get("video_type", "ecommerce"),
                platform=doc_data.get("platform", "douyin"),
                iteration_count=iteration
            )
            
            if evolved_ids:
                print(f"✓ REFLECT 完成：优化了 {len(evolved_ids)} 条记忆")
                print("  这些经验将在后续创作中自动应用")
            else:
                print("⚠ REFLECT 操作未执行（可能因为 UniMem 不可用或没有相关记忆）")
        
        print("\n优化完成！您可以继续提供反馈，或输入 'quit' 退出。")
    
    # 交互式循环结束时，执行最终的 REFLECT 操作
    if iteration > 0 and script_memory_ids:
        print(f"\n{'='*60}")
        print("执行最终 REFLECT 操作：总结本次创作经验")
        print(f"{'='*60}")
        
        evolved_ids = generator.reflect_on_script_creation(
            script_memory_ids=script_memory_ids,
            video_type=doc_data.get("video_type", "ecommerce"),
            platform=doc_data.get("platform", "douyin"),
            iteration_count=iteration
        )
        
        if evolved_ids:
            print(f"✓ 最终 REFLECT 完成：优化了 {len(evolved_ids)} 条记忆")
            print("  这些经验已保存，将在未来的创作中自动应用")
        else:
            print("⚠ 最终 REFLECT 操作未执行")
    
    print("\n感谢使用！所有生成和优化的剧本已保存到当前目录。")


def main():
    """主函数"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="短视频剧本生成器")
    parser.add_argument("--template", action="store_true", help="仅创建 Word 模板")
    parser.add_argument("--template-path", default="video_script_template.docx", 
                       help="模板保存路径")
    parser.add_argument("--doc", help="Word 文档路径")
    parser.add_argument("--output", default="generated_script.json",
                       help="输出剧本文件路径")
    parser.add_argument("--interactive", "-i", action="store_true",
                       help="交互式模式")
    
    args = parser.parse_args()
    
    # 如果只是创建模板，跳过 UniMem 初始化
    if args.template:
        generator = VideoScriptGenerator(skip_unimem=True)
        generator.create_template(args.template_path)
        print(f"模板已创建: {args.template_path}")
        return
    
    # 尝试初始化 UniMem，如果失败则使用独立模式
    try:
        generator = VideoScriptGenerator()
        print("✓ UniMem 已启用，将使用记忆检索和存储功能")
    except Exception as e:
        print(f"⚠ UniMem 初始化失败: {e}")
        print("⚠ 将使用独立模式（不使用 UniMem 功能）")
        generator = VideoScriptGenerator(skip_unimem=True)
    
    # 交互式模式
    if args.interactive:
        if generator.unimem is None:
            print("⚠ 注意：独立模式下，交互式优化功能可能受限")
        interactive_mode(generator)
        return
    
    # 命令行模式
    if args.doc:
        # 解析文档
        doc_data = generator.parse_word_document(args.doc)
        
        # 生成剧本
        script = generator.generate_script(doc_data)
        
        if script:
            # 保存剧本
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(script, f, ensure_ascii=False, indent=2)
            print(f"剧本已生成并保存到: {args.output}")
        else:
            print("剧本生成失败")
    else:
        # 默认：交互式模式
        if generator.unimem is None:
            print("⚠ 注意：独立模式下，交互式优化功能可能受限")
        interactive_mode(generator)


if __name__ == "__main__":
    main()

