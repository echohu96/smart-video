# Smart Video - 视频总结工具架构方案

## 项目概述

Smart Video 是一个智能视频内容总结工具，主要用于学习和总结视频内容。**当前版本支持 YouTube 视频，采用可扩展的多平台架构设计，未来将扩展支持 Bilibili、Vimeo 等更多视频平台。**

## 核心功能

1. **字幕下载**：从 YouTube 下载视频字幕（不下载视频文件）
2. **内容提取**：解析字幕文件，提取文本内容
3. **AI 总结**：使用 AI 分析并生成结构化总结
4. **输出管理**：生成 Markdown 格式的总结文件（包含视频 URL）

**重要设计原则**：
- ❌ **不保存视频源文件**（节省存储空间）
- ✅ **只下载字幕文件**（体积小，包含完整文本）
- ✅ **无字幕时临时下载音频**（仅用于转录，转录后立即删除）
- ✅ **保存视频 URL**（在 Markdown 中，方便后续查看原视频）

## 技术架构

### 1. 整体架构设计

```
┌─────────────────────────────────────────────────────────┐
│                    Smart Video System                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │  Video Input │ -> │  Subtitle    │ -> │  Extract  │ │
│  │   (YouTube)  │    │  Downloader  │    │  Content  │ │
│  │   (URL only) │    │  (No Video!) │    │  (Text)   │ │
│  └──────────────┘    └──────────────┘    └───────────┘ │
│                                                           │
│         │                      │                │         │
│         v                      v                v         │
│  ┌──────────────────────────────────────────────────┐   │
│  │           AI Summary Engine                      │   │
│  │  - Transcript Analysis                           │   │
│  │  - Content Summarization                        │   │
│  │  - Key Points Extraction                        │   │
│  └──────────────────────────────────────────────────┘   │
│                                                           │
│         │                                                │
│         v                                                │
│  ┌──────────────┐                                       │
│  │  MD Generator │                                       │
│  │  (Output)     │                                       │
│  └──────────────┘                                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 2. 技术栈选择

#### 后端核心
- **Python 3.10+**：主要开发语言
- **yt-dlp**：YouTube 字幕下载（**不下载视频**，只下载字幕）
- **FFmpeg**：仅在无字幕时临时处理音频（转录后立即删除）
- **Whisper** 或 **OpenAI Whisper API**：仅在无字幕视频时使用（临时下载音频→转录→删除音频）
- **OpenAI API** / **Claude API** / **本地 LLM**：AI 总结引擎

#### 可选依赖（参考 TubeArchivist）
- **Elasticsearch**：如果未来需要全文搜索功能
- **Redis**：任务队列和缓存（如果做异步处理）

#### 前端（未来扩展）
- **React** / **Vue.js**：Web 界面
- **FastAPI** / **Flask**：API 服务

### 3. 核心模块设计

#### 3.1 字幕下载模块 (`subtitle_downloader.py`)
```python
功能：
- 接收 YouTube URL
- 使用 yt-dlp 只下载字幕文件（不下载视频）
- 优先使用手动字幕，其次自动生成字幕
- 提取视频元数据（标题、作者、时长、URL等）
- 如果无字幕，临时下载音频用于转录（转录后立即删除）
- 处理下载失败和重试逻辑
- 不保存任何视频/音频文件
```

#### 3.2 内容提取模块 (`content_extractor.py`)
```python
功能：
- 解析字幕文件（SRT/VTT），提取纯文本
- 如果无字幕：临时下载音频 → Whisper 转录 → 立即删除音频文件
- 提取视频元数据（标题、作者、时长、URL、发布时间等）
- 生成时间戳索引（可选，用于章节定位）
```

#### 3.3 AI 总结模块 (`ai_summarizer.py`)
```python
功能：
- 接收转录文本
- 调用 AI API 进行总结
- 提取关键点、章节、摘要
- 生成结构化内容
```

#### 3.4 Markdown 生成模块 (`md_generator.py`)
```python
功能：
- 将 AI 总结结果格式化为 Markdown
- 包含视频信息（标题、作者、URL、时长等）
- 包含摘要、关键点、章节等
- **重要：保存视频 URL**，方便后续查看原视频
- 支持自定义模板
```

#### 3.5 主控制器 (`main.py` / `cli.py`)
```python
功能：
- 命令行接口
- 流程编排
- 错误处理
- 日志记录
```

## 项目结构

```
smart-video/
├── README.md
├── ARCHITECTURE.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── src/
│   ├── __init__.py
│   ├── main.py              # 主入口
│   ├── cli.py                # CLI 接口
│   │
│   ├── downloader/
│   │   ├── __init__.py
│   │   ├── subtitle_downloader.py  # 只下载字幕，不下载视频
│   │   └── yt_dlp_wrapper.py
│   │
│   ├── extractor/
│   │   ├── __init__.py
│   │   ├── content_extractor.py
│   │   ├── subtitle_parser.py
│   │   └── whisper_transcriber.py  # 可选
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── summarizer.py
│   │   ├── prompts.py        # AI 提示词模板
│   │   └── providers/        # 支持多个 AI 提供商
│   │       ├── openai.py
│   │       ├── claude.py
│   │       └── local_llm.py
│   │
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── md_generator.py
│   │   └── templates.py      # MD 模板
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       ├── logger.py
│       └── file_manager.py
│
├── output/                   # 输出目录
│   └── summaries/            # 只保存 Markdown 总结文件
│
├── cache/                    # 缓存目录（临时文件）
│   ├── subtitles/            # 字幕文件缓存（可选，节省重复下载）
│   └── temp/                 # 临时音频文件（无字幕时，转录后立即删除）
│
└── tests/
    ├── test_downloader.py
    ├── test_extractor.py
    ├── test_summarizer.py
    └── test_generator.py
