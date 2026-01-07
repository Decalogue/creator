"""
Pytest 配置和共享 fixtures

注意：运行测试前需要激活 myswift 环境：
    conda activate myswift
"""

import os
import sys
from typing import Any
import pytest


def pytest_configure(config: Any) -> None:
    """
    Pytest 配置钩子
    
    在测试运行前检查环境配置，并给出警告提示。
    
    Args:
        config: Pytest 配置对象
    """
    ***REMOVED*** 检查环境
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env != "myswift":
        print("\n" + "="*60)
        print("警告：当前未激活 myswift 环境")
        print(f"当前环境: {conda_env or '未设置'}")
        print("请先运行: conda activate myswift")
        print("="*60 + "\n")
        ***REMOVED*** 不强制退出，允许继续运行（某些测试可能不需要环境）


@pytest.fixture(scope="session")
def check_seeme_environment() -> None:
    """
    检查 myswift 环境是否激活
    
    如果环境未激活，跳过测试。
    
    Yields:
        None
    """
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env != "myswift":
        pytest.skip("需要激活 myswift 环境: conda activate myswift")


@pytest.fixture(scope="function")
def mock_qdrant_client() -> Any:
    """
    Mock Qdrant 客户端 fixture
    
    返回一个 Mock 对象，用于模拟 Qdrant 客户端的行为。
    
    Returns:
        MagicMock: Mock 的 Qdrant 客户端对象
    """
    from unittest.mock import MagicMock
    return MagicMock()


@pytest.fixture(scope="function")
def mock_embedding_model() -> Any:
    """
    Mock 嵌入模型 fixture
    
    返回一个 Mock 对象，模拟嵌入模型的行为。
    默认返回 384 维向量（all-MiniLM-L6-v2 模型维度）。
    
    Returns:
        MagicMock: Mock 的嵌入模型对象，encode 方法返回 384 维向量
    """
    from unittest.mock import MagicMock
    model = MagicMock()
    model.encode.return_value = [[0.1] * 384]  ***REMOVED*** all-MiniLM-L6-v2 维度
    return model

