"""
Direct Access (DA) - 快速访问记忆

会话级记忆，类似于"会议笔记"
"""

from typing import List, Optional
from datetime import datetime
from ..types import Memory, RetrievalResult

import logging
logger = logging.getLogger(__name__)


class DirectAccess:
    """直接访问记忆：会话级记忆层"""
    
    def __init__(self, backend: str = "redis", max_tokens: int = 10000):
        """
        初始化 DA
        
        Args:
            backend: 存储后端
            max_tokens: 最大 token 数
        """
        self.backend = backend
        self.max_tokens = max_tokens
        self._notes: List[Memory] = []  ***REMOVED*** 临时使用内存存储
        
        logger.info(f"DA initialized with backend={backend}, max_tokens={max_tokens}")
    
    def add(self, memory: Memory):
        """添加笔记到 DA"""
        self._notes.append(memory)
        logger.debug(f"Added memory {memory.id} to DA")
    
    def add_note(self, memory: Memory):
        """添加笔记（别名）"""
        self.add(memory)
    
    def search(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """搜索 DA 中的记忆"""
        results = []
        
        for memory in self._notes:
            ***REMOVED*** 简单的文本匹配
            if query.lower() in memory.content.lower():
                score = 0.8
                results.append(RetrievalResult(
                    memory=memory,
                    score=score,
                    retrieval_method="da_text_match",
                ))
        
        ***REMOVED*** 按分数排序
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]

