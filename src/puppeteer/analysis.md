***REMOVED*** Puppeteer 代码结构深度分析

> 基于论文 "Multi-Agent Collaboration via Evolving Orchestration" 的实现代码分析

***REMOVED******REMOVED*** 📋 目录结构概览

```
puppeteer/
├── main.py                 ***REMOVED*** 主入口
├── agent/                  ***REMOVED*** 智能体模块
│   ├── agent.py           ***REMOVED*** 抽象基类
│   ├── reasoning_agent.py ***REMOVED*** 推理智能体实现
│   ├── agent_info/        ***REMOVED*** 智能体信息管理
│   └── register/          ***REMOVED*** 智能体注册机制
├── inference/             ***REMOVED*** 推理与编排核心
│   ├── base/              ***REMOVED*** 基础图结构
│   ├── graph/             ***REMOVED*** Agent图与Action图
│   ├── policy/             ***REMOVED*** 策略网络（RL）
│   └── reasoning/          ***REMOVED*** 推理路径管理
├── model/                 ***REMOVED*** 模型管理
│   ├── model_config.py    ***REMOVED*** 模型配置
│   ├── query_manager.py   ***REMOVED*** 查询管理
│   └── embedding.py       ***REMOVED*** Embedding/状态表示
├── tools/                 ***REMOVED*** 工具系统
│   ├── base/              ***REMOVED*** 工具基类
│   ├── web_search.py      ***REMOVED*** 网络搜索
│   ├── code_interpreter.py ***REMOVED*** 代码执行
│   └── file_read.py       ***REMOVED*** 文件读取
├── tasks/                 ***REMOVED*** 任务定义
│   ├── runner.py         ***REMOVED*** 任务运行器
│   ├── evaluator.py      ***REMOVED*** 评估器
│   └── [task_files]      ***REMOVED*** 具体任务实现
├── config/                ***REMOVED*** 配置文件
│   ├── global.yaml       ***REMOVED*** 全局配置
│   └── policy.json       ***REMOVED*** 策略配置
└── prompts/              ***REMOVED*** 提示词模板
```

---

***REMOVED******REMOVED*** 🏗️ 核心架构设计

***REMOVED******REMOVED******REMOVED*** 1. 整体架构模式

**设计模式：**
- **中心化编排器（Puppeteer）**：动态选择下一个执行的 Agent
- **多路径并行推理**：支持多个推理路径同时探索
- **强化学习优化**：使用 REINFORCE 算法训练编排策略
- **图结构表示**：Agent 图和 Action 图记录协作模式

**核心流程：**
```
任务输入 → 初始化推理路径 → 策略选择 Agent → Agent 执行动作 → 
状态更新 → 策略选择下一个 Agent → ... → 终止 → 评估奖励 → 策略更新
```

---

***REMOVED******REMOVED*** 🔍 模块详细分析

***REMOVED******REMOVED******REMOVED*** 2. Agent 模块 (`agent/`)

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.1 核心类层次

**`Agent` (抽象基类)**
- **职责**：定义所有 Agent 的通用接口和行为
- **关键属性**：
  - `role`: Agent 角色名称
  - `role_prompt`: 角色提示词
  - `dialog_history`: 对话历史
  - `actions`: 可用动作列表
  - `query_func`: LLM 查询函数
- **关键方法**：
  - `activate()`: 激活 Agent，准备执行任务
  - `deactivate()`: 停用 Agent，保存状态
  - `take_action()`: 执行动作（抽象方法）
  - `_execute_action()`: 执行具体动作（抽象方法）
  - `_reasoning_operation()`: 推理操作（抽象方法）
  - `_tool_operation()`: 工具操作（抽象方法）

**`Reasoning_Agent` (具体实现)**
- **继承**：`Agent`
- **职责**：实现具体的推理 Agent 逻辑
- **核心功能**：
  1. **动作选择**：根据当前状态选择动作（推理类或工具类）
  2. **动作执行**：
     - 推理动作：直接调用 LLM 进行推理
     - 工具动作：调用外部工具（搜索、代码执行等）
  3. **结果处理**：提取最终答案，更新全局状态

