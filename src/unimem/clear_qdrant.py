"""
清空 Qdrant collection 的脚本
"""

***REMOVED*** 注意：types.py 已重命名为 memory_types.py，不再与标准库冲突

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_collection(collection_name: str, qdrant_host: str = "localhost", qdrant_port: int = 6333):
    """
    清空指定的 Qdrant collection
    
    Args:
        collection_name: collection 名称
        qdrant_host: Qdrant 主机地址
        qdrant_port: Qdrant 端口
    """
    try:
        client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        ***REMOVED*** 检查 collection 是否存在
        collections = client.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if collection_name not in collection_names:
            logger.info(f"Collection '{collection_name}' 不存在，无需清空")
            return
        
        ***REMOVED*** 删除 collection
        logger.info(f"正在删除 collection: {collection_name}")
        client.delete_collection(collection_name)
        logger.info(f"✅ Collection '{collection_name}' 已删除")
        
        ***REMOVED*** 重新创建 collection（使用新的模型配置）
        logger.info(f"正在重新创建 collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=384,  ***REMOVED*** multilingual-e5-small 的维度
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"✅ Collection '{collection_name}' 已重新创建")
        
    except Exception as e:
        logger.error(f"❌ 清空 collection 失败: {e}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="清空 Qdrant collection")
    parser.add_argument("--collection", "-c", default="unimem_memories", help="Collection 名称")
    parser.add_argument("--host", default="localhost", help="Qdrant 主机地址")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant 端口")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print(f"清空 Qdrant Collection: {args.collection}")
    print(f"Qdrant 地址: {args.host}:{args.port}")
    print("=" * 60)
    
    clear_collection(args.collection, args.host, args.port)
    
    print("\n✅ 完成！现在可以使用新的 embedding 模型重新索引数据了。")

