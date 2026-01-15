"""
Markdown 生成器
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .templates import generate_markdown, format_duration
from ..utils.logger import get_logger
from ..utils.file_manager import get_output_dir
from ..downloader.base import VideoMetadata

logger = get_logger(__name__)


class MarkdownGenerator:
    """Markdown 生成器"""
    
    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化 Markdown 生成器
        
        Args:
            output_dir: 输出目录，如果为 None 则使用配置中的目录
        """
        if output_dir:
            self.output_dir = Path(output_dir)
        else:
            self.output_dir = get_output_dir()
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        summary: str,
        metadata: VideoMetadata,
        filename: Optional[str] = None,
        generated_at: Optional[str] = None
    ) -> str:
        """
        生成并保存 Markdown 文件
        
        Args:
            summary: AI 生成的总结内容
            metadata: 视频元数据
            filename: 输出文件名（如果为 None 则自动生成）
            generated_at: 生成时间（ISO 格式）
        
        Returns:
            生成的 Markdown 文件路径
        """
        # 转换为字典格式
        metadata_dict = {
            'title': metadata.title,
            'author': metadata.author,
            'duration': metadata.duration,
            'url': metadata.url,
            'video_id': metadata.video_id,
            'description': metadata.description,
            'publish_date': metadata.publish_date,
            'view_count': metadata.view_count,
            'thumbnail_url': metadata.thumbnail_url,
        }
        
        # 生成 Markdown 内容
        md_content = generate_markdown(
            summary=summary,
            metadata=metadata_dict,
            generated_at=generated_at
        )
        
        # 确定文件名
        if filename is None:
            # 使用视频标题生成文件名（清理特殊字符）
            safe_title = self._sanitize_filename(metadata.title)
            filename = f"{safe_title}.md"
        
        # 确保文件名以 .md 结尾
        if not filename.endswith('.md'):
            filename = f"{filename}.md"
        
        # 构建完整路径
        output_path = self.output_dir / filename
        
        # 如果文件已存在，添加序号
        if output_path.exists():
            base_name = output_path.stem
            counter = 1
            while output_path.exists():
                output_path = self.output_dir / f"{base_name}_{counter}.md"
                counter += 1
            logger.warning(f"文件已存在，使用新文件名: {output_path.name}")
        
        # 保存文件
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Markdown 文件已保存: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"保存 Markdown 文件失败: {e}", exc_info=True)
            raise
    
    def _sanitize_filename(self, filename: str, max_length: int = 100) -> str:
        """
        清理文件名，移除特殊字符
        
        Args:
            filename: 原始文件名
            max_length: 最大长度
        
        Returns:
            清理后的文件名
        """
        # 移除或替换特殊字符
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # 移除前后空格和点
        filename = filename.strip(' .')
        
        # 限制长度
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        # 如果文件名为空，使用默认名称
        if not filename:
            filename = "video_summary"
        
        return filename

