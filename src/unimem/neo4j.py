"""
UniMem Neo4j 图数据库操作

提供与 UniMem 相关的 Neo4j 操作函数：
- 实体（Entity）的 CRUD 操作
- 关系（Relation）的 CRUD 操作
- 记忆节点的操作
- 图查询和检索
"""

import time
import logging
from typing import List, Optional, Dict, Any, Tuple
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher

from .types import Entity, Relation, Memory, MemoryType

logger = logging.getLogger(__name__)

***REMOVED*** 数据库设置
graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')
node_matcher = NodeMatcher(graph)
relationship_matcher = RelationshipMatcher(graph)


def get_current_time(format_string="%Y-%m-%d-%H-%M-%S"):
    """获取当前时间字符串"""
    return time.strftime(format_string, time.localtime())


***REMOVED*** ==================== 实体操作 ====================

def create_entity(entity: Entity) -> bool:
    """
    创建实体节点
    
    Args:
        entity: Entity 对象
        
    Returns:
        是否成功创建
    """
    try:
        ***REMOVED*** 检查是否已存在
        existing = node_matcher.match("Entity", id=entity.id).first()
        if existing:
            logger.warning(f"Entity {entity.id} already exists, updating instead")
            return update_entity(entity)
        
        ***REMOVED*** 创建新节点
        node = Node(
            "Entity",
            id=entity.id,
            name=entity.name,
            entity_type=entity.entity_type,
            description=entity.description,
            retrieval_key=entity.retrieval_key,
            retrieval_value=entity.retrieval_value,
            created_at=get_current_time()
        )
        graph.create(node)
        logger.debug(f"Created entity: {entity.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to create entity {entity.id}: {e}", exc_info=True)
        return False


def get_entity(entity_id: str) -> Optional[Entity]:
    """
    获取实体节点
    
    Args:
        entity_id: 实体ID
        
    Returns:
        Entity 对象，如果不存在则返回 None
    """
    try:
        node = node_matcher.match("Entity", id=entity_id).first()
        if not node:
            return None
        
        ***REMOVED*** 获取邻居节点
        neighbors = []
        for rel in graph.match((node, None)):
            neighbors.append(rel.end_node["id"])
        
        entity = Entity(
            id=node["id"],
            name=node.get("name", ""),
            entity_type=node.get("entity_type", ""),
            description=node.get("description", ""),
            retrieval_key=node.get("retrieval_key", ""),
            retrieval_value=node.get("retrieval_value", ""),
            neighbors=neighbors
        )
        return entity
    except Exception as e:
        logger.error(f"Failed to get entity {entity_id}: {e}", exc_info=True)
        return None


def update_entity(entity: Entity) -> bool:
    """
    更新实体节点
    
    Args:
        entity: Entity 对象
        
    Returns:
        是否成功更新
    """
    try:
        node = node_matcher.match("Entity", id=entity.id).first()
        if not node:
            logger.warning(f"Entity {entity.id} not found, creating instead")
            return create_entity(entity)
        
        ***REMOVED*** 更新属性
        node["name"] = entity.name
        node["entity_type"] = entity.entity_type
        node["description"] = entity.description
        node["retrieval_key"] = entity.retrieval_key
        node["retrieval_value"] = entity.retrieval_value
        node["updated_at"] = get_current_time()
        
        graph.push(node)
        logger.debug(f"Updated entity: {entity.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update entity {entity.id}: {e}", exc_info=True)
        return False


def delete_entity(entity_id: str) -> bool:
    """
    删除实体节点
    
    Args:
        entity_id: 实体ID
        
    Returns:
        是否成功删除
    """
    try:
        node = node_matcher.match("Entity", id=entity_id).first()
        if not node:
            logger.warning(f"Entity {entity_id} not found")
            return False
        
        ***REMOVED*** 删除节点及其所有关系
        graph.delete(node)
        logger.debug(f"Deleted entity: {entity_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete entity {entity_id}: {e}", exc_info=True)
        return False


def find_entities_by_type(entity_type: str, limit: int = 100) -> List[Entity]:
    """
    根据类型查找实体
    
    Args:
        entity_type: 实体类型
        limit: 返回数量限制
        
    Returns:
        实体列表
    """
    try:
        nodes = node_matcher.match("Entity", entity_type=entity_type).limit(limit)
        entities = []
        for node in nodes:
            entity = Entity(
                id=node["id"],
                name=node.get("name", ""),
                entity_type=node.get("entity_type", ""),
                description=node.get("description", ""),
                retrieval_key=node.get("retrieval_key", ""),
                retrieval_value=node.get("retrieval_value", ""),
                neighbors=[]
            )
            entities.append(entity)
        return entities
    except Exception as e:
        logger.error(f"Failed to find entities by type {entity_type}: {e}", exc_info=True)
        return []


