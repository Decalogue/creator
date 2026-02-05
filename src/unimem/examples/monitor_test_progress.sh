#!/bin/bash

echo "=========================================="
echo "UniMem 测试进度监控"
echo "=========================================="
echo

# 查找最新日志
LATEST_LOG=$(ls -t context_graph_test_*.log 2>/dev/null | head -1)

if [ -z "$LATEST_LOG" ]; then
    echo "❌ 未找到测试日志文件"
    exit 1
fi

echo "📋 最新日志文件: $LATEST_LOG"
echo "📅 最后修改时间: $(stat -c %y "$LATEST_LOG" | cut -d'.' -f1)"
echo

# 检查进程
if pgrep -f "comprehensive_context_graph_test.py" > /dev/null; then
    PID=$(pgrep -f "comprehensive_context_graph_test.py" | head -1)
    echo "✅ 测试正在运行中..."
    echo "   进程ID: $PID"
    ETIME=$(ps -p $PID -o etime= 2>/dev/null | xargs)
    echo "   运行时间: $ETIME"
else
    echo "⚠️  测试进程未运行（可能已完成）"
fi

echo
echo "--- 测试进度统计 ---"

# 统计已完成场景
COMPLETED=$(grep -c "【步骤8】获取最终剧本\|测试完成" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已完成场景数: $COMPLETED/5"

# 统计已存储脚本
SCRIPT_COUNT=$(grep -c "Stored script to UniMem\|剧本生成成功" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "已生成剧本数: $SCRIPT_COUNT/5"

# 统计DecisionEvent
EVENT_COUNT=$(grep -c "Created decision event\|Created DecisionEvent" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "DecisionEvent创建数: $EVENT_COUNT ⭐"

# 统计最终剧本保存
FINAL_SCRIPT_COUNT=$(grep -c "最终剧本已获取\|最终剧本已保存" "$LATEST_LOG" 2>/dev/null || echo "0")
echo "最终剧本保存数: $FINAL_SCRIPT_COUNT/5 ⭐"

# 统计错误
ERRORS=$(grep -ci "error\|exception\|failed" "$LATEST_LOG" 2>/dev/null | head -1 || echo "0")
echo "错误/异常数: $ERRORS"

echo
echo "--- 当前步骤 ---"
CURRENT_STEP=$(grep -E "【步骤[0-9]】" "$LATEST_LOG" 2>/dev/null | tail -1)
if [ -n "$CURRENT_STEP" ]; then
    echo "$CURRENT_STEP"
else
    echo "正在初始化..."
fi

echo
echo "--- 最后15行日志 ---"
tail -15 "$LATEST_LOG" 2>/dev/null

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
    
    # 检查最终剧本文件
    if [ -d "final_scripts" ]; then
        SCRIPT_FILES=$(ls final_scripts/*_final_script.txt 2>/dev/null | wc -l)
        if [ "$SCRIPT_FILES" -gt 0 ]; then
            echo "最终剧本文件: final_scripts/ (共$SCRIPT_FILES个文件)"
        fi
    fi
fi

echo
echo "=========================================="
