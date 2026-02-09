#!/usr/bin/env python
"""
UniMem 测试运行脚本（Python 版本）

自动激活 seeme 环境并运行测试

功能：
- 检查 conda 环境是否激活
- 自动运行 pytest 或 unittest
- 提供详细的测试输出
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


def check_seeme_environment() -> bool:
    """
    检查 seeme 环境是否激活
    
    Returns:
        bool: 如果环境已激活返回 True，否则返回 False
    """
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    
    if conda_env != "seeme":
        print("=" * 60)
        print("警告：当前未激活 seeme 环境")
        print(f"当前环境: {conda_env or '未设置'}")
        print("")
        print("请先运行以下命令激活环境：")
        print("  conda activate seeme")
        print("")
        print("或者使用以下命令自动激活并运行测试：")
        print("  bash tests/run_tests.sh")
        print("=" * 60)
        return False
    
    return True


def run_tests() -> int:
    """
    运行测试
    
    自动检测并使用 pytest 或 unittest 运行测试。
    
    Returns:
        int: 退出代码，0 表示成功，非 0 表示失败
    """
    # 获取测试目录
    test_dir = Path(__file__).parent
    
    # 检查环境
    if not check_seeme_environment():
        response = input("\n是否继续运行测试？(y/n): ")
        if response.lower() != 'y':
            print("测试已取消")
            return 1
    
    print("\n" + "=" * 60)
    print("开始运行 UniMem 测试")
    print("=" * 60)
    print(f"当前环境: {os.environ.get('CONDA_DEFAULT_ENV', '未设置')}")
    print(f"Python 路径: {sys.executable}")
    print(f"测试目录: {test_dir}")
    print("=" * 60 + "\n")
    
    # 尝试使用 pytest
    try:
        import pytest
        print("使用 pytest 运行测试...\n")
        exit_code = pytest.main([
            str(test_dir),
            "-v",
            "--tb=short",
            "-W", "ignore::DeprecationWarning",
        ])
        return exit_code
    except ImportError:
        print("pytest 未安装，使用 unittest 运行测试...\n")
        import unittest
        loader = unittest.TestLoader()
        suite = loader.discover(str(test_dir), pattern="test_*.py")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)

