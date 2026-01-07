***REMOVED***!/bin/bash
***REMOVED*** UniMem HTTP Service 启动脚本
***REMOVED*** 默认工作目录为 src

***REMOVED*** 切换到 src 目录（脚本在 unimem/scripts/，需要回到 src）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UNIMEM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$(cd "$UNIMEM_DIR/.." && pwd)"
cd "$SRC_DIR"

***REMOVED*** 确保在 src 目录
if [ ! -d "unimem" ]; then
    echo "错误: 当前目录不是 src 目录，请确保脚本在 src/unimem/scripts/ 下运行"
    exit 1
fi

***REMOVED*** 激活 conda 环境（如果使用 conda）
***REMOVED*** conda activate seeme

***REMOVED*** 设置环境变量（可选）
***REMOVED*** export UNIMEM_CONFIG_FILE="unimem/config/unimem_service.json"
***REMOVED*** export UNIMEM_HOST="0.0.0.0"
***REMOVED*** export UNIMEM_PORT="9622"
***REMOVED*** export UNIMEM_STORAGE_BACKEND="redis"
***REMOVED*** export UNIMEM_GRAPH_BACKEND="neo4j"
***REMOVED*** export UNIMEM_VECTOR_BACKEND="qdrant"

***REMOVED*** 启动服务（默认工作目录为 src）
***REMOVED*** 配置文件路径相对于 src 目录
python -m unimem.service.server \
    --host "${UNIMEM_HOST:-0.0.0.0}" \
    --port "${UNIMEM_PORT:-9622}" \
    ${UNIMEM_CONFIG_FILE:+--config "$UNIMEM_CONFIG_FILE"}

