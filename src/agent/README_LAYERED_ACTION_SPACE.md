***REMOVED*** 分层行动空间使用指南

***REMOVED******REMOVED*** 概述

实现了 Manus 风格的三层行动空间架构，解决工具系统扁平化的问题：
- **L1**: 原子函数调用（固定、正交，对 KV Cache 友好）
- **L2**: 沙盒工具（预装在系统中，通过 shell 动态交互）
- **L3**: 软件包与 API（编写 Python 脚本调用 API）

***REMOVED******REMOVED*** L1: 原子函数调用（Atomic Function Calling）

***REMOVED******REMOVED******REMOVED*** 核心特点

- **固定、正交**：函数列表固定，不会动态变化
- **对 KV Cache 友好**：始终在系统提示词中，不会重置 KV Cache
- **功能边界清晰**：每个函数职责单一

***REMOVED******REMOVED******REMOVED*** 可用函数

1. **read_file**: 读取文件内容
2. **write_file**: 写入文件内容
3. **execute_shell**: 执行 shell 命令（用于调用 L2 工具）
4. **search_files**: 在文件系统中搜索文件
5. **search_web**: 搜索互联网（需要集成搜索引擎 API）

***REMOVED******REMOVED******REMOVED*** 使用示例

```python
from agent.layered_action_space import get_layered_action_space

las = get_layered_action_space()

***REMOVED*** 读取文件
result = las.execute_l1_function("read_file", {"file_path": "/path/to/file.txt"})

***REMOVED*** 写入文件
result = las.execute_l1_function(
    "write_file",
    {"file_path": "/path/to/file.txt", "content": "文件内容"}
)

***REMOVED*** 执行 shell 命令（调用 L2 工具）
result = las.execute_l1_function("execute_shell", {"command": "grep pattern file.txt"})
```

***REMOVED******REMOVED*** L2: 沙盒工具（Sandbox Tools）

***REMOVED******REMOVED******REMOVED*** 核心特点

- **预装在系统中**：工具作为预装软件放在 Linux VM 沙箱中
- **通过 shell 动态交互**：Agent 通过 L1 的 `execute_shell` 使用
- **动态发现**：可以使用 `which` 和 `man` 命令发现工具

***REMOVED******REMOVED******REMOVED*** 可用工具示例

- `grep`: 在文件中搜索文本模式
- `sed`: 流编辑器，用于文本替换
- `awk`: 文本处理工具
- `curl`: HTTP 客户端
- `wget`: 文件下载工具
- `ffmpeg`: 音视频处理工具
- `imagemagick`: 图像处理工具
- `pandoc`: 文档格式转换工具

***REMOVED******REMOVED******REMOVED*** 使用示例

```python
***REMOVED*** 通过 L1 的 execute_shell 使用 L2 工具
result = las.execute_l1_function(
    "execute_shell",
    {"command": "grep -r 'pattern' /path/to/directory"}
)

***REMOVED*** 发现工具
description = las.discover_l2_tool("grep")
if description:
    print(f"工具信息: {description}")
```

***REMOVED******REMOVED*** L3: 软件包与 API（Packages & APIs）

***REMOVED******REMOVED******REMOVED*** 核心特点

- **编写 Python 脚本**：Agent 可以编写 Python 脚本执行复杂任务
- **调用预授权 API**：API keys 已预安装
- **使用预安装的 Python 包**：可以导入和使用预安装的包
- **返回摘要结果**：不加载所有原始数据，只返回摘要

***REMOVED******REMOVED******REMOVED*** 使用示例

```python
***REMOVED*** 编写并执行 Python 脚本
script_content = """
import json
from datetime import datetime

data = {
    "timestamp": datetime.now().isoformat(),
    "message": "Hello from L3 script!"
}

print(json.dumps(data, ensure_ascii=False, indent=2))
"""

summary, script_path = las.execute_l3_script(script_content, "my_script.py")
print(summary)  ***REMOVED*** 摘要结果
print(f"脚本路径: {script_path}")
```

***REMOVED******REMOVED*** 在 ReActAgent 中的应用

`react.py` 中的 `ReActAgent` 已经集成了分层行动空间：

1. **系统提示词**：包含 L1/L2/L3 的描述
2. **工具执行**：Agent 可以直接使用 L1 函数
3. **L2 工具**：通过 L1 的 `execute_shell` 使用
4. **L3 脚本**：通过 L1 的 `write_file` 和 `execute_shell` 创建和执行

***REMOVED******REMOVED******REMOVED*** 工作流程

```
Agent 需要执行任务
    ↓
选择行动空间层级
    ↓
L1: 直接调用原子函数
L2: 通过 execute_shell 调用系统工具
L3: 编写 Python 脚本并执行
```

***REMOVED******REMOVED*** 设计优势

***REMOVED******REMOVED******REMOVED*** 1. 对 KV Cache 友好

- L1 函数固定，不会动态变化
- 不会因为动态加载工具定义而重置 KV Cache
- 历史记录中的工具调用不会失效

***REMOVED******REMOVED******REMOVED*** 2. 功能边界清晰

- L1: 核心原子操作
- L2: 系统工具（通过 shell）
- L3: 复杂任务（通过脚本）

***REMOVED******REMOVED******REMOVED*** 3. 可扩展性

- L2 工具可以动态发现（通过 `which` 和 `man`）
- L3 脚本可以调用任何预授权的 API
- 不需要修改系统提示词

***REMOVED******REMOVED*** 与现有工具系统的关系

分层行动空间是对现有工具系统的补充，不是替代：

- **现有工具系统**（`tools/`）：用于特定领域的工具（如 calculator、weather）
- **分层行动空间**：用于通用操作和系统级工具

两者可以共存，Agent 可以根据任务选择合适的工具。

***REMOVED******REMOVED*** 沙箱目录结构

```
agent/sandbox/
├── scripts/          ***REMOVED*** L3 Python 脚本
└── ...              ***REMOVED*** 其他沙箱文件
```

***REMOVED******REMOVED*** 安全考虑

1. **L1 函数**：有基本的参数验证和错误处理
2. **L2 工具**：在沙箱目录中执行，有超时限制（30秒）
3. **L3 脚本**：在沙箱目录中执行，有超时限制（60秒）

未来可以增强：
- 更严格的权限控制
- 资源限制（CPU、内存）
- 网络访问控制
