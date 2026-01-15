"""
内容提取主模块
协调字幕解析和元数据提取
"""

from typing import Optional, Tuple
from pathlib import Path
from .subtitle_parser import SubtitleParser
from .metadata_extractor import MetadataExtractor
from ..downloader.base import VideoMetadata, VideoPlatform
from ..utils.logger import get_logger
from ..utils.exceptions import SubtitleNotFoundError

logger = get_logger(__name__)


class ContentExtractor:
    """内容提取器"""
    
    def __init__(self, platform: VideoPlatform):
        """
        初始化内容提取器
        
        Args:
            platform: 视频平台实例
        """
        self.platform = platform
        self.subtitle_parser = SubtitleParser()
        self.metadata_extractor = MetadataExtractor()
    
    def extract(
        self,
        url: str,
        subtitle_file: Optional[str] = None
    ) -> Tuple[str, VideoMetadata]:
        """
        提取视频内容
        
        Args:
            url: 视频 URL
            subtitle_file: 字幕文件路径（如果已下载）
        
        Returns:
            (文本内容, 视频元数据) 元组
        
        Raises:
            SubtitleNotFoundError: 字幕未找到
        """
        logger.info(f"开始提取内容: {url}")
        
        # 提取元数据
        metadata = self.platform.extract_metadata(url)
        logger.debug(f"元数据提取成功: {metadata.title}")
        
        # 提取文本内容
        if subtitle_file and Path(subtitle_file).exists():
            logger.info(f"从字幕文件提取文本: {subtitle_file}")
            text = self.subtitle_parser.parse(subtitle_file)
            logger.info(f"文本提取成功，长度: {len(text)} 字符")
        else:
            raise SubtitleNotFoundError(f"字幕文件不存在: {subtitle_file}")
        
        return text, metadata
    
    def extract_with_timestamps(
        self,
        subtitle_file: str
    ) -> list:
        """
        提取带时间戳的文本内容
        
        Args:
            subtitle_file: 字幕文件路径
        
        Returns:
            时间戳和文本的列表 [(时间戳(秒), 文本), ...]
        """
        logger.debug(f"提取带时间戳的内容: {subtitle_file}")
        return self.subtitle_parser.parse_with_timestamps(subtitle_file)

