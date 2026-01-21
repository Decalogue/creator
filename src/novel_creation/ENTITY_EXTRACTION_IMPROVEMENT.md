***REMOVED*** 实体提取改进方案（基于 Kimi 能力分析）

***REMOVED******REMOVED*** Kimi 实体提取优势分析

***REMOVED******REMOVED******REMOVED*** 1. 分类更细致（7大类 vs 当前3类）

**Kimi 的分类**：
- 人物实体
- 组织/机构
- 地点实体
- 物品/装备
- 生物/妖怪亚种
- 概念/规则
- 时间/期限

**当前系统的分类**：
- CHARACTER（角色）
- SETTING（地点）
- SYMBOL（物品/符号）

**差距**：缺少组织、概念、规则、时间等类型

***REMOVED******REMOVED******REMOVED*** 2. 提取更全面

**Kimi 提取的实体类型**：
- ✅ 具体物品（黑鲨·静刃电锯、赤霄牌锯条）
- ✅ 概念/规则（当票法、尾巴债、恐惧抵押）
- ✅ 时间期限（三年期、七日限、明晚零点）
- ✅ 生物亚种（钉背鼠妖、鬣狗妖）
- ✅ 组织/机构（白夜当铺、回收队）

**当前系统可能遗漏**：
- ❌ 概念/规则类实体
- ❌ 时间/期限类实体
- ❌ 组织/机构（可能归类到 SETTING）
- ❌ 生物亚种（可能归类到 CHARACTER）

***REMOVED******REMOVED******REMOVED*** 3. 描述更详细

**Kimi 的描述格式**：
```
- **林鸦**（主角，废楼回收员＋无证驱妖人）
- **白夜当铺**（典当"情绪"与肢体的机构）
- **黑鲨·静刃电锯**（掺银附魔）
```

**当前系统的描述**：
- 通常只有简单的1-2句话描述
- 缺少括号内的关键信息补充

***REMOVED******REMOVED******REMOVED*** 4. 结构化输出

**Kimi 的输出**：
- 按类别分组
- 已去重
- 清晰的层次结构

**当前系统的输出**：
- 扁平列表
- 需要后续处理才能分组

***REMOVED******REMOVED*** 改进方案

***REMOVED******REMOVED******REMOVED*** 方案1：扩展实体类型（推荐）

在 `EntityType` 枚举中添加新类型：

```python
class EntityType(Enum):
    CHARACTER = "character"  ***REMOVED*** 角色
    ORGANIZATION = "organization"  ***REMOVED*** 组织/机构
    LOCATION = "location"  ***REMOVED*** 地点
    ITEM = "item"  ***REMOVED*** 物品/装备
    CREATURE = "creature"  ***REMOVED*** 生物/妖怪
    CONCEPT = "concept"  ***REMOVED*** 概念/规则
    TIME = "time"  ***REMOVED*** 时间/期限
    SETTING = "setting"  ***REMOVED*** 设定（保留兼容性）
    SYMBOL = "symbol"  ***REMOVED*** 符号（保留兼容性）
```

***REMOVED******REMOVED******REMOVED*** 方案2：改进提取提示词

参考 Kimi 的提取方式，改进提示词：

