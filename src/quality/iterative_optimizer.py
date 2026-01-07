"""
迭代优化器

基于质量评估结果，迭代优化内容质量。
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass

from .quality_assessor import QualityAssessor, QualityReport
from .consistency_checker import ConsistencyChecker, ConsistencyReport
from .repair_mechanism import RepairMechanism

logger = logging.getLogger(__name__)


@dataclass
class OptimizationConfig:
    """优化配置"""
    max_iterations: int = 5  ***REMOVED*** 最大迭代次数
    quality_threshold: float = 0.8  ***REMOVED*** 质量阈值
    consistency_threshold: float = 0.7  ***REMOVED*** 一致性阈值
    enable_auto_repair: bool = True  ***REMOVED*** 是否启用自动修复
    improvement_threshold: float = 0.05  ***REMOVED*** 改进阈值（如果改进小于此值，停止优化）


class IterativeOptimizer:
    """迭代优化器
    
    基于质量评估和一致性检查结果，迭代优化内容质量。
    
    优化流程：
    1. 评估当前内容质量
    2. 检查一致性
    3. 如果质量不足，进行修复
    4. 重新评估
    5. 重复直到达到阈值或达到最大迭代次数
    """
    
    def __init__(
        self,
        quality_assessor: Optional[QualityAssessor] = None,
        consistency_checker: Optional[ConsistencyChecker] = None,
        repair_mechanism: Optional[RepairMechanism] = None,
        config: Optional[OptimizationConfig] = None
    ):
        """
        初始化迭代优化器
        
        Args:
            quality_assessor: 质量评估器
            consistency_checker: 一致性检查器
            repair_mechanism: 修复机制
            config: 优化配置
        """
        self.quality_assessor = quality_assessor or QualityAssessor()
        self.consistency_checker = consistency_checker or ConsistencyChecker()
        self.repair_mechanism = repair_mechanism or RepairMechanism()
        self.config = config or OptimizationConfig()
        
        logger.info("IterativeOptimizer initialized")
    
    def optimize(
        self,
        content: str,
        expected: Optional[str] = None,
        memories: Optional[List] = None,
        custom_optimizer: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        迭代优化内容
        
        Args:
            content: 要优化的内容
            expected: 预期内容（用于质量评估）
            memories: 相关记忆（用于一致性检查）
            custom_optimizer: 自定义优化函数
            
        Returns:
            优化结果字典：
            - optimized_content: 优化后的内容
            - initial_quality: 初始质量分数
            - final_quality: 最终质量分数
            - iterations: 迭代次数
            - history: 优化历史
        """
        if not content:
            return {
                "optimized_content": content,
                "initial_quality": 0.0,
                "final_quality": 0.0,
                "iterations": 0,
                "history": []
            }
        
        memories = memories or []
        current_content = content
        history = []
        
        ***REMOVED*** 初始评估
        initial_quality = self.quality_assessor.assess(current_content, expected)
        initial_consistency = self.consistency_checker.check(current_content, memories)
        
        history.append({
            "iteration": 0,
            "content": current_content,
            "quality": initial_quality.overall_score,
            "consistency": initial_consistency.score
        })
        
        logger.info(f"Initial quality: {initial_quality.overall_score:.2f}, consistency: {initial_consistency.score:.2f}")
        
        ***REMOVED*** 迭代优化
        for iteration in range(1, self.config.max_iterations + 1):
            ***REMOVED*** 检查是否已达到阈值
            if (initial_quality.overall_score >= self.config.quality_threshold and
                initial_consistency.score >= self.config.consistency_threshold):
                logger.info(f"Quality and consistency already meet threshold, skipping optimization")
                break
            
            ***REMOVED*** 评估当前质量
            quality_report = self.quality_assessor.assess(current_content, expected)
            consistency_report = self.consistency_checker.check(current_content, memories)
            
            ***REMOVED*** 检查是否需要优化
            if (quality_report.overall_score >= self.config.quality_threshold and
                consistency_report.score >= self.config.consistency_threshold):
                logger.info(f"Quality and consistency meet threshold at iteration {iteration}")
                break
            
            ***REMOVED*** 优化内容
            if custom_optimizer:
                ***REMOVED*** 使用自定义优化函数
                optimized = custom_optimizer(current_content, quality_report, consistency_report)
            else:
                ***REMOVED*** 使用默认优化策略
                optimized = self._default_optimize(current_content, quality_report, consistency_report)
            
            ***REMOVED*** 检查改进
            new_quality = self.quality_assessor.assess(optimized, expected)
            improvement = new_quality.overall_score - quality_report.overall_score
            
            if improvement < self.config.improvement_threshold:
                logger.info(f"Improvement too small ({improvement:.3f}), stopping optimization")
                break
            
            current_content = optimized
            
            ***REMOVED*** 记录历史
            history.append({
                "iteration": iteration,
                "content": current_content,
                "quality": new_quality.overall_score,
                "consistency": consistency_report.score,
                "improvement": improvement
            })
            
            logger.info(f"Iteration {iteration}: quality={new_quality.overall_score:.2f}, improvement={improvement:.3f}")
        
        ***REMOVED*** 最终评估
        final_quality = self.quality_assessor.assess(current_content, expected)
        final_consistency = self.consistency_checker.check(current_content, memories)
        
        return {
            "optimized_content": current_content,
            "initial_quality": initial_quality.overall_score,
            "final_quality": final_quality.overall_score,
            "initial_consistency": initial_consistency.score,
            "final_consistency": final_consistency.score,
            "iterations": len(history) - 1,
            "history": history,
            "improvement": final_quality.overall_score - initial_quality.overall_score
        }
    
    def _default_optimize(
        self,
        content: str,
        quality_report: QualityReport,
        consistency_report: ConsistencyReport
    ) -> str:
        """默认优化策略"""
        optimized_content = content
        
        ***REMOVED*** 1. 修复一致性问题
        if consistency_report.issues and self.config.enable_auto_repair:
            repair_result = self.repair_mechanism.repair(
                optimized_content,
                consistency_report,
                auto_repair=True
            )
            optimized_content = repair_result["repaired_content"]
        
        ***REMOVED*** 2. 根据质量报告改进
        if quality_report.suggestions:
            ***REMOVED*** 使用 LLM 根据建议改进
            optimized_content = self._improve_based_on_suggestions(
                optimized_content,
                quality_report.suggestions
            )
        
        return optimized_content
    
    def _improve_based_on_suggestions(
        self,
        content: str,
        suggestions: List[str]
    ) -> str:
        """根据建议改进内容"""
        try:
            suggestions_text = "\n".join(f"- {s}" for s in suggestions)
            prompt = f"""请根据以下建议改进内容：

改进建议：
{suggestions_text}

待改进内容：
{content}

请直接输出改进后的内容，不要添加额外说明。"""
            
            from ..unimem.chat import ark_deepseek_v3_2
            messages = [{"role": "user", "content": prompt}]
            _, improved = ark_deepseek_v3_2(messages)
            
            return improved
        except Exception as e:
            logger.error(f"Error improving content: {e}", exc_info=True)
            return content
    
    def optimize_batch(
        self,
        contents: List[str],
        expected_list: Optional[List[str]] = None,
        memories_list: Optional[List[List]] = None
    ) -> List[Dict[str, Any]]:
        """批量优化"""
        results = []
        expected_list = expected_list or [None] * len(contents)
        memories_list = memories_list or [[]] * len(contents)
        
        for content, expected, memories in zip(contents, expected_list, memories_list):
            result = self.optimize(content, expected, memories)
            results.append(result)
        
        return results