**关键代码片段：**
```python
***REMOVED*** agent/reasoning_agent.py
def take_action(self, global_info, external_tools_enabled=True):
    ***REMOVED*** 1. 判断动作类型（终止/工具/推理）
    if self.actions[0] in TERMINATION_ACTION_LIST:
        ***REMOVED*** 终止动作
    elif self.actions[0] in TOOL_ACTION_LIST:
        ***REMOVED*** 工具动作：需要生成参数
        action_json = self._format_tool_action(...)
    elif self.actions[0] in REASONING_ACTION_LIST:
        ***REMOVED*** 推理动作：直接执行
        action_json = {"action": self.actions[0], "parameter": ""}
    
    ***REMOVED*** 2. 执行动作
    step_data, answer, flag, tokens = self._execute_action(action_json, global_info)
    
    ***REMOVED*** 3. 构建 Action 对象并返回
    current_action = self._build_current_action(...)
    return current_action, terminated
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.2 Agent 类型分类

**推理类 Agent** (`REASONING_ACTION_LIST`)
- `reasoning`: 逻辑推理
- `critique`: 评估和批判
- `question`: 生成澄清问题
- `reflect`: 反思分析
- `conclude`: 生成结论
- `summarize`: 总结信息
- `planning`: 制定计划
- `modify`: 修正错误

**工具类 Agent** (`TOOL_ACTION_LIST`)
- `search_arxiv`: 搜索 arXiv 论文
- `search_bing`: Bing 搜索
- `access_website`: 访问网站
- `run_python`: 执行 Python 代码
- `read_file`: 读取文件

**终止类 Agent** (`TERMINATION_ACTION_LIST`)
- `terminate`: 终止推理过程

***REMOVED******REMOVED******REMOVED******REMOVED*** 2.3 Agent 注册机制

**`agent/register/register.py`**
- **全局注册表**：`agent_global_registry`
- **功能**：
  - 从 `personas.jsonl` 加载 Agent 定义
  - 为每个 Agent 分配唯一索引和哈希值
  - 管理 Agent 生命周期（创建、重置、获取）

---

***REMOVED******REMOVED******REMOVED*** 3. Inference 模块 (`inference/`)

***REMOVED******REMOVED******REMOVED******REMOVED*** 3.1 推理核心：`GraphReasoning`

**`inference/reasoning/reasoning.py`**

**核心职责**：
- 管理多个并行推理路径
- 协调策略网络选择 Agent
- 处理路径分裂和终止
- 聚合最终答案

**关键方法：**

```python
class GraphReasoning:
    def __init__(self, task, graph, env=None):
        self.task = task                    ***REMOVED*** 任务定义
        self.agent_graph = graph            ***REMOVED*** Agent 图
        self.action_graph = ActionGraph()   ***REMOVED*** Action 图
        self.reasoning_paths = []           ***REMOVED*** 推理路径列表
        self.policy = ContinuousREINFORCE(...)  ***REMOVED*** 策略网络
    
    def start(self, save_data):
        """初始化推理路径"""
        ***REMOVED*** 1. 策略选择初始 Agent
        matches = self.policy.forward(global_info)
        
        ***REMOVED*** 2. 为每个选中的 Agent 创建推理路径
        for match in matches:
            agent = agent_global_registry.get_agent_from_idx(match)
            reasoning_path = GraphReasoningPath(...)
            self.reasoning_paths.append(reasoning_path)
    
    def step(self):
        """执行一步推理"""
        ***REMOVED*** 1. 每个路径执行一步
        for reasoning_path in self.reasoning_paths:
            reasoning_path.step()
        
        ***REMOVED*** 2. 处理路径分裂
        for reasoning_path in self.reasoning_paths:
            if reasoning_path.state == ReasoningState.SPLITING:
                split_paths = reasoning_path.split(...)
                self.reasoning_paths.extend(split_paths)
        
        ***REMOVED*** 3. 更新图结构
        self.update_graph()
    
    def finalize(self):
        """结束推理，计算奖励，更新策略"""
        ***REMOVED*** 1. 聚合答案
        for reasoning_path in self.reasoning_paths:
            aggregated_answer = self.aggregate_answers(...)
            
            ***REMOVED*** 2. 计算奖励
            reward = evaluator.check(aggregated_answer, ground_truth)
            
            ***REMOVED*** 3. 构建 transition
            transition = {
                'state': reasoning_path.global_info.workflow.state,
                'reward': reward,
                'action': None,
                'next_state': None,
                'done': True,
                'path_id': idx
            }
            
            ***REMOVED*** 4. 更新策略
            self.policy.finalize_task(transition, reasoning_path.global_info)
        
        ***REMOVED*** 5. 策略网络更新
        self.policy.update()
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 3.2 推理路径：`GraphReasoningPath`

