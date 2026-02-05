"""
增强的实体提取器
使用 LLM 辅助提取，提升实体提取质量和数量
"""
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from context import Entity, EntityType, RelationType

logger = logging.getLogger(__name__)


@dataclass
class EntityExtractionResult:
    """实体提取结果"""
    entities: List[Entity]
    relations: List[Dict[str, Any]]
    confidence: float


class EnhancedEntityExtractor:
    """
    增强的实体提取器
    
    使用多层级方法提取实体：
    1. LLM 辅助提取（主要方法）
    2. NER 模型提取（辅助方法，可选）
    3. 规则匹配（补充方法）
    """
    
    def __init__(self, llm_client=None, use_ner: bool = False):
        """
        初始化实体提取器
        
        Args:
            llm_client: LLM 客户端（用于辅助提取）
            use_ner: 是否使用 NER 模型（需要额外安装）
        """
        self.llm_client = llm_client
        self.use_ner = use_ner
        
        # 角色名模式（改进版）
        self.character_patterns = [
            r'["""]([^"""]{2,20})["""]',  # 引号内的内容
            r'[，。！？]\s*([A-Za-z\u4e00-\u9fa5]{2,10})\s*[说道说]',  # "XXX说道"
            r'([A-Za-z\u4e00-\u9fa5]{2,10})\s*[的]?\s*[眼睛目光表情]',  # "XXX的眼睛"
        ]
        
        # 地点模式
        self.location_patterns = [
            r'[在到]\s*([A-Za-z\u4e00-\u9fa5]{2,15})\s*[，。]',  # "在XXX"
            r'([A-Za-z\u4e00-\u9fa5]{2,15})\s*[市省县区]',  # "XXX市"
        ]
        
        # 物品/符号模式
        self.item_patterns = [
            r'[一本一张一把一个]\s*([A-Za-z\u4e00-\u9fa5]{2,10})',  # "一本XXX"
            r'([A-Za-z\u4e00-\u9fa5]{2,10})\s*[日记书剑]',  # "XXX日记"
        ]
    
    def extract_entities(self, text: str, chapter_number: int = 0) -> EntityExtractionResult:
        """
        提取实体（多层级方法）
        
        Args:
            text: 文本内容
            chapter_number: 章节编号
        
        Returns:
            EntityExtractionResult
        """
        all_entities = []
        all_relations = []
        
        # 1. LLM 辅助提取（主要方法）
        if self.llm_client:
            try:
                llm_result = self._extract_with_llm(text, chapter_number)
                all_entities.extend(llm_result['entities'])
                all_relations.extend(llm_result['relations'])
                logger.debug(f"LLM 提取到 {len(llm_result['entities'])} 个实体")
            except Exception as e:
                logger.warning(f"LLM 提取失败: {e}")
        
        # 2. 规则匹配（补充方法）
        rule_result = self._extract_with_rules(text, chapter_number)
        all_entities.extend(rule_result['entities'])
        all_relations.extend(rule_result['relations'])
        logger.debug(f"规则提取到 {len(rule_result['entities'])} 个实体")
        
        # 3. 合并和去重
        merged_entities = self._merge_entities(all_entities)
        merged_relations = self._merge_relations(all_relations)
        
        # 计算置信度
        confidence = self._calculate_confidence(merged_entities, merged_relations)
        
        return EntityExtractionResult(
            entities=merged_entities,
            relations=merged_relations,
            confidence=confidence
        )
    
    def _extract_with_llm(self, text: str, chapter_number: int) -> Dict[str, Any]:
        """
        使用 LLM 辅助提取实体
        
        Args:
            text: 文本内容
            chapter_number: 章节编号
        
        Returns:
            {'entities': [...], 'relations': [...]}
        """
        if not self.llm_client:
            return {'entities': [], 'relations': []}

        from config.novel.prompts import get_entity_extraction_prompt
        prompt = get_entity_extraction_prompt(text, max_chars=2000)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = self.llm_client(messages)
            
            # 解析 JSON 响应
            import json
            # deepseek_v3_2 返回 (reasoning_content, content) 元组
            if isinstance(response, tuple):
                _, content = response
            elif hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # 提取 JSON 部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                # 转换为 Entity 对象
                entities = []
                for e in data.get('entities', []):
                    entity_type_map = {
                        'character': EntityType.CHARACTER,
                        'location': EntityType.SETTING,  # 地点使用 SETTING
                        'setting': EntityType.SETTING,
                        'item': EntityType.SYMBOL,
                        'symbol': EntityType.SYMBOL,
                        'concept': EntityType.THEME,  # 概念使用 THEME
                        'theme': EntityType.THEME,
                    }
                    entity_type = entity_type_map.get(e.get('type', 'character'), EntityType.CHARACTER)
                    
                    # 验证实体名称（过滤掉句子片段）
                    entity_name = e['name'].strip()
                    # 过滤掉包含动词、标点的片段（如"林风睁开眼"）
                    if len(entity_name) > 1 and len(entity_name) <= 20:
                        # 检查是否包含明显的动词或动作词
                        action_words = ['睁开', '看到', '听到', '说道', '说道', '走来', '跑去', '想起', '想起', '感到', '觉得']
                        if not any(word in entity_name for word in action_words):
                            entity = Entity(
                                id=f"llm_{chapter_number}_{hash(entity_name) % 10000}",
                                type=entity_type,
                                name=entity_name,
                                content=e.get('description', ''),
                                metadata={
                                    "chapter": chapter_number,  # 确保设置章节号
                                    "extraction_method": "llm",
                                    **(e.get('attributes', {}))
                                }
                            )
                            entities.append(entity)
                        else:
                            logger.debug(f"过滤掉动作片段实体: {entity_name}")
                    else:
                        logger.debug(f"过滤掉无效实体名称: {entity_name} (长度: {len(entity_name)})")
                
                return {
                    'entities': entities,
                    'relations': data.get('relations', [])
                }
        except Exception as e:
            logger.error(f"LLM 提取失败: {e}")
        
        return {'entities': [], 'relations': []}
    
    def _extract_with_rules(self, text: str, chapter_number: int) -> Dict[str, Any]:
        """
        使用规则匹配提取实体（改进版）
        
        Args:
            text: 文本内容
            chapter_number: 章节编号
        
        Returns:
            {'entities': [...], 'relations': [...]}
        """
        entities = []
        relations = []
        
        # 提取角色
        characters = set()
        for pattern in self.character_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                if match and 2 <= len(match) <= 20:
                    characters.add(match)
        
        for char_name in list(characters)[:10]:  # 最多10个角色
            entity = Entity(
                id=f"char_{chapter_number}_{hash(char_name) % 10000}",
                type=EntityType.CHARACTER,
                name=char_name,
                content=f"出现在第{chapter_number}章的角色",
                metadata={"chapter": chapter_number, "extraction_method": "rule"}
            )
            entities.append(entity)
        
        # 提取地点
        locations = set()
        for pattern in self.location_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                if match and 2 <= len(match) <= 15:
                    locations.add(match)
        
        for loc_name in list(locations)[:5]:  # 最多5个地点
            entity = Entity(
                id=f"loc_{chapter_number}_{hash(loc_name) % 10000}",
                type=EntityType.SETTING,  # 地点使用 SETTING
                name=loc_name,
                content=f"在第{chapter_number}章中提到的地点",
                metadata={"chapter": chapter_number, "extraction_method": "rule"}
            )
            entities.append(entity)
        
        # 提取物品/符号
        items = set()
        for pattern in self.item_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match else ""
                if match and 2 <= len(match) <= 10:
                    items.add(match)
        
        # 关键词匹配
        symbol_keywords = ["日记", "书", "剑", "戒指", "吊坠", "地图", "钥匙", "设备", "仪器"]
        for keyword in symbol_keywords:
            if keyword in text:
                items.add(keyword)
        
        for item_name in list(items)[:5]:  # 最多5个物品
            entity = Entity(
                id=f"item_{chapter_number}_{hash(item_name) % 10000}",
                type=EntityType.SYMBOL,
                name=item_name,
                content=f"在第{chapter_number}章中提到的{item_name}",
                metadata={"chapter": chapter_number, "extraction_method": "rule"}
            )
            entities.append(entity)
        
        return {
            'entities': entities,
            'relations': relations
        }
    
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """合并和去重实体"""
        entity_map = {}
        
        for entity in entities:
            # 使用 name 作为唯一标识
            key = entity.name.lower()
            
            if key not in entity_map:
                entity_map[key] = entity
            else:
                # 合并属性
                existing = entity_map[key]
                if entity.content and not existing.content:
                    existing.content = entity.content
                if entity.metadata:
                    existing.metadata.update(entity.metadata)
        
        return list(entity_map.values())
    
    def _merge_relations(self, relations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """合并和去重关系"""
        relation_set = set()
        
        for rel in relations:
            # 使用 (source, target, type) 作为唯一标识
            key = (rel.get('source', ''), rel.get('target', ''), rel.get('type', ''))
            if key not in relation_set:
                relation_set.add(key)
        
        return [rel for rel in relations if (rel.get('source', ''), rel.get('target', ''), rel.get('type', '')) in relation_set]
    
    def _calculate_confidence(self, entities: List[Entity], relations: List[Dict[str, Any]]) -> float:
        """计算提取置信度"""
        if not entities:
            return 0.0
        
        # 基础置信度
        base_confidence = 0.5
        
        # LLM 提取的实体置信度更高
        llm_count = sum(1 for e in entities if e.metadata.get('extraction_method') != 'rule')
        if llm_count > 0:
            base_confidence += 0.3
        
        # 有关系的实体置信度更高
        if relations:
            base_confidence += 0.2
        
        return min(base_confidence, 1.0)
