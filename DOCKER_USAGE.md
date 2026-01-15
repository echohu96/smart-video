# Docker 使用指南

## 快速开始

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp env.example .env

# 编辑 .env 文件，至少配置 OpenAI API Key
nano .env  # 或使用你喜欢的编辑器
```

**必需配置**：
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. 启动服务

```bash
# 使用快速设置脚本（推荐）
./scripts/docker-setup.sh

# 或手动启动
docker-compose up -d
```

### 3. 使用服务

#### 方式一：使用 run --rm（推荐，执行完自动删除容器）

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

#### 方式二：使用 exec（容器常驻）

```bash
# 基础使用（有字幕的视频）
docker-compose exec smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx"

# 无字幕视频（使用 Whisper 转录）
docker-compose exec smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx" --use-whisper
```

## 常用命令

### 查看日志

```bash
# 查看实时日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100
```

### 进入容器

```bash
# 使用 run --rm（临时容器，退出后删除）
docker-compose run --rm smart-video bash

# 使用 exec（需要容器已运行）
docker-compose exec smart-video bash
```

### 停止服务

```bash
docker-compose down
```

### 重启服务

```bash
docker-compose restart
```

## 注意事项

1. **首次使用 Whisper**：首次使用 Whisper 时会自动下载模型（可能需要几分钟），模型会缓存在容器内。

2. **资源要求**：使用 Whisper 时建议至少 2GB 内存，docker-compose.yml 中已配置 4GB 内存限制。

3. **输出文件**：生成的 Markdown 文件保存在 `./output/summaries/` 目录中。

4. **缓存**：字幕文件会缓存在 `./cache/subtitles/` 目录中，可以节省重复下载时间。

## 故障排查

### 容器无法启动

```bash
# 检查日志
docker-compose logs smart-video

# 检查配置
docker-compose config
```

### API Key 错误

确保 `.env` 文件中已正确配置 `OPENAI_API_KEY`。

### 网络问题

如果无法访问 YouTube，可以在 `.env` 文件中配置代理：
```env
HTTP_PROXY=http://proxy.example.com:8080
HTTPS_PROXY=http://proxy.example.com:8080
```

## 更多信息

详细部署文档请参考：[部署指南](./docs/guides/DEPLOYMENT.md)

