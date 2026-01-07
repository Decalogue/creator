"""
记忆效用追踪器

实现 ReMe 的效用追踪和自动清理机制
追踪每个记忆的 retrieval_count (f) 和 utility_score (u)
实现 φ_remove(E) 删除函数
"""

import logging
from typing import Dict, List, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field

from ..types import Memory

logger = logging.getLogger(__name__)


@dataclass
class UtilityMetrics:
    """记忆效用指标"""
    retrieval_count: int = 0  ***REMOVED*** 检索次数 f(E)
    utility_score: float = 0.0  ***REMOVED*** 效用分数 u(E)
    last_retrieved: Optional[datetime] = None
    last_utility_update: Optional[datetime] = None
    
    @property
    def utility_ratio(self) -> float:
        """效用比率 u(E)/f(E)"""
        if self.retrieval_count == 0:
            return 0.0
        return self.utility_score / self.retrieval_count
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "retrieval_count": self.retrieval_count,
            "utility_score": self.utility_score,
            "utility_ratio": self.utility_ratio,
            "last_retrieved": self.last_retrieved.isoformat() if self.last_retrieved else None,
            "last_utility_update": self.last_utility_update.isoformat() if self.last_utility_update else None,
        }


class UtilityTracker:
    """记忆效用追踪器（借鉴 ReMe 的效用机制）"""
    
    def __init__(self, alpha: int = 5, beta: float = 0.3):
        """
        初始化效用追踪器
        
        Args:
            alpha: 频率阈值（记忆被检索至少 alpha 次才考虑删除）
            beta: 效用阈值（u(E)/f(E) < beta 时删除）
        """
        self.alpha = alpha
        self.beta = beta
        
        ***REMOVED*** 内存中的效用指标（实际应该持久化到存储）
        self._metrics: Dict[str, UtilityMetrics] = {}
        
        logger.info(f"UtilityTracker initialized (alpha={alpha}, beta={beta})")
    
    def track_retrieval(self, memory_id: str) -> None:
        """追踪记忆检索"""
        if memory_id not in self._metrics:
            self._metrics[memory_id] = UtilityMetrics()
        
        self._metrics[memory_id].retrieval_count += 1
        self._metrics[memory_id].last_retrieved = datetime.now()
        
        logger.debug(f"Tracked retrieval for memory {memory_id}: count={self._metrics[memory_id].retrieval_count}")
    
    def update_utility(
        self,
        memory_id: str,
        task_success: bool,
        utility_increment: float = 1.0
    ) -> None:
        """
        更新记忆的效用
        
        Args:
            memory_id: 记忆ID
            task_success: 任务是否成功
            utility_increment: 成功时增加的效用值
        """
        if memory_id not in self._metrics:
            self._metrics[memory_id] = UtilityMetrics()
        
        metrics = self._metrics[memory_id]
        
        if task_success:
            metrics.utility_score += utility_increment
            logger.debug(
                f"Updated utility for memory {memory_id}: "
                f"utility={metrics.utility_score} (task succeeded)"
            )
        else:
            ***REMOVED*** 失败时不增加效用（甚至可以减少，但这里先保持简单）
            logger.debug(
                f"Memory {memory_id} used but task failed, "
                f"utility unchanged: {metrics.utility_score}"
            )
        
        metrics.last_utility_update = datetime.now()
    
    def should_remove(self, memory_id: str) -> bool:
        """
        判断记忆是否应该被删除（实现 φ_remove(E)）
        
        ReMe 的删除函数：
        φ_remove(E) = { 1, if f(E) ≥ α && u(E)/f(E) ≤ β
                      { 0, otherwise
        
        Args:
            memory_id: 记忆ID
            
        Returns:
            是否应该删除
        """
        if memory_id not in self._metrics:
            return False
        
        metrics = self._metrics[memory_id]
        f = metrics.retrieval_count
        u = metrics.utility_score
        
        ***REMOVED*** φ_remove(E) 逻辑
        if f >= self.alpha:
            utility_ratio = metrics.utility_ratio
            if utility_ratio <= self.beta:
                logger.info(
                    f"Memory {memory_id} should be removed: "
                    f"f(E)={f} >= {self.alpha}, "
                    f"u(E)/f(E)={utility_ratio:.3f} <= {self.beta}"
                )
                return True
        
        return False
    
    def get_metrics(self, memory_id: str) -> Optional[UtilityMetrics]:
        """获取记忆的效用指标"""
        return self._metrics.get(memory_id)
    
    def get_all_candidates_for_removal(self) -> List[str]:
        """
        获取所有应该被删除的记忆ID列表
        
        Returns:
            应该删除的记忆ID列表
        """
        candidates = []
        for memory_id, metrics in self._metrics.items():
            if self.should_remove(memory_id):
                candidates.append(memory_id)
        
        logger.info(f"Found {len(candidates)} memory candidates for removal")
        return candidates
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_memories = len(self._metrics)
        high_utility = sum(
            1 for m in self._metrics.values()
            if m.retrieval_count > 0 and m.utility_ratio > 0.5
        )
        ***REMOVED*** 计算低效用记忆（需要 memory_id，这里简化处理）
        low_utility = len(self.get_all_candidates_for_removal())
        
        return {
            "total_tracked": total_memories,
            "high_utility_count": high_utility,
            "low_utility_candidates": len(self.get_all_candidates_for_removal()),
            "average_retrieval_count": (
                sum(m.retrieval_count for m in self._metrics.values()) / max(total_memories, 1)
            ),
            "average_utility_ratio": (
                sum(m.utility_ratio for m in self._metrics.values()) / max(total_memories, 1)
            ),
        }
    
    def load_metrics(self, memory_id: str, metrics_data: Dict) -> None:
        """从持久化数据加载指标"""
        metrics = UtilityMetrics(
            retrieval_count=metrics_data.get("retrieval_count", 0),
            utility_score=metrics_data.get("utility_score", 0.0),
            last_retrieved=datetime.fromisoformat(metrics_data["last_retrieved"])
            if metrics_data.get("last_retrieved") else None,
            last_utility_update=datetime.fromisoformat(metrics_data["last_utility_update"])
            if metrics_data.get("last_utility_update") else None,
        )
        self._metrics[memory_id] = metrics
    
    def save_metrics(self, memory_id: str) -> Optional[Dict]:
        """保存指标到持久化存储"""
        if memory_id not in self._metrics:
            return None
        return self._metrics[memory_id].to_dict()


