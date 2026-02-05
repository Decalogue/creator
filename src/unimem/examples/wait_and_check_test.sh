#!/bin/bash

LOG_FILE=$(ls -t context_graph_test_full_*.log 2>/dev/null | head -1)

if [ -z "$LOG_FILE" ]; then
    echo "❌ 未找到日志文件"
    exit 1
fi

echo "等待测试完成..."
echo "日志文件: $LOG_FILE"
echo

MAX_WAIT=600  # 最多等待10分钟
WAIT_INTERVAL=30  # 每30秒检查一次
ELAPSED=0

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if ! pgrep -f "comprehensive_context_graph_test.py" > /dev/null; then
        echo "✅ 测试进程已完成"
        break
    fi
    
    if grep -q "测试完成\|测试完成！" "$LOG_FILE" 2>/dev/null; then
        echo "✅ 测试已完成（在日志中发现完成标记）"
        break
    fi
    
    SCENARIOS=$(grep -c "Parsing Word document" "$LOG_FILE" 2>/dev/null || echo "0")
    if [ "$SCENARIOS" -ge 5 ]; then
        echo "✅ 所有场景已处理完成"
        # 再等待一下确保测试完全结束
        sleep 10
        break
    fi
    
    sleep $WAIT_INTERVAL
    ELAPSED=$((ELAPSED + WAIT_INTERVAL))
    echo "[$(date '+%H:%M:%S')] 已等待 ${ELAPSED}秒，已处理场景: $SCENARIOS/5"
done

echo
echo "最终状态:"
bash monitor_test.sh
