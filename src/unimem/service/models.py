"""
UniMem Service API 请求/响应模型

使用 Pydantic 定义 API 的输入输出格式
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class RetainRequest(BaseModel):
    """RETAIN 操作请求"""
    experience: Dict[str, Any] = Field(..., description="经验数据，包含 content, timestamp, context, metadata")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息，包含 session_id, user_id, metadata")
    operation_id: Optional[str] = Field(None, description="操作ID（用于幂等性检查）")


class RetainResponse(BaseModel):
    """RETAIN 操作响应"""
    success: bool = Field(..., description="操作是否成功")
    memory: Optional[Dict[str, Any]] = Field(None, description="创建的记忆对象")
    error: Optional[str] = Field(None, description="错误信息（如果失败）")


class RecallRequest(BaseModel):
    """RECALL 操作请求"""
    query: str = Field(..., description="查询字符串")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    memory_type: Optional[str] = Field(None, description="记忆类型过滤（episodic/semantic/world/experience/observation/opinion）")
    top_k: int = Field(10, description="返回结果数量", ge=1, le=100)


class RecallResponse(BaseModel):
    """RECALL 操作响应"""
    success: bool = Field(..., description="操作是否成功")
    results: Optional[List[Dict[str, Any]]] = Field(None, description="检索结果列表，每个结果包含 memory, score, retrieval_method")
    error: Optional[str] = Field(None, description="错误信息（如果失败）")


class ReflectRequest(BaseModel):
    """REFLECT 操作请求"""
    memories: List[Dict[str, Any]] = Field(..., description="需要优化的记忆列表")
    task: Dict[str, Any] = Field(..., description="任务上下文，包含 id, description, context, metadata")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class ReflectResponse(BaseModel):
    """REFLECT 操作响应"""
    success: bool = Field(..., description="操作是否成功")
    updated_memories: Optional[List[Dict[str, Any]]] = Field(None, description="优化后的记忆列表")
    error: Optional[str] = Field(None, description="错误信息（如果失败）")


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态（ok/error）")
    unimem_initialized: bool = Field(..., description="UniMem 是否已初始化")
    message: Optional[str] = Field(None, description="额外信息")

