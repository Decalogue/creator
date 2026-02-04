"""
Skill 类：单技能表示（元数据 + 主体 + 资源）

创作相关：表示一个可被 Creator 按需加载的 SOP/规范/说明，含元数据、
主体内容和资源文件，供 skills.manager 扫描与披露。
"""
import yaml
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class SkillMetadata:
    """Skill 元数据（第一层，始终加载）"""
    name: str
    description: str
    version: str = "1.0.0"
    author: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)  ***REMOVED*** 触发关键词


class Skill:
    """
    Skill 类
    表示一个包含说明文档、脚本和资源的 Skill
    """
    
    def __init__(self, skill_path: Path):
        """
        初始化 Skill
        
        Args:
            skill_path: Skill 目录路径
        """
        self.skill_path = Path(skill_path)
        self.skill_md_path = self.skill_path / "SKILL.md"
        
        if not self.skill_md_path.exists():
            raise ValueError(f"SKILL.md not found in {skill_path}")
        
        ***REMOVED*** 渐进式披露的三层内容
        self._metadata: Optional[SkillMetadata] = None  ***REMOVED*** 第一层：元数据（始终加载）
        self._body: Optional[str] = None  ***REMOVED*** 第二层：主体内容（触发时加载）
        self._resources: Dict[str, str] = {}  ***REMOVED*** 第三层：资源文件（按需加载）
        
        ***REMOVED*** 加载元数据（第一层，始终加载）
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """加载 SKILL.md 的元数据部分（YAML front matter）"""
        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ***REMOVED*** 解析 YAML front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                metadata_dict = yaml.safe_load(yaml_content) or {}
            else:
                metadata_dict = {}
        else:
            metadata_dict = {}
        
        ***REMOVED*** 创建元数据对象
        self._metadata = SkillMetadata(
            name=metadata_dict.get('name', self.skill_path.name),
            description=metadata_dict.get('description', ''),
            version=metadata_dict.get('version', '1.0.0'),
            author=metadata_dict.get('author'),
            tags=metadata_dict.get('tags', []),
            triggers=metadata_dict.get('triggers', [])
        )
    
    def load_body(self) -> str:
        """加载 SKILL.md 的主体内容（第二层，触发时加载）"""
        if self._body is not None:
            return self._body
        
        with open(self.skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ***REMOVED*** 移除 YAML front matter，只保留主体内容
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                self._body = parts[2].strip()
            else:
                self._body = content
        else:
            self._body = content
        
        return self._body
    
    def load_resource(self, filename: str) -> str:
        """
        加载资源文件（第三层，按需加载）
        
        Args:
            filename: 资源文件名（相对于 skill_path）
        
        Returns:
            文件内容
        """
        if filename in self._resources:
            return self._resources[filename]
        
        resource_path = self.skill_path / filename
        if not resource_path.exists():
            raise FileNotFoundError(f"Resource file not found: {resource_path}")
        
        with open(resource_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._resources[filename] = content
        return content
    
    def list_resources(self) -> List[str]:
        """列出所有可用的资源文件"""
        return [
            file.name for file in self.skill_path.iterdir()
            if file.is_file() and file.name != "SKILL.md"
        ]
    
    @property
    def metadata(self) -> SkillMetadata:
        """获取元数据（第一层）"""
        return self._metadata
    
    @property
    def name(self) -> str:
        """Skill 名称"""
        return self._metadata.name
    
    @property
    def description(self) -> str:
        """Skill 描述"""
        return self._metadata.description
    
    def get_context(self, level: int = 1) -> str:
        """
        获取指定层级的上下文内容
        
        Args:
            level: 层级（1=元数据，2=主体，3=所有资源）
        
        Returns:
            上下文内容
        """
        context_parts = []
        
        ***REMOVED*** 第一层：元数据（始终包含）
        context_parts.append(f"***REMOVED*** {self._metadata.name}\n")
        context_parts.append(f"**描述**: {self._metadata.description}\n")
        if self._metadata.tags:
            context_parts.append(f"**标签**: {', '.join(self._metadata.tags)}\n")
        if self._metadata.triggers:
            context_parts.append(f"**触发词**: {', '.join(self._metadata.triggers)}\n")
        
        ***REMOVED*** 第二层：主体内容
        if level >= 2:
            body = self.load_body()
            context_parts.append(f"\n{body}\n")
        
        ***REMOVED*** 第三层：资源文件
        if level >= 3:
            resources = self.list_resources()
            for resource in resources:
                try:
                    content = self.load_resource(resource)
                    context_parts.append(f"\n***REMOVED******REMOVED*** {resource}\n\n{content}\n")
                except Exception as e:
                    context_parts.append(f"\n***REMOVED******REMOVED*** {resource}\n\n[加载失败: {str(e)}]\n")
        
        return "\n".join(context_parts)
    
    def estimate_tokens(self, level: int = 1) -> int:
        """
        估算指定层级的 token 数量（粗略估算：1 token ≈ 4 字符）
        
        Args:
            level: 层级
        
        Returns:
            估算的 token 数量
        """
        context = self.get_context(level)
        return len(context) // 4
