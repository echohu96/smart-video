#!/bin/bash

# Smart Video Docker 快速设置脚本
# 自动检查环境、创建配置文件、构建镜像并启动服务

set -e

# 颜色定义
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

# 检查 Docker
check_docker() {
    print_info "检查 Docker 环境..."
if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

    print_info "Docker 环境检查通过"
}

# 创建 .env 文件
create_env_file() {
if [ ! -f .env ]; then
        print_info "创建 .env 文件..."
    cp env.example .env
        print_warn "请编辑 .env 文件，填入你的 API Key"
        print_warn "至少需要配置 OPENAI_API_KEY"
else
        print_info ".env 文件已存在，跳过创建"
fi
}

# 创建必要的目录
create_directories() {
    print_info "创建必要的目录..."
mkdir -p output/summaries
mkdir -p cache/subtitles
mkdir -p cache/temp
    print_info "目录创建完成"
}

# 构建 Docker 镜像
build_image() {
    print_info "构建 Docker 镜像（这可能需要几分钟）..."
docker-compose build
    print_info "镜像构建完成"
}

# 启动服务
start_service() {
    print_info "启动服务..."
docker-compose up -d
    print_info "服务启动完成"
}

# 显示使用说明
show_usage() {
    echo ""
    print_info "=========================================="
    print_info "Smart Video Docker 部署完成！"
    print_info "=========================================="
    echo ""
    print_info "使用方式："
    echo "  1. 处理视频："
    echo "     docker-compose exec smart-video python src/main.py --url \"https://www.youtube.com/watch?v=xxx\""
    echo ""
    echo "  2. 无字幕视频（使用 Whisper）："
    echo "     docker-compose exec smart-video python src/main.py --url \"https://www.youtube.com/watch?v=xxx\" --use-whisper"
echo ""
    echo "  3. 进入容器："
    echo "     docker-compose exec smart-video bash"
echo ""
    echo "  4. 查看日志："
    echo "     docker-compose logs -f"
echo ""
    print_warn "请确保 .env 文件中已配置 API Key！"
echo ""
}

# 主函数
main() {
echo ""
    print_info "=========================================="
    print_info "Smart Video Docker 快速设置"
    print_info "=========================================="
echo ""
    
    check_docker
    create_env_file
    create_directories
    build_image
    start_service
    show_usage
}

# 执行主函数
main
