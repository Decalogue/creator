***REMOVED*** 基于多智能体动态编排与记忆系统的创作助手


***REMOVED******REMOVED*** 方案
多智能体动态编排 + 记忆系统 + 强化学习
超越死板的流水线结构，让AI像导演一样动态选人、即兴组局，最终进化出比人类设计更优秀、更高效、更省钱的环状协作模式。

```
任务输入 → 编排层 Puppeteer / ReAct + 创作层 Agents + 记忆系统 UniMem + 评估反馈 + 策略优化
```

***REMOVED******REMOVED******REMOVED*** 编排层-Puppeteer / ReAct

***REMOVED******REMOVED******REMOVED*** 创作层-Agents

***REMOVED******REMOVED******REMOVED*** 记忆系统-UniMem

***REMOVED******REMOVED******REMOVED*** 关键特性

- **动态编排**：根据状态实时选择 Agent，不依赖固定流程
- **自适应学习**：通过强化学习优化协作模式
- **环状协作**：自动涌现出"反复打磨"的协作模式
- **记忆管理**：智能压缩、更新、重组记忆
- **成本优化**：平衡质量与成本，自动学习高效策略

***REMOVED******REMOVED******REMOVED*** 研发路线图

结合当前 Agent 与 Memory 领域发展，各阶段优先级与落地顺序见 **[docs/ROADMAP.md](docs/ROADMAP.md)**：  
闭环打通（创作 API + 记忆/图谱 API + 前端）→ 编排可观测 & UniMem 贯通 → Agent/Memory 升级 → 稳定性与成本。

***REMOVED******REMOVED******REMOVED*** 快速定位

| 要改什么 | 主要看哪里 |
|----------|------------|
| 创作逻辑（大纲/续写/润色/对话） | `src/api/`、`src/novel_creation/`（ReactNovelCreator） |
| 记忆与图谱 API、UniMem 对接 | `src/api/memory_handlers.py`、`src/unimem/` |
| 编排事件与流式推送 | `src/api/orchestration_events.py`、`src/api_flask.py`（/api/creator/stream） |
| 前端创作页与记忆面板 | `frontend/src/pages/home/creator.tsx` |

更多模块说明与主路径/支线划分见 **[src/README.md](src/README.md)**；工程原则见 **[Instructions/工程原则.md](Instructions/工程原则.md)**；路线图与阶段规划见 **[docs/ROADMAP.md](docs/ROADMAP.md)**；调研论文（Memory/Agent）见 **[docs/article.md](docs/article.md)**。

***REMOVED******REMOVED******REMOVED*** 运行与故障排查

- **「无法连接后端（network error）」但后端已生成 novel_plan.json**  
  说明请求已到达后端且创作已完成，但浏览器在等待流式响应时连接被断开。常见原因：**反向代理/网关读超时**（如 Nginx 默认 60s）短于创作耗时（数分钟）。  
  - **处理**：若前面有 Nginx 等代理，对该流式接口调大读超时，例如 `proxy_read_timeout 300s;` 或更长。  
  - 服务端已对 `/api/creator/stream` 每 30 秒发送 SSE 心跳（`: keepalive`），可减少因“空闲”被断开的概率，但总耗时若超过代理配置的读超时仍会断开。
