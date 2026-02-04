"""
60集短剧剧本生成脚本

基于"换壳理论"生成60集短剧剧本
流程：创建成长线 → 换壳 → 添加调味 → 生成剧本

注意：本示例依赖已删除的 src/workflow 模块（ShellSwappingOrchestrator、SeasoningManager），
当前已禁用。若需恢复，请将换壳/调味逻辑迁至 unimem 或独立模块后再启用。
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

***REMOVED*** 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from unimem.character import CharacterGrowthArcManager
from unimem.storage.hierarchical.hierarchical_storage import HierarchicalStorage, ContentLevel
from unimem.memory_types import Memory
from unimem.adapters.script_adapter import ScriptAdapter
from unimem.chat import ark_deepseek_v3_2

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_growth_arcs(growth_arc_manager: CharacterGrowthArcManager) -> Dict[str, Any]:
    """创建主要人物的成长线"""
    logger.info("=" * 60)
    logger.info("步骤1: 创建人物成长线")
    logger.info("=" * 60)
    
    ***REMOVED*** 男主角成长线
    hero_arc = growth_arc_manager.create_growth_arc(
        character_id="hero_001",
        character_name="林辰",
        early_state="底层小人物，生活困顿，被欺负（第1-10集）",
        mid_conflict="遇到神秘机遇/卷入大事件，被迫做出选择，面临生死考验（第11-50集）",
        late_outcome="逆袭成功，掌控局面，获得真爱（第51-60集）",
        metadata={
            "script_format": "short_drama",
            "growth_pace": "fast",
            "episodes_per_stage": {
                "early": "1-10集",
                "mid": "11-50集",
                "late": "51-60集"
            },
            "role": "男主角"
        }
    )
    logger.info(f"✓ 创建男主角成长线：{hero_arc.character_name}")
    
    ***REMOVED*** 女主角成长线
    heroine_arc = growth_arc_manager.create_growth_arc(
        character_id="heroine_001",
        character_name="苏雨",
        early_state="独立坚强的女性，有自己的事业和追求（第1-10集）",
        mid_conflict="与男主角相遇，经历误会、冲突、相互了解（第11-50集）",
        late_outcome="与男主角携手，共同面对困难，收获真爱（第51-60集）",
        metadata={
            "script_format": "short_drama",
            "growth_pace": "fast",
            "episodes_per_stage": {
                "early": "1-10集",
                "mid": "11-50集",
                "late": "51-60集"
            },
            "role": "女主角"
        }
    )
    logger.info(f"✓ 创建女主角成长线：{heroine_arc.character_name}")
    
    ***REMOVED*** 反派成长线
    villain_arc = growth_arc_manager.create_growth_arc(
        character_id="villain_001",
        character_name="赵天",
        early_state="表面光鲜，实则内心阴暗，掌控一定势力（第1-10集）",
        mid_conflict="与男主角产生冲突，不断制造障碍，暴露真实面目（第11-50集）",
        late_outcome="最终失败，受到应有惩罚（第51-60集）",
        metadata={
            "script_format": "short_drama",
            "growth_pace": "fast",
            "episodes_per_stage": {
                "early": "1-10集",
                "mid": "11-50集",
                "late": "51-60集"
            },
            "role": "反派"
        }
    )
    logger.info(f"✓ 创建反派成长线：{villain_arc.character_name}")
    
    return {
        "hero": hero_arc,
        "heroine": heroine_arc,
        "villain": villain_arc
    }


def create_source_story(growth_arcs: Dict[str, Any]) -> Dict[str, Any]:
    """创建源故事（核心故事）"""
    logger.info("=" * 60)
    logger.info("步骤2: 创建源故事（核心故事）")
    logger.info("=" * 60)
    
    source_story = {
        "id": "script_60_episodes",
        "type": "script",
        "title": "逆袭之路",
        "episode_count": 60,
        "episode_length": "2-3分钟",
        "total_length": "120-180分钟",
        "conflicts": [
            "身份危机（每5-10集一个冲突）",
            "商业竞争/势力争夺（每3-5集一个冲突）",
            "情感纠葛（每2-3集一个冲突）",
            "生死考验（每10-15集一个高潮）"
        ],
        "relationships": {
            "林辰": "苏雨（恋人关系）",
            "林辰": "赵天（敌对关系）",
            "苏雨": "赵天（复杂关系）"
        },
        "emotional_progression": [
            "愤怒（第1-10集）",
            "困惑（第11-20集）",
            "成长（第21-30集）",
            "坚定（第31-40集）",
            "突破（第41-50集）",
            "胜利（第51-60集）"
        ],
        "pace": "fast",
        "metadata": {
            "genre": "urban",  ***REMOVED*** 默认都市题材
            "target_audience": "都市白领、年轻人",
            "main_characters": [
                {
                    "name": "林辰",
                    "role": "男主角",
                    "characteristics": "底层逆袭，有正义感，聪明勇敢"
                },
                {
                    "name": "苏雨",
                    "role": "女主角",
                    "characteristics": "独立坚强，聪明美丽，有自己的事业"
                },
                {
                    "name": "赵天",
                    "role": "反派",
                    "characteristics": "表面光鲜，内心阴暗，掌控势力"
                }
            ]
        }
    }
    
    logger.info(f"✓ 创建源故事：{source_story['title']}")
    logger.info(f"  集数：{source_story['episode_count']}集")
    logger.info(f"  题材：{source_story['metadata']['genre']}")
    
    return source_story


def swap_shell(
    orchestrator: Any,
    source_story: Dict[str, Any],
    target_shell: str,
    character_ids: List[str]
) -> Any:
    """换壳工作流"""
    logger.info("=" * 60)
    logger.info(f"步骤3: 换壳工作流（目标外壳：{target_shell}）")
    logger.info("=" * 60)
    
    shelled_story = orchestrator.swap_shell(
        source_story=source_story,
        target_shell=target_shell,
        character_ids=character_ids
    )
    
    logger.info(f"✓ 换壳完成")
    logger.info(f"  外壳类型：{shelled_story.shell.shell_type}")
    logger.info(f"  背景：{shelled_story.shell.background[:50]}...")
    
    return shelled_story


def add_seasonings(
    seasoning_manager: Any,
    shelled_story: Any,
    shell_type: str
) -> Any:
    """添加调味"""
    logger.info("=" * 60)
    logger.info("步骤4: 添加调味（调味七件套）")
    logger.info("=" * 60)
    default_seasonings = getattr(seasoning_manager, "DEFAULT_SEASONINGS", [])
    seasoned_story = seasoning_manager.add_seasonings(
        story=shelled_story,
        seasonings=default_seasonings,
        shell_type=shell_type,
        intensity=1.2  ***REMOVED*** 短剧提高强度
    )
    
    logger.info(f"✓ 添加调味完成")
    logger.info(f"  调味数量：{len(seasoned_story.seasonings)}")
    logger.info(f"  强度：{seasoned_story.metadata.get('intensity', 1.0)}")
    
    return seasoned_story


def generate_script_outline(
    adapter: ScriptAdapter,
    seasoned_story: Any,
    source_story: Dict[str, Any],
    shell_type: str
) -> Dict[str, Any]:
    """生成剧本大纲"""
    logger.info("=" * 60)
    logger.info("步骤5: 生成剧本大纲")
    logger.info("=" * 60)
    
    ***REMOVED*** 构建提示词
    prompt = f"""请创作一个{shell_type}题材的60集短剧故事大纲。

