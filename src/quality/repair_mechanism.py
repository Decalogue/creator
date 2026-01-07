"""
自动修复机制

根据一致性检查结果，自动修复发现的问题。
"""

import logging
from typing import List, Dict, Any, Optional

from .consistency_checker import Issue, ConsistencyReport
from ..unimem.chat import ark_deepseek_v3_2

logger = logging.getLogger(__name__)


class RepairMechanism:
    """自动修复机制
    
    根据一致性检查报告，自动修复发现的问题。
    """
    
    def __init__(self, llm_func=None):
        """
        初始化自动修复机制
        
        Args:
            llm_func: LLM 调用函数
        """
        self.llm_func = llm_func or ark_deepseek_v3_2
        logger.info("RepairMechanism initialized")
    
    def repair(
        self,
        content: str,
        report: ConsistencyReport,
        auto_repair: bool = True
    ) -> Dict[str, Any]:
        """
        修复内容中的一致性问题
        
        Args:
            content: 要修复的内容
            report: 一致性检查报告
            auto_repair: 是否自动修复（如果为False，只返回修复建议）
            
        Returns:
            修复结果字典：
            - repaired_content: 修复后的内容
            - fixed_issues: 已修复的问题列表
            - remaining_issues: 未修复的问题列表
            - suggestions: 修复建议
        """
        if not report.issues:
            return {
                "repaired_content": content,
                "fixed_issues": [],
                "remaining_issues": [],
                "suggestions": []
            }
        
        ***REMOVED*** 按严重程度排序问题
        sorted_issues = sorted(
            report.issues,
            key=lambda x: {"critical": 3, "major": 2, "minor": 1}.get(x.severity, 0),
            reverse=True
        )
        
        fixed_issues = []
        remaining_issues = []
        repaired_content = content
        
        ***REMOVED*** 修复每个问题
        for issue in sorted_issues:
            if auto_repair:
                repair_result = self._repair_issue(repaired_content, issue)
                if repair_result["success"]:
                    repaired_content = repair_result["content"]
                    fixed_issues.append(issue)
                else:
                    remaining_issues.append(issue)
            else:
                remaining_issues.append(issue)
        
        return {
            "repaired_content": repaired_content,
            "fixed_issues": fixed_issues,
            "remaining_issues": remaining_issues,
            "suggestions": [issue.suggestion for issue in remaining_issues if issue.suggestion]
        }
    
    def _repair_issue(self, content: str, issue: Issue) -> Dict[str, Any]:
        """
        修复单个问题
        
        Args:
            content: 要修复的内容
            issue: 要修复的问题
            
        Returns:
            修复结果字典：
            - success: 是否成功
            - content: 修复后的内容
            - message: 修复说明
        """
        try:
            ***REMOVED*** 根据问题类型选择修复策略
            if issue.type == "character":
                return self._repair_character_issue(content, issue)
            elif issue.type == "setting":
                return self._repair_setting_issue(content, issue)
            elif issue.type == "plot":
                return self._repair_plot_issue(content, issue)
            elif issue.type == "style":
                return self._repair_style_issue(content, issue)
            else:
                ***REMOVED*** 使用 LLM 通用修复
                return self._llm_repair(content, issue)
        except Exception as e:
            logger.error(f"Error repairing issue: {e}", exc_info=True)
            return {
                "success": False,
                "content": content,
                "message": f"修复失败: {str(e)}"
            }
    
    def _repair_character_issue(self, content: str, issue: Issue) -> Dict[str, Any]:
        """修复人物一致性问题"""
        ***REMOVED*** 使用 LLM 修复
        return self._llm_repair(content, issue)
    
    def _repair_setting_issue(self, content: str, issue: Issue) -> Dict[str, Any]:
        """修复设定一致性问题"""
        return self._llm_repair(content, issue)
    
    def _repair_plot_issue(self, content: str, issue: Issue) -> Dict[str, Any]:
        """修复情节一致性问题"""
        return self._llm_repair(content, issue)
    
    def _repair_style_issue(self, content: str, issue: Issue) -> Dict[str, Any]:
        """修复风格一致性问题"""
        return self._llm_repair(content, issue)
    
    def _llm_repair(self, content: str, issue: Issue) -> Dict[str, Any]:
        """使用 LLM 修复问题"""
        try:
            prompt = f"""请修复以下内容中的问题：

问题描述：{issue.description}
问题类型：{issue.type}
严重程度：{issue.severity}
修复建议：{issue.suggestion or "请根据问题描述进行修复"}

待修复内容：
{content}

请直接输出修复后的内容，不要添加额外说明。"""
            
            messages = [{"role": "user", "content": prompt}]
            _, repaired = self.llm_func(messages)
            
            return {
                "success": True,
                "content": repaired,
                "message": f"已修复 {issue.type} 类型问题"
            }
        except Exception as e:
            logger.error(f"LLM repair failed: {e}", exc_info=True)
            return {
                "success": False,
                "content": content,
                "message": f"LLM修复失败: {str(e)}"
            }
    
    def batch_repair(
        self,
        contents: List[str],
        reports: List[ConsistencyReport],
        auto_repair: bool = True
    ) -> List[Dict[str, Any]]:
        """批量修复"""
        results = []
        for content, report in zip(contents, reports):
            result = self.repair(content, report, auto_repair)
            results.append(result)
        return results

