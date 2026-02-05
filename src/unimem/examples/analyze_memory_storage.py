#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆存储分析脚本
分析Neo4j和Qdrant中的记忆存储情况，检查decision_trace、reasoning、DecisionEvent的覆盖率
"""

import sys
import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem.neo4j import get_graph
from py2neo import NodeMatcher
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def analyze_memory_storage():
    """分析记忆存储情况"""
    print("\n" + "="*70)
    print("记忆存储分析")
    print("="*70 + "\n")
    
    try:
        graph = get_graph()
        if not graph:
            print("❌ 无法连接到Neo4j")
            return
        
        matcher = NodeMatcher(graph)
        
        # 1. 统计Memory节点
        print("【1. Memory节点统计】")
        memory_query = "MATCH (m:Memory) RETURN count(m) as count"
        memory_count = graph.run(memory_query).data()[0]['count']
        print(f"  总Memory数: {memory_count}")
        
        # 按类型统计
        type_query = """
        MATCH (m:Memory)
        RETURN m.memory_type as type, count(m) as count
        ORDER BY count DESC
        """
        type_stats = graph.run(type_query).data()
        print("  按类型分布:")
        for stat in type_stats:
            print(f"    - {stat['type'] or '未知'}: {stat['count']}个")
        
        # 2. DecisionEvent节点统计
        print("\n【2. DecisionEvent节点统计】")
        event_query = "MATCH (e:DecisionEvent) RETURN count(e) as count"
        event_count = graph.run(event_query).data()[0]['count']
        print(f"  总DecisionEvent数: {event_count}")
        
        # 检查DecisionEvent与Memory的关联
        relation_query = """
        MATCH (e:DecisionEvent)-[:TRACES]->(m:Memory)
        RETURN count(e) as count
        """
        related_count = graph.run(relation_query).data()[0]['count']
        print(f"  已关联到Memory的DecisionEvent: {related_count}个")
        
        if event_count > 0:
            # 获取最近的DecisionEvent
            recent_query = """
            MATCH (e:DecisionEvent)
            RETURN e.id as id, e.memory_id as memory_id, e.reasoning as reasoning, e.timestamp as timestamp
            ORDER BY e.timestamp DESC
            LIMIT 10
            """
            recent_events = graph.run(recent_query).data()
            print("\n  最近的DecisionEvent (前10个):")
            for i, event in enumerate(recent_events, 1):
                reasoning = event.get('reasoning', '') or ''
                print(f"    {i}. {event['id']}")
                print(f"       Memory ID: {event['memory_id']}")
                print(f"       Reasoning: {reasoning[:60] if reasoning else '无'}...")
        
        # 3. decision_trace覆盖率分析
        print("\n【3. decision_trace覆盖率分析】")
        trace_query = """
        MATCH (m:Memory)
        RETURN 
            count(m) as total,
            sum(CASE WHEN m.decision_trace IS NOT NULL AND m.decision_trace <> '' THEN 1 ELSE 0 END) as with_trace
        """
        trace_stats = graph.run(trace_query).data()[0]
        total = trace_stats['total']
        with_trace = trace_stats['with_trace']
        coverage = (with_trace / total * 100) if total > 0 else 0
        print(f"  总Memory数: {total}")
        print(f"  有decision_trace的Memory: {with_trace}")
        print(f"  覆盖率: {coverage:.1f}%")
        
        # 按类型分析decision_trace覆盖率
        type_trace_query = """
        MATCH (m:Memory)
        WITH m.memory_type as type, m,
            CASE WHEN m.decision_trace IS NOT NULL AND m.decision_trace <> '' THEN 1 ELSE 0 END as has_trace
        RETURN 
            type,
            count(m) as total,
            sum(has_trace) as with_trace
        ORDER BY total DESC
        """
        type_trace_stats = graph.run(type_trace_query).data()
        if type_trace_stats:
            print("\n  按类型分析:")
            for stat in type_trace_stats:
                type_name = stat['type'] or '未知'
                total_type = stat['total']
                with_trace_type = stat['with_trace']
                coverage_type = (with_trace_type / total_type * 100) if total_type > 0 else 0
                print(f"    - {type_name}: {with_trace_type}/{total_type} ({coverage_type:.1f}%)")
        
        # 4. reasoning覆盖率分析
        print("\n【4. reasoning覆盖率分析】")
        reasoning_query = """
        MATCH (m:Memory)
        RETURN 
            count(m) as total,
            sum(CASE WHEN m.reasoning IS NOT NULL AND m.reasoning <> '' THEN 1 ELSE 0 END) as with_reasoning
        """
        reasoning_stats = graph.run(reasoning_query).data()[0]
        total = reasoning_stats['total']
        with_reasoning = reasoning_stats['with_reasoning']
        coverage = (with_reasoning / total * 100) if total > 0 else 0
        print(f"  总Memory数: {total}")
        print(f"  有reasoning的Memory: {with_reasoning}")
        print(f"  覆盖率: {coverage:.1f}%")
        
        # 5. Memory关系分析
        print("\n【5. Memory关系分析】")
        relation_query = """
        MATCH (m1:Memory)-[r:RELATED_TO]->(m2:Memory)
        RETURN count(r) as count
        """
        relation_count = graph.run(relation_query).data()[0]['count']
        print(f"  RELATED_TO关系数: {relation_count}")
        
        # 检查反馈记忆与脚本记忆的关联
        feedback_script_query = """
        MATCH (f:Memory)-[:RELATED_TO]->(s:Memory)
        WHERE f.memory_type = 'feedback' AND s.memory_type = 'script'
        RETURN count(f) as count
        """
        feedback_script_count = graph.run(feedback_script_query).data()[0]['count']
        print(f"  反馈记忆->脚本记忆关系: {feedback_script_count}")
        
        # 6. 最近创建的Memory分析
        print("\n【6. 最近创建的Memory分析（前10个）】")
        recent_memory_query = """
        MATCH (m:Memory)
        OPTIONAL MATCH (e:DecisionEvent)-[:TRACES]->(m)
        RETURN 
            m.id as id,
            m.memory_type as type,
            m.reasoning as reasoning,
            CASE WHEN m.decision_trace IS NOT NULL AND m.decision_trace <> '' THEN '是' ELSE '否' END as has_trace,
            CASE WHEN e IS NOT NULL THEN '是' ELSE '否' END as has_event,
            m.created_at as created_at
        ORDER BY m.created_at DESC
        LIMIT 10
        """
        recent_memories = graph.run(recent_memory_query).data()
        for i, mem in enumerate(recent_memories, 1):
            print(f"  {i}. {mem['id'][:36]}...")
            print(f"     类型: {mem['type'] or '未知'}")
            print(f"     有decision_trace: {mem['has_trace']}")
            print(f"     有DecisionEvent: {mem['has_event']}")
            reasoning = mem.get('reasoning', '') or ''
            if reasoning:
                print(f"     Reasoning: {reasoning[:60]}...")
        
        # 7. 问题诊断
        print("\n【7. 问题诊断】")
        issues = []
        
        if coverage < 80:
            issues.append({
                "severity": "高",
                "issue": f"decision_trace覆盖率过低 ({coverage:.1f}%)",
                "suggestion": "检查retain方法中decision_trace的创建逻辑，确保所有Memory都有decision_trace"
            })
        
        reasoning_coverage = (with_reasoning / total * 100) if total > 0 else 0
        if reasoning_coverage < 80:
            issues.append({
                "severity": "中",
                "issue": f"reasoning覆盖率较低 ({reasoning_coverage:.1f}%)",
                "suggestion": "增强reasoning提取逻辑，在retain和reflect中更主动地生成reasoning"
            })
        
        if event_count < memory_count * 0.8:
            issues.append({
                "severity": "高",
                "issue": f"DecisionEvent数量 ({event_count}) 少于Memory数量 ({memory_count})",
                "suggestion": "检查DecisionEvent创建逻辑，确保每个有decision_trace的Memory都有对应的DecisionEvent"
            })
        
        if relation_count == 0:
            issues.append({
                "severity": "中",
                "issue": "Memory之间没有建立关系",
                "suggestion": "在store_feedback_to_unimem和optimize_and_regenerate中建立RELATED_TO关系"
            })
        
        if issues:
            for issue in issues:
                print(f"  [{issue['severity']}] {issue['issue']}")
                print(f"     建议: {issue['suggestion']}")
        else:
            print("  ✓ 未发现明显问题")
        
        # 8. 改进建议
        print("\n【8. 改进建议】")
        suggestions = []
        
        if coverage < 100:
            suggestions.append("1. 确保所有Memory在retain时都有decision_trace")
            suggestions.append("   - 检查generate_video_script.py中的store_script_to_unimem")
            suggestions.append("   - 检查store_feedback_to_unimem")
            suggestions.append("   - 检查optimize_and_regenerate")
        
        if event_count < memory_count:
            suggestions.append("2. 确保每个有decision_trace的Memory都有对应的DecisionEvent")
            suggestions.append("   - 检查core.py中retain方法的DecisionEvent创建逻辑")
            suggestions.append("   - 确保decision_trace不为空时才创建DecisionEvent")
        
        if relation_count == 0:
            suggestions.append("3. 建立Memory之间的关系")
            suggestions.append("   - 反馈记忆应该RELATED_TO脚本记忆")
            suggestions.append("   - 优化脚本应该RELATED_TO原始脚本")
            suggestions.append("   - REFLECT经验应该RELATED_TO相关脚本和反馈")
        
        if suggestions:
            for suggestion in suggestions:
                print(f"  {suggestion}")
        else:
            print("  ✓ 当前状态良好，无需改进")
        
        # 生成分析报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": {
                "total_memories": memory_count,
                "total_decision_events": event_count,
                "decision_trace_coverage": coverage,
                "reasoning_coverage": reasoning_coverage,
                "relation_count": relation_count
            },
            "issues": issues,
            "suggestions": suggestions
        }
        
        report_path = Path(__file__).parent / f"memory_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n分析报告已保存到: {report_path}")
        
    except Exception as e:
        logger.error(f"分析失败: {e}", exc_info=True)
        print(f"❌ 分析失败: {e}")


if __name__ == "__main__":
    analyze_memory_storage()