故事核心（"骨头"）：
{seasoned_story.enhanced_content}

要求：
1. 60集短剧，每集2-3分钟，总时长120-180分钟
2. 快节奏叙事，每集都要有冲突或反转
3. 人物成长线：
   - 第1-10集：前期状态（底层小人物，生活困顿）
   - 第11-50集：中期冲突（遇到机遇/冲突，被迫做出选择）
   - 第51-60集：后期结果（逆袭成功，掌控局面）
4. 核心冲突：身份危机、商业竞争/势力争夺、情感纠葛、生死考验
5. 调味元素：{', '.join([s.seasoning_type.value if hasattr(s, 'seasoning_type') else str(s) for s in (seasoned_story.seasonings if hasattr(seasoned_story, 'seasonings') and seasoned_story.seasonings else [])])}
6. 适合短视频平台的观看习惯，每集要有亮点

请以 JSON 格式返回结果：
{{
    "title": "短剧标题",
    "genre": "题材类型",
    "theme": "主题",
    "main_storyline": "主要故事线",
    "main_characters": [
        {{
            "name": "角色名",
            "role": "角色定位",
            "characteristics": "角色特点"
        }}
    ],
    "conflicts": ["冲突1", "冲突2", ...],
    "episode_structure": {{
        "early_stage": {{
            "episodes": "1-10集",
            "description": "前期状态描述"
        }},
        "mid_stage": {{
            "episodes": "11-50集",
            "description": "中期冲突描述"
        }},
        "late_stage": {{
            "episodes": "51-60集",
            "description": "后期结果描述"
        }}
    }},
    "seasonings": ["调味1", "调味2", ...]
}}"""
    
    try:
        messages = [
            {"role": "system", "content": "你是一个专业的短剧编剧，擅长创作快节奏、有冲突、有亮点的短剧剧本。请始终以有效的、完整的 JSON 格式返回结果。"},
            {"role": "user", "content": prompt}
        ]
        _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
        content = response_text
        
        ***REMOVED*** 尝试提取 JSON
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            outline = json.loads(json_match.group())
        else:
            ***REMOVED*** 如果提取失败，创建默认大纲
            outline = {
                "title": source_story["title"],
                "genre": shell_type,
                "theme": "逆袭成长",
                "main_storyline": "一个底层小人物通过努力和机遇，最终逆袭成功的故事",
                "main_characters": source_story["metadata"]["main_characters"],
                "conflicts": source_story["conflicts"],
                "episode_structure": {
                    "early_stage": {
                        "episodes": "1-10集",
                        "description": "前期状态：底层小人物，生活困顿"
                    },
                    "mid_stage": {
                        "episodes": "11-50集",
                        "description": "中期冲突：遇到机遇/冲突，被迫做出选择"
                    },
                    "late_stage": {
                        "episodes": "51-60集",
                        "description": "后期结果：逆袭成功，掌控局面"
                    }
                },
                "seasonings": [s.seasoning_type.value if hasattr(s, 'seasoning_type') else str(s) for s in (seasoned_story.seasonings if hasattr(seasoned_story, 'seasonings') and seasoned_story.seasonings else [])]
            }
        
        logger.info(f"✓ 生成剧本大纲：{outline.get('title', '未知')}")
        return outline
        
    except Exception as e:
        logger.error(f"生成剧本大纲失败：{e}", exc_info=True)
        ***REMOVED*** 返回默认大纲
        return {
            "title": source_story["title"],
            "genre": shell_type,
            "theme": "逆袭成长",
            "main_storyline": "一个底层小人物通过努力和机遇，最终逆袭成功的故事",
            "main_characters": source_story["metadata"]["main_characters"],
            "conflicts": source_story["conflicts"],
            "episode_structure": {
                "early_stage": {"episodes": "1-10集", "description": "前期状态"},
                "mid_stage": {"episodes": "11-50集", "description": "中期冲突"},
                "late_stage": {"episodes": "51-60集", "description": "后期结果"}
            },
            "seasonings": [s.seasoning_type.value for s in seasoned_story.seasonings]
        }


def generate_episode_outlines(
    adapter: ScriptAdapter,
    outline: Dict[str, Any],
    episode_count: int = 60,
    batch_size: int = 10
) -> List[Dict[str, Any]]:
    """生成分集大纲（分批生成）
    
    Args:
        adapter: 脚本适配器
        outline: 故事大纲
        episode_count: 总集数，默认60集
        batch_size: 每批生成的集数，默认10集（可选10或20）
    
    Returns:
        分集大纲列表
    """
    logger.info("=" * 60)
    logger.info(f"步骤6: 生成分集大纲（{episode_count}集，每批{batch_size}集）")
    logger.info("=" * 60)
    
    import re
    
    ***REMOVED*** 分批生成（每次生成batch_size集）
    all_outlines = []
    total_batches = (episode_count + batch_size - 1) // batch_size
    
    outline_text = f"""
