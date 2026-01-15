"""
下载器模块
支持多平台视频下载（当前支持 YouTube）
"""

from .base import VideoPlatform
from .youtube import YouTubePlatform

__all__ = [
    "VideoPlatform",
    "YouTubePlatform",
]

