"""
Dashboard API

为前端 Dashboard 提供数据接口
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from agent.infra.observability import get_agent_observability
from agent.infra.cache import get_agent_cache
from agent.infra.experiment import ExperimentManager
from unimem.core import UniMem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# 全局实例（延迟初始化）
_observability = None
_cache = None
_experiment_manager = None
_unimem = None


def get_observability():
    """获取可观测性实例"""
    global _observability
    if _observability is None:
        _observability = get_agent_observability()
    return _observability


def get_cache():
    """获取缓存实例"""
    global _cache
    if _cache is None:
        _cache = get_agent_cache()
    return _cache


def get_experiment_manager():
    """获取实验管理器实例"""
    global _experiment_manager
    if _experiment_manager is None:
        _experiment_manager = ExperimentManager()
    return _experiment_manager


@router.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    获取 Agent 指标
    
    Returns:
        Dashboard 指标数据
    """
    try:
        observability = get_observability()
        metrics = observability.get_dashboard_metrics()
        return {
            "success": True,
            "data": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取指标失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """
    获取缓存统计
    
    Returns:
        缓存统计数据
    """
    try:
        cache = get_cache()
        stats = cache.get_stats()
        return {
            "success": True,
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/traces")
async def get_traces(limit: int = 100) -> Dict[str, Any]:
    """
    获取追踪记录
    
    Args:
        limit: 返回的最大记录数
    
    Returns:
        追踪记录列表
    """
    try:
        observability = get_observability()
        traces = observability.get_traces(limit=limit)
        return {
            "success": True,
            "data": traces,
            "count": len(traces),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取追踪记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments")
async def list_experiments() -> Dict[str, Any]:
    """
    列出所有实验
    
    Returns:
        实验列表
    """
    try:
        manager = get_experiment_manager()
        experiments = []
        for name, experiment in manager.experiments.items():
            experiments.append({
                "name": experiment.name,
                "description": experiment.description,
                "variants": len(experiment.variants),
                "results": len(experiment.results),
                "created_at": experiment.created_at.isoformat()
            })
        return {
            "success": True,
            "data": experiments,
            "count": len(experiments)
        }
    except Exception as e:
        logger.error(f"列出实验失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/experiments/{experiment_name}")
async def get_experiment(experiment_name: str) -> Dict[str, Any]:
    """
    获取实验详情和对比结果
    
    Args:
        experiment_name: 实验名称
    
    Returns:
        实验详情和对比结果
    """
    try:
        manager = get_experiment_manager()
        if experiment_name not in manager.experiments:
            raise HTTPException(status_code=404, detail=f"实验不存在: {experiment_name}")
        
        comparison = manager.compare_results(experiment_name)
        return {
            "success": True,
            "data": comparison,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取实验详情失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/metrics")
async def get_memory_metrics() -> Dict[str, Any]:
    """
    获取 Memory 系统指标
    
    Returns:
        Memory 指标数据
    """
    try:
        # 尝试获取 UniMem 实例（如果可用）
        global _unimem
        if _unimem is None:
            # 这里需要根据实际情况获取 UniMem 实例
            # 暂时返回占位数据
            return {
                "success": True,
                "data": {
                    "available": False,
                    "message": "UniMem 实例未初始化"
                },
                "timestamp": datetime.now().isoformat()
            }
        
        # 获取 UniMem 指标
        metrics = _unimem.get_metrics()
        health = _unimem.health_check()
        
        return {
            "success": True,
            "data": {
                "metrics": metrics,
                "health": health,
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取 Memory 指标失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "data": {
                "available": False
            },
            "timestamp": datetime.now().isoformat()
        }


@router.post("/cache/clear")
async def clear_cache() -> Dict[str, Any]:
    """
    清空所有缓存
    
    Returns:
        操作结果
    """
    try:
        cache = get_cache()
        cache.clear_all()
        return {
            "success": True,
            "message": "缓存已清空",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"清空缓存失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    健康检查
    
    Returns:
        系统健康状态
    """
    try:
        observability = get_observability()
        cache = get_cache()
        
        # 获取基本指标
        metrics = observability.get_dashboard_metrics()
        
        # 判断健康状态
        health_status = "healthy"
        if metrics["success_rate"] < 0.9:  # 成功率低于90%
            health_status = "degraded"
        if metrics["success_rate"] < 0.5:  # 成功率低于50%
            health_status = "unhealthy"
        
        return {
            "success": True,
            "data": {
                "status": health_status,
                "metrics": {
                    "success_rate": metrics["success_rate"],
                    "total_queries": metrics["total_queries"],
                    "avg_latency": metrics["avg_latency"],
                },
                "cache": cache.get_stats(),
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}", exc_info=True)
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }
