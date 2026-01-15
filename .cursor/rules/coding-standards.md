# 编码规范

## 文档字符串要求

**所有公共 API 必须包含文档字符串：**

```python
def download_subtitle(url: str, languages: List[str] = None) -> str:
    """
    下载 YouTube 视频的字幕文件。
    
    只下载字幕，不下载视频文件。优先使用手动字幕，
    其次使用自动生成字幕。
    
    Args:
        url: YouTube 视频 URL
        languages: 字幕语言列表，默认为 ['en', 'zh']
    
    Returns:
        字幕文件路径
    
    Raises:
        SubtitleNotFoundError: 如果视频没有可用字幕
        DownloadError: 如果下载失败
    
    Note:
        此函数不保存视频文件，只下载字幕。
        详见 docs/architecture/DESIGN_PRINCIPLES.md
    """
    pass
```

## 注释要求

**关键逻辑必须注释：**
- 复杂算法和业务逻辑
- 设计决策和权衡
- 已知问题和限制
- 未来改进方向

**注释格式：**
```python
# 设计决策：不保存视频文件，只保存字幕
# 原因：节省存储空间，用户可通过 URL 查看原视频
# 详见：docs/architecture/DESIGN_PRINCIPLES.md
```

## 特殊说明

### 关于视频文件

**重要原则**：本项目不保存视频文件，只保存字幕和总结。
- 所有相关代码和文档必须体现这一原则
- 任何可能保存视频文件的改动都需要特别说明
- 详见 `docs/architecture/DESIGN_PRINCIPLES.md`

### 关于文档版本

- 文档没有版本号，只有最新版本
- 文档必须始终反映当前系统状态
- 历史变更记录在 CHANGELOG.md 中

