"""
场景 Agent

负责生成和优化场景描述，包括：
- 场景设定
- 环境描写
- 氛围营造
"""

import logging
from typing import Dict, Any, Optional

from .base_creative_agent import BaseCreativeAgent

logger = logging.getLogger(__name__)


class SceneAgent(BaseCreativeAgent):
    """场景 Agent
    
    专门负责场景相关内容的生成和优化。
    """
    
    def __init__(self, index: int, model: str = "gpt", **kwargs):
        role_prompt = """你是一个专业的场景设计师，擅长：
1. 描绘生动的场景环境
2. 营造合适的氛围
3. 通过环境描写推动情节
4. 保持场景与情节的一致性

请根据给定的场景要求和上下文，生成高质量的场景描述。"""
        
        super().__init__(
            role="SceneAgent",
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
        """生成场景内容"""
        try:
            prompt = self._build_scene_prompt(context, constraints)
            
            messages = [{"role": "user", "content": prompt}]
            response = self.query_func(messages, system_prompt=self.role_prompt)
            
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            return {
                "content": content,
                "metadata": {
                    "agent": "SceneAgent",
                    "type": "scene",
                    "scene_type": context.get("scene_type", "未知"),
                    "constraints": constraints or {}
                },
                "confidence": 0.8
            }
        except Exception as e:
            logger.error(f"SceneAgent generate_content error: {e}", exc_info=True)
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
        """验证场景内容"""
        issues = []
        suggestions = []
        
        if not content or len(content.strip()) < 30:
            issues.append("场景描述过短")
            suggestions.append("请提供更详细的场景描述")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _build_scene_prompt(
        self,
        context: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> str:
        """构建场景生成提示词"""
        prompt_parts = ["请生成场景描述。"]
        
        if context.get("scene_type"):
            prompt_parts.append(f"\n场景类型：{context['scene_type']}")
        
        if context.get("location"):
            prompt_parts.append(f"\n地点：{context['location']}")
        
        if context.get("atmosphere"):
            prompt_parts.append(f"\n氛围要求：{context['atmosphere']}")
        
        if context.get("previous_content"):
            prompt_parts.append(f"\n前文内容：\n{context['previous_content']}")
        
        if constraints:
            if "detail_level" in constraints:
                prompt_parts.append(f"\n详细程度：{constraints['detail_level']}")
        
        return "\n".join(prompt_parts)