***REMOVED*** ==================== 关系操作 ====================

def create_relation(relation: Relation) -> bool:
    """
    创建关系边
    
    Args:
        relation: Relation 对象
        
    Returns:
        是否成功创建
    """
    try:
        ***REMOVED*** 获取源节点和目标节点
        source_node = node_matcher.match("Entity", id=relation.source).first()
        target_node = node_matcher.match("Entity", id=relation.target).first()
        
        if not source_node or not target_node:
            logger.error(f"Source or target node not found for relation {relation.source} -> {relation.target}")
            return False
        
        ***REMOVED*** 检查关系是否已存在
        existing = relationship_matcher.match((source_node, target_node)).first()
        if existing:
            logger.warning(f"Relation {relation.source} -> {relation.target} already exists, updating instead")
            return update_relation(relation)
        
        ***REMOVED*** 创建关系
        rel = Relationship(
            source_node,
            "RELATED_TO",
            target_node,
            description=relation.description,
            keywords=",".join(relation.keywords) if relation.keywords else "",
            retrieval_key=relation.retrieval_key,
            retrieval_value=relation.retrieval_value,
            created_at=get_current_time()
        )
        graph.create(rel)
        logger.debug(f"Created relation: {relation.source} -> {relation.target}")
        return True
    except Exception as e:
        logger.error(f"Failed to create relation {relation.source} -> {relation.target}: {e}", exc_info=True)
        return False


def get_relation(source_id: str, target_id: str) -> Optional[Relation]:
    """
    获取关系
    
    Args:
        source_id: 源实体ID
        target_id: 目标实体ID
        
    Returns:
        Relation 对象，如果不存在则返回 None
    """
    try:
        source_node = node_matcher.match("Entity", id=source_id).first()
        target_node = node_matcher.match("Entity", id=target_id).first()
        
        if not source_node or not target_node:
            return None
        
        rel = relationship_matcher.match((source_node, target_node)).first()
        if not rel:
            return None
        
        keywords_str = rel.get("keywords", "")
        keywords = keywords_str.split(",") if keywords_str else []
        
        relation = Relation(
            source=source_id,
            target=target_id,
            keywords=keywords,
            description=rel.get("description", ""),
            retrieval_key=rel.get("retrieval_key", ""),
            retrieval_value=rel.get("retrieval_value", "")
        )
        return relation
    except Exception as e:
        logger.error(f"Failed to get relation {source_id} -> {target_id}: {e}", exc_info=True)
        return None


def update_relation(relation: Relation) -> bool:
    """
    更新关系
    
    Args:
        relation: Relation 对象
        
    Returns:
        是否成功更新
    """
    try:
        source_node = node_matcher.match("Entity", id=relation.source).first()
        target_node = node_matcher.match("Entity", id=relation.target).first()
        
        if not source_node or not target_node:
            logger.error(f"Source or target node not found for relation {relation.source} -> {relation.target}")
            return False
        
        rel = relationship_matcher.match((source_node, target_node)).first()
        if not rel:
            logger.warning(f"Relation {relation.source} -> {relation.target} not found, creating instead")
            return create_relation(relation)
        
        ***REMOVED*** 更新属性
        rel["description"] = relation.description
        rel["keywords"] = ",".join(relation.keywords) if relation.keywords else ""
        rel["retrieval_key"] = relation.retrieval_key
        rel["retrieval_value"] = relation.retrieval_value
        rel["updated_at"] = get_current_time()
        
        graph.push(rel)
        logger.debug(f"Updated relation: {relation.source} -> {relation.target}")
        return True
    except Exception as e:
        logger.error(f"Failed to update relation {relation.source} -> {relation.target}: {e}", exc_info=True)
        return False


def delete_relation(source_id: str, target_id: str) -> bool:
    """
    删除关系
    
    Args:
        source_id: 源实体ID
        target_id: 目标实体ID
        
    Returns:
        是否成功删除
    """
    try:
        source_node = node_matcher.match("Entity", id=source_id).first()
        target_node = node_matcher.match("Entity", id=target_id).first()
        
        if not source_node or not target_node:
            logger.warning(f"Source or target node not found for relation {source_id} -> {target_id}")
            return False
        
        rel = relationship_matcher.match((source_node, target_node)).first()
        if not rel:
            logger.warning(f"Relation {source_id} -> {target_id} not found")
            return False
        
        graph.delete(rel)
        logger.debug(f"Deleted relation: {source_id} -> {target_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete relation {source_id} -> {target_id}: {e}", exc_info=True)
        return False


