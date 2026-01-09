"""
UniMem Neo4j 图数据库操作

提供与 UniMem 相关的 Neo4j 操作函数：
- 实体（Entity）的 CRUD 操作
- 关系（Relation）的 CRUD 操作
- 记忆节点的操作
- 图查询和检索

工业级特性：
- 连接池管理（Graph 连接池）
- 事务支持（Transaction）
- 重试机制（指数退避）
- 健康检查（ping）
- 线程安全（Graph 线程安全）
- 统一异常处理（使用适配器异常体系）
- 性能监控（操作耗时统计）
"""

import os
import json
import time
import logging
import threading
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

try:
    from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
    from py2neo.errors import ServiceUnavailable, ClientError, TransientError
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    Graph = None
    Node = None
    Relationship = None
    NodeMatcher = None
    RelationshipMatcher = None
    ServiceUnavailable = Exception
    ClientError = Exception
    TransientError = Exception

from .memory_types import Entity, Relation, Memory, MemoryType, MemoryLayer
from .adapters.base import (
    AdapterError,
    AdapterNotAvailableError,
    AdapterConfigurationError,
)

logger = logging.getLogger(__name__)

***REMOVED*** 全局变量（线程安全）
_graph: Optional[Any] = None
_node_matcher: Optional[Any] = None
_relationship_matcher: Optional[Any] = None
_graph_lock = threading.Lock()


def get_graph(
    uri: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    database: Optional[str] = None,
    max_connections: int = 50
) -> Optional[Any]:
    """
    获取 Neo4j Graph 实例（单例模式，线程安全）
    
    支持环境变量：NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE, NEO4J_MAX_CONNECTIONS
    """
    global _graph, _node_matcher, _relationship_matcher, graph, node_matcher, relationship_matcher
    
    if not NEO4J_AVAILABLE:
        raise AdapterNotAvailableError("Neo4j library (py2neo) not available", adapter_name="Neo4jClient")
    
    ***REMOVED*** 读取配置（简化版）
    uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7680")
    user = user or os.getenv("NEO4J_USER", "neo4j")
    password = password or os.getenv("NEO4J_PASSWORD", "seeme_db")  ***REMOVED*** 默认密码
    database = database or os.getenv("NEO4J_DATABASE", "neo4j")
    ***REMOVED*** py2neo 的 Graph 不支持 max_connections 参数，移除它
    if not uri.startswith(("bolt://", "neo4j://")):
        raise AdapterConfigurationError(f"Invalid Neo4j URI: {uri}", adapter_name="Neo4jClient")
    
    with _graph_lock:
        if _graph is None:
            try:
                ***REMOVED*** py2neo Graph 不支持 max_connections 参数
                _graph = Graph(uri, auth=(user, password), name=database)
                
                ***REMOVED*** 测试连接（带重试）
                for attempt in range(3):
                    try:
                        _graph.run("RETURN 1").data()
                        break
                    except Exception as e:
                        if attempt == 2:
                            raise ServiceUnavailable(f"Failed to connect after 3 attempts: {e}")
                        time.sleep(0.1 * (2 ** attempt))
                
                _node_matcher = NodeMatcher(_graph)
                _relationship_matcher = RelationshipMatcher(_graph)
                ***REMOVED*** 同时更新模块级别变量
                graph = _graph
                node_matcher = _node_matcher
                relationship_matcher = _relationship_matcher
                logger.info(f"Neo4j connected: {uri}/{database}")
            except (ServiceUnavailable, ClientError) as e:
                _graph = _node_matcher = _relationship_matcher = None
                raise AdapterNotAvailableError(f"Failed to connect to Neo4j: {e}", adapter_name="Neo4jClient", cause=e) from e
            except Exception as e:
                _graph = _node_matcher = _relationship_matcher = None
                raise AdapterError(f"Failed to initialize Neo4j: {e}", adapter_name="Neo4jClient", cause=e) from e
    
    return _graph


def _execute_with_retry(operation: callable, operation_name: str = "operation", max_retries: int = None) -> Any:
    """带重试的操作执行"""
    if max_retries is None:
        max_retries = _max_retries
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except (ServiceUnavailable, TransientError) as e:
            last_error = e
            if attempt < max_retries:
                wait_time = _retry_delay * (2 ** attempt)  ***REMOVED*** 指数退避
                logger.warning(f"{operation_name} failed (attempt {attempt + 1}/{max_retries + 1}): {e}, retrying in {wait_time:.3f}s...")
                time.sleep(wait_time)
            else:
                logger.error(f"{operation_name} failed after {max_retries + 1} attempts: {e}")
        except ClientError as e:
            ***REMOVED*** 客户端错误不重试
            logger.error(f"{operation_name} failed with client error: {e}")
            raise AdapterError(
                f"{operation_name} failed: {e}",
                adapter_name="Neo4jClient",
                cause=e
            ) from e
        except Exception as e:
            ***REMOVED*** 未知错误不重试
            logger.error(f"{operation_name} failed with unexpected error: {e}", exc_info=True)
            raise AdapterError(
                f"{operation_name} failed: {e}",
                adapter_name="Neo4jClient",
                cause=e
            ) from e
    
    if last_error:
        raise AdapterNotAvailableError(
            f"{operation_name} failed after retries: {last_error}",
            adapter_name="Neo4jClient",
            cause=last_error
        ) from last_error
    
    return None


