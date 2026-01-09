"""
小说情节分析和章节大纲创作示例

使用滑动窗口读取小说，通过 AtomLinkAdapter 进行情节分析，
并生成章节大纲。
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Set
from pathlib import Path

***REMOVED*** 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem import UniMem, Experience, Context
from unimem.adapters.atom_link_adapter import AtomLinkAdapter
from unimem.memory_types import Memory, Entity

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NovelAnalyzer:
    """小说分析器"""
    
    def __init__(self, window_size: int = 512, overlap: int = 64):
        """
        初始化小说分析器
        
        Args:
            window_size: 滑动窗口大小（字符数）
            overlap: 窗口重叠大小（字符数）
        """
        self.window_size = window_size
        self.overlap = overlap
        
        ***REMOVED*** 初始化 UniMem 和 AtomLinkAdapter
        config = {
            "graph": {
                "backend": "networkx",  ***REMOVED*** 使用轻量级 networkx，不需要 Neo4j
            },
            "vector": {
                "backend": "qdrant",  ***REMOVED*** 使用 Qdrant 作为向量数据库
            },
            "network": {
                "local_model_path": "/root/data/AI/pretrain/multilingual-e5-small",
                "qdrant_host": "localhost",
                "qdrant_port": 6333,
                "collection_name": "novel_analysis",
            }
        }
        
        ***REMOVED*** 传递后端参数，避免配置验证错误
        self.memory = UniMem(
            config=config,
            storage_backend="redis",  ***REMOVED*** 默认存储后端
            graph_backend="networkx",  ***REMOVED*** 使用轻量级 networkx
            vector_backend="qdrant",  ***REMOVED*** 使用 Qdrant
        )
        ***REMOVED*** 直接访问 network_adapter（即 AtomLinkAdapter）
        self.adapter = self.memory.network_adapter
        
        logger.info(f"小说分析器初始化完成（窗口大小: {window_size}, 重叠: {overlap}）")
    
    def read_novel_with_sliding_window(self, file_path: str) -> List[str]:
        """
        使用滑动窗口读取小说
        
        Args:
            file_path: 小说文件路径
            
        Returns:
            文本片段列表
        """
        logger.info(f"开始读取小说: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        total_chars = len(content)
        logger.info(f"小说总字符数: {total_chars}")
        
        ***REMOVED*** 滑动窗口切分
        segments = []
        start = 0
        
        while start < total_chars:
            end = min(start + self.window_size, total_chars)
            segment = content[start:end]
            segments.append(segment)
            
            ***REMOVED*** 移动到下一个窗口（考虑重叠）
            start += self.window_size - self.overlap
            
            if len(segments) % 10 == 0:
                logger.info(f"已处理 {len(segments)} 个片段...")
        
        logger.info(f"共切分为 {len(segments)} 个片段")
        return segments
    
    def analyze_segment(self, segment: str, segment_id: int, context: Context) -> Memory:
        """
        分析单个文本片段，构建结构化原子笔记
        
        Args:
            segment: 文本片段
            segment_id: 片段编号
            context: 上下文信息
            
        Returns:
            分析后的记忆对象
        """
        ***REMOVED*** 使用 AtomLinkAdapter 构建原子笔记
        ***REMOVED*** 这会自动使用 LLM 分析内容，提取 keywords, context, tags
        ***REMOVED*** 并生成结构化的 Memory 对象
        timestamp = datetime.now()
        
        ***REMOVED*** 提取实体（这里可以后续扩展，从片段中提取角色、地点等实体）
        entities = []  ***REMOVED*** 暂时为空，后续可以添加实体提取逻辑
        
        ***REMOVED*** 使用 construct_atomic_note 构建原子笔记
        ***REMOVED*** 这会调用 LLM 分析内容，生成结构化的摘要和元数据
        ***REMOVED*** generate_summary=True 表示生成摘要性内容，而不是直接使用原始片段
        memory = self.adapter.construct_atomic_note(
            content=segment,
            timestamp=timestamp,
            entities=entities,
            generate_summary=True  ***REMOVED*** 生成摘要，而不是直接使用原始文本
        )
        
        ***REMOVED*** 添加片段相关的元数据
        memory.metadata = memory.metadata or {}
        memory.metadata.update({
            "segment_id": segment_id,
            "window_size": self.window_size,
            "overlap": self.overlap,
        })
        
        ***REMOVED*** 添加到向量存储
        if hasattr(self.adapter, 'add_memory_to_vector_store'):
            try:
                self.adapter.add_memory_to_vector_store(memory)
            except Exception as e:
                logger.warning(f"添加记忆到向量存储失败: {e}")
        
        logger.debug(f"片段 {segment_id} 分析完成: {memory.id[:8]}... (关键词: {len(memory.keywords)}, 标签: {len(memory.tags)})")
        return memory
    
    def analyze_novel(self, file_path: str) -> List[Memory]:
        """
        分析整部小说
        
        Args:
            file_path: 小说文件路径
            
        Returns:
            所有片段的记忆列表
        """
        logger.info("=" * 60)
        logger.info("开始分析小说")
        logger.info("=" * 60)
        
        ***REMOVED*** 读取小说片段
        segments = self.read_novel_with_sliding_window(file_path)
        
        ***REMOVED*** 创建上下文
        context = Context(
            session_id=f"novel_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            user_id="novel_analyzer",
            metadata={
                "novel_file": file_path,
                "total_segments": len(segments),
            }
        )
        
        ***REMOVED*** 分析每个片段
        memories = []
        for i, segment in enumerate(segments, 1):
            try:
                memory = self.analyze_segment(segment, i, context)
                memories.append(memory)
                
                ***REMOVED*** 每处理 10 个片段，生成一次链接
                if i % 10 == 0:
                    logger.info(f"处理片段 {i}/{len(segments)}，生成链接...")
                    links = self.adapter.generate_links(memory, top_k=5)
                    if links:
                        memory.links.update(links)
                        self.adapter.update_memory_in_vector_store(memory)
                
            except Exception as e:
                logger.error(f"分析片段 {i} 时出错: {e}")
                continue
        
        logger.info(f"小说分析完成，共生成 {len(memories)} 个记忆片段")
        return memories
    
    def extract_plot_points(self, memories: List[Memory], top_k: int = 20) -> List[Dict[str, Any]]:
        """
        提取关键情节点
        
        Args:
            memories: 记忆列表
            top_k: 返回前 k 个关键情节
            
        Returns:
            关键情节点列表
        """
        logger.info("提取关键情节点...")
        
        ***REMOVED*** 使用语义检索找到最重要的情节
        plot_points = []
        
        ***REMOVED*** 查询关键词
        queries = [
            "主要角色",
            "重要事件",
            "冲突和矛盾",
            "情感关系",
            "武功招式",
            "门派斗争",
        ]
        
        for query in queries:
            results = self.adapter.semantic_retrieval(query, top_k=3)
            for result in results:
                plot_points.append({
                    "query": query,
                    "memory": result,
                    "content": result.content[:100] + "...",
                    "keywords": result.keywords,
                    "tags": result.tags,
                    "context": result.context,
                })
        
        ***REMOVED*** 去重
        seen_ids = set()
        unique_points = []
        for point in plot_points:
            if point["memory"].id not in seen_ids:
                unique_points.append(point)
                seen_ids.add(point["memory"].id)
        
        logger.info(f"提取了 {len(unique_points)} 个关键情节点")
        return unique_points[:top_k]
    
    def generate_chapter_outline(self, memories: List[Memory], num_chapters: int = 10) -> List[Dict[str, Any]]:
        """
        生成章节大纲
        
        Args:
            memories: 记忆列表
            num_chapters: 章节数量
            
        Returns:
            章节大纲列表
        """
        logger.info(f"生成 {num_chapters} 章大纲...")
        
        ***REMOVED*** 将记忆按时间顺序分组到不同章节
        segments_per_chapter = len(memories) // num_chapters
        
        chapters = []
        for i in range(num_chapters):
            start_idx = i * segments_per_chapter
            end_idx = (i + 1) * segments_per_chapter if i < num_chapters - 1 else len(memories)
            
            chapter_memories = memories[start_idx:end_idx]
            
            ***REMOVED*** 提取章节关键词和主题
            chapter_keywords = set()
            chapter_tags = set()
            chapter_contexts = []
            
            for mem in chapter_memories:
                chapter_keywords.update(mem.keywords)
                chapter_tags.update(mem.tags)
                if mem.context and mem.context != "General":
                    chapter_contexts.append(mem.context)
            
            ***REMOVED*** 使用语义检索找到章节核心内容
            if chapter_memories:
                ***REMOVED*** 使用章节中间的记忆作为查询
                query_memory = chapter_memories[len(chapter_memories) // 2]
                related = self.adapter.semantic_retrieval(query_memory.content[:200], top_k=5)
                
                chapters.append({
                    "chapter_num": i + 1,
                    "segment_range": (start_idx + 1, end_idx),
                    "memories_count": len(chapter_memories),
                    "keywords": list(chapter_keywords)[:10],
                    "tags": list(chapter_tags)[:5],
                    "main_context": chapter_contexts[0] if chapter_contexts else "未分类",
                    "key_content": [mem.content[:100] + "..." for mem in related[:3]],
                })
        
        logger.info(f"生成了 {len(chapters)} 章大纲")
        return chapters
    
    def visualize_links(self, memories: List[Memory], output_file: str = None) -> Dict[str, Any]:
        """
        可视化或保存笔记之间的链接关系
        
        Args:
            memories: 记忆列表
            output_file: 输出文件路径（可选，支持 .json, .txt, .dot 格式）
            
        Returns:
            链接关系字典
        """
        logger.info("构建链接关系图...")
        
        ***REMOVED*** 构建链接关系
        links_data = {
            "nodes": [],
            "edges": [],
            "statistics": {
                "total_memories": len(memories),
                "memories_with_links": 0,
                "total_links": 0,
            }
        }
        
        ***REMOVED*** 创建节点
        memory_map = {mem.id: mem for mem in memories}
        for mem in memories:
            node = {
                "id": mem.id,
                "content_preview": mem.content[:100] + "..." if len(mem.content) > 100 else mem.content,
                "keywords": mem.keywords[:5],
                "tags": mem.tags[:3],
                "context": mem.context,
                "link_count": len(mem.links),
            }
            links_data["nodes"].append(node)
            
            ***REMOVED*** 创建边（链接）
            if mem.links:
                links_data["statistics"]["memories_with_links"] += 1
                for linked_id in mem.links:
                    if linked_id in memory_map:  ***REMOVED*** 确保链接的记忆存在
                        edge = {
                            "source": mem.id,
                            "target": linked_id,
                            "source_preview": mem.content[:50],
                            "target_preview": memory_map[linked_id].content[:50],
                        }
                        links_data["edges"].append(edge)
                        links_data["statistics"]["total_links"] += 1
        
        ***REMOVED*** 保存到文件
        if output_file:
            output_path = Path(output_file)
            suffix = output_path.suffix.lower()
            
            if suffix == '.json':
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(links_data, f, ensure_ascii=False, indent=2)
                logger.info(f"链接关系已保存到 JSON 文件: {output_file}")
            
            elif suffix == '.txt':
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write("记忆链接关系图\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(f"统计信息:\n")
                    f.write(f"  总记忆数: {links_data['statistics']['total_memories']}\n")
                    f.write(f"  有链接的记忆数: {links_data['statistics']['memories_with_links']}\n")
                    f.write(f"  总链接数: {links_data['statistics']['total_links']}\n\n")
                    f.write("=" * 80 + "\n")
                    f.write("链接关系:\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for edge in links_data["edges"]:
                        source_node = next((n for n in links_data["nodes"] if n["id"] == edge["source"]), None)
                        target_node = next((n for n in links_data["nodes"] if n["id"] == edge["target"]), None)
                        if source_node and target_node:
                            f.write(f"记忆 {edge['source'][:8]}... -> 记忆 {edge['target'][:8]}...\n")
                            f.write(f"  源: {source_node['content_preview']}\n")
                            f.write(f"  目标: {target_node['content_preview']}\n")
                            f.write(f"  关键词: {', '.join(source_node['keywords'][:3])} -> {', '.join(target_node['keywords'][:3])}\n")
                            f.write("\n")
                
                logger.info(f"链接关系已保存到文本文件: {output_file}")
            
            elif suffix == '.dot':
                ***REMOVED*** Graphviz DOT 格式
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write("digraph MemoryLinks {\n")
                    f.write("  rankdir=LR;\n")
                    f.write("  node [shape=box, style=rounded];\n\n")
                    
                    ***REMOVED*** 添加节点
                    for node in links_data["nodes"]:
                        label = node["content_preview"].replace('"', "'").replace('\n', ' ')
                        if len(label) > 50:
                            label = label[:50] + "..."
                        f.write(f'  "{node["id"][:8]}" [label="{label}"];\n')
                    
                    f.write("\n")
                    
                    ***REMOVED*** 添加边
                    for edge in links_data["edges"]:
                        f.write(f'  "{edge["source"][:8]}" -> "{edge["target"][:8]}";\n')
                    
                    f.write("}\n")
                
                logger.info(f"链接关系已保存到 Graphviz DOT 文件: {output_file}")
                logger.info(f"可以使用以下命令生成图片: dot -Tpng {output_file} -o {output_file.replace('.dot', '.png')}")
        
        return links_data
    
    def print_analysis_report(self, memories: List[Memory], plot_points: List[Dict], chapters: List[Dict]):
        """打印分析报告"""
        print("\n" + "=" * 80)
        print("小说情节分析报告")
        print("=" * 80)
        
        print(f"\n【统计信息】")
        print(f"  总片段数: {len(memories)}")
        print(f"  关键情节点: {len(plot_points)}")
        print(f"  章节数: {len(chapters)}")
        
        print(f"\n【关键情节点】（前 10 个）")
        for i, point in enumerate(plot_points[:10], 1):
            print(f"\n  {i}. 查询: {point['query']}")
            print(f"     关键词: {', '.join(point['keywords'][:5])}")
            print(f"     标签: {', '.join(point['tags'][:3])}")
            print(f"     内容摘要: {point['content']}")
        
        print(f"\n【章节大纲】")
        for chapter in chapters:
            print(f"\n  第 {chapter['chapter_num']} 章")
            print(f"    片段范围: {chapter['segment_range'][0]}-{chapter['segment_range'][1]}")
            print(f"    主要关键词: {', '.join(chapter['keywords'][:5])}")
            print(f"    主题: {chapter['main_context']}")
            print(f"    关键内容:")
            for j, content in enumerate(chapter['key_content'], 1):
                print(f"      {j}. {content}")
        
        print("\n" + "=" * 80)


def main():
    """主函数"""
    novel_file = "/root/data/AI/creator/src/data/金庸-笑傲江湖.txt"
    
    if not os.path.exists(novel_file):
        print(f"错误: 文件不存在: {novel_file}")
        return
    
    ***REMOVED*** 创建分析器（窗口大小 500 字符，重叠 100 字符）
    analyzer = NovelAnalyzer(window_size=512, overlap=64)
    
    try:
        ***REMOVED*** 分析小说
        memories = analyzer.analyze_novel(novel_file)
        
        ***REMOVED*** 提取关键情节点
        plot_points = analyzer.extract_plot_points(memories, top_k=20)
        
        ***REMOVED*** 生成章节大纲
        chapters = analyzer.generate_chapter_outline(memories, num_chapters=10)
        
        ***REMOVED*** 打印报告
        analyzer.print_analysis_report(memories, plot_points, chapters)
        
        print("\n✅ 分析完成！")
        
    except Exception as e:
        logger.error(f"分析过程中出错: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

