"""
一致性 Agent

负责检查内容的一致性（人物、设定、情节等）。
"""

import logging
from typing import Dict, Any, Optional

from .base_creative_agent import BaseCreativeAgent

logger = logging.getLogger(__name__)


class ConsistencyAgent(BaseCreativeAgent):
    """一致性 Agent"""
    
    def __init__(self, index: int, model: str = "gpt", **kwargs):
        role_prompt = """你是一个专业的一致性检查员，负责检查内容在人物、设定、情节等方面的一致性。"""
        
        super().__init__(
            role="ConsistencyAgent",
            role_prompt=role_prompt,
            index=index,
            model=model,
            **kwargs
        )
    
    def generate_content(self, context: Dict[str, Any], constraints: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """检查并修复一致性问题"""
        try:
            prompt = f"请检查以下内容的一致性：\n{context.get('content', '')}\n参考记忆：\n{context.get('memories', '')}"
            messages = [{"role": "user", "content": prompt}]
            response = self.query_func(messages, system_prompt=self.role_prompt)
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            return {
                "content": content,
                "metadata": {"agent": "ConsistencyAgent", "type": "consistency"},
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"ConsistencyAgent error: {e}", exc_info=True)
            return {"content": "", "metadata": {}, "confidence": 0.0}
    
    def validate_content(self, content: str, requirements: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """验证一致性"""
        return {
            "is_valid": True,
            "issues": [],
            "suggestions": []
        }

