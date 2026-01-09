***REMOVED***!/bin/bash
***REMOVED*** 监控新模板测试的进度

echo "=========================================="
echo "新模板测试进度监控"
echo "=========================================="
echo

***REMOVED*** 检查测试进程
if ps aux | grep -v grep | grep -q "comprehensive_context_graph_test.py"; then
    echo "✅ 测试正在运行中..."
    echo
else
    echo "⚠️  测试进程未运行"
    echo
fi

***REMOVED*** 检查最新日志文件
LATEST_LOG=$(ls -t /root/data/AI/creator/src/unimem/examples/context_graph_test_new_template_*.log 2>/dev/null | head -1)

if [ -n "$LATEST_LOG" ]; then
    echo "📋 最新日志文件: $LATEST_LOG"
    echo
    echo "--- 最后30行日志 ---"
    tail -30 "$LATEST_LOG"
    echo
    echo "--- 测试统计 ---"
    echo "已完成场景数: $(grep -c "测试场景:" "$LATEST_LOG" 2>/dev/null || echo 0)"
    echo "REFLECT完成次数: $(grep -c "REFLECT completed" "$LATEST_LOG" 2>/dev/null || echo 0)"
    echo "生成脚本次数: $(grep -c "Script generated successfully" "$LATEST_LOG" 2>/dev/null || echo 0)"
    echo
else
    echo "⚠️  未找到日志文件"
    echo
fi

***REMOVED*** 检查文档
echo "--- 测试文档 ---"
DOC_COUNT=$(ls -1 /tmp/test_docs_new_template/*.docx 2>/dev/null | wc -l)
if [ "$DOC_COUNT" -gt 0 ]; then
    echo "✅ 找到 $DOC_COUNT 份测试文档"
    ls -lh /tmp/test_docs_new_template/*.docx 2>/dev/null | awk '{print "  -", $9, "("$5")"}'
else
    echo "⚠️  未找到测试文档"
fi

echo
echo "=========================================="
