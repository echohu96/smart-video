# Whisper 转录问题排查指南

## 问题：转录进度不显示，程序自动退出

### 可能的原因

1. **输出缓冲问题**
   - Docker 环境可能缓冲了 stderr 输出
   - Python 的输出可能被缓冲

2. **转录时间较长**
   - 21 分钟的视频可能需要 5-10 分钟转录时间
   - 在转录完成前，可能看不到进度输出

3. **内存不足**
   - Whisper 需要足够的内存
   - 当前配置：4G 内存限制

4. **模型加载问题**
   - 首次使用需要下载模型（约 139MB）
   - 模型加载可能需要时间

### 已实施的解决方案

代码中已经添加了以下改进：

1. **stderr 重新配置**
   ```python
   sys.stderr.reconfigure(line_buffering=True, encoding='utf-8')
   ```

2. **强制刷新输出**
   ```python
   sys.stdout.flush()
   sys.stderr.flush()
   ```

3. **详细错误信息**
   - 添加了完整的异常堆栈跟踪
   - 输出详细的错误类型和消息

4. **调试日志**
   - 在关键步骤添加了日志输出
   - 可以追踪程序执行流程

### 检查配置

#### 1. 环境变量检查

确保 `.env` 文件中包含：

```bash
# 确保 Python 输出不被缓冲
PYTHONUNBUFFERED=1

# Whisper 配置
USE_WHISPER=true
WHISPER_MODEL=base  # 或 tiny/small/medium/large
```

#### 2. Docker 配置检查

`Dockerfile` 中已设置：
```dockerfile
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8
```

`docker-compose.yml` 中已设置：
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # Whisper 需要足够内存
```

#### 3. 运行命令

使用以下命令运行，确保能看到所有输出：

```bash
# 构建镜像
docker-compose build

# 运行（使用 --no-deps 避免依赖问题）
docker-compose run --rm --no-deps smart-video \
  python -m src.main \
  --url "https://www.youtube.com/watch?v=YOUR_VIDEO_ID" \
  --use-whisper
```

### 诊断步骤

#### 1. 检查日志输出

运行后，查看是否有以下日志：
- `[Whisper 转录进行中... 进度会实时显示]`
- `开始调用 Whisper transcribe 方法...`
- 任何错误信息

#### 2. 检查模型加载

首次运行时，应该看到：
```
100%|███████████████████████████████████████| 139M/139M [00:35<00:00, 4.05MiB/s]
```

#### 3. 检查转录进度

如果看到 `[Whisper 转录进行中...]` 但没有后续输出，可能是：
- 转录正在进行中（需要等待 5-10 分钟）
- 转录过程出错（应该会显示错误信息）

#### 4. 检查内存使用

如果内存不足，可能会：
- 程序崩溃
- 转录失败
- 没有错误信息（被系统杀死）

### 常见问题

#### Q: 为什么看不到 Whisper 的进度条？

A: Whisper 的 `verbose=True` 会将进度输出到 stderr。如果看不到，可能是：
1. Docker 缓冲了输出（已通过 `PYTHONUNBUFFERED=1` 解决）
2. 转录正在进行中，但进度更新较慢
3. 转录过程出错（应该会显示错误）

#### Q: 程序运行后立即退出，没有错误信息？

A: 可能的原因：
1. 转录过程出错，但错误被捕获了（检查日志）
2. 内存不足，程序被系统杀死（检查 Docker 日志）
3. 音频文件有问题（检查下载的音频文件）

#### Q: 如何确认转录是否在进行？

A: 可以通过以下方式：
1. 检查 CPU 使用率（应该较高）
2. 检查内存使用（应该占用较多）
3. 等待足够长的时间（21 分钟视频需要 5-10 分钟）

### 调试建议

1. **增加超时时间**
   ```bash
   timeout 1200 docker-compose run --rm smart-video ...
   ```

2. **查看完整日志**
   ```bash
   docker-compose run --rm smart-video ... 2>&1 | tee output.log
   ```

3. **检查容器资源使用**
   ```bash
   docker stats smart-video
   ```

4. **使用更小的模型测试**
   在 `.env` 中设置：
   ```bash
   WHISPER_MODEL=tiny  # 更快，但准确度较低
   ```

### 如果问题仍然存在

1. 检查 Docker 日志：
   ```bash
   docker-compose logs smart-video
   ```

2. 检查系统资源：
   ```bash
   docker stats
   ```

3. 尝试本地运行（不使用 Docker）：
   ```bash
   python -m src.main --url "..." --use-whisper
   ```

4. 提供完整的错误日志和系统信息

