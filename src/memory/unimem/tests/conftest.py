"""
Pytest 配置和共享 fixtures

注意：运行测试前需要激活 seeme 环境：
    conda activate seeme
"""

import os
import sys
import pytest


def pytest_configure(config):
    """Pytest 配置钩子"""
    ***REMOVED*** 检查环境
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env != "seeme":
        print("\n" + "="*60)
        print("警告：当前未激活 seeme 环境")
        print(f"当前环境: {conda_env or '未设置'}")
        print("请先运行: conda activate seeme")
        print("="*60 + "\n")
        ***REMOVED*** 不强制退出，允许继续运行（某些测试可能不需要环境）


@pytest.fixture(scope="session")
def check_seeme_environment():
    """检查 seeme 环境是否激活"""
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    if conda_env != "seeme":
        pytest.skip("需要激活 seeme 环境: conda activate seeme")


@pytest.fixture(scope="function")
def mock_qdrant_client():
    """Mock Qdrant 客户端 fixture"""
    from unittest.mock import MagicMock
    return MagicMock()


@pytest.fixture(scope="function")
def mock_embedding_model():
    """Mock 嵌入模型 fixture"""
    from unittest.mock import MagicMock
    model = MagicMock()
    model.encode.return_value = [[0.1] * 384]  ***REMOVED*** all-MiniLM-L6-v2 维度
    return model

