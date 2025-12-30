"""
存储管理器

管理 FoA/DA/LTM 三层存储，直接使用分层存储适配器
"""

from typing import Optional, List
from ..types import Memory, MemoryType, Context, RetrievalResult
from ..adapters import LayeredStorageAdapter, MemoryTypeAdapter

import logging
logger = logging.getLogger(__name__)


class StorageManager:
    """
    存储管理器：管理三层存储架构
    
    直接使用 LayeredStorageAdapter 进行存储操作，不再维护独立的 FoA/DA/LTM 类
    """
    
    def __init__(
        self,
        storage_adapter: LayeredStorageAdapter,
        memory_type_adapter: MemoryTypeAdapter,
    ):
        """
        初始化存储管理器
        
        Args:
            storage_adapter: 分层存储适配器（参考 CogMem）
            memory_type_adapter: 记忆分类适配器（参考 MemMachine）
        """
        self.storage_adapter = storage_adapter
        self.memory_type_adapter = memory_type_adapter
        
        logger.info("StorageManager initialized")
    
    def add_memory(self, memory: Memory, context: Optional[Context] = None) -> bool:
        """
        添加记忆到存储系统
        
        自动判断应该存储到哪一层：
        - FoA: 所有新记忆先进入工作记忆
        - DA: 如果记忆对会话关键，进入快速访问层
        - LTM: 所有记忆最终进入长期存储
        
        Args:
            memory: 记忆对象
            context: 上下文信息（用于判断是否关键）
            
        Returns:
            是否成功添加
        """
        try:
            ***REMOVED*** 1. 分类记忆类型
            if not memory.memory_type:
                memory.memory_type = self.memory_type_adapter.classify(memory)
            
            ***REMOVED*** 2. 添加到 FoA（工作记忆）
            if not self.storage_adapter.add_to_foa(memory):
                logger.warning(f"Failed to add memory {memory.id} to FoA")
                return False
            
            ***REMOVED*** 3. 如果关键，添加到 DA（快速访问）
            if context and self.storage_adapter.is_session_critical(memory, context):
                if not self.storage_adapter.add_to_da(memory):
                    logger.warning(f"Failed to add memory {memory.id} to DA")
                    ***REMOVED*** DA 失败不影响整体流程
            
            ***REMOVED*** 4. 添加到 LTM（长期存储）
            if not self.storage_adapter.add_to_ltm(memory, memory.memory_type):
                logger.error(f"Failed to add memory {memory.id} to LTM")
                return False
            
            logger.debug(f"Memory {memory.id} added to storage (type: {memory.memory_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding memory {memory.id}: {e}")
            return False
    
    def search_foa(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """在 FoA 中搜索"""
        try:
            memories = self.storage_adapter.search_foa(query, top_k)
            return [
                RetrievalResult(
                    memory=m,
                    score=1.0,
                    retrieval_method="foa",
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error searching FoA: {e}")
            return []
    
    def search_da(self, query: str, context: Optional[Context] = None, top_k: int = 10) -> List[RetrievalResult]:
        """在 DA 中搜索"""
        try:
            memories = self.storage_adapter.search_da(query, context or Context(), top_k)
            return [
                RetrievalResult(
                    memory=m,
                    score=0.9,
                    retrieval_method="da",
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error searching DA: {e}")
            return []
    
    def search_ltm(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """在 LTM 中搜索"""
        try:
            memories = self.storage_adapter.search_ltm(query, top_k)
            return [
                RetrievalResult(
                    memory=m,
                    score=0.8,
                    retrieval_method="ltm",
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error searching LTM: {e}")
            return []
    
    def update_memory(self, memory: Memory) -> bool:
        """
        更新记忆
        
        实现跨层更新逻辑：需要更新所有包含该记忆的层
        """
        try:
            ***REMOVED*** 检查记忆在哪些层
            ***REMOVED*** 1. 检查 FoA
            foa_memories = self.storage_adapter.search_foa("", top_k=1000)
            if any(m.id == memory.id for m in foa_memories):
                ***REMOVED*** 从 FoA 移除旧版本，添加新版本
                ***REMOVED*** 注意：这里需要适配器支持更新操作
                logger.debug(f"Memory {memory.id} found in FoA, updating...")
            
            ***REMOVED*** 2. 检查 DA
            da_memories = self.storage_adapter.search_da("", Context(), top_k=1000)
            if any(m.id == memory.id for m in da_memories):
                ***REMOVED*** 更新 DA 中的记忆
                if hasattr(self.storage_adapter, 'update_in_da'):
                    self.storage_adapter.update_in_da(memory)
                else:
                    ***REMOVED*** 回退方案：删除后重新添加
                    if hasattr(self.storage_adapter, 'remove_from_da'):
                        self.storage_adapter.remove_from_da(memory.id)
                    self.storage_adapter.add_to_da(memory)
                logger.debug(f"Memory {memory.id} found in DA, updating...")
            
            ***REMOVED*** 3. 更新 LTM（总是需要更新）
            if hasattr(self.storage_adapter, 'update_in_ltm'):
                self.storage_adapter.update_in_ltm(memory, memory.memory_type)
            else:
                ***REMOVED*** 回退方案：删除后重新添加
                if hasattr(self.storage_adapter, 'remove_from_ltm'):
                    self.storage_adapter.remove_from_ltm(memory.id)
                self.storage_adapter.add_to_ltm(memory, memory.memory_type)
            
            logger.debug(f"Memory {memory.id} updated in storage")
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory {memory.id}: {e}")
            return False
    
    def cleanup(self, max_age_hours: int = 24) -> int:
        """
        清理旧记忆（防止内存泄漏）
        
        Args:
            max_age_hours: 最大保留时间（小时）
            
        Returns:
            清理的记忆数量
        """
        if hasattr(self.storage_adapter, 'cleanup_old_memories'):
            return self.storage_adapter.cleanup_old_memories(max_age_hours)
        return 0
