# 编码规范

本文档定义 Smart Video 项目的编码标准和最佳实践。

## Python 编码规范

### 1. 代码风格

遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范。

### 2. 命名规范

- **模块名**：小写字母，单词间用下划线分隔
  ```python
  subtitle_downloader.py
  content_extractor.py
  ```

- **类名**：大驼峰命名（PascalCase）
  ```python
  class SubtitleDownloader:
      pass
  
  class ContentExtractor:
      pass
  ```

- **函数/方法名**：小写字母，单词间用下划线分隔
  ```python
  def download_subtitle(url: str) -> str:
      pass
  
  def extract_text_from_subtitle(file_path: str) -> str:
      pass
  ```

- **常量**：全大写，单词间用下划线分隔
  ```python
  MAX_RETRY_COUNT = 3
  DEFAULT_SUBTITLE_LANGUAGES = ['en', 'zh']
  ```

- **私有方法/属性**：单下划线前缀
  ```python
  def _validate_url(self, url: str) -> bool:
      pass
  
  self._cache_dir = "./cache"
  ```

### 3. 类型注解

**所有公共 API 必须包含类型注解：**

```python
from typing import List, Optional, Dict

def download_subtitle(
    url: str,
    languages: Optional[List[str]] = None,
    output_dir: str = "./cache"
) -> str:
    """
    下载字幕文件。
    
    Args:
        url: YouTube 视频 URL
        languages: 字幕语言列表
        output_dir: 输出目录
    
    Returns:
        字幕文件路径
    """
    pass
```

### 4. 文档字符串

**所有公共类、函数、方法必须包含文档字符串：**

```python
def process_video(url: str) -> Dict[str, Any]:
    """
    处理视频，生成总结。
    
    流程：
    1. 下载字幕（不下载视频）
    2. 提取文本内容
    3. AI 总结
    4. 生成 Markdown
    
    Args:
        url: YouTube 视频 URL
    
    Returns:
        包含总结信息的字典：
        {
            'title': str,
            'summary': str,
            'output_path': str
        }
    
    Raises:
        SubtitleNotFoundError: 如果视频没有字幕
        AIAPIError: 如果 AI API 调用失败
    
    Note:
        此函数不保存视频文件，只处理字幕。
        详见 docs/architecture/DESIGN_PRINCIPLES.md
    """
    pass
```

### 5. 错误处理

**使用自定义异常类：**

```python
class SmartVideoError(Exception):
    """基础异常类"""
    pass

class SubtitleNotFoundError(SmartVideoError):
    """字幕未找到异常"""
    pass

class DownloadError(SmartVideoError):
    """下载失败异常"""
    pass

class AIAPIError(SmartVideoError):
    """AI API 调用异常"""
    pass
```

**错误处理示例：**

```python
try:
    subtitle_path = download_subtitle(url)
except SubtitleNotFoundError as e:
    logger.error(f"视频 {url} 没有可用字幕: {e}")
    # 尝试使用 Whisper 转录
    return transcribe_with_whisper(url)
except DownloadError as e:
    logger.error(f"下载失败: {e}")
    raise
```

### 6. 日志记录

**使用标准 logging 模块：**

```python
import logging

logger = logging.getLogger(__name__)

def download_subtitle(url: str) -> str:
    logger.info(f"开始下载字幕: {url}")
    try:
        # 下载逻辑
        logger.debug(f"字幕下载成功: {subtitle_path}")
        return subtitle_path
    except Exception as e:
        logger.error(f"字幕下载失败: {e}", exc_info=True)
        raise
```

**日志级别：**
- `DEBUG`: 详细的调试信息
- `INFO`: 一般信息（默认）
- `WARNING`: 警告信息
- `ERROR`: 错误信息
- `CRITICAL`: 严重错误

### 7. 配置管理

**使用环境变量和配置文件：**

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置"""
    openai_api_key: str
    subtitle_languages: List[str] = ['en', 'zh']
    cache_dir: str = "./cache"
    output_dir: str = "./output/summaries"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 项目特定规范

### 1. 不保存视频文件

**所有下载和处理代码必须遵循：**

```python
# ✅ 正确：只下载字幕
ydl_opts = {
    'skip_download': True,  # 不下载视频
    'writesubtitles': True,  # 只下载字幕
}

# ❌ 错误：下载视频文件
ydl_opts = {
    'format': 'best',  # 这会下载视频
}
```

### 2. 临时文件管理

**临时文件必须在使用后立即删除：**

```python
import tempfile
import os

def transcribe_audio(url: str) -> str:
    """转录音频（临时下载，转录后删除）"""
    temp_audio = None
    try:
        # 临时下载音频
        temp_audio = download_temp_audio(url)
        
        # 转录
        transcript = whisper_transcribe(temp_audio)
        
        return transcript
    finally:
        # 确保删除临时文件
        if temp_audio and os.path.exists(temp_audio):
            os.remove(temp_audio)
            logger.debug(f"已删除临时音频文件: {temp_audio}")
```

### 3. 文档同步

**代码改动后必须更新文档：**

- 更新 `CHANGELOG.md`
- 更新相关技术文档
- 更新代码注释

详见 `.cursorrules` 中的文档维护规则。

## 测试规范

### 1. 单元测试

**所有公共函数必须有单元测试：**

```python
# tests/test_subtitle_downloader.py
import pytest
from src.downloader.subtitle_downloader import download_subtitle

def test_download_subtitle_success():
    """测试成功下载字幕"""
    url = "https://www.youtube.com/watch?v=test"
    result = download_subtitle(url)
    assert result is not None
    assert os.path.exists(result)

def test_download_subtitle_no_subtitle():
    """测试无字幕视频"""
    url = "https://www.youtube.com/watch?v=no_subtitle"
    with pytest.raises(SubtitleNotFoundError):
        download_subtitle(url)
```

### 2. 测试覆盖率

- 目标覆盖率：> 80%
- 关键模块覆盖率：> 90%

## 代码审查检查清单

提交代码前检查：

- [ ] 代码符合 PEP 8 规范
- [ ] 所有公共 API 有类型注解
- [ ] 所有公共函数有文档字符串
- [ ] 错误处理完善
- [ ] 日志记录适当
- [ ] 不保存视频文件（如适用）
- [ ] 临时文件已清理
- [ ] 单元测试通过
- [ ] 文档已更新