class UtilityBasedMemoryManager:
    """基于效用的记忆管理器（集成到 UniMem）"""
    
    def __init__(self, tracker: UtilityTracker):
        """
        初始化记忆管理器
        
        Args:
            tracker: 效用追踪器实例
        """
        self.tracker = tracker
        logger.info("UtilityBasedMemoryManager initialized")
    
    def should_remove_memory(self, memory: Memory) -> bool:
        """判断记忆是否应该被删除"""
        return self.tracker.should_remove(memory.id)
    
    def on_memory_retrieved(self, memory: Memory) -> None:
        """记忆被检索时的回调"""
        self.tracker.track_retrieval(memory.id)
        
        ***REMOVED*** 更新记忆的元数据
        if not memory.metadata:
            memory.metadata = {}
        memory.metadata["retrieval_count"] = self.tracker.get_metrics(memory.id).retrieval_count
        memory.metadata["last_retrieved"] = datetime.now().isoformat()
    
    def on_task_completed(
        self,
        memory_ids: List[str],
        task_success: bool,
        utility_increment: float = 1.0
    ) -> None:
        """
        任务完成时的回调
        
        Args:
            memory_ids: 任务中使用的记忆ID列表
            task_success: 任务是否成功
            utility_increment: 成功时的效用增量
        """
        for memory_id in memory_ids:
            self.tracker.update_utility(memory_id, task_success, utility_increment)
    
    def get_memories_to_remove(self) -> List[str]:
        """获取应该删除的记忆ID列表"""
        return self.tracker.get_all_candidates_for_removal()
    
    def cleanup_low_utility_memories(
        self,
        storage_manager,  ***REMOVED*** StorageManager 类型（避免循环导入）
        dry_run: bool = True
    ) -> Dict[str, int]:
        """
        清理低效记忆
        
        Args:
            storage_manager: 存储管理器（用于实际删除）
            dry_run: 是否为试运行（不实际删除）
            
        Returns:
            统计信息：{"removed": count, "candidates": count}
        """
        candidates = self.get_memories_to_remove()
        
        if dry_run:
            logger.info(f"Dry run: would remove {len(candidates)} memories")
            return {"removed": 0, "candidates": len(candidates)}
        
        ***REMOVED*** 实际删除
        removed_count = 0
        for memory_id in candidates:
            try:
                ***REMOVED*** 从存储中删除（需要实现 StorageManager 的删除方法）
                if hasattr(storage_manager, "remove_memory"):
                    if storage_manager.remove_memory(memory_id):
                        ***REMOVED*** 从追踪器中移除
                        if memory_id in self.tracker._metrics:
                            del self.tracker._metrics[memory_id]
                        removed_count += 1
                        logger.info(f"Removed low-utility memory: {memory_id}")
            except Exception as e:
                logger.error(f"Error removing memory {memory_id}: {e}", exc_info=True)
        
        logger.info(f"Cleanup completed: removed {removed_count}/{len(candidates)} memories")
        return {"removed": removed_count, "candidates": len(candidates)}

