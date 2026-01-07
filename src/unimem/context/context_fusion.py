"""
上下文融合

将多个上下文源融合成一个统一的上下文。
"""

import logging
from typing import List, Dict, Any, Optional

from ..chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


class ContextFusion:
    """上下文融合器
    
    将多个上下文源融合成一个统一的上下文，支持：
    - 去重
    - 优先级排序
    - 智能合并
    """
    
    def __init__(self, llm_func=None):
        """
        初始化上下文融合器
        
        Args:
            llm_func: LLM 调用函数
        """
        self.llm_func = llm_func or ark_deepseek_v3_2
        logger.info("ContextFusion initialized")
    
    def fuse(
        self,
        contexts: List[str],
        strategy: str = "merge",
        max_length: Optional[int] = None
    ) -> str:
        """
        融合多个上下文
        
        Args:
            contexts: 上下文列表
            strategy: 融合策略（"merge" 或 "concatenate"）
            max_length: 最大长度限制
            
        Returns:
            融合后的上下文
        """
        if not contexts:
            return ""
        
        if len(contexts) == 1:
            result = contexts[0]
            if max_length and len(result) > max_length:
                from .context_compressor import ContextCompressor
                compressor = ContextCompressor(self.llm_func)
                return compressor.compress(result, max_length)
            return result
        
        try:
            if strategy == "merge":
                ***REMOVED*** 使用 LLM 智能合并
                return self._llm_merge(contexts, max_length)
            else:
                ***REMOVED*** 简单拼接
                return self._concatenate(contexts, max_length)
        except Exception as e:
            logger.error(f"Error fusing contexts: {e}", exc_info=True)
            ***REMOVED*** 降级策略：简单拼接
            return self._concatenate(contexts, max_length)
    
    def _llm_merge(self, contexts: List[str], max_length: Optional[int]) -> str:
        """使用 LLM 智能合并"""
        prompt_parts = ["请将以下多个上下文融合成一个统一的上下文：\n"]
        
        for i, ctx in enumerate(contexts, 1):
            prompt_parts.append(f"上下文 {i}：\n{ctx}\n")
        
        if max_length:
            prompt_parts.append(f"\n要求：融合后的内容不超过{max_length}字，保留所有关键信息。")
        else:
            prompt_parts.append("\n要求：融合后的内容应保留所有关键信息，去除重复内容。")
        
        prompt_parts.append("\n融合后的上下文：")
        
        prompt = "\n".join(prompt_parts)
        messages = [{"role": "user", "content": prompt}]
        _, merged = self.llm_func(messages)
        
        ***REMOVED*** 如果超过最大长度，进行压缩
        if max_length and len(merged) > max_length:
            from .context_compressor import ContextCompressor
            compressor = ContextCompressor(self.llm_func)
            merged = compressor.compress(merged, max_length)
        
        return merged
    
    def _concatenate(self, contexts: List[str], max_length: Optional[int]) -> str:
        """简单拼接"""
        ***REMOVED*** 去重
        seen = set()
        unique_contexts = []
        for ctx in contexts:
            if ctx and ctx not in seen:
                seen.add(ctx)
                unique_contexts.append(ctx)
        
        ***REMOVED*** 拼接
        fused = "\n\n".join(unique_contexts)
        
        ***REMOVED*** 如果超过最大长度，截断
        if max_length and len(fused) > max_length:
            fused = fused[:max_length] + "..."
        
        return fused
    
    def fuse_with_weights(
        self,
        contexts: List[str],
        weights: List[float],
        max_length: Optional[int] = None
    ) -> str:
        """
        带权重的融合
        
        Args:
            contexts: 上下文列表
            weights: 权重列表（与 contexts 对应）
            max_length: 最大长度限制
            
        Returns:
            融合后的上下文
        """
        if len(contexts) != len(weights):
            logger.warning("Contexts and weights length mismatch, using equal weights")
            return self.fuse(contexts, max_length=max_length)
        
        ***REMOVED*** 按权重排序
        weighted = list(zip(contexts, weights))
        weighted.sort(key=lambda x: x[1], reverse=True)
        
        ***REMOVED*** 提取排序后的上下文
        sorted_contexts = [ctx for ctx, _ in weighted]
        
        return self.fuse(sorted_contexts, strategy="merge", max_length=max_length)