标题：{outline.get('title', '')}
题材：{outline.get('genre', '')}
主题：{outline.get('theme', '')}
主要故事线：{outline.get('main_storyline', '')}
主要角色：{json.dumps(outline.get('main_characters', []), ensure_ascii=False)}
核心冲突：{json.dumps(outline.get('conflicts', []), ensure_ascii=False)}
阶段描述：
- 第1-10集：{outline.get('episode_structure', {}).get('early_stage', {}).get('description', '前期状态')}
- 第11-50集：{outline.get('episode_structure', {}).get('mid_stage', {}).get('description', '中期冲突')}
- 第51-60集：{outline.get('episode_structure', {}).get('late_stage', {}).get('description', '后期结果')}
"""
    
    for batch_start in range(0, episode_count, batch_size):
        batch_end = min(batch_start + batch_size, episode_count)
        batch_num = batch_start // batch_size + 1
        
        logger.info(f"生成第 {batch_start+1}-{batch_end} 集大纲（批次 {batch_num}/{total_batches}）...")
        
        ***REMOVED*** 确定阶段描述
        if batch_start + 1 <= 10:
            stage_desc = "前期状态阶段：底层小人物，生活困顿"
        elif batch_start + 1 <= 50:
            stage_desc = "中期冲突阶段：遇到机遇/冲突，被迫做出选择"
        else:
            stage_desc = "后期结果阶段：逆袭成功，掌控局面"
        
        prompt = f"""请根据以下故事大纲，生成第{batch_start+1}到第{batch_end}集的分集大纲。

