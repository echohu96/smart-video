"""
AI 总结主模块
"""

from typing import Optional, Dict, Any
from .providers.base import AIProvider
from .providers.openai import OpenAIProvider
from ..utils.logger import get_logger
from ..utils.config import get_settings
from ..utils.exceptions import AIAPIError, ConfigurationError

logger = get_logger(__name__)


class Summarizer:
    """AI 总结器"""
    
    def __init__(self, provider: Optional[str] = None):
        """
        初始化总结器
        
        Args:
            provider: AI 提供商名称（'openai' 或其他），如果为 None 则自动选择
        """
        self.settings = get_settings()
        self.provider_name = provider or self._detect_provider()
        self.provider = self._create_provider(self.provider_name)
    
    def _detect_provider(self) -> str:
        """
        自动检测可用的 AI 提供商
        
        Returns:
            提供商名称
        
        Raises:
            ConfigurationError: 没有可用的提供商
        """
        # 检查 OpenAI
        if self.settings.openai_api_key:
            return 'openai'
        
        # 检查 Anthropic（未来支持）
        if self.settings.anthropic_api_key:
            raise ConfigurationError("Anthropic Claude 暂不支持，将在未来版本中添加")
        
        raise ConfigurationError("未配置任何 AI 提供商 API Key")
    
    def _create_provider(self, provider_name: str) -> AIProvider:
        """
        创建 AI 提供商实例
        
        Args:
            provider_name: 提供商名称
        
        Returns:
            AI 提供商实例
        
        Raises:
            ConfigurationError: 提供商不支持或配置错误
        """
        if provider_name == 'openai':
            return OpenAIProvider()
        else:
            raise ConfigurationError(f"不支持的 AI 提供商: {provider_name}")
    
    def summarize(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        生成文本总结
        
        Args:
            text: 要总结的文本
            metadata: 视频元数据（可选）
            custom_prompt: 自定义提示词（可选）
        
        Returns:
            生成的总结文本
        
        Raises:
            AIAPIError: API 调用失败
        """
        logger.info(f"开始生成总结 (提供商: {self.provider_name})")
        
        if not self.provider.is_available():
            raise ConfigurationError(f"AI 提供商 {self.provider_name} 不可用")
        
        try:
            summary = self.provider.summarize(
                text=text,
                metadata=metadata,
                prompt=custom_prompt
            )
            logger.info("总结生成成功")
            return summary
        except Exception as e:
            logger.error(f"总结生成失败: {e}")
            raise

