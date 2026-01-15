# Smart Video - 智能视频总结工具

一个用于学习和总结视频内容的智能工具，支持 YouTube 视频的自动下载、转录和 AI 总结。

## 功能特性

- 🎥 **YouTube 视频支持**：自动下载字幕（不下载视频文件）
- 📝 **智能总结**：使用 AI 生成结构化视频总结
- 📄 **Markdown 输出**：生成易读的 Markdown 格式总结文件
- 🎤 **Whisper 转录**：支持无字幕视频的语音转文字
- 🔄 **多平台架构**：采用可扩展设计，当前支持 YouTube，未来将支持 Bilibili、Vimeo 等
- 🚀 **Docker 部署**：一键部署，跨平台支持

## 快速开始

### 方式一：Docker 部署（推荐）🚀

**一键部署，跨平台支持，无需配置环境**

```bash
# 克隆仓库
git clone https://github.com/echohu96/smart-video.git
cd smart-video

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入你的 API Key

# 一键启动
docker-compose up -d

# 使用服务（推荐：执行完自动删除容器）
docker-compose run --rm smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx"

# 无字幕视频（使用 Whisper）
docker-compose run --rm smart-video python -m src.main --url "https://www.youtube.com/watch?v=xxx" --use-whisper
```

**快速使用**：参见 [Docker 使用指南](./DOCKER_USAGE.md)  
**详细部署文档**：参见 [部署指南](./docs/guides/DEPLOYMENT.md)

### 方式二：本地安装

**环境要求：**
- Python 3.10+
- FFmpeg
- OpenAI API Key（或其他 AI 服务 API Key）

**安装步骤：**

```bash
# 克隆仓库
git clone https://github.com/echohu96/smart-video.git
cd smart-video

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp env.example .env
# 编辑 .env 文件，填入你的 API Key
```

**使用示例：**

```bash
# 基础使用
python src/main.py --url "https://www.youtube.com/watch?v=xxx"

# 指定输出文件
python src/main.py --url "https://www.youtube.com/watch?v=xxx" --output summary.md

# 仅保存转录文本（不调用 AI，总结）
python src/main.py --url "https://www.youtube.com/watch?v=xxx" --skip-summary --output transcript.txt
```

## 项目状态

✅ **MVP 已完成** - 核心功能已实现，支持 YouTube 视频总结和 Whisper 转录

## 技术栈

- Python 3.10+
- yt-dlp - 视频下载
- OpenAI API / Claude API - AI 总结
- Whisper（可选）- 语音转文字

## 项目结构

详见 [架构文档](./docs/architecture/ARCHITECTURE.md)

### 文档目录

**架构文档：**
- [架构设计](./docs/architecture/ARCHITECTURE.md) - 系统整体架构
- [设计原则](./docs/architecture/DESIGN_PRINCIPLES.md) - 核心设计理念
- [实现细节](./docs/architecture/IMPLEMENTATION.md) - 技术实现细节

**开发文档：**
- [项目计划](./docs/development/PROJECT_PLAN.md) - 开发计划和里程碑
- [编码规范](./docs/development/CODING_STANDARDS.md) - 编码标准和最佳实践

**使用指南：**
- [部署指南](./docs/guides/DEPLOYMENT.md) - Docker 一键部署指南

**其他：**
- [变更日志](./CHANGELOG.md) - 项目变更历史

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 作者

echohu96
