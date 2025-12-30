"""
分层存储适配器

实现 UniMem 的 FoA/DA/LTM 三层存储
参考架构：CogMem（三层记忆架构）
"""

from typing import Dict, Any, Optional, List
from abc import abstractmethod
import threading
from .base import BaseAdapter
from ..types import Memory, Context, MemoryType
import logging

logger = logging.getLogger(__name__)


class LayeredStorageAdapter(BaseAdapter):
    """
    分层存储适配器
    
    功能需求：实现 FoA/DA/LTM 三层存储
    参考架构：CogMem（三层记忆架构）
    
    线程安全：使用锁保护内存存储操作
    """
    
    @abstractmethod
    def add_to_foa(self, memory: Memory) -> bool:
        """添加到 FoA（工作记忆层）"""
        pass
    
    @abstractmethod
    def add_to_da(self, memory: Memory) -> bool:
        """添加到 DA（快速访问层）"""
        pass
    
    @abstractmethod
    def add_to_ltm(self, memory: Memory, memory_type: MemoryType) -> bool:
        """添加到 LTM（长期存储层）"""
        pass
    
    @abstractmethod
    def search_foa(self, query: str, top_k: int = 10) -> List[Memory]:
        """在 FoA 中搜索"""
        pass
    
    @abstractmethod
    def search_da(self, query: str, context: Context, top_k: int = 10) -> List[Memory]:
        """在 DA 中搜索"""
        pass
    
    @abstractmethod
    def search_ltm(self, query: str, top_k: int = 10) -> List[Memory]:
        """在 LTM 中搜索"""
        pass
    
    @abstractmethod
    def is_session_critical(self, memory: Memory, context: Context) -> bool:
        """判断记忆是否对会话关键（用于决定是否进入 DA）"""
        pass
    
    def _do_initialize(self):
        """初始化分层存储适配器"""
        ***REMOVED*** 参考 CogMem 的初始化思路
        ***REMOVED*** FoA: 工作记忆，极小 token 预算
        ***REMOVED*** DA: 快速访问，会话级
        ***REMOVED*** LTM: 长期存储，无限制
        self.foa_storage: List[Memory] = []
        self.da_storage: Dict[str, Memory] = {}
        self.ltm_storage: Dict[str, Memory] = {}
        
        ***REMOVED*** 线程安全锁
        self._foa_lock = threading.RLock()
        self._da_lock = threading.RLock()
        self._ltm_lock = threading.RLock()
        
        ***REMOVED*** FoA token 预算配置
        self.foa_max_tokens = self.config.get("foa_max_tokens", 100)
        self.foa_max_memories = self.config.get("foa_max_memories", 10)
        
        logger.info(f"Layered storage adapter initialized (using CogMem principles, FoA max: {self.foa_max_tokens} tokens)")
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        简单实现：使用字符数 / 4 作为近似值
        实际应该使用 tiktoken 等库
        """
        return len(text) // 4
    
    def _get_foa_tokens(self) -> int:
        """计算当前 FoA 的 token 总数（线程安全）"""
        with self._foa_lock:
            total = 0
            for memory in self.foa_storage:
                total += self._estimate_tokens(memory.content)
            return total
    
    def add_to_foa(self, memory: Memory) -> bool:
        """
        添加到 FoA（工作记忆层）
        
        参考 CogMem 的 FoA 思路：
        - 极小 token 预算（~100 tokens）
        - 动态重构和淘汰
        """
        with self._foa_lock:
            ***REMOVED*** 估算新记忆的 token 数
            memory_tokens = self._estimate_tokens(memory.content)
            current_tokens = sum(self._estimate_tokens(m.content) for m in self.foa_storage)
            
            ***REMOVED*** 如果超过 token 预算，移除最旧的记忆
            while (current_tokens + memory_tokens > self.foa_max_tokens or 
                   len(self.foa_storage) >= self.foa_max_memories) and self.foa_storage:
                removed = self.foa_storage.pop(0)
                current_tokens -= self._estimate_tokens(removed.content)
                logger.debug(f"Removed memory {removed.id} from FoA due to token budget")
            
            self.foa_storage.append(memory)
            logger.debug(f"Added memory {memory.id} to FoA (tokens: {memory_tokens}, total: {current_tokens + memory_tokens})")
            return True
    
    def add_to_da(self, memory: Memory) -> bool:
        """
        添加到 DA（快速访问层）
        
        参考 CogMem 的 DA 思路：
        - 会话级记忆
        - 关键信息快速访问
        """
        with self._da_lock:
            self.da_storage[memory.id] = memory
            logger.debug(f"Added memory {memory.id} to DA")
            return True
    
    def add_to_ltm(self, memory: Memory, memory_type: MemoryType) -> bool:
        """
        添加到 LTM（长期存储层）
        
        参考 CogMem 的 LTM 思路：
        - 跨会话存储
        - 无限制容量
        """
        with self._ltm_lock:
            self.ltm_storage[memory.id] = memory
            logger.debug(f"Added memory {memory.id} to LTM (type: {memory_type})")
            return True
    
    def search_foa(self, query: str, top_k: int = 10) -> List[Memory]:
        """在 FoA 中搜索（线程安全）"""
        with self._foa_lock:
            ***REMOVED*** 简单实现：返回最近的记忆
            return self.foa_storage[-top_k:].copy()  ***REMOVED*** 返回副本，避免外部修改
    
    def search_da(self, query: str, context: Context, top_k: int = 10) -> List[Memory]:
        """在 DA 中搜索（线程安全）"""
        with self._da_lock:
            ***REMOVED*** 简单实现：返回所有 DA 记忆
            return list(self.da_storage.values())[:top_k]
    
    def search_ltm(self, query: str, top_k: int = 10) -> List[Memory]:
        """在 LTM 中搜索（线程安全）"""
        with self._ltm_lock:
            ***REMOVED*** 简单实现：返回所有 LTM 记忆
            return list(self.ltm_storage.values())[:top_k]
    
    def is_session_critical(self, memory: Memory, context: Context) -> bool:
        """
        判断记忆是否对会话关键
        
        参考 CogMem 的判断思路
        """
        ***REMOVED*** 简单启发式：包含用户ID或会话ID的记忆视为关键
        if context.user_id and context.user_id in memory.content:
            return True
        if context.session_id and context.session_id in memory.content:
            return True
        return False
    
    def cleanup_old_memories(self, max_age_hours: int = 24) -> int:
        """
        清理旧记忆（防止内存泄漏）
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            清理的记忆数量
        """
        from datetime import datetime, timedelta
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        ***REMOVED*** 清理 DA 中的旧记忆（FoA 通过 token 预算自动管理）
        cleaned_da = 0
        with self._da_lock:
            da_to_remove = [
                memory_id for memory_id, memory in self.da_storage.items()
                if memory.timestamp < cutoff_time
            ]
            for memory_id in da_to_remove:
                del self.da_storage[memory_id]
                cleaned_da += 1
        
        logger.info(f"Cleaned up {cleaned_da} old memories from DA")
        return cleaned_da
    
    def remove_from_foa(self, memory_id: str) -> bool:
        """从 FoA 移除记忆（用于回滚）"""
        with self._foa_lock:
            self.foa_storage = [m for m in self.foa_storage if m.id != memory_id]
            return True
    
    def remove_from_da(self, memory_id: str) -> bool:
        """从 DA 移除记忆（用于回滚）"""
        with self._da_lock:
            if memory_id in self.da_storage:
                del self.da_storage[memory_id]
                return True
            return False
    
    def remove_from_ltm(self, memory_id: str) -> bool:
        """从 LTM 移除记忆（用于回滚）"""
        with self._ltm_lock:
            if memory_id in self.ltm_storage:
                del self.ltm_storage[memory_id]
                return True
            return False
