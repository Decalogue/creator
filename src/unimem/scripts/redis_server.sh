#!/bin/bash

# Redis 服务管理脚本
# 用于启动、停止、重启和检查 Redis 数据库服务
# 默认工作目录为 src

set -e

# 切换到 src 目录（脚本在 unimem/scripts/，需要回到 src）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
UNIMEM_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="$(cd "$UNIMEM_DIR/.." && pwd)"
cd "$SRC_DIR"

# 配置
CONTAINER_NAME="redis_unimem"
HOST_PORT=6379
STORAGE_PATH="./unimem/redis_storage"  # 相对于 src 目录
IMAGE_NAME="redis:7-alpine"
REDIS_PASSWORD=""  # 可选，如果设置则启用密码保护

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        echo
        echo "安装方式（选择其一）："
        echo "  1. 使用 apt 安装（推荐）:"
        echo "     sudo apt-get update"
        echo "     sudo apt-get install -y docker.io"
        echo "     sudo systemctl start docker"
        echo "     sudo systemctl enable docker"
        echo
        echo "  2. 使用 snap 安装:"
        echo "     sudo snap install docker"
        echo
        echo "  3. 使用官方安装脚本:"
        echo "     curl -fsSL https://get.docker.com -o get-docker.sh"
        echo "     sudo sh get-docker.sh"
        echo
        echo "安装后，可能需要将当前用户添加到 docker 组:"
        echo "     sudo usermod -aG docker $USER"
        echo "     # 然后重新登录或执行: newgrp docker"
        echo
        echo "详细安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    # 检查 Docker 服务是否运行
    if ! docker info &> /dev/null; then
        print_warn "Docker 已安装但服务未运行"
        echo "尝试启动 Docker 服务..."
        if command -v systemctl &> /dev/null; then
            echo "请运行: sudo systemctl start docker"
        fi
        exit 1
    fi
    
    print_info "Docker 已安装: $(docker --version)"
}

