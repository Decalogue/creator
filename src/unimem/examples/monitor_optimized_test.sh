***REMOVED***!/bin/bash

***REMOVED*** 监控优化后的测试进度

echo "=========================================="
echo "优化后测试进度监控"
echo "=========================================="
echo

***REMOVED*** 查找最新的日志文件
LATEST_LOG=$(ls -t /root/data/AI/creator/src/unimem/examples/context_graph_test_optimized_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ 未找到测试日志文件"
    exit 1
fi

echo "📋 最新日志文件: $LATEST_LOG"
echo

***REMOVED*** 检查进程是否运行
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

***REMOVED*** 统计场景完成情况
COMPLETED_SCENARIOS=$(grep -c "Parsing Word document.*scenario_" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已处理场景数: $COMPLETED_SCENARIOS"

***REMOVED*** 统计REFLECT完成情况
REFLECT_COUNT=$(grep -c "REFLECT completed" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "REFLECT完成次数: $REFLECT_COUNT"

***REMOVED*** 统计脚本生成情况
SCRIPT_COUNT=$(grep -c "Script generated successfully" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "生成脚本次数: $SCRIPT_COUNT"

***REMOVED*** 统计优化情况
OPTIMIZE_COUNT=$(grep -c "Optimizing script based on user feedback" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "优化次数: $OPTIMIZE_COUNT"

***REMOVED*** 检查测试是否完成
if grep -q "测试完成" "$LATEST_LOG" 2>/dev/null; then
    echo
    echo "✅ 测试已完成！"
    echo
    echo "--- 测试结果文件 ---"
    grep -E "测试结果|进化报告" "$LATEST_LOG" | tail -3
fi

echo
echo "=========================================="
