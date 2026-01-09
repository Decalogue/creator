***REMOVED***!/usr/bin/env python3
"""
批量重新索引已有记忆到Qdrant

将Neo4j中所有记忆的向量重新存储到Qdrant，并建立记忆关联
"""

import sys
import os
from pathlib import Path

***REMOVED*** 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem import UniMem
from py2neo import Graph
from unimem.memory_types import Memory, MemoryType, MemoryLayer
from datetime import datetime
import json

def reindex_all_memories():
    """重新索引所有记忆到Qdrant"""
    print("="*70)
    print("批量重新索引记忆到Qdrant")
    print("="*70)
    
    ***REMOVED*** 连接Neo4j
    graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')
    
    ***REMOVED*** 创建UniMem实例
    config = {
        "storage": {
            "foa_backend": "redis",
            "da_backend": "redis",
            "ltm_backend": "neo4j",
        },
        "graph": {
            "neo4j_uri": "bolt://localhost:7680",
            "neo4j_user": "neo4j",
            "neo4j_password": "seeme_db",
        },
        "network": {
            "qdrant_host": "localhost",
            "qdrant_port": 6333,
        }
    }
    
    ***REMOVED*** 直接检查Qdrant连接（使用HTTP API避免客户端版本问题）
    try:
        import requests
        response = requests.get("http://localhost:6333/collections/unimem_memories", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'ok':
                result = data.get('result', {})
                config = result.get('config', {})
                params = config.get('params', {})
                vectors = params.get('vectors', {})
                dim = vectors.get('size', 384)
                print(f"✓ Qdrant可用，collection维度: {dim}\n")
            else:
                print(f"❌ Qdrant collection状态异常")
                return False
        else:
            print(f"❌ Qdrant HTTP错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Qdrant不可用: {e}")
        return False
    
    unimem = UniMem(config=config)
    
    ***REMOVED*** 确保embedding模型可用
    if not unimem.network_adapter.embedding_model:
        print("❌ Embedding模型不可用，无法进行重新索引")
        return False
    
    print("✓ Embedding模型可用，开始重新索引...\n")
    
    ***REMOVED*** 从Neo4j读取所有记忆
    query = """
    MATCH (m:Memory)
    RETURN m.id as id, m.content as content, m.source as source,
           m.memory_type as type, m.metadata as metadata,
           m.created_at as created_at, m.keywords as keywords,
           m.tags as tags, m.context as context
    ORDER BY m.created_at ASC
    """
    results = graph.run(query).data()
    
    print(f"找到 {len(results)} 条记忆需要重新索引\n")
    
    success_count = 0
    fail_count = 0
    
    for i, row in enumerate(results, 1):
        try:
            ***REMOVED*** 解析metadata
            metadata_str = row.get('metadata', '{}')
            if isinstance(metadata_str, str):
                try:
                    metadata = json.loads(metadata_str)
                except:
                    metadata = {}
            else:
                metadata = metadata_str or {}
            
            ***REMOVED*** 解析类型
            memory_type = None
            type_str = row.get('type', '')
            if type_str:
                try:
                    memory_type = MemoryType(type_str)
                except:
                    pass
            
            ***REMOVED*** 解析keywords和tags
            keywords = []
            if row.get('keywords'):
                kw_str = row['keywords']
                if isinstance(kw_str, str):
                    keywords = [k.strip() for k in kw_str.split(',') if k.strip()]
            
            tags = []
            if row.get('tags'):
                tag_str = row['tags']
                if isinstance(tag_str, str):
                    tags = [t.strip() for t in tag_str.split(',') if t.strip()]
            
            ***REMOVED*** 解析时间戳
            created_at_str = row.get('created_at', '')
            if created_at_str:
                try:
                    timestamp = datetime.fromisoformat(created_at_str.replace(' ', 'T'))
                except:
                    timestamp = datetime.now()
            else:
                timestamp = datetime.now()
            
            ***REMOVED*** 创建Memory对象
            memory = Memory(
                id=row['id'],
                content=row.get('content', '') or '',
                timestamp=timestamp,
                memory_type=memory_type,
                layer=MemoryLayer.LTM,
                keywords=keywords,
                tags=tags,
                context=row.get('context', ''),
                metadata=metadata
            )
            
            ***REMOVED*** 直接使用network_adapter的方法添加向量
            ***REMOVED*** 因为embedding_model可用，即使qdrant_client可能未初始化，我们也可以手动添加
            try:
                ***REMOVED*** 生成embedding
                embedding = unimem.network_adapter._get_embedding(memory.content)
                if embedding is None:
                    fail_count += 1
                    print(f"  [{i}/{len(results)}] ✗ {memory.id[:20]}... (无法生成embedding)")
                    continue
                
                ***REMOVED*** 直接使用Qdrant客户端添加
                from qdrant_client import QdrantClient
                import uuid as uuid_lib
                
                qdrant_client = QdrantClient(host="localhost", port=6333)
                
                ***REMOVED*** 处理ID - Qdrant需要字符串或整数ID
                ***REMOVED*** 使用memory.id的hash作为整数ID，或者使用字符串
                try:
                    ***REMOVED*** 尝试使用UUID的int表示（取前64位）
                    uuid_obj = uuid_lib.UUID(memory.id)
                    ***REMOVED*** 使用字符串ID（Qdrant支持字符串ID）
                    point_id = str(uuid_obj)
                except:
                    ***REMOVED*** 如果不是UUID格式，使用hash
                    import hashlib
                    hash_obj = hashlib.md5(memory.id.encode())
                    ***REMOVED*** 使用hash的前16位作为整数ID
                    point_id = int(hash_obj.hexdigest()[:16], 16)
                
                ***REMOVED*** 添加payload
                payload = {
                    "content": memory.content,
                    "context": memory.context or "",
                    "keywords": memory.keywords,
                    "tags": memory.tags,
                    "timestamp": memory.timestamp.isoformat(),
                    "memory_type": memory.memory_type.value if memory.memory_type else "",
                    "source": memory.metadata.get("source", "") if memory.metadata else "",
                }
                
                ***REMOVED*** 添加向量
                qdrant_client.upsert(
                    collection_name="unimem_memories",
                    points=[{
                        "id": point_id,
                        "vector": embedding,
                        "payload": payload
                    }]
                )
                
                success_count += 1
                print(f"  [{i}/{len(results)}] ✓ {memory.id[:20]}... ({memory.memory_type.value if memory.memory_type else 'None'})")
                
            except Exception as e:
                fail_count += 1
                print(f"  [{i}/{len(results)}] ✗ {memory.id[:20]}... (错误: {str(e)[:50]})")
                
        except Exception as e:
            fail_count += 1
            print(f"  [{i}/{len(results)}] ✗ 错误: {e}")
    
    print(f"\n" + "="*70)
    print(f"重新索引完成")
    print(f"  成功: {success_count}条")
    print(f"  失败: {fail_count}条")
    print("="*70)
    
    ***REMOVED*** 检查Qdrant中的向量数量
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(host="localhost", port=6333)
        collection_info = client.get_collection("unimem_memories")
        print(f"\nQdrant向量统计:")
        print(f"  向量数量: {collection_info.points_count}")
        print(f"  索引状态: {collection_info.status}")
    except Exception as e:
        print(f"\n无法查询Qdrant统计: {e}")
    
    ***REMOVED*** 现在尝试建立记忆关联
    print(f"\n开始建立记忆关联...")
    establish_memory_links(unimem, graph)
    
    return success_count > 0


def establish_memory_links(unimem, graph):
    """建立记忆间的关联"""
    ***REMOVED*** 获取所有记忆
    query = "MATCH (m:Memory) RETURN m.id as id ORDER BY m.created_at ASC"
    results = graph.run(query).data()
    
    memory_ids = [r['id'] for r in results]
    print(f"  需要处理的记忆数: {len(memory_ids)}")
    
    linked_count = 0
    for i, memory_id in enumerate(memory_ids, 1):
        try:
            ***REMOVED*** 从Neo4j获取记忆
            from unimem.neo4j import get_memory
            memory = get_memory(memory_id)
            
            if memory:
                ***REMOVED*** 生成链接
                links = unimem.network_adapter.generate_links(memory, top_k=5)
                if links:
                    memory.links = links
                    ***REMOVED*** 更新Neo4j中的记忆，建立关联
                    unimem.storage.update_memory(memory)
                    linked_count += len(links)
                    print(f"  [{i}/{len(memory_ids)}] {memory_id[:20]}... -> {len(links)}个链接")
                    
        except Exception as e:
            print(f"  [{i}/{len(memory_ids)}] 处理失败: {e}")
    
    print(f"\n  建立关联完成，共建立 {linked_count} 个链接")
    
    ***REMOVED*** 检查Neo4j中的关联数
    relation_query = "MATCH ()-[r:RELATED_TO]->() RETURN count(r) as count"
    relation_result = graph.run(relation_query).data()
    total_relations = relation_result[0]['count'] if relation_result else 0
    print(f"  Neo4j中的总关联数: {total_relations}")


if __name__ == "__main__":
    success = reindex_all_memories()
    sys.exit(0 if success else 1)
