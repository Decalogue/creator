"""
小说分析脚本：窗口512，重叠64，分析前10个窗口，并保存结果
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.examples.novel_analysis import NovelAnalyzer

def save_results_to_file(memories, plot_points, chapters, output_file: str):
    """保存分析结果到文件"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_segments": len(memories),
        "memories": [
            {
                "id": mem.id,
                "content": mem.content,
                "keywords": mem.keywords,
                "tags": mem.tags,
                "context": mem.context,
                "timestamp": mem.timestamp.isoformat() if mem.timestamp else None,
                "metadata": mem.metadata,
            }
            for mem in memories
        ],
        "plot_points": [
            {
                "query": point["query"],
                "content": point["content"],
                "keywords": point["keywords"],
                "tags": point["tags"],
                "context": point["context"],
            }
            for point in plot_points
        ],
        "chapters": [
            {
                "chapter_num": ch["chapter_num"],
                "segment_range": ch["segment_range"],
                "memories_count": ch["memories_count"],
                "keywords": ch["keywords"],
                "tags": ch["tags"],
                "main_context": ch["main_context"],
                "key_content": ch["key_content"],
            }
            for ch in chapters
        ],
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 结果已保存到: {output_file}")

def main():
    """分析前10个窗口并保存结果"""
    novel_file = "/root/data/AI/creator/src/data/金庸-笑傲江湖.txt"
    
    ***REMOVED*** 创建分析器：窗口512，重叠64
    analyzer = NovelAnalyzer(window_size=512, overlap=64)
    
    ***REMOVED*** 计算前30个窗口需要的字符数（增加数量以形成链接网络）
    ***REMOVED*** 窗口大小512，重叠64，每个窗口实际前进 512-64=448 字符
    ***REMOVED*** 前30个窗口需要：512 + 29 * 448 = 512 + 12992 = 13504 字符
    chars_needed = 512 + 29 * (512 - 64)
    
    print("=" * 60)
    print(f"开始分析小说（窗口512，重叠64，前30个窗口）")
    print(f"预计需要读取约 {chars_needed} 字符")
    print("=" * 60)
    
    ***REMOVED*** 读取所需字符
    with open(novel_file, 'r', encoding='utf-8') as f:
        content = f.read(chars_needed)
    
    ***REMOVED*** 创建临时测试文件
    test_file = "/root/data/AI/creator/src/data/test_novel.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"已读取 {len(content)} 字符")
    
    try:
        ***REMOVED*** 分析小说（但只处理前10个窗口）
        segments = analyzer.read_novel_with_sliding_window(test_file)
        
        ***REMOVED*** 只取前30个窗口（增加数量以形成链接网络和测试演化机制）
        segments = segments[:30]
        print(f"将处理 {len(segments)} 个窗口")
        
        ***REMOVED*** 创建上下文
        from unimem import Context
        context = Context(
            session_id=f"novel_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id="novel_analyzer",
            metadata={
                "novel_file": test_file,
                "total_segments": len(segments),
                "window_size": 512,
                "overlap": 64,
            }
        )
        
        ***REMOVED*** 分析每个片段
        memories = []
        for i, segment in enumerate(segments, 1):
            try:
                memory = analyzer.analyze_segment(segment, i, context)
                memories.append(memory)
                
                ***REMOVED*** 每处理 5 个片段，生成一次链接并进行记忆演化
                if i % 5 == 0 and i >= 10:  ***REMOVED*** 至少需要10个记忆才能进行演化
                    print(f"处理片段 {i}/{len(segments)}，生成链接并进行记忆演化...")
                    
                    ***REMOVED*** 1. 生成链接
                    links = analyzer.adapter.generate_links(memory, top_k=5)
                    if links:
                        memory.links.update(links)
                        analyzer.adapter.update_memory_in_vector_store(memory)
                        print(f"  ✅ 生成了 {len(links)} 个链接")
                    
                    ***REMOVED*** 2. 查找相关记忆并进行演化
                    related = analyzer.adapter.find_related_memories(memory, top_k=5)
                    if related:
                        ***REMOVED*** 使用当前记忆的上下文作为新上下文，或者生成一个综合上下文
                        new_context = f"与 {len(related)} 个相关记忆关联，形成记忆网络"
                        evolved_memory = analyzer.adapter.evolve_memory(memory, related, new_context)
                        if evolved_memory != memory:
                            analyzer.adapter.update_memory_in_vector_store(evolved_memory)
                            print(f"  ✅ 记忆演化完成，更新了 {len(evolved_memory.links)} 个链接")
                
                if i % 10 == 0:
                    print(f"已处理 {i}/{len(segments)} 个片段...")
                
            except Exception as e:
                print(f"分析片段 {i} 时出错: {e}")
                continue
        
        print(f"\n✅ 成功分析 {len(memories)} 个片段")
        
        ***REMOVED*** 提取关键情节点
        if len(memories) >= 3:
            plot_points = analyzer.extract_plot_points(memories, top_k=10)
            print(f"✅ 提取了 {len(plot_points)} 个关键情节点")
            
            ***REMOVED*** 生成章节大纲（15章，对应30个窗口）
            chapters = analyzer.generate_chapter_outline(memories, num_chapters=15)
            print(f"✅ 生成了 {len(chapters)} 章大纲")
            
            ***REMOVED*** 打印详细报告
            analyzer.print_analysis_report(memories, plot_points, chapters)
            
            ***REMOVED*** 保存结果到文件
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"/root/data/AI/creator/src/data/novel_analysis_results_{timestamp}.json"
            save_results_to_file(memories, plot_points, chapters, output_file)
            
            ***REMOVED*** 可视化并保存链接关系
            print("\n" + "=" * 60)
            print("生成链接关系图...")
            print("=" * 60)
            
            ***REMOVED*** 保存为 JSON
            links_json = f"/root/data/AI/creator/src/data/novel_links_{timestamp}.json"
            links_data = analyzer.visualize_links(memories, links_json)
            
            ***REMOVED*** 保存为文本
            links_txt = f"/root/data/AI/creator/src/data/novel_links_{timestamp}.txt"
            analyzer.visualize_links(memories, links_txt)
            
            ***REMOVED*** 保存为 Graphviz DOT 格式（用于可视化）
            links_dot = f"/root/data/AI/creator/src/data/novel_links_{timestamp}.dot"
            analyzer.visualize_links(memories, links_dot)
            
            ***REMOVED*** 打印链接统计
            stats = links_data["statistics"]
            print(f"\n【链接关系统计】")
            print(f"  总记忆数: {stats['total_memories']}")
            print(f"  有链接的记忆数: {stats['memories_with_links']}")
            print(f"  总链接数: {stats['total_links']}")
            print(f"  平均每个记忆的链接数: {stats['total_links'] / max(stats['memories_with_links'], 1):.2f}")
        else:
            print("⚠️  记忆片段太少，跳过情节提取和章节大纲生成")
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