```python
prompt = f"""请从以下小说章节中提取实体，**按类别分组并去重**。

章节内容：
{text[:2000]}...

请提取以下类型的实体（**必须完整提取所有类型**）：

1. **人物实体（Character）**：人物姓名、称呼、角色身份
   - 示例：林鸦（主角，废楼回收员＋无证驱妖人）
   - 注意：包含角色的身份、职业等关键信息

2. **组织/机构（Organization）**：组织名称、机构名称
   - 示例：白夜当铺（典当"情绪"与肢体的机构）
   - 注意：包含组织的性质和功能

3. **地点实体（Location）**：地点名称、场所、建筑
   - 示例：73层烂尾楼、第七廊桥（旧书集市）
   - 注意：包含地点的特征或用途

4. **物品/装备（Item）**：重要物品、道具、装备
   - 示例：黑鲨·静刃电锯（掺银附魔）
   - 注意：包含物品的特征或属性

5. **生物/妖怪（Creature）**：生物种类、妖怪亚种
   - 示例：鬣狗妖（犬型妖怪，缺尾）
   - 注意：包含生物的特征或分类

6. **概念/规则（Concept）**：规则、法律、概念
   - 示例：当票法（含附件300页）、尾巴债（同类代偿条款3.2）
   - 注意：包含规则的内容或说明

7. **时间/期限（Time）**：时间点、期限、时间范围
   - 示例：三年期（林鸦当票原始期限）、明晚零点（浮空艇升空巡航窗口）
   - 注意：包含时间的含义或用途

**提取要求**：
- 每个实体必须包含：名称、类型、描述（括号内的补充信息）
- 描述应包含实体的关键特征、属性或说明
- 按类型分组输出
- 去重处理

请以 JSON 格式返回，格式如下：
{{
  "entities": [
    {{
      "name": "实体名称",
      "type": "character|organization|location|item|creature|concept|time",
      "description": "实体描述（包含括号内的补充信息）",
      "metadata": {{
        "role": "主角/配角/反派等（仅人物）",
        "category": "具体分类（如'犬型妖怪'）",
        "attributes": ["属性1", "属性2"]
      }}
    }}
  ]
}}
"""
```

***REMOVED******REMOVED******REMOVED*** 方案3：集成 Kimi 到多模型投票系统

如果 Kimi 有 API 接口，可以将其加入多模型投票：

```python
***REMOVED*** 在 MultiModelEntityExtractor 中添加 Kimi
llm_clients = [
    gemini_3_flash,
    deepseek_v3_2,
    kimi_client  ***REMOVED*** 新增
]
```

**优势**：
- 利用 Kimi 的强提取能力
- 通过投票机制提高准确率
- 互补各模型的优势

***REMOVED******REMOVED******REMOVED*** 方案4：改进实体描述格式

在实体提取结果中，要求模型提供更详细的描述：

```python
{
    "name": "林鸦",
    "type": "character",
    "description": "主角，废楼回收员＋无证驱妖人",
    "metadata": {
        "role": "主角",
        "professions": ["废楼回收员", "无证驱妖人"],
        "key_attributes": []
    }
}
```

***REMOVED******REMOVED******REMOVED*** 方案5：后处理增强

在提取后，对实体进行后处理：

1. **分类细化**：根据描述自动细化分类
2. **属性提取**：从描述中提取关键属性
3. **关系识别**：识别实体间的关系
4. **分组输出**：按类型分组，便于查看

***REMOVED******REMOVED*** 实施优先级

***REMOVED******REMOVED******REMOVED*** 高优先级（立即实施）
1. ✅ **改进提取提示词**：参考 Kimi 的提示词格式，要求更详细的描述
2. ✅ **扩展实体类型**：添加 ORGANIZATION, CONCEPT, TIME 等类型

***REMOVED******REMOVED******REMOVED*** 中优先级（后续优化）
3. ⚠️ **集成 Kimi**：如果有 API，加入多模型投票
4. ⚠️ **改进描述格式**：要求模型提供更结构化的描述

***REMOVED******REMOVED******REMOVED*** 低优先级（长期优化）
5. 📋 **后处理增强**：自动分类细化、属性提取等

***REMOVED******REMOVED*** 预期效果

实施后预期：
- ✅ 实体提取覆盖率提升 30-50%
- ✅ 概念、规则、时间等抽象实体不再遗漏
- ✅ 实体描述更详细，包含关键信息
- ✅ 分类更准确，便于后续使用

***REMOVED******REMOVED*** 注意事项

1. **兼容性**：新增实体类型需要保持向后兼容
2. **性能**：更详细的提取可能增加 Token 消耗
3. **准确性**：需要验证新类型的提取准确性
4. **Kimi API**：需要确认是否有可用的 API 接口
