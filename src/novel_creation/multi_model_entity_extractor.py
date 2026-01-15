"""
多模型投票实体提取器
使用多个 LLM 模型提取实体，通过投票机制保留公共部分，提高准确性
"""
import re
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from collections import Counter

from creative_context import Entity, EntityType, RelationType

logger = logging.getLogger(__name__)


@dataclass
class EntityVote:
    """实体投票结果"""
    name: str
    type: EntityType
    votes: int  ***REMOVED*** 投票数
    descriptions: List[str]  ***REMOVED*** 各模型的描述
    metadata_list: List[Dict[str, Any]]  ***REMOVED*** 各模型的元数据


class MultiModelEntityExtractor:
    """
    多模型投票实体提取器
    
    使用多个 LLM 模型并行提取实体，通过投票机制：
    1. 多个模型同时提取
    2. 对实体名称进行标准化和匹配
    3. 保留至少 N 个模型都提取到的实体（投票阈值）
    4. 合并描述和元数据
    """
    
    def __init__(
        self,
        llm_clients: List[Any],
        vote_threshold: int = 2,  ***REMOVED*** 至少2个模型都提取到才保留
        use_ner: bool = False
    ):
        """
        初始化多模型实体提取器
        
        Args:
            llm_clients: LLM 客户端列表（至少2个）
            vote_threshold: 投票阈值（至少需要多少个模型都提取到）
            use_ner: 是否使用 NER 模型（可选）
        """
        if len(llm_clients) < 2:
            raise ValueError("至少需要2个LLM客户端进行投票")
        
        self.llm_clients = llm_clients
        self.vote_threshold = min(vote_threshold, len(llm_clients))
        self.use_ner = use_ner
        
        logger.info(f"多模型实体提取器初始化：{len(llm_clients)} 个模型，投票阈值: {self.vote_threshold}")
    
    def extract_entities(self, text: str, chapter_number: int = 0) -> List[Entity]:
        """
        使用多模型投票提取实体
        
        Args:
            text: 文本内容
            chapter_number: 章节编号
        
        Returns:
            提取的实体列表（经过投票筛选）
        """
        ***REMOVED*** 1. 并行调用多个模型提取
        all_results = []
        for i, llm_client in enumerate(self.llm_clients):
            try:
                result = self._extract_with_single_model(llm_client, text, chapter_number, model_id=i)
                all_results.append(result)
                logger.debug(f"模型 {i} 提取到 {len(result)} 个实体")
            except Exception as e:
                logger.warning(f"模型 {i} 提取失败: {e}")
                all_results.append([])
        
        ***REMOVED*** 2. 投票和合并
        voted_entities = self._vote_and_merge(all_results, chapter_number)
        
        logger.info(
            f"多模型投票结果：{len(all_results)} 个模型，"
            f"共提取 {sum(len(r) for r in all_results)} 个候选实体，"
            f"投票后保留 {len(voted_entities)} 个实体"
        )
        
        return voted_entities
    
    def _extract_with_single_model(
        self,
        llm_client: Any,
        text: str,
        chapter_number: int,
        model_id: int
    ) -> List[Dict[str, Any]]:
        """
        使用单个模型提取实体
        
        Args:
            llm_client: LLM 客户端
            text: 文本内容
            chapter_number: 章节编号
            model_id: 模型ID（用于日志）
        
        Returns:
            实体字典列表 [{"name": "...", "type": "...", "description": "...", ...}, ...]
        """
        prompt = f"""请从以下小说章节中提取实体。**重要：只提取真正的实体名称，不要提取句子片段或描述性短语。**

章节内容：
{text[:2000]}...

请提取以下类型的实体：
1. **角色（Character）**：人物姓名、称呼（如"林修"、"三长老"），**不要提取**动作描述（如"说道"、"睁开眼"）
2. **地点（Location）**：地点名称、场所（如"青阳镇"、"演武场"），**不要提取**位置描述（如"在...上"、"从...中"）
3. **物品（Item/Symbol）**：重要物品、道具名称（如"测灵玉"、"青阳诀"），**不要提取**抽象概念或描述

**提取规则**：
- 实体名称必须是**完整的名词或名词短语**（2-10个字符）
- **不要提取**包含动词的片段（如"苦涩地说"、"但林修知"）
- **不要提取**包含介词的位置描述（如"指尖接触的瞬间"、"在手中的名册上"）
- **不要提取**句子片段或描述性短语

请以 JSON 格式返回，格式如下：
{{
  "entities": [
    {{
      "name": "实体名称（必须是完整的名词）",
      "type": "character|location|item",
      "description": "实体描述（1-2句话）"
    }}
  ]
}}

**示例**：
正确：{{"name": "林修", "type": "character", "description": "小说主角，林家年轻子弟"}}
错误：{{"name": "但林修知", "type": "character", "description": "..."}}  （这是句子片段）
错误：{{"name": "指尖接触的瞬间", "type": "location", "description": "..."}}  （这是位置描述）
"""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            response = llm_client(messages)
            
            ***REMOVED*** 解析响应
            import json
            if isinstance(response, tuple):
                _, content = response
            elif hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            ***REMOVED*** 提取 JSON 部分
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                entities = []
                for e in data.get('entities', []):
                    ***REMOVED*** 验证实体名称
                    entity_name = e.get('name', '').strip()
                    if self._is_valid_entity_name(entity_name):
                        entities.append({
                            "name": entity_name,
                            "type": e.get('type', 'character'),
                            "description": e.get('description', ''),
                            "model_id": model_id
                        })
                    else:
                        logger.debug(f"模型 {model_id} 提取到无效实体名称: {entity_name}")
                
                return entities
        except Exception as e:
            logger.error(f"模型 {model_id} 提取失败: {e}")
        
        return []
    
    def _is_valid_entity_name(self, name: str) -> bool:
        """
        验证实体名称是否有效
        
        Args:
            name: 实体名称
        
        Returns:
            是否有效
        """
        if not name or len(name) < 2 or len(name) > 20:
            return False
        
        ***REMOVED*** 过滤掉包含动词的片段
        action_words = [
            '睁开', '看到', '听到', '说道', '走来', '跑去', '想起', '感到', '觉得',
            '知道', '发现', '决定', '开始', '结束', '完成', '进行', '执行',
            '苦涩', '终于', '此刻', '闪烁', '渴望', '能够', '像...一样'
        ]
        if any(word in name for word in action_words):
            return False
        
        ***REMOVED*** 过滤掉包含介词的片段
        preposition_words = ['在', '从', '到', '向', '往', '的', '上', '下', '中', '里']
        ***REMOVED*** 如果名称以介词开头或结尾，可能是位置描述
        if name.startswith(tuple(preposition_words)) or name.endswith(tuple(preposition_words)):
            ***REMOVED*** 但允许"青阳镇"这样的地名
            if len(name) <= 4:  ***REMOVED*** 短名称可能是地名
                pass
            else:
                return False
        
        ***REMOVED*** 过滤掉明显的句子片段
        if name.startswith(('但', '然而', '不过', '虽然', '因为', '所以')):
            return False
        
        ***REMOVED*** 过滤掉包含标点的片段（除了允许的标点）
        if re.search(r'[，。！？；：]', name):
            return False
        
        return True
    
    def _normalize_entity_name(self, name: str) -> str:
        """
        标准化实体名称（用于匹配）
        
        Args:
            name: 实体名称
        
        Returns:
            标准化后的名称
        """
        ***REMOVED*** 移除空格和标点
        normalized = re.sub(r'[，。！？；：\s]', '', name)
        return normalized
    
    def _vote_and_merge(
        self,
        all_results: List[List[Dict[str, Any]]],
        chapter_number: int
    ) -> List[Entity]:
        """
        投票和合并实体
        
        Args:
            all_results: 各模型的提取结果列表
            chapter_number: 章节编号
        
        Returns:
            合并后的实体列表
        """
        ***REMOVED*** 1. 按标准化名称分组
        entity_votes: Dict[str, EntityVote] = {}
        
        for model_id, entities in enumerate(all_results):
            for entity_dict in entities:
                name = entity_dict['name']
                normalized = self._normalize_entity_name(name)
                
                ***REMOVED*** 类型映射
                type_map = {
                    'character': EntityType.CHARACTER,
                    'location': EntityType.SETTING,
                    'setting': EntityType.SETTING,
                    'item': EntityType.SYMBOL,
                    'symbol': EntityType.SYMBOL,
                }
                entity_type = type_map.get(entity_dict.get('type', 'character'), EntityType.CHARACTER)
                
                if normalized not in entity_votes:
                    entity_votes[normalized] = EntityVote(
                        name=name,  ***REMOVED*** 使用第一个遇到的名称
                        type=entity_type,
                        votes=0,
                        descriptions=[],
                        metadata_list=[]
                    )
                
                vote = entity_votes[normalized]
                vote.votes += 1
                vote.descriptions.append(entity_dict.get('description', ''))
                vote.metadata_list.append({'model_id': model_id})
        
        ***REMOVED*** 2. 只保留达到投票阈值的实体
        voted_entities = []
        for normalized, vote in entity_votes.items():
            if vote.votes >= self.vote_threshold:
                ***REMOVED*** 合并描述（取最长的或最常见的）
                best_description = max(vote.descriptions, key=len) if vote.descriptions else ""
                
                entity = Entity(
                    id=f"voted_{chapter_number}_{hash(normalized) % 10000}",
                    type=vote.type,
                    name=vote.name,
                    content=best_description,
                    metadata={
                        "chapter": chapter_number,
                        "extraction_method": "multi_model_vote",
                        "votes": vote.votes,
                        "total_models": len(all_results),
                        "vote_ratio": vote.votes / len(all_results)
                    }
                )
                voted_entities.append(entity)
                logger.debug(f"实体 '{vote.name}' 获得 {vote.votes}/{len(all_results)} 票，已保留")
            else:
                logger.debug(f"实体 '{vote.name}' 仅获得 {vote.votes}/{len(all_results)} 票，未达到阈值 {self.vote_threshold}，已过滤")
        
        return voted_entities
