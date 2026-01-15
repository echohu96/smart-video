"""
视频平台抽象基类
为多平台支持提供统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class VideoMetadata:
    """视频元数据"""
    title: str
    author: str
    duration: int  # 秒
    url: str
    video_id: str
    description: Optional[str] = None
    publish_date: Optional[str] = None
    view_count: Optional[int] = None
    thumbnail_url: Optional[str] = None


class VideoPlatform(ABC):
    """视频平台抽象基类"""
    
    @abstractmethod
    def download_subtitle(
        self,
        url: str,
        languages: Optional[List[str]] = None,
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """
        下载字幕文件（不下载视频）
        
        Args:
            url: 视频 URL
            languages: 字幕语言列表
            output_dir: 输出目录
        
        Returns:
            字幕文件路径，如果没有字幕则返回 None
        
        Raises:
            DownloadError: 下载失败
        """
        pass
    
    @abstractmethod
    def download_audio(
        self,
        url: str,
        output_dir: Optional[str] = None
    ) -> str:
        """
        临时下载音频文件（无字幕时用于转录）
        
        Args:
            url: 视频 URL
            output_dir: 输出目录
        
        Returns:
            音频文件路径
        
        Raises:
            DownloadError: 下载失败
        """
        pass
    
    @abstractmethod
    def extract_metadata(self, url: str) -> VideoMetadata:
        """
        提取视频元数据
        
        Args:
            url: 视频 URL
        
        Returns:
            视频元数据
        
        Raises:
            DownloadError: 提取失败
        """
        pass
    
    @abstractmethod
    def has_subtitle(self, url: str, languages: Optional[List[str]] = None) -> bool:
        """
        检查视频是否有字幕
        
        Args:
            url: 视频 URL
            languages: 字幕语言列表
        
        Returns:
            是否有字幕
        """
        pass

