"""
分层行动空间（Layered Action Space）
实现 Manus 风格的三层架构

L1: 原子函数调用（Atomic Function Calling）- 核心层
L2: 沙盒工具（Sandbox Tools）- 卸载层
L3: 软件包与 API（Packages & APIs）- 代码层
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ActionLayer(Enum):
    """行动空间层级"""
    L1_ATOMIC = "L1_ATOMIC"  ***REMOVED*** 原子函数调用
    L2_SANDBOX = "L2_SANDBOX"  ***REMOVED*** 沙盒工具
    L3_CODE = "L3_CODE"  ***REMOVED*** 软件包与 API


class LayeredActionSpace:
    """
    分层行动空间管理器
    
    实现 Manus 风格的三层架构：
    - L1: 固定、正交的原子函数（对 KV Cache 友好）
    - L2: 预装在 VM 沙箱中的工具（通过 shell 动态交互）
    - L3: Agent 编写的 Python 脚本（调用预授权 API）
    """
    
    def __init__(self, sandbox_dir: Optional[Path] = None):
        """
        初始化分层行动空间
        
        Args:
            sandbox_dir: 沙箱目录，默认为 agent/sandbox/
        """
        if sandbox_dir is None:
            current_dir = Path(__file__).parent
            sandbox_dir = current_dir / "sandbox"
        
        self.sandbox_dir = Path(sandbox_dir)
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)
        
        ***REMOVED*** L1 原子函数列表（固定、正交）
        self.l1_functions = {
            "read_file": self._l1_read_file,
            "write_file": self._l1_write_file,
            "execute_shell": self._l1_execute_shell,
            "search_files": self._l1_search_files,
            "search_web": self._l1_search_web,
        }
        
        ***REMOVED*** L2 沙盒工具（通过 shell 命令使用）
        ***REMOVED*** 这些工具预装在系统中，Agent 通过 L1 的 execute_shell 使用
        self.l2_tools_info = {
            "grep": "在文件中搜索文本模式",
            "sed": "流编辑器，用于文本替换",
            "awk": "文本处理工具",
            "curl": "HTTP 客户端",
            "wget": "文件下载工具",
            "ffmpeg": "音视频处理工具",
            "imagemagick": "图像处理工具",
            "pandoc": "文档格式转换工具",
        }
        
        ***REMOVED*** L3 代码层（Python 脚本和 API）
        self.l3_scripts_dir = self.sandbox_dir / "scripts"
        self.l3_scripts_dir.mkdir(exist_ok=True)
        
        ***REMOVED*** 预授权的 API keys（示例）
        self.l3_api_keys = {
            ***REMOVED*** 可以从环境变量或配置文件读取
        }
    
    def get_l1_functions_description(self) -> str:
        """
        获取 L1 原子函数的描述（用于系统提示词）
        
        Returns:
            L1 函数描述文本
        """
        descriptions = [
            "L1 原子函数（固定、正交，始终可用）:",
            ""
        ]
        
        for func_name, func in self.l1_functions.items():
            doc = func.__doc__ or "无描述"
            ***REMOVED*** 提取第一行非空描述
            lines = [line.strip() for line in doc.split('\n') if line.strip()]
            if lines:
                first_line = lines[0]
                ***REMOVED*** 如果第一行以句号结尾，去掉句号
                if first_line.endswith('。'):
                    first_line = first_line[:-1]
                descriptions.append(f"- {func_name}: {first_line}")
            else:
                descriptions.append(f"- {func_name}: 无描述")
        
        descriptions.append("")
        descriptions.append("注意：L1 函数对 KV Cache 友好，功能边界清晰。")
        
        return "\n".join(descriptions)
    
    def get_l2_tools_description(self) -> str:
        """
        获取 L2 沙盒工具的描述（用于系统提示词）
        
        Returns:
            L2 工具描述文本
        """
        descriptions = [
            "L2 沙盒工具（预装在系统中，通过 shell 命令使用）:",
            ""
        ]
        
        for tool_name, description in self.l2_tools_info.items():
            descriptions.append(f"- {tool_name}: {description}")
        
        descriptions.append("")
        descriptions.append("注意：L2 工具通过 L1 的 `execute_shell` 函数使用。")
        descriptions.append("可以使用 `execute_shell` 执行命令，例如：`execute_shell({'command': 'grep -r pattern /path'})`")
        
        return "\n".join(descriptions)
    
    def get_l3_description(self) -> str:
        """
        获取 L3 代码层的描述（用于系统提示词）
        
        Returns:
            L3 描述文本
        """
        return """L3 代码层（编写 Python 脚本调用 API 或使用软件包）:

- 可以编写 Python 脚本执行复杂任务
- 可以调用预授权的 API（API keys 已预安装）
- 可以导入和使用预安装的 Python 包
- 脚本执行后返回摘要结果，不加载所有原始数据

注意：L3 脚本通过 L1 的 `write_file` 和 `execute_shell` 创建和执行。
例如：
1. 使用 `write_file` 创建 Python 脚本
2. 使用 `execute_shell` 执行脚本：`python script.py`
"""
    
    ***REMOVED*** ========== L1 原子函数实现 ==========
    
    def _l1_read_file(self, arguments: Dict[str, Any]) -> str:
        """
        读取文件内容。读取指定路径的文件并返回其内容。
        
        Args:
            arguments: {"file_path": "文件路径"}
        
        Returns:
            文件内容
        """
        file_path = arguments.get("file_path", "")
        if not file_path:
            return "错误：缺少 file_path 参数"
        
        try:
            path = Path(file_path)
            if not path.exists():
                return f"错误：文件不存在: {file_path}"
            
            content = path.read_text(encoding="utf-8")
            return f"文件内容 ({len(content)} 字符):\n{content}"
        except Exception as e:
            return f"错误：读取文件失败: {str(e)}"
    
    def _l1_write_file(self, arguments: Dict[str, Any]) -> str:
        """
        写入文件内容。将内容写入指定路径的文件，如果目录不存在会自动创建。
        
        Args:
            arguments: {"file_path": "文件路径", "content": "文件内容"}
        
        Returns:
            写入结果
        """
        file_path = arguments.get("file_path", "")
        content = arguments.get("content", "")
        
        if not file_path:
            return "错误：缺少 file_path 参数"
        
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return f"成功：已写入文件 {file_path} ({len(content)} 字符)"
        except Exception as e:
            return f"错误：写入文件失败: {str(e)}"
    
    def _l1_execute_shell(self, arguments: Dict[str, Any]) -> str:
        """
        执行 shell 命令。用于调用 L2 沙盒工具或执行系统命令。
        
        Args:
            arguments: {"command": "shell 命令"}
        
        Returns:
            命令输出
        """
        command = arguments.get("command", "")
        if not command:
            return "错误：缺少 command 参数"
        
        try:
            ***REMOVED*** 在沙箱目录中执行命令
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.sandbox_dir),
                capture_output=True,
                text=True,
                timeout=30  ***REMOVED*** 30秒超时
            )
            
            output = result.stdout
            error = result.stderr
            
            if result.returncode == 0:
                return f"命令执行成功:\n{output}" if output else "命令执行成功（无输出）"
            else:
                return f"命令执行失败 (退出码: {result.returncode}):\n{error if error else output}"
        except subprocess.TimeoutExpired:
            return "错误：命令执行超时（>30秒）"
        except Exception as e:
            return f"错误：执行命令失败: {str(e)}"
    
    def _l1_search_files(self, arguments: Dict[str, Any]) -> str:
        """
        在文件系统中搜索文件。使用 glob 模式在指定目录中搜索匹配的文件。
        
        Args:
            arguments: {"pattern": "搜索模式", "directory": "搜索目录（可选）"}
        
        Returns:
            搜索结果
        """
        pattern = arguments.get("pattern", "")
        directory = arguments.get("directory", ".")
        
        if not pattern:
            return "错误：缺少 pattern 参数"
        
        try:
            search_dir = Path(directory)
            if not search_dir.exists():
                return f"错误：目录不存在: {directory}"
            
            ***REMOVED*** 使用 glob 搜索文件
            matches = list(search_dir.rglob(pattern))
            
            if matches:
                results = [f"- {str(match)}" for match in matches[:20]]  ***REMOVED*** 最多20个结果
                if len(matches) > 20:
                    results.append(f"... 还有 {len(matches) - 20} 个结果")
                return f"找到 {len(matches)} 个匹配文件:\n" + "\n".join(results)
            else:
                return f"未找到匹配的文件: {pattern}"
        except Exception as e:
            return f"错误：搜索文件失败: {str(e)}"
    
    def _l1_search_web(self, arguments: Dict[str, Any]) -> str:
        """
        搜索互联网。在当前实现中为模拟，实际应集成搜索引擎 API。
        
        Args:
            arguments: {"query": "搜索查询"}
        
        Returns:
            搜索结果
        """
        query = arguments.get("query", "")
        if not query:
            return "错误：缺少 query 参数"
        
        ***REMOVED*** 这里是模拟实现，实际应该调用搜索引擎 API
        return f"网络搜索结果（模拟）: {query}\n\n提示：实际实现需要集成搜索引擎 API（如 Google Search API、Bing API 等）。"
    
    def execute_l1_function(self, function_name: str, arguments: Dict[str, Any]) -> str:
        """
        执行 L1 原子函数
        
        Args:
            function_name: 函数名称
            arguments: 函数参数
        
        Returns:
            执行结果
        """
        if function_name not in self.l1_functions:
            return f"错误：L1 函数不存在: {function_name}"
        
        try:
            func = self.l1_functions[function_name]
            return func(arguments)
        except Exception as e:
            return f"错误：执行 L1 函数失败: {str(e)}"
    
    def discover_l2_tool(self, tool_name: str) -> Optional[str]:
        """
        发现 L2 工具（通过 man 命令或 which 命令）
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具描述（如果存在）
        """
        try:
            ***REMOVED*** 检查工具是否存在
            result = subprocess.run(
                f"which {tool_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                tool_path = result.stdout.strip()
                ***REMOVED*** 尝试获取工具描述（通过 man 命令）
                man_result = subprocess.run(
                    f"man {tool_name} 2>/dev/null | head -n 5",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                description = self.l2_tools_info.get(tool_name, "预装的系统工具")
                return f"{tool_name}: {description}\n路径: {tool_path}"
            else:
                return None
        except Exception:
            return None
    
    def execute_l3_script(
        self,
        script_content: str,
        script_name: Optional[str] = None
    ) -> Tuple[str, Path]:
        """
        执行 L3 Python 脚本
        
        Args:
            script_content: 脚本内容
            script_name: 脚本名称（可选，自动生成）
        
        Returns:
            (执行结果摘要, 脚本文件路径)
        """
        if not script_name:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            script_name = f"l3_script_{timestamp}.py"
        
        script_path = self.l3_scripts_dir / script_name
        
        try:
            ***REMOVED*** 写入脚本文件
            script_path.write_text(script_content, encoding="utf-8")
            
            ***REMOVED*** 执行脚本
            result = subprocess.run(
                f"python {script_path}",
                shell=True,
                cwd=str(self.sandbox_dir),
                capture_output=True,
                text=True,
                timeout=60  ***REMOVED*** 60秒超时
            )
            
            output = result.stdout
            error = result.stderr
            
            if result.returncode == 0:
                ***REMOVED*** 返回摘要（不返回所有原始数据）
                summary = f"脚本执行成功: {script_name}\n输出长度: {len(output)} 字符"
                if output:
                    ***REMOVED*** 只返回前500字符作为预览
                    summary += f"\n输出预览:\n{output[:500]}{'...' if len(output) > 500 else ''}"
                return summary, script_path
            else:
                return f"脚本执行失败 (退出码: {result.returncode}):\n{error if error else output}", script_path
        except subprocess.TimeoutExpired:
            return f"错误：脚本执行超时（>60秒）: {script_name}", script_path
        except Exception as e:
            return f"错误：执行脚本失败: {str(e)}", script_path


***REMOVED*** 全局分层行动空间实例（延迟初始化）
_layered_action_space_instance: Optional[LayeredActionSpace] = None


def get_layered_action_space(sandbox_dir: Optional[Path] = None) -> LayeredActionSpace:
    """
    获取全局分层行动空间实例
    
    Args:
        sandbox_dir: 沙箱目录，如果为 None 则使用默认目录
    
    Returns:
        LayeredActionSpace 实例
    """
    global _layered_action_space_instance
    
    if _layered_action_space_instance is None:
        _layered_action_space_instance = LayeredActionSpace(sandbox_dir)
    
    return _layered_action_space_instance
