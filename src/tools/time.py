from typing import Any, Dict
from datetime import datetime
from .base import Tool

***REMOVED*** 尝试导入 pytz，如果没有则使用标准库
try:
    import pytz
    HAS_PYTZ = True
except ImportError:
    HAS_PYTZ = False


class TimeTool(Tool):
    """时间查询工具"""
    
    def __init__(self):
        super().__init__(
            name="get_current_time",
            description="获取当前时间和日期信息"
        )
    
    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_current_time",
                "description": "获取指定时区的当前时间和日期",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "时区名称，例如：'Asia/Shanghai'、'America/New_York'、'UTC'。默认为 'Asia/Shanghai'",
                            "default": "Asia/Shanghai"
                        },
                        "format": {
                            "type": "string",
                            "description": "时间格式，'full' 表示完整格式，'date' 表示仅日期，'time' 表示仅时间。默认为 'full'",
                            "enum": ["full", "date", "time"],
                            "default": "full"
                        }
                    },
                    "required": []
                }
            }
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """验证时区参数"""
        if not HAS_PYTZ:
            ***REMOVED*** 如果没有 pytz，只支持 UTC
            timezone = arguments.get("timezone", "UTC")
            return timezone == "UTC"
        
        timezone = arguments.get("timezone", "Asia/Shanghai")
        try:
            pytz.timezone(timezone)
            return True
        except (pytz.exceptions.UnknownTimeZoneError, AttributeError):
            return False
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        """获取当前时间"""
        timezone_str = arguments.get("timezone", "Asia/Shanghai" if HAS_PYTZ else "UTC")
        format_type = arguments.get("format", "full")
        
        try:
            if HAS_PYTZ:
                tz = pytz.timezone(timezone_str)
                now = datetime.now(tz)
            else:
                ***REMOVED*** 如果没有 pytz，使用 UTC
                from datetime import timezone
                now = datetime.now(timezone.utc)
                timezone_str = "UTC"
            
            if format_type == "date":
                return f"{timezone_str} 当前日期：{now.strftime('%Y-%m-%d')}"
            elif format_type == "time":
                return f"{timezone_str} 当前时间：{now.strftime('%H:%M:%S')}"
            else:  ***REMOVED*** full
                return (
                    f"{timezone_str} 当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"星期：{['周一', '周二', '周三', '周四', '周五', '周六', '周日'][now.weekday()]}"
                )
        except Exception as e:
            return f"获取时间失败：{str(e)}"
