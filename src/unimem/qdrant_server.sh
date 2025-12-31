***REMOVED***!/bin/bash

***REMOVED*** Qdrant 服务管理脚本
***REMOVED*** 用于启动、停止、重启和检查 Qdrant 向量数据库服务

set -e

***REMOVED*** 配置
CONTAINER_NAME="qdrant_unimem"
HOST_PORT_HTTP=6333
HOST_PORT_GRPC=6334
STORAGE_PATH="./qdrant_storage"
IMAGE_NAME="qdrant/qdrant"

***REMOVED*** 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' ***REMOVED*** No Color

***REMOVED*** 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

***REMOVED*** 检查 Docker 是否安装
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
        echo "     ***REMOVED*** 然后重新登录或执行: newgrp docker"
        echo
        echo "详细安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    ***REMOVED*** 检查 Docker 服务是否运行
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

***REMOVED*** 检查容器是否运行
is_running() {
    docker ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

***REMOVED*** 检查容器是否存在（包括已停止的）
container_exists() {
    docker ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

***REMOVED*** 启动 Qdrant 服务
start() {
    print_info "启动 Qdrant 服务..."
    
    check_docker
    
    if is_running; then
        print_warn "Qdrant 容器已在运行: ${CONTAINER_NAME}"
        return 0
    fi
    
    ***REMOVED*** 如果容器存在但未运行，启动它
    if container_exists; then
        print_info "发现已存在的容器，启动中..."
        docker start ${CONTAINER_NAME}
        print_info "Qdrant 服务已启动"
        return 0
    fi
    
    ***REMOVED*** 创建存储目录
    mkdir -p ${STORAGE_PATH}
    
    ***REMOVED*** 检查镜像是否存在，不存在则拉取
    print_info "检查 Qdrant 镜像..."
    if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${IMAGE_NAME}:latest$"; then
        print_info "镜像不存在，开始拉取 ${IMAGE_NAME}..."
        if ! docker pull ${IMAGE_NAME}; then
            print_error "镜像拉取失败，可能是网络问题"
            echo
            echo "网络诊断："
            echo "  - 检查 DNS 解析: nslookup registry-1.docker.io"
            echo "  - 检查网络连接: ping -c 3 registry-1.docker.io"
            echo "  - 检查防火墙: sudo ufw status"
            echo
            echo "解决方案："
            echo "  1. 使用代理（如果环境支持）："
            echo "     export HTTP_PROXY=http://proxy.example.com:8080"
            echo "     export HTTPS_PROXY=http://proxy.example.com:8080"
            echo "     sudo systemctl restart docker"
            echo
            echo "  2. 手动下载镜像文件（如果有其他可访问的网络）："
            echo "     在其他机器上: docker save qdrant/qdrant -o qdrant.tar"
            echo "     传输到此机器后: docker load -i qdrant.tar"
            echo
            echo "  3. 使用本地已有的镜像（如果有）："
            echo "     docker images | grep qdrant"
            echo
            echo "  4. 检查 Docker 配置: cat /etc/docker/daemon.json"
            echo
            echo "  5. 联系网络管理员检查网络限制和 DNS 配置"
            exit 1
        fi
        print_info "镜像拉取成功"
    else
        print_info "镜像已存在"
    fi
    
    ***REMOVED*** 启动新容器
    print_info "创建并启动新的 Qdrant 容器..."
    if ! docker run -d \
        --name ${CONTAINER_NAME} \
        -p ${HOST_PORT_HTTP}:6333 \
        -p ${HOST_PORT_GRPC}:6334 \
        -v "$(pwd)/${STORAGE_PATH}:/qdrant/storage" \
        ${IMAGE_NAME}; then
        print_error "容器启动失败"
        echo "请检查错误信息，或运行: docker logs ${CONTAINER_NAME}"
        exit 1
    fi
    
    ***REMOVED*** 等待服务就绪
    print_info "等待 Qdrant 服务就绪..."
    sleep 3
    
    ***REMOVED*** 检查服务健康状态
    if check_health; then
        print_info "Qdrant 服务启动成功！"
        print_info "HTTP API: http://localhost:${HOST_PORT_HTTP}"
        print_info "gRPC: localhost:${HOST_PORT_GRPC}"
        print_info "Web UI: http://localhost:${HOST_PORT_HTTP}/dashboard"
        print_info "存储路径: $(pwd)/${STORAGE_PATH}"
    else
        print_error "Qdrant 服务启动失败，请检查日志: docker logs ${CONTAINER_NAME}"
        exit 1
    fi
}

***REMOVED*** 停止 Qdrant 服务
stop() {
    print_info "停止 Qdrant 服务..."
    
    if ! container_exists; then
        print_warn "容器不存在: ${CONTAINER_NAME}"
        return 0
    fi
    
    if is_running; then
        docker stop ${CONTAINER_NAME}
        print_info "Qdrant 服务已停止"
    else
        print_warn "Qdrant 服务未运行"
    fi
}

***REMOVED*** 重启 Qdrant 服务
restart() {
    print_info "重启 Qdrant 服务..."
    stop
    sleep 2
    start
}

***REMOVED*** 删除容器（保留数据）
remove() {
    print_info "删除 Qdrant 容器..."
    
    if ! container_exists; then
        print_warn "容器不存在: ${CONTAINER_NAME}"
        return 0
    fi
    
    if is_running; then
        stop
    fi
    
    docker rm ${CONTAINER_NAME}
    print_info "容器已删除（数据保留在 ${STORAGE_PATH}）"
}

***REMOVED*** 删除容器和数据
clean() {
    print_warn "这将删除容器和所有数据！"
    read -p "确认删除? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        remove
        rm -rf ${STORAGE_PATH}
        print_info "容器和数据已完全删除"
    else
        print_info "操作已取消"
    fi
}

***REMOVED*** 检查服务健康状态
check_health() {
    if ! is_running; then
        return 1
    fi
    
    ***REMOVED*** 检查 HTTP 端点（Qdrant 使用根路径或 /collections 作为健康检查）
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${HOST_PORT_HTTP}/collections || echo "000")
    if [ "$response" = "200" ]; then
        return 0
    else
        ***REMOVED*** 尝试根路径
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${HOST_PORT_HTTP}/ || echo "000")
        if [ "$response" = "200" ]; then
            return 0
        else
            return 1
        fi
    fi
}

