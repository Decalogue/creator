"""
分层存储适配器

实现 UniMem 的 FoA/DA/LTM 三层存储
参考架构：CogMem（三层记忆架构）

核心功能：
- FoA (Focus of Attention)：工作记忆层，极小 token 预算（~100 tokens）
- DA (Declarative Access)：快速访问层，会话级记忆
- LTM (Long-Term Memory)：长期存储层，无限制容量

工业级特性：
- 线程安全（RLock）
- 配置验证
- 完善的错误处理
"""

from typing import Dict, List
from datetime import datetime, timedelta
import threading
import logging

from .base import (
    BaseAdapter,
    AdapterConfigurationError,
    AdapterError
)
from ..types import Memory, Context, MemoryType

logger = logging.getLogger(__name__)


class LayeredStorageAdapter(BaseAdapter):
    """
    分层存储适配器
    
    功能需求：实现 FoA/DA/LTM 三层存储
    参考架构：CogMem（三层记忆架构）
    
    核心特性：
    - FoA: 工作记忆层，极小 token 预算（~100 tokens），动态重构和淘汰
    - DA: 快速访问层，会话级记忆，关键信息快速访问
    - LTM: 长期存储层，无限制容量，跨会话存储
    
    线程安全：使用 RLock 保护所有存储操作
    """
    
    def _do_initialize(self) -> None:
        """
        初始化分层存储适配器
        
        初始化三层存储结构和线程安全锁。
        
        Raises:
            AdapterConfigurationError: 如果配置无效
        """
        ***REMOVED*** 参考 CogMem 的初始化思路
        ***REMOVED*** FoA: 工作记忆，极小 token 预算
        ***REMOVED*** DA: 快速访问，会话级
        ***REMOVED*** LTM: 长期存储，无限制
        self.foa_storage: List[Memory] = []
        self.da_storage: Dict[str, Memory] = {}
        self.ltm_storage: Dict[str, Memory] = {}
        
        ***REMOVED*** 线程安全锁（使用 RLock 支持嵌套锁）
        self._foa_lock = threading.RLock()
        self._da_lock = threading.RLock()
        self._ltm_lock = threading.RLock()
        
        ***REMOVED*** FoA token 预算配置
        foa_max_tokens = int(self.config.get("foa_max_tokens", 100))
        foa_max_memories = int(self.config.get("foa_max_memories", 10))
        
        ***REMOVED*** 配置验证
        if foa_max_tokens <= 0:
            raise AdapterConfigurationError(
                f"foa_max_tokens must be positive, got {foa_max_tokens}",
                adapter_name=self.__class__.__name__
            )
        if foa_max_memories <= 0:
            raise AdapterConfigurationError(
                f"foa_max_memories must be positive, got {foa_max_memories}",
                adapter_name=self.__class__.__name__
            )
        
        self.foa_max_tokens = foa_max_tokens
        self.foa_max_memories = foa_max_memories
        
        logger.info(
            f"Layered storage adapter initialized "
            f"(using CogMem principles, FoA max: {self.foa_max_tokens} tokens, "
            f"{self.foa_max_memories} memories)"
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """
        估算文本的 token 数量
        
        简单实现：使用字符数 / 4 作为近似值（适用于英文和中文）。
        实际应该使用 tiktoken 等库进行精确计算。
        
        Args:
            text: 输入文本
            
        Returns:
            int: 估算的 token 数量
        """
        if not text:
            return 0
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
        - 动态重构和淘汰（FIFO 策略）
        
        Args:
            memory: 要添加的记忆
            
        Returns:
            bool: 是否成功添加
            
        Note:
            - 如果超过 token 预算或记忆数量限制，会自动移除最旧的记忆
            - 线程安全
        """
        if not memory:
            logger.warning("Cannot add None memory to FoA")
            return False
        
        if not self.is_available():
            logger.warning("LayeredStorageAdapter not available, cannot add to FoA")
            return False
        
        try:
            with self._foa_lock:
                ***REMOVED*** 估算新记忆的 token 数
                memory_tokens = self._estimate_tokens(memory.content)
                current_tokens = sum(self._estimate_tokens(m.content) for m in self.foa_storage)
                
                ***REMOVED*** 如果超过 token 预算或记忆数量限制，移除最旧的记忆（FIFO）
                while (current_tokens + memory_tokens > self.foa_max_tokens or 
                       len(self.foa_storage) >= self.foa_max_memories) and self.foa_storage:
                    removed = self.foa_storage.pop(0)
                    removed_tokens = self._estimate_tokens(removed.content)
                    current_tokens -= removed_tokens
                    logger.debug(f"Removed memory {removed.id[:8]}... from FoA due to token budget")
                
                self.foa_storage.append(memory)
                logger.debug(f"Added memory {memory.id[:8]}... to FoA (tokens: {memory_tokens}, total: {current_tokens + memory_tokens})")
                return True
        except Exception as e:
            logger.error(f"Error adding memory to FoA: {e}", exc_info=True)
            return False
    
    def add_to_da(self, memory: Memory) -> bool:
        """
        添加到 DA（快速访问层）
        
        参考 CogMem 的 DA 思路：
        - 会话级记忆
        - 关键信息快速访问
        
        Args:
            memory: 要添加的记忆
            
        Returns:
            bool: 是否成功添加
            
        Note:
            - 线程安全
            - 使用字典存储，支持快速查找
        """
        if not memory:
            logger.warning("Cannot add None memory to DA")
            return False
        
        if not self.is_available():
            logger.warning("LayeredStorageAdapter not available, cannot add to DA")
            return False
        
        try:
            with self._da_lock:
                self.da_storage[memory.id] = memory
                logger.debug(f"Added memory {memory.id[:8]}... to DA")
                return True
        except Exception as e:
            logger.error(f"Error adding memory to DA: {e}", exc_info=True)
            return False
    
    def add_to_ltm(self, memory: Memory, memory_type: MemoryType) -> bool:
        """
        添加到 LTM（长期存储层）
        
        参考 CogMem 的 LTM 思路：
        - 跨会话存储
        - 无限制容量
        
        Args:
            memory: 要添加的记忆
            memory_type: 记忆类型
            
        Returns:
            bool: 是否成功添加
            
        Note:
            - 线程安全
            - 使用字典存储，支持快速查找
        """
        if not memory:
            logger.warning("Cannot add None memory to LTM")
            return False
        
        if not self.is_available():
            logger.warning("LayeredStorageAdapter not available, cannot add to LTM")
            return False
        
        try:
            with self._ltm_lock:
                self.ltm_storage[memory.id] = memory
                logger.debug(f"Added memory {memory.id[:8]}... to LTM (type: {memory_type.value})")
                return True
        except Exception as e:
            logger.error(f"Error adding memory to LTM: {e}", exc_info=True)
            return False
    
    def search_foa(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        在 FoA 中搜索
        
        Args:
            query: 查询字符串（当前未使用，保留用于接口一致性）
            top_k: 返回结果数量
            
        Returns:
            List[Memory]: 最近的记忆列表（最新的在前）
            
        Note:
            - 线程安全
            - 返回副本，避免外部修改内部存储
            - 当前实现为简单实现（返回最近的记忆），实际应该实现语义搜索
        """
        if not self.is_available():
            return []
        
        try:
            with self._foa_lock:
                ***REMOVED*** 简单实现：返回最近的记忆（最新的在前）
                ***REMOVED*** 实际应该实现语义搜索
                return self.foa_storage[-top_k:].copy()  ***REMOVED*** 返回副本，避免外部修改
        except Exception as e:
            logger.error(f"Error searching FoA: {e}", exc_info=True)
            return []
    
    def search_da(self, query: str, context: Context, top_k: int = 10) -> List[Memory]:
        """
        在 DA 中搜索
        
        Args:
            query: 查询字符串（当前未使用，保留用于接口一致性）
            context: 上下文信息（当前未使用，保留用于接口一致性）
            top_k: 返回结果数量
            
        Returns:
            List[Memory]: DA 中的记忆列表
            
        Note:
            - 线程安全
            - 当前实现为简单实现（返回所有记忆），实际应该实现语义搜索
        """
        if not self.is_available():
            return []
        
        try:
            with self._da_lock:
                ***REMOVED*** 简单实现：返回所有 DA 记忆
                ***REMOVED*** 实际应该实现语义搜索
                return list(self.da_storage.values())[:top_k]
        except Exception as e:
            logger.error(f"Error searching DA: {e}", exc_info=True)
            return []
    
    def search_ltm(self, query: str, top_k: int = 10) -> List[Memory]:
        """
        在 LTM 中搜索
        
        Args:
            query: 查询字符串（当前未使用，保留用于接口一致性）
            top_k: 返回结果数量
            
        Returns:
            List[Memory]: LTM 中的记忆列表
            
        Note:
            - 线程安全
            - 当前实现为简单实现（返回所有记忆），实际应该实现语义搜索
        """
        if not self.is_available():
            return []
        
        try:
            with self._ltm_lock:
                ***REMOVED*** 简单实现：返回所有 LTM 记忆
                ***REMOVED*** 实际应该实现语义搜索
                return list(self.ltm_storage.values())[:top_k]
        except Exception as e:
            logger.error(f"Error searching LTM: {e}", exc_info=True)
            return []
    
    def is_session_critical(self, memory: Memory, context: Context) -> bool:
        """
        判断记忆是否对会话关键（用于决定是否进入 DA）
        
        参考 CogMem 的判断思路：包含用户ID或会话ID的记忆视为关键。
        
        Args:
            memory: 要判断的记忆
            context: 上下文信息
            
        Returns:
            bool: 如果记忆对会话关键则返回 True
            
        Note:
            - 当前实现为简单启发式规则
            - 实际应该使用更复杂的判断逻辑（如 LLM 判断）
        """
        if not memory or not context:
            return False
        
        try:
            ***REMOVED*** 简单启发式：包含用户ID或会话ID的记忆视为关键
            if context.user_id and memory.content and context.user_id in memory.content:
                return True
            if context.session_id and memory.content and context.session_id in memory.content:
                return True
            return False
        except Exception as e:
            logger.warning(f"Error in is_session_critical: {e}")
            return False
    
    def cleanup_old_memories(self, max_age_hours: int = 24) -> int:
        """
        清理旧记忆（防止内存泄漏）
        
        清理 DA 中超过指定时间的旧记忆。FoA 通过 token 预算自动管理，LTM 通常不清理。
        
        Args:
            max_age_hours: 最大保留时间（小时），默认 24 小时
            
        Returns:
            int: 清理的记忆数量
            
        Note:
            - 只清理 DA 中的旧记忆
            - FoA 通过 token 预算自动管理，无需手动清理
            - LTM 通常不清理（长期存储）
        """
        if not self.is_available():
            return 0
        
        if max_age_hours <= 0:
            logger.warning(f"Invalid max_age_hours: {max_age_hours}, must be positive")
            return 0
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            ***REMOVED*** 清理 DA 中的旧记忆（FoA 通过 token 预算自动管理，LTM 通常不清理）
            cleaned_da = 0
            with self._da_lock:
                da_to_remove = [
                    memory_id for memory_id, memory in self.da_storage.items()
                    if memory.timestamp and memory.timestamp < cutoff_time
                ]
                for memory_id in da_to_remove:
                    del self.da_storage[memory_id]
                    cleaned_da += 1
            
            if cleaned_da > 0:
                logger.info(f"Cleaned up {cleaned_da} old memories from DA (max_age: {max_age_hours}h)")
            return cleaned_da
        except Exception as e:
            logger.error(f"Error cleaning up old memories: {e}", exc_info=True)
            return 0
    
    def remove_from_foa(self, memory_id: str) -> bool:
        """
        从 FoA 移除记忆（用于回滚）
        
        Args:
            memory_id: 要移除的记忆 ID
            
        Returns:
            bool: 是否成功移除（如果记忆不存在也返回 True）
            
        Note:
            - 线程安全
        """
        if not memory_id:
            return False
        
        try:
            with self._foa_lock:
                original_count = len(self.foa_storage)
                self.foa_storage = [m for m in self.foa_storage if m.id != memory_id]
                removed = len(self.foa_storage) < original_count
                if removed:
                    logger.debug(f"Removed memory {memory_id[:8]}... from FoA")
                return True
        except Exception as e:
            logger.error(f"Error removing memory from FoA: {e}", exc_info=True)
            return False
    
    def remove_from_da(self, memory_id: str) -> bool:
        """
        从 DA 移除记忆（用于回滚）
        
        Args:
            memory_id: 要移除的记忆 ID
            
        Returns:
            bool: 是否成功移除
            
        Note:
            - 线程安全
        """
        if not memory_id:
            return False
        
        try:
            with self._da_lock:
                if memory_id in self.da_storage:
                    del self.da_storage[memory_id]
                    logger.debug(f"Removed memory {memory_id[:8]}... from DA")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error removing memory from DA: {e}", exc_info=True)
            return False
    
    def remove_from_ltm(self, memory_id: str) -> bool:
        """
        从 LTM 移除记忆（用于回滚）
        
        Args:
            memory_id: 要移除的记忆 ID
            
        Returns:
            bool: 是否成功移除
            
        Note:
            - 线程安全
        """
        if not memory_id:
            return False
        
        try:
            with self._ltm_lock:
                if memory_id in self.ltm_storage:
                    del self.ltm_storage[memory_id]
                    logger.debug(f"Removed memory {memory_id[:8]}... from LTM")
                    return True
                return False
        except Exception as e:
            logger.error(f"Error removing memory from LTM: {e}", exc_info=True)
            return False
