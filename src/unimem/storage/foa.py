"""
Focus of Attention (FoA) - 工作记忆

顶层短期记忆，类似于"人类当前正在思考的内容"
"""

from typing import List, Optional
from ..types import Memory, RetrievalResult

import logging
logger = logging.getLogger(__name__)


class FocusOfAttention:
    """注意力焦点：工作记忆层"""
    
    def __init__(self, backend: str = "redis", max_tokens: int = 100):
        """
        初始化 FoA
        
        Args:
            backend: 存储后端
            max_tokens: 最大 token 数
        """
        self.backend = backend
        self.max_tokens = max_tokens
        self._memories: List[Memory] = []  ***REMOVED*** 临时使用内存存储
        
        logger.info(f"FoA initialized with backend={backend}, max_tokens={max_tokens}")
    
    def add(self, memory: Memory):
        """添加记忆到 FoA"""
        ***REMOVED*** 检查 token 限制
        if len(self._memories) >= 10:  ***REMOVED*** 简单限制
            ***REMOVED*** 移除最旧的记忆
            self._memories.pop(0)
        
        self._memories.append(memory)
        logger.debug(f"Added memory {memory.id} to FoA")
    
    def search(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """搜索 FoA 中的记忆"""
        results = []
        
        for memory in self._memories:
            ***REMOVED*** 简单的文本匹配
            if query.lower() in memory.content.lower():
                score = 1.0
                results.append(RetrievalResult(
                    memory=memory,
                    score=score,
                    retrieval_method="foa_text_match",
                ))
        
        ***REMOVED*** 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

