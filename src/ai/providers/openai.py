"""
OpenAI 提供商实现
"""

from typing import Optional
from openai import OpenAI
from .base import AIProvider
from ...utils.logger import get_logger
from ...utils.config import get_settings
from ...utils.exceptions import AIAPIError, ConfigurationError

logger = get_logger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAI 提供商"""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        初始化 OpenAI 提供商
        
        Args:
            api_key: OpenAI API Key（如果为 None，从配置读取）
            model: 模型名称（如果为 None，从配置读取）
        """
        self.settings = get_settings()
        self.api_key = api_key or self.settings.openai_api_key
        self.model = model or self.settings.openai_model
        
        if not self.api_key:
            raise ConfigurationError("OpenAI API Key 未配置")
        
        self.client = OpenAI(api_key=self.api_key)
    
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
        if not prompt:
            from ..prompts import get_summary_prompt
            prompt = get_summary_prompt(metadata=metadata)
        
        try:
            logger.info(f"调用 OpenAI API 生成总结 (模型: {self.model})")
            logger.debug(f"文本长度: {len(text)} 字符")
            
            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一个专业的视频内容总结助手，擅长分析视频内容并生成结构化的总结。"
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\n转录内容：\n{text}"
                }
            ]
            
            # 调用 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
            )
            
            # 提取结果
            summary = response.choices[0].message.content.strip()
            
            logger.info(f"总结生成成功，长度: {len(summary)} 字符")
            return summary
        
        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}", exc_info=True)
            raise AIAPIError(f"OpenAI API 调用失败: {e}")
    
    def is_available(self) -> bool:
        """
        检查 OpenAI 是否可用
        
        Returns:
            是否可用
        """
        return self.api_key is not None and len(self.api_key) > 0

