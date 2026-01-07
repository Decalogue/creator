"""
存储管理器

管理 FoA/DA/LTM 三层存储，直接使用分层存储适配器

设计特点：
- 三层存储架构（FoA/DA/LTM）：参考 CogMem
- 自动层级判断：根据记忆类型和上下文自动判断存储层级
- 跨层更新：支持跨层更新记忆
- 统一接口：提供统一的存储和检索接口
- 错误处理：完善的错误处理和降级策略
"""

from typing import Optional, List, Set
from ..types import Memory, MemoryType, Context, RetrievalResult
from ..adapters import LayeredStorageAdapter, MemoryTypeAdapter

import logging
logger = logging.getLogger(__name__)


class StorageManager:
    """
    存储管理器：管理三层存储架构
    
    直接使用 LayeredStorageAdapter 进行存储操作，实现 FoA/DA/LTM 三层存储架构。
    
    存储策略：
    - FoA (Focus of Attention): 工作记忆，所有新记忆先进入此层
    - DA (Direct Access): 快速访问层，会话关键记忆进入此层
    - LTM (Long-Term Memory): 长期存储，所有记忆最终进入此层
    
    设计参考：
    - CogMem: 三层存储架构
    - MemMachine: 记忆类型分类
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
        if not storage_adapter:
            raise ValueError("storage_adapter cannot be None")
        if not memory_type_adapter:
            raise ValueError("memory_type_adapter cannot be None")
        
        self.storage_adapter = storage_adapter
        self.memory_type_adapter = memory_type_adapter
        
        ***REMOVED*** 缓存：记录记忆所在的层级（用于优化 update_memory）
        self._memory_layers: dict[str, Set[str]] = {}
        
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
            
        Raises:
            ValueError: 如果 memory 为 None
        """
        if not memory:
            raise ValueError("memory cannot be None")
        
        try:
            ***REMOVED*** 1. 分类记忆类型
            if not memory.memory_type:
                memory.memory_type = self.memory_type_adapter.classify(memory)
            
            layers_added: Set[str] = set()
            
            ***REMOVED*** 2. 添加到 FoA（工作记忆）
            if not self.storage_adapter.add_to_foa(memory):
                logger.warning(f"Failed to add memory {memory.id} to FoA")
                return False
            layers_added.add("foa")
            
            ***REMOVED*** 3. 如果关键，添加到 DA（快速访问）
            if context and self.storage_adapter.is_session_critical(memory, context):
                if not self.storage_adapter.add_to_da(memory):
                    logger.warning(f"Failed to add memory {memory.id} to DA")
                    ***REMOVED*** DA 失败不影响整体流程
                else:
                    layers_added.add("da")
            
            ***REMOVED*** 4. 添加到 LTM（长期存储）
            if not self.storage_adapter.add_to_ltm(memory, memory.memory_type):
                logger.error(f"Failed to add memory {memory.id} to LTM")
                ***REMOVED*** 回滚：移除已添加的层
                if "foa" in layers_added and hasattr(self.storage_adapter, 'remove_from_foa'):
                    self.storage_adapter.remove_from_foa(memory.id)
                if "da" in layers_added and hasattr(self.storage_adapter, 'remove_from_da'):
                    self.storage_adapter.remove_from_da(memory.id)
                return False
            layers_added.add("ltm")
            
            ***REMOVED*** 更新缓存
            self._memory_layers[memory.id] = layers_added
            
            logger.debug(f"Memory {memory.id} added to storage (type: {memory.memory_type}, layers: {layers_added})")
            return True
            
        except Exception as e:
            logger.error(f"Error adding memory {memory.id}: {e}", exc_info=True)
            return False
    
    def search_foa(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        在 FoA (Focus of Attention) 中搜索
        
        FoA 是工作记忆层，包含当前正在处理的记忆。
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for search_foa")
            return []
        
        try:
            memories = self.storage_adapter.search_foa(query, top_k)
            return [
                RetrievalResult(
                    memory=m,
                    score=1.0,  ***REMOVED*** FoA 优先级最高
                    retrieval_method="foa",
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error searching FoA: {e}", exc_info=True)
            return []
    
    def search_da(self, query: str, context: Optional[Context] = None, top_k: int = 10) -> List[RetrievalResult]:
        """
        在 DA (Direct Access) 中搜索
        
        DA 是快速访问层，包含会话关键记忆。
        
        Args:
            query: 查询字符串
            context: 上下文信息（可选）
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for search_da")
            return []
        
        try:
            memories = self.storage_adapter.search_da(query, context or Context(), top_k)
            return [
                RetrievalResult(
                    memory=m,
                    score=0.9,  ***REMOVED*** DA 优先级较高
                    retrieval_method="da",
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error searching DA: {e}", exc_info=True)
            return []
    
    def search_ltm(self, query: str, top_k: int = 10) -> List[RetrievalResult]:
        """
        在 LTM (Long-Term Memory) 中搜索
        
        LTM 是长期存储层，包含所有历史记忆。
        
        Args:
            query: 查询字符串
            top_k: 返回结果数量
            
        Returns:
            检索结果列表
        """
        if not query or not query.strip():
            logger.warning("Empty query for search_ltm")
            return []
        
        try:
            memories = self.storage_adapter.search_ltm(query, top_k)
            return [
                RetrievalResult(
                    memory=m,
                    score=0.8,  ***REMOVED*** LTM 优先级较低
                    retrieval_method="ltm",
                )
                for m in memories
            ]
        except Exception as e:
            logger.error(f"Error searching LTM: {e}", exc_info=True)
            return []
    
    def update_memory(self, memory: Memory) -> bool:
        """
        更新记忆
        
        实现跨层更新逻辑：需要更新所有包含该记忆的层。
        使用缓存优化，避免搜索所有记忆。
        
        Args:
            memory: 要更新的记忆对象
            
        Returns:
            是否成功更新
            
        Raises:
            ValueError: 如果 memory 为 None
        """
        if not memory:
            raise ValueError("memory cannot be None")
        
        try:
            ***REMOVED*** 获取记忆所在的层级（优先使用缓存）
            layers = self._memory_layers.get(memory.id, set())
            
            ***REMOVED*** 如果缓存中没有，尝试从适配器获取（降级方案）
            if not layers:
                logger.debug(f"Memory {memory.id} not in cache, checking layers...")
                ***REMOVED*** 注意：这里不搜索所有记忆，而是假设记忆可能在所有层
                ***REMOVED*** 如果适配器支持直接查询，应该使用适配器的方法
                layers = {"foa", "da", "ltm"}  ***REMOVED*** 保守策略：更新所有层
            
            updated_layers: Set[str] = set()
            
            ***REMOVED*** 1. 更新 FoA（如果存在）
            if "foa" in layers:
                if hasattr(self.storage_adapter, 'update_in_foa'):
                    if self.storage_adapter.update_in_foa(memory):
                        updated_layers.add("foa")
                else:
                    ***REMOVED*** 回退方案：删除后重新添加
                    if hasattr(self.storage_adapter, 'remove_from_foa'):
                        self.storage_adapter.remove_from_foa(memory.id)
                    if self.storage_adapter.add_to_foa(memory):
                        updated_layers.add("foa")
                logger.debug(f"Memory {memory.id} updated in FoA")
            
            ***REMOVED*** 2. 更新 DA（如果存在）
            if "da" in layers:
                if hasattr(self.storage_adapter, 'update_in_da'):
                    if self.storage_adapter.update_in_da(memory):
                        updated_layers.add("da")
                else:
                    ***REMOVED*** 回退方案：删除后重新添加
                    if hasattr(self.storage_adapter, 'remove_from_da'):
                        self.storage_adapter.remove_from_da(memory.id)
                    if self.storage_adapter.add_to_da(memory):
                        updated_layers.add("da")
                logger.debug(f"Memory {memory.id} updated in DA")
            
            ***REMOVED*** 3. 更新 LTM（总是需要更新）
            if hasattr(self.storage_adapter, 'update_in_ltm'):
                if self.storage_adapter.update_in_ltm(memory, memory.memory_type):
                    updated_layers.add("ltm")
            else:
                ***REMOVED*** 回退方案：删除后重新添加
                if hasattr(self.storage_adapter, 'remove_from_ltm'):
                    self.storage_adapter.remove_from_ltm(memory.id)
                if self.storage_adapter.add_to_ltm(memory, memory.memory_type):
                    updated_layers.add("ltm")
            logger.debug(f"Memory {memory.id} updated in LTM")
            
            ***REMOVED*** 更新缓存
            self._memory_layers[memory.id] = updated_layers
            
            logger.debug(f"Memory {memory.id} updated in storage (layers: {updated_layers})")
            return True
            
        except Exception as e:
            logger.error(f"Error updating memory {memory.id}: {e}", exc_info=True)
            return False
    
    def cleanup(self, max_age_hours: int = 24) -> int:
        """
        清理旧记忆（防止内存泄漏）
        
        清理超过指定时间的旧记忆，主要用于 FoA 和 DA 层。
        LTM 层通常不清理，作为长期存储。
        
        Args:
            max_age_hours: 最大保留时间（小时），默认 24 小时
            
        Returns:
            清理的记忆数量
        """
        if max_age_hours <= 0:
            logger.warning(f"Invalid max_age_hours: {max_age_hours}, using default 24")
            max_age_hours = 24
        
        try:
            if hasattr(self.storage_adapter, 'cleanup_old_memories'):
                cleaned_count = self.storage_adapter.cleanup_old_memories(max_age_hours)
                logger.info(f"Cleaned up {cleaned_count} old memories (max_age: {max_age_hours}h)")
                
                ***REMOVED*** 清理缓存中被删除的记忆
                ***REMOVED*** 注意：这里无法精确知道哪些记忆被删除，所以不清除缓存
                ***REMOVED*** 缓存会在下次访问时自动更新
                
                return cleaned_count
            else:
                logger.warning("Storage adapter does not support cleanup_old_memories")
                return 0
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            return 0
    
    def get_memory_layers(self, memory_id: str) -> Set[str]:
        """
        获取记忆所在的层级
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            记忆所在的层级集合（foa, da, ltm）
        """
        return self._memory_layers.get(memory_id, set())
    
    def clear_cache(self):
        """
        清除缓存
        
        用于在需要时手动清除层级缓存
        """
        self._memory_layers.clear()
        logger.debug("Memory layers cache cleared")