def get_entity_relations(entity_id: str, direction: str = "both") -> List[Relation]:
    """
    获取实体的所有关系
    
    Args:
        entity_id: 实体ID
        direction: 关系方向 ("outgoing", "incoming", "both")
        
    Returns:
        关系列表
    """
    try:
        node = node_matcher.match("Entity", id=entity_id).first()
        if not node:
            return []
        
        relations = []
        
        if direction in ("outgoing", "both"):
            for rel in graph.match((node, None)):
                keywords_str = rel.get("keywords", "")
                keywords = keywords_str.split(",") if keywords_str else []
                relations.append(Relation(
                    source=entity_id,
                    target=rel.end_node["id"],
                    keywords=keywords,
                    description=rel.get("description", ""),
                    retrieval_key=rel.get("retrieval_key", ""),
                    retrieval_value=rel.get("retrieval_value", "")
                ))
        
        if direction in ("incoming", "both"):
            for rel in graph.match((None, node)):
                keywords_str = rel.get("keywords", "")
                keywords = keywords_str.split(",") if keywords_str else []
                relations.append(Relation(
                    source=rel.start_node["id"],
                    target=entity_id,
                    keywords=keywords,
                    description=rel.get("description", ""),
                    retrieval_key=rel.get("retrieval_key", ""),
                    retrieval_value=rel.get("retrieval_value", "")
                ))
        
        return relations
    except Exception as e:
        logger.error(f"Failed to get relations for entity {entity_id}: {e}", exc_info=True)
        return []


***REMOVED*** ==================== 批量操作 ====================

def create_entities_batch(entities: List[Entity]) -> int:
    """
    批量创建实体
    
    Args:
        entities: 实体列表
        
    Returns:
        成功创建的数量
    """
    success_count = 0
    for entity in entities:
        if create_entity(entity):
            success_count += 1
    logger.info(f"Created {success_count}/{len(entities)} entities")
    return success_count


def create_relations_batch(relations: List[Relation]) -> int:
    """
    批量创建关系
    
    Args:
        relations: 关系列表
        
    Returns:
        成功创建的数量
    """
    success_count = 0
    for relation in relations:
        if create_relation(relation):
            success_count += 1
    logger.info(f"Created {success_count}/{len(relations)} relations")
    return success_count


***REMOVED*** ==================== 图查询操作 ====================

def find_path_between_entities(source_id: str, target_id: str, max_depth: int = 3) -> List[List[str]]:
    """
    查找两个实体之间的路径
    
    Args:
        source_id: 源实体ID
        target_id: 目标实体ID
        max_depth: 最大路径深度
        
    Returns:
        路径列表（每条路径是实体ID列表）
    """
    try:
        query = f"""
        MATCH path = shortestPath((source:Entity {{id: '{source_id}'}})-[*..{max_depth}]-(target:Entity {{id: '{target_id}'}}))
        RETURN [node in nodes(path) | node.id] as path
        LIMIT 10
        """
        result = graph.run(query).data()
        paths = [record["path"] for record in result]
        return paths
    except Exception as e:
        logger.error(f"Failed to find path between {source_id} and {target_id}: {e}", exc_info=True)
        return []


def get_entity_neighbors(entity_id: str, depth: int = 1) -> List[Entity]:
    """
    获取实体的邻居节点（指定深度）
    
    Args:
        entity_id: 实体ID
        depth: 深度（1表示直接邻居）
        
    Returns:
        邻居实体列表
    """
    try:
        query = f"""
        MATCH (source:Entity {{id: '{entity_id}'}})-[*1..{depth}]-(neighbor:Entity)
        RETURN DISTINCT neighbor
        LIMIT 100
        """
        result = graph.run(query).data()
        neighbors = []
        for record in result:
            node = record["neighbor"]
            if node["id"] != entity_id:  ***REMOVED*** 排除自己
                entity = Entity(
                    id=node["id"],
                    name=node.get("name", ""),
                    entity_type=node.get("entity_type", ""),
                    description=node.get("description", ""),
                    retrieval_key=node.get("retrieval_key", ""),
                    retrieval_value=node.get("retrieval_value", ""),
                    neighbors=[]
                )
                neighbors.append(entity)
        return neighbors
    except Exception as e:
        logger.error(f"Failed to get neighbors for entity {entity_id}: {e}", exc_info=True)
        return []


