"""
文件管理工具模块
"""

import os
import shutil
from pathlib import Path
from typing import Optional
from .logger import get_logger
from .config import get_settings

logger = get_logger(__name__)


def ensure_dir(directory: str) -> Path:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
    
    Returns:
        Path 对象
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_cache_dir() -> Path:
    """获取缓存目录"""
    settings = get_settings()
    return ensure_dir(settings.cache_dir)


def get_subtitle_cache_dir() -> Path:
    """获取字幕缓存目录"""
    settings = get_settings()
    return ensure_dir(settings.subtitle_cache_dir)


def get_temp_dir() -> Path:
    """获取临时文件目录"""
    settings = get_settings()
    return ensure_dir(settings.temp_dir)


def get_output_dir() -> Path:
    """获取输出目录"""
    settings = get_settings()
    return ensure_dir(settings.output_dir)


def cleanup_temp_file(file_path: str) -> bool:
    """
    清理临时文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        是否成功删除
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"已删除临时文件: {file_path}")
            return True
    except Exception as e:
        logger.warning(f"删除临时文件失败 {file_path}: {e}")
        return False
    return False


def cleanup_temp_dir(directory: str, pattern: Optional[str] = None) -> int:
    """
    清理临时目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件名模式（可选）
    
    Returns:
        删除的文件数量
    """
    count = 0
    try:
        path = Path(directory)
        if not path.exists():
            return 0
        
        if pattern:
            files = list(path.glob(pattern))
        else:
            files = list(path.iterdir())
        
        for file_path in files:
            if file_path.is_file():
                try:
                    file_path.unlink()
                    count += 1
                    logger.debug(f"已删除临时文件: {file_path}")
                except Exception as e:
                    logger.warning(f"删除文件失败 {file_path}: {e}")
    except Exception as e:
        logger.error(f"清理临时目录失败 {directory}: {e}")
    
    return count


def get_file_size(file_path: str) -> int:
    """
    获取文件大小（字节）
    
    Args:
        file_path: 文件路径
    
    Returns:
        文件大小（字节）
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        格式化后的文件大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

