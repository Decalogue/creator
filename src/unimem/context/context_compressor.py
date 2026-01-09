"""
上下文压缩

使用 LLM 对长文本进行智能压缩，保留关键信息。

工业级特性：
- 参数验证和输入检查
- 统一异常处理
"""

import logging
from typing import Optional

from ..chat import ark_deepseek_v3_2
from ..adapters.base import AdapterError

logger = logging.getLogger(__name__)


class ContextCompressor:
    """上下文压缩器
    
    使用 LLM 对长文本进行智能压缩，保留关键信息。
    """
    
    def __init__(self, llm_func=None):
        """
        初始化上下文压缩器
        
        Args:
            llm_func: LLM 调用函数，如果为 None 则使用默认函数
        """
        self.llm_func = llm_func or ark_deepseek_v3_2
        logger.info("ContextCompressor initialized")
    
    def compress(
        self,
        content: str,
        target_length: int,
        preserve_key_info: bool = True
    ) -> str:
        """
        压缩内容到目标长度
        
        Args:
            content: 要压缩的内容（不能为空）
            target_length: 目标长度（字符数，必须 > 0）
            preserve_key_info: 是否保留关键信息（默认 True）
            
        Returns:
            压缩后的内容
            
        Raises:
            AdapterError: 如果参数无效
        """
        if not content or not isinstance(content, str):
            raise AdapterError("content must be a non-empty string", adapter_name="ContextCompressor")
        if target_length <= 0:
            raise AdapterError(f"target_length must be positive, got {target_length}", adapter_name="ContextCompressor")
        
        if len(content) <= target_length:
            return content
        
        try:
            ***REMOVED*** 构建压缩提示词
            prompt = f"""请将以下内容压缩到约{target_length}字，{"保留所有关键信息" if preserve_key_info else "可以适当精简"}：

{content}

压缩要求：
1. 保留核心信息和关键细节
2. 保持逻辑连贯性
3. 尽量接近目标长度
4. 使用简洁的语言

压缩后的内容："""
            
            messages = [{"role": "user", "content": prompt}]
            _, compressed = self.llm_func(messages)
            
            ***REMOVED*** 确保不超过目标长度太多
            if len(compressed) > target_length * 1.2:
                ***REMOVED*** 如果压缩后仍然过长，进行二次压缩
                compressed = self._simple_truncate(compressed, target_length)
            
            logger.debug(f"Compressed content from {len(content)} to {len(compressed)} chars")
            return compressed
            
        except Exception as e:
            logger.error(f"Error compressing content: {e}", exc_info=True)
            ***REMOVED*** 降级策略：简单截断
            return self._simple_truncate(content, target_length)
    
    def _simple_truncate(self, content: str, target_length: int) -> str:
        """简单截断（降级策略）"""
        if len(content) <= target_length:
            return content
        
        ***REMOVED*** 尝试在句号、问号、感叹号处截断
        truncated = content[:target_length]
        last_period = max(
            truncated.rfind('。'),
            truncated.rfind('！'),
            truncated.rfind('？'),
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?')
        )
        
        if last_period > target_length * 0.8:  ***REMOVED*** 如果句号位置合理
            return truncated[:last_period + 1]
        else:
            return truncated + "..."
    
    def compress_batch(
        self,
        contents: list[str],
        target_length_per_item: int
    ) -> list[str]:
        """批量压缩"""
        return [self.compress(content, target_length_per_item) for content in contents]

