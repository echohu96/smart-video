"""
配置管理模块
使用 pydantic-settings 管理配置
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # AI Provider Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API Key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI Model")
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API Key")
    
    # Download Configuration
    subtitle_languages: str = Field(
        default="en,zh,zh-Hans,zh-Hant",
        description="字幕语言列表（逗号分隔）"
    )
    auto_download_subtitles: bool = Field(default=True, description="自动下载字幕")
    cache_subtitles: bool = Field(default=True, description="是否缓存字幕文件")
    
    # Path Configuration
    cache_dir: str = Field(default="./cache", description="缓存目录")
    subtitle_cache_dir: str = Field(
        default="./cache/subtitles",
        description="字幕缓存目录"
    )
    temp_dir: str = Field(
        default="./cache/temp",
        description="临时文件目录（无字幕时临时音频）"
    )
    output_dir: str = Field(
        default="./output/summaries",
        description="总结输出目录"
    )
    
    # Whisper Configuration
    use_whisper: bool = Field(default=False, description="是否使用 Whisper")
    whisper_model: str = Field(default="base", description="Whisper 模型大小")
    
    # Proxy Configuration
    http_proxy: Optional[str] = Field(default=None, description="HTTP 代理")
    https_proxy: Optional[str] = Field(default=None, description="HTTPS 代理")
    
    # Logging
    log_level: str = Field(default="INFO", description="日志级别")
    
    @property
    def subtitle_languages_list(self) -> List[str]:
        """获取字幕语言列表（属性）"""
        return [lang.strip() for lang in self.subtitle_languages.split(",") if lang.strip()]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
