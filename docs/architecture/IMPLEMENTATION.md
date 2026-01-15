# 实现细节文档

## 核心模块实现细节

### 1. 字幕下载模块（不下载视频）

#### 核心设计原则
- ✅ **只下载字幕文件**（体积小，通常几KB到几十KB）
- ❌ **不下载视频文件**（节省存储空间）
- ⚠️ **无字幕时临时下载音频**（仅用于转录，转录后立即删除）

#### 使用 yt-dlp 的优势
- TubeArchivist 也使用 yt-dlp，成熟稳定
- 支持多种字幕格式（SRT, VTT, TTML）
- 可以只下载字幕，不下载视频/音频
- 支持代理和重试机制

#### 实现要点
```python
# 关键配置 - 只下载字幕，不下载视频
ydl_opts = {
    'skip_download': True,        # 关键：跳过视频/音频下载
    'writesubtitles': True,       # 下载字幕
    'writeautomaticsub': True,    # 下载自动生成字幕
    'subtitleslangs': ['en', 'zh', 'zh-Hans', 'zh-Hant'],  # 字幕语言
    'subtitlesformat': 'vtt',     # 字幕格式
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': False,
    'no_warnings': False,
}

# 如果无字幕，才临时下载音频用于转录
if no_subtitles_available:
    audio_opts = {
        'format': 'bestaudio/best',  # 只下载音频
        'skip_download': False,      # 需要下载音频
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }],
    }
    # 转录后立即删除音频文件
```

### 2. 字幕处理策略

#### 优先级
1. **手动字幕**（最准确，优先使用）
2. **自动生成字幕**（YouTube 自动生成，次优选择）
3. **语音识别**（使用 Whisper，仅在无字幕时使用）
   - 临时下载音频文件
   - 使用 Whisper 转录
   - **立即删除音频文件**（不保存）

#### 字幕格式转换
- VTT → 纯文本（去除时间戳）
- 保留时间戳信息（用于章节定位）

### 3. AI 总结策略

#### 提示词设计（示例）

```python
SUMMARY_PROMPT = """
请分析以下视频转录内容，生成一份结构化的总结。

视频标题：{title}
视频作者：{author}
视频时长：{duration}

转录内容：
{transcript}

请按照以下格式输出：

# 视频总结

## 基本信息
- 标题：{title}
- 作者：{author}
- 时长：{duration}

## 核心内容摘要
[2-3段总结视频主要内容]

## 关键要点
1. [要点1]
2. [要点2]
3. [要点3]
...

## 详细章节
### 章节1：[标题]
[内容]

### 章节2：[标题]
[内容]

## 总结
[整体评价和收获]
"""
```

#### AI 提供商选择

**OpenAI GPT-4/GPT-3.5**
- 优点：质量高、响应快
- 缺点：需要 API Key、有成本

**Claude (Anthropic)**
- 优点：长文本处理能力强
- 缺点：需要 API Key

**本地 LLM（Ollama/LocalAI）**
- 优点：免费、隐私保护
- 缺点：需要本地资源、可能质量较低

### 4. Markdown 输出格式

#### 标准模板结构

```markdown
# [视频标题]

**作者**：{author}  
**发布时间**：{publish_date}  
**视频时长**：{duration}  
**🔗 视频链接**：[点击查看原视频]({url}) | {url}

> 💡 **提示**：本文档为视频内容总结，如需观看原视频，请点击上方链接。

---

## 📋 内容摘要

[AI 生成的摘要]

## 🔑 关键要点

1. [要点1]
2. [要点2]
3. [要点3]

## 📚 详细内容

### 章节 1：[标题]
[内容]

### 章节 2：[标题]
[内容]

## 💡 总结与思考

[总结]

---

*本文档由 Smart Video 自动生成*
*生成时间：{timestamp}*
```

### 5. 错误处理

#### 常见错误场景

1. **视频不可用**
   - 视频已删除
   - 地区限制
   - 年龄限制

2. **字幕不可用**
   - 无字幕视频
   - 语言不匹配
   - 字幕格式错误

3. **AI API 错误**
   - API Key 无效
   - 配额超限
   - 网络错误

4. **存储空间不足**（极少发生，因为不保存视频）
   - 字幕文件很小（通常 < 100KB）
   - 临时音频文件会在转录后立即删除
   - 定期清理字幕缓存（可选）

## 性能优化

### 1. 缓存策略
- **字幕文件缓存**（可选）：已下载的字幕可以缓存，避免重复下载
- **总结结果缓存**：已总结的视频不重复处理（使用视频ID判断）
- **不缓存视频文件**：不保存任何视频/音频文件
- 使用视频ID或URL哈希判断是否已处理

### 2. 并发处理
- 多视频批量处理时使用线程池
- 下载和 AI 处理可以异步进行

### 3. 资源管理
- **不保存视频文件**：从一开始就不下载视频
- **临时音频文件**：无字幕时临时下载音频，转录后立即删除
- **字幕文件**：可选缓存，体积小（通常 < 100KB）
- **定期清理**：定期清理临时文件和过期字幕缓存

## 配置管理

### 环境变量配置

```env
# AI 配置
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4-turbo-preview
ANTHROPIC_API_KEY=sk-ant-xxx

# 下载配置（不下载视频，只下载字幕）
SUBTITLE_LANGUAGES=en,zh,zh-Hans,zh-Hant
AUTO_DOWNLOAD_SUBTITLES=true
CACHE_SUBTITLES=true  # 是否缓存字幕文件（可选）

# 路径配置
CACHE_DIR=./cache
SUBTITLE_CACHE_DIR=./cache/subtitles  # 字幕缓存目录（可选）
TEMP_DIR=./cache/temp                 # 临时文件目录（无字幕时临时音频）
OUTPUT_DIR=./output/summaries         # 总结输出目录

# 可选：Whisper
USE_WHISPER=false
WHISPER_MODEL=base  # tiny, base, small, medium, large

# 代理配置（如果需要）
HTTP_PROXY=
HTTPS_PROXY=
```

## 测试策略

### 单元测试
- 字幕解析测试
- Markdown 生成测试
- 配置加载测试

### 集成测试
- 完整流程测试（下载→提取→总结→生成）
- 错误场景测试
- 不同视频类型测试

### 测试数据
- 准备几个不同类型的 YouTube 视频 URL
- 有字幕/无字幕视频
- 不同语言视频
- 长视频/短视频

## 部署建议

### 本地运行
```bash
python src/main.py --url "https://youtube.com/watch?v=xxx"
```

### Docker 部署（未来）
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装 FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY output/ ./output/
COPY cache/ ./cache/

CMD ["python", "src/main.py"]
```

## 未来扩展点

### 1. Web 界面
- FastAPI + React
- 文件上传/URL 输入
- 实时处理状态
- 历史记录查看

### 2. 定时任务
- 使用 Celery 或 APScheduler
- 监控 YouTube 频道 RSS
- 自动下载和总结新视频

### 3. 数据库
- SQLite（轻量）或 PostgreSQL
- 存储视频元数据
- 总结历史记录
- 用户配置

### 4. 多平台支持
- Bilibili（需要 bilibili-api）
- Vimeo（yt-dlp 支持）
- 本地视频文件

## 参考资源

- [yt-dlp 文档](https://github.com/yt-dlp/yt-dlp)
- [TubeArchivist 源码](https://github.com/tubearchivist/tubearchivist)
- [OpenAI API 文档](https://platform.openai.com/docs)
- [Whisper 文档](https://github.com/openai/whisper)

