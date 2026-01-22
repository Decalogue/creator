"""
修复验证器
验证修复是否真正解决了目标问题
"""
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FixValidationResult:
    """修复验证结果"""
    issue_type: str
    fixed: bool  ***REMOVED*** 问题是否已解决
    introduced_new: bool  ***REMOVED*** 是否引入新问题
    still_exists: bool  ***REMOVED*** 问题是否仍然存在
    verification_score: float  ***REMOVED*** 验证评分（0-1）


class FixValidator:
    """修复验证器"""
    
    def __init__(self):
        self.validators = {
            'style_issue.心理活动过多': self._validate_thought_count,
            'style_issue.对话缺乏动作': self._validate_dialogue_action,
            'style_issue.对话占比过低': self._validate_dialogue_ratio,
            'plot_inconsistency': self._validate_plot_consistency,
            'coherence_issue': self._validate_coherence,
        }
    
    def validate_fix(
        self,
        original_content: str,
        rewritten_content: str,
        target_issues: List[Dict[str, Any]]
    ) -> Dict[str, FixValidationResult]:
        """
        验证修复是否真正解决了目标问题
        
        Args:
            original_content: 原始内容
            rewritten_content: 重写后内容
            target_issues: 目标问题列表
        
        Returns:
            验证结果字典 {issue_type: FixValidationResult}
        """
        results = {}
        
        for issue in target_issues:
            issue_type = issue.get('type', '')
            description = issue.get('description', '')
            
            ***REMOVED*** 确定问题类型（支持模糊匹配）
            actual_issue_type = self._match_issue_type(issue_type, description)
            
            if actual_issue_type and actual_issue_type in self.validators:
                validator_func = self.validators[actual_issue_type]
                result = validator_func(original_content, rewritten_content, issue)
                results[issue_type] = result
            else:
                ***REMOVED*** 使用通用验证器
                result = self._validate_generic(original_content, rewritten_content, issue)
                results[issue_type] = result
        
        return results
    
    def _match_issue_type(self, issue_type: str, description: str) -> Optional[str]:
        """匹配问题类型"""
        ***REMOVED*** 精确匹配
        if issue_type in self.validators:
            return issue_type
        
        ***REMOVED*** 模糊匹配
        if '心理活动' in description or 'thought' in description.lower():
            return 'style_issue.心理活动过多'
        elif '对话缺乏动作' in description or 'dialogue' in description.lower() and 'action' in description.lower():
            return 'style_issue.对话缺乏动作'
        elif '对话占比' in description or 'dialogue_ratio' in description.lower():
            return 'style_issue.对话占比过低'
        elif 'plot' in issue_type.lower() or '情节' in description:
            return 'plot_inconsistency'
        elif 'coherence' in issue_type.lower() or '连贯' in description:
            return 'coherence_issue'
        
        return None
    
    def _validate_thought_count(
        self,
        original_content: str,
        rewritten_content: str,
        issue: Dict[str, Any]
    ) -> FixValidationResult:
        """验证心理活动句子数"""
        ***REMOVED*** 统计心理活动句子
        thought_patterns = [
            r'[^。！？]*想[^。！？]*[。！？]',
            r'[^。！？]*觉得[^。！？]*[。！？]',
            r'[^。！？]*认为[^。！？]*[。！？]',
            r'[^。！？]*感觉[^。！？]*[。！？]',
        ]
        
        original_count = sum(len(re.findall(pattern, original_content)) for pattern in thought_patterns)
        rewritten_count = sum(len(re.findall(pattern, rewritten_content)) for pattern in thought_patterns)
        
        ***REMOVED*** 获取元数据中的原始计数
        metadata = issue.get('metadata', {})
        original_issue_count = metadata.get('thought_sentence_count', original_count)
        
        fixed = rewritten_count <= 10
        still_exists = rewritten_count > 10
        introduced_new = original_count <= 10 and rewritten_count > 10
        
        ***REMOVED*** 计算验证评分
        if original_issue_count > 10:
            improvement = (original_issue_count - rewritten_count) / original_issue_count
            if fixed:
                verification_score = min(1.0, improvement * 2)
            else:
                ***REMOVED*** 即使没有完全修复，如果有改善也给予一定评分
                verification_score = max(0.2, improvement * 1.5) if improvement > 0 else 0.2
        else:
            ***REMOVED*** 原始问题数<=10，如果重写后没有引入新问题，给予高分
            verification_score = 1.0 if not introduced_new else max(0.2, 1.0 - (rewritten_count - original_issue_count) / max(original_issue_count, 1))
        
        return FixValidationResult(
            issue_type=issue.get('type', ''),
            fixed=fixed,
            introduced_new=introduced_new,
            still_exists=still_exists,
            verification_score=verification_score
        )
    
    def _validate_dialogue_action(
        self,
        original_content: str,
        rewritten_content: str,
        issue: Dict[str, Any]
    ) -> FixValidationResult:
        """验证对话中的动作或情绪"""
        ***REMOVED*** 提取对话
        dialogue_pattern = r'["""]([^"""]+)["""]'
        
        original_dialogues = re.findall(dialogue_pattern, original_content)
        rewritten_dialogues = re.findall(dialogue_pattern, rewritten_content)
        
        ***REMOVED*** 检查对话前后是否有动作词
        action_words = ['说', '道', '问', '答', '喊', '叫', '笑', '哭', '皱眉', '摇头', '点头', '握', '看', '望', '走', '跑']
        
        def count_dialogue_with_action(content: str, dialogues: List[str]) -> int:
            count = 0
            for dialogue in dialogues:
                ***REMOVED*** 查找对话前后的上下文
                dialogue_with_quotes = f'"{dialogue}"'
                if dialogue_with_quotes in content:
                    idx = content.index(dialogue_with_quotes)
                    context_before = content[max(0, idx-50):idx]
                    context_after = content[idx+len(dialogue_with_quotes):idx+len(dialogue_with_quotes)+50]
                    
                    if any(word in context_before or word in context_after for word in action_words):
                        count += 1
            return count
        
        original_with_action = count_dialogue_with_action(original_content, original_dialogues)
        rewritten_with_action = count_dialogue_with_action(rewritten_content, rewritten_dialogues)
        
        original_ratio = original_with_action / len(original_dialogues) if original_dialogues else 0
        rewritten_ratio = rewritten_with_action / len(rewritten_dialogues) if rewritten_dialogues else 0
        
        fixed = rewritten_ratio >= 0.3
        still_exists = rewritten_ratio < 0.3
        introduced_new = original_ratio >= 0.3 and rewritten_ratio < 0.3
        
        ***REMOVED*** 计算验证评分
        if original_ratio < 0.3:
            if (0.3 - original_ratio) > 0:
                improvement = (rewritten_ratio - original_ratio) / (0.3 - original_ratio)
                verification_score = min(1.0, max(0.2, improvement))  ***REMOVED*** 至少0.2，避免0.00
            else:
                verification_score = 0.5  ***REMOVED*** 如果原始比率已经接近0.3，给予中性评分
        else:
            ***REMOVED*** 原始比率已经>=0.3，如果重写后保持或改善，给予高分
            if rewritten_ratio >= 0.3:
                verification_score = 1.0 if not introduced_new else 0.5
            else:
                ***REMOVED*** 重写后反而降低，给予低分但至少0.2
                verification_score = max(0.2, rewritten_ratio / 0.3)
        
        return FixValidationResult(
            issue_type=issue.get('type', ''),
            fixed=fixed,
            introduced_new=introduced_new,
            still_exists=still_exists,
            verification_score=verification_score
        )
    
    def _validate_dialogue_ratio(
        self,
        original_content: str,
        rewritten_content: str,
        issue: Dict[str, Any]
    ) -> FixValidationResult:
        """验证对话占比"""
        dialogue_pattern = r'["""]([^"""]+)["""]'
        
        original_dialogues = re.findall(dialogue_pattern, original_content)
        rewritten_dialogues = re.findall(dialogue_pattern, rewritten_content)
        
        original_dialogue_length = sum(len(d) for d in original_dialogues)
        rewritten_dialogue_length = sum(len(d) for d in rewritten_dialogues)
        
        original_ratio = original_dialogue_length / len(original_content) if original_content else 0
        rewritten_ratio = rewritten_dialogue_length / len(rewritten_content) if rewritten_content else 0
        
        fixed = 0.2 <= rewritten_ratio <= 0.4
        still_exists = rewritten_ratio < 0.2 or rewritten_ratio > 0.4
        introduced_new = (0.2 <= original_ratio <= 0.4) and (rewritten_ratio < 0.2 or rewritten_ratio > 0.4)
        
        ***REMOVED*** 计算验证评分
        if original_ratio < 0.2:
            if (0.2 - original_ratio) > 0:
                improvement = min(1.0, (rewritten_ratio - original_ratio) / (0.2 - original_ratio))
                if fixed:
                    verification_score = improvement
                else:
                    ***REMOVED*** 即使没有完全修复，如果有改善也给予一定评分
                    verification_score = max(0.2, improvement * 0.8) if improvement > 0 else 0.2
            else:
                verification_score = 0.5  ***REMOVED*** 如果原始比率已经接近0.2，给予中性评分
        elif original_ratio > 0.4:
            if (original_ratio - 0.4) > 0:
                improvement = min(1.0, (original_ratio - rewritten_ratio) / (original_ratio - 0.4))
                if fixed:
                    verification_score = improvement
                else:
                    ***REMOVED*** 即使没有完全修复，如果有改善也给予一定评分
                    verification_score = max(0.2, improvement * 0.8) if improvement > 0 else 0.2
            else:
                verification_score = 0.5  ***REMOVED*** 如果原始比率已经接近0.4，给予中性评分
        else:
            ***REMOVED*** 原始比率在0.2-0.4之间，如果重写后保持或改善，给予高分
            if 0.2 <= rewritten_ratio <= 0.4:
                verification_score = 1.0 if not introduced_new else 0.5
            else:
                ***REMOVED*** 重写后偏离理想范围，给予低分但至少0.2
                deviation = abs(rewritten_ratio - 0.3) / 0.3  ***REMOVED*** 偏离理想值0.3的程度
                verification_score = max(0.2, 1.0 - deviation)
        
        return FixValidationResult(
            issue_type=issue.get('type', ''),
            fixed=fixed,
            introduced_new=introduced_new,
            still_exists=still_exists,
            verification_score=verification_score
        )
    
    def _validate_plot_consistency(
        self,
        original_content: str,
        rewritten_content: str,
        issue: Dict[str, Any]
    ) -> FixValidationResult:
        """验证情节一致性"""
        ***REMOVED*** 这里简化处理，实际应该检查关键词匹配
        metadata = issue.get('metadata', {})
        expected_keywords = metadata.get('expected_keywords', [])
        
        if not expected_keywords:
            ***REMOVED*** 无法验证，返回中性结果
            return FixValidationResult(
                issue_type=issue.get('type', ''),
                fixed=False,
                introduced_new=False,
                still_exists=True,
                verification_score=0.5
            )
        
        ***REMOVED*** 检查关键词出现率
        original_found = sum(1 for kw in expected_keywords if kw in original_content)
        rewritten_found = sum(1 for kw in expected_keywords if kw in rewritten_content)
        
        original_ratio = original_found / len(expected_keywords) if expected_keywords else 0
        rewritten_ratio = rewritten_found / len(expected_keywords) if expected_keywords else 0
        
        ***REMOVED*** 修复逻辑：考虑改善程度，而不仅仅是绝对值
        ***REMOVED*** 如果原始关键词出现率很低（<0.3），只要重写后有改善就给予一定评分
        if original_ratio < 0.3:
            ***REMOVED*** 原始出现率低，检查是否有改善
            if rewritten_ratio > original_ratio:
                ***REMOVED*** 有改善，计算改善程度
                improvement = (rewritten_ratio - original_ratio) / (0.3 - original_ratio) if (0.3 - original_ratio) > 0 else 1.0
                ***REMOVED*** 改善评分 = 基础分(0.3) + 改善分(最高0.4)
                verification_score = 0.3 + min(0.4, improvement * 0.4)
                fixed = rewritten_ratio >= 0.5  ***REMOVED*** 只有达到0.5才认为完全修复
            elif rewritten_ratio == original_ratio:
                ***REMOVED*** 无改善，给予低分（但至少0.2，避免0.00）
                verification_score = max(0.2, original_ratio * 2)  ***REMOVED*** 至少0.2，或基于原始比率的评分
                fixed = False
            else:
                ***REMOVED*** 恶化，给予更低分（但至少0.1，避免0.00）
                degradation = (original_ratio - rewritten_ratio) / max(original_ratio, 0.1)
                verification_score = max(0.1, 0.2 - degradation * 0.1)
                fixed = False
        else:
            ***REMOVED*** 原始出现率较高，使用标准逻辑
            fixed = rewritten_ratio >= 0.5
            ***REMOVED*** 如果重写后有改善，给予额外加分
            if rewritten_ratio > original_ratio:
                improvement_bonus = min(0.2, (rewritten_ratio - original_ratio) * 0.5)
                verification_score = min(1.0, rewritten_ratio + improvement_bonus)
            else:
                verification_score = max(0.2, rewritten_ratio)  ***REMOVED*** 至少0.2，避免0.00
        
        still_exists = rewritten_ratio < 0.5
        introduced_new = original_ratio >= 0.5 and rewritten_ratio < 0.5
        
        ***REMOVED*** 限制评分范围
        verification_score = max(0.0, min(1.0, verification_score))
        
        return FixValidationResult(
            issue_type=issue.get('type', ''),
            fixed=fixed,
            introduced_new=introduced_new,
            still_exists=still_exists,
            verification_score=verification_score
        )
    
    def _validate_coherence(
        self,
        original_content: str,
        rewritten_content: str,
        issue: Dict[str, Any]
    ) -> FixValidationResult:
        """验证连贯性"""
        ***REMOVED*** 这里简化处理，实际应该使用更复杂的连贯性检查
        ***REMOVED*** 检查基本的一致性：长度、结构等
        original_length = len(original_content)
        rewritten_length = len(rewritten_content)
        
        length_similarity = 1 - abs(original_length - rewritten_length) / max(original_length, 1)
        
        ***REMOVED*** 简化：如果长度相似度较高，认为连贯性保持
        fixed = length_similarity > 0.7
        still_exists = not fixed
        introduced_new = False
        
        verification_score = length_similarity
        
        return FixValidationResult(
            issue_type=issue.get('type', ''),
            fixed=fixed,
            introduced_new=introduced_new,
            still_exists=still_exists,
            verification_score=verification_score
        )
    
    def _validate_generic(
        self,
        original_content: str,
        rewritten_content: str,
        issue: Dict[str, Any]
    ) -> FixValidationResult:
        """通用验证器"""
        ***REMOVED*** 对于没有专门验证器的问题，使用通用验证
        ***REMOVED*** 这里简化处理，实际应该更复杂
        return FixValidationResult(
            issue_type=issue.get('type', ''),
            fixed=False,  ***REMOVED*** 无法确定
            introduced_new=False,
            still_exists=True,
            verification_score=0.5
        )
    
    def calculate_overall_validation_score(self, validation_results: Dict[str, FixValidationResult]) -> float:
        """计算总体验证评分"""
        if not validation_results:
            return 0.0
        
        scores = [result.verification_score for result in validation_results.values()]
        return sum(scores) / len(scores) if scores else 0.0
    
    def is_fix_successful(self, validation_results: Dict[str, FixValidationResult], min_score: float = 0.6) -> bool:
        """判断修复是否成功"""
        if not validation_results:
            return False
        
        ***REMOVED*** 检查是否有问题被解决
        fixed_count = sum(1 for r in validation_results.values() if r.fixed)
        total_count = len(validation_results)
        
        ***REMOVED*** 检查是否引入新问题
        introduced_new_count = sum(1 for r in validation_results.values() if r.introduced_new)
        
        ***REMOVED*** 计算总体评分
        overall_score = self.calculate_overall_validation_score(validation_results)
        
        ***REMOVED*** 成功条件：
        ***REMOVED*** 1. 至少解决了一半的问题
        ***REMOVED*** 2. 没有引入新问题
        ***REMOVED*** 3. 总体评分 >= min_score
        return (
            fixed_count >= total_count * 0.5 and
            introduced_new_count == 0 and
            overall_score >= min_score
        )