**`inference/reasoning/path.py`**

**状态机：**
```python
class ReasoningState(Enum):
    INITIALIZED = 1    ***REMOVED*** 已初始化
    SPLITING = 2       ***REMOVED*** 正在分裂
    ANSWERING = 3      ***REMOVED*** 正在回答
    FINALIZING = 4     ***REMOVED*** 正在结束
    DISCARDING = 5     ***REMOVED*** 已丢弃
    AGGREGATING = 6    ***REMOVED*** 正在聚合
```

**核心流程：**
```python
def step(self):
    ***REMOVED*** 1. 当前 Agent 执行动作
    current_action, terminated = self.current_agent.take_action(...)
    
    ***REMOVED*** 2. 更新全局信息
    self.update_global_info(current_action)
    
    ***REMOVED*** 3. 添加到 Action 图
    self.action_graph.add_action(node_id, current_action.to_dict(), ...)
    
    ***REMOVED*** 4. 判断终止条件
    if terminated or len(self.agent_sequence) >= self.max_step_num:
        self.state = ReasoningState.FINALIZING
        return
    
    ***REMOVED*** 5. 策略选择下一个 Agent
    next_agents_idx = self.policy.forward(self.global_info)
    self.next_agents = [agent_global_registry.get_agent_from_idx(idx) 
                        for idx in next_agents_idx]
    
    ***REMOVED*** 6. 处理多个候选 Agent
    if len(self.next_agents) == 1:
        ***REMOVED*** 单个 Agent：直接继续
        self.current_agent = self.next_agents[0]
        self.agent_sequence.append(self.current_agent.unique_identifier)
        self.state = ReasoningState.ANSWERING
    else:
        ***REMOVED*** 多个 Agent：分裂路径
        self.state = ReasoningState.SPLITING
```

**路径分裂机制：**
- 当策略选择多个 Agent 时，创建多个并行路径
- 每个路径共享相同的初始状态和 Agent 序列
- 后续独立执行，形成不同的推理轨迹

***REMOVED******REMOVED******REMOVED******REMOVED*** 3.3 策略网络：`ContinuousREINFORCE`

**`inference/policy/REINFORCE_continuous.py`**

**核心组件：**

1. **状态表示** (`RewardModelTokenRepresentation`)
   - 使用 Reward Model 的最后一个 token 的 hidden state
   - 输入：当前任务状态（问题 + 历史动作 + 结果）
   - 输出：状态向量（用于策略网络输入）

2. **策略网络** (`MLP_PolicyNetwork`)
   - 结构：`input_dim → 512 → 128 → 32 → output_dim`
   - 激活函数：ReLU + Softmax
   - 输出：每个 Agent 的选择概率

3. **REINFORCE 算法**
   ```python
   def forward(self, global_info):
       ***REMOVED*** 1. 获取状态表示
       state_embedding = self.state_representation.get_embedding(global_info)
       
       ***REMOVED*** 2. 策略网络输出概率
       probs = self.policy_network(state_embedding)
       
       ***REMOVED*** 3. 采样（训练）或选择最大（推理）
       if self.training:
           action_indices = self._sample(probs, self.next_num_agents)
       else:
           action_indices = self._select_top_k(probs, self.next_num_agents)
       
       return action_indices
   
   def finalize_task(self, transition, global_info):
       """任务结束时，记录 transition 用于训练"""
       self.current_trajectories.append({
           'states': [...],
           'actions': [...],
           'rewards': transition['reward'],
           'path_id': transition['path_id']
       })
   
   def update(self):
       """使用 REINFORCE 更新策略网络"""
       ***REMOVED*** 1. 计算每个轨迹的回报
       returns = self._compute_returns(trajectories)
       
       ***REMOVED*** 2. 计算策略梯度
       policy_loss = self._compute_policy_loss(returns, trajectories)
       
       ***REMOVED*** 3. 反向传播
       optimizer.step()
   ```

**LLM Prior 机制：**
- 可选：使用 LLM 生成 Agent 选择的先验分布
- 与策略网络输出结合，形成最终概率分布
- 帮助策略网络学习更好的选择模式

***REMOVED******REMOVED******REMOVED******REMOVED*** 3.4 图结构

**Agent 图** (`inference/graph/agent_graph.py`)
- **节点**：Agent 实例
- **边**：Agent 之间的协作关系（从 predecessor 到 successor）
- **用途**：
  - 记录 Agent 协作模式
  - 可视化推理过程
  - 分析协作拓扑结构

