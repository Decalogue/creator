***REMOVED***!/bin/bash
***REMOVED*** 监控测试进度和 Neo4j 记忆存储

echo "============================================================"
echo "测试进度监控"
echo "============================================================"

LOG_FILE="/root/data/AI/creator/src/unimem/examples/multi_test_workflow_local.log"
NEO4J_CHECK_SCRIPT="/tmp/check_neo4j.py"

***REMOVED*** 创建 Neo4j 检查脚本
cat > $NEO4J_CHECK_SCRIPT << 'PYTHON_EOF'
from py2neo import Graph
graph = Graph("bolt://localhost:7680", auth=('neo4j', 'seeme_db'), name='neo4j')
query = "MATCH (m:Memory) RETURN count(m) as count"
result = graph.run(query).data()
count = result[0]['count'] if result else 0
print(count)
PYTHON_EOF

while true; do
    echo ""
    echo "--- $(date '+%Y-%m-%d %H:%M:%S') ---"
    
    ***REMOVED*** 检查日志文件大小
    if [ -f "$LOG_FILE" ]; then
        LINES=$(wc -l < "$LOG_FILE" 2>/dev/null || echo "0")
        echo "日志行数: $LINES"
        
        ***REMOVED*** 检查最近的进度
        echo "最近的进度:"
        tail -3 "$LOG_FILE" 2>/dev/null | grep -E "(测试|REFLECT|完成|Stored|memory_id)" | tail -3 || echo "  等待中..."
    fi
    
    ***REMOVED*** 检查 Neo4j 中的记忆数量
    if command -v python3 &> /dev/null; then
        COUNT=$(cd /root/data/AI/creator/src && conda activate seeme 2>/dev/null && PYTHONPATH=/root/data/AI/creator/src:$PYTHONPATH python3 $NEO4J_CHECK_SCRIPT 2>/dev/null || echo "0")
        echo "Neo4j Memory 节点数: $COUNT"
    fi
    
    ***REMOVED*** 检查进程是否还在运行
    if pgrep -f "run_multi_test_workflow.py" > /dev/null; then
        echo "测试进程: 运行中"
    else
        echo "测试进程: 已完成或已停止"
        break
    fi
    
    sleep 30
done

echo ""
echo "============================================================"
echo "监控结束"
echo "============================================================"
