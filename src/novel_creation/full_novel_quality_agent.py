***REMOVED***!/usr/bin/env python3
"""
全本小说质量检查与优化 Agent

基于小说目录和各种信息，对1-100章进行完整的质量检查并生成优化结果：
1. 全本连贯性检查（跨章节）
2. 角色一致性深度检查（全本）
3. 世界观一致性检查（全本）
4. 情节逻辑完整性检查
5. 风格统一性检查
6. 生成优化建议报告
7. 自动优化问题章节（可选）
8. 生成优化后的完整小说
"""

import sys
import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime

***REMOVED*** 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent))

from novel_creation.quality_checker import QualityChecker, QualityIssue, IssueType, IssueSeverity
from novel_creation.react_novel_creator import NovelChapter
from llm.chat import kimi_k2, deepseek_v3_2

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FullNovelQualityAgent:
    """全本小说质量检查 Agent"""
    
    def __init__(self, novel_output_dir: Path, llm_client=None, strict_mode: bool = False):
        """
        初始化全本检查 Agent
        
        Args:
            novel_output_dir: 小说输出目录（包含 chapters/ 和 metadata.json）
            llm_client: LLM 客户端（可选，用于高级检查，默认使用 gemini_3_flash 更宽松）
            strict_mode: 是否使用严格模式（默认 False，使用更宽松的标准）
        """
        self.novel_output_dir = Path(novel_output_dir)
        self.chapters_dir = self.novel_output_dir / "chapters"
        self.metadata_file = self.novel_output_dir / "metadata.json"
        self.novel_plan_file = self.novel_output_dir / "novel_plan.json"
        self.semantic_mesh_file = self.novel_output_dir / "semantic_mesh" / "mesh.json"
        
        ***REMOVED*** 默认使用 gemini_3_flash（更宽松），如果用户指定则使用指定客户端
        from llm.chat import gemini_3_flash
        self.llm_client = llm_client or gemini_3_flash
        self.strict_mode = strict_mode
        
        ***REMOVED*** 为优化功能单独设置LLM客户端（使用更经济的模型）
        self.optimization_llms = [kimi_k2, deepseek_v3_2]
        self.current_optimization_llm_index = 0
        
        ***REMOVED*** 初始化实体提取器（使用和react_novel_creator.py相同的方法）
        self.entity_extractor = self._init_entity_extractor()
        
        self.quality_checker = QualityChecker(llm_client=self.llm_client, strict_mode=strict_mode)
        
        ***REMOVED*** 加载所有可用信息
        self.metadata = self._load_metadata()
        self.novel_plan = self._load_novel_plan()
        self.semantic_mesh_data = self._load_semantic_mesh()
        
        ***REMOVED*** 加载所有章节
        self.chapters = self._load_all_chapters()
        
        ***REMOVED*** 统计信息
        self.all_entities = {}  ***REMOVED*** 全本实体库
        self.character_profiles = {}  ***REMOVED*** 角色档案
        
        ***REMOVED*** 转换语义网格数据为quality_checker期望的格式
        self.semantic_mesh_entities_dict = self._convert_semantic_mesh_to_dict()
        
        logger.info(f"加载完成：{len(self.chapters)} 章")
    
    def _init_entity_extractor(self):
        """初始化实体提取器（检查时只用 kimi_k2，不需要投票）"""
        try:
            from novel_creation.enhanced_entity_extractor import EnhancedEntityExtractor
            extractor = EnhancedEntityExtractor(
                llm_client=kimi_k2,
                use_ner=False
            )
            logger.info("增强实体提取器已启用（使用 Kimi K2 模型）")
            return extractor
        except Exception as e:
            logger.warning(f"实体提取器初始化失败: {e}")
            return None
    
    def _load_metadata(self) -> Dict[str, Any]:
        """加载元数据"""
        if not self.metadata_file.exists():
            raise FileNotFoundError(f"元数据文件不存在: {self.metadata_file}")
        
        with open(self.metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_novel_plan(self) -> Dict[str, Any]:
        """加载小说大纲（novel_plan.json）"""
        if self.novel_plan_file.exists():
            try:
                with open(self.novel_plan_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载小说大纲失败: {e}")
        ***REMOVED*** 如果不存在，尝试从metadata中获取
        return self.metadata.get('plan', {})
    
    def _load_all_chapters(self) -> List[NovelChapter]:
        """加载所有章节"""
        chapters = []
        
        for i in range(1, 101):
            chapter_file = self.chapters_dir / f"chapter_{i:03d}.txt"
            meta_file = self.chapters_dir / f"chapter_{i:03d}_meta.json"
            
            if not chapter_file.exists():
                logger.warning(f"第{i}章文件不存在: {chapter_file}")
                continue
            
            ***REMOVED*** 读取章节内容
            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            ***REMOVED*** 读取元数据（如果有）
            metadata = {}
            if meta_file.exists():
                with open(meta_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
            
            chapter = NovelChapter(
                chapter_number=i,
                title=metadata.get('title', f'第{i}章'),
                content=content,
                summary=metadata.get('summary', ''),
                metadata=metadata.get('metadata', {})
            )
            chapters.append(chapter)
        
        return chapters
    
    def _load_semantic_mesh(self) -> Optional[Dict[str, Any]]:
        """加载语义网格（如果存在）"""
        ***REMOVED*** 尝试加载 semantic_mesh/mesh.json
        if self.semantic_mesh_file.exists():
            try:
                with open(self.semantic_mesh_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载语义网格失败: {e}")
        
        ***REMOVED*** 尝试加载 semantic_mesh/semantic_mesh.json（旧格式）
        mesh_file = self.novel_output_dir / "semantic_mesh" / "semantic_mesh.json"
        if mesh_file.exists():
            try:
                with open(mesh_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载语义网格失败: {e}")
        
        return None
    
    def _convert_semantic_mesh_to_dict(self) -> Dict[str, Any]:
        """将语义网格数据转换为quality_checker期望的格式
        
        quality_checker期望格式: {entity_id: {name, type, metadata, ...}}
        """
        if not self.semantic_mesh_data:
            return {}
        
        entities_dict = {}
        
        ***REMOVED*** 如果semantic_mesh_data包含entities字段
        if isinstance(self.semantic_mesh_data, dict):
            entities = self.semantic_mesh_data.get('entities', {})
            
            ***REMOVED*** 如果entities已经是字典格式（entity_id -> entity_data）
            if isinstance(entities, dict):
                for entity_id, entity_data in entities.items():
                    ***REMOVED*** 确保格式正确
                    if isinstance(entity_data, dict):
                        entities_dict[entity_id] = entity_data
                    else:
                        ***REMOVED*** 如果是其他格式，尝试转换
                        logger.warning(f"实体 {entity_id} 格式异常: {type(entity_data)}")
            ***REMOVED*** 如果entities是列表格式
            elif isinstance(entities, list):
                for entity in entities:
                    if isinstance(entity, dict):
                        entity_id = entity.get('id', entity.get('name', ''))
                        if entity_id:
                            entities_dict[entity_id] = entity
        
        return entities_dict
    
    def _parse_entities_txt(self, text: str) -> List[Tuple[str, str, str, int]]:
        """解析 entities.txt 文本格式，返回 [(name, type, description, chapter_num), ...]"""
        entities = []
        current_type = ""
        for line in text.splitlines():
            line_stripped = line.strip()
            if not line_stripped:
                continue
            if line_stripped.endswith(":"):
                current_type = line_stripped.rstrip(":").strip()
                continue
            if line_stripped.startswith("- ") and "（第" in line_stripped and "）:" in line_stripped:
                part = line_stripped[2:].strip()
                match = re.match(r"^(.+?)【关键】?（第(\d+)章）:\s*(.*)$", part)
                if not match:
                    match = re.match(r"^(.+?)（第(\d+)章）:\s*(.*)$", part)
                if match:
                    name = match.group(1).strip()
                    ch_num = int(match.group(2))
                    desc = match.group(3).strip()
                    if name:
                        type_map = {"角色": "character", "组织": "organization", "地点": "location",
                                    "物品": "item", "生物": "creature", "概念": "concept", "时间": "time"}
                        etype = type_map.get(current_type, current_type or "unknown")
                        entities.append((name, etype, desc, ch_num))
        return entities
    
    def _extract_all_entities(self):
        """提取全本所有实体，构建实体库
        
        使用和react_novel_creator.py相同的实体提取方法（kimi_k2），
        并充分利用所有可用信息（novel_plan.json, metadata.json, semantic_mesh/mesh.json等）
        """
        logger.info("提取全本实体...")
        
        ***REMOVED*** 1. 优先从语义网格加载实体（如果存在）
        if self.semantic_mesh_data:
            try:
                entities = self.semantic_mesh_data.get('entities', {})
                relations = self.semantic_mesh_data.get('relations', [])
                
                for entity_id, entity_data in entities.items():
                    name = entity_data.get('name', '')
                    entity_type = entity_data.get('type', '')
                    content = entity_data.get('content', '')
                    metadata = entity_data.get('metadata', {})
                    
                    if name:
                        ***REMOVED*** 转换实体类型
                        type_map = {
                            'character': 'character',
                            'location': 'location',
                            'setting': 'location',
                            'item': 'item',
                            'symbol': 'item',
                            'concept': 'concept',
                            'organization': 'organization',
                            'creature': 'creature',
                            'time': 'time'
                        }
                        etype = type_map.get(entity_type.lower(), 'unknown')
                        
                        ***REMOVED*** 获取首次出现章节
                        chapter_num = metadata.get('chapter', metadata.get('first_appearance', 1))
                        appearances = metadata.get('appearances', metadata.get('appearance_chapters', [chapter_num]))
                        
                        self._add_entity(name, etype, content or '', chapter_num)
                        ***REMOVED*** 更新出现章节列表
                        if name in self.all_entities:
                            self.all_entities[name]['appearances'] = appearances if isinstance(appearances, list) else [appearances]
                
                logger.info(f"从语义网格加载了 {len(entities)} 个实体")
            except Exception as e:
                logger.warning(f"从语义网格加载实体失败: {e}")
        
        ***REMOVED*** 2. 从章节实体文件加载（如果存在）
        for chapter in self.chapters:
            entities_file = self.chapters_dir / f"chapter_{chapter.chapter_number:03d}_entities.txt"
            if entities_file.exists():
                try:
                    with open(entities_file, 'r', encoding='utf-8') as f:
                        raw = f.read()
                    ***REMOVED*** 尝试 JSON
                    try:
                        data = json.loads(raw)
                        items = data.get('entities', [])
                        for entity in items:
                            name = entity.get('name', '')
                            etype = entity.get('type', '')
                            desc = entity.get('description', '')
                            if name:
                                self._add_entity(name, etype, desc, chapter.chapter_number)
                    except json.JSONDecodeError:
                        for name, etype, desc, ch_num in self._parse_entities_txt(raw):
                            self._add_entity(name, etype, desc, ch_num)
                except Exception as e:
                    logger.debug(f"读取第{chapter.chapter_number}章实体失败: {e}")
        
        ***REMOVED*** 3. 使用kimi_k2进行实体提取（对于没有实体文件的章节）
        if self.entity_extractor:
            logger.info("使用kimi_k2进行实体提取...")
            for chapter in self.chapters:
                ***REMOVED*** 如果该章节已经有实体信息，跳过
                entities_file = self.chapters_dir / f"chapter_{chapter.chapter_number:03d}_entities.txt"
                if entities_file.exists():
                    continue
                
                try:
                    ***REMOVED*** 使用实体提取器提取实体
                    if hasattr(self.entity_extractor, 'extract_entities'):
                        result = self.entity_extractor.extract_entities(
                            chapter.content,
                            chapter.chapter_number
                        )
                        
                        ***REMOVED*** 处理提取结果
                        if hasattr(result, 'entities'):
                            entities = result.entities
                        elif isinstance(result, list):
                            entities = result
                        elif isinstance(result, dict):
                            entities = result.get('entities', [])
                        else:
                            entities = []
                        
                        for entity in entities:
                            if hasattr(entity, 'name'):
                                name = entity.name
                                etype = entity.type.value if hasattr(entity.type, 'value') else str(entity.type)
                                desc = entity.content or ''
                            elif isinstance(entity, dict):
                                name = entity.get('name', '')
                                etype = entity.get('type', '')
                                desc = entity.get('description', '')
                            else:
                                continue
                            
                            if name and len(name) > 1:
                                self._add_entity(name, etype, desc, chapter.chapter_number)
                        
                        if entities:
                            logger.debug(f"第{chapter.chapter_number}章：提取到 {len(entities)} 个实体")
                except Exception as e:
                    logger.warning(f"第{chapter.chapter_number}章实体提取失败: {e}")
        
        ***REMOVED*** 4. 从 novel_plan.json 补充角色信息
        if self.novel_plan:
            overall = self.novel_plan.get("overall", {})
            characters = overall.get("characters", [])
            
            for c in characters:
                name = c.get("name", "")
                if name:
                    if name not in self.character_profiles:
                        self.character_profiles[name] = {
                            "name": name,
                            "description": c.get("description", ""),
                            "first_appearance": 1,
                            "appearances": [],
                            "characteristics": {},
                        }
                    ***REMOVED*** 更新描述（如果更详细）
                    if c.get("description") and len(c.get("description", "")) > len(self.character_profiles[name].get("description", "")):
                        self.character_profiles[name]["description"] = c.get("description", "")
        
        ***REMOVED*** 5. 从 metadata.json 补充角色信息
        if self.metadata:
            plan = self.metadata.get('plan', {})
            if plan:
                characters = plan.get('characters', [])
                for c in characters:
                    name = c.get("name", "")
                    if name:
                        if name not in self.character_profiles:
                            self.character_profiles[name] = {
                                "name": name,
                                "description": c.get("description", ""),
                                "first_appearance": 1,
                                "appearances": [],
                                "characteristics": {},
                            }
        
        logger.info(f"提取完成：{len(self.all_entities)} 个实体，{len(self.character_profiles)} 个角色")
    
    def _add_entity(self, name: str, etype: str, desc: str, chapter_number: int):
        """添加实体到 all_entities 和 character_profiles"""
        if name not in self.all_entities:
            self.all_entities[name] = {
                "type": etype,
                "description": desc,
                "first_appearance": chapter_number,
                "appearances": [],
            }
        app = self.all_entities[name]["appearances"]
        if chapter_number not in app:
            app.append(chapter_number)
        if etype == "character":
            if name not in self.character_profiles:
                self.character_profiles[name] = {
                    "name": name,
                    "description": desc,
                    "first_appearance": chapter_number,
                    "appearances": [chapter_number],
                    "characteristics": {},
                }
            else:
                app = self.character_profiles[name]["appearances"]
                if chapter_number not in app:
                    app.append(chapter_number)
    
    def run_full_check(self, auto_optimize: bool = False) -> Dict[str, Any]:
        """
        运行全本质量检查
        
        Args:
            auto_optimize: 是否自动优化问题章节
        
        Returns:
            完整的检查报告（如果 auto_optimize=True，包含优化后的章节）
        """
        logger.info("=" * 60)
        logger.info("开始全本质量检查")
        if auto_optimize:
            logger.info("模式：检查 + 自动优化")
        logger.info("=" * 60)
        
        ***REMOVED*** 提取全本实体
        self._extract_all_entities()
        
        report = {
            "check_time": datetime.now().isoformat(),
            "novel_title": self.metadata.get('title', '未知'),
            "total_chapters": len(self.chapters),
            "auto_optimize": auto_optimize,
            "checks": {},
            "chapter_quality": {}
        }
        
        ***REMOVED*** 对每章进行详细检查
        logger.info("\n[1/7] 逐章质量检查...")
        chapter_issues = {}
        for chapter in self.chapters:
            prev_chapters = [
                {"number": c.chapter_number, "content": c.content, "summary": c.summary}
                for c in self.chapters[:chapter.chapter_number - 1]
            ]
            
            ***REMOVED*** 构建完整的上下文信息（充分利用所有可用信息）
            context_info = {
                "novel_plan": self.novel_plan,
                "metadata": self.metadata,
                "semantic_mesh": self.semantic_mesh_data,
                "character_profiles": self.character_profiles,
                "all_entities": self.all_entities,
                "previous_chapters": prev_chapters
            }
            
            quality_result = self.quality_checker.check_chapter(
                chapter_content=chapter.content,
                chapter_number=chapter.chapter_number,
                previous_chapters=prev_chapters,
                novel_plan=self.novel_plan,
                semantic_mesh_entities=self.semantic_mesh_entities_dict
            )
            
            def _issue_to_dict(issue):
                d = {"description": issue.description, "location": issue.location, "suggestion": issue.suggestion, "metadata": issue.metadata or {}}
                d["type"] = issue.issue_type.value if hasattr(issue.issue_type, "value") else str(issue.issue_type)
                d["severity"] = issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity)
                return d

            chapter_issues[chapter.chapter_number] = {
                "total_issues": len(quality_result),
                "issues": [_issue_to_dict(issue) for issue in quality_result],
                "has_high_severity": any(issue.severity == IssueSeverity.HIGH for issue in quality_result)
            }
        
        report["chapter_quality"] = chapter_issues
        
        ***REMOVED*** 2. 全本连贯性检查
        logger.info("\n[2/7] 全本连贯性检查...")
        coherence_report = self._check_full_novel_coherence()
        report["checks"]["coherence"] = coherence_report
        
        ***REMOVED*** 3. 角色一致性深度检查
        logger.info("\n[3/7] 角色一致性深度检查...")
        character_report = self._check_character_consistency_full()
        report["checks"]["character_consistency"] = character_report
        
        ***REMOVED*** 4. 世界观一致性检查
        logger.info("\n[4/7] 世界观一致性检查...")
        worldview_report = self._check_worldview_consistency_full()
        report["checks"]["worldview_consistency"] = worldview_report
        
        ***REMOVED*** 5. 情节逻辑完整性检查
        logger.info("\n[5/7] 情节逻辑完整性检查...")
        plot_report = self._check_plot_integrity()
        report["checks"]["plot_integrity"] = plot_report
        
        ***REMOVED*** 6. 风格统一性检查
        logger.info("\n[6/7] 风格统一性检查...")
        style_report = self._check_style_consistency()
        report["checks"]["style_consistency"] = style_report
        
        ***REMOVED*** 7. 生成优化建议
        logger.info("\n[7/7] 生成优化建议...")
        recommendations = self._generate_recommendations(report)
        report["recommendations"] = recommendations
        
        ***REMOVED*** 计算总体评分
        report["overall_score"] = self._calculate_overall_score(report)
        
        ***REMOVED*** 如果需要自动优化
        if auto_optimize:
            logger.info("\n" + "=" * 60)
            logger.info("开始自动优化问题章节...")
            logger.info("=" * 60)
            optimization_result = self._optimize_chapters(report)
            report["optimization"] = optimization_result
        
        logger.info("\n" + "=" * 60)
        logger.info(f"全本质量检查完成！总体评分: {report['overall_score']:.2f}/1.00")
        if auto_optimize:
            logger.info(f"优化章节数: {report.get('optimization', {}).get('optimized_count', 0)}")
        logger.info("=" * 60)
        
        return report
    
    def _check_full_novel_coherence(self) -> Dict[str, Any]:
        """全本连贯性检查"""
        issues = []
        coherence_scores = []
        
        ***REMOVED*** 检查章节间的连贯性
        for i in range(len(self.chapters) - 1):
            current = self.chapters[i]
            next_chapter = self.chapters[i + 1]
            
            ***REMOVED*** 检查主要角色是否连续出现
            current_chars = set(self._extract_characters_from_text(current.content))
            next_chars = set(self._extract_characters_from_text(next_chapter.content))
            
            ***REMOVED*** 主要角色（出现频率高的）
            main_chars = {name for name, info in self.character_profiles.items() 
                         if len(info['appearances']) >= 10}
            
            ***REMOVED*** 如果主要角色在前一章出现，但下一章没有，可能是连贯性问题
            missing_main_chars = (current_chars & main_chars) - next_chars
            if missing_main_chars and i > 0:  ***REMOVED*** 排除第一章
                issues.append({
                    "type": "character_discontinuity",
                    "severity": "medium",
                    "description": f"第{current.chapter_number}章到第{next_chapter.chapter_number}章：主要角色 {', '.join(missing_main_chars)} 突然消失",
                    "chapters": [current.chapter_number, next_chapter.chapter_number]
                })
            
            ***REMOVED*** 计算连贯性得分（基于角色连续性）
            if main_chars:
                continuity_ratio = len((current_chars & main_chars) & (next_chars & main_chars)) / len(main_chars)
                coherence_scores.append(continuity_ratio)
        
        coherence_score = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 1.0
        
        return {
            "score": round(coherence_score, 2),
            "issues": issues,
            "summary": f"连贯性得分: {coherence_score:.2f}，发现 {len(issues)} 个问题"
        }
    
    def _extract_characters_from_text(self, text: str) -> List[str]:
        """从文本中提取角色名（使用kimi_k2实体提取和实体库匹配）"""
        characters = []
        
        ***REMOVED*** 1. 优先从实体库中匹配（使用已知角色列表）
        for char_name in self.character_profiles.keys():
            if char_name in text:
                characters.append(char_name)
        
        ***REMOVED*** 2. 如果实体提取器可用，使用它提取新角色
        if self.entity_extractor and len(characters) < 3:
            try:
                result = self.entity_extractor.extract_entities(text, 0)
                
                ***REMOVED*** 处理提取结果
                if hasattr(result, 'entities'):
                    entities = result.entities
                elif isinstance(result, list):
                    entities = result
                elif isinstance(result, dict):
                    entities = result.get('entities', [])
                else:
                    entities = []
                
                for entity in entities:
                    if hasattr(entity, 'name'):
                        name = entity.name
                        etype = entity.type.value if hasattr(entity.type, 'value') else str(entity.type)
                    elif isinstance(entity, dict):
                        name = entity.get('name', '')
                        etype = entity.get('type', '')
                    else:
                        continue
                    
                    ***REMOVED*** 只保留角色类型的实体
                    if etype.lower() in ['character', '角色'] and name and len(name) > 1:
                        if name not in characters:
                            characters.append(name)
            except Exception as e:
                logger.debug(f"使用实体提取器提取角色失败: {e}")
        
        return characters
    
    def _check_character_consistency_full(self) -> Dict[str, Any]:
        """角色一致性深度检查（全本）
        
        充分利用novel_plan.json、metadata.json和semantic_mesh中的角色信息
        """
        character_issues = []
        
        ***REMOVED*** 从novel_plan.json和metadata.json获取标准角色列表
        standard_characters = set()
        if self.novel_plan:
            overall = self.novel_plan.get("overall", {})
            for c in overall.get("characters", []):
                name = c.get("name", "")
                if name:
                    standard_characters.add(name)
        
        if self.metadata:
            plan = self.metadata.get('plan', {})
            for c in plan.get('characters', []):
                name = c.get("name", "")
                if name:
                    standard_characters.add(name)
        
        ***REMOVED*** 检查每个角色的出现情况
        for char_name, profile in self.character_profiles.items():
            appearances = profile.get("appearances", [])
            if len(appearances) < 2:
                continue
            
            ***REMOVED*** 检查角色名称是否在标准列表中（避免误判）
            if char_name in standard_characters:
                ***REMOVED*** 这是标准角色，进行一致性检查
                ***REMOVED*** 可扩展：检查名称变体、性格一致性等
                pass
        
        return {
            "characters_checked": len(self.character_profiles),
            "standard_characters": list(standard_characters),
            "issues": character_issues,
            "summary": f"检查了 {len(self.character_profiles)} 个角色，发现 {len(character_issues)} 个问题"
        }
    
    def _check_worldview_consistency_full(self) -> Dict[str, Any]:
        """世界观一致性检查（全本）
        
        充分利用novel_plan.json、metadata.json和semantic_mesh中的世界观信息
        """
        worldview_issues = []
        
        ***REMOVED*** 从novel_plan.json获取世界观设定
        overall_plan = self.novel_plan.get('overall', {}) if self.novel_plan else {}
        background = overall_plan.get('background', '')
        
        ***REMOVED*** 从metadata.json获取世界观设定
        if self.metadata:
            plan = self.metadata.get('plan', {})
            if plan:
                overall = plan.get('overall', {})
                if overall.get('background'):
                    background = overall.get('background', background)
        
        ***REMOVED*** 从semantic_mesh获取世界观实体
        worldview_entities = {}
        if self.semantic_mesh_data:
            entities = self.semantic_mesh_data.get('entities', {})
            for entity_id, entity_data in entities.items():
                entity_type = entity_data.get('type', '').lower()
                if entity_type in ['location', 'setting', 'concept', 'item']:
                    name = entity_data.get('name', '')
                    if name:
                        worldview_entities[name] = entity_data
        
        ***REMOVED*** 检查关键世界观元素是否在全本中保持一致
        ***REMOVED*** 这里可以扩展为更复杂的检查
        
        return {
            "background": background[:200] if background else "",
            "worldview_entities_count": len(worldview_entities),
            "issues": worldview_issues,
            "summary": f"世界观一致性检查完成，发现 {len(worldview_issues)} 个问题"
        }
    
    def _check_plot_integrity(self) -> Dict[str, Any]:
        """情节逻辑完整性检查
        
        充分利用novel_plan.json中的情节大纲和关键节点信息
        """
        plot_issues = []
        
        ***REMOVED*** 从novel_plan.json获取关键情节节点
        key_plot_points = []
        if self.novel_plan:
            overall = self.novel_plan.get('overall', {})
            key_plot_points = overall.get('key_plot_points', [])
        
        if self.metadata:
            plan = self.metadata.get('plan', {})
            if plan:
                overall = plan.get('overall', {})
                if overall.get('key_plot_points'):
                    key_plot_points = overall.get('key_plot_points', key_plot_points)
        
        ***REMOVED*** 检查章节大纲是否与整体大纲一致
        chapter_outlines = []
        if self.novel_plan:
            overall = self.novel_plan.get('overall', {})
            chapter_outlines = overall.get('chapter_outline', [])
        
        if self.metadata:
            plan = self.metadata.get('plan', {})
            if plan:
                overall = plan.get('overall', {})
                if overall.get('chapter_outline'):
                    chapter_outlines = overall.get('chapter_outline', chapter_outlines)
        
        ***REMOVED*** 检查伏笔是否回收
        ***REMOVED*** 检查情节逻辑是否完整
        ***REMOVED*** 检查是否有矛盾
        
        return {
            "key_plot_points_count": len(key_plot_points),
            "chapter_outlines_count": len(chapter_outlines),
            "issues": plot_issues,
            "summary": f"情节逻辑完整性检查完成，发现 {len(plot_issues)} 个问题"
        }
    
    def _check_style_consistency(self) -> Dict[str, Any]:
        """风格统一性检查"""
        style_issues = []
        
        ***REMOVED*** 统计每章的对话占比（使用与 quality_checker 相同的检测逻辑）
        dialogue_ratios = []
        for chapter in self.chapters:
            ***REMOVED*** 使用多种引号格式检测（与 quality_checker 保持一致）
            dialogues = []
            ***REMOVED*** 中文双引号："和"（U+201C和U+201D）
            pattern1 = r'[\u201C]([^\u201D]+?)[\u201D]'
            dialogues.extend(re.findall(pattern1, chapter.content))
            ***REMOVED*** 中文单引号：'和'（U+2018和U+2019）
            pattern2 = r'[\u2018]([^\u2019]+?)[\u2019]'
            dialogues.extend(re.findall(pattern2, chapter.content))
            ***REMOVED*** 日式引号：「和」（U+300C和U+300D）
            pattern3 = r'[\u300C]([^\u300D]+?)[\u300D]'
            dialogues.extend(re.findall(pattern3, chapter.content))
            ***REMOVED*** 日式双引号：『和』（U+300E和U+300F）
            pattern4 = r'[\u300E]([^\u300F]+?)[\u300F]'
            dialogues.extend(re.findall(pattern4, chapter.content))
            ***REMOVED*** 英文引号："和"、'和'
            pattern5 = r'["\']([^"\']+?)["\']'
            dialogues.extend(re.findall(pattern5, chapter.content))
            
            total_chars = len(chapter.content)
            dialogue_chars = sum(len(d) for d in dialogues)
            ratio = dialogue_chars / total_chars if total_chars > 0 else 0
            dialogue_ratios.append(ratio)
            
            ***REMOVED*** 检查对话占比是否在合理范围（根据模式调整）
            checker = self.quality_checker
            if ratio < checker.dialogue_ratio_ideal_min:
                style_issues.append({
                    "chapter": chapter.chapter_number,
                    "type": "low_dialogue_ratio",
                    "severity": "low",
                    "description": f"第{chapter.chapter_number}章对话占比过低: {ratio:.1%}（目标: {checker.dialogue_ratio_ideal_min:.0%}-{checker.dialogue_ratio_ideal_max:.0%}）"
                })
            elif ratio > checker.dialogue_ratio_ideal_max:
                style_issues.append({
                    "chapter": chapter.chapter_number,
                    "type": "high_dialogue_ratio",
                    "severity": "low",
                    "description": f"第{chapter.chapter_number}章对话占比过高: {ratio:.1%}（目标: {checker.dialogue_ratio_ideal_min:.0%}-{checker.dialogue_ratio_ideal_max:.0%}）"
                })
        
        avg_dialogue_ratio = sum(dialogue_ratios) / len(dialogue_ratios) if dialogue_ratios else 0
        
        return {
            "issues": style_issues,
            "avg_dialogue_ratio": round(avg_dialogue_ratio, 2),
            "summary": f"风格统一性检查完成，平均对话占比: {avg_dialogue_ratio:.1%}，发现 {len(style_issues)} 个问题"
        }
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成优化建议"""
        recommendations = []
        
        ***REMOVED*** 统计问题章节
        chapter_quality = report.get("chapter_quality", {})
        problematic_chapters = [
            ch_num for ch_num, quality in chapter_quality.items()
            if quality.get("total_issues", 0) >= 3 or quality.get("has_high_severity", False)
        ]
        
        if problematic_chapters:
            recommendations.append({
                "priority": "high",
                "type": "chapter_optimization",
                "description": f"建议优化 {len(problematic_chapters)} 个问题章节",
                "chapters": sorted(problematic_chapters),
                "action": "运行自动优化或手动修复"
            })
        
        ***REMOVED*** 风格问题建议
        style_issues = report.get("checks", {}).get("style_consistency", {}).get("issues", [])
        if style_issues:
            low_dialogue = [i for i in style_issues if i.get("type") == "low_dialogue_ratio"]
            if low_dialogue:
                recommendations.append({
                    "priority": "medium",
                    "type": "dialogue_enhancement",
                    "description": f"{len(low_dialogue)} 章对话占比过低，建议增加对话",
                    "chapters": [i["chapter"] for i in low_dialogue],
                    "action": "在对话中增加动作描写和情绪表达"
                })
        
        ***REMOVED*** 连贯性问题建议
        coherence_issues = report.get("checks", {}).get("coherence", {}).get("issues", [])
        if coherence_issues:
            recommendations.append({
                "priority": "medium",
                "type": "coherence_fix",
                "description": f"发现 {len(coherence_issues)} 个连贯性问题",
                "action": "检查章节间的角色连续性和情节衔接"
            })
        
        return recommendations
    
    def _calculate_overall_score(self, report: Dict[str, Any]) -> float:
        """计算总体评分"""
        scores = []
        
        ***REMOVED*** 连贯性得分
        coherence_score = report.get("checks", {}).get("coherence", {}).get("score", 1.0)
        scores.append(coherence_score * 0.3)
        
        ***REMOVED*** 章节质量得分（基于问题数量）
        chapter_quality = report.get("chapter_quality", {})
        if chapter_quality:
            total_issues = sum(q.get("total_issues", 0) for q in chapter_quality.values())
            total_chapters = len(chapter_quality)
            avg_issues = total_issues / total_chapters if total_chapters > 0 else 0
            ***REMOVED*** 问题越少，得分越高（每章平均问题数 <= 2 为满分）
            chapter_score = max(0, 1.0 - avg_issues / 4.0)
            scores.append(chapter_score * 0.4)
        else:
            scores.append(0.4)
        
        ***REMOVED*** 风格得分
        style_issues = report.get("checks", {}).get("style_consistency", {}).get("issues", [])
        style_score = max(0, 1.0 - len(style_issues) / 50.0)  ***REMOVED*** 50个问题为0分
        scores.append(style_score * 0.2)
        
        ***REMOVED*** 角色一致性得分
        char_issues = report.get("checks", {}).get("character_consistency", {}).get("issues", [])
        char_score = max(0, 1.0 - len(char_issues) / 10.0)  ***REMOVED*** 10个问题为0分
        scores.append(char_score * 0.1)
        
        overall = sum(scores)
        return round(overall, 2)
    
    def _optimize_chapters(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """
        自动优化问题章节
        
        Args:
            report: 检查报告
        
        Returns:
            优化结果
        """
        optimization_result = {
            "optimized_chapters": [],
            "optimized_count": 0,
            "failed_chapters": [],
            "optimization_details": {}
        }
        
        ***REMOVED*** 识别需要优化的章节（问题数 >= 3 或高严重度）
        chapter_quality = report.get("chapter_quality", {})
        chapters_to_optimize = [
            ch_num for ch_num, quality in chapter_quality.items()
            if quality.get("total_issues", 0) >= 3 or quality.get("has_high_severity", False)
        ]
        
        logger.info(f"需要优化的章节: {chapters_to_optimize}")
        
        ***REMOVED*** 创建优化输出目录
        optimized_dir = self.novel_output_dir / "optimized"
        optimized_dir.mkdir(exist_ok=True)
        optimized_chapters_dir = optimized_dir / "chapters"
        optimized_chapters_dir.mkdir(exist_ok=True)
        
        for ch_num in chapters_to_optimize[:10]:  ***REMOVED*** 限制一次最多优化10章
            try:
                logger.info(f"优化第{ch_num}章...")
                chapter = self.chapters[ch_num - 1]
                quality_info = chapter_quality[ch_num]
                
                ***REMOVED*** 生成优化后的章节
                optimized_content = self._optimize_single_chapter(chapter, quality_info)
                
                if optimized_content:
                    ***REMOVED*** 保存优化后的章节
                    optimized_file = optimized_chapters_dir / f"chapter_{ch_num:03d}.txt"
                    with open(optimized_file, 'w', encoding='utf-8') as f:
                        f.write(optimized_content)
                    
                    optimization_result["optimized_chapters"].append(ch_num)
                    optimization_result["optimization_details"][ch_num] = {
                        "original_issues": quality_info.get("total_issues", 0),
                        "status": "optimized"
                    }
                    logger.info(f"第{ch_num}章优化完成")
                else:
                    optimization_result["failed_chapters"].append(ch_num)
                    logger.warning(f"第{ch_num}章优化失败")
                    
            except Exception as e:
                logger.error(f"优化第{ch_num}章时出错: {e}", exc_info=True)
                optimization_result["failed_chapters"].append(ch_num)
        
        optimization_result["optimized_count"] = len(optimization_result["optimized_chapters"])
        
        ***REMOVED*** 生成优化后的完整小说
        if optimization_result["optimized_count"] > 0:
            self._generate_optimized_full_novel(optimized_chapters_dir)
        
        return optimization_result
    
    def _optimize_single_chapter(self, chapter: NovelChapter, quality_info: Dict[str, Any]) -> Optional[str]:
        """
        优化单个章节
        
        使用 kimi_k2 和 deepseek_v3_2 进行优化，如果一个失败会自动切换到另一个
        
        Args:
            chapter: 章节对象
            quality_info: 质量信息
        
        Returns:
            优化后的章节内容，如果失败返回 None
        """
        issues = quality_info.get("issues", [])
        if not issues:
            return None
        
        ***REMOVED*** 构建优化提示词
        issues_summary = []
        for issue in issues[:3]:  ***REMOVED*** 最多处理3个问题
            issue_type = issue.get("type", "")
            description = issue.get("description", "")
            suggestion = issue.get("suggestion", "")
            issues_summary.append(f"- {issue_type}: {description}\n  建议: {suggestion}")
        
        ***REMOVED*** 构建上下文信息（充分利用所有可用信息）
        context_parts = []
        
        ***REMOVED*** 1. 角色信息
        if self.character_profiles:
            key_characters = []
            for char_name, profile in list(self.character_profiles.items())[:10]:  ***REMOVED*** 最多10个关键角色
                desc = profile.get("description", "")
                if desc:
                    key_characters.append(f"- {char_name}: {desc[:100]}")
            if key_characters:
                context_parts.append("关键角色信息：\n" + "\n".join(key_characters))
        
        ***REMOVED*** 2. 章节大纲信息
        chapter_outline = None
        if self.novel_plan:
            overall = self.novel_plan.get('overall', {})
            outlines = overall.get('chapter_outline', [])
            for outline in outlines:
                if outline.get('chapter_number') == chapter.chapter_number:
                    chapter_outline = outline.get('summary', '')
                    break
        
        if not chapter_outline and self.metadata:
            plan = self.metadata.get('plan', {})
            if plan:
                overall = plan.get('overall', {})
                outlines = overall.get('chapter_outline', [])
                for outline in outlines:
                    if outline.get('chapter_number') == chapter.chapter_number:
                        chapter_outline = outline.get('summary', '')
                        break
        
        if chapter_outline:
            context_parts.append(f"章节大纲：{chapter_outline}")
        
        ***REMOVED*** 3. 世界观设定
        if self.novel_plan:
            overall = self.novel_plan.get('overall', {})
            background = overall.get('background', '')
            if background:
                context_parts.append(f"世界观背景：{background[:200]}...")
        
        context_text = "\n\n".join(context_parts) if context_parts else ""
        
        prompt = f"""请优化以下小说章节，修复检测到的质量问题。

章节标题：{chapter.title}
章节编号：第{chapter.chapter_number}章

{context_text}

当前内容：
{chapter.content[:3000]}...

检测到的问题：
{chr(10).join(issues_summary)}

优化要求：
1. **必须对原文进行实质性修改**：根据上述问题改写相应句子/段落，不能原样返回。至少修改 2～3 处以上以修复问题。
2. 保持核心情节和主要事件不变，但表达方式、用词、句式等可以且应当调整。
3. 修复上述质量问题（如对话动作、心理活动、情节衔接等）。
4. 保持文笔风格一致，字数在合理范围内（±10%）。
5. 确保角色名称、性格、世界观设定与前面章节保持一致。
6. **重要**：不需要所有角色每章都出现，只需确保本章出现的角色与前面章节保持一致即可。根据章节设定和情节需要，某些章节可能只涉及部分角色，这是正常的创作情况。

请直接返回优化后的**完整**章节内容，不要包含标题或其他格式。不要原样照抄原文。"""

        ***REMOVED*** 尝试使用不同的LLM进行优化
        for i, llm_func in enumerate(self.optimization_llms):
            try:
                logger.info(f"使用 {llm_func.__name__} 优化第{chapter.chapter_number}章...")
                reasoning, optimized_content = llm_func(
                    [{"role": "user", "content": prompt}],
                    max_new_tokens=4096
                )
                
                if not optimized_content or len(optimized_content) <= 100:
                    continue
                
                optimized_content = optimized_content.strip()
                orig = chapter.content.strip()
                
                ***REMOVED*** 相似度检查：若与原文几乎相同，视为未优化，不采纳
                try:
                    import difflib
                    ratio = difflib.SequenceMatcher(None, orig, optimized_content).ratio()
                    if ratio >= 0.98:
                        logger.warning(
                            f"第{chapter.chapter_number}章优化结果与原文相似度过高 ({ratio:.2%})，视为未修改，跳过"
                        )
                        if i < len(self.optimization_llms) - 1:
                            continue
                        return None
                except Exception:
                    pass
                
                logger.info(f"第{chapter.chapter_number}章优化成功 (使用 {llm_func.__name__})")
                return optimized_content
                    
            except Exception as e:
                logger.error(f"使用 {llm_func.__name__} 优化第{chapter.chapter_number}章失败: {e}")
                if i < len(self.optimization_llms) - 1:
                    logger.info(f"切换到下一个LLM继续尝试...")
                    continue
        
        logger.warning(f"所有LLM都无法优化第{chapter.chapter_number}章")
        return None
    
    def _generate_optimized_full_novel(self, optimized_chapters_dir: Path):
        """生成优化后的完整小说"""
        logger.info("生成优化后的完整小说...")
        
        full_content = []
        full_content.append(f"《{self.metadata.get('title', '未知')}》\n")
        full_content.append("=" * 60 + "\n\n")
        
        for i in range(1, 101):
            ***REMOVED*** 优先使用优化后的章节
            optimized_file = optimized_chapters_dir / f"chapter_{i:03d}.txt"
            original_file = self.chapters_dir / f"chapter_{i:03d}.txt"
            
            if optimized_file.exists():
                with open(optimized_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                full_content.append(f"第{i}章 {self.chapters[i-1].title}\n")
                full_content.append("-" * 40 + "\n")
                full_content.append(content)
                full_content.append("\n\n")
            elif original_file.exists():
                with open(original_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                full_content.append(f"第{i}章 {self.chapters[i-1].title}\n")
                full_content.append("-" * 40 + "\n")
                full_content.append(content)
                full_content.append("\n\n")
        
        ***REMOVED*** 保存完整版
        full_novel_file = self.novel_output_dir / "optimized" / f"{self.metadata.get('title', '小说')}_优化版.txt"
        with open(full_novel_file, 'w', encoding='utf-8') as f:
            f.write(''.join(full_content))
        
        logger.info(f"优化后的完整小说已保存: {full_novel_file}")
    
    def save_report(self, report: Dict[str, Any], output_file: Optional[Path] = None):
        """保存检查报告"""
        if output_file is None:
            output_file = self.novel_output_dir / "full_quality_report.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"检查报告已保存: {output_file}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='全本小说质量检查 Agent')
    parser.add_argument(
        '--novel_dir',
        type=str,
        required=True,
        help='小说输出目录路径'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='报告输出文件路径（可选）'
    )
    parser.add_argument(
        '--optimize',
        action='store_true',
        help='自动优化问题章节（生成优化后的版本）'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='使用严格模式检查（默认使用宽松模式，更符合网络小说特点）'
    )
    
    args = parser.parse_args()
    
    ***REMOVED*** 创建 Agent（默认使用宽松模式，除非用户指定 --strict）
    agent = FullNovelQualityAgent(Path(args.novel_dir), strict_mode=args.strict)
    
    ***REMOVED*** 运行检查（可选：自动优化）
    report = agent.run_full_check(auto_optimize=args.optimize)
    
    ***REMOVED*** 保存报告
    output_file = Path(args.output) if args.output else None
    agent.save_report(report, output_file)
    
    ***REMOVED*** 打印摘要
    print("\n" + "=" * 60)
    print("检查报告摘要")
    print("=" * 60)
    print(f"总体评分: {report['overall_score']:.2f}/1.00")
    print(f"检查章节数: {report['total_chapters']}")
    
    ***REMOVED*** 统计问题
    chapter_quality = report.get("chapter_quality", {})
    total_issues = sum(q.get("total_issues", 0) for q in chapter_quality.values())
    problematic_chapters = [ch for ch, q in chapter_quality.items() if q.get("total_issues", 0) >= 3]
    print(f"总问题数: {total_issues}")
    print(f"问题章节数: {len(problematic_chapters)}")
    
    if args.optimize:
        opt_result = report.get("optimization", {})
        print(f"\n优化结果:")
        print(f"  优化章节数: {opt_result.get('optimized_count', 0)}")
        print(f"  失败章节数: {len(opt_result.get('failed_chapters', []))}")
        if opt_result.get('optimized_count', 0) > 0:
            title = report.get("novel_title", "小说")
            print(f"  优化后的完整小说: {agent.novel_output_dir / 'optimized' / f'{title}_优化版.txt'}")
    
    print("\n详细报告已保存到:", output_file or agent.novel_output_dir / "full_quality_report.json")


if __name__ == "__main__":
    main()