**Action 图** (`inference/graph/action_graph.py`)
- **节点**：Action 实例
- **边**：Action 之间的依赖关系
- **用途**：
  - 记录动作执行顺序
  - 支持并行执行（无依赖的动作可并行）
  - 可视化推理路径

---

***REMOVED******REMOVED******REMOVED*** 4. Model 模块 (`model/`)

***REMOVED******REMOVED******REMOVED******REMOVED*** 4.1 模型配置 (`model_config.py`)

**支持的模型：**
- `gpt-3.5`: OpenAI GPT-3.5 Turbo
- `gpt-4o`: OpenAI GPT-4o
- `qwen-2.5-14b`: 本地部署的 Qwen 模型

**配置结构：**
```python
@dataclass
class ModelConfig:
    name: str              ***REMOVED*** 模型名称
    function_name: str     ***REMOVED*** 查询函数名
    api_model_name: str   ***REMOVED*** API 模型名
    provider: str         ***REMOVED*** 提供商（openai/local）
    max_tokens: int       ***REMOVED*** 最大 token 数
    model_size: int       ***REMOVED*** 模型大小（用于成本计算）
    temperature: float    ***REMOVED*** 温度参数
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 4.2 查询管理 (`query_manager.py`)

**功能：**
- 统一管理不同模型的查询接口
- 处理 API 调用、重试、错误处理
- 支持 OpenAI API 和本地模型

***REMOVED******REMOVED******REMOVED******REMOVED*** 4.3 状态表示 (`embedding.py`)

**`RewardModelTokenRepresentation`**
- **输入**：任务状态（问题 + 历史动作序列）
- **处理**：使用 Reward Model 编码状态
- **输出**：状态向量（用于策略网络）

---

***REMOVED******REMOVED******REMOVED*** 5. Tools 模块 (`tools/`)

***REMOVED******REMOVED******REMOVED******REMOVED*** 5.1 工具基类 (`base/base_tool.py`)

**`Tool` (抽象基类)**
- **关键特性**：
  - 超时控制
  - 错误处理
  - 统一执行接口

***REMOVED******REMOVED******REMOVED******REMOVED*** 5.2 具体工具实现

**`web_search.py`**
- Bing 搜索
- arXiv 搜索
- 网站访问

**`code_interpreter.py`**
- Python 代码执行
- 沙箱环境
- 结果提取

**`file_read.py`**
- 文件读取
- 内容提取

**工具注册机制** (`base/register.py`)
- 全局工具注册表：`global_tool_registry`
- 统一工具调用接口

---

***REMOVED******REMOVED******REMOVED*** 6. Tasks 模块 (`tasks/`)

***REMOVED******REMOVED******REMOVED******REMOVED*** 6.1 任务运行器 (`runner.py`)

**`BenchmarkRunner`**
- **职责**：
  - 初始化推理系统
  - 运行推理过程
  - 管理任务生命周期

**核心方法：**
```python
def run_reasoning(self, data_item):
    ***REMOVED*** 1. 设置推理系统
    reasoning, graph = self.setup_reasoning(data_item)
    
    ***REMOVED*** 2. 启动推理
    reasoning.start(self.save_state)
    
    ***REMOVED*** 3. 执行 N 步推理
    final_ans, _ = reasoning.n_step(self.max_step_num)
    
    ***REMOVED*** 4. 可视化
    reasoning.visualize_path()
    reasoning.visualize_graph()
    
    return final_ans
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 6.2 评估器 (`evaluator.py`)

**`BenchmarkEvaluator`**
- **功能**：
  - 评估答案正确性
  - 提取答案（选择题、数学题等）
  - 计算奖励信号

**支持的任务类型：**
- MMLU-Pro: 多选题
- GSM-Hard: 数学题
- SRDD: 软件需求开发
- Creative Writing: 创意写作

***REMOVED******REMOVED******REMOVED******REMOVED*** 6.3 具体任务实现

**`mmlu_pro.py`, `gsm_hard.py`, `srdd.py`, `creative_writing.py`**
- 每个任务定义自己的数据加载和运行逻辑
- 统一的接口：`run(runner, evaluator, results_dir, mode, data_limit)`

---

***REMOVED******REMOVED******REMOVED*** 7. 配置系统

***REMOVED******REMOVED******REMOVED******REMOVED*** 7.1 全局配置 (`config/global.yaml`)

