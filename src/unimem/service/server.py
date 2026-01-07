"""
UniMem HTTP Service 主文件

提供 FastAPI 服务，启动时初始化 UniMem 实例
"""

import os
import logging
from typing import Optional
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api import router, set_unimem_instance
from ..core import UniMem
from ..config import UniMemConfig

***REMOVED*** 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

***REMOVED*** 创建 FastAPI 应用
app = FastAPI(
    title="UniMem Service",
    description="UniMem HTTP API Service - 提供记忆系统的 REST API 接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

***REMOVED*** 添加 CORS 中间件（允许跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  ***REMOVED*** 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

***REMOVED*** 注册路由
app.include_router(router)


def load_config(config_file: Optional[str] = None):
    """
    加载 UniMem 配置
    
    Args:
        config_file: 配置文件路径（可选）
        
    Returns:
        (config_dict, storage_backend, graph_backend, vector_backend)
    """
    ***REMOVED*** 1. 从环境变量获取配置文件路径
    if not config_file:
        config_file = os.getenv("UNIMEM_CONFIG_FILE")
    
    ***REMOVED*** 2. 使用 UniMemConfig 加载配置（会自动从环境变量读取）
    config_obj = UniMemConfig(config_file=config_file)
    config_dict = config_obj.to_dict()
    
    ***REMOVED*** 3. 从环境变量获取后端配置（UniMemConfig已经处理了，但我们还需要返回）
    storage_backend = os.getenv("UNIMEM_STORAGE_BACKEND", "redis")
    graph_backend = os.getenv("UNIMEM_GRAPH_BACKEND", "neo4j")
    vector_backend = os.getenv("UNIMEM_VECTOR_BACKEND", "qdrant")
    
    return config_dict, storage_backend, graph_backend, vector_backend


@app.on_event("startup")
async def startup_event():
    """启动时初始化 UniMem"""
    try:
        logger.info("=" * 60)
        logger.info("Starting UniMem Service...")
        logger.info("=" * 60)
        
        ***REMOVED*** 加载配置
        config_file = os.getenv("UNIMEM_CONFIG_FILE")
        config_dict, storage_backend, graph_backend, vector_backend = load_config(config_file)
        
        logger.info(f"Configuration loaded:")
        logger.info(f"  Storage backend: {storage_backend}")
        logger.info(f"  Graph backend: {graph_backend}")
        logger.info(f"  Vector backend: {vector_backend}")
        
        ***REMOVED*** 初始化 UniMem
        logger.info("Initializing UniMem...")
        unimem = UniMem(
            config=config_dict,
            storage_backend=storage_backend,
            graph_backend=graph_backend,
            vector_backend=vector_backend,
        )
        
        ***REMOVED*** 设置全局实例
        set_unimem_instance(unimem)
        
        logger.info("=" * 60)
        logger.info("UniMem Service started successfully!")
        logger.info("=" * 60)
        logger.info("API Documentation: http://localhost:9622/docs")
        logger.info("Health Check: http://localhost:9622/unimem/health")
        
    except Exception as e:
        logger.error(f"Failed to initialize UniMem: {e}", exc_info=True)
        logger.error("Service will start but UniMem operations will fail")
        ***REMOVED*** 不抛出异常，让服务启动（可以处理健康检查等请求）


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理资源"""
    logger.info("Shutting down UniMem Service...")


@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "UniMem Service",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/unimem/health",
    }


def main():
    """主函数：启动服务"""
    import argparse
    
    parser = argparse.ArgumentParser(description="UniMem HTTP Service")
    parser.add_argument(
        "--host",
        type=str,
        default=os.getenv("UNIMEM_HOST", "0.0.0.0"),
        help="服务绑定地址（默认: 0.0.0.0）"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("UNIMEM_PORT", "9622")),
        help="服务端口（默认: 9622）"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="配置文件路径（可选）"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="开发模式：代码变更时自动重载"
    )
    
    args = parser.parse_args()
    
    ***REMOVED*** 设置配置文件环境变量（如果提供）
    if args.config:
        os.environ["UNIMEM_CONFIG_FILE"] = args.config
    
    ***REMOVED*** 启动服务
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()

