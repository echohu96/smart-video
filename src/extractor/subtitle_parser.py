"""
字幕解析器
解析 SRT/VTT 格式字幕文件，提取纯文本
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SubtitleParser:
    """字幕解析器"""
    
    @staticmethod
    def parse(file_path: str) -> str:
        """
        解析字幕文件，提取纯文本
        
        Args:
            file_path: 字幕文件路径
        
        Returns:
            提取的文本内容
        
        Raises:
            ValueError: 文件格式不支持或解析失败
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"字幕文件不存在: {file_path}")
        
        # 根据文件扩展名选择解析方法
        ext = path.suffix.lower()
        
        if ext == '.vtt':
            return SubtitleParser._parse_vtt(file_path)
        elif ext == '.srt':
            return SubtitleParser._parse_srt(file_path)
        else:
            raise ValueError(f"不支持的字幕格式: {ext}")
    
    @staticmethod
    def _parse_vtt(file_path: str) -> str:
        """
        解析 VTT 格式字幕
        
        Args:
            file_path: VTT 文件路径
        
        Returns:
            提取的文本内容
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除 VTT 头部信息
        content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
        
        # 移除时间戳行（格式：00:00:00.000 --> 00:00:00.000）
        content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', content)
        
        # 移除序号行
        content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
        
        # 移除 HTML 标签
        content = re.sub(r'<[^>]+>', '', content)
        
        # 移除多余的空行
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # 清理文本
        lines = []
        for line in content.split('\n'):
            line = line.strip()
            if line and not line.isdigit():  # 跳过空行和纯数字行
                lines.append(line)
        
        return '\n'.join(lines)
    
    @staticmethod
    def _parse_srt(file_path: str) -> str:
        """
        解析 SRT 格式字幕
        
        Args:
            file_path: SRT 文件路径
        
        Returns:
            提取的文本内容
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割字幕块
        blocks = re.split(r'\n\s*\n', content)
        
        lines = []
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            # 移除序号行（第一行）
            lines_in_block = block.split('\n')
            if len(lines_in_block) < 2:
                continue
            
            # 移除时间戳行（第二行）
            if len(lines_in_block) >= 3:
                # 提取文本行（第三行及以后）
                text_lines = lines_in_block[2:]
                text = '\n'.join(text_lines).strip()
                
                # 移除 HTML 标签
                text = re.sub(r'<[^>]+>', '', text)
                
                if text:
                    lines.append(text)
        
        return '\n'.join(lines)
    
    @staticmethod
    def parse_with_timestamps(file_path: str) -> List[Tuple[float, str]]:
        """
        解析字幕文件，保留时间戳信息
        
        Args:
            file_path: 字幕文件路径
        
        Returns:
            时间戳和文本的列表 [(时间戳(秒), 文本), ...]
        """
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext == '.vtt':
            return SubtitleParser._parse_vtt_with_timestamps(file_path)
        elif ext == '.srt':
            return SubtitleParser._parse_srt_with_timestamps(file_path)
        else:
            raise ValueError(f"不支持的字幕格式: {ext}")
    
    @staticmethod
    def _parse_vtt_with_timestamps(file_path: str) -> List[Tuple[float, str]]:
        """解析 VTT 格式字幕，保留时间戳"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除 VTT 头部
        content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
        
        results = []
        pattern = r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\s*\n(.*?)(?=\n\d{2}:\d{2}:\d{2}\.\d{3}|\Z)'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            hours, minutes, seconds, milliseconds = map(int, match.groups()[:4])
            timestamp = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
            text = match.group(5).strip()
            
            # 移除 HTML 标签
            text = re.sub(r'<[^>]+>', '', text)
            
            if text:
                results.append((timestamp, text))
        
        return results
    
    @staticmethod
    def _parse_srt_with_timestamps(file_path: str) -> List[Tuple[float, str]]:
        """解析 SRT 格式字幕，保留时间戳"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        blocks = re.split(r'\n\s*\n', content)
        results = []
        
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            
            lines = block.split('\n')
            if len(lines) < 3:
                continue
            
            # 解析时间戳（第二行）
            time_line = lines[1]
            time_match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*', time_line)
            if time_match:
                hours, minutes, seconds, milliseconds = map(int, time_match.groups())
                timestamp = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0
                
                # 提取文本（第三行及以后）
                text = '\n'.join(lines[2:]).strip()
                text = re.sub(r'<[^>]+>', '', text)  # 移除 HTML 标签
                
                if text:
                    results.append((timestamp, text))
        
        return results

