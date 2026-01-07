"""
UniMem 基本使用示例

展示 UniMem 系统的核心功能：
- RETAIN: 存储新记忆
- RECALL: 检索相关记忆
- REFLECT: 更新和优化记忆
- SLEEP UPDATE: 批量优化记忆
- 适配器状态查询

运行前确保：
1. 已激活 myswift 环境：conda activate myswift
2. 相关服务已启动（Redis、Neo4j、Qdrant 等，根据配置）
"""

import logging
from datetime import datetime
from typing import Dict, Any, List
from unimem import UniMem, Experience, Context, Task

***REMOVED*** 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    基本使用示例
    
    演示 UniMem 系统的核心操作流程
    """
    ***REMOVED*** 初始化系统
    print("Initializing UniMem...")
    try:
        memory = UniMem(
            storage_backend="redis",
            graph_backend="neo4j",
            vector_backend="qdrant",
        )
        print("UniMem initialized successfully\n")
    except Exception as e:
        logger.error(f"Failed to initialize UniMem: {e}")
        print(f"错误: 初始化失败 - {e}")
        return
    
    ***REMOVED*** 1. RETAIN 操作：存储新记忆
    print("=" * 50)
    print("1. RETAIN: Storing new memory")
    print("=" * 50)
    
    experience = Experience(
        content="用户喜欢在早上喝咖啡，并且偏爱深度烘焙的豆子。",
        timestamp=datetime.now(),
        context="早餐偏好讨论"
    )
    context = Context(
        session_id="session_001",
        user_id="user_123",
    )
    
    retained_memory = memory.retain(experience, context)
    print(f"✓ Memory stored: ID={retained_memory.id}")
    print(f"  Content: {retained_memory.content[:50]}...")
    print(f"  Type: {retained_memory.memory_type}")
    print()
    
    ***REMOVED*** 2. RECALL 操作：检索相关记忆
    print("=" * 50)
    print("2. RECALL: Retrieving related memories")
    print("=" * 50)
    
    query = "用户的早餐偏好是什么？"
    recall_context = Context(
        session_id="session_001",
        user_id="user_123",
    )
    
    try:
        results = memory.recall(query, context=recall_context, top_k=5)
        if isinstance(results, dict):
            ***REMOVED*** 如果返回字典格式（新版本）
            results_list = results.get("results", [])
        else:
            ***REMOVED*** 如果返回列表格式（旧版本）
            results_list = results
        
        print(f"✓ Retrieved {len(results_list)} memories:")
        for i, result in enumerate(results_list, 1):
            if hasattr(result, 'score') and hasattr(result, 'memory'):
                print(f"  {i}. Score: {result.score:.3f}, Method: {result.retrieval_method}")
                print(f"     Content: {result.memory.content[:50]}...")
            elif isinstance(result, dict):
                print(f"  {i}. {result.get('content', '')[:50]}...")
    except Exception as e:
        logger.error(f"RECALL operation failed: {e}")
        print(f"⚠️ 检索失败: {e}")
    print()
    
    ***REMOVED*** 3. REFLECT 操作：更新和优化记忆
    print("=" * 50)
    print("3. REFLECT: Updating and optimizing memories")
    print("=" * 50)
    
    task = Task(
        id="task_001",
        description="更新用户画像",
        context="根据最新交互更新用户对咖啡的偏好"
    )
    
    try:
        ***REMOVED*** 获取记忆列表
        if isinstance(results, dict):
            results_list = results.get("results", [])
        else:
            results_list = results
        
        memories_to_reflect = [
            result.memory if hasattr(result, 'memory') else result 
            for result in results_list[:3]
        ] if results_list else [retained_memory]
        
        evolved_memories = memory.reflect(memories_to_reflect, task)
        if isinstance(evolved_memories, dict):
            evolved_list = evolved_memories.get("evolved_memories", [])
        else:
            evolved_list = evolved_memories
        
        print(f"✓ Evolved {len(evolved_list)} memories")
        for mem in evolved_list:
            mem_id = mem.id if hasattr(mem, 'id') else mem.get('id', 'unknown')
            print(f"  - Memory {mem_id}: Updated")
    except Exception as e:
        logger.error(f"REFLECT operation failed: {e}")
        print(f"⚠️ 记忆演化失败: {e}")
    print()
    
    ***REMOVED*** 4. 睡眠更新
    print("=" * 50)
    print("4. SLEEP UPDATE: Batch optimization")
    print("=" * 50)
    
    try:
        count = memory.run_sleep_update()
        print(f"✓ Sleep update completed: {count} memories processed")
    except Exception as e:
        logger.error(f"SLEEP UPDATE operation failed: {e}")
        print(f"⚠️ 睡眠更新失败: {e}")
    print()
    
    ***REMOVED*** 5. 适配器状态
    print("=" * 50)
    print("5. ADAPTER STATUS")
    print("=" * 50)
    
    try:
        status = memory.get_adapter_status()
        for name, info in status.items():
            available = "✓" if info.get("available") else "✗"
            print(f"  {available} {name}: {info.get('adapter', 'N/A')}")
    except Exception as e:
        logger.error(f"Failed to get adapter status: {e}")
        print(f"⚠️ 获取适配器状态失败: {e}")
    print()


if __name__ == "__main__":
    main()
