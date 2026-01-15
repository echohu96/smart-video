# 部署指南

本文档描述如何使用 Docker 一键部署 Smart Video 项目。

## 部署方式

Smart Video 支持通过 Docker 和 Docker Compose 进行一键部署，无需手动配置环境，支持跨平台部署（Linux、macOS、Windows）。

## 前置要求

### 必需
- Docker 20.10+ 
- Docker Compose 2.0+（或使用 Docker Desktop，已包含 Compose）

### 可选
- 至少 2GB 可用磁盘空间（用于缓存和输出）
- 网络连接（用于下载字幕和调用 AI API）

## 快速开始

### 方式一：使用快速设置脚本（推荐）🚀

```bash
# 1. 克隆项目
git clone https://github.com/echohu96/smart-video.git
cd smart-video

# 2. 运行快速设置脚本
./scripts/docker-setup.sh

# 脚本会自动：
# - 检查 Docker 环境
# - 创建 .env 文件（如果不存在）
# - 创建必要的目录
# - 构建 Docker 镜像
# - 启动服务
```

### 方式二：手动部署

#### 1. 克隆项目

```bash
git clone https://github.com/echohu96/smart-video.git
cd smart-video
```

#### 2. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，填入你的 API Key
# 至少需要配置一个 AI 提供商的 API Key
nano .env  # 或使用你喜欢的编辑器
```

**必需配置：**
```env
# 至少配置一个 AI 提供商
OPENAI_API_KEY=your_openai_api_key_here
# 或
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

#### 3. 启动服务

```bash
# 使用 Docker Compose 一键启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 4. 使用服务

**推荐方式：使用 `run --rm`（执行完自动删除容器）**

```bash
# 基础使用（有字幕的视频）
docker-compose run --rm smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx"

# 无字幕视频（使用 Whisper 转录）
docker-compose run --rm smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx" --use-whisper

# 强制使用 Whisper（即使有字幕）
docker-compose run --rm smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx" --force-whisper

# 指定输出文件
docker-compose run --rm smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx" --output my_summary.md
```

**或者使用 `exec`（需要容器已运行）**

```bash
# 先启动容器
docker-compose up -d

# 然后执行命令
docker-compose exec smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx"

# 进入容器交互式使用
docker-compose exec smart-video bash
```

## Docker 配置说明

### Dockerfile

项目使用多阶段构建，优化镜像大小：

1. **构建阶段**：安装 Python 依赖
2. **运行阶段**：最小化运行时镜像

### docker-compose.yml

包含以下服务：

- **smart-video**：主应用服务
  - 自动安装依赖
  - 挂载配置和输出目录
  - 支持环境变量配置

### 数据持久化

以下目录会被挂载到宿主机，确保数据持久化：

- `./output` → `/app/output` - 总结输出目录
- `./cache` → `/app/cache` - 缓存目录（字幕、临时文件）
- `.env` → `/app/.env` - 环境变量配置

## 配置选项

### 环境变量

所有配置通过 `.env` 文件管理，详见 `env.example`。

**关键配置：**

```env
# AI 提供商（至少配置一个）
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4-turbo-preview

# 或使用 Claude
ANTHROPIC_API_KEY=sk-ant-xxx

# 路径配置（可选，使用默认值即可）
OUTPUT_DIR=./output/summaries
CACHE_DIR=./cache
SUBTITLE_CACHE_DIR=./cache/subtitles
TEMP_DIR=./cache/temp

# 字幕配置
SUBTITLE_LANGUAGES=en,zh,zh-Hans,zh-Hant
AUTO_DOWNLOAD_SUBTITLES=true

# Whisper 配置（无字幕时使用）
USE_WHISPER=false  # 设置为 true 以默认使用 Whisper
WHISPER_MODEL=base  # 可选: tiny, base, small, medium, large
```

### 端口配置

当前版本为 CLI 工具，无需端口。未来 Web 界面版本会添加端口配置。

## 常用命令

### 启动和停止

```bash
# 启动服务（后台运行）
docker-compose up -d

# 启动服务（前台运行，查看日志）
docker-compose up

# 停止服务
docker-compose down

# 停止并删除数据卷（谨慎使用）
docker-compose down -v
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs

# 查看实时日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100
```

### 执行命令

**推荐：使用 `run --rm`（执行完自动删除容器，显示日志）**

```bash
# 执行单次命令（有字幕视频）
docker-compose run --rm smart-video python -m src.main --url "https://youtube.com/watch?v=xxx"

