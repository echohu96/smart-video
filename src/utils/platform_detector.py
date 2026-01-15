"""
平台检测器
用于检测视频 URL 所属的平台
"""

import re
from typing import Optional
from enum import Enum
from .logger import get_logger
from .exceptions import PlatformNotSupportedError

logger = get_logger(__name__)


class VideoPlatform(Enum):
    """支持的视频平台"""
    YOUTUBE = "youtube"
    BILIBILI = "bilibili"
    VIMEO = "vimeo"
    UNKNOWN = "unknown"


class PlatformDetector:
    """平台检测器"""
    
    # YouTube URL 模式
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    ]
    
    # Bilibili URL 模式（未来支持）
    BILIBILI_PATTERNS = [
        r'(?:https?://)?(?:www\.)?bilibili\.com/video/([a-zA-Z0-9]+)',
        r'(?:https?://)?b23\.tv/([a-zA-Z0-9]+)',
    ]
    
    # Vimeo URL 模式（未来支持）
    VIMEO_PATTERNS = [
        r'(?:https?://)?(?:www\.)?vimeo\.com/(\d+)',
    ]
    
    @classmethod
    def detect(cls, url: str) -> VideoPlatform:
        """
        检测视频 URL 所属的平台
        
        Args:
            url: 视频 URL
        
        Returns:
            平台枚举值
        
        Raises:
            PlatformNotSupportedError: 如果平台不支持
        """
        url = url.strip()
        
        # 检测 YouTube
        for pattern in cls.YOUTUBE_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                logger.debug(f"检测到 YouTube 平台: {url}")
                return VideoPlatform.YOUTUBE
        
        # 检测 Bilibili（未来支持）
        for pattern in cls.BILIBILI_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                logger.debug(f"检测到 Bilibili 平台: {url} (暂不支持)")
                raise PlatformNotSupportedError(
                    f"Bilibili 平台暂不支持，将在未来版本中添加"
                )
        
        # 检测 Vimeo（未来支持）
        for pattern in cls.VIMEO_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                logger.debug(f"检测到 Vimeo 平台: {url} (暂不支持)")
                raise PlatformNotSupportedError(
                    f"Vimeo 平台暂不支持，将在未来版本中添加"
                )
        
        # 未知平台
        logger.warning(f"无法识别平台: {url}")
        raise PlatformNotSupportedError(f"不支持的视频平台: {url}")
    
    @classmethod
    def is_supported(cls, url: str) -> bool:
        """
        检查 URL 是否支持
        
        Args:
            url: 视频 URL
        
        Returns:
            是否支持
        """
        try:
            platform = cls.detect(url)
            return platform == VideoPlatform.YOUTUBE
        except PlatformNotSupportedError:
            return False
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        提取视频 ID
        
        Args:
            url: 视频 URL
        
        Returns:
            视频 ID，如果无法提取则返回 None
        """
        # YouTube
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.search(pattern, url, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None

