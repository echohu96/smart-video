"""
自定义异常类
"""


class SmartVideoError(Exception):
    """Smart Video 基础异常类"""
    pass


class SubtitleNotFoundError(SmartVideoError):
    """字幕未找到异常"""
    pass


class DownloadError(SmartVideoError):
    """下载失败异常"""
    pass


class AIAPIError(SmartVideoError):
    """AI API 调用异常"""
    pass


class TranscriptionError(SmartVideoError):
    """转录失败异常"""
    pass


class PlatformNotSupportedError(SmartVideoError):
    """平台不支持异常"""
    pass


class ConfigurationError(SmartVideoError):
    """配置错误异常"""
    pass