# 无字幕视频（使用 Whisper）
docker-compose run --rm smart-video python -m src.main --url "https://youtube.com/watch?v=xxx" --use-whisper

# 查看实时日志
docker-compose run --rm smart-video python -m src.main --url "https://youtube.com/watch?v=xxx" 2>&1 | tee output.log
```

**或者使用 `exec`（需要容器已运行）**

```bash
# 执行单次命令
docker-compose exec smart-video python -m src.main --url "https://youtube.com/watch?v=xxx"

# 进入容器
docker-compose exec smart-video bash

# 查看容器状态
docker-compose ps
```

### 更新和重建

```bash
# 拉取最新代码
git pull

# 重建镜像（代码更新后）
docker-compose build

# 重建并重启
docker-compose up -d --build

# 强制重建（不使用缓存）
docker-compose build --no-cache
```

## 跨平台部署

### Linux

```bash
# 标准 Linux 发行版
sudo apt-get update
sudo apt-get install docker.io docker-compose

# 或使用 Docker 官方仓库
curl -fsSL https://get.docker.com | sh
```

### macOS

```bash
# 使用 Homebrew
brew install --cask docker

# 或直接下载 Docker Desktop
# https://www.docker.com/products/docker-desktop
```

### Windows

1. 下载并安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 确保启用 WSL 2 后端（推荐）
3. 按照上述步骤操作

## 数据管理

### 备份

```bash
# 备份输出目录
tar -czf backup-$(date +%Y%m%d).tar.gz output/

# 备份配置
cp .env .env.backup
```

### 清理

```bash
# 清理缓存（保留字幕缓存）
docker-compose exec smart-video rm -rf /app/cache/temp/*

# 清理所有缓存
docker-compose exec smart-video rm -rf /app/cache/*

# 清理旧的总结文件（保留最近 30 天）
find output/summaries -type f -mtime +30 -delete
```

## 故障排查

### 常见问题

#### 1. 容器无法启动

```bash
# 检查日志
docker-compose logs smart-video

# 检查配置
docker-compose config

# 验证环境变量
docker-compose exec smart-video env | grep OPENAI
```

#### 2. API Key 错误

```bash
# 检查 .env 文件
cat .env

# 重新加载配置
docker-compose down
docker-compose up -d
```

#### 3. 网络问题

```bash
# 测试网络连接
docker-compose exec smart-video ping -c 3 youtube.com

# 检查代理配置（如需要）
# 在 .env 中配置 HTTP_PROXY 和 HTTPS_PROXY
```

#### 4. 磁盘空间不足

```bash
# 检查磁盘使用
docker system df

# 清理未使用的镜像和容器
docker system prune -a

# 清理缓存
docker-compose exec smart-video rm -rf /app/cache/temp/*
```

### 调试模式

```bash
# 进入容器调试
docker-compose exec smart-video bash

# 在容器内执行 Python
python src/main.py --url "https://youtube.com/watch?v=xxx" --verbose

# 查看 Python 环境
python --version
pip list
```

## 生产环境建议

### 安全配置

1. **保护 API Key**
   - 不要将 `.env` 文件提交到 Git
   - 使用环境变量或密钥管理服务
   - 定期轮换 API Key

2. **访问控制**
   - 限制容器网络访问
   - 使用防火墙规则
   - 考虑添加身份验证（未来 Web 版本）

### 性能优化

1. **资源限制**
   ```yaml
   # docker-compose.yml
   services:
     smart-video:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

2. **缓存策略**
   - 启用字幕缓存，避免重复下载
   - 定期清理临时文件
   - 考虑使用 Redis 缓存（未来版本）

### 监控和日志

1. **日志管理**
   ```bash
   # 配置日志轮转
   docker-compose logs --tail=1000 > logs/app.log
   ```

2. **健康检查**
   ```yaml
   # docker-compose.yml
   healthcheck:
     test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
     interval: 30s
     timeout: 10s
     retries: 3
   ```

## 未来扩展

### Web 界面部署

未来版本将支持 Web 界面，部署方式将包括：

- Web 服务端口配置
- 反向代理配置（Nginx）
- HTTPS/SSL 配置
- 数据库服务（PostgreSQL/SQLite）

### 定时任务

未来版本将支持定时任务，部署方式将包括：

- Celery 任务队列
- Redis 消息队列
- 定时任务调度器

## 相关文档

- [架构设计](../architecture/ARCHITECTURE.md)
- [设计原则](../architecture/DESIGN_PRINCIPLES.md)
- [实现细节](../architecture/IMPLEMENTATION.md)
- [编码规范](../development/CODING_STANDARDS.md)

