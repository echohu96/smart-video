# Smart Video - Dockerfile
# 多阶段构建，优化镜像大小

# ============================================
# 构建阶段
# ============================================
FROM python:3.11-slim as builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖（构建时）
# 包括编译工具和 Whisper 所需的依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖到临时目录
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================
# 运行阶段
# ============================================
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装运行时依赖
# FFmpeg 用于音频处理（Whisper 转录需要）
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制 Python 依赖
COPY --from=builder /root/.local /root/.local

# 确保 Python 可以找到本地安装的包
ENV PATH=/root/.local/bin:$PATH

# 复制项目文件
COPY src/ ./src/
COPY env.example ./env.example

# 创建必要的目录
RUN mkdir -p /app/output/summaries \
    /app/cache/subtitles \
    /app/cache/temp

# 设置环境变量
# PYTHONUNBUFFERED=1 确保 Python 输出不被缓冲，实时显示
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# 默认命令（可以覆盖）
# 使用 -m 方式运行，确保包导入正确
CMD ["python", "-m", "src.main", "--help"]