def search_entities_by_text(text: str, limit: int = 10) -> List[Entity]:
    """
    通过文本搜索实体（在名称和描述中搜索）
    
    Args:
        text: 搜索文本
        limit: 返回数量限制
        
    Returns:
        实体列表
    """
    try:
        query = f"""
        MATCH (e:Entity)
        WHERE e.name CONTAINS '{text}' OR e.description CONTAINS '{text}'
        RETURN e
        LIMIT {limit}
        """
        result = graph.run(query).data()
        entities = []
        for record in result:
            node = record["e"]
            entity = Entity(
                id=node["id"],
                name=node.get("name", ""),
                entity_type=node.get("entity_type", ""),
                description=node.get("description", ""),
                retrieval_key=node.get("retrieval_key", ""),
                retrieval_value=node.get("retrieval_value", ""),
                neighbors=[]
            )
            entities.append(entity)
        return entities
    except Exception as e:
        logger.error(f"Failed to search entities by text '{text}': {e}", exc_info=True)
        return []


***REMOVED*** ==================== Memory (LTM) 操作 ====================

def create_memory(memory: Memory) -> bool:
    """
    创建记忆节点（LTM - Long-Term Memory）
    
    Args:
        memory: Memory 对象
        
    Returns:
        是否成功创建
    """
    try:
        ***REMOVED*** 检查是否已存在
        existing = node_matcher.match("Memory", id=memory.id).first()
        if existing:
            logger.warning(f"Memory {memory.id} already exists, updating instead")
            return update_memory(memory)
        
        ***REMOVED*** 创建记忆节点
        node = Node(
            "Memory",
            id=memory.id,
            content=memory.content,
            timestamp=memory.timestamp.isoformat() if memory.timestamp else get_current_time(),
            memory_type=memory.memory_type.value if memory.memory_type else "",
            layer=memory.layer.value if memory.layer else "ltm",
            keywords=",".join(memory.keywords) if memory.keywords else "",
            tags=",".join(memory.tags) if memory.tags else "",
            context=memory.context or "",
            retrieval_count=memory.retrieval_count,
            last_accessed=memory.last_accessed.isoformat() if memory.last_accessed else "",
            metadata=str(memory.metadata) if memory.metadata else "{}",
            created_at=get_current_time()
        )
        graph.create(node)
        
        ***REMOVED*** 创建类型标签
        if memory.memory_type:
            type_value = memory.memory_type.value.upper()
            ***REMOVED*** 添加类型标签
            query = f"MATCH (m:Memory {{id: '{memory.id}'}}) SET m:{type_value} RETURN m"
            graph.run(query)
        
        ***REMOVED*** 关联实体
        if memory.entities:
            for entity_id in memory.entities:
                entity_node = node_matcher.match("Entity", id=entity_id).first()
                if entity_node:
                    rel = Relationship(node, "MENTIONS", entity_node)
                    graph.create(rel)
        
        ***REMOVED*** 关联其他记忆（links）
        if memory.links:
            for linked_memory_id in memory.links:
                linked_node = node_matcher.match("Memory", id=linked_memory_id).first()
                if linked_node:
                    rel = Relationship(node, "RELATED_TO", linked_node)
                    graph.create(rel)
        
        logger.debug(f"Created memory: {memory.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to create memory {memory.id}: {e}", exc_info=True)
        return False


