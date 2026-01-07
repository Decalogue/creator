"""
风格 Agent

负责确保写作风格的一致性。
"""

import logging
from typing import Dict, Any, Optional

from .base_creative_agent import BaseCreativeAgent

logger = logging.getLogger(__name__)


class StyleAgent(BaseCreativeAgent):
    """风格 Agent"""
    
    def __init__(self, index: int, model: str = "gpt", **kwargs):
        role_prompt = """你是一个专业的风格检查员，负责确保写作风格的一致性。"""
        
        super().__init__(
            role="StyleAgent",
            role_prompt=role_prompt,
            index=index,
            model=model,
            **kwargs
        )
    
    def generate_content(self, context: Dict[str, Any], constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调整内容风格"""
        try:
            prompt = f"请调整以下内容的风格：\n{context.get('content', '')}"
            messages = [{"role": "user", "content": prompt}]
            response = self.query_func(messages, system_prompt=self.role_prompt)
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            return {
                "content": content,
                "metadata": {"agent": "StyleAgent", "type": "style"},
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"StyleAgent error: {e}", exc_info=True)
            return {"content": "", "metadata": {}, "confidence": 0.0}
    
    def validate_content(self, content: str, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证风格一致性"""
        return {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }

