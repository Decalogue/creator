"""
人物 Agent

负责生成和优化人物相关内容，包括：
- 人物设定
- 人物对话
- 人物行为
"""

import logging
from typing import Dict, Any, Optional

from .base_creative_agent import BaseCreativeAgent

logger = logging.getLogger(__name__)


class CharacterAgent(BaseCreativeAgent):
    """人物 Agent
    
    专门负责人物相关内容的生成和优化。
    """
    
    def __init__(self, index: int, model: str = "gpt", **kwargs):
        role_prompt = """你是一个专业的人物设计师，擅长：
1. 设计立体的人物形象
2. 生成符合人物性格的对话
3. 描述人物的行为和动作
4. 保持人物一致性

请根据给定的人物设定和上下文，生成高质量的人物相关内容。"""
        
        super().__init__(
            role="CharacterAgent",
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
        """生成人物相关内容"""
        try:
            prompt = self._build_character_prompt(context, constraints)
            
            messages = [{"role": "user", "content": prompt}]
            response = self.query_func(messages, system_prompt=self.role_prompt)
            
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            return {
                "content": content,
                "metadata": {
                    "agent": "CharacterAgent",
                    "type": "character",
                    "character_name": context.get("character_name", "未知"),
                    "constraints": constraints or {}
                },
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"CharacterAgent generate_content error: {e}", exc_info=True)
            return {
                "content": "",
                "metadata": {},
                "confidence": 0.0
            }
    
    def validate_content(
        self,
        content: str,
        requirements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """验证人物内容"""
        issues = []
        suggestions = []
        
        if not content or len(content.strip()) < 20:
            issues.append("人物内容过短")
            suggestions.append("请提供更详细的人物描述或对话")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _build_character_prompt(
        self,
        context: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> str:
        """构建人物生成提示词"""
        prompt_parts = ["请生成人物相关内容。"]
        
        if context.get("character_name"):
            prompt_parts.append(f"\n人物名称：{context['character_name']}")
        
        if context.get("character_profile"):
            prompt_parts.append(f"\n人物设定：\n{context['character_profile']}")
        
        if context.get("previous_content"):
            prompt_parts.append(f"\n前文内容：\n{context['previous_content']}")
        
        if constraints:
            if "dialogue_style" in constraints:
                prompt_parts.append(f"\n对话风格：{constraints['dialogue_style']}")
        
        return "\n".join(prompt_parts)

