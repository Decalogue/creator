"""
修复策略库
实现问题-修复映射表和修复策略管理
"""
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FixStrategy(Enum):
    """修复策略类型"""
    CONSERVATIVE = "conservative"  ***REMOVED*** 保守修复：最小改动
    AGGRESSIVE = "aggressive"      ***REMOVED*** 激进修复：彻底重构
    SURGICAL = "surgical"          ***REMOVED*** 精准修复：针对特定问题
    ITERATIVE = "iterative"        ***REMOVED*** 迭代修复：逐步改进


@dataclass
class IssueFixStrategy:
    """问题修复策略"""
    issue_type: str
    detection_rule: str
    fix_prompt_template: str
    few_shot_examples: List[str]
    verification_rule: str
    strategy_type: FixStrategy
    success_rate: float = 0.0  ***REMOVED*** 历史成功率
    min_success_rate: float = 0.5  ***REMOVED*** 最低可接受成功率


class FixStrategyLibrary:
    """修复策略库"""
    
    def __init__(self):
        self.strategies = self._initialize_strategies()
        self.fix_history = []  ***REMOVED*** 修复历史记录
    
    def _initialize_strategies(self) -> Dict[str, IssueFixStrategy]:
        """初始化修复策略"""
        strategies = {}
        
        ***REMOVED*** 1. 心理活动描写过多
        strategies["style_issue.心理活动过多"] = IssueFixStrategy(
            issue_type="style_issue.心理活动过多",
            detection_rule="thought_sentence_count > 10",
            fix_prompt_template="""**修复要求：减少心理活动描写**

当前问题：发现{thought_count}句心理活动描写（限制：10句）

**修复方法**：
1. 将心理活动转换为对话：
   - 不好："他想，这到底是怎么回事？"
   - 好：他皱着眉头问道："这到底是怎么回事？"

2. 将心理活动转换为动作：
   - 不好："他觉得非常紧张。"
   - 好：他的手心开始出汗，呼吸变得急促。

3. 删除重复的心理活动：
   - 如果同一想法已经通过对话或动作表达，删除心理活动描述

**具体修改示例**：
{few_shot_examples}

**验证标准**：重写后心理活动句子数必须 ≤ 10句""",
            few_shot_examples=[
                "原文：'他想，这不可能。' → 修改：他摇头说道：'这不可能。'",
                "原文：'她觉得非常害怕。' → 修改：她的身体开始颤抖，声音也变得微弱。",
                "原文：'他认为这个计划有问题。' → 修改：他指着计划书说道：'这个计划有问题。'"
            ],
            verification_rule="thought_sentence_count <= 10",
            strategy_type=FixStrategy.SURGICAL,
            success_rate=0.0
        )
        
        ***REMOVED*** 2. 对话缺乏动作或情绪
        strategies["style_issue.对话缺乏动作"] = IssueFixStrategy(
            issue_type="style_issue.对话缺乏动作",
            detection_rule="dialogue_with_action_ratio < 0.3",
            fix_prompt_template="""**修复要求：在对话中增加动作和情绪描写**

当前问题：{dialogue_count}段对话中，只有{dialogue_with_action}段包含动作或情绪（目标：≥30%）

**修复方法**：
1. 在对话前增加动作描写：
   - 不好："'你来了。'他说。"
   - 好：他抬起头，眼中闪过一丝惊讶："你来了。"

2. 在对话中增加情绪表达：
   - 不好："'我不相信。'她回答。"
   - 好：她紧握双拳，声音中带着愤怒："我不相信。"

3. 结合环境描写：
   - 不好："'这里很危险。'他警告。"
   - 好：他环顾四周，压低声音警告道："这里很危险。"

**具体修改示例**：
{few_shot_examples}

**验证标准**：重写后对话中包含动作或情绪的比例必须 ≥ 30%""",
            few_shot_examples=[
                "原文：'你来了。'他说。 → 修改：他抬起头，眼中闪过一丝惊讶：'你来了。'",
                "原文：'我不相信。'她回答。 → 修改：她紧握双拳，声音中带着愤怒：'我不相信。'",
                "原文：'这里很危险。'他警告。 → 修改：他环顾四周，压低声音警告道：'这里很危险。'"
            ],
            verification_rule="dialogue_with_action_ratio >= 0.3",
            strategy_type=FixStrategy.SURGICAL,
            success_rate=0.0
        )
        
        ***REMOVED*** 3. 对话占比过低
        strategies["style_issue.对话占比过低"] = IssueFixStrategy(
            issue_type="style_issue.对话占比过低",
            detection_rule="dialogue_ratio < 0.2",
            fix_prompt_template="""**修复要求：增加对话占比**

当前问题：对话占比仅{dialogue_ratio_percent:.1f}%（目标：20-40%）

**修复方法**：
1. 将叙述转换为对话：
   - 不好：他告诉她要小心。
   - 好："小心点，"他提醒道，"这里很危险。"

2. 增加推进情节的对话：
   - 在关键情节转折点增加对话
   - 通过对话展现人物性格和关系

3. 增加信息传达的对话：
   - 将背景信息通过对话自然传达
   - 避免大段纯叙述

**具体修改示例**：
{few_shot_examples}

**验证标准**：重写后对话占比必须达到 20-40%""",
            few_shot_examples=[
                "原文：他告诉她要小心。 → 修改：'小心点，'他提醒道，'这里很危险。'",
                "原文：她解释了计划的内容。 → 修改：'计划是这样的，'她开始解释，'我们需要...'"
            ],
            verification_rule="0.2 <= dialogue_ratio <= 0.4",
            strategy_type=FixStrategy.ITERATIVE,
            success_rate=0.0
        )
        
        ***REMOVED*** 4. 情节不一致
        strategies["plot_inconsistency"] = IssueFixStrategy(
            issue_type="plot_inconsistency",
            detection_rule="expected_keywords_found_ratio < 0.5",
            fix_prompt_template="""**修复要求：保持大纲一致性**

当前问题：章节内容可能偏离大纲，预期关键词大部分未出现

**修复方法**：
1. 确保核心情节与大纲一致：
   - 检查章节摘要：{chapter_summary}
   - 确保关键事件和转折点都包含在内

2. 保持人物行为逻辑一致：
   - 人物行为必须符合其性格设定
   - 不能出现与前面章节矛盾的行为

3. 保持世界观设定一致：
   - 不能出现与设定矛盾的描述
   - 保持时间线和空间逻辑正确

**重要**：只修改偏离大纲的部分，不要改变已经正确的内容。

**验证标准**：重写后必须包含大纲中的关键要素""",
            few_shot_examples=[],
            verification_rule="expected_keywords_found_ratio >= 0.5",
            strategy_type=FixStrategy.CONSERVATIVE,
            success_rate=0.0
        )
        
        ***REMOVED*** 5. 连贯性问题
        strategies["coherence_issue"] = IssueFixStrategy(
            issue_type="coherence_issue",
            detection_rule="coherence_score < 0.7",
            fix_prompt_template="""**修复要求：改善连贯性**

当前问题：章节连贯性不足

**修复方法**：
1. 确保与前面章节的衔接：
   - 检查上一章的结尾
   - 确保本章开头自然承接

2. 保持情节逻辑连贯：
   - 确保事件顺序合理
   - 避免突兀的转折

3. 保持人物关系连贯：
   - 人物关系变化必须符合逻辑
   - 不能出现突然的关系转变

**验证标准**：重写后连贯性评分必须 ≥ 0.7""",
            few_shot_examples=[],
            verification_rule="coherence_score >= 0.7",
            strategy_type=FixStrategy.CONSERVATIVE,
            success_rate=0.0
        )
        
        return strategies
    
    def get_strategy(self, issue_type: str, issue_metadata: Dict[str, Any]) -> Optional[IssueFixStrategy]:
        """获取修复策略"""
        ***REMOVED*** 精确匹配
        if issue_type in self.strategies:
            strategy = self.strategies[issue_type]
            ***REMOVED*** 根据元数据填充模板
            return self._fill_strategy_template(strategy, issue_metadata)
        
        ***REMOVED*** 模糊匹配
        for key, strategy in self.strategies.items():
            if key.split('.')[-1] in issue_type or issue_type in key:
                return self._fill_strategy_template(strategy, issue_metadata)
        
        logger.warning(f"未找到问题类型 {issue_type} 的修复策略")
        return None
    
    def _fill_strategy_template(self, strategy: IssueFixStrategy, metadata: Dict[str, Any]) -> IssueFixStrategy:
        """填充策略模板"""
        ***REMOVED*** 创建副本
        filled_strategy = IssueFixStrategy(
            issue_type=strategy.issue_type,
            detection_rule=strategy.detection_rule,
            fix_prompt_template=strategy.fix_prompt_template,
            few_shot_examples=strategy.few_shot_examples,
            verification_rule=strategy.verification_rule,
            strategy_type=strategy.strategy_type,
            success_rate=strategy.success_rate,
            min_success_rate=strategy.min_success_rate
        )
        
        ***REMOVED*** 填充模板变量
        try:
            filled_strategy.fix_prompt_template = filled_strategy.fix_prompt_template.format(
                **metadata,
                few_shot_examples="\n".join(f"- {ex}" for ex in filled_strategy.few_shot_examples)
            )
        except KeyError as e:
            logger.warning(f"策略模板填充失败，缺少变量: {e}")
        
        return filled_strategy
    
    def record_fix_attempt(
        self,
        issue_type: str,
        strategy_type: FixStrategy,
        success: bool,
        validation_score: float = 0.0,
        metadata: Dict[str, Any] = None
    ):
        """
        记录修复尝试（Phase 2: 增强历史学习）
        
        Args:
            issue_type: 问题类型
            strategy_type: 使用的策略类型
            success: 是否成功
            validation_score: 验证评分（0-1）
            metadata: 额外元数据（内容长度、问题严重度等）
        """
        self.fix_history.append({
            'issue_type': issue_type,
            'strategy_type': strategy_type.value,
            'success': success,
            'validation_score': validation_score,
            'metadata': metadata or {},
            'timestamp': __import__('time').time()
        })
        
        ***REMOVED*** 更新策略成功率
        self._update_strategy_success_rate(issue_type)
        
        ***REMOVED*** 限制历史记录数量（保留最近1000条）
        if len(self.fix_history) > 1000:
            self.fix_history = self.fix_history[-1000:]
    
    def _update_strategy_success_rate(self, issue_type: str):
        """更新策略成功率"""
        if issue_type not in self.strategies:
            return
        
        ***REMOVED*** 统计该问题类型的历史成功率
        relevant_history = [
            h for h in self.fix_history
            if h['issue_type'] == issue_type
        ]
        
        if relevant_history:
            success_count = sum(1 for h in relevant_history if h['success'])
            self.strategies[issue_type].success_rate = success_count / len(relevant_history)
            logger.debug(f"问题类型 {issue_type} 的历史成功率: {self.strategies[issue_type].success_rate:.2%}")
    
    def get_best_strategy_for_issue(self, issue_type: str) -> Optional[FixStrategy]:
        """获取问题的最佳策略（基于历史数据）"""
        if issue_type in self.strategies:
            return self.strategies[issue_type].strategy_type
        
        ***REMOVED*** 根据历史数据选择最佳策略
        relevant_history = [
            h for h in self.fix_history
            if h['issue_type'] == issue_type
        ]
        
        if relevant_history:
            ***REMOVED*** 按策略类型统计成功率
            strategy_success_rates = {}
            for h in relevant_history:
                strategy = h['strategy_type']
                if strategy not in strategy_success_rates:
                    strategy_success_rates[strategy] = {'success': 0, 'total': 0, 'avg_score': []}
                
                strategy_success_rates[strategy]['total'] += 1
                if h['success']:
                    strategy_success_rates[strategy]['success'] += 1
                strategy_success_rates[strategy]['avg_score'].append(h.get('validation_score', 0))
            
            ***REMOVED*** 选择成功率最高的策略
            best_strategy = None
            best_rate = 0
            for strategy, stats in strategy_success_rates.items():
                rate = stats['success'] / stats['total']
                avg_score = sum(stats['avg_score']) / len(stats['avg_score']) if stats['avg_score'] else 0
                ***REMOVED*** 综合考虑成功率和平均评分
                combined_score = rate * 0.7 + avg_score * 0.3
                
                if combined_score > best_rate:
                    best_rate = combined_score
                    best_strategy = FixStrategy(strategy)
            
            if best_strategy:
                logger.info(f"基于历史数据，问题类型 {issue_type} 的最佳策略: {best_strategy.value} (成功率: {best_rate:.2%})")
                return best_strategy
        
        ***REMOVED*** 根据问题类型推断策略
        if '心理活动' in issue_type or '对话' in issue_type:
            return FixStrategy.SURGICAL
        elif '一致性' in issue_type or '连贯' in issue_type:
            return FixStrategy.CONSERVATIVE
        else:
            return FixStrategy.ITERATIVE
    
    def get_similar_historical_cases(
        self,
        issue_type: str,
        content_length: int,
        severity: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        获取相似的历史案例（Phase 2: 用于预测）
        
        Args:
            issue_type: 问题类型
            content_length: 内容长度
            severity: 问题严重度
            limit: 返回数量限制
        
        Returns:
            相似的历史案例列表
        """
        similar_cases = []
        
        for h in self.fix_history:
            if h['issue_type'] != issue_type:
                continue
            
            ***REMOVED*** 计算相似度
            similarity = 0.0
            
            ***REMOVED*** 问题类型匹配
            if h['issue_type'] == issue_type:
                similarity += 0.4
            
            ***REMOVED*** 内容长度相似度（±20%范围内）
            hist_length = h.get('metadata', {}).get('content_length', 0)
            if hist_length > 0:
                length_diff = abs(content_length - hist_length) / hist_length
                if length_diff <= 0.2:
                    similarity += 0.3 * (1 - length_diff / 0.2)
            
            ***REMOVED*** 严重度匹配
            hist_severity = h.get('metadata', {}).get('severity', '')
            if hist_severity == severity:
                similarity += 0.3
            
            if similarity > 0.3:  ***REMOVED*** 相似度阈值
                similar_cases.append({
                    **h,
                    'similarity': similarity
                })
        
        ***REMOVED*** 按相似度排序，返回最相似的案例
        similar_cases.sort(key=lambda x: x['similarity'], reverse=True)
        return similar_cases[:limit]
    
    def get_best_strategy_for_issue(self, issue_type: str) -> Optional[FixStrategy]:
        """获取问题的最佳策略"""
        if issue_type in self.strategies:
            return self.strategies[issue_type].strategy_type
        
        ***REMOVED*** 根据问题类型推断策略
        if '心理活动' in issue_type or '对话' in issue_type:
            return FixStrategy.SURGICAL
        elif '一致性' in issue_type or '连贯' in issue_type:
            return FixStrategy.CONSERVATIVE
        else:
            return FixStrategy.ITERATIVE
    
    def select_strategy(self, issue_type: str, severity: str, previous_attempts: int = 0) -> FixStrategy:
        """根据问题类型、严重度和历史选择策略"""
        if severity == 'high':
            return FixStrategy.AGGRESSIVE
        elif previous_attempts > 2:
            return FixStrategy.CONSERVATIVE
        else:
            best_strategy = self.get_best_strategy_for_issue(issue_type)
            return best_strategy or FixStrategy.ITERATIVE
