# Memory Genesis 2026 参赛与 Video Demo 指南

本文档整合 **参赛策略、提交要求与视频录制指南**：三赛道对应、Track 1/2/3 对齐与加分项、官方 How to Submit、推荐执行顺序、Video Demo 结构及开关云端记忆对比、提交前自检。

---

## 一、提交要求（官方 How to Submit）

*Note: A submission portal will be available soon. Stay tuned for updates on the competition page.*

**Required**

| Item | Description |
|------|-------------|
| **GitHub Repository** | Public repo with your project code |
| **README.md** | Clear project introduction, setup instructions, and **how EverMemOS is used** |
| **Video Demo** | 3–5 minute video **demonstrating your project and explaining the concept** |

**Optional (Preferred)**

| Item | Description |
|------|-------------|
| **Live Demo** | Deployed application or interactive demo link |

**Submission Checklist**

- [ ] GitHub repository is public and accessible
- [ ] README includes project overview and setup instructions
- [ ] README explains how EverMemOS powers your solution
- [ ] Video demo is 3–5 minutes and **covers functionality + concept**
- [ ] (Optional) Live demo URL included in README

---

## 二、三赛道与 Creator 的对应关系

| 赛道 | 核心要求 | Creator 对应 | 建议主/辅 |
|------|----------|--------------|-----------|
| **Track 1: Agent + Memory** | 构建具有长期、演进记忆的智能体 | **Content Creator Copilot**：记住品牌声音、过往内容、受众反馈的助手 | **主攻** |
| **Track 2: Platform Plugins** | 将 EverMemOS 集成到开发者工作环境（插件/SDK） | 可包装为 **LangChain/LlamaIndex 记忆后端** 或 **CLI 工具** | 辅/加分 |
| **Track 3: OS Infrastructure** | 优化 EverMemOS 平台（检索、提取器、多语言等） | **自定义检索**（UniMem 图谱 + EverMemOS）、**多语言**（中文创作）、**领域提取器**（创作领域） | 辅/加分 |

**结论**：主报 **Track 1 - Content Creator Copilot**，在 README 与视频中顺带体现 Track 2（如“可作 LangChain 记忆后端”）、Track 3（自定义检索/中文/领域记忆）的亮点。

---

## 三、Track 1/2/3 对齐与加分要点

**Track 1（Content Creator Copilot）**  
赛题：*Assistant that remembers your brand voice, past content, and audience feedback.*

| 能力点 | 当前状态 | 建议动作 |
|--------|----------|----------|
| 记住**品牌声音/风格** | semantic_mesh + UniMem 作品内实体与风格 | 项目级风格摘要写入 EverMemOS，续写前检索注入 |
| 记住**过往内容** | 已做：大纲/章节双写 EverMemOS，recall 注入 | 保持；视频中展示续写前召回 |
| 记住**受众反馈** | 未做 | 若有反馈入口可写入 EverMemOS 并检索 |

**Track 2（平台插件）**  
CLI 已实现：`python -m scripts.evermemos_cli get/search/add --user-id xxx`（需在 `src` 下执行）。README 可说明 EverMemOS 封装可复用于 LangChain/LlamaIndex。

**Track 3（基础设施）**  
在 README/视频中强调：**混合检索**（EverMemOS 长期语义 + UniMem/图谱作品内实体）、**中文长篇创作**、领域提取（大纲/章节摘要写入 EverMemOS）。

---

## 四、一句话参赛叙事（供 README/视频用）

> **Creator 创作助手** 是面向 Track 1「Content Creator Copilot」的智能体：用 **EverMemOS** 存储与检索用户的项目级长期记忆（大纲、章节、风格与反馈），用 **UniMem + semantic_mesh** 维护单作品内的实体与情节图谱，实现“长期记忆 + 作品内结构”的混合检索，支持中文长篇创作与跨项目记忆复用。

---

## 五、推荐执行顺序

1. **提交前**
   - 撰写/更新 README：EverMemOS 集成小节（配置、数据流、how EverMemOS is used）、三赛道对应说明。
   - 录制 video_demo（3–5 分钟）：完整创作流程 + 记忆写入与检索 + **开关云端记忆对比**（见下文）。
2. **已实现（可于视频中展示）**
   - CLI：`scripts/evermemos_cli` add/get/search。
   - 前端「云端记忆」区块：记忆列表页底部「云端记忆（EverMemOS）」；无 Key 时显示配置提示。

---

