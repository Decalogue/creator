"""
动态 Context 路由器（Context Router）
环境感知 Agent，根据用户行为预测并预加载上下文

核心功能：
- 注意力焦点预测：根据光标位置、输入速率、修改频率
- 预调度机制：提前加载相关联的记忆块
- 高速缓存（Cache）：实现零延迟的上下文补全
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import time

from .semantic_mesh_memory import SemanticMeshMemory, Entity

logger = logging.getLogger(__name__)


class FocusType(Enum):
    """注意力焦点类型"""
    CHARACTER_DIALOGUE = "character_dialogue"  ***REMOVED*** 角色对话
    DESCRIPTION = "description"  ***REMOVED*** 描写
    PLOT_DEVELOPMENT = "plot_development"  ***REMOVED*** 情节发展
    SETTING = "setting"  ***REMOVED*** 设定
    UNKNOWN = "unknown"  ***REMOVED*** 未知


@dataclass
class UserBehavior:
    """用户行为数据"""
    cursor_position: int = 0
    input_rate: float = 0.0  ***REMOVED*** 字符/秒
    modification_frequency: float = 0.0  ***REMOVED*** 修改次数/分钟
    pause_duration: float = 0.0  ***REMOVED*** 停顿时长（秒）
    recent_changes: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ContextCache:
    """上下文缓存"""
    entity_id: str
    context: Dict[str, Any]
    cached_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    last_accessed: str = field(default_factory=lambda: datetime.now().isoformat())


class ContextRouter:
    """
    动态上下文路由器
    
    根据用户行为预测注意力焦点，并预加载相关上下文
    """
    
    def __init__(
        self,
        semantic_mesh: SemanticMeshMemory,
        cache_size: int = 100,
        preload_threshold: float = 0.5  ***REMOVED*** 预加载阈值
    ):
        """
        初始化上下文路由器
        
        Args:
            semantic_mesh: 语义网格记忆系统
            cache_size: 缓存大小
            preload_threshold: 预加载阈值（预测置信度）
        """
        self.semantic_mesh = semantic_mesh
        self.cache_size = cache_size
        self.preload_threshold = preload_threshold
        
        ***REMOVED*** 上下文缓存
        self.context_cache: Dict[str, ContextCache] = {}
        
        ***REMOVED*** 用户行为历史
        self.behavior_history: List[UserBehavior] = []
        
        ***REMOVED*** 预加载任务队列
        self.preload_queue: List[str] = []  ***REMOVED*** 实体 ID 列表
        
        ***REMOVED*** 回调函数（当上下文准备好时调用）
        self.on_context_ready: Optional[Callable[[str, Dict[str, Any]], None]] = None
    
    def update_user_behavior(self, behavior: UserBehavior) -> None:
        """
        更新用户行为数据
        
        Args:
            behavior: 用户行为数据
        """
        self.behavior_history.append(behavior)
        
        ***REMOVED*** 只保留最近的行为历史（如最近1小时）
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.behavior_history = [
            b for b in self.behavior_history
            if datetime.fromisoformat(b.timestamp) > cutoff_time
        ]
        
        ***REMOVED*** 分析行为并预测焦点
        self._analyze_and_predict()
    
    def _analyze_and_predict(self) -> None:
        """分析用户行为并预测注意力焦点"""
        if not self.behavior_history:
            return
        
        recent_behavior = self.behavior_history[-10:]  ***REMOVED*** 最近10次行为
        
        ***REMOVED*** 计算平均输入速率
        avg_input_rate = sum(b.input_rate for b in recent_behavior) / len(recent_behavior)
        
        ***REMOVED*** 检测停顿
        if recent_behavior:
            last_behavior = recent_behavior[-1]
            if last_behavior.pause_duration > 0.5:  ***REMOVED*** 停顿超过500ms
                ***REMOVED*** 触发预加载
                self._trigger_preload(last_behavior)
        
        ***REMOVED*** 预测焦点类型
        focus_type = self._predict_focus_type(recent_behavior)
        
        logger.debug(f"Predicted focus type: {focus_type.value}")
    
    def _predict_focus_type(self, behaviors: List[UserBehavior]) -> FocusType:
        """
        预测注意力焦点类型
        
        Args:
            behaviors: 用户行为列表
        
        Returns:
            预测的焦点类型
        """
        ***REMOVED*** 简化实现：基于最近修改的内容
        if not behaviors:
            return FocusType.UNKNOWN
        
        ***REMOVED*** 分析最近修改的内容关键词
        recent_changes = []
        for b in behaviors[-5:]:  ***REMOVED*** 最近5次行为
            recent_changes.extend(b.recent_changes)
        
        ***REMOVED*** 简单的关键词匹配（实际应使用更智能的方法）
        change_text = " ".join(recent_changes).lower()
        
        if any(keyword in change_text for keyword in ["说", "道", "问", "答"]):
            return FocusType.CHARACTER_DIALOGUE
        elif any(keyword in change_text for keyword in ["天空", "云", "风", "景色"]):
            return FocusType.DESCRIPTION
        elif any(keyword in change_text for keyword in ["突然", "然后", "接着"]):
            return FocusType.PLOT_DEVELOPMENT
        else:
            return FocusType.UNKNOWN
    
    def _trigger_preload(self, behavior: UserBehavior) -> None:
        """
        触发预加载
        
        Args:
            behavior: 用户行为数据
        """
        ***REMOVED*** 根据当前光标位置和最近修改，预测可能需要的实体
        ***REMOVED*** 这里是一个简化实现
        
        ***REMOVED*** 假设我们可以从行为中提取实体 ID
        ***REMOVED*** 实际应该使用更智能的方法
        
        ***REMOVED*** 添加到预加载队列
        ***REMOVED*** self.preload_queue.append(entity_id)
        
        pass
    
    def preload_context(self, entity_id: str, agent_type: str = "general") -> Dict[str, Any]:
        """
        预加载上下文
        
        Args:
            entity_id: 实体 ID
            agent_type: Agent 类型
        
        Returns:
            上下文字典
        """
        ***REMOVED*** 检查缓存
        cache_key = f"{entity_id}:{agent_type}"
        if cache_key in self.context_cache:
            cache = self.context_cache[cache_key]
            cache.access_count += 1
            cache.last_accessed = datetime.now().isoformat()
            logger.debug(f"Context cache hit: {cache_key}")
            return cache.context
        
        ***REMOVED*** 从语义网格获取上下文
        context = self.semantic_mesh.get_context_for_agent(entity_id, agent_type)
        
        ***REMOVED*** 存入缓存
        if len(self.context_cache) >= self.cache_size:
            ***REMOVED*** 移除最久未访问的缓存
            oldest_key = min(
                self.context_cache.keys(),
                key=lambda k: self.context_cache[k].last_accessed
            )
            del self.context_cache[oldest_key]
        
        self.context_cache[cache_key] = ContextCache(
            entity_id=entity_id,
            context=context
        )
        
        logger.debug(f"Context preloaded: {cache_key}")
        
        return context
    
    def get_context_for_agent(
        self,
        entity_id: str,
        agent_type: str = "general",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        为 Agent 获取上下文
        
        Args:
            entity_id: 实体 ID
            agent_type: Agent 类型
            use_cache: 是否使用缓存
        
        Returns:
            上下文字典
        """
        if use_cache:
            return self.preload_context(entity_id, agent_type)
        else:
            return self.semantic_mesh.get_context_for_agent(entity_id, agent_type)
    
    def register_context_ready_callback(
        self,
        callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        注册上下文准备就绪回调
        
        Args:
            callback: 回调函数（entity_id, context）
        """
        self.on_context_ready = callback
