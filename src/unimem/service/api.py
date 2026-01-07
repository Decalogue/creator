"""
UniMem Service API 路由定义

提供 REST API 端点：retain, recall, reflect, health
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import logging

from .models import (
    RetainRequest, RetainResponse,
    RecallRequest, RecallResponse,
    ReflectRequest, ReflectResponse,
    HealthResponse,
)
from .utils import (
    dict_to_experience, dict_to_context, dict_to_task, dict_to_memory,
    dataclass_to_dict, serialize_retrieval_result,
)
from ..types import MemoryType
from ..core import UniMem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/unimem", tags=["unimem"])

***REMOVED*** 全局 UniMem 实例（启动时初始化）
unimem_instance: Optional[UniMem] = None


def set_unimem_instance(instance: UniMem):
    """设置 UniMem 实例"""
    global unimem_instance
    unimem_instance = instance


def get_unimem_instance() -> UniMem:
    """获取 UniMem 实例"""
    if not unimem_instance:
        raise HTTPException(status_code=503, detail="UniMem service not initialized")
    return unimem_instance


@router.post("/retain", response_model=RetainResponse)
async def retain(request: RetainRequest):
    """
    存储新记忆（RETAIN 操作）
    
    将经验数据存储为记忆，并更新图结构和网络链接
    """
    try:
        unimem = get_unimem_instance()
        
        ***REMOVED*** 转换请求数据为 UniMem 类型
        experience = dict_to_experience(request.experience)
        context = dict_to_context(request.context)
        
        ***REMOVED*** 调用 UniMem retain
        memory = unimem.retain(experience, context, request.operation_id)
        
        ***REMOVED*** 转换为响应格式
        memory_dict = dataclass_to_dict(memory)
        return RetainResponse(success=True, memory=memory_dict)
        
    except Exception as e:
        logger.error(f"RETAIN failed: {e}", exc_info=True)
        return RetainResponse(success=False, error=str(e))


@router.post("/recall", response_model=RecallResponse)
async def recall(request: RecallRequest):
    """
    检索记忆（RECALL 操作）
    
    根据查询字符串检索相关记忆，支持多维检索和融合
    """
    try:
        unimem = get_unimem_instance()
        
        ***REMOVED*** 转换请求数据
        context = dict_to_context(request.context)
        memory_type = None
        if request.memory_type:
            try:
                memory_type = MemoryType(request.memory_type)
            except ValueError:
                logger.warning(f"Invalid memory_type: {request.memory_type}, ignoring filter")
        
        ***REMOVED*** 调用 UniMem recall
        results = unimem.recall(
            query=request.query,
            context=context,
            memory_type=memory_type,
            top_k=request.top_k,
        )
        
        ***REMOVED*** 转换为响应格式
        results_list = [serialize_retrieval_result(r) for r in results]
        return RecallResponse(success=True, results=results_list)
        
    except Exception as e:
        logger.error(f"RECALL failed: {e}", exc_info=True)
        return RecallResponse(success=False, error=str(e))


@router.post("/reflect", response_model=ReflectResponse)
async def reflect(request: ReflectRequest):
    """
    优化记忆（REFLECT 操作）
    
    基于任务上下文更新和优化记忆，产生新观点
    """
    try:
        unimem = get_unimem_instance()
        
        ***REMOVED*** 转换请求数据
        memories = [dict_to_memory(m) for m in request.memories]
        task = dict_to_task(request.task)
        context = dict_to_context(request.context)
        
        ***REMOVED*** 调用 UniMem reflect
        updated_memories = unimem.reflect(memories, task, context)
        
        ***REMOVED*** 转换为响应格式
        updated_list = [dataclass_to_dict(m) for m in updated_memories]
        return ReflectResponse(success=True, updated_memories=updated_list)
        
    except Exception as e:
        logger.error(f"REFLECT failed: {e}", exc_info=True)
        return ReflectResponse(success=False, error=str(e))


@router.get("/health", response_model=HealthResponse)
async def health():
    """
    健康检查
    
    检查服务状态和 UniMem 初始化状态
    """
    try:
        unimem = get_unimem_instance()
        ***REMOVED*** 如果能够获取实例，说明已初始化
        return HealthResponse(
            status="ok",
            unimem_initialized=True,
            message="UniMem service is running"
        )
    except HTTPException:
        return HealthResponse(
            status="error",
            unimem_initialized=False,
            message="UniMem service not initialized"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return HealthResponse(
            status="error",
            unimem_initialized=False,
            message=f"Health check error: {str(e)}"
        )