**关键配置项：**
```yaml
***REMOVED*** API 配置
api_keys:
    openai_api_key: ""
    openai_base_url: "https://api.openai.com/v1/"
    bing_api_key: ""

***REMOVED*** 图探索参数
graph:
    max_parallel_paths: 4  ***REMOVED*** 最大并行路径数
    max_step_num: 5       ***REMOVED*** 每个路径最大步数

***REMOVED*** 外部工具
external_tools_enabled: True

***REMOVED*** 文件路径
file_path:
    root_file_path: ./data
```

***REMOVED******REMOVED******REMOVED******REMOVED*** 7.2 策略配置 (`config/policy.json`)

**关键参数：**
```json
{
    "training": {
        "learning_rate": 0.0001,
        "gamma": 0.99,           // 折扣因子
        "sample_size": 1
    },
    "agent": {
        "max_num_agents": 3,     // 最大 Agent 数
        "next_num_agents": 3,    // 下一步选择的 Agent 数
        "max_path": 6            // 最大路径长度
    },
    "cost": {
        "scale": 0.1,            // 成本缩放因子
        "growth_rate": 1.0        // 成本增长率
    }
}
```

---

***REMOVED******REMOVED*** 🔄 完整执行流程

***REMOVED******REMOVED******REMOVED*** 8. 端到端流程

```
1. 初始化阶段
   ├── 加载配置文件 (global.yaml, policy.json)
   ├── 注册所有 Agent (从 personas.jsonl)
   ├── 创建 Agent 图
   ├── 初始化策略网络
   └── 创建推理系统 (GraphReasoning)

2. 启动阶段 (reasoning.start())
   ├── 策略选择初始 Agent
   ├── 为每个选中的 Agent 创建推理路径
   └── 初始化全局信息 (GlobalInfo)

3. 推理循环 (reasoning.step(), 重复 N 次)
   ├── 对每个推理路径：
   │   ├── 当前 Agent 执行动作
   │   ├── 更新全局状态
   │   ├── 添加到 Action 图
   │   ├── 策略选择下一个 Agent
   │   └── 处理路径分裂（如果多个候选）
   ├── 处理路径分裂
   ├── 更新 Agent 图
   └── 检查终止条件

4. 结束阶段 (reasoning.finalize())
   ├── 聚合每个路径的答案
   ├── 评估答案（计算奖励）
   ├── 记录 transition
   ├── 更新策略网络（REINFORCE）
   └── 返回最终答案

5. 可视化
   ├── 可视化推理路径
   ├── 可视化 Agent 图
   └── 可视化 Action 图
```

---

***REMOVED******REMOVED*** 🎯 关键设计特点

***REMOVED******REMOVED******REMOVED*** 9. 核心创新点

1. **动态编排**
   - 策略网络根据当前状态动态选择 Agent
   - 不依赖固定的流水线或图结构
   - 支持自适应调整

2. **并行路径探索**
   - 支持多个推理路径同时执行
   - 路径可以分裂和合并
   - 提高探索效率

3. **强化学习优化**
   - 使用 REINFORCE 算法训练策略
   - 奖励 = 任务完成质量 - λ × 成本
   - 自动学习高效的协作模式

4. **图结构记录**
   - Agent 图记录协作模式
   - Action 图记录执行顺序
   - 支持拓扑结构分析

5. **状态表示**
   - 使用 Reward Model 编码状态
   - 捕获任务进展和上下文
   - 为策略网络提供有效输入

---

***REMOVED******REMOVED*** 📊 数据流

***REMOVED******REMOVED******REMOVED*** 10. 状态流转

```
任务输入 (task)
    ↓
GlobalInfo (全局信息)
    ├── task: 任务定义
    ├── workflow: 动作序列
    ├── state_answers: 状态答案
    ├── code_path: 代码路径
    └── logger: 日志记录器
    ↓
策略网络 (Policy)
    ├── 输入: 状态表示 (Reward Model embedding)
    ├── 输出: Agent 选择概率
    └── 采样: 选择下一个 Agent
    ↓
Agent 执行
    ├── 推理动作 → LLM 生成
    └── 工具动作 → 工具执行
    ↓
Action 对象
    ├── action: 动作定义
    ├── result: 执行结果
    ├── cost: 成本
    └── tokens: Token 消耗
    ↓
更新 GlobalInfo
    ├── workflow.add_action()
    ├── state_answers.append()
    └── code_path 更新
    ↓
循环或终止
```

---

