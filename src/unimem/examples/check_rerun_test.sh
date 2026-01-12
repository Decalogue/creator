***REMOVED***!/bin/bash

LATEST_LOG=$(ls -t context_graph_test_rerun_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ 未找到测试日志文件"
    exit 1
fi

echo "=========================================="
echo "测试状态监控（重新运行）"
echo "=========================================="
echo "日志文件: $LATEST_LOG"
echo

***REMOVED*** 检查进程
if pgrep -f "comprehensive_context_graph_test.py" > /dev/null; then
    PID=$(pgrep -f "comprehensive_context_graph_test.py" | head -1)
    echo "✅ 测试正在运行 (PID: $PID)"
    ps -p $PID -o etime= 2>&1 | xargs echo "   运行时间:"
else
    echo "⚠️  测试进程未运行（可能已完成）"
fi

echo
echo "--- 进度统计 ---"
COMPLETED=$(grep -c "Parsing Word document.*scenario_" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已处理场景: $COMPLETED/5"

STORED=$(grep -c "Stored script to UniMem" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已存储脚本: $STORED/5"

EVENT=$(grep -c "Created decision event\|Created DecisionEvent" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "DecisionEvent创建: $EVENT"

ERRORS=$(grep -ci "error\|exception\|failed" "$LATEST_LOG" 2>/dev/null | grep -v "API connection error" | head -1 || echo "0")
echo "错误/异常数（排除LightRAG）: $ERRORS"

echo
echo "--- 最后10行日志 ---"
tail -10 "$LATEST_LOG" 2>/dev/null

if grep -q "测试完成\|测试完成！" "$LATEST_LOG" 2>/dev/null; then
    echo
    echo "✅ 测试已完成！"
    echo
    echo "--- 结果文件 ---"
    RESULT_FILE=$(grep -o "测试结果: [^ ]*" "$LATEST_LOG" 2>/dev/null | tail -1 | cut -d' ' -f2)
    EVOLUTION_FILE=$(grep -o "进化报告: [^ ]*" "$LATEST_LOG" 2>/dev/null | tail -1 | cut -d' ' -f2)
    if [ -n "$RESULT_FILE" ] && [ -f "$RESULT_FILE" ]; then
        echo "结果文件: $RESULT_FILE"
    fi
    if [ -n "$EVOLUTION_FILE" ] && [ -f "$EVOLUTION_FILE" ]; then
        echo "进化报告: $EVOLUTION_FILE"
    fi
fi

