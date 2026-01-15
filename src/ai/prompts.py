"""
AI 提示词模板
"""

from typing import Optional, Dict, Any


def get_summary_prompt(metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    获取总结提示词模板
    
    Args:
        metadata: 视频元数据
    
    Returns:
        提示词字符串
    """
    title = metadata.get('title', '未知视频') if metadata else '未知视频'
    author = metadata.get('author', '未知作者') if metadata else '未知作者'
    duration = metadata.get('duration', 0) if metadata else 0
    
    # 格式化时长
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    
    if hours > 0:
        duration_str = f"{hours}小时{minutes}分钟{seconds}秒"
    elif minutes > 0:
        duration_str = f"{minutes}分钟{seconds}秒"
    else:
        duration_str = f"{seconds}秒"
    
    prompt = f"""请分析以下视频转录内容，生成一份结构化的总结。

视频标题：{title}
视频作者：{author}
视频时长：{duration_str}

请按照以下格式输出：

# 视频总结

## 基本信息
- 标题：{title}
- 作者：{author}
- 时长：{duration_str}

## 核心内容摘要
[2-3段总结视频主要内容，突出核心观点和关键信息]

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

...

## 总结
[整体评价和收获，可以包括：
- 视频的核心价值
- 主要收获
- 值得思考的问题
- 后续行动建议等]

**要求：**
- 总结要准确、全面，突出核心内容
- 关键要点要清晰、有条理
- 章节划分要合理，便于阅读
- 语言要简洁、专业
- 如果视频内容较长，可以适当合并相似章节
"""
    
    return prompt


def get_simple_summary_prompt() -> str:
    """
    获取简单总结提示词（用于快速总结）
    
    Returns:
        提示词字符串
    """
    return """请对以下视频转录内容进行总结，要求：
1. 提取核心观点和关键信息
2. 总结主要章节内容
3. 语言简洁、准确
4. 突出视频的价值和收获

请用中文输出。"""

