"""
AI 提供商抽象基类
为多 AI 提供商支持提供统一接口
"""

from abc import ABC, abstractmethod
from typing import Optional


class AIProvider(ABC):
    """AI 提供商抽象基类"""
    
    @abstractmethod
    def summarize(
        self,
        text: str,
        metadata: Optional[dict] = None,
        prompt: Optional[str] = None
    ) -> str:
        """
        生成文本总结
        
        Args:
            text: 要总结的文本
            metadata: 视频元数据（可选）
            prompt: 自定义提示词（可选）
        
        Returns:
            生成的总结文本
        
        Raises:
            AIAPIError: API 调用失败
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        检查提供商是否可用
        
        Returns:
            是否可用
        """
        pass

