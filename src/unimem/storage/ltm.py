"""
Long-Term Memory (LTM) - 长期存储

知识库底层，跨会话存储
"""

from typing import List, Optional
from ..types import Memory, MemoryType, RetrievalResult

import logging
logger = logging.getLogger(__name__)


class LongTermMemory:
    """长期记忆：跨会话存储层"""
    
    def __init__(self, backend: str = "postgresql"):
        """
        初始化 LTM
        
        Args:
            backend: 存储后端
        """
        self.backend = backend
        self._memories: dict[str, Memory] = {}  ***REMOVED*** 临时使用内存存储
        
        logger.info(f"LTM initialized with backend={backend}")
    
    def add(self, memory: Memory, memory_type: Optional[MemoryType] = None):
        """添加记忆到 LTM"""
        if memory_type:
            memory.memory_type = memory_type
        self._memories[memory.id] = memory
        logger.debug(f"Added memory {memory.id} to LTM")
    
    def update(self, memory: Memory):
        """更新记忆"""
        if memory.id in self._memories:
            self._memories[memory.id] = memory
            logger.debug(f"Updated memory {memory.id} in LTM")
    
    def search(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """搜索 LTM 中的记忆"""
        results = []
        
        for memory in self._memories.values():
            ***REMOVED*** 简单的文本匹配
            if query.lower() in memory.content.lower():
                score = 0.6
                results.append(RetrievalResult(
                    memory=memory,
                    score=score,
                    retrieval_method="ltm_text_match",
                ))
        
        ***REMOVED*** 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