```

## 实现步骤

### Phase 1: 核心功能（MVP + Whisper）
1. ✅ 项目初始化
2. ✅ 实现字幕下载模块（yt-dlp，**只下载字幕，不下载视频**）
3. ✅ 实现字幕提取和解析
4. ✅ 实现基础 AI 总结（使用 OpenAI API）
5. ✅ 实现 Markdown 生成（包含视频 URL）
6. ✅ 实现 CLI 接口
7. ✅ 支持无字幕视频（Whisper 转录）
8. ✅ 多平台架构设计（当前实现 YouTube，为未来扩展预留接口）

### Phase 2: 增强功能
1. ✅ 支持无字幕视频（Whisper 转录）
2. 优化 AI 提示词，提升总结质量
3. 支持多种 AI 提供商（Claude 等）
4. ✅ 添加视频元数据提取
5. ✅ 错误处理和重试机制

### Phase 3: 扩展功能
1. Web 界面开发
2. 定时任务系统（定时拉取指定频道）
3. 数据库存储（视频历史、总结记录）
4. 批量处理功能
5. 支持更多视频平台

## 关于 TubeArchivist 的使用

**建议**：不完全依赖 TubeArchivist，而是参考其设计思路

**原因**：
1. TubeArchivist 是一个完整的媒体服务器系统，功能复杂
2. 我们只需要下载和字幕提取功能
3. 直接使用 yt-dlp 更轻量、更灵活

**参考 TubeArchivist 的部分**：
- yt-dlp 的配置和参数设置
- 字幕下载和处理逻辑
- 视频元数据提取方式
- 错误处理机制

## 配置示例

### `.env.example`
```env
# AI Provider
OPENAI_API_KEY=your_openai_api_key
# 或
ANTHROPIC_API_KEY=your_claude_api_key

# 下载配置（不下载视频，只下载字幕）
SUBTITLE_CACHE_DIR=./cache/subtitles  # 字幕缓存（可选）
TEMP_DIR=./cache/temp                 # 临时文件目录（无字幕时临时音频）
OUTPUT_PATH=./output/summaries        # 总结输出目录

# 可选：Whisper
USE_WHISPER=false
WHISPER_MODEL=base

# 可选：代理
PROXY_URL=
```

## 使用示例（CLI）

```bash
# 基础使用
python src/main.py --url "https://www.youtube.com/watch?v=xxx"

# 指定输出路径
python src/main.py --url "https://www.youtube.com/watch?v=xxx" --output ./my_summary.md

# 使用不同的 AI 提供商
python src/main.py --url "https://www.youtube.com/watch?v=xxx" --ai-provider claude

# 批量处理
python src/main.py --batch urls.txt
```

## 未来扩展方向

1. **Web 界面**
   - 上传视频链接
   - 查看总结历史
   - 导出多种格式

2. **定时任务**
   - 监控指定 YouTube 频道
   - 自动下载和总结新视频
   - 邮件/通知推送

3. **多平台支持**（架构已设计，待实现）
   - ✅ YouTube（已实现）
   - 🔄 Bilibili（未来支持）
   - 🔄 Vimeo（未来支持）
   - 🔄 本地视频文件（未来支持）
   
   **架构设计**：采用 `VideoPlatform` 抽象基类，所有平台实现统一接口，便于扩展。

4. **高级功能**
   - 视频章节自动识别
   - 关键帧提取
   - 多语言支持
   - 总结模板自定义

## 部署方案

### Docker 一键部署（推荐）

项目支持通过 Docker 和 Docker Compose 进行一键部署，支持跨平台（Linux、macOS、Windows）。

**优势：**
- ✅ 无需手动配置 Python 环境
- ✅ 自动安装所有依赖（包括 FFmpeg）
- ✅ 跨平台部署，环境一致
- ✅ 数据持久化，配置简单
- ✅ 易于更新和维护

**快速部署：**
```bash
# 1. 克隆项目
git clone https://github.com/echohu96/smart-video.git
cd smart-video

# 2. 配置环境变量
cp env.example .env
# 编辑 .env，填入 API Key

# 3. 一键启动
docker-compose up -d

# 4. 使用服务
docker-compose exec smart-video python src/main.py --url "https://youtube.com/watch?v=xxx"
```

**详细部署文档**：参见 [部署指南](../guides/DEPLOYMENT.md)

### 本地部署

如果需要本地部署，需要手动安装：
- Python 3.10+
- FFmpeg
- Python 依赖包（requirements.txt）

详见 README.md 中的安装说明。

## 注意事项

1. **API 成本**：AI 总结会产生 API 调用费用，需要考虑成本控制
2. **下载速度**：字幕文件很小，下载速度快
3. **存储空间**：**不保存视频文件**，只保存字幕和总结，存储需求极小
4. **无字幕视频**：如果视频无字幕，需要临时下载音频进行转录（转录后立即删除）
5. **视频 URL**：总结文件中保存视频 URL，方便后续查看原视频
6. **版权问题**：仅用于个人学习，注意使用合规性
7. **Docker 部署**：推荐使用 Docker 部署，避免环境配置问题