def health_check() -> Dict[str, Any]:
    """
    健康检查（带连接状态和统计信息）
    
    Returns:
        健康状态字典
    """
    if not NEO4J_AVAILABLE:
        return {
            "available": False,
            "error": "Neo4j library not available",
            "timestamp": datetime.now().isoformat(),
        }
    
    try:
        graph = get_graph()
        if not graph:
            return {
                "available": False,
                "error": "Neo4j graph not available",
                "timestamp": datetime.now().isoformat(),
            }
        
        ***REMOVED*** 检查连接
        is_alive = _ping_graph(graph, max_retries=1)
        
        ***REMOVED*** 获取数据库信息
        try:
            db_info = graph.run("CALL db.info() YIELD name, version RETURN name, version").data()
        except Exception:
            db_info = []
        
        return {
            "available": is_alive,
            "status": "healthy" if is_alive else "unhealthy",
            "database": db_info[0] if db_info else {},
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "available": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


***REMOVED*** 模块级别的全局变量（延迟初始化）
def _ensure_initialized():
    """确保 Neo4j 连接已初始化"""
    global _graph, _node_matcher, _relationship_matcher, graph, node_matcher, relationship_matcher
    
    ***REMOVED*** 如果模块级别变量未初始化，或者全局变量未初始化，则初始化
    if _graph is None or _node_matcher is None or graph is None or node_matcher is None:
        try:
            ***REMOVED*** get_graph() 会初始化 _graph, _node_matcher, _relationship_matcher
            _graph = get_graph()
            if _graph is None:
                raise AdapterNotAvailableError("Failed to get Neo4j graph", adapter_name="Neo4jClient")
            ***REMOVED*** 确保 node_matcher 也被初始化（get_graph 应该已经初始化了，但为了安全再检查一次）
            if _node_matcher is None and _graph:
                _node_matcher = NodeMatcher(_graph)
                _relationship_matcher = RelationshipMatcher(_graph)
            ***REMOVED*** 更新模块级别变量（必须执行，即使 _graph 已经存在）
            graph = _graph
            node_matcher = _node_matcher
            relationship_matcher = _relationship_matcher
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j in _ensure_initialized: {e}")
            raise


***REMOVED*** 直接定义全局变量（简单方式）
graph: Optional[Any] = None
node_matcher: Optional[Any] = None
relationship_matcher: Optional[Any] = None


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
    _ensure_initialized()
    
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
    _ensure_initialized()
    
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
    _ensure_initialized()
    
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
    _ensure_initialized()
    
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
    _ensure_initialized()
    
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
        ***REMOVED*** 确保 Neo4j 连接已初始化
        _ensure_initialized()
        if not node_matcher:
            logger.error("Neo4j node_matcher not initialized")
            return False
        
        ***REMOVED*** 检查是否已存在
        existing = node_matcher.match("Memory", id=memory.id).first()
        if existing:
            logger.warning(f"Memory {memory.id} already exists, updating instead")
            return update_memory(memory)
        
        ***REMOVED*** 提取source字段（如果存在）
        source = ""
        if memory.metadata and isinstance(memory.metadata, dict):
            source = memory.metadata.get("source", "")
        
        ***REMOVED*** 提取reasoning和decision_trace字段（Context Graph增强）
        reasoning = memory.reasoning or ""
        decision_trace_json = ""
        if memory.decision_trace:
            import json
            decision_trace_json = json.dumps(memory.decision_trace, ensure_ascii=False)
        
        ***REMOVED*** 将metadata保存为JSON字符串（便于查询）
        import json
        metadata_json = json.dumps(memory.metadata, ensure_ascii=False) if memory.metadata else "{}"
        
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
            metadata=metadata_json,  ***REMOVED*** 保存为JSON字符串
            source=source,  ***REMOVED*** 提取source为独立属性
            reasoning=reasoning,  ***REMOVED*** 新增：决策理由
            decision_trace=decision_trace_json,  ***REMOVED*** 新增：决策痕迹
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
        ***REMOVED*** 确保 Neo4j 连接已初始化
        try:
            _ensure_initialized()
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
            return None
        
        if not node_matcher or not graph:
            logger.error("Neo4j node_matcher or graph not initialized")
            return None
        
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
        metadata_str = node.get("metadata", "{}")
        try:
            metadata = json.loads(metadata_str) if isinstance(metadata_str, str) else metadata_str
        except:
            metadata = {}
        
        ***REMOVED*** 解析时间戳
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
        layer_str = node.get("layer", "ltm")
        layer = None
        try:
            layer = MemoryLayer(layer_str)
        except:
            pass
        
        ***REMOVED*** 解析 reasoning 和 decision_trace（Context Graph增强）
        reasoning = node.get("reasoning") or None
        decision_trace = None
        decision_trace_str = node.get("decision_trace", "")
        if decision_trace_str:
            try:
                decision_trace = json.loads(decision_trace_str) if isinstance(decision_trace_str, str) else decision_trace_str
            except:
                decision_trace = None
        
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
            metadata=metadata,
            reasoning=reasoning,  ***REMOVED*** 新增：决策理由
            decision_trace=decision_trace,  ***REMOVED*** 新增：决策痕迹
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
        ***REMOVED*** 确保 Neo4j 连接已初始化
        try:
            _ensure_initialized()
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
            return False
        
        if not node_matcher or not graph:
            logger.error("Neo4j node_matcher or graph not initialized")
            return False
        
        node = node_matcher.match("Memory", id=memory.id).first()
        if not node:
            logger.warning(f"Memory {memory.id} not found, creating instead")
            return create_memory(memory)
        
        ***REMOVED*** 提取source字段（如果存在）
        source = ""
        if memory.metadata and isinstance(memory.metadata, dict):
            source = memory.metadata.get("source", "")
        
        ***REMOVED*** 提取reasoning和decision_trace字段（Context Graph增强）
        reasoning = memory.reasoning or ""
        decision_trace_json = ""
        if memory.decision_trace:
            decision_trace_json = json.dumps(memory.decision_trace, ensure_ascii=False)
        
        ***REMOVED*** 将metadata保存为JSON字符串（便于查询）
        metadata_json = json.dumps(memory.metadata, ensure_ascii=False) if memory.metadata else "{}"
        
        ***REMOVED*** 更新属性
        node["content"] = memory.content
        node["timestamp"] = memory.timestamp.isoformat() if memory.timestamp else get_current_time()
        node["memory_type"] = memory.memory_type.value if memory.memory_type else ""
        node["keywords"] = ",".join(memory.keywords) if memory.keywords else ""
        node["tags"] = ",".join(memory.tags) if memory.tags else ""
        node["context"] = memory.context or ""
        node["retrieval_count"] = memory.retrieval_count
        node["last_accessed"] = memory.last_accessed.isoformat() if memory.last_accessed else ""
        node["metadata"] = metadata_json  ***REMOVED*** 保存为JSON字符串
        node["source"] = source  ***REMOVED*** 更新source字段
        node["reasoning"] = reasoning  ***REMOVED*** 新增：更新决策理由
        node["decision_trace"] = decision_trace_json  ***REMOVED*** 新增：更新决策痕迹
        
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
        ***REMOVED*** 确保 Neo4j 连接已初始化
        try:
            _ensure_initialized()
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")
            return False
        
        if not node_matcher or not graph:
            logger.error("Neo4j node_matcher or graph not initialized")
            return False
        
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


def create_decision_event(
    memory_id: str,
    decision_trace: Dict[str, Any],
    reasoning: Optional[str] = None,
    related_entity_ids: Optional[List[str]] = None
) -> bool:
    """
    创建决策事件节点（Context Graph增强）
    
    决策事件节点用于记录决策的完整上下文，连接相关实体和记忆，形成决策图谱。
    
    Args:
        memory_id: 关联的记忆ID
        decision_trace: 决策痕迹字典
        reasoning: 决策理由（可选）
        related_entity_ids: 相关实体ID列表（可选）
        
    Returns:
        是否成功创建
    """
    try:
        _ensure_initialized()
        if not node_matcher or not graph:
            logger.error("Neo4j node_matcher or graph not initialized")
            return False
        
        ***REMOVED*** 查找记忆节点
        memory_node = node_matcher.match("Memory", id=memory_id).first()
        if not memory_node:
            logger.warning(f"Memory {memory_id} not found, cannot create decision event")
            return False
        
        ***REMOVED*** 创建决策事件节点
        event_id = f"decision_{memory_id}"
        
        ***REMOVED*** 检查是否已存在
        existing = node_matcher.match("DecisionEvent", id=event_id).first()
        if existing:
            logger.debug(f"Decision event {event_id} already exists, updating instead")
            return update_decision_event(event_id, decision_trace, reasoning, related_entity_ids)
        
        import json
        inputs_json = json.dumps(decision_trace.get("inputs", []), ensure_ascii=False)
        rules_json = json.dumps(decision_trace.get("rules_applied", []), ensure_ascii=False)
        exceptions_json = json.dumps(decision_trace.get("exceptions", []), ensure_ascii=False)
        approvals_json = json.dumps(decision_trace.get("approvals", []), ensure_ascii=False)
        
        event_node = Node(
            "DecisionEvent",
            id=event_id,
            memory_id=memory_id,
            inputs=inputs_json,
            rules_applied=rules_json,
            exceptions=exceptions_json,
            approvals=approvals_json,
            reasoning=reasoning or "",
            timestamp=decision_trace.get("timestamp", get_current_time()),
            operation_id=decision_trace.get("operation_id", ""),
            created_at=get_current_time()
        )
        
        graph.create(event_node)
        
        ***REMOVED*** 连接到Memory节点
        graph.create(Relationship(event_node, "TRACES", memory_node))
        
        ***REMOVED*** 连接到相关实体
        if related_entity_ids:
            for entity_id in related_entity_ids:
                entity_node = node_matcher.match("Entity", id=entity_id).first()
                if entity_node:
                    graph.create(Relationship(event_node, "INVOLVES", entity_node))
        
        logger.debug(f"Created decision event: {event_id} for memory {memory_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create decision event for memory {memory_id}: {e}", exc_info=True)
        return False


def update_decision_event(
    event_id: str,
    decision_trace: Dict[str, Any],
    reasoning: Optional[str] = None,
    related_entity_ids: Optional[List[str]] = None
) -> bool:
    """
    更新决策事件节点
    
    Args:
        event_id: 事件ID
        decision_trace: 决策痕迹字典
        reasoning: 决策理由（可选）
        related_entity_ids: 相关实体ID列表（可选）
        
    Returns:
        是否成功更新
    """
    try:
        _ensure_initialized()
        if not node_matcher or not graph:
            logger.error("Neo4j node_matcher or graph not initialized")
            return False
        
        event_node = node_matcher.match("DecisionEvent", id=event_id).first()
        if not event_node:
            logger.warning(f"Decision event {event_id} not found")
            return False
        
        import json
        event_node["inputs"] = json.dumps(decision_trace.get("inputs", []), ensure_ascii=False)
        event_node["rules_applied"] = json.dumps(decision_trace.get("rules_applied", []), ensure_ascii=False)
        event_node["exceptions"] = json.dumps(decision_trace.get("exceptions", []), ensure_ascii=False)
        event_node["approvals"] = json.dumps(decision_trace.get("approvals", []), ensure_ascii=False)
        if reasoning:
            event_node["reasoning"] = reasoning
        
        graph.push(event_node)
        
        ***REMOVED*** 更新实体关联
        if related_entity_ids:
            ***REMOVED*** 删除旧的实体关联
            for rel in graph.match((event_node, None), "INVOLVES"):
                graph.delete(rel)
            
            ***REMOVED*** 创建新的实体关联
            for entity_id in related_entity_ids:
                entity_node = node_matcher.match("Entity", id=entity_id).first()
                if entity_node:
                    graph.create(Relationship(event_node, "INVOLVES", entity_node))
        
        logger.debug(f"Updated decision event: {event_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update decision event {event_id}: {e}", exc_info=True)
        return False


def get_decision_events_for_memory(memory_id: str) -> List[Dict[str, Any]]:
    """
    获取记忆的所有决策事件
    
    Args:
        memory_id: 记忆ID
        
    Returns:
        决策事件列表
    """
    try:
        _ensure_initialized()
        if not graph:
            logger.error("Neo4j graph not initialized")
            return []
        
        query = """
        MATCH (de:DecisionEvent)-[:TRACES]->(m:Memory {id: $memory_id})
        RETURN de
        ORDER BY de.timestamp DESC
        """
        result = graph.run(query, memory_id=memory_id).data()
        
        events = []
        for record in result:
            de = record["de"]
            import json
            event = {
                "id": de.get("id"),
                "memory_id": de.get("memory_id"),
                "inputs": json.loads(de.get("inputs", "[]")) if de.get("inputs") else [],
                "rules_applied": json.loads(de.get("rules_applied", "[]")) if de.get("rules_applied") else [],
                "exceptions": json.loads(de.get("exceptions", "[]")) if de.get("exceptions") else [],
                "approvals": json.loads(de.get("approvals", "[]")) if de.get("approvals") else [],
                "reasoning": de.get("reasoning", ""),
                "timestamp": de.get("timestamp"),
            }
            events.append(event)
        
        return events
        
    except Exception as e:
        logger.error(f"Failed to get decision events for memory {memory_id}: {e}", exc_info=True)
        return []