## 六、Video Demo 目标（functionality + concept）

- **Functionality**：演示创作流程（大纲、续写、记忆面板与云端记忆列表）、可选润色/对话。
- **Concept**：说明 **EverMemOS 如何支撑方案**——谁写入（大纲/章节/润色/对话后）、谁检索（规划前、续写前、润色与对话前）、何时调用；混合检索与中文长篇场景。
- **加分**：**开关云端记忆对比**（续写质量/连贯性差异）、云端记忆列表随创作增长。

---

## 七、推荐视频结构（总长约 4 分钟）

| 段落 | 时长 | 内容 |
|------|------|------|
| **开场** | ~20s | 标题 + 一句话：Creator + EverMemOS，Content Creator Copilot；长篇、记忆增强续写与润色。 |
| **主流程录屏** | ~1.5min | 从**新小说**开始：建作品 → 大纲 → **续写 1–2 章**（流式）；打开记忆面板，展示 **云端记忆（EverMemOS）** 列表随续写增加。 |
| **开关云端记忆对比** | ~1–1.5min | **关**：取消勾选「续写时注入云端记忆」→ 续写 → 结果（无云端注入）；**开**：勾选 → 再续写 → 对比前后文/人物一致性，指向「云端记忆」列表说明检索注入。 |
| **收尾** | ~30s | 混合检索（EverMemOS + 作品内图谱）、中文长篇、可选 CLI；感谢 + 仓库/README。 |

---

## 七 A、从一部新小说开始的录屏动线（逐步操作）

按下面顺序操作，便于一气呵成录完主流程；若要做开关对比，在步骤 4 之后接「八、开关云端记忆对比」。

| 步骤 | 操作 | 口播/字幕建议 |
|------|------|----------------|
| **1. 进入创作页** | 打开 Creator 创作页；在「当前作品」处**输入新书名**（如「玄灵大陆的AI科学家」），确保是全新项目。 | 简短说明：从一部新小说开始演示。 |
| **2. 生成大纲** | 模式选 **「大纲」** → 在**下方输入框**里输入**主题/大纲提示词**（与书名是两处：书名定作品 ID，输入框定题材与设定）→ 发送，等待大纲生成完成。 | 可快进或剪掉等待，保留「开始 → 完成」；说明「大纲会写入 EverMemOS，供后续检索」。 |
| **3. 续写第 1～2 章** | 模式选 **「章节」** → 确认「续写时注入云端记忆」**已勾选**（默认）→ 续写第 1 章、第 2 章（流式输出可见）。 | 说明「续写前会从云端召回记忆并注入 prompt；续写后本章摘要写入云端」。 |
| **4. 展示记忆面板** | 打开右侧**记忆面板**，切到列表视图 → 展开 **「云端记忆（EverMemOS）」**，展示已有条数及摘要。 | 说明「随创作进行，云端记忆列表增长；下次续写会检索这些内容」。 |
| **5.（可选）开关对比** | 见 **八、开关云端记忆对比**：取消勾选 → 续写一章 → 再勾选 → 再续写一章，对比两句或列表变化。 | 口播：开/关时续写对前文依赖的差异。 |

**注意**：若后端/前端为本地，录屏前确认 `API_URL` 与后端端口一致；若用 Live Demo 环境，直接访问演示地址即可。

### 示例：充分检验记忆能力的大纲提示词

以下提示词围绕「穿越到玄灵大陆的AI科学家」，刻意包含**多角色、具体数字、专有名词、伏笔与长线设定**，便于续写多章后检验跨章人物、伏笔与长程召回效果；录屏时可直接复制到「大纲」模式输入框使用。

```
题材：玄幻+软科幻。主角林渊，原地球 AI 实验室首席，意外穿越到玄灵大陆，保留一枚仅能充能三次的「因果核」（每次使用会改写局部因果，用尽则永久失效）。大陆有九大灵脉，每脉有一名镇守者；主角所在北境灵脉的镇守者名为苏晚，与林渊在第三章因「灵脉共振」事件结识。要求：前 20 章埋下至少两条伏笔——（1）林渊在实验室的编号 7 号项目与玄灵大陆的「第七层遗言」传说有关联；（2）苏晚身上有一道自小就有的封印，封印解除时会引发大陆级天象。长线设定包括：大陆通用货币为「灵晶」，1 上品灵晶 = 100 中品 = 10000 下品；修炼境界为凝气、筑基、金丹、元婴、化神；林渊尝试用 AI 思维解构修炼体系，在第五卷会提出「灵能可计算性」假说。风格偏严谨与伏笔回收，人物对话要有记忆点（如关键数字、约定、誓言），便于跨章检索验证。
```

