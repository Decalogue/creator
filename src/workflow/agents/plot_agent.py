"""
情节 Agent

负责生成和优化故事情节，包括：
- 情节设计
- 冲突设置
- 节奏控制
"""

import logging
from typing import Dict, Any, Optional

from .base_creative_agent import BaseCreativeAgent

logger = logging.getLogger(__name__)


class PlotAgent(BaseCreativeAgent):
    """情节 Agent
    
    专门负责故事情节的生成和优化。
    """
    
    def __init__(self, index: int, model: str = "gpt", **kwargs):
        role_prompt = """你是一个专业的情节设计师，擅长：
1. 设计引人入胜的故事情节
2. 设置合理的冲突和转折
3. 控制故事节奏
4. 确保情节逻辑连贯

请根据给定的上下文和约束条件，生成高质量的情节内容。"""
        
        super().__init__(
            role="PlotAgent",
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
        """生成情节内容"""
        try:
            ***REMOVED*** 构建提示词
            prompt = self._build_plot_prompt(context, constraints)
            
            ***REMOVED*** 调用模型生成
            messages = [{"role": "user", "content": prompt}]
            response = self.query_func(messages, system_prompt=self.role_prompt)
            
            content = response.get("content", "") if isinstance(response, dict) else str(response)
            
            return {
                "content": content,
                "metadata": {
                    "agent": "PlotAgent",
                    "type": "plot",
                    "constraints": constraints or {}
                },
                "confidence": 0.8  ***REMOVED*** 简化处理
            }
        except Exception as e:
            logger.error(f"PlotAgent generate_content error: {e}", exc_info=True)
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
        """验证情节内容"""
        issues = []
        suggestions = []
        
        ***REMOVED*** 简化验证逻辑
        if not content or len(content.strip()) < 50:
            issues.append("情节内容过短")
            suggestions.append("请提供更详细的情节描述")
        
        if requirements:
            if "min_length" in requirements and len(content) < requirements["min_length"]:
                issues.append(f"内容长度不足（要求至少{requirements['min_length']}字）")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _build_plot_prompt(
        self,
        context: Dict[str, Any],
        constraints: Optional[Dict[str, Any]]
    ) -> str:
        """构建情节生成提示词"""
        prompt_parts = ["请生成故事情节。"]
        
        if context.get("previous_content"):
            prompt_parts.append(f"\n前文内容：\n{context['previous_content']}")
        
        if context.get("memories"):
            prompt_parts.append(f"\n相关记忆：\n{context['memories']}")
        
        if constraints:
            if "style" in constraints:
                prompt_parts.append(f"\n写作风格：{constraints['style']}")
            if "tone" in constraints:
                prompt_parts.append(f"\n情感基调：{constraints['tone']}")
            if "conflict" in constraints:
                prompt_parts.append(f"\n冲突要求：{constraints['conflict']}")
        
        return "\n".join(prompt_parts)

