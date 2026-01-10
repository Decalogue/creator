***REMOVED***!/bin/bash

echo "=========================================="
echo "修复后测试进度监控"
echo "=========================================="
echo

LATEST_LOG=$(ls -t /root/data/AI/creator/src/unimem/examples/context_graph_test_fixed_final_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ 未找到测试日志文件"
    exit 1
fi

echo "📋 最新日志文件: $LATEST_LOG"
echo

if pgrep -f "comprehensive_context_graph_test.py" > /dev/null; then
    echo "✅ 测试正在运行中..."
else
    echo "⚠️  测试进程未运行（可能已完成或出错）"
fi

echo
echo "--- 最后30行日志 ---"
tail -30 "$LATEST_LOG" 2>/dev/null

echo
echo "--- 测试统计 ---"

COMPLETED_SCENARIOS=$(grep -c "Parsing Word document.*scenario_" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已处理场景数: $COMPLETED_SCENARIOS"

REFLECT_COUNT=$(grep -c "REFLECT completed" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "REFLECT完成次数: $REFLECT_COUNT"

SCRIPT_COUNT=$(grep -c "Script generated successfully" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "生成脚本次数: $SCRIPT_COUNT"

EVENT_COUNT=$(grep -c "Created decision event for memory" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "DecisionEvent创建次数: $EVENT_COUNT ⭐"

TRACE_COUNT=$(grep -c "Retrieved decision_trace from metadata\|Constructed decision_trace from metadata" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "从metadata读取decision_trace次数: $TRACE_COUNT ⭐"

if grep -q "测试完成" "$LATEST_LOG" 2>/dev/null; then
    echo
    echo "✅ 测试已完成！"
    echo
    echo "--- 测试结果文件 ---"
    grep -E "测试结果|进化报告" "$LATEST_LOG" | tail -3
fi

echo
echo "=========================================="
