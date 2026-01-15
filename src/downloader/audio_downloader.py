"""
音频下载器
无字幕时临时下载音频用于转录（转录后立即删除）
"""

import os
from pathlib import Path
from typing import Optional
import yt_dlp
from ..utils.logger import get_logger
from ..utils.config import get_settings
from ..utils.exceptions import DownloadError
from ..utils.file_manager import get_temp_dir

logger = get_logger(__name__)


class AudioDownloader:
    """音频下载器（临时下载，用于转录）"""
    
    def __init__(self):
        """初始化音频下载器"""
        self.settings = get_settings()
        self.temp_dir = get_temp_dir()
    
    def download(self, url: str, output_dir: Optional[str] = None) -> str:
        """
        临时下载音频文件（用于转录）
        
        Args:
            url: 视频 URL
            output_dir: 输出目录，默认使用临时目录
        
        Returns:
            音频文件路径
        
        Raises:
            DownloadError: 下载失败
        """
        output_dir = output_dir or str(self.temp_dir)
        
        # 配置 yt-dlp 选项（只下载音频）
        ydl_opts = {
            'format': 'bestaudio/best',  # 只下载音频
            'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',  # 转换为 WAV 格式（Whisper 推荐）
                'preferredquality': '192',
            }],
            'quiet': False,
            'no_warnings': False,
        }
        
        # 添加代理配置
        if self.settings.http_proxy:
            ydl_opts['proxy'] = self.settings.http_proxy
        elif self.settings.https_proxy:
            ydl_opts['proxy'] = self.settings.https_proxy
        
        try:
            logger.info(f"开始下载音频（临时）: {url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 提取信息
                info = ydl.extract_info(url, download=True)
                video_id = info.get('id', '')
                
                # 查找下载的音频文件
                audio_file = self._find_audio_file(output_dir, video_id)
                
                if audio_file:
                    logger.info(f"音频下载成功: {audio_file}")
                    logger.warning(f"注意：此音频文件将在转录后自动删除")
                    return audio_file
                else:
                    raise DownloadError(f"未找到下载的音频文件: {url}")
        
        except Exception as e:
            logger.error(f"音频下载失败: {e}", exc_info=True)
            raise DownloadError(f"音频下载失败: {e}")
    
    def _find_audio_file(self, output_dir: str, video_id: str) -> Optional[str]:
        """
        查找下载的音频文件
        
        Args:
            output_dir: 输出目录
            video_id: 视频 ID
        
        Returns:
            音频文件路径，如果不存在则返回 None
        """
        output_path = Path(output_dir)
        
        # 查找 WAV 格式音频（FFmpeg 转换后）
        audio_files = list(output_path.glob(f"{video_id}.wav"))
        if audio_files:
            return str(audio_files[0])
        
        # 查找其他格式音频
        for ext in ['m4a', 'mp3', 'opus', 'webm']:
            audio_files = list(output_path.glob(f"{video_id}.{ext}"))
            if audio_files:
                return str(audio_files[0])
        
        return None