***REMOVED******REMOVED*** 🔧 扩展点

***REMOVED******REMOVED******REMOVED*** 11. 如何扩展系统

***REMOVED******REMOVED******REMOVED******REMOVED*** 11.1 添加新 Agent
1. 在 `personas.jsonl` 中定义新 Agent
2. 指定 `role`, `role_prompt`, `actions`
3. 系统自动注册

***REMOVED******REMOVED******REMOVED******REMOVED*** 11.2 添加新动作
1. 在 `agent/agent_info/actions.py` 中添加动作名
2. 在 `prompts/general/actions_reasoning.jsonl` 或 `actions_external_tools.jsonl` 中添加提示词
3. 在 `Reasoning_Agent` 中实现动作逻辑（如需要）

***REMOVED******REMOVED******REMOVED******REMOVED*** 11.3 添加新工具
1. 继承 `Tool` 基类
2. 实现 `execute()` 方法
3. 在 `tools/base/register.py` 中注册

***REMOVED******REMOVED******REMOVED******REMOVED*** 11.4 添加新任务
1. 在 `tasks/` 中创建新任务文件
2. 实现 `run(runner, evaluator, results_dir, mode, data_limit)` 函数
3. 在 `main.py` 中注册任务

***REMOVED******REMOVED******REMOVED******REMOVED*** 11.5 修改策略网络
1. 修改 `MLP_PolicyNetwork` 结构
2. 或实现新的策略网络类
3. 在 `ContinuousREINFORCE` 中使用

---

***REMOVED******REMOVED*** 📈 性能优化建议

***REMOVED******REMOVED******REMOVED*** 12. 优化方向

1. **并行化**
   - 多个推理路径可以真正并行执行
   - 工具调用可以异步执行

2. **缓存机制**
   - 缓存 LLM 查询结果
   - 缓存工具执行结果

3. **路径剪枝**
   - 早期终止低质量路径
   - 动态调整并行路径数

4. **状态压缩**
   - 压缩历史状态表示
   - 只保留关键信息

5. **模型优化**
   - 使用更小的 Reward Model
   - 量化策略网络

---

***REMOVED******REMOVED*** 🐛 潜在问题与改进

***REMOVED******REMOVED******REMOVED*** 13. 已知限制

1. **状态表示维度**
   - 当前使用 Reward Model 的 hidden state
   - 可能无法完全捕获复杂状态

2. **路径管理**
   - 路径分裂可能导致资源消耗增加
   - 需要更好的路径选择策略

3. **奖励设计**
   - 当前奖励函数较简单
   - 可以设计更细粒度的奖励

4. **训练效率**
   - REINFORCE 算法方差较大
   - 可以尝试 Actor-Critic 等方法

---

***REMOVED******REMOVED*** 📚 相关文件索引

***REMOVED******REMOVED******REMOVED*** 14. 关键文件清单

**核心文件：**
- `main.py`: 主入口
- `inference/reasoning/reasoning.py`: 推理核心
- `inference/policy/REINFORCE_continuous.py`: 策略网络
- `agent/reasoning_agent.py`: Agent 实现
- `tasks/runner.py`: 任务运行器

**配置文件：**
- `config/global.yaml`: 全局配置
- `config/policy.json`: 策略配置
- `personas/personas.jsonl`: Agent 定义

**工具文件：**
- `tools/web_search.py`: 网络搜索
- `tools/code_interpreter.py`: 代码执行
- `tools/file_read.py`: 文件读取

**模型文件：**
- `model/model_config.py`: 模型配置
- `model/query_manager.py`: 查询管理
- `model/embedding.py`: 状态表示

---

***REMOVED******REMOVED*** 🎓 总结

Puppeteer 实现了一个**基于强化学习的动态多智能体协作框架**，核心特点包括：

1. **动态编排**：策略网络根据状态动态选择 Agent
2. **并行探索**：支持多个推理路径同时执行
3. **强化学习**：使用 REINFORCE 优化协作策略
4. **图结构**：记录和分析协作模式
5. **模块化设计**：易于扩展和定制

该框架为构建更强大的多智能体系统提供了坚实的基础，可以在此基础上：
- 集成更先进的 RL 算法（如 PPO、A3C）
- 添加更复杂的奖励设计
- 支持更多类型的 Agent 和工具
- 优化状态表示和策略网络结构

---

*分析完成时间：2025年1月*
*基于代码版本：Puppeteer (NeurIPS 2025)*

