"""
运行多个测试流程，收集记忆数据，并分析公共模式
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

***REMOVED*** 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from unimem.examples.generate_video_script import VideoScriptGenerator
from unimem.memory_types import Context

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiTestTracker:
    """跟踪多个测试流程"""
    
    def __init__(self):
        self.all_tests = []
        self.all_memory_operations = []
        self.all_memory_ids = []
    
    def add_test(self, test_name: str, doc_path: str, results: Dict[str, Any]):
        """添加一个测试结果"""
        self.all_tests.append({
            "test_name": test_name,
            "doc_path": doc_path,
            "timestamp": datetime.now().isoformat(),
            "results": results
        })
        if "memory_ids" in results:
            self.all_memory_ids.extend(results["memory_ids"])
        if "memory_operations" in results:
            self.all_memory_operations.extend(results["memory_operations"])
    
    def save_report(self, output_path: str):
        """保存完整报告"""
        report = {
            "summary": {
                "total_tests": len(self.all_tests),
                "total_memory_ids": len(set(self.all_memory_ids)),
                "total_memory_operations": len(self.all_memory_operations),
                "test_timestamp": datetime.now().isoformat()
            },
            "tests": self.all_tests,
            "all_memory_operations": self.all_memory_operations,
            "all_memory_ids": list(set(self.all_memory_ids))
        }
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n完整测试报告已保存到: {output_path}")


def run_single_test(generator: VideoScriptGenerator, doc_path: str, test_name: str, 
                   feedbacks: List[Dict[str, str]]) -> Dict[str, Any]:
    """运行单个测试流程"""
    
    print(f"\n{'='*70}")
    print(f"测试: {test_name}")
    print(f"文档: {doc_path}")
    print(f"{'='*70}\n")
    
    results = {
        "test_name": test_name,
        "doc_path": doc_path,
        "memory_ids": [],
        "memory_operations": [],
        "feedbacks": [],
        "optimizations": []
    }
    
    try:
        ***REMOVED*** 1. 解析文档
        print("1. 解析需求文档...")
        doc_data = generator.parse_word_document(doc_path)
        results["doc_data"] = {
            "video_type": doc_data.get("video_type"),
            "platform": doc_data.get("platform"),
            "duration": doc_data.get("duration_seconds")
        }
        results["memory_operations"].append({
            "operation": "PARSE",
            "timestamp": datetime.now().isoformat(),
            "details": {"doc_path": doc_path}
        })
        
        ***REMOVED*** 2. 生成初始剧本
        print("2. 生成初始剧本...")
        script = generator.generate_script(doc_data)
        if not script:
            print("  ✗ 剧本生成失败")
            return results
        
        script_memory_id = script.get("unimem_memory_id")
        if script_memory_id:
            results["memory_ids"].append(script_memory_id)
            results["memory_operations"].append({
                "operation": "RETAIN_SCRIPT",
                "timestamp": datetime.now().isoformat(),
                "details": {"memory_id": script_memory_id, "round": 0}
            })
        
        print(f"  ✓ 剧本已生成，memory_id: {script_memory_id}")
        
        ***REMOVED*** 3. 多轮反馈优化
        accumulated_modifications = []
        current_script = script
        
        for i, feedback_info in enumerate(feedbacks, 1):
            round_num = i
            feedback = feedback_info.get("feedback", "")
            
            print(f"\n3.{round_num} 第 {round_num} 轮反馈优化...")
            print(f"   反馈: {feedback[:60]}...")
            
            ***REMOVED*** 提取修改需求
            modifications = generator.extract_modification_feedback(
                feedback,
                existing_modifications=accumulated_modifications
            )
            
            if modifications:
                accumulated_modifications.extend(modifications)
                results["feedbacks"].append({
                    "round": round_num,
                    "feedback": feedback,
                    "modifications": modifications
                })
            
            ***REMOVED*** 存储反馈
            feedback_memory_id = generator.store_feedback_to_unimem(
                feedback=feedback,
                script_memory_id=script_memory_id
            )
            if feedback_memory_id:
                results["memory_ids"].append(feedback_memory_id)
                results["memory_operations"].append({
                    "operation": "RETAIN_FEEDBACK",
                    "timestamp": datetime.now().isoformat(),
                    "details": {"memory_id": feedback_memory_id, "round": round_num}
                })
            
            ***REMOVED*** 优化剧本
            optimized_script = generator.optimize_and_regenerate(
                original_doc_data=doc_data,
                modification_feedback=modifications,
                original_script=current_script,
                accumulated_modifications=accumulated_modifications
            )
            
            if optimized_script:
                new_memory_id = optimized_script.get("unimem_memory_id")
                if new_memory_id and new_memory_id != script_memory_id:
                    results["memory_ids"].append(new_memory_id)
                    results["memory_operations"].append({
                        "operation": "RETAIN_SCRIPT",
                        "timestamp": datetime.now().isoformat(),
                        "details": {"memory_id": new_memory_id, "round": round_num, "is_update": True}
                    })
                    script_memory_id = new_memory_id
                
                results["optimizations"].append({
                    "round": round_num,
                    "segments_count": len(optimized_script.get("segments", [])),
                    "memory_id": new_memory_id
                })
                current_script = optimized_script
                print(f"  ✓ 优化完成")
        
        ***REMOVED*** 4. REFLECT 操作
        if results["memory_ids"]:
            print(f"\n4. 执行 REFLECT 操作...")
            evolved_ids = generator.reflect_on_script_creation(
                script_memory_ids=results["memory_ids"],
                video_type=doc_data.get("video_type", "ecommerce"),
                platform=doc_data.get("platform", "douyin"),
                iteration_count=len(feedbacks)
            )
            
            if evolved_ids:
                results["memory_operations"].append({
                    "operation": "REFLECT_SUCCESS",
                    "timestamp": datetime.now().isoformat(),
                    "details": {"evolved_memory_ids": evolved_ids}
                })
                print(f"  ✓ REFLECT 完成，优化了 {len(evolved_ids)} 条记忆")
            else:
                results["memory_operations"].append({
                    "operation": "REFLECT_FAILED",
                    "timestamp": datetime.now().isoformat(),
                    "details": {"reason": "No memories evolved"}
                })
                print(f"  ⚠ REFLECT 未产生结果")
        
        print(f"\n✓ 测试完成: {test_name}")
        
    except Exception as e:
        print(f"  ✗ 测试失败: {e}")
        results["error"] = str(e)
        import traceback
        traceback.print_exc()
    
    return results


def analyze_common_patterns(tracker: MultiTestTracker) -> Dict[str, Any]:
    """分析所有测试中的公共模式"""
    
    print("\n" + "="*70)
    print("分析公共模式和长期记忆")
    print("="*70)
    
    analysis = {
        "video_types": {},
        "platforms": {},
        "common_modifications": [],
        "common_preferences": [],
        "optimization_patterns": {}
    }
    
    ***REMOVED*** 统计视频类型和平台
    for test in tracker.all_tests:
        doc_data = test.get("results", {}).get("doc_data", {})
        video_type = doc_data.get("video_type", "unknown")
        platform = doc_data.get("platform", "unknown")
        
        analysis["video_types"][video_type] = analysis["video_types"].get(video_type, 0) + 1
        analysis["platforms"][platform] = analysis["platforms"].get(platform, 0) + 1
    
    ***REMOVED*** 收集所有修改需求
    all_modifications = []
    for test in tracker.all_tests:
        for feedback in test.get("results", {}).get("feedbacks", []):
            all_modifications.extend(feedback.get("modifications", []))
    
    ***REMOVED*** 统计常见修改需求
    modification_counts = {}
    for mod in all_modifications:
        modification_counts[mod] = modification_counts.get(mod, 0) + 1
    
    ***REMOVED*** 找出出现频率高的修改需求（公共模式）
    common_modifications = [
        mod for mod, count in modification_counts.items() 
        if count >= 2  ***REMOVED*** 至少出现2次
    ]
    analysis["common_modifications"] = sorted(
        common_modifications,
        key=lambda x: modification_counts[x],
        reverse=True
    )
    analysis["modification_counts"] = modification_counts  ***REMOVED*** 保存计数供后续使用
    
    ***REMOVED*** 分析优化模式
    total_optimizations = sum(
        len(test.get("results", {}).get("optimizations", []))
        for test in tracker.all_tests
    )
    analysis["optimization_patterns"] = {
        "total_optimization_rounds": total_optimizations,
        "average_rounds_per_test": total_optimizations / len(tracker.all_tests) if tracker.all_tests else 0
    }
    
    return analysis


def main():
    """主函数：运行多个测试流程"""
    
    print("="*70)
    print("多流程测试：生成剧本、优化、记忆验证")
    print("="*70)
    
    ***REMOVED*** 初始化生成器（使用 HTTP 服务）
    use_service = os.getenv("USE_UNIMEM_SERVICE", "false").lower() == "true"
    service_url = os.getenv("UNIMEM_SERVICE_URL", "http://localhost:9622")
    
    try:
        generator = VideoScriptGenerator(use_service=use_service, service_url=service_url)
        print(f"\n✓ UniMem 初始化成功（模式: {'HTTP服务' if use_service else '本地实例'}）")
    except Exception as e:
        print(f"⚠ UniMem 初始化失败: {e}")
        print("⚠ 使用独立模式（记忆功能受限）")
        generator = VideoScriptGenerator(skip_unimem=True)
    
    tracker = MultiTestTracker()
    
    ***REMOVED*** 定义测试文档和反馈
    test_configs = [
        {
            "name": "测试1-电商-手机-抖音",
            "doc": "video_script_filled_example.docx",  ***REMOVED*** 使用已有的文档
            "feedbacks": [
                {"feedback": "开场不够吸引人，需要更有冲击力的开场。另外中间部分节奏有点慢，需要加快一些。"},
                {"feedback": "结尾的转化引导太生硬了，希望更自然一些，像朋友推荐一样。"},
                {"feedback": "整体感觉不错，但是可以加一些情感共鸣的元素，让观众更有代入感。"}
            ]
        },
        {
            "name": "测试2-电商-美妆-小红书",
            "doc": "video_script_test2_ecommerce_lipstick_xiaohongshu.docx",
            "feedbacks": [
                {"feedback": "试色部分可以更详细，展示不同光线下的效果。"},
                {"feedback": "持久度测试可以更直观，用时间轴展示。"},
                {"feedback": "整体风格很好，但可以增加一些使用技巧分享。"}
            ]
        },
        {
            "name": "测试3-教育-Python-抖音",
            "doc": "video_script_test3_education_python_douyin.docx",
            "feedbacks": [
                {"feedback": "代码演示可以更清晰，增加注释说明。"},
                {"feedback": "实例可以更贴近实际应用场景。"},
                {"feedback": "讲解节奏可以稍微放慢，让初学者更容易跟上。"}
            ]
        },
        {
            "name": "测试4-娱乐-搞笑-抖音",
            "doc": "video_script_test4_entertainment_funny_douyin.docx",
            "feedbacks": [
                {"feedback": "开头可以更有悬念，吸引观众继续看下去。"},
                {"feedback": "笑点可以更突出，增加一些音效或特效。"},
                {"feedback": "整体很好，但结尾可以更有记忆点。"}
            ]
        },
        {
            "name": "测试5-电商-服装-淘宝",
            "doc": "video_script_test5_ecommerce_dress_taobao.docx",
            "feedbacks": [
                {"feedback": "面料细节展示可以更清晰，突出质感。"},
                {"feedback": "上身效果可以展示更多角度和场景。"},
                {"feedback": "整体不错，但可以增加一些搭配建议。"}
            ]
        }
    ]
    
    ***REMOVED*** 运行所有测试
    for config in test_configs:
        doc_path = config["doc"]
        if not os.path.exists(doc_path):
            print(f"\n⚠ 跳过测试 {config['name']}：文档不存在 {doc_path}")
            continue
        
        results = run_single_test(
            generator=generator,
            doc_path=doc_path,
            test_name=config["name"],
            feedbacks=config["feedbacks"]
        )
        
        tracker.add_test(config["name"], doc_path, results)
    
    ***REMOVED*** 分析公共模式
    analysis = analyze_common_patterns(tracker)
    
    ***REMOVED*** 保存报告
    report_path = "multi_test_workflow_report.json"
    tracker.save_report(report_path)
    
    ***REMOVED*** 打印分析结果
    print("\n" + "="*70)
    print("公共模式分析结果")
    print("="*70)
    
    print(f"\n【测试统计】")
    print(f"  总测试数: {analysis['optimization_patterns']['total_optimization_rounds']}")
    print(f"  平均优化轮次: {analysis['optimization_patterns']['average_rounds_per_test']:.1f}")
    
    print(f"\n【视频类型分布】")
    for vtype, count in analysis["video_types"].items():
        print(f"  {vtype}: {count} 次")
    
    print(f"\n【平台分布】")
    for platform, count in analysis["platforms"].items():
        print(f"  {platform}: {count} 次")
    
    print(f"\n【常见修改需求（公共模式）】")
    if analysis["common_modifications"]:
        modification_counts = analysis.get("modification_counts", {})
        for mod in analysis["common_modifications"][:10]:  ***REMOVED*** 显示前10个
            count = modification_counts.get(mod, 0)
            print(f"  - {mod} (出现 {count} 次)")
    else:
        print("  暂无明显的公共模式（需要更多测试数据）")
    
    print("\n" + "="*70)
    print("多流程测试完成！")
    print("="*70)
    
    ***REMOVED*** 提出改进方向
    print("\n【改进方向建议】")
    if analysis["common_modifications"]:
        print("  1. 提取公共的长期记忆：")
        print("     - 将常见修改需求总结为通用创作原则")
        print("     - 建立视频类型和平台的最佳实践库")
        print("     - 创建可复用的优化模板")
    
    print("  2. 创新思路：")
    print("     - 基于历史记忆自动预测用户可能的修改需求")
    print("     - 根据视频类型和平台自动应用最佳实践")
    print("     - 建立跨项目的记忆共享机制")
    print("     - 实现记忆的自动分类和标签化")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