def get_memory(memory_id: str) -> Optional[Memory]:
    """
    获取记忆节点
    
    Args:
        memory_id: 记忆ID
        
    Returns:
        Memory 对象，如果不存在则返回 None
    """
    try:
        node = node_matcher.match("Memory", id=memory_id).first()
        if not node:
            return None
        
        ***REMOVED*** 获取关联的实体
        entities = []
        for rel in graph.match((node, None), "MENTIONS"):
            entities.append(rel.end_node["id"])
        
        ***REMOVED*** 获取关联的记忆（links）
        links = set()
        for rel in graph.match((node, None), "RELATED_TO"):
            links.add(rel.end_node["id"])
        
        ***REMOVED*** 解析 keywords 和 tags
        keywords_str = node.get("keywords", "")
        keywords = keywords_str.split(",") if keywords_str else []
        
        tags_str = node.get("tags", "")
        tags = tags_str.split(",") if tags_str else []
        
        ***REMOVED*** 解析 metadata
        import json
        metadata_str = node.get("metadata", "{}")
        try:
            metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
        except:
            metadata = {}
        
        ***REMOVED*** 解析时间戳
        from datetime import datetime
        timestamp_str = node.get("timestamp", "")
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else datetime.now()
        
        last_accessed_str = node.get("last_accessed", "")
        last_accessed = datetime.fromisoformat(last_accessed_str) if last_accessed_str else None
        
        ***REMOVED*** 解析 memory_type
        memory_type_str = node.get("memory_type", "")
        memory_type = None
        if memory_type_str:
            try:
                memory_type = MemoryType(memory_type_str)
            except:
                pass
        
        ***REMOVED*** 解析 layer
        from .types import MemoryLayer
        layer_str = node.get("layer", "ltm")
        layer = None
        try:
            layer = MemoryLayer(layer_str)
        except:
            pass
        
        memory = Memory(
            id=node["id"],
            content=node.get("content", ""),
            timestamp=timestamp,
            memory_type=memory_type,
            layer=layer,
            keywords=keywords,
            tags=tags,
            context=node.get("context"),
            links=links,
            entities=entities,
            retrieval_count=node.get("retrieval_count", 0),
            last_accessed=last_accessed,
            metadata=metadata
        )
        return memory
    except Exception as e:
        logger.error(f"Failed to get memory {memory_id}: {e}", exc_info=True)
        return None


def update_memory(memory: Memory) -> bool:
    """
    更新记忆节点
    
    Args:
        memory: Memory 对象
        
    Returns:
        是否成功更新
    """
    try:
        node = node_matcher.match("Memory", id=memory.id).first()
        if not node:
            logger.warning(f"Memory {memory.id} not found, creating instead")
            return create_memory(memory)
        
        ***REMOVED*** 更新属性
        node["content"] = memory.content
        node["timestamp"] = memory.timestamp.isoformat() if memory.timestamp else get_current_time()
        node["memory_type"] = memory.memory_type.value if memory.memory_type else ""
        node["keywords"] = ",".join(memory.keywords) if memory.keywords else ""
        node["tags"] = ",".join(memory.tags) if memory.tags else ""
        node["context"] = memory.context or ""
        node["retrieval_count"] = memory.retrieval_count
        node["last_accessed"] = memory.last_accessed.isoformat() if memory.last_accessed else ""
        node["metadata"] = str(memory.metadata) if memory.metadata else "{}"
        
        graph.push(node)
        
        ***REMOVED*** 更新关联关系（删除旧关系，创建新关系）
        ***REMOVED*** 删除旧的实体关联
        for rel in graph.match((node, None), "MENTIONS"):
            graph.delete(rel)
        
        ***REMOVED*** 创建新的实体关联
        if memory.entities:
            for entity_id in memory.entities:
                entity_node = node_matcher.match("Entity", id=entity_id).first()
                if entity_node:
                    rel = Relationship(node, "MENTIONS", entity_node)
                    graph.create(rel)
        
        ***REMOVED*** 删除旧的记忆关联
        for rel in graph.match((node, None), "RELATED_TO"):
            graph.delete(rel)
        
        ***REMOVED*** 创建新的记忆关联
        if memory.links:
            for linked_memory_id in memory.links:
                linked_node = node_matcher.match("Memory", id=linked_memory_id).first()
                if linked_node:
                    rel = Relationship(node, "RELATED_TO", linked_node)
                    graph.create(rel)
        
        logger.debug(f"Updated memory: {memory.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to update memory {memory.id}: {e}", exc_info=True)
        return False


def delete_memory(memory_id: str) -> bool:
    """
    删除记忆节点
    
    Args:
        memory_id: 记忆ID
        
    Returns:
        是否成功删除
    """
    try:
        node = node_matcher.match("Memory", id=memory_id).first()
        if not node:
            logger.warning(f"Memory {memory_id} not found")
            return False
        
        ***REMOVED*** 删除所有关联关系
        for rel in graph.match((node, None)):
            graph.delete(rel)
        for rel in graph.match((None, node)):
            graph.delete(rel)
        
        ***REMOVED*** 删除节点
        graph.delete(node)
        
        logger.debug(f"Deleted memory: {memory_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete memory {memory_id}: {e}", exc_info=True)
        return False


