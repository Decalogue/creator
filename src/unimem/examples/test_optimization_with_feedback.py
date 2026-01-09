"""
模拟用户反馈优化剧本的测试脚本
记录记忆操作流程和结果
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem.examples.generate_video_script import VideoScriptGenerator
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class OptimizationTracker:
    """跟踪优化过程"""
    
    def __init__(self):
        self.optimization_history = []
        self.memory_operations = []
        self.feedback_rounds = []
    
    def log_operation(self, operation_type: str, details: Dict[str, Any]):
        """记录记忆操作"""
        self.memory_operations.append({
            "timestamp": datetime.now().isoformat(),
            "operation": operation_type,
            "details": details
        })
        logger.info(f"[Memory Operation] {operation_type}: {details}")
    
    def log_feedback_round(self, round_num: int, feedback: str, modifications: List[str], script_id: str = None):
        """记录反馈轮次"""
        self.feedback_rounds.append({
            "round": round_num,
            "timestamp": datetime.now().isoformat(),
            "user_feedback": feedback,
            "extracted_modifications": modifications,
            "script_memory_id": script_id
        })
    
    def save_report(self, output_path: str):
        """保存分析报告"""
        report = {
            "optimization_history": self.optimization_history,
            "memory_operations": self.memory_operations,
            "feedback_rounds": self.feedback_rounds,
            "summary": {
                "total_rounds": len(self.feedback_rounds),
                "total_memory_operations": len(self.memory_operations),
                "memory_operation_types": {}
            }
        }
        
        ***REMOVED*** 统计操作类型
        for op in self.memory_operations:
            op_type = op["operation"]
            report["summary"]["memory_operation_types"][op_type] = \
                report["summary"]["memory_operation_types"].get(op_type, 0) + 1
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n优化跟踪报告已保存到: {output_path}")


def simulate_user_feedback_optimization():
    """模拟用户反馈优化流程"""
    
    print("\n" + "="*70)
    print("模拟用户反馈优化剧本流程")
    print("="*70 + "\n")
    
    tracker = OptimizationTracker()
    
    ***REMOVED*** 初始化生成器（使用 UniMem HTTP 服务）
    ***REMOVED*** 优先使用 HTTP 服务，如果服务不可用则使用本地实例
    use_service = os.getenv("USE_UNIMEM_SERVICE", "false").lower() == "true"
    service_url = os.getenv("UNIMEM_SERVICE_URL", "http://localhost:9622")
    
    if use_service:
        print(f"使用 UniMem HTTP 服务: {service_url}")
    else:
        print("使用 UniMem 本地实例")
    
    try:
        generator = VideoScriptGenerator(use_service=use_service, service_url=service_url)
        tracker.log_operation("INIT", {
            "status": "UniMem enabled",
            "mode": "service" if use_service else "local"
        })
    except Exception as e:
        print(f"⚠ UniMem 初始化失败: {e}")
        print("⚠ 使用独立模式（记忆功能受限）")
        generator = VideoScriptGenerator(skip_unimem=True)
        tracker.log_operation("INIT", {"status": "standalone mode", "error": str(e)})
    
    ***REMOVED*** 1. 读取初始剧本
    script_file = "generated_script.json"
    if not os.path.exists(script_file):
        print(f"错误：找不到剧本文件 {script_file}")
        return
    
    print(f"1. 读取初始剧本: {script_file}")
    with open(script_file, "r", encoding="utf-8") as f:
        initial_script = json.load(f)
    
    print(f"   - 段数: {len(initial_script.get('segments', []))}")
    print(f"   - 总时长: {initial_script.get('editing_script', {}).get('total_duration', 0)}秒")
    print(f"   - 开头: {initial_script.get('summary', {}).get('hook', 'N/A')[:50]}...")
    
    ***REMOVED*** 2. 解析原始文档（用于优化）
    doc_file = "video_script_filled_example.docx"
    if not os.path.exists(doc_file):
        print(f"⚠ 找不到文档文件 {doc_file}，将使用默认配置")
        doc_data = {
            "task_memories": [],
            "modification_memories": [],
            "general_memories": [],
            "user_preferences": {},
            "product_info": {},
            "shot_materials": [],
            "video_type": "ecommerce",
            "platform": "douyin",
            "duration_seconds": 60
        }
    else:
        print(f"\n2. 解析原始文档: {doc_file}")
        doc_data = generator.parse_word_document(doc_file)
        tracker.log_operation("PARSE", {
            "document": doc_file,
            "task_memories_count": len(doc_data.get("task_memories", [])),
            "general_memories_count": len(doc_data.get("general_memories", []))
        })
    
    ***REMOVED*** 3. 模拟多轮用户反馈
    current_script = initial_script
    accumulated_modifications = doc_data.get("modification_memories", []).copy()
    script_memory_id = current_script.get("unimem_memory_id")
    
    ***REMOVED*** 如果初始剧本没有 memory_id 且有 UniMem，先存储初始剧本
    if generator.unimem and not script_memory_id:
        print("\n正在存储初始剧本到 UniMem...")
        script_memory_id = generator.adapter.store_script_to_unimem(
            script_data=current_script,
            task_memories=doc_data.get("task_memories", []),
            video_type=doc_data.get("video_type", "ecommerce"),
            platform=doc_data.get("platform", "douyin")
        )
        if script_memory_id:
            current_script["unimem_memory_id"] = script_memory_id
            tracker.log_operation("RETAIN_SCRIPT", {
                "round": 0,
                "memory_id": script_memory_id,
                "is_initial": True
            })
            print(f"  ✓ 初始剧本已存储，memory_id: {script_memory_id}")
        else:
            print("  ⚠ 初始剧本存储失败")
    
    ***REMOVED*** 定义模拟反馈
    feedbacks = [
        {
            "round": 1,
            "feedback": "开场不够吸引人，需要更有冲击力的开场。另外中间部分节奏有点慢，需要加快一些。",
            "expected_modifications": ["开场更有冲击力", "加快中间部分节奏"]
        },
        {
            "round": 2,
            "feedback": "结尾的转化引导太生硬了，希望更自然一些，像朋友推荐一样。还有夜景拍照那个部分可以更详细一点。",
            "expected_modifications": ["结尾转化引导更自然", "夜景拍照部分更详细"]
        },
        {
            "round": 3,
            "feedback": "整体感觉不错，但是可以加一些情感共鸣的元素，让观众更有代入感。",
            "expected_modifications": ["增加情感共鸣元素"]
        }
    ]
    
    print(f"\n3. 开始模拟 {len(feedbacks)} 轮用户反馈优化\n")
    
    for feedback_info in feedbacks:
        round_num = feedback_info["round"]
        feedback = feedback_info["feedback"]
        
        print("-" * 70)
        print(f"【第 {round_num} 轮反馈】")
        print(f"用户反馈: {feedback}\n")
        
        ***REMOVED*** 提取修改需求
        print("正在提取修改需求...")
        modifications = generator.extract_modification_feedback(
            feedback,
            existing_modifications=accumulated_modifications
        )
        
        tracker.log_feedback_round(round_num, feedback, modifications, script_memory_id)
        tracker.log_operation("EXTRACT_MODIFICATIONS", {
            "round": round_num,
            "input": feedback,
            "extracted": modifications,
            "accumulated_count": len(accumulated_modifications)
        })
        
        if not modifications:
            print("  ⚠ 未能提取到明确的修改需求")
            continue
        
        print(f"  提取到 {len(modifications)} 条修改需求：")
        for i, mod in enumerate(modifications, 1):
            print(f"    {i}. {mod}")
        
        ***REMOVED*** 添加到累积列表
        accumulated_modifications.extend(modifications)
        print(f"\n  累积修改需求总数: {len(accumulated_modifications)}")
        
        ***REMOVED*** 存储反馈到 UniMem（如果可用）
        if generator.unimem:
            print("\n正在存储反馈到 UniMem...")
            feedback_memory_id = generator.store_feedback_to_unimem(
                feedback=feedback,
                script_memory_id=script_memory_id
            )
            tracker.log_operation("RETAIN_FEEDBACK", {
                "round": round_num,
                "memory_id": feedback_memory_id,
                "related_script_id": script_memory_id
            })
            if feedback_memory_id:
                print(f"  ✓ 反馈已存储，memory_id: {feedback_memory_id}")
        
        ***REMOVED*** 优化并重新生成
        print("\n正在优化剧本...")
        tracker.log_operation("OPTIMIZE_START", {
            "round": round_num,
            "accumulated_modifications_count": len(accumulated_modifications)
        })
        
        optimized_script = generator.optimize_and_regenerate(
            original_doc_data=doc_data,
            modification_feedback=modifications,
            original_script=current_script,
            accumulated_modifications=accumulated_modifications
        )
        
        if not optimized_script:
            print("  ✗ 优化失败")
            ***REMOVED*** 回退修改需求
            accumulated_modifications = accumulated_modifications[:-len(modifications)]
            continue
        
        ***REMOVED*** 检查是否有新的 memory_id
        new_memory_id = optimized_script.get("unimem_memory_id")
        if new_memory_id and new_memory_id != script_memory_id:
            tracker.log_operation("RETAIN_SCRIPT", {
                "round": round_num,
                "memory_id": new_memory_id,
                "is_update": new_memory_id != script_memory_id
            })
            script_memory_id = new_memory_id
        
        ***REMOVED*** 显示优化结果
        optimized_summary = optimized_script.get("summary", {})
        print(f"\n  ✓ 优化完成")
        print(f"    开头亮点: {optimized_summary.get('hook', 'N/A')[:60]}...")
        print(f"    核心内容: {optimized_summary.get('core_content', 'N/A')[:60]}...")
        print(f"    段数: {len(optimized_script.get('segments', []))}")
        
        ***REMOVED*** 保存优化后的剧本
        output_file = f"generated_script_optimized_v{round_num}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(optimized_script, f, ensure_ascii=False, indent=2)
        print(f"    已保存到: {output_file}")
        
        ***REMOVED*** 更新当前剧本
        current_script = optimized_script
        doc_data["modification_memories"] = accumulated_modifications.copy()
        
        tracker.log_operation("OPTIMIZE_COMPLETE", {
            "round": round_num,
            "output_file": output_file,
            "segments_count": len(optimized_script.get("segments", []))
        })
        
        print()
    
    ***REMOVED*** 4. REFLECT 操作（如果可用）
    if generator.unimem and script_memory_id:
        print("\n" + "=" * 70)
        print("4. 执行 REFLECT 操作：总结创作经验")
        print("=" * 70 + "\n")
        
        script_memory_ids = [script_memory_id] if script_memory_id else []
        
        tracker.log_operation("REFLECT_START", {
            "script_memory_ids": script_memory_ids,
            "total_feedback_rounds": len(feedbacks)
        })
        
        evolved_ids = generator.reflect_on_script_creation(
            script_memory_ids=script_memory_ids,
            video_type=doc_data.get("video_type", "ecommerce"),
            platform=doc_data.get("platform", "douyin"),
            iteration_count=len(feedbacks)
        )
        
        if evolved_ids:
            tracker.log_operation("REFLECT_COMPLETE", {
                "evolved_memory_ids": evolved_ids,
                "count": len(evolved_ids)
            })
            print(f"✓ REFLECT 完成：优化了 {len(evolved_ids)} 条记忆")
        else:
            tracker.log_operation("REFLECT_FAILED", {"reason": "No memories evolved"})
            print("⚠ REFLECT 操作未产生结果")
    
    ***REMOVED*** 5. 生成分析报告
    print("\n" + "=" * 70)
    print("5. 生成优化分析报告")
    print("=" * 70 + "\n")
    
    report_file = "optimization_analysis_report.json"
    tracker.save_report(report_file)
    
    ***REMOVED*** 读取报告以打印摘要
    with open(report_file, "r", encoding="utf-8") as f:
        report = json.load(f)
    
    ***REMOVED*** 打印摘要
    print("\n【优化摘要】")
    print(f"  总反馈轮次: {len(tracker.feedback_rounds)}")
    print(f"  总记忆操作: {len(tracker.memory_operations)}")
    print(f"  操作类型分布:")
    for op_type, count in report["summary"]["memory_operation_types"].items():
        print(f"    - {op_type}: {count}")
    
    print(f"\n【记忆操作流程】")
    for i, op in enumerate(tracker.memory_operations, 1):
        print(f"  {i}. {op['operation']} - {op['timestamp']}")
        if 'details' in op:
            details = op['details']
            if 'memory_id' in details:
                print(f"     Memory ID: {details['memory_id']}")
    
    print("\n优化流程完成！")


if __name__ == "__main__":
    simulate_user_feedback_optimization()

