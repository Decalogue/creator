***REMOVED***!/bin/bash
***REMOVED*** Context Graph 综合测试启动脚本

cd "$(dirname "$0")"
cd ../..

echo "=========================================="
echo "Context Graph 综合测试"
echo "=========================================="
echo ""
echo "本测试将："
echo "  1. 生成5个差异化的测试场景"
echo "  2. 执行完整的多轮交互流程"
echo "  3. 验证Context Graph功能"
echo "  4. 分析结果并进化系统"
echo ""
echo "预计耗时: 15-30分钟"
echo ""
read -p "按回车键开始测试，或Ctrl+C取消..."

***REMOVED*** 激活conda环境
source ~/anaconda3/etc/profile.d/conda.sh
conda activate myswift 2>/dev/null || conda activate seeme 2>/dev/null || echo "⚠ 未找到conda环境，使用系统Python"

***REMOVED*** 设置PYTHONPATH
export PYTHONPATH=/root/data/AI/creator/src:$PYTHONPATH

***REMOVED*** 运行测试
echo ""
echo "开始运行测试..."
echo "=========================================="
echo ""

python3 unimem/examples/comprehensive_context_graph_test.py 2>&1 | tee context_graph_test_$(date +%Y%m%d_%H%M%S).log

echo ""
echo "=========================================="
echo "测试完成！"
echo "=========================================="
echo ""
echo "查看结果文件："
echo "  - context_graph_test_results_*.json"
echo "  - context_graph_test_evolution_*.json"
echo "  - context_graph_test_*.log"
echo ""
