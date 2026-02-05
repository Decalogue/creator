#!/bin/bash

# Docker 镜像加速器配置脚本
# 用于配置国内 Docker 镜像源，解决拉取镜像超时问题

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否为 root 用户
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "此脚本需要 root 权限，请使用 sudo 运行"
        exit 1
    fi
}

# 配置 Docker 镜像加速器
configure_mirror() {
    print_info "配置 Docker 镜像加速器..."
    
    DOCKER_DAEMON_JSON="/etc/docker/daemon.json"
    
    # 国内镜像源列表
    MIRRORS=(
        "https://docker.mirrors.ustc.edu.cn"
        "https://hub-mirror.c.163.com"
        "https://mirror.baidubce.com"
    )
    
    # 创建镜像源 JSON 数组
    MIRRORS_JSON=""
    for mirror in "${MIRRORS[@]}"; do
        if [ -z "$MIRRORS_JSON" ]; then
            MIRRORS_JSON="\"$mirror\""
        else
            MIRRORS_JSON="$MIRRORS_JSON, \"$mirror\""
        fi
    done
    
    # 备份现有配置
    if [ -f "$DOCKER_DAEMON_JSON" ]; then
        print_info "备份现有配置到 ${DOCKER_DAEMON_JSON}.bak"
        cp "$DOCKER_DAEMON_JSON" "${DOCKER_DAEMON_JSON}.bak"
    fi
    
    # 创建或更新配置
    print_info "更新 Docker 配置..."
    cat > "$DOCKER_DAEMON_JSON" << EOF
{
  "registry-mirrors": [
    $MIRRORS_JSON
  ]
}
EOF
    
    print_info "配置已更新"
    print_info "配置文件内容:"
    cat "$DOCKER_DAEMON_JSON"
    
    # 重启 Docker 服务
    print_info "重启 Docker 服务..."
    if systemctl restart docker; then
        print_info "Docker 服务已重启"
        sleep 2
        
        # 验证配置
        if docker info | grep -q "Registry Mirrors"; then
            print_info "镜像加速器配置成功！"
            docker info | grep -A 10 "Registry Mirrors"
        else
            print_warn "配置可能未生效，请检查 Docker 日志"
        fi
    else
        print_error "Docker 服务重启失败"
        exit 1
    fi
}

# 测试镜像拉取
test_pull() {
    print_info "测试镜像拉取..."
    if docker pull hello-world:latest; then
        print_info "镜像拉取测试成功！"
        docker rmi hello-world:latest &> /dev/null || true
    else
        print_error "镜像拉取测试失败，请检查网络连接"
        exit 1
    fi
}

# 主函数
main() {
    print_info "Docker 镜像加速器配置脚本"
    echo
    
    check_root
    
    configure_mirror
    
    echo
    print_info "是否测试镜像拉取？(y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        test_pull
    fi
    
    echo
    print_info "配置完成！现在可以尝试运行: ./unimem/scripts/qdrant_server.sh start"
}

main "$@"

