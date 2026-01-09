***REMOVED***!/bin/bash
***REMOVED*** Context Graph测试监控脚本

LOG_FILE=$(ls -t context_graph_test_*.log 2>/dev/null | head -1)
if [ -z "$LOG_FILE" ]; then
    echo "⚠ 未找到日志文件，测试可能尚未开始"
    exit 1
fi

echo "=========================================="
echo "Context Graph测试监控"
echo "=========================================="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

***REMOVED*** 1. 检查进程状态
echo "【进程状态】"
if ps aux | grep -v grep | grep -q "comprehensive_context_graph_test.*python3"; then
    ps aux | grep -v grep | grep "comprehensive_context_graph_test.*python3" | awk '{print "  ✓ 测试正在运行 (PID: " $2 ", CPU: " $3 "%, MEM: " $4 "%, 运行时间: " $10 ")"}'
else
    echo "  ✗ 测试进程未运行（可能已完成）"
fi
echo ""

***REMOVED*** 2. 检查日志文件
echo "【日志文件】"
if [ -f "$LOG_FILE" ]; then
    SIZE=$(ls -lh "$LOG_FILE" | awk '{print $5}')
    LINES=$(wc -l < "$LOG_FILE")
    echo "  文件: $LOG_FILE"
    echo "  大小: $SIZE"
    echo "  行数: $LINES"
else
    echo "  ⚠ 日志文件不存在"
fi
echo ""

***REMOVED*** 3. 检查测试进度
echo "【测试进度】"
if [ -f "$LOG_FILE" ]; then
    ***REMOVED*** 检查是否有场景开始
    SCENARIOS=$(grep -c "测试场景:" "$LOG_FILE" 2>/dev/null || echo "0")
    echo "  已开始场景数: $SCENARIOS"
    
    ***REMOVED*** 检查是否有场景完成
    COMPLETED=$(grep -c "RETAIN completed" "$LOG_FILE" 2>/dev/null || echo "0")
    echo "  已完成的RETAIN操作: $COMPLETED"
    
    ***REMOVED*** 检查是否有REFLECT操作
    REFLECT_COUNT=$(grep -c "REFLECT完成\|evolved_memories\|新经验" "$LOG_FILE" 2>/dev/null || echo "0")
    echo "  REFLECT操作数: $REFLECT_COUNT"
    
    ***REMOVED*** 检查错误数
    ERROR_COUNT=$(grep -c "ERROR\|Exception\|Traceback" "$LOG_FILE" 2>/dev/null || echo "0")
    if [ "$ERROR_COUNT" -gt 0 ]; then
        echo "  ⚠ 错误数: $ERROR_COUNT"
    fi
fi
echo ""

***REMOVED*** 4. 检查最新活动
echo "【最新活动】（最后10行）"
if [ -f "$LOG_FILE" ]; then
    tail -10 "$LOG_FILE" | grep -E "(INFO|WARNING|ERROR)" | tail -5 | sed 's/^/  /'
fi
echo ""

***REMOVED*** 5. 检查结果文件
echo "【结果文件】"
RESULTS=$(ls -t context_graph_test_results_*.json 2>/dev/null | head -1)
if [ -n "$RESULTS" ]; then
    SIZE=$(ls -lh "$RESULTS" | awk '{print $5}')
    echo "  ✓ 测试结果: $RESULTS ($SIZE)"
    
    ***REMOVED*** 尝试提取摘要
    if command -v python3 &> /dev/null; then
        SCENARIOS_COUNT=$(python3 -c "import json; f=open('$RESULTS'); data=json.load(f); print(len(data.get('scenarios', [])))" 2>/dev/null || echo "N/A")
        echo "    场景数: $SCENARIOS_COUNT"
    fi
else
    echo "  ⚠ 结果文件尚未生成（测试仍在进行中）"
fi

EVOLUTION=$(ls -t context_graph_test_evolution_*.json 2>/dev/null | head -1)
if [ -n "$EVOLUTION" ]; then
    SIZE=$(ls -lh "$EVOLUTION" | awk '{print $5}')
    echo "  ✓ 进化报告: $EVOLUTION ($SIZE)"
fi
echo ""

***REMOVED*** 6. 关键信息提取
echo "【关键信息】"
if [ -f "$LOG_FILE" ]; then
    ***REMOVED*** 提取最近完成的场景
    LAST_SCENARIO=$(grep "测试场景:" "$LOG_FILE" | tail -1 | sed 's/.*测试场景: //' | cut -d' ' -f1-2)
    if [ -n "$LAST_SCENARIO" ]; then
        echo "  当前场景: $LAST_SCENARIO"
    fi
    
    ***REMOVED*** 检查是否有DecisionEvent创建
    DECISION_EVENTS=$(grep -c "Created decision event\|DecisionEvent" "$LOG_FILE" 2>/dev/null || echo "0")
    echo "  决策事件节点: $DECISION_EVENTS"
    
    ***REMOVED*** 检查reasoning提取
    REASONING_COUNT=$(grep -c "reasoning\|决策理由" "$LOG_FILE" 2>/dev/null || echo "0")
    echo "  Reasoning提取: $REASONING_COUNT 次"
fi

echo ""
echo "=========================================="
