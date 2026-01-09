***REMOVED***!/bin/bash
***REMOVED*** 监控改进后的测试进度

LOG_FILE="multi_test_with_improvements.log"
CHECK_INTERVAL=30

echo "================================================================"
echo "监控改进后的测试进度"
echo "================================================================"
echo "日志文件: $LOG_FILE"
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "================================================================"
echo ""

while true; do
    clear
    echo "================================================================"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 测试进度监控"
    echo "================================================================"
    echo ""
    
    ***REMOVED*** 检查进程
    if pgrep -f "run_multi_test_workflow.py" > /dev/null; then
        echo "✓ 测试进程正在运行"
    else
        echo "✗ 测试进程未运行"
    fi
    echo ""
    
    ***REMOVED*** 统计Neo4j中的记忆
    echo "【Neo4j记忆统计】"
    python3 << 'PYEOF'
from py2neo import Graph
from datetime import datetime

try:
    graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')
    
    ***REMOVED*** 总记忆数
    total_query = "MATCH (m:Memory) RETURN count(m) as count"
    total_result = graph.run(total_query).data()
    total = total_result[0]['count'] if total_result else 0
    
    ***REMOVED*** 有source的记忆数
    source_query = """
    MATCH (m:Memory)
    WHERE m.source IS NOT NULL AND m.source <> ""
    RETURN count(m) as count
    """
    source_result = graph.run(source_query).data()
    with_source = source_result[0]['count'] if source_result else 0
    
    ***REMOVED*** 记忆类型分布
    type_query = """
    MATCH (m:Memory)
    RETURN m.memory_type as type, count(m) as count
    ORDER BY count DESC
    """
    type_results = graph.run(type_query).data()
    
    ***REMOVED*** 记忆关联数
    relation_query = """
    MATCH ()-[r:RELATED_TO]->()
    RETURN count(r) as count
    """
    relation_result = graph.run(relation_query).data()
    relations = relation_result[0]['count'] if relation_result else 0
    
    print(f"  总记忆数: {total}")
    print(f"  有Source字段: {with_source} ({with_source/total*100:.1f}%)" if total > 0 else "  有Source字段: 0")
    print(f"  记忆关联数: {relations}")
    print(f"\n  类型分布:")
    for r in type_results[:5]:
        print(f"    {r['type'] or 'None'}: {r['count']}")
    
except Exception as e:
    print(f"  错误: {e}")
PYEOF
    
    echo ""
    echo "【最新日志】"
    tail -20 "$LOG_FILE" 2>/dev/null | grep -E "(测试|Test|ERROR|Error|✓|✗|REFLECT|RETAIN|RECALL|Stored|stored)" | tail -10
    
    echo ""
    echo "【测试统计】"
    grep -E "^测试|^测试[0-9]" "$LOG_FILE" 2>/dev/null | tail -5
    
    echo ""
    echo "按 Ctrl+C 停止监控"
    sleep $CHECK_INTERVAL
done
