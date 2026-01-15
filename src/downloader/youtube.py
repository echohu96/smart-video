"""
YouTube 平台实现
"""

from typing import Optional, List
import yt_dlp
from datetime import datetime
from .base import VideoPlatform, VideoMetadata
from .subtitle_downloader import SubtitleDownloader
from .audio_downloader import AudioDownloader
from ..utils.logger import get_logger
from ..utils.config import get_settings
from ..utils.exceptions import DownloadError, SubtitleNotFoundError

logger = get_logger(__name__)


class YouTubePlatform(VideoPlatform):
    """YouTube 平台实现"""
    
    def __init__(self):
        """初始化 YouTube 平台"""
        self.settings = get_settings()
        self.subtitle_downloader = SubtitleDownloader()
        self.audio_downloader = AudioDownloader()
    
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
            SubtitleNotFoundError: 字幕未找到
        """
        return self.subtitle_downloader.download(
            url=url,
            languages=languages,
            output_dir=output_dir
        )
    
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
        return self.audio_downloader.download(url=url, output_dir=output_dir)
    
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
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
        }
        
        # 添加代理配置
        if self.settings.http_proxy:
            ydl_opts['proxy'] = self.settings.http_proxy
        elif self.settings.https_proxy:
            ydl_opts['proxy'] = self.settings.https_proxy
        
        try:
            logger.debug(f"提取视频元数据: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 提取视频 ID
                video_id = info.get('id', '')
                
                # 提取标题
                title = info.get('title', 'Unknown')
                
                # 提取作者
                uploader = info.get('uploader', 'Unknown')
                channel = info.get('channel', uploader)
                author = channel or uploader
                
                # 提取时长（秒）
                duration = info.get('duration', 0) or 0
                
                # 提取描述
                description = info.get('description', '')
                
                # 提取发布时间
                upload_date = info.get('upload_date', '')
                publish_date = None
                if upload_date:
                    try:
                        # 格式：YYYYMMDD
                        dt = datetime.strptime(upload_date, '%Y%m%d')
                        publish_date = dt.strftime('%Y-%m-%d')
                    except Exception:
                        pass
                
                # 提取观看次数
                view_count = info.get('view_count', 0)
                
                # 提取缩略图 URL
                thumbnail_url = info.get('thumbnail', '')
                
                metadata = VideoMetadata(
                    title=title,
                    author=author,
                    duration=duration,
                    url=url,
                    video_id=video_id,
                    description=description,
                    publish_date=publish_date,
                    view_count=view_count,
                    thumbnail_url=thumbnail_url,
                )
                
                logger.debug(f"元数据提取成功: {title}")
                return metadata
        
        except Exception as e:
            logger.error(f"元数据提取失败: {e}", exc_info=True)
            raise DownloadError(f"元数据提取失败: {e}")
    
    def has_subtitle(self, url: str, languages: Optional[List[str]] = None) -> bool:
        """
        检查视频是否有字幕
        
        Args:
            url: 视频 URL
            languages: 字幕语言列表
        
        Returns:
            是否有字幕
        """
        return self.subtitle_downloader.has_subtitle(url=url, languages=languages)

