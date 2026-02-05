"""
订阅式记忆通知机制（Pub/Sub Memory）
上下文中心总线，Agent 订阅特定 Topic

核心功能：
- Topic 订阅：Agent 订阅感兴趣的语义主题
- 实时推送：当相关内容被创建/修改时，自动推送
- 冲突检测：自动检测设定冲突（OOC）
"""
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Topic(Enum):
    """订阅主题"""
    CHARACTER_DIALOGUE = "character_dialogue"  # 角色对话
    SETTING_DESCRIPTION = "setting_description"  # 设定描述
    PLOT_DEVELOPMENT = "plot_development"  # 情节发展
    WORLDVIEW = "worldview"  # 世界观
    STYLE = "style"  # 风格
    CONSISTENCY = "consistency"  # 一致性
    ALL = "all"  # 所有主题


@dataclass
class Subscription:
    """订阅信息"""
    agent_id: str
    topics: Set[Topic]
    callback: Callable[[str, Dict[str, Any]], None]  # (topic, data)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Message:
    """消息"""
    topic: Topic
    entity_id: str
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class PubSubMemoryBus:
    """
    订阅式记忆总线
    
    实现 Agent 间的实时通知机制
    """
    
    def __init__(self):
        """初始化记忆总线"""
        self.subscriptions: Dict[str, Subscription] = {}
        self.message_history: List[Message] = []
        self.max_history: int = 1000
    
    def subscribe(
        self,
        agent_id: str,
        topics: List[Topic],
        callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """
        订阅主题
        
        Args:
            agent_id: Agent ID
            topics: 订阅的主题列表
            callback: 回调函数（topic, data）
            
        Raises:
            ValueError: 如果参数无效
            TypeError: 如果 callback 不是可调用对象
        """
        if not agent_id or not isinstance(agent_id, str):
            raise ValueError("agent_id must be a non-empty string")
        
        if not topics or not isinstance(topics, list):
            raise ValueError("topics must be a non-empty list")
        
        if not callable(callback):
            raise TypeError("callback must be callable")
        
        subscription = Subscription(
            agent_id=agent_id,
            topics=set(topics),
            callback=callback
        )
        self.subscriptions[agent_id] = subscription
        logger.info(f"Agent {agent_id} subscribed to topics: {[t.value for t in topics]}")
    
    def unsubscribe(self, agent_id: str) -> None:
        """
        取消订阅
        
        Args:
            agent_id: Agent ID
        """
        if agent_id in self.subscriptions:
            del self.subscriptions[agent_id]
            logger.info(f"Agent {agent_id} unsubscribed")
    
    def publish(
        self,
        topic: Topic,
        entity_id: str,
        data: Dict[str, Any]
    ) -> int:
        """
        发布消息
        
        Args:
            topic: 主题
            entity_id: 实体 ID
            data: 数据字典
        
        Returns:
            通知的 Agent 数量
            
        Raises:
            ValueError: 如果参数无效
            TypeError: 如果 topic 不是 Topic 类型
        """
        if not isinstance(topic, Topic):
            raise TypeError(f"topic must be a Topic enum, got {type(topic)}")
        
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError("entity_id must be a non-empty string")
        
        if not isinstance(data, dict):
            raise ValueError("data must be a dictionary")
        
        message = Message(
            topic=topic,
            entity_id=entity_id,
            data=data
        )
        
        # 保存到历史
        self.message_history.append(message)
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
        
        # 通知订阅者
        notified_count = 0
        for agent_id, subscription in self.subscriptions.items():
            if Topic.ALL in subscription.topics or topic in subscription.topics:
                try:
                    subscription.callback(topic.value, data)
                    notified_count += 1
                    logger.debug(f"Notified agent {agent_id} about topic {topic.value}")
                except Exception as e:
                    logger.error(f"Error notifying agent {agent_id}: {e}")
        
        logger.info(f"Published message on topic {topic.value}, notified {notified_count} agents")
        
        return notified_count
    
    def get_message_history(
        self,
        topic: Optional[Topic] = None,
        limit: int = 100
    ) -> List[Message]:
        """
        获取消息历史
        
        Args:
            topic: 主题过滤（可选）
            limit: 最多返回的消息数
        
        Returns:
            消息列表
        """
        messages = self.message_history
        if topic:
            messages = [m for m in messages if m.topic == topic]
        
        return messages[-limit:]
    
    def detect_conflicts(
        self,
        entity_id: str,
        new_content: str,
        topic: Topic
    ) -> List[Dict[str, Any]]:
        """
        检测冲突
        
        当新内容发布时，检测是否与已有内容冲突。
        当前实现为简化版本，仅检测世界观冲突。
        
        TODO: 增强冲突检测逻辑
        - 支持更多主题类型的冲突检测
        - 使用语义相似度进行智能检测
        - 支持自定义冲突检测规则
        
        Args:
            entity_id: 实体 ID
            new_content: 新内容字符串
            topic: 主题
        
        Returns:
            冲突列表，每个冲突包含：
            - entity_id: 冲突的实体 ID
            - message: 冲突的消息数据
            - conflict_type: 冲突类型
        """
        if not entity_id or not isinstance(entity_id, str):
            raise ValueError("entity_id must be a non-empty string")
        
        if not isinstance(new_content, str):
            raise ValueError("new_content must be a string")
        
        if not isinstance(topic, Topic):
            raise TypeError(f"topic must be a Topic enum, got {type(topic)}")
        
        conflicts = []
        
        # 获取相关历史消息
        related_messages = self.get_message_history(topic=topic, limit=50)
        
        # 简化的冲突检测（实际应使用更智能的方法）
        # 例如：检测世界观冲突
        if topic == Topic.WORLDVIEW:
            # 检查是否有矛盾的世界观描述
            for msg in related_messages:
                if "contradicts" in msg.data.get("metadata", {}):
                    conflicts.append({
                        "entity_id": msg.entity_id,
                        "message": msg.data,
                        "conflict_type": "worldview_contradiction"
                    })
        
        return conflicts
