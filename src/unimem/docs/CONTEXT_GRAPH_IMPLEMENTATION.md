# Context Graph 改进实施总结

## 实施时间
2026-01-09

## 已完成的改进

### ✅ 1. Memory类增强 - 添加决策痕迹字段

**文件**: `memory_types.py`

**改动**:
- 添加 `reasoning: Optional[str] = None` - 存储"为什么"（决策理由）
- 添加 `decision_trace: Optional[Dict[str, Any]] = None` - 存储决策痕迹（输入-规则-异常-审批-输出）
- 更新 `to_dict()` 和 `from_dict()` 方法支持新字段
- 添加字段验证逻辑

### ✅ 2. REFLECT提示词增强 - 明确提取"为什么"

**文件**: `adapters/operation_adapter.py`

**改动**:
- 增强 `_build_reflect_prompt`，明确要求：
  - 重点说明"为什么"（决策理由、推理过程、依据的先例或规则）
  - 对于新观点，说明**为什么**持有这个观点
  - 对于新经验，明确说明：是什么、为什么、如何应用
  - 对于每个重要决策，明确回答：为什么选择这个方案、基于什么先例、遇到什么异常
- 新增 `_extract_reasoning_from_text` 方法：
  - 从文本中提取"为什么"
  - 识别包含"为什么"、"因为"、"基于"等关键词的句子
  - 使用LLM进一步提炼决策理由
- 更新 `_extract_experiences` 方法：
  - 在创建经验记忆时提取并存储 `reasoning` 字段
  - 支持显式和隐式经验提取

### ✅ 3. Neo4j存储增强 - 支持reasoning和decision_trace

**文件**: `neo4j.py`

**改动**:
- `create_memory`: 
  - 提取 `reasoning` 和 `decision_trace` 字段
  - 将 `decision_trace` 保存为JSON字符串
  - 在节点中存储这两个字段
- `update_memory`:
  - 更新 `reasoning` 和 `decision_trace` 字段
- `get_memory`:
  - 读取 `reasoning` 和 `decision_trace` 字段
  - 解析 `decision_trace` JSON字符串

### ✅ 4. RETAIN方法增强 - 捕获决策痕迹

**文件**: `core.py`

**改动**:
- 在 `retain` 方法中，从 `context.metadata` 提取决策相关信息：
  - `inputs`: 输入数据
  - `rules`: 应用的规则
  - `exceptions`: 异常处理
  - `approvals`: 审批流程
- 构建 `decision_trace` 字典，包含完整决策上下文
- 提取 `reasoning` 从 `context.metadata`
- 在创建 Memory 对象时传入 `reasoning` 和 `decision_trace`

## 使用方式

### 在RETAIN时捕获决策痕迹

```python
from unimem import UniMem
from unimem.memory_types import Experience, Context

unimem = UniMem(config)

# 创建经验，包含决策上下文
experience = Experience(
    content="生成视频脚本：电商口红推广",
    timestamp=datetime.now()
)

# 在context中提供决策痕迹
context = Context(
    metadata={
        "source": "video_script",
        "inputs": ["用户需求文档", "历史脚本", "平台规则"],
        "rules": ["抖音3秒原则", "电商转化率要求"],
        "exceptions": ["特殊节假日营销"],
        "approvals": ["产品经理审批"],
        "reasoning": "基于用户反馈历史，选择突出持久度的卖点，因为这是该产品最受关注的特性"
    }
)

# 存储记忆（会自动捕获决策痕迹）
memory = unimem.retain(experience, context)
```

### 在REFLECT时提取"为什么"

REFLECT操作会自动：
1. 从LLM回答中提取"为什么"信息
2. 将reasoning存储到经验记忆中
3. 形成可搜索的决策理由

## 下一步

### 待实施功能（P1优先级）

1. **先例搜索功能**
   - 基于决策上下文（inputs, rules, exceptions）搜索相似先例
   - 实现 `search_precedents` 方法

2. **决策事件节点**
   - 在Neo4j中创建DecisionEvent节点
   - 连接相关实体和记忆
   - 形成完整的决策图谱

3. **跨系统决策上下文**
   - 支持多系统、多场景的决策痕迹捕获
   - 建立跨系统的记忆关联

## 测试建议

1. 测试reasoning字段的提取和存储
2. 测试decision_trace的完整性
3. 测试REFLECT时reasoning的自动提取
4. 验证Neo4j中reasoning和decision_trace字段的查询