***REMOVED*** 显示服务状态
status() {
    print_info "检查 Qdrant 服务状态..."
    
    if ! container_exists; then
        print_warn "容器不存在: ${CONTAINER_NAME}"
        return 1
    fi
    
    if is_running; then
        print_info "容器状态: 运行中"
        
        if check_health; then
            print_info "服务健康: 正常"
            print_info "HTTP API: http://localhost:${HOST_PORT_HTTP}"
            print_info "Web UI: http://localhost:${HOST_PORT_HTTP}/dashboard"
        else
            print_warn "服务健康: 异常"
        fi
        
        ***REMOVED*** 显示容器信息
        echo
        print_info "容器信息:"
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        print_warn "容器状态: 已停止"
        print_info "使用 '$0 start' 启动服务"
    fi
}

***REMOVED*** 显示日志
logs() {
    if ! container_exists; then
        print_error "容器不存在: ${CONTAINER_NAME}"
        exit 1
    fi
    
    docker logs -f ${CONTAINER_NAME}
}

***REMOVED*** 显示使用说明
usage() {
    cat << EOF
Qdrant 服务管理脚本

用法: $0 <command>

命令:
    start       启动 Qdrant 服务（如果容器不存在则创建）
    stop        停止 Qdrant 服务
    restart     重启 Qdrant 服务
    status      显示服务状态
    logs        显示服务日志（实时）
    remove      删除容器（保留数据）
    clean       删除容器和数据（危险操作）
    help        显示此帮助信息

示例:
    $0 start          ***REMOVED*** 启动服务
    $0 status          ***REMOVED*** 查看状态
    $0 logs            ***REMOVED*** 查看日志
    $0 stop            ***REMOVED*** 停止服务

配置:
    容器名称: ${CONTAINER_NAME}
    HTTP 端口: ${HOST_PORT_HTTP}
    gRPC 端口: ${HOST_PORT_GRPC}
    存储路径: ${STORAGE_PATH}
    Docker 镜像: ${IMAGE_NAME}

EOF
}

***REMOVED*** 主函数
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
        remove)
            remove
            ;;
        clean)
            clean
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            if [ -z "${1:-}" ]; then
                usage
            else
                print_error "未知命令: $1"
                echo
                usage
                exit 1
            fi
            ;;
    esac
}

***REMOVED*** 执行主函数
main "$@"

