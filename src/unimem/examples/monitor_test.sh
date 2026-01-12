#!/bin/bash

LOG_FILE=$(ls -t context_graph_test_full_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ 未找到日志文件"
    exit 1
fi

echo "=========================================="
echo "测试状态监控"
echo "=========================================="
echo "日志文件: $LOG_FILE"
echo

# 检查进程
if pgrep -f "comprehensive_context_graph_test.py" > /dev/null; then
    PID=$(pgrep -f "comprehensive_context_graph_test.py" | head -1)
    echo "✅ 测试正在运行 (PID: $PID)"
    ps -p $PID -o etime= 2>/dev/null | xargs echo "   运行时间:"
else
    echo "⚠️  测试进程未运行"
fi

echo
echo "--- 进度统计 ---"
COMPLETED=$(grep -c "Parsing Word document.*scenario_" "$LOG_FILE" 2>/dev/null || echo "0")
echo "已处理场景: $COMPLETED/5"

STORED=$(grep -c "Stored script to UniMem" "$LOG_FILE" 2>/dev/null || echo "0")
echo "已存储脚本: $STORED/5"

EVENT=$(grep -c "Created decision event\|Created DecisionEvent" "$LOG_FILE" 2>/dev/null || echo "0")
echo "DecisionEvent创建: $EVENT"

ERRORS=$(grep -ci "error\|exception\|failed" "$LOG_FILE" 2>/dev/null || echo "0")
echo "错误/异常数: $ERRORS"

echo
echo "--- 最后10行日志 ---"
tail -10 "$LOG_FILE" 2>/dev/null

if grep -q "测试完成\|测试完成！" "$LOG_FILE" 2>/dev/null; then
    echo
    echo "✅ 测试已完成！"
fi