故事大纲：
{outline_text}

要求：
1. 每集都要有明确的冲突或反转
2. 当前批次属于：{stage_desc}
3. 每集2-3分钟，要有亮点
4. 节奏要快，冲突要密集
5. **重要：必须生成完整的 {batch_end - batch_start} 集（第{batch_start+1}-{batch_end}集），不能缺失任何一集**

请以 JSON 格式返回，包含 episode_outlines 数组，每个元素包含：
{{
    "episode": 集数（{batch_start+1}-{batch_end}）,
    "title": "集标题",
    "summary": "集概要（100-150字）",
    "conflict": "本集冲突",
    "highlight": "本集亮点"
}}"""
        
        ***REMOVED*** 尝试生成，最多重试1次
        max_retries = 1
        batch_outlines = []
        
        for retry in range(max_retries + 1):
            try:
                messages = [
                    {"role": "system", "content": "你是一个专业的短剧编剧，擅长创作快节奏、有冲突、有亮点的短剧剧本。请始终以有效的、完整的 JSON 格式返回结果，确保JSON格式正确且完整。"},
                    {"role": "user", "content": prompt}
                ]
                _, response_text = ark_deepseek_v3_2(messages, max_new_tokens=4096)
                content = response_text
                
                ***REMOVED*** 方法1: 尝试直接提取完整的JSON对象
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        batch_outlines = result.get("episode_outlines", [])
                        if batch_outlines:
                            break
                    except json.JSONDecodeError:
                        pass
                
                ***REMOVED*** 方法2: 尝试提取episode_outlines数组
                array_match = re.search(r'"episode_outlines"\s*:\s*\[(.*?)\]', content, re.DOTALL)
                if array_match:
                    try:
                        array_text = '[' + array_match.group(1) + ']'
                        ***REMOVED*** 尝试修复常见的JSON问题
                        array_text = re.sub(r',\s*}', '}', array_text)  ***REMOVED*** 移除对象末尾的逗号
                        array_text = re.sub(r',\s*]', ']', array_text)  ***REMOVED*** 移除数组末尾的逗号
                        batch_outlines = json.loads(array_text)
                        if batch_outlines:
                            break
                    except json.JSONDecodeError:
                        pass
                
                ***REMOVED*** 方法3: 尝试找到第一个[到最后一个]之间的内容
                bracket_start = content.find('[')
                if bracket_start != -1:
                    bracket_count = 0
                    bracket_end = -1
                    for i in range(bracket_start, len(content)):
                        if content[i] == '[':
                            bracket_count += 1
                        elif content[i] == ']':
                            bracket_count -= 1
                            if bracket_count == 0:
                                bracket_end = i + 1
                                break
                    if bracket_end > bracket_start:
                        try:
                            array_text = content[bracket_start:bracket_end]
                            array_text = re.sub(r',\s*}', '}', array_text)
                            array_text = re.sub(r',\s*]', ']', array_text)
                            batch_outlines = json.loads(array_text)
                            if batch_outlines:
                                break
                        except json.JSONDecodeError:
                            pass
                
                ***REMOVED*** 如果重试次数未用完，继续重试
                if retry < max_retries:
                    logger.warning(f"批次 {batch_num} JSON解析失败，正在重试...")
                    continue
                
            except Exception as e:
                if retry < max_retries:
                    logger.warning(f"批次 {batch_num} 生成失败，正在重试：{e}")
                    continue
                else:
                    logger.error(f"批次 {batch_num} 生成失败（已重试{max_retries}次）：{e}", exc_info=True)
        
        ***REMOVED*** 如果成功解析，过滤并添加
        if batch_outlines:
            ***REMOVED*** 过滤出当前批次的集数
            batch_outlines = [ep for ep in batch_outlines if batch_start + 1 <= ep.get("episode", 0) <= batch_end]
            all_outlines.extend(batch_outlines)
            logger.info(f"✓ 批次 {batch_num} 完成：生成 {len(batch_outlines)} 集")
        else:
            ***REMOVED*** 如果所有方法都失败，使用默认数据
            logger.warning(f"批次 {batch_num} JSON解析失败，将使用默认数据")
            for i in range(batch_start + 1, batch_end + 1):
                if i <= 10:
                    stage = "前期状态"
                    conflict = "身份危机、生活困顿"
                elif i <= 50:
                    stage = "中期冲突"
                    conflict = "遇到机遇/冲突，被迫做出选择"
                else:
                    stage = "后期结果"
                    conflict = "逆袭成功，掌控局面"
                all_outlines.append({
                    "episode": i,
                    "title": f"第{i}集",
                    "summary": f"第{i}集：{stage}阶段的故事发展",
                    "conflict": conflict,
                    "highlight": f"本集亮点：{conflict}"
                })
    
    ***REMOVED*** 检查完整性并补充缺失的集
    existing_episodes = {ep.get("episode", 0) for ep in all_outlines}
    for i in range(1, episode_count + 1):
        if i not in existing_episodes:
            logger.warning(f"第{i}集缺失，将生成默认内容")
            if i <= 10:
                stage = "前期状态"
                conflict = "身份危机、生活困顿"
            elif i <= 50:
                stage = "中期冲突"
                conflict = "遇到机遇/冲突，被迫做出选择"
            else:
                stage = "后期结果"
                conflict = "逆袭成功，掌控局面"
            
            all_outlines.append({
                "episode": i,
                "title": f"第{i}集",
                "summary": f"第{i}集：{stage}阶段的故事发展",
                "conflict": conflict,
                "highlight": f"本集亮点：{conflict}"
            })
    
    ***REMOVED*** 按集数排序
    all_outlines.sort(key=lambda x: x.get("episode", 0))
    
    logger.info(f"✓ 生成分集大纲完成：{len(all_outlines)}集")
    return all_outlines


def save_script(
    outline: Dict[str, Any],
    episode_outlines: List[Dict[str, Any]],
    seasoned_story: Any,
    output_dir: str = "output"
):
    """保存剧本"""
    logger.info("=" * 60)
    logger.info("步骤7: 保存剧本")
    logger.info("=" * 60)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    ***REMOVED*** 保存完整剧本
    script_file = output_path / f"script_60_episodes_{timestamp}.json"
    script_data = {
        "title": outline.get("title", "逆袭之路"),
        "genre": outline.get("genre", "urban"),
        "episode_count": 60,
        "outline": outline,
        "episode_outlines": episode_outlines,
        "seasoned_story": {
            "content": seasoned_story.enhanced_content,
            "seasonings": [
                {
                    "type": s.seasoning_type.value,
                    "description": s.description
                }
                for s in seasoned_story.seasonings
            ]
        },
        "metadata": {
            "created_at": timestamp,
            "based_on": "换壳理论",
            "growth_arcs": {
                "hero": "林辰：底层小人物 → 遇到机遇 → 逆袭成功",
                "heroine": "苏雨：独立坚强 → 相互了解 → 收获真爱",
                "villain": "赵天：表面光鲜 → 暴露面目 → 最终失败"
            }
        }
    }
    
    with open(script_file, "w", encoding="utf-8") as f:
        json.dump(script_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✓ 剧本已保存：{script_file}")
    
    ***REMOVED*** 保存文本格式
    text_file = output_path / f"script_60_episodes_{timestamp}.txt"
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(f"《{outline.get('title', '逆袭之路')}》\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"题材：{outline.get('genre', 'urban')}\n")
        f.write(f"集数：60集\n")
        f.write(f"主题：{outline.get('theme', '逆袭成长')}\n\n")
        f.write("故事大纲：\n")
        f.write(outline.get('main_storyline', '') + "\n\n")
        f.write("分集大纲：\n")
        for ep in episode_outlines:
            f.write(f"\n第{ep['episode']}集：{ep.get('title', '')}\n")
            f.write(f"概要：{ep.get('summary', '')}\n")
            f.write(f"冲突：{ep.get('conflict', '')}\n")
            f.write(f"亮点：{ep.get('highlight', '')}\n")
    
    logger.info(f"✓ 文本格式已保存：{text_file}")
    
    return script_file, text_file


def main():
    """主函数：生成60集短剧剧本"""
    logger.info("=" * 60)
    logger.info("开始生成60集短剧剧本（基于换壳理论）")
    logger.info("=" * 60)
    logger.warning(
        "本示例依赖已删除的 workflow 模块（ShellSwappingOrchestrator、SeasoningManager），"
        "当前已禁用。若需恢复，请将换壳/调味逻辑迁至 unimem 或独立模块。"
    )
    sys.exit(0)

    ***REMOVED*** 1. 初始化组件（以下代码在 workflow 恢复前不会执行）
    growth_arc_manager = CharacterGrowthArcManager(storage_manager=None)
    hierarchical_storage = HierarchicalStorage(storage_manager=None)
    orchestrator = ShellSwappingOrchestrator(
        growth_arc_manager=growth_arc_manager,
        hierarchical_storage=hierarchical_storage
    )
    seasoning_manager = SeasoningManager(llm_func=ark_deepseek_v3_2)
    adapter = ScriptAdapter()
    
    ***REMOVED*** 2. 创建人物成长线
    growth_arcs = create_growth_arcs(growth_arc_manager)
    character_ids = ["hero_001", "heroine_001", "villain_001"]
    
    ***REMOVED*** 3. 创建源故事
    source_story = create_source_story(growth_arcs)
    
    ***REMOVED*** 4. 选择外壳类型（可以修改）
    ***REMOVED*** 可选：urban（都市）, fantasy（玄幻）, sci-fi（科幻）, historical（历史）, mystery（悬疑）
    shell_type = "urban"  ***REMOVED*** 默认都市题材，用户可修改
    
    ***REMOVED*** 5. 换壳
    shelled_story = swap_shell(
        orchestrator,
        source_story,
        shell_type,
        character_ids
    )
    
    ***REMOVED*** 6. 添加调味
    seasoned_story = add_seasonings(
        seasoning_manager,
        shelled_story,
        shell_type
    )
    
    if not seasoned_story:
        logger.error("添加调味失败，使用默认故事")
        seasoned_story = type('obj', (object,), {
            'enhanced_content': shelled_story.content if hasattr(shelled_story, 'content') else str(shelled_story),
            'seasonings': []
        })()
    
    ***REMOVED*** 7. 生成剧本大纲
    outline = generate_script_outline(
        adapter,
        seasoned_story,
        source_story,
        shell_type
    )
    
    ***REMOVED*** 8. 生成分集大纲
    episode_outlines = generate_episode_outlines(
        adapter,
        outline,
        episode_count=60
    )
    
    ***REMOVED*** 9. 保存剧本
    script_file, text_file = save_script(
        outline,
        episode_outlines,
        seasoned_story
    )
    
    logger.info("=" * 60)
    logger.info("60集短剧剧本生成完成！")
    logger.info("=" * 60)
    logger.info(f"剧本文件：{script_file}")
    logger.info(f"文本文件：{text_file}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()


