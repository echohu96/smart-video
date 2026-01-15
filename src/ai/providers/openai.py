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
        self.max_chars_per_chunk = 12000
        self.chunk_summary_max_tokens = 800
    
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

            if len(text) > self.max_chars_per_chunk:
                summary = self._summarize_long_text(text, prompt)
            else:
                summary = self._summarize_once(prompt, text, max_tokens=2000)

            logger.info(f"总结生成成功，长度: {len(summary)} 字符")
            return summary

        except Exception as e:
            logger.error(f"OpenAI API 调用失败: {e}", exc_info=True)
            raise AIAPIError(f"OpenAI API 调用失败: {e}")

    def _summarize_once(self, prompt: str, content: str, max_tokens: int) -> str:
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的视频内容总结助手，擅长分析视频内容并生成结构化的总结。"
            },
            {
                "role": "user",
                "content": f"{prompt}\n\n转录内容：\n{content}"
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()

    def _summarize_long_text(self, text: str, final_prompt: str) -> str:
        from ..prompts import get_chunk_summary_prompt

        chunks = self._chunk_text(text, self.max_chars_per_chunk)
        logger.info(f"文本过长，分段总结：共 {len(chunks)} 段")

        chunk_summaries = []
        total_chunks = len(chunks)
        for index, chunk in enumerate(chunks, start=1):
            chunk_prompt = get_chunk_summary_prompt(index, total_chunks)
            chunk_summary = self._summarize_once(
                chunk_prompt,
                chunk,
                max_tokens=self.chunk_summary_max_tokens
            )
            chunk_summaries.append(f"第 {index} 段要点：\n{chunk_summary}")

        combined_summary = "\n\n".join(chunk_summaries)
        merged_prompt = (
            f"{final_prompt}\n\n"
            "下面是对各个片段的要点总结，请基于这些要点生成最终的结构化总结。"
        )
        return self._summarize_once(merged_prompt, combined_summary, max_tokens=2000)

    def _chunk_text(self, text: str, max_chars: int) -> list[str]:
        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        chunks = []
        current = []
        current_len = 0

        for paragraph in paragraphs:
            paragraph_len = len(paragraph) + 2
            if current and current_len + paragraph_len > max_chars:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0

            if paragraph_len > max_chars:
                chunks.extend(self._split_long_paragraph(paragraph, max_chars))
            else:
                current.append(paragraph)
                current_len += paragraph_len

        if current:
            chunks.append("\n\n".join(current))

        return chunks

    def _split_long_paragraph(self, paragraph: str, max_chars: int) -> list[str]:
        chunks = []
        start = 0
        paragraph_len = len(paragraph)
        while start < paragraph_len:
            end = min(start + max_chars, paragraph_len)
            chunks.append(paragraph[start:end])
            start = end
        return chunks
    
    def is_available(self) -> bool:
        """
        检查 OpenAI 是否可用
        
        Returns:
            是否可用
        """
        return self.api_key is not None and len(self.api_key) > 0
