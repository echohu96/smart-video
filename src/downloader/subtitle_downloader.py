"""
字幕下载器
使用 yt-dlp 只下载字幕，不下载视频
"""

import os
from pathlib import Path
from typing import Optional, List
import yt_dlp
from ..utils.logger import get_logger
from ..utils.config import get_settings
from ..utils.exceptions import DownloadError, SubtitleNotFoundError
from ..utils.file_manager import get_subtitle_cache_dir

logger = get_logger(__name__)


class SubtitleDownloader:
    """字幕下载器"""
    
    def __init__(self):
        """初始化字幕下载器"""
        self.settings = get_settings()
        self.cache_dir = get_subtitle_cache_dir()
    
    def download(
        self,
        url: str,
        languages: Optional[List[str]] = None,
        output_dir: Optional[str] = None,
        use_cache: bool = True
    ) -> Optional[str]:
        """
        下载字幕文件（不下载视频）
        
        Args:
            url: 视频 URL
            languages: 字幕语言列表，默认从配置读取
            output_dir: 输出目录，默认使用缓存目录
            use_cache: 是否使用缓存
        
        Returns:
            字幕文件路径，如果没有字幕则返回 None
        
        Raises:
            DownloadError: 下载失败
            SubtitleNotFoundError: 字幕未找到
        """
        languages = languages or self.settings.subtitle_languages_list
        output_dir = output_dir or str(self.cache_dir)
        
        # 检查缓存
        if use_cache and self.settings.cache_subtitles:
            cached_file = self._get_cached_subtitle(url, languages)
            if cached_file and os.path.exists(cached_file):
                logger.info(f"使用缓存字幕: {cached_file}")
                return cached_file
        
        # 配置 yt-dlp 选项（关键：只下载字幕，不下载视频）
        ydl_opts = {
            'skip_download': True,  # 关键：跳过视频/音频下载
            'writesubtitles': True,  # 下载字幕
            'writeautomaticsub': True,  # 下载自动生成字幕
            'subtitleslangs': languages,  # 字幕语言
            'subtitlesformat': 'vtt',  # 字幕格式（VTT）
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'ignoreerrors': False,
        }
        
        # 添加代理配置
        if self.settings.http_proxy:
            ydl_opts['proxy'] = self.settings.http_proxy
        elif self.settings.https_proxy:
            ydl_opts['proxy'] = self.settings.https_proxy
        
        try:
            logger.info(f"开始下载字幕: {url}")
            logger.debug(f"字幕语言: {languages}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 提取信息
                info = ydl.extract_info(url, download=True)
                video_id = info.get('id', '')
                
                # 查找下载的字幕文件
                subtitle_file = self._find_subtitle_file(output_dir, video_id)
                
                if subtitle_file:
                    logger.info(f"字幕下载成功: {subtitle_file}")
                    return subtitle_file
                else:
                    logger.warning(f"未找到字幕文件: {url}")
                    raise SubtitleNotFoundError(f"视频没有可用字幕: {url}")
        
        except SubtitleNotFoundError:
            raise
        except Exception as e:
            logger.error(f"字幕下载失败: {e}", exc_info=True)
            raise DownloadError(f"字幕下载失败: {e}")
    
    def _get_cached_subtitle(
        self,
        url: str,
        languages: List[str]
    ) -> Optional[str]:
        """
        获取缓存的字幕文件
        
        Args:
            url: 视频 URL
            languages: 字幕语言列表
        
        Returns:
            缓存文件路径，如果不存在则返回 None
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                video_id = info.get('id', '')
                
                # 查找缓存文件
                for lang in languages:
                    cache_file = self.cache_dir / f"{video_id}.{lang}.vtt"
                    if cache_file.exists():
                        return str(cache_file)
        except Exception:
            pass
        
        return None
    
    def _find_subtitle_file(self, output_dir: str, video_id: str) -> Optional[str]:
        """
        查找下载的字幕文件
        
        Args:
            output_dir: 输出目录
            video_id: 视频 ID
        
        Returns:
            字幕文件路径，如果不存在则返回 None
        """
        output_path = Path(output_dir)
        
        # 查找 VTT 格式字幕
        subtitle_files = list(output_path.glob(f"{video_id}*.vtt"))
        if subtitle_files:
            return str(subtitle_files[0])
        
        # 查找 SRT 格式字幕
        subtitle_files = list(output_path.glob(f"{video_id}*.srt"))
        if subtitle_files:
            return str(subtitle_files[0])
        
        return None
    
    def has_subtitle(
        self,
        url: str,
        languages: Optional[List[str]] = None
    ) -> bool:
        """
        检查视频是否有字幕
        
        Args:
            url: 视频 URL
            languages: 字幕语言列表
        
        Returns:
            是否有字幕
        """
        languages = languages or self.settings.subtitle_languages_list
        
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
            }
            
            if self.settings.http_proxy:
                ydl_opts['proxy'] = self.settings.http_proxy
            elif self.settings.https_proxy:
                ydl_opts['proxy'] = self.settings.https_proxy
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # 检查字幕可用性
                subtitles = info.get('subtitles', {})
                automatic_captions = info.get('automatic_captions', {})
                
                # 检查手动字幕
                for lang in languages:
                    if lang in subtitles:
                        return True
                
                # 检查自动字幕
                for lang in languages:
                    if lang in automatic_captions:
                        return True
                
                return False
        
        except Exception as e:
            logger.warning(f"检查字幕失败: {e}")
            return False

