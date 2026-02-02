***REMOVED***!/usr/bin/env python3
"""
检查 UniMem 服务连接状态
检查 Redis、Neo4j、Qdrant 的连接状态

运行前请先激活 seeme 环境：
  conda activate seeme
  python unimem/scripts/check_connections.py
或：
  conda run -n seeme python unimem/scripts/check_connections.py
"""

import sys
import os
from pathlib import Path

***REMOVED*** 添加 src 目录到路径
src_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_dir))

import logging
from typing import Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_redis() -> Dict[str, Any]:
    """检查 Redis 连接"""
    try:
        import redis
        from unimem.redis import get_redis_client
        
        client = get_redis_client()
        if client:
            ***REMOVED*** 测试连接
            client.ping()
            info = client.info()
            return {
                "status": "✓ 已连接",
                "host": client.connection_pool.connection_kwargs.get('host', 'unknown'),
                "port": client.connection_pool.connection_kwargs.get('port', 'unknown'),
                "version": info.get('redis_version', 'unknown'),
                "connected_clients": info.get('connected_clients', 0),
            }
        else:
            return {
                "status": "✗ 未连接",
                "reason": "Redis 客户端不可用"
            }
    except ImportError:
        return {
            "status": "✗ 未安装",
            "reason": "redis 库未安装"
        }
    except Exception as e:
        return {
            "status": "✗ 连接失败",
            "reason": str(e)
        }


def check_neo4j() -> Dict[str, Any]:
    """检查 Neo4j 连接"""
    try:
        ***REMOVED*** 尝试使用 py2neo（UniMem 实际使用的库）
        try:
            from py2neo import Graph
            import os
            
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7680")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "seeme_db")
            database = os.getenv("NEO4J_DATABASE", "neo4j")
            
            graph = Graph(uri, auth=(user, password), name=database)
            
            ***REMOVED*** 测试连接
            result = graph.run("RETURN 1 as test").data()
            
            return {
                "status": "✓ 已连接",
                "uri": uri,
                "user": user,
                "database": database,
                "library": "py2neo",
            }
        except ImportError:
            ***REMOVED*** 回退到标准 neo4j 库
            from neo4j import GraphDatabase
            import os
            
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7680")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "seeme_db")
            
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                
                ***REMOVED*** 获取数据库信息
                server_info = driver.get_server_info()
                
                driver.close()
                
                return {
                    "status": "✓ 已连接",
                    "uri": uri,
                    "user": user,
                    "version": server_info.agent,
                    "protocol_version": server_info.protocol_version,
                    "library": "neo4j",
                }
    except ImportError:
        return {
            "status": "✗ 未安装",
            "reason": "neo4j 或 py2neo 库未安装"
        }
    except Exception as e:
        return {
            "status": "✗ 连接失败",
            "reason": str(e),
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7680"),
            "user": os.getenv("NEO4J_USER", "neo4j")
        }


def check_qdrant() -> Dict[str, Any]:
    """检查 Qdrant 连接"""
    try:
        from qdrant_client import QdrantClient
        import os
        
        host = os.getenv("QDRANT_HOST", "localhost")
        port = int(os.getenv("QDRANT_PORT", "6333"))
        
        client = QdrantClient(host=host, port=port)
        
        ***REMOVED*** 测试连接
        collections = client.get_collections().collections
        
        return {
            "status": "✓ 已连接",
            "host": host,
            "port": port,
            "collections_count": len(collections),
            "collections": [c.name for c in collections[:5]],  ***REMOVED*** 显示前5个
        }
    except ImportError:
        return {
            "status": "✗ 未安装",
            "reason": "qdrant_client 库未安装"
        }
    except Exception as e:
        return {
            "status": "✗ 连接失败",
            "reason": str(e),
            "host": os.getenv("QDRANT_HOST", "localhost"),
            "port": os.getenv("QDRANT_PORT", "6333")
        }


def check_unimem_status() -> Dict[str, Any]:
    """检查 UniMem 服务状态"""
    try:
        import requests
        
        url = "http://localhost:9622/unimem/health"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "✓ 服务运行中",
                "url": url,
                "health": data
            }
        else:
            return {
                "status": "⚠ 服务响应异常",
                "status_code": response.status_code,
                "url": url
            }
    except ImportError:
        return {
            "status": "✗ 未安装",
            "reason": "requests 库未安装"
        }
    except requests.exceptions.ConnectionError:
        return {
            "status": "✗ 服务未启动",
            "url": "http://localhost:9622/unimem/health",
            "reason": "无法连接到服务"
        }
    except Exception as e:
        return {
            "status": "✗ 检查失败",
            "reason": str(e)
        }


def main():
    """主函数"""
    print("=" * 70)
    print("UniMem 服务连接状态检查")
    print("=" * 70)
    print()
    
    ***REMOVED*** 检查 Redis
    print("【1. Redis 连接状态】")
    redis_status = check_redis()
    print(f"   状态: {redis_status['status']}")
    for key, value in redis_status.items():
        if key != 'status':
            print(f"   {key}: {value}")
    print()
    
    ***REMOVED*** 检查 Neo4j
    print("【2. Neo4j 连接状态】")
    neo4j_status = check_neo4j()
    print(f"   状态: {neo4j_status['status']}")
    for key, value in neo4j_status.items():
        if key != 'status':
            print(f"   {key}: {value}")
    print()
    
    ***REMOVED*** 检查 Qdrant
    print("【3. Qdrant 连接状态】")
    qdrant_status = check_qdrant()
    print(f"   状态: {qdrant_status['status']}")
    for key, value in qdrant_status.items():
        if key != 'status':
            print(f"   {key}: {value}")
    print()
    
    ***REMOVED*** 检查 UniMem 服务
    print("【4. UniMem 服务状态】")
    unimem_status = check_unimem_status()
    print(f"   状态: {unimem_status['status']}")
    for key, value in unimem_status.items():
        if key != 'status':
            print(f"   {key}: {value}")
    print()
    
    ***REMOVED*** 总结
    print("=" * 70)
    print("连接状态总结")
    print("=" * 70)
    all_ok = (
        "✓" in redis_status['status'] and
        "✓" in neo4j_status['status'] and
        "✓" in qdrant_status['status'] and
        "✓" in unimem_status['status']
    )
    
    if all_ok:
        print("✓ 所有服务连接正常！")
    else:
        print("⚠ 部分服务连接异常，请检查配置和服务状态")
        if "✗" in redis_status['status']:
            print(f"   - Redis: {redis_status.get('reason', '未知错误')}")
        if "✗" in neo4j_status['status']:
            print(f"   - Neo4j: {neo4j_status.get('reason', '未知错误')}")
        if "✗" in qdrant_status['status']:
            print(f"   - Qdrant: {qdrant_status.get('reason', '未知错误')}")
        if "✗" in unimem_status['status']:
            print(f"   - UniMem 服务: {unimem_status.get('reason', '未知错误')}")
    
    print()


if __name__ == "__main__":
    main()
