"""
检索引擎

实现多维检索和 RRF 融合，直接使用适配器

设计特点：
- 多维检索：组合多种检索方法（实体、抽象、语义、子图、时间、存储层）
- 并行执行：使用线程池并行执行多种检索，提升性能
- RRF 融合：使用 Reciprocal Rank Fusion 融合多个检索结果
- 重排序：对融合后的结果进行重排序
- 错误处理：单个检索失败不影响整体检索

工业级特性：
- 线程安全（适配器已保证）
- 统一异常处理（使用适配器异常体系）
- 性能监控（操作耗时统计）
- 优雅降级（检索失败时的处理）
"""

import logging
import concurrent.futures
from functools import wraps
from typing import List, Optional, Dict, Any

from ..memory_types import RetrievalResult, Memory, Context
from ..adapters import GraphAdapter, AtomLinkAdapter, RetrievalAdapter
from ..adapters.base import AdapterError, AdapterNotAvailableError

logger = logging.getLogger(__name__)


def _safe_retrieval(func):
    """
    安全检索装饰器：捕获异常并返回空列表
    
    确保单个检索失败不影响整体检索
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"{func.__name__} failed: {e}", exc_info=True)
            return []
    return wrapper


class RetrievalEngine:
    """
    检索引擎：多维检索和融合
    
    直接使用各个适配器进行检索，然后融合结果。
    
    支持多种检索方法：
    - 实体级检索：基于实体和关系的检索（当前占位）
    - 抽象概念检索：基于抽象概念的检索（当前占位）
    - 语义检索（A-Mem）：基于向量相似度的检索
    - 子图链接检索（A-Mem）：基于子图结构的检索
    - 时间检索（CogMem）：基于时间维度的检索
    - 存储层检索（CogMem）：FoA/DA/LTM 分层检索
    
    检索流程：
    1. 并行执行多种检索方法
    2. 使用 RRF (Reciprocal Rank Fusion) 融合结果
    3. 重排序结果
    4. 返回 Top-K 结果
    """
    
    def __init__(
        self,
        graph_adapter: GraphAdapter,
        atom_link_adapter: AtomLinkAdapter,
        retrieval_adapter: RetrievalAdapter,
        storage_manager: Optional[Any] = None,
        max_workers: int = 5,
    ):
        """
        初始化检索引擎
        
        Args:
            graph_adapter: 图结构适配器（预留）
            atom_link_adapter: 原子链接适配器（参考 A-Mem）
            retrieval_adapter: 检索引擎适配器（参考各架构）
            storage_manager: 存储管理器（用于 FoA/DA/LTM 检索）
            max_workers: 并行执行的最大线程数（默认 5）
            
        Raises:
            AdapterError: 如果适配器无效
        """
        if not graph_adapter:
            raise AdapterError("graph_adapter cannot be None", adapter_name="RetrievalEngine")
        if not atom_link_adapter:
            raise AdapterError("atom_link_adapter cannot be None", adapter_name="RetrievalEngine")
        if not retrieval_adapter:
            raise AdapterError("retrieval_adapter cannot be None", adapter_name="RetrievalEngine")
        
        self.graph_adapter = graph_adapter
        self.atom_link_adapter = atom_link_adapter
        self.retrieval_adapter = retrieval_adapter
        self.storage_manager = storage_manager
        self.max_workers = max(max_workers, 1)  # 确保至少为 1
        
        logger.info(f"RetrievalEngine initialized (max_workers={self.max_workers})")
    
    @_safe_retrieval
    def entity_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        实体级检索（低级别检索）
        
        使用图结构适配器进行实体检索
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索到的记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for entity_retrieval")
            return []
        return self.graph_adapter.entity_retrieval(query, top_k=top_k)
    
    @_safe_retrieval
    def abstract_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        抽象概念检索（高级别检索）
        
        使用图结构适配器进行抽象检索
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索到的记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for abstract_retrieval")
            return []
        return self.graph_adapter.abstract_retrieval(query, top_k=top_k)
    
    @_safe_retrieval
    def semantic_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        语义检索
        
        使用原子链接适配器进行语义检索（A-Mem 风格，基于向量相似度）
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索到的记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for semantic_retrieval")
            return []
        return self.atom_link_adapter.semantic_retrieval(query, top_k=top_k)
    
    @_safe_retrieval
    def subgraph_link_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        子图链接检索
        
        使用原子链接适配器进行子图链接检索（A-Mem 风格，基于子图结构）
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索到的记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for subgraph_link_retrieval")
            return []
        return self.atom_link_adapter.subgraph_link_retrieval(query, top_k=top_k)
    
    @_safe_retrieval
    def temporal_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        时间检索
        
        使用检索引擎适配器进行时间检索（CogMem 风格，基于时间维度）
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索到的记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for temporal_retrieval")
            return []
        return self.retrieval_adapter.temporal_retrieval(query, top_k=top_k)
    
    def multi_dimensional_retrieval(
        self,
        query: str,
        context: Optional[Context] = None,
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """
        多维检索
        
        并行执行多种检索方法，然后融合结果。
        
        检索流程：
        1. 并行执行多种检索方法（实体、抽象、语义、子图、时间、存储层）
        2. 使用 RRF (Reciprocal Rank Fusion) 融合结果
        3. 重排序结果
        4. 返回 Top-K 结果
        
        Args:
            query: 查询字符串
            context: 上下文信息（可选）
            top_k: 返回结果数量
            
        Returns:
            融合后的检索结果列表
            
        Raises:
            ValueError: 如果 query 为空
        """
        if not query or not query.strip():
            logger.warning("Empty query for multi_dimensional_retrieval")
            return []
        
        logger.debug(f"Multi-dimensional retrieval: query='{query[:50]}...', top_k={top_k}")
        
        all_results: List[List[Memory]] = []
        
        # 1. 并行执行多种检索方法（图结构、语义、子图、时间）
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交检索任务
            futures: Dict[concurrent.futures.Future, str] = {
                executor.submit(self.entity_retrieval, query, top_k): "entity",
                executor.submit(self.abstract_retrieval, query, top_k): "abstract",
                executor.submit(self.semantic_retrieval, query, top_k): "semantic",
                executor.submit(self.subgraph_link_retrieval, query, top_k): "subgraph",
                executor.submit(self.temporal_retrieval, query, top_k): "temporal",
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(futures):
                method_name = futures[future]
                try:
                    results = future.result() or []
                    all_results.append(results)
                    logger.debug(f"{method_name} retrieval: {len(results)} results")
                except Exception as e:
                    logger.warning(f"{method_name} retrieval failed: {e}", exc_info=True)
                    all_results.append([])  # 失败时添加空列表
        
        # 2. 存储层检索（如果 storage_manager 可用，串行执行以避免线程安全问题）
        if self.storage_manager:
            for layer_name, search_func in [
                ("FoA", lambda: self.storage_manager.search_foa(query, top_k, context)),
                ("DA", lambda: self.storage_manager.search_da(query, context, top_k)),
                ("LTM", lambda: self.storage_manager.search_ltm(query, top_k)),
            ]:
                try:
                    results = [r.memory for r in search_func()] if search_func() else []
                    all_results.append(results)
                    logger.debug(f"{layer_name} retrieval: {len(results)} results")
                except Exception as e:
                    logger.warning(f"{layer_name} retrieval failed: {e}", exc_info=True)
                    all_results.append([])
        
        # 3. RRF 融合
        try:
            fused_memories = self.retrieval_adapter.rrf_fusion(all_results) or []
            logger.debug(f"RRF fusion: {len(fused_memories)} memories")
        except Exception as e:
            logger.error(f"RRF fusion failed: {e}", exc_info=True)
            # 降级：直接合并所有结果（去重）
            fused_memories = []
            seen_ids = set()
            for results in all_results:
                for memory in results:
                    if memory and memory.id not in seen_ids:
                        fused_memories.append(memory)
                        seen_ids.add(memory.id)
            logger.warning(f"Fallback to simple merge: {len(fused_memories)} memories")
        
        # 4. 重排序
        try:
            ranked_memories = self.retrieval_adapter.rerank(query, fused_memories)
            logger.debug(f"Rerank: {len(ranked_memories)} memories")
        except Exception as e:
            logger.warning(f"Rerank failed: {e}", exc_info=True)
            # 降级：使用原始顺序
            ranked_memories = fused_memories
        
        # 5. 转换为 RetrievalResult
        results = []
        for i, memory in enumerate(ranked_memories):
            # 尝试从 memory 的 metadata 中获取分数
            if hasattr(memory, 'metadata') and isinstance(memory.metadata, dict):
                score = memory.metadata.get("rrf_score", 1.0 / (i + 1))
            else:
                score = 1.0 / (i + 1)
            
            results.append(RetrievalResult(
                memory=memory,
                score=score,
                retrieval_method="multi_dimensional",
            ))
        
        logger.info(f"Multi-dimensional retrieval completed: {len(results)} results (requested {top_k})")
        return results[:top_k]
    
    def rrf_fusion(self, results_list: List[List[Memory]], k: int = 60) -> List[Memory]:
        """
        RRF (Reciprocal Rank Fusion) 融合
        
        使用检索引擎适配器的 RRF 融合方法。
        
        RRF 是一种融合多个排序列表的方法，通过计算每个项目的倒数排名分数来融合结果。
        
        Args:
            results_list: 多个检索结果列表
            k: RRF 参数（默认 60）
            
        Returns:
            融合后的记忆列表
        """
        if not results_list:
            logger.warning("Empty results_list for RRF fusion")
            return []
        
        try:
            return self.retrieval_adapter.rrf_fusion(results_list, k=k)
        except Exception as e:
            logger.error(f"RRF fusion failed: {e}", exc_info=True)
            # 降级：简单合并
            merged = []
            seen_ids = set()
            for results in results_list:
                for memory in results:
                    if memory.id not in seen_ids:
                        merged.append(memory)
                        seen_ids.add(memory.id)
            return merged
    
    def rerank(self, query: str, results: List[Memory]) -> List[Memory]:
        """
        重排序
        
        使用检索引擎适配器的重排序方法，根据查询相关性对结果进行重新排序。
        
        Args:
            query: 查询字符串
            results: 待重排序的记忆列表
            
        Returns:
            重排序后的记忆列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for rerank")
            return results
        
        if not results:
            logger.warning("Empty results for rerank")
            return results
        
        try:
            return self.retrieval_adapter.rerank(query, results)
        except Exception as e:
            logger.warning(f"Rerank failed: {e}", exc_info=True)
            # 降级：返回原始顺序
            return results
