"""
检索引擎

实现多维检索和 RRF 融合，直接使用适配器
"""

from typing import List, Optional
from ..types import RetrievalResult, Memory, Context
from ..adapters import GraphAdapter, NetworkLinkAdapter, RetrievalAdapter

import logging
logger = logging.getLogger(__name__)


class RetrievalEngine:
    """
    检索引擎：多维检索和融合
    
    直接使用各个适配器进行检索，然后融合结果
    """
    
    def __init__(
        self,
        graph_adapter: GraphAdapter,
        network_link_adapter: NetworkLinkAdapter,
        retrieval_adapter: RetrievalAdapter,
        storage_manager=None,
    ):
        """
        初始化检索引擎
        
        Args:
            graph_adapter: 图结构适配器（参考 LightRAG）
            network_link_adapter: 网络链接适配器（参考 A-Mem）
            retrieval_adapter: 检索引擎适配器（参考各架构）
            storage_manager: 存储管理器（用于 FoA/DA/LTM 检索）
        """
        self.graph_adapter = graph_adapter
        self.network_link_adapter = network_link_adapter
        self.retrieval_adapter = retrieval_adapter
        self.storage_manager = storage_manager
        
        logger.info("RetrievalEngine initialized")
    
    def entity_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        实体级检索（低级别检索）
        
        使用图结构适配器进行实体检索
        """
        return self.graph_adapter.entity_retrieval(query, top_k=top_k)
    
    def abstract_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        抽象概念检索（高级别检索）
        
        使用图结构适配器进行抽象检索
        """
        return self.graph_adapter.abstract_retrieval(query, top_k=top_k)
    
    def semantic_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        语义检索
        
        使用网络链接适配器进行语义检索
        """
        return self.network_link_adapter.semantic_retrieval(query, top_k=top_k)
    
    def subgraph_link_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        子图链接检索
        
        使用网络链接适配器进行子图链接检索
        """
        return self.network_link_adapter.subgraph_link_retrieval(query, top_k=top_k)
    
    def temporal_retrieval(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        时间检索
        
        使用检索引擎适配器进行时间检索
        """
        return self.retrieval_adapter.temporal_retrieval(query, top_k=top_k)
    
    def multi_dimensional_retrieval(
        self,
        query: str,
        context: Optional[Context] = None,
        top_k: int = 10,
    ) -> List[RetrievalResult]:
        """
        多维检索
        
        并行执行多种检索方法，然后融合结果
        
        Args:
            query: 查询字符串
            context: 上下文信息
            top_k: 返回结果数量
            
        Returns:
            融合后的检索结果
        """
        all_results: List[List[Memory]] = []
        
        ***REMOVED*** 1. 图结构检索（LightRAG）
        entity_results = self.entity_retrieval(query, top_k)
        all_results.append(entity_results)
        
        abstract_results = self.abstract_retrieval(query, top_k)
        all_results.append(abstract_results)
        
        ***REMOVED*** 2. 子图链接检索（A-Mem）
        semantic_results = self.semantic_retrieval(query, top_k)
        all_results.append(semantic_results)
        
        graph_results = self.subgraph_link_retrieval(query, top_k)
        all_results.append(graph_results)
        
        ***REMOVED*** 3. 时间检索（CogMem）
        temporal_results = self.temporal_retrieval(query, top_k)
        all_results.append(temporal_results)
        
        ***REMOVED*** 4. 存储层检索（如果 storage_manager 可用）
        if self.storage_manager:
            foa_results = [r.memory for r in self.storage_manager.search_foa(query, top_k)]
            all_results.append(foa_results)
            
            da_results = [r.memory for r in self.storage_manager.search_da(query, context, top_k)]
            all_results.append(da_results)
            
            ltm_results = [r.memory for r in self.storage_manager.search_ltm(query, top_k)]
            all_results.append(ltm_results)
        
        ***REMOVED*** 5. RRF 融合（使用适配器的方法，它会返回融合后的 Memory 列表和分数）
        fused_memories = self.retrieval_adapter.rrf_fusion(all_results)
        
        ***REMOVED*** 6. 重排序
        ranked_memories = self.retrieval_adapter.rerank(query, fused_memories)
        
        ***REMOVED*** 7. 转换为 RetrievalResult
        ***REMOVED*** 从 RRF 融合中获取分数（如果适配器支持）
        results = []
        for i, memory in enumerate(ranked_memories):
            ***REMOVED*** 尝试从 memory 的 metadata 中获取分数
            score = memory.metadata.get("rrf_score", 1.0 / (i + 1)) if hasattr(memory, 'metadata') else 1.0 / (i + 1)
            results.append(RetrievalResult(
                memory=memory,
                score=score,
                retrieval_method="multi_dimensional",
            ))
        
        logger.debug(f"Multi-dimensional retrieval: {len(results)} results")
        return results[:top_k]
    
    def rrf_fusion(self, results_list: List[List[Memory]], k: int = 60) -> List[Memory]:
        """
        RRF (Reciprocal Rank Fusion) 融合
        
        使用检索引擎适配器的 RRF 融合方法
        """
        return self.retrieval_adapter.rrf_fusion(results_list, k=k)
    
    def rerank(self, query: str, results: List[Memory]) -> List[Memory]:
        """
        重排序
        
        使用检索引擎适配器的重排序方法
        """
        return self.retrieval_adapter.rerank(query, results)
