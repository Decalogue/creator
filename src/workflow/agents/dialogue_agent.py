"""
对话 Agent

负责生成人物对话内容。
"""

import logging
from typing import Dict, Any, Optional

from .base_creative_agent import BaseCreativeAgent

logger = logging.getLogger(__name__)


class DialogueAgent(BaseCreativeAgent):
    """对话 Agent"""
    
    def __init__(self, index: int, model: str = "gpt", **kwargs):
        role_prompt = """你是一个专业的对话设计师，擅长生成符合人物性格和情节发展的对话。"""
        
        super().__init__(
            role="DialogueAgent",
            role_prompt=role_prompt,
            index=index,
            model=model,
            **kwargs
        )
    
    def generate_content(
        self,
        context: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成对话内容"""
        try:
            prompt = f"请生成人物对话。\n上下文：{context.get('previous_content', '')}"
            messages = [{"role": "user", "content": prompt}]
            response = self.query_func(messages, system_prompt=self.role_prompt)
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            return {
                "content": content,
                "metadata": {"agent": "DialogueAgent", "type": "dialogue"},
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"DialogueAgent error: {e}", exc_info=True)
            return {"content": "", "metadata": {}, "confidence": 0.0}
    
    def validate_content(self, content: str, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证对话内容"""
        return {
            "is_valid": bool(content and len(content.strip()) > 0),
            "issues": [],
            "suggestions": []
        }

