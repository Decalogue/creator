"""
UniMem 基本使用示例
"""

import logging
from datetime import datetime
from unimem import UniMem, Experience, Context, Task

***REMOVED*** 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """基本使用示例"""
    ***REMOVED*** 初始化系统
    print("Initializing UniMem...")
    memory = UniMem(
        storage_backend="redis",
        graph_backend="neo4j",
        vector_backend="qdrant",
    )
    print("UniMem initialized successfully\n")
    
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
    
    results = memory.recall(query, context=recall_context, top_k=5)
    print(f"✓ Retrieved {len(results)} memories:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. Score: {result.score:.3f}, Method: {result.retrieval_method}")
        print(f"     Content: {result.memory.content[:50]}...")
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
    
    memories_to_reflect = [result.memory for result in results[:3]] if results else [retained_memory]
    evolved_memories = memory.reflect(memories_to_reflect, task)
    print(f"✓ Evolved {len(evolved_memories)} memories")
    for mem in evolved_memories:
        print(f"  - Memory {mem.id}: Updated")
    print()
    
    ***REMOVED*** 4. 睡眠更新
    print("=" * 50)
    print("4. SLEEP UPDATE: Batch optimization")
    print("=" * 50)
    
    count = memory.run_sleep_update()
    print(f"✓ Sleep update completed: {count} memories processed")
    print()
    
    ***REMOVED*** 5. 适配器状态
    print("=" * 50)
    print("5. ADAPTER STATUS")
    print("=" * 50)
    
    status = memory.get_adapter_status()
    for name, info in status.items():
        available = "✓" if info.get("available") else "✗"
        print(f"  {available} {name}: {info.get('adapter', 'N/A')}")
    print()


if __name__ == "__main__":
    main()