# 检查容器是否运行
is_running() {
    docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# 检查容器是否存在（包括已停止的）
container_exists() {
    docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# 启动 Redis 服务
start() {
    check_docker
    
    if is_running; then
        print_warn "Redis 容器已在运行: ${CONTAINER_NAME}"
        return 0
    fi
    
    # 创建存储目录
    mkdir -p "${STORAGE_PATH}"
    
    print_info "启动 Redis 容器..."
    
    # 构建 Docker 命令
    DOCKER_CMD=(
        docker run -d
        --name "${CONTAINER_NAME}"
        -p "${HOST_PORT}:6379"
        -v "${STORAGE_PATH}:/data"
        --restart unless-stopped
    )
    
    # 如果设置了密码，添加到命令
    if [ -n "${REDIS_PASSWORD}" ]; then
        DOCKER_CMD+=(--requirepass "${REDIS_PASSWORD}")
        print_info "Redis 密码保护已启用"
    fi
    
    DOCKER_CMD+=(
        "${IMAGE_NAME}"
        redis-server --appendonly yes
    )
    
    "${DOCKER_CMD[@]}"
    
    # 等待服务启动
    sleep 2
    
    if is_running; then
        print_info "Redis 服务已启动"
        print_info "容器名称: ${CONTAINER_NAME}"
        print_info "端口映射: ${HOST_PORT}:6379"
        print_info "数据存储: ${STORAGE_PATH}"
        if [ -n "${REDIS_PASSWORD}" ]; then
            print_info "密码: ${REDIS_PASSWORD}（已设置）"
            print_warn "请设置环境变量: export REDIS_PASSWORD=${REDIS_PASSWORD}"
        else
            print_warn "未设置密码，生产环境建议启用密码保护"
        fi
        echo
        print_info "测试连接:"
        echo "  redis-cli -h localhost -p ${HOST_PORT} ping"
    else
        print_error "Redis 服务启动失败"
        exit 1
    fi
}

# 停止 Redis 服务
stop() {
    if ! container_exists; then
        print_warn "Redis 容器不存在: ${CONTAINER_NAME}"
        return 0
    fi
    
    if is_running; then
        print_info "停止 Redis 容器..."
        docker stop "${CONTAINER_NAME}"
        print_info "Redis 服务已停止"
    else
        print_warn "Redis 容器未运行"
    fi
}

# 重启 Redis 服务
restart() {
    stop
    sleep 1
    start
}

# 删除 Redis 容器（注意：会删除数据）
remove() {
    stop
    
    if container_exists; then
        print_warn "删除 Redis 容器（数据不会丢失，存储在 ${STORAGE_PATH}）..."
        docker rm "${CONTAINER_NAME}"
        print_info "Redis 容器已删除"
    else
        print_warn "Redis 容器不存在"
    fi
}

# 检查服务状态
status() {
    if is_running; then
        print_info "Redis 服务运行中"
        echo
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo
        print_info "测试连接..."
        if command -v redis-cli &> /dev/null; then
            if [ -n "${REDIS_PASSWORD}" ]; then
                redis-cli -h localhost -p ${HOST_PORT} -a "${REDIS_PASSWORD}" ping 2>/dev/null && print_info "连接正常" || print_error "连接失败"
            else
                redis-cli -h localhost -p ${HOST_PORT} ping 2>/dev/null && print_info "连接正常" || print_error "连接失败"
            fi
        else
            print_warn "redis-cli 未安装，无法测试连接"
        fi
    else
        if container_exists; then
            print_warn "Redis 容器存在但未运行"
            echo
            docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}"
            echo
            print_info "运行 '$0 start' 启动服务"
        else
            print_warn "Redis 容器不存在"
            print_info "运行 '$0 start' 创建并启动服务"
        fi
    fi
}

# 查看日志
logs() {
    if ! container_exists; then
        print_error "Redis 容器不存在"
        exit 1
    fi
    
    docker logs -f "${CONTAINER_NAME}"
}

# 进入 Redis CLI
cli() {
    if ! is_running; then
        print_error "Redis 服务未运行"
        exit 1
    fi
    
    if ! command -v redis-cli &> /dev/null; then
        print_error "redis-cli 未安装"
        echo "安装方式："
        echo "  sudo apt-get install redis-tools"
        exit 1
    fi
    
    if [ -n "${REDIS_PASSWORD}" ]; then
        redis-cli -h localhost -p ${HOST_PORT} -a "${REDIS_PASSWORD}"
    else
        redis-cli -h localhost -p ${HOST_PORT}
    fi
}

# 显示帮助信息
usage() {
    echo "Redis 服务管理脚本"
    echo
    echo "用法: $0 {start|stop|restart|status|logs|cli|remove}"
    echo
    echo "命令："
    echo "  start    - 启动 Redis 服务"
    echo "  stop     - 停止 Redis 服务"
    echo "  restart  - 重启 Redis 服务"
    echo "  status   - 查看服务状态"
    echo "  logs     - 查看服务日志"
    echo "  cli      - 进入 Redis CLI"
    echo "  remove   - 删除容器（数据保留在 ${STORAGE_PATH}）"
    echo
    echo "配置："
    echo "  修改脚本中的变量来更改配置："
    echo "  - CONTAINER_NAME: 容器名称"
    echo "  - HOST_PORT: 主机端口（默认: 6379）"
    echo "  - STORAGE_PATH: 数据存储路径（默认: ./unimem/redis_storage）"
    echo "  - REDIS_PASSWORD: Redis 密码（可选，设置后启用密码保护）"
    echo
    echo "环境变量："
    echo "  可以在调用脚本前设置环境变量来覆盖配置："
    echo "  export REDIS_PASSWORD='your_password'"
}

# 主函数
main() {
    case "${1:-}" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            status
            ;;
        logs)
            logs
            ;;
        cli)
            cli
            ;;
        remove)
            remove
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            echo "未知命令: ${1:-}"
            echo
            usage
            exit 1
            ;;
    esac
}

# 读取环境变量覆盖配置
if [ -n "${REDIS_CONTAINER_NAME:-}" ]; then
    CONTAINER_NAME="${REDIS_CONTAINER_NAME}"
fi
if [ -n "${REDIS_HOST_PORT:-}" ]; then
    HOST_PORT="${REDIS_HOST_PORT}"
fi
if [ -n "${REDIS_STORAGE_PATH:-}" ]; then
    STORAGE_PATH="${REDIS_STORAGE_PATH}"
fi
if [ -n "${REDIS_PASSWORD:-}" ]; then
    REDIS_PASSWORD="${REDIS_PASSWORD}"
fi

# 执行主函数
main "$@"

