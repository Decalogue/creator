"""
天气查询技能示例
模拟天气查询功能
"""
from typing import Any, Dict
from datetime import datetime
import random
from .base import Skill


class WeatherSkill(Skill):
    """天气查询技能（模拟实现）"""
    
    def __init__(self):
        super().__init__(
            name="get_weather",
            description="查询指定城市的天气信息"
        )
        ***REMOVED*** 模拟天气数据
        self._weather_data = {
            "北京": {"temp": "15°C", "condition": "晴", "humidity": "45%"},
            "上海": {"temp": "18°C", "condition": "多云", "humidity": "60%"},
            "广州": {"temp": "25°C", "condition": "晴", "humidity": "70%"},
            "深圳": {"temp": "26°C", "condition": "晴", "humidity": "68%"},
            "杭州": {"temp": "20°C", "condition": "小雨", "humidity": "75%"},
        }
    
    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "查询指定城市的当前天气信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {
                            "type": "string",
                            "description": "城市名称，例如：北京、上海、广州"
                        },
                        "date": {
                            "type": "string",
                            "description": "查询日期，格式：YYYY-MM-DD。如果不提供，默认为今天",
                            "default": None
                        }
                    },
                    "required": ["city"]
                }
            }
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """验证城市参数"""
        if "city" not in arguments:
            return False
        city = str(arguments["city"]).strip()
        return len(city) > 0
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        """查询天气"""
        city = arguments["city"]
        date = arguments.get("date")
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        ***REMOVED*** 检查是否有该城市的天气数据
        if city in self._weather_data:
            weather = self._weather_data[city]
            return (
                f"{city} {date} 的天气：\n"
                f"温度：{weather['temp']}\n"
                f"天气：{weather['condition']}\n"
                f"湿度：{weather['humidity']}"
            )
        else:
            ***REMOVED*** 对于未知城市，返回模拟数据
            temp = random.randint(10, 30)
            conditions = ["晴", "多云", "小雨", "阴"]
            condition = random.choice(conditions)
            humidity = random.randint(40, 80)
            
            return (
                f"{city} {date} 的天气（模拟数据）：\n"
                f"温度：{temp}°C\n"
                f"天气：{condition}\n"
                f"湿度：{humidity}%"
            )