**检验点**：续写若干章后，用「跨章人物」「伏笔」「长线设定」三类检索或开关云端记忆对比，可验证对「林渊、苏晚、因果核、第七层遗言、灵晶换算、境界体系」等的前后一致与召回效果。

---

## 八、开关云端记忆对比——具体操作

- **前置**：同一本书已写若干章（例如 ≥3 章），且已配置 `EVERMEMOS_API_KEY`。
- **步骤 1（关）**  
  - 创作页 → 模式「章节」→ **取消勾选**「续写时注入云端记忆（EverMemOS）」→ 续写。  
  - 说明：当前续写**不注入**云端记忆，仅本地大纲 + mesh。展示生成结果。
- **步骤 2（开）**  
  - **勾选**「续写时注入云端记忆」→ 再续写。  
  - 说明：从 EverMemOS 召回该项目记忆并注入 prompt。展示结果；打开右侧 **云端记忆（EverMemOS）** 列表，说明「续写后新章节会写入，下次可被检索」。
- **对比要点（口播或字幕）**：开云端记忆时续写更易保持风格与前文细节；关时仅依赖本地，长篇易丢早期细节。书面对比与三项目（同大纲_开/关、新大纲_关）正文分析见 [因果核_三项目对比.md](因果核_三项目对比.md)。

---

## 九、录屏与剪辑建议

- **分辨率**：1080p，浏览器全屏或固定窗口，避免无关弹窗。
- **节奏**：流式等待可加速或裁剪，保留「开始续写 → 首句出现 → 结尾完成」。
- **字幕/旁白**：关键处加简短字幕（如「关闭云端记忆」「开启云端记忆」）；旁白控制在 3–5 分钟内。
- **对比段落**：先播「关」再播「开」，画面标注「无云端注入」/「云端记忆注入」。

---

## 十、可选加分镜头

- 云端记忆列表：从 0 条 → 续写几章后 N 条。
- 长程召回：≥21 章作品可一句话说明并展示续写。
- CLI：`python -m scripts.evermemos_cli search --user-id <project_id> --query "前文 情节"` 约 10s。
- 润色/对话：选一段润色或问「这本书的主角是谁」，体现记忆使用。

---

## 十一、提交前自检（对齐官方 Submission Checklist）

- [ ] 视频时长 **3–5 分钟**。
- [ ] **Covers functionality**：完整创作流程（至少含续写），出现「云端记忆（EverMemOS）」列表或写入/检索的直观展示。
- [ ] **Covers concept**：说明 EverMemOS 在方案中的角色（谁写入、谁检索、何时调用）。
- [ ] **建议**：包含开关云端记忆的对比（关 → 开）。
- [ ] 标题或结尾包含项目名、EverMemOS、Memory Genesis 2026。
- [ ] （可选）Live Demo URL 在 README 或视频描述中注明。

---

## 十二、视频录制前检查（go/no-go）

录屏前建议逐项确认，避免中途断线或界面不符：

- [ ] **后端**：`src` 下 `python api_flask.py` 已启动，端口与前端 `API_URL` 一致（或使用 Live Demo 环境则无需本地后端）
- [ ] **前端**：创作页可正常打开，模式切换（大纲/章节/润色/对话）与「续写时注入云端记忆」勾选可见
- [ ] **云端记忆**：若演示开关对比，已配置 `EVERMEMOS_API_KEY` 且该项目已有若干章（建议 ≥3 章），记忆面板「云端记忆（EverMemOS）」可拉取列表
- [ ] **浏览器**：无无关弹窗、扩展通知；分辨率建议 1080p，可提前关勿扰
- [ ] **素材**：同一本书已写 5–10 章时，开关对比效果更明显；可提前跑一次续写确认流式输出正常

---

## 十三、与「继续改进」的衔接

- **为 video_demo 服务**：续写前「续写时注入云端记忆」开关与记忆面板「云端记忆」列表已实现；可事先用同一本书写满 5–10 章再录，对比更明显。
- **改进方向**（见 [ROADMAP.md](ROADMAP.md)、[EVERMEMOS_INTEGRATION.md](EVERMEMOS_INTEGRATION.md)）：回归测试、可观测；README 已含概览、setup、How EverMemOS is used 与 Live Demo 链接，便于评委查看。
