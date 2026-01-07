***REMOVED***!/bin/bash
***REMOVED*** Puppeteer 与 UniMem 集成测试脚本

set -e

echo "============================================================"
echo "Puppeteer 与 UniMem 集成测试"
echo "============================================================"

***REMOVED*** 切换到项目根目录 (src)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PUPPETEER_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$(cd "$PUPPETEER_DIR/.." && pwd)"
cd "$SRC_DIR"

echo "工作目录: $SRC_DIR"
echo ""

***REMOVED*** 检查 UniMem 服务
echo "检查 UniMem 服务..."
if curl -s http://localhost:9622/unimem/health > /dev/null 2>&1; then
    echo "✓ UniMem 服务正在运行"
else
    echo "✗ UniMem 服务未运行"
    echo ""
    echo "请先启动 UniMem 服务："
    echo "  cd $SRC_DIR"
    echo "  ./unimem/scripts/start_unimem_service.sh"
    echo ""
    echo "或直接运行："
    echo "  python -m unimem.service.server"
    echo ""
    read -p "是否继续测试（测试会在服务连接部分失败）? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "开始运行测试..."
echo ""

***REMOVED*** 激活 conda 环境（如果需要）
***REMOVED*** conda activate seeme

***REMOVED*** 运行测试（需要在 puppeteer 目录下）
cd puppeteer
python examples/test_unimem_integration.py

echo ""
echo "============================================================"
echo "测试完成"
echo "============================================================"

