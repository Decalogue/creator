"""
质量 Agent

负责评估和优化内容质量。
"""

import logging
from typing import Dict, Any, Optional

from .base_creative_agent import BaseCreativeAgent

logger = logging.getLogger(__name__)


class QualityAgent(BaseCreativeAgent):
    """质量 Agent"""
    
    def __init__(self, index: int, model: str = "gpt", **kwargs):
        role_prompt = """你是一个专业的质量评估员，负责评估内容的整体质量并提供改进建议。"""
        
        super().__init__(
            role="QualityAgent",
            role_prompt=role_prompt,
            index=index,
            model=model,
            **kwargs
        )
    
    def generate_content(self, context: Dict[str, Any], constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """评估内容质量"""
        try:
            prompt = f"请评估以下内容的质量：\n{context.get('content', '')}"
            messages = [{"role": "user", "content": prompt}]
            response = self.query_func(messages, system_prompt=self.role_prompt)
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            return {
                "content": content,
                "metadata": {"agent": "QualityAgent", "type": "quality"},
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"QualityAgent error: {e}", exc_info=True)
            return {"content": "", "metadata": {}, "confidence": 0.0}
    
    def validate_content(self, content: str, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证质量"""
        return {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }

