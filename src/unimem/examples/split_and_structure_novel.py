"""
拆分小说章节并结构化前5章
然后基于分析结果提出新的武侠创作 idea

功能：
1. 拆分小说章节
2. 结构化前N章（使用 AtomLinkAdapter）
3. 基于分析结果生成新的武侠创作 idea

运行前确保：
1. 已激活 myswift 环境：conda activate myswift
2. Qdrant 服务已启动（localhost:6333）
3. 小说文件存在：data/金庸-笑傲江湖.txt
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.adapters.atom_link_adapter import AtomLinkAdapter
from unimem.types import Memory, Entity
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def split_chapters(novel_file: Path) -> List[Dict[str, Any]]:
    """
    拆分章节
    
    Args:
        novel_file: 小说文件路径
        
    Returns:
        章节列表，每个章节包含 title, content, start_line
    """
    content = novel_file.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    chapters = []
    current_chapter = None
    current_content = []
    current_start_line = 0
    
    ***REMOVED*** 章节标题模式：顶格，格式为"数字+空格+标题"
    chapter_pattern = r'^([一二三四五六七八九十百千万]+|[0-9]+)\s+([^\n]+)$'
    
    for i, line in enumerate(lines):
        ***REMOVED*** 检查是否是章节标题（顶格，不缩进）
        stripped = line.strip()
        if stripped and not line.startswith('　') and not line.startswith(' ') and re.match(chapter_pattern, stripped):
            ***REMOVED*** 保存上一章
            if current_chapter:
                chapters.append({
                    'title': current_chapter,
                    'content': '\n'.join(current_content).strip(),
                    'start_line': current_start_line
                })
            ***REMOVED*** 开始新章
            current_chapter = stripped
            current_content = []
            current_start_line = i + 1
        elif current_chapter:
            ***REMOVED*** 属于当前章节的内容（保留原始格式）
            current_content.append(line)
    
    ***REMOVED*** 保存最后一章
    if current_chapter:
        chapters.append({
            'title': current_chapter,
            'content': '\n'.join(current_content).strip(),
            'start_line': current_start_line
        })
    
    return chapters


def structure_chapters(
    chapters: List[Dict[str, Any]], 
    adapter: AtomLinkAdapter, 
    num_chapters: int = 5
) -> List[Dict[str, Any]]:
    """
    结构化前N章
    
    Args:
        chapters: 章节列表
        adapter: AtomLinkAdapter 实例
        num_chapters: 要结构化的章节数量
        
    Returns:
        结构化后的章节列表
    """
    logger.info(f"开始结构化前 {num_chapters} 章...")
    
    structured_chapters = []
    
    for i, chapter in enumerate(chapters[:num_chapters], 1):
        logger.info(f"\n处理第 {i} 章: {chapter['title']}")
        logger.info(f"内容长度: {len(chapter['content'])} 字符")
        
        ***REMOVED*** 使用创作内容分析
        analysis = adapter._analyze_content(
            chapter['content'][:2000],  ***REMOVED*** 限制长度避免过长
            is_creative_content=True
        )
        
        ***REMOVED*** 构建原子笔记
        memory = adapter.construct_atomic_note(
            content=chapter['content'][:2000],
            timestamp=datetime.now(),
            entities=[],
            generate_summary=True,
            is_creative_content=True
        )
        
        ***REMOVED*** 添加到向量存储
        adapter.add_memory_to_vector_store(memory)
        
        structured_chapters.append({
            'chapter_num': i,
            'title': chapter['title'],
            'memory_id': memory.id,
            'keywords': analysis.get('keywords', []),
            'context': analysis.get('context', ''),
            'tags': analysis.get('tags', []),
            'creative_dimensions': analysis.get('creative_dimensions', {}),
            'summary': memory.content[:300]  ***REMOVED*** 摘要
        })
        
        logger.info(f"✅ 第 {i} 章结构化完成")
        logger.info(f"  关键词: {', '.join(analysis.get('keywords', [])[:5])}")
        logger.info(f"  类型: {analysis.get('creative_dimensions', {}).get('genre', 'N/A')}")
    
    return structured_chapters


def generate_creative_idea(
    structured_chapters: List[Dict[str, Any]], 
    adapter: AtomLinkAdapter
) -> Dict[str, Any]:
    """
    基于结构化结果生成新的武侠创作 idea
    
    Args:
        structured_chapters: 结构化后的章节列表
        adapter: AtomLinkAdapter 实例
        
    Returns:
        创作 idea 字典
    """
    logger.info("\n" + "="*50)
    logger.info("基于分析结果生成新的武侠创作 idea...")
    logger.info("="*50)
    
    ***REMOVED*** 提取关键信息
    genres = []
    styles = []
    characters = []
    events = []
    themes = []
    
    for ch in structured_chapters:
        dims = ch.get('creative_dimensions', {})
        if dims.get('genre'):
            genres.append(dims['genre'])
        if dims.get('writing_style'):
            styles.append(dims['writing_style'])
        if dims.get('characters'):
            characters.extend(dims['characters'])
        if dims.get('events'):
            events.extend(dims['events'])
        if ch.get('tags'):
            themes.extend(ch['tags'])
    
    ***REMOVED*** 构建 prompt
    prompt = f"""基于对《笑傲江湖》前5章的结构化分析，请创作一个全新的武侠小说 idea。

分析结果：
- 作品类型: {', '.join(set(genres))}
- 写作风格: {', '.join(set(styles))}
- 主要人物类型: {len(characters)} 个角色
- 关键事件类型: {len(events)} 个事件
        - 主题标签: {', '.join(list(set(themes))[:10])}

要求：
1. 创作一个全新的武侠故事 idea，不要重复《笑傲江湖》的情节
2. 可以借鉴其叙事风格和结构，但要有创新
3. 包含：故事背景、主要人物、核心冲突、独特设定
4. 要有吸引人的开篇情节

请以 JSON 格式返回：
{{
    "title": "作品标题",
    "genre": "作品类型",
    "background": "故事背景（时代、地点、世界观）",
    "main_characters": [
        {{"name": "角色名", "role": "角色定位", "characteristics": "性格特征"}},
        ...
    ],
    "core_conflict": "核心冲突",
    "unique_setting": "独特设定（区别于传统武侠的创新点）",
    "opening_scene": "开篇场景描述",
    "writing_style": "建议的写作风格",
    "themes": ["主题1", "主题2", ...]
}}"""
    
    try:
        messages = [
            {"role": "system", "content": "你是一个专业的武侠小说创作助手，擅长基于经典作品分析创作全新的武侠故事。请始终以有效的 JSON 格式返回结果。"},
            {"role": "user", "content": prompt}
        ]
        
        from unimem.chat import ark_deepseek_v3_2
        _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=2048)
        
        result = adapter._parse_json_response(response_text)
        
        if result:
            return result
        else:
            logger.warning("无法解析 JSON，返回文本")
            return {"raw_response": response_text}
    except Exception as e:
        logger.error(f"生成创作 idea 失败: {e}")
        return {}


def main() -> None:
    """
    主函数
    
    执行完整的流程：拆分章节 -> 结构化 -> 生成创作 idea
    """
    ***REMOVED*** 初始化适配器
    config = {
        'local_model_path': '/root/data/AI/pretrain/multilingual-e5-small',
        'qdrant_host': 'localhost',
        'qdrant_port': 6333,
        'collection_name': 'xiaoaohujiang_analysis'
    }
    
    try:
        adapter = AtomLinkAdapter(config)
        adapter.initialize()
        
        if not adapter.is_available():
            logger.error("适配器初始化失败，请检查配置和服务")
            return
    except Exception as e:
        logger.error(f"初始化适配器失败: {e}")
        return
    
    ***REMOVED*** 1. 拆分章节
    novel_file = Path(__file__).parent.parent.parent / 'data' / '金庸-笑傲江湖.txt'
    logger.info(f"读取小说文件: {novel_file}")
    
    if not novel_file.exists():
        logger.error(f"小说文件不存在: {novel_file}")
        return
    
    try:
        chapters = split_chapters(novel_file)
        logger.info(f"✅ 成功拆分 {len(chapters)} 个章节")
    except Exception as e:
        logger.error(f"拆分章节失败: {e}")
        return
    
    ***REMOVED*** 显示前10章标题
    logger.info("\n前10章标题:")
    for i, ch in enumerate(chapters[:10], 1):
        logger.info(f"  {i}. {ch['title']} (行 {ch['start_line']}, {len(ch['content'])} 字符)")
    
    ***REMOVED*** 2. 结构化前5章
    structured = structure_chapters(chapters, adapter, num_chapters=5)
    
    ***REMOVED*** 保存结构化结果
    output_file = Path(__file__).parent.parent.parent / 'data' / 'xiaoaohujiang_structured.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured, f, ensure_ascii=False, indent=2)
    logger.info(f"\n✅ 结构化结果已保存到: {output_file}")
    
    ***REMOVED*** 3. 生成新的武侠创作 idea
    creative_idea = generate_creative_idea(structured, adapter)
    
    ***REMOVED*** 保存创作 idea
    idea_file = Path(__file__).parent.parent.parent / 'data' / 'new_wuxia_idea.json'
    with open(idea_file, 'w', encoding='utf-8') as f:
        json.dump(creative_idea, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ 创作 idea 已保存到: {idea_file}")
    
    ***REMOVED*** 打印创作 idea
    logger.info("\n" + "="*50)
    logger.info("🎨 新的武侠创作 IDEA")
    logger.info("="*50)
    if isinstance(creative_idea, dict) and 'title' in creative_idea:
        logger.info(f"标题: {creative_idea.get('title')}")
        logger.info(f"类型: {creative_idea.get('genre')}")
        logger.info(f"\n故事背景:\n{creative_idea.get('background', '')}")
        logger.info(f"\n核心冲突:\n{creative_idea.get('core_conflict', '')}")
        logger.info(f"\n独特设定:\n{creative_idea.get('unique_setting', '')}")
        logger.info(f"\n主要人物:")
        for char in creative_idea.get('main_characters', [])[:3]:
            logger.info(f"  - {char.get('name')}: {char.get('role')} ({char.get('characteristics')})")
        logger.info(f"\n开篇场景:\n{creative_idea.get('opening_scene', '')[:300]}...")
    else:
        logger.info(json.dumps(creative_idea, ensure_ascii=False, indent=2))
    
    logger.info("\n✅ 所有任务完成！")


if __name__ == "__main__":
    main()

