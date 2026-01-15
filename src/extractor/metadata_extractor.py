"""
元数据提取器
从视频平台提取元数据
"""

from typing import Dict, Any
from ..downloader.base import VideoMetadata
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MetadataExtractor:
    """元数据提取器"""
    
    @staticmethod
    def to_dict(metadata: VideoMetadata) -> Dict[str, Any]:
        """
        将元数据转换为字典
        
        Args:
            metadata: 视频元数据
        
        Returns:
            元数据字典
        """
        return {
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
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """
        格式化时长
        
        Args:
            seconds: 秒数
        
        Returns:
            格式化后的时长字符串（如 "1:23:45"）
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"

