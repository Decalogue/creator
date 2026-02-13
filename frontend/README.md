# 创想AI 前端

基于 Umi 4 + React + Ant Design 的 AI 创作助手前端应用。

## 页面结构

| 路径 | 组件 | 说明 |
|------|------|------|
| `/` | `home/intro` | 主页：Hero、工作流、记忆系统、CTA |
| `/creator` | `home/creator` | 创作助手主界面 |
| `/ai` | `home/ai` | AI 对话 |

## 主要组件

- **IntroFooter**：主页页脚，含品牌、联系方式、链接、订阅区
- **WorkflowGraph**：工作流编排可视化。`variant="creation"` 展示创作流程（构思→记忆召回(跨章人物、伏笔、长线设定)→续写→质检⇄重写→实体提取→记忆入库），`variant="research"` 展示通用研究流程
- **MemoryGraphThree**：3D 记忆图谱
- **OrchestrationFlow**：编排流程展示

## 主题

- `INTRO_THEME`：主页亮色主题（白底、品牌红橙）
- `CREATOR_THEME`：创作助手深色主题（指挥中心风格）

## 联系方式（页脚）

- 邮箱：decalogue80@gmail.com
- 电话：13661445290
- 地址：上海市

## 开发

```bash
pnpm install
pnpm dev
```

## 构建

```bash
pnpm build
```
