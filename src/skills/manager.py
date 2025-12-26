"""
Skill Manager
管理所有 Skills，实现扫描、加载和渐进式披露
"""
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from .skill import Skill, SkillMetadata


class SkillManager:
    """
    Skill 管理器
    负责扫描、加载和管理所有 Skills
    """
    
    def __init__(self, skills_dir: Optional[Path] = None):
        """
        初始化 Skill Manager
        
        Args:
            skills_dir: Skills 目录路径，默认为当前模块目录下的 skills 子目录
        """
        if skills_dir is None:
            ***REMOVED*** 默认使用当前文件所在目录
            current_dir = Path(__file__).parent
            skills_dir = current_dir
        
        self.skills_dir = Path(skills_dir)
        self._skills: Dict[str, Skill] = {}
        self._metadata_cache: Dict[str, SkillMetadata] = {}
        
        ***REMOVED*** 扫描并加载所有 Skills
        self.scan_skills()
    
    def scan_skills(self) -> None:
        """扫描 Skills 目录，加载所有 Skills 的元数据"""
        if not self.skills_dir.exists():
            return
        
        self._skills.clear()
        self._metadata_cache.clear()
        
        ***REMOVED*** 遍历所有子目录
        for item in self.skills_dir.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                skill_md = item / "SKILL.md"
                if skill_md.exists():
                    try:
                        skill = Skill(item)
                        self._skills[skill.name] = skill
                        self._metadata_cache[skill.name] = skill.metadata
                    except Exception as e:
                        print(f"Warning: Failed to load skill {item.name}: {e}")
    
    def list_skills(self) -> List[str]:
        """列出所有可用的 Skill 名称"""
        return list(self._skills.keys())
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """获取指定的 Skill"""
        return self._skills.get(name)
    
    def get_metadata(self, name: str) -> Optional[SkillMetadata]:
        """获取 Skill 的元数据（第一层，轻量级）"""
        return self._metadata_cache.get(name)
    
    def get_all_metadata(self) -> List[SkillMetadata]:
        """获取所有 Skills 的元数据列表（用于模型选择）"""
        return list(self._metadata_cache.values())
    
    def select_skills(self, query: str, max_skills: int = 5) -> List[Skill]:
        """
        根据查询选择相关的 Skills
        
        Args:
            query: 查询文本
            max_skills: 最多返回的 Skills 数量
        
        Returns:
            相关的 Skills 列表
        """
        query_lower = query.lower()
        scored_skills: List[Tuple[int, Skill]] = []
        
        for skill in self._skills.values():
            score = 0
            
            ***REMOVED*** 检查触发词
            for trigger in skill.metadata.triggers:
                if trigger.lower() in query_lower:
                    score += 10
            
            ***REMOVED*** 检查标签
            for tag in skill.metadata.tags:
                if tag.lower() in query_lower:
                    score += 5
            
            ***REMOVED*** 检查描述
            if skill.metadata.description.lower() in query_lower:
                score += 3
            
            ***REMOVED*** 检查名称
            if skill.metadata.name.lower() in query_lower:
                score += 2
            
            if score > 0:
                scored_skills.append((score, skill))
        
        ***REMOVED*** 按分数排序
        scored_skills.sort(key=lambda x: x[0], reverse=True)
        
        ***REMOVED*** 返回前 max_skills 个
        return [skill for _, skill in scored_skills[:max_skills]]
    
    def get_context_for_query(self, query: str, level: int = 2) -> str:
        """
        根据查询获取相关 Skills 的上下文
        
        Args:
            query: 查询文本
            level: 加载层级（1=元数据，2=主体，3=所有资源）
        
        Returns:
            组合的上下文内容
        """
        selected_skills = self.select_skills(query)
        
        if not selected_skills:
            return ""
        
        context_parts = []
        total_tokens = 0
        
        for skill in selected_skills:
            skill_context = skill.get_context(level)
            skill_tokens = skill.estimate_tokens(level)
            
            ***REMOVED*** 粗略限制：如果超过 10k tokens，只加载元数据
            if total_tokens + skill_tokens > 10000 and level > 1:
                skill_context = skill.get_context(1)
                skill_tokens = skill.estimate_tokens(1)
            
            context_parts.append(skill_context)
            total_tokens += skill_tokens
        
        return "\n\n---\n\n".join(context_parts)
    
    def reload_skill(self, name: str) -> None:
        """重新加载指定的 Skill"""
        skill = self._skills.get(name)
        if skill:
            skill_path = skill.skill_path
            try:
                new_skill = Skill(skill_path)
                self._skills[name] = new_skill
                self._metadata_cache[name] = new_skill.metadata
            except Exception as e:
                print(f"Warning: Failed to reload skill {name}: {e}")


***REMOVED*** 全局 Skill Manager 实例
default_manager = SkillManager()