def search_memories_by_type(memory_type: MemoryType, limit: int = 100) -> List[Memory]:
    """
    根据类型查询记忆
    
    Args:
        memory_type: 记忆类型
        limit: 返回数量限制
        
    Returns:
        记忆列表
    """
    try:
        type_value = memory_type.value
        query = f"""
        MATCH (m:Memory)
        WHERE m.memory_type = '{type_value}'
        RETURN m
        ORDER BY m.timestamp DESC
        LIMIT {limit}
        """
        result = graph.run(query).data()
        memories = []
        for record in result:
            memory = get_memory(record["m"]["id"])
            if memory:
                memories.append(memory)
        return memories
    except Exception as e:
        logger.error(f"Failed to search memories by type '{memory_type}': {e}", exc_info=True)
        return []


def search_memories_by_entity(entity_id: str, limit: int = 100) -> List[Memory]:
    """
    查询与实体相关的记忆
    
    Args:
        entity_id: 实体ID
        limit: 返回数量限制
        
    Returns:
        记忆列表
    """
    try:
        query = f"""
        MATCH (e:Entity {{id: '{entity_id}'}})<-[:MENTIONS]-(m:Memory)
        RETURN m
        ORDER BY m.timestamp DESC
        LIMIT {limit}
        """
        result = graph.run(query).data()
        memories = []
        for record in result:
            memory = get_memory(record["m"]["id"])
            if memory:
                memories.append(memory)
        return memories
    except Exception as e:
        logger.error(f"Failed to search memories by entity '{entity_id}': {e}", exc_info=True)
        return []


def search_memories_by_time_range(start_time: str, end_time: str, limit: int = 100) -> List[Memory]:
    """
    根据时间范围查询记忆
    
    Args:
        start_time: 开始时间（ISO 格式字符串）
        end_time: 结束时间（ISO 格式字符串）
        limit: 返回数量限制
        
    Returns:
        记忆列表
    """
    try:
        query = f"""
        MATCH (m:Memory)
        WHERE m.timestamp >= '{start_time}' AND m.timestamp <= '{end_time}'
        RETURN m
        ORDER BY m.timestamp DESC
        LIMIT {limit}
        """
        result = graph.run(query).data()
        memories = []
        for record in result:
            memory = get_memory(record["m"]["id"])
            if memory:
                memories.append(memory)
        return memories
    except Exception as e:
        logger.error(f"Failed to search memories by time range: {e}", exc_info=True)
        return []


def search_memories_by_text(text: str, limit: int = 100) -> List[Memory]:
    """
    通过文本搜索记忆（在内容中搜索）
    
    Args:
        text: 搜索文本
        limit: 返回数量限制
        
    Returns:
        记忆列表
    """
    try:
        query = f"""
        MATCH (m:Memory)
        WHERE m.content CONTAINS '{text}'
        RETURN m
        ORDER BY m.timestamp DESC
        LIMIT {limit}
        """
        result = graph.run(query).data()
        memories = []
        for record in result:
            memory = get_memory(record["m"]["id"])
            if memory:
                memories.append(memory)
        return memories
    except Exception as e:
        logger.error(f"Failed to search memories by text '{text}': {e}", exc_info=True)
        return []


def get_memory_relationships(memory_id: str, depth: int = 1) -> List[Dict[str, Any]]:
    """
    获取记忆的关系网络
    
    Args:
        memory_id: 记忆ID
        depth: 关系深度
        
    Returns:
        关系列表
    """
    try:
        query = f"""
        MATCH path = (m:Memory {{id: '{memory_id}'}})-[*1..{depth}]-(related)
        RETURN path
        LIMIT 50
        """
        result = graph.run(query).data()
        relationships = []
        for record in result:
            relationships.append(record["path"])
        return relationships
    except Exception as e:
        logger.error(f"Failed to get memory relationships for {memory_id}: {e}", exc_info=True)
        return []


def create_memory_indexes() -> bool:
    """
    创建 Memory 节点的索引（提升查询性能）
    
    Returns:
        是否成功创建索引
    """
    try:
        indexes = [
            ("Memory", "id"),
            ("Memory", "memory_type"),
            ("Memory", "timestamp"),
            ("Memory", "layer"),
        ]
        
        for label, property_name in indexes:
            try:
                query = f"CREATE INDEX IF NOT EXISTS FOR (m:{label}) ON (m.{property_name})"
                graph.run(query)
                logger.info(f"Created index on {label}.{property_name}")
            except Exception as e:
                logger.warning(f"Index on {label}.{property_name} may already exist: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to create memory indexes: {e}", exc_info=True)
        return False
