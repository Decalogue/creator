"""
计算器技能示例
支持基本的数学运算
"""
from typing import Any, Dict
from .base import Skill


class CalculatorSkill(Skill):
    """计算器技能"""
    
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，支持加减乘除、幂运算等"
        )
    
    def get_function_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "执行数学计算。支持基本运算（+、-、*、/）和幂运算（**）。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "要计算的数学表达式，例如：'2 + 3 * 4' 或 '10 ** 2'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """验证表达式是否安全"""
        if "expression" not in arguments:
            return False
        
        expression = str(arguments["expression"])
        
        ***REMOVED*** 只允许数字、运算符和空格
        allowed_chars = set("0123456789+-*/.()^ ")
        ***REMOVED*** 也允许 ** 表示幂运算
        if not all(c in allowed_chars or expression[i:i+2] == "**" for i, c in enumerate(expression)):
            return False
        
        ***REMOVED*** 不允许导入或执行代码
        dangerous_keywords = ["import", "exec", "eval", "__", "open", "file"]
        expression_lower = expression.lower()
        for keyword in dangerous_keywords:
            if keyword in expression_lower:
                return False
        
        return True
    
    def execute(self, arguments: Dict[str, Any]) -> str:
        """执行计算"""
        expression = arguments["expression"]
        original_expression = expression
        
        try:
            ***REMOVED*** 将 ^ 替换为 **
            expression = expression.replace("^", "**")
            
            ***REMOVED*** 使用更安全的方式计算
            ***REMOVED*** 只允许数字、运算符和括号
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars or expression[i:i+2] == "**" 
                      for i, c in enumerate(expression)):
                return "计算错误：表达式包含不允许的字符"
            
            ***REMOVED*** 安全地计算表达式（限制内置函数）
            result = eval(expression, {"__builtins__": {}}, {})
            
            ***REMOVED*** 格式化结果
            if isinstance(result, float):
                ***REMOVED*** 如果是浮点数，保留合理的小数位数
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)
            
            return f"计算结果：{original_expression} = {result}"
        except ZeroDivisionError:
            return "计算错误：除以零"
        except Exception as e:
            return f"计算错误：{str(e)}"
