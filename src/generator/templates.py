"""
Markdown 模板
"""

from typing import Dict, Any, Optional
from datetime import datetime


def format_duration(seconds: int) -> str:
    """
    格式化时长
    
    Args:
        seconds: 秒数
    
    Returns:
        格式化后的时长字符串
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def generate_markdown(
    summary: str,
    metadata: Dict[str, Any],
    generated_at: Optional[str] = None
) -> str:
    """
    生成 Markdown 格式的总结文件
    
    Args:
        summary: AI 生成的总结内容
        metadata: 视频元数据
        generated_at: 生成时间（ISO 格式），如果为 None 则使用当前时间
    
    Returns:
        Markdown 格式的字符串
    """
    title = metadata.get('title', '未知视频')
    author = metadata.get('author', '未知作者')
    url = metadata.get('url', '')
    duration = metadata.get('duration', 0)
    publish_date = metadata.get('publish_date')
    view_count = metadata.get('view_count')
    
    # 格式化时长
    duration_str = format_duration(duration)
    
    # 生成时间
    if generated_at is None:
        generated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 构建 Markdown
    md_lines = [
        f"# {title}",
        "",
        f"**作者**：{author}",
    ]
    
    if publish_date:
        md_lines.append(f"**发布时间**：{publish_date}")
    
    md_lines.extend([
        f"**视频时长**：{duration_str}",
        f"**🔗 视频链接**：[点击查看原视频]({url}) | {url}",
        "",
        "> 💡 **提示**：本文档为视频内容总结，如需观看原视频，请点击上方链接。",
        "",
        "---",
        "",
    ])
    
    # 添加总结内容
    md_lines.append(summary)
    
    # 添加页脚
    md_lines.extend([
        "",
        "---",
        "",
        f"*本文档由 Smart Video 自动生成*",
        f"*生成时间：{generated_at}*",
    ])
    
    return "\n".join(md_lines)


def generate_simple_markdown(
    summary: str,
    metadata: Dict[str, Any]
) -> str:
    """
    生成简化版 Markdown（用于快速预览）
    
    Args:
        summary: AI 生成的总结内容
        metadata: 视频元数据
    
    Returns:
        Markdown 格式的字符串
    """
    title = metadata.get('title', '未知视频')
    url = metadata.get('url', '')
    
    md_lines = [
        f"# {title}",
        "",
        f"**视频链接**：{url}",
        "",
        "---",
        "",
        summary,
    ]
    
    return "\n".join(md_lines)

