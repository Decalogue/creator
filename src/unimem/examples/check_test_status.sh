***REMOVED***!/bin/bash

echo "=========================================="
echo "测试状态检查脚本"
echo "=========================================="
echo

LATEST_LOG=$(ls -t /root/data/AI/creator/src/unimem/examples/context_graph_test_auto_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ 未找到测试日志文件"
    exit 1
fi

echo "📋 最新日志文件: $LATEST_LOG"
echo

if pgrep -f "comprehensive_context_graph_test.py" > /dev/null; then
    echo "✅ 测试正在运行中..."
    PID=$(pgrep -f "comprehensive_context_graph_test.py" | head -1)
    echo "   进程ID: $PID"
else
    echo "⚠️  测试进程未运行（可能已完成）"
fi

echo
echo "--- 最后20行日志 ---"
tail -20 "$LATEST_LOG" 2>/dev/null

echo
echo "--- 测试进度统计 ---"

COMPLETED_SCENARIOS=$(grep -c "Parsing Word document.*scenario_" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已处理场景数: $COMPLETED_SCENARIOS/5"

SCRIPT_COUNT=$(grep -c "Stored script to UniMem" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已存储脚本数: $SCRIPT_COUNT/5"

EVENT_COUNT=$(grep -c "Created decision event for memory" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "DecisionEvent创建数: $EVENT_COUNT ⭐"

TRACE_COUNT=$(grep -c "Retrieved decision_trace from metadata\|Constructed decision_trace from metadata" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "从metadata读取decision_trace次数: $TRACE_COUNT ⭐"

REASONING_COUNT=$(grep -c "Retrieved reasoning from metadata" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "从metadata读取reasoning次数: $REASONING_COUNT ⭐"

if grep -q "测试完成" "$LATEST_LOG" 2>/dev/null; then
    echo
    echo "✅ 测试已完成！"
    echo
    echo "--- 测试结果文件 ---"
    RESULT_FILE=$(grep -o "测试结果: [^ ]*" "$LATEST_LOG" 2>/dev/null | tail -1 | cut -d' ' -f2)
    if [ -n "$RESULT_FILE" ] && [ -f "$RESULT_FILE" ]; then
        echo "结果文件: $RESULT_FILE"
    fi
fi

echo
echo "=========================================="
echo "💡 提示: 使用以下命令查看实时日志"
echo "   tail -f $LATEST_LOG"
echo "=========================================="
