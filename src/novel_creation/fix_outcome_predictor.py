"""
修复效果预测器
基于历史数据预测修复成功率
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FixPrediction:
    """修复预测结果"""
    success_probability: float  ***REMOVED*** 成功概率（0-1）
    recommendation: str  ***REMOVED*** 建议：'proceed', 'use_alternative_strategy', 'skip_rewrite'
    alternative_strategy: Optional[str] = None  ***REMOVED*** 备用策略
    confidence: float = 0.0  ***REMOVED*** 预测置信度（0-1）
    similar_cases_count: int = 0  ***REMOVED*** 相似历史案例数


class FixOutcomePredictor:
    """修复效果预测器"""
    
    def __init__(self, fix_strategy_library):
        """
        初始化预测器
        
        Args:
            fix_strategy_library: 修复策略库（用于访问历史数据）
        """
        self.fix_strategy_library = fix_strategy_library
    
    def predict_success_probability(
        self,
        issue_type: str,
        content_length: int,
        fix_strategy: str,
        severity: str = 'medium',
        previous_attempts: int = 0
    ) -> FixPrediction:
        """
        基于历史数据预测修复成功率
        
        Args:
            issue_type: 问题类型
            content_length: 内容长度
            fix_strategy: 修复策略
            severity: 问题严重度
            previous_attempts: 之前的尝试次数
        
        Returns:
            修复预测结果
        """
        ***REMOVED*** 获取相似的历史案例
        similar_cases = self.fix_strategy_library.get_similar_historical_cases(
            issue_type, content_length, severity, limit=10
        )
        
        if not similar_cases:
            ***REMOVED*** 没有历史数据，使用默认预测
            logger.debug(f"问题类型 {issue_type} 无历史数据，使用默认预测")
            return FixPrediction(
                success_probability=0.5,  ***REMOVED*** 中性预测
                recommendation='proceed',
                confidence=0.0,
                similar_cases_count=0
            )
        
        ***REMOVED*** 基于相似案例计算成功概率
        success_count = sum(1 for c in similar_cases if c['success'])
        total_count = len(similar_cases)
        base_success_rate = success_count / total_count if total_count > 0 else 0.5
        
        ***REMOVED*** 计算平均验证评分
        avg_validation_score = sum(c.get('validation_score', 0) for c in similar_cases) / total_count
        
        ***REMOVED*** 考虑策略匹配度
        strategy_match_count = sum(1 for c in similar_cases if c['strategy_type'] == fix_strategy)
        strategy_match_rate = strategy_match_count / total_count if total_count > 0 else 0.5
        
        ***REMOVED*** 如果策略匹配度高，提升成功概率
        if strategy_match_rate > 0.5:
            strategy_bonus = (strategy_match_rate - 0.5) * 0.2
        else:
            strategy_bonus = (strategy_match_rate - 0.5) * 0.1
        
        ***REMOVED*** 考虑之前的尝试次数（尝试次数越多，成功率可能越低）
        attempt_penalty = min(0.2, previous_attempts * 0.05)
        
        ***REMOVED*** 综合计算成功概率
        success_probability = (
            base_success_rate * 0.4 +
            avg_validation_score * 0.3 +
            strategy_match_rate * 0.2 +
            (1 - attempt_penalty) * 0.1
        ) + strategy_bonus
        
        ***REMOVED*** 限制在合理范围内
        success_probability = max(0.0, min(1.0, success_probability))
        
        ***REMOVED*** 计算置信度（基于历史案例数量）
        confidence = min(1.0, total_count / 10.0)  ***REMOVED*** 10个案例 = 100%置信度
        
        ***REMOVED*** 生成建议
        if success_probability < 0.3:
            recommendation = 'skip_rewrite'
            alternative_strategy = None
        elif success_probability < 0.5:
            recommendation = 'use_alternative_strategy'
            ***REMOVED*** 尝试找到更好的策略
            alternative_strategy = self._find_better_strategy(issue_type, similar_cases, fix_strategy)
        else:
            recommendation = 'proceed'
            alternative_strategy = None
        
        logger.info(
            f"修复预测：问题类型={issue_type}, "
            f"策略={fix_strategy}, "
            f"成功概率={success_probability:.2%}, "
            f"置信度={confidence:.2%}, "
            f"建议={recommendation}, "
            f"相似案例数={total_count}"
        )
        
        return FixPrediction(
            success_probability=success_probability,
            recommendation=recommendation,
            alternative_strategy=alternative_strategy,
            confidence=confidence,
            similar_cases_count=total_count
        )
    
    def _find_better_strategy(
        self,
        issue_type: str,
        similar_cases: List[Dict[str, Any]],
        current_strategy: str
    ) -> Optional[str]:
        """查找更好的策略"""
        ***REMOVED*** 按策略类型统计成功率
        strategy_stats = {}
        for case in similar_cases:
            strategy = case['strategy_type']
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {'success': 0, 'total': 0, 'avg_score': []}
            
            strategy_stats[strategy]['total'] += 1
            if case['success']:
                strategy_stats[strategy]['success'] += 1
            strategy_stats[strategy]['avg_score'].append(case.get('validation_score', 0))
        
        ***REMOVED*** 找到成功率最高的策略（排除当前策略）
        best_strategy = None
        best_score = 0
        
        for strategy, stats in strategy_stats.items():
            if strategy == current_strategy:
                continue
            
            if stats['total'] < 2:  ***REMOVED*** 至少需要2个案例
                continue
            
            success_rate = stats['success'] / stats['total']
            avg_score = sum(stats['avg_score']) / len(stats['avg_score']) if stats['avg_score'] else 0
            combined_score = success_rate * 0.7 + avg_score * 0.3
            
            if combined_score > best_score:
                best_score = combined_score
                best_strategy = strategy
        
        if best_strategy and best_score > 0.5:
            logger.info(f"找到更好的策略: {best_strategy} (评分: {best_score:.2%})")
            return best_strategy
        
        return None
    
    def should_proceed_with_rewrite(
        self,
        issue_type: str,
        content_length: int,
        fix_strategy: str,
        severity: str = 'medium',
        previous_attempts: int = 0,
        min_success_probability: float = 0.4
    ) -> bool:
        """
        判断是否应该进行重写
        
        Args:
            issue_type: 问题类型
            content_length: 内容长度
            fix_strategy: 修复策略
            severity: 问题严重度
            previous_attempts: 之前的尝试次数
            min_success_probability: 最低成功概率阈值
        
        Returns:
            是否应该进行重写
        """
        prediction = self.predict_success_probability(
            issue_type, content_length, fix_strategy, severity, previous_attempts
        )
        
        ***REMOVED*** 如果严重度高，降低阈值
        if severity == 'high':
            min_success_probability = max(0.3, min_success_probability - 0.1)
        
        should_proceed = (
            prediction.success_probability >= min_success_probability and
            prediction.recommendation != 'skip_rewrite'
        )
        
        if not should_proceed:
            logger.info(
                f"预测不建议重写：成功概率{prediction.success_probability:.2%} "
                f"低于阈值{min_success_probability:.2%}，建议={prediction.recommendation}"
            )
        
        return should_proceed
