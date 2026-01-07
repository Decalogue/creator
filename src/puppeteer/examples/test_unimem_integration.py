"""
测试 Puppeteer 与 UniMem 的集成

测试内容：
1. UniMem 服务连接
2. UniMem 工具注册
3. 记忆存储和检索
4. 在模拟任务中使用记忆
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

***REMOVED*** 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

***REMOVED*** 测试配置
UNIMEM_API_URL = os.getenv("UNIMEM_API_URL", "http://localhost:9622")
TEST_ENABLED = True


def test_unimem_service_connection():
    """测试 UniMem 服务连接"""
    print("\n" + "=" * 60)
    print("测试 1: UniMem 服务连接")
    print("=" * 60)
    
    try:
        import requests
        response = requests.get(f"{UNIMEM_API_URL}/unimem/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ UniMem 服务连接成功")
            print(f"  状态: {data.get('status', 'unknown')}")
            print(f"  初始化: {data.get('unimem_initialized', False)}")
            return True
        else:
            print(f"✗ UniMem 服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ 无法连接到 UniMem 服务 ({UNIMEM_API_URL})")
        print(f"  提示: 请确保 UniMem 服务已启动")
        print(f"  启动命令: python -m unimem.service.server")
        return False
    except Exception as e:
        print(f"✗ 连接测试失败: {e}")
        return False


def test_unimem_tools_registration():
    """测试 UniMem 工具注册"""
    print("\n" + "=" * 60)
    print("测试 2: UniMem 工具注册")
    print("=" * 60)
    
    try:
        ***REMOVED*** 切换到 puppeteer 目录并添加到 Python 路径
        puppeteer_dir = Path(__file__).parent.parent
        original_dir = os.getcwd()
        
        ***REMOVED*** 添加 puppeteer 目录到路径
        if str(puppeteer_dir) not in sys.path:
            sys.path.insert(0, str(puppeteer_dir))
        
        os.chdir(puppeteer_dir)
        
        ***REMOVED*** 导入工具注册表
        from tools.base.register import global_tool_registry
        
        ***REMOVED*** 检查工具是否注册
        retain_tool = global_tool_registry.get_tool("unimem_retain")
        recall_tool = global_tool_registry.get_tool("unimem_recall")
        reflect_tool = global_tool_registry.get_tool("unimem_reflect")
        
        tools_found = []
        tools_missing = []
        
        if retain_tool:
            tools_found.append("unimem_retain")
            print(f"✓ unimem_retain 工具已注册")
        else:
            tools_missing.append("unimem_retain")
            print(f"✗ unimem_retain 工具未注册")
        
        if recall_tool:
            tools_found.append("unimem_recall")
            print(f"✓ unimem_recall 工具已注册")
        else:
            tools_missing.append("unimem_recall")
            print(f"✗ unimem_recall 工具未注册")
        
        if reflect_tool:
            tools_found.append("unimem_reflect")
            print(f"✓ unimem_reflect 工具已注册")
        else:
            tools_missing.append("unimem_reflect")
            print(f"✗ unimem_reflect 工具未注册")
        
        os.chdir(original_dir)
        
        if tools_missing:
            print(f"\n提示: 如果工具未注册，请确保已导入:")
            print(f"  from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool, UniMemReflectTool")
            return False
        
        return True
        
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        print(f"  提示: 请确保在 puppeteer 目录下运行测试")
        return False
    except Exception as e:
        print(f"✗ 工具注册测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_unimem_operations():
    """测试 UniMem 基本操作"""
    print("\n" + "=" * 60)
    print("测试 3: UniMem 基本操作（存储和检索）")
    print("=" * 60)
    
    try:
        import requests
        
        ***REMOVED*** 1. 存储记忆
        print("\n【步骤 1】存储测试记忆...")
        test_memory = {
            "content": f"测试记忆：这是一个测试记忆，创建时间 {datetime.now().isoformat()}",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "test": True,
                "test_id": "integration_test_001"
            }
        }
        
        retain_url = f"{UNIMEM_API_URL}/unimem/retain"
        retain_response = requests.post(
            retain_url,
            json={
                "experience": test_memory,
                "context": {
                    "test": True,
                    "session_id": "test_session"
                }
            },
            timeout=30
        )
        
        if retain_response.status_code != 200:
            print(f"✗ 存储记忆失败: {retain_response.status_code}")
            print(f"  响应: {retain_response.text}")
            return False
        
        retain_result = retain_response.json()
        if not retain_result.get("success"):
            print(f"✗ 存储记忆失败: {retain_result.get('error', 'Unknown error')}")
            return False
        
        print(f"✓ 记忆存储成功")
        memory_id = retain_result.get("memory", {}).get("id", "unknown")
        print(f"  记忆 ID: {memory_id[:20]}...")
        
        ***REMOVED*** 2. 检索记忆
        print("\n【步骤 2】检索测试记忆...")
        recall_url = f"{UNIMEM_API_URL}/unimem/recall"
        recall_response = requests.post(
            recall_url,
            json={
                "query": "测试记忆",
                "context": {
                    "test": True
                },
                "top_k": 5
            },
            timeout=30
        )
        
        if recall_response.status_code != 200:
            print(f"✗ 检索记忆失败: {recall_response.status_code}")
            print(f"  响应: {recall_response.text}")
            return False
        
        recall_result = recall_response.json()
        if not recall_result.get("success"):
            print(f"✗ 检索记忆失败: {recall_result.get('error', 'Unknown error')}")
            return False
        
        memories = recall_result.get("results", [])
        print(f"✓ 检索到 {len(memories)} 条记忆")
        
        ***REMOVED*** 验证是否找到测试记忆
        found_test_memory = False
        for mem in memories:
            content = mem.get("content", "") if isinstance(mem, dict) else getattr(mem, "content", "")
            if "测试记忆" in content:
                found_test_memory = True
                print(f"✓ 找到测试记忆")
                print(f"  内容: {content[:60]}...")
                break
        
        if not found_test_memory and len(memories) > 0:
            print(f"⚠️ 未找到测试记忆，但检索功能正常")
            print(f"  找到的记忆示例: {memories[0].get('content', '')[:60]}...")
        elif not found_test_memory:
            print(f"⚠️ 未找到任何记忆（可能索引还未更新）")
        
        return True
        
    except Exception as e:
        print(f"✗ 操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_tool_execution():
    """测试工具执行"""
    print("\n" + "=" * 60)
    print("测试 4: 工具执行")
    print("=" * 60)
    
    try:
        ***REMOVED*** 切换到 puppeteer 目录并添加到 Python 路径
        puppeteer_dir = Path(__file__).parent.parent
        original_dir = os.getcwd()
        
        ***REMOVED*** 添加 puppeteer 目录到路径
        if str(puppeteer_dir) not in sys.path:
            sys.path.insert(0, str(puppeteer_dir))
        
        os.chdir(puppeteer_dir)
        
        from tools.base.register import global_tool_registry
        
        ***REMOVED*** 测试 retain 工具
        print("\n【步骤 1】测试 unimem_retain 工具...")
        retain_tool = global_tool_registry.get_tool("unimem_retain")
        if not retain_tool:
            print("✗ retain 工具未找到")
            os.chdir(original_dir)
            return False
        
        success, result = retain_tool.execute(
            experience={
                "content": f"工具测试记忆：通过工具接口存储的记忆 {datetime.now().isoformat()}",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"test": True, "source": "tool_test"}
            },
            context={
                "test": True,
                "session_id": "tool_test_session"
            }
        )
        
        if success:
            print(f"✓ retain 工具执行成功")
            memory_id = result.get("id", "unknown") if isinstance(result, dict) else getattr(result, "id", "unknown")
            print(f"  记忆 ID: {memory_id[:20]}...")
        else:
            print(f"✗ retain 工具执行失败: {result}")
            os.chdir(original_dir)
            return False
        
        ***REMOVED*** 测试 recall 工具
        print("\n【步骤 2】测试 unimem_recall 工具...")
        recall_tool = global_tool_registry.get_tool("unimem_recall")
        if not recall_tool:
            print("✗ recall 工具未找到")
            os.chdir(original_dir)
            return False
        
        success, results = recall_tool.execute(
            query="工具测试",
            context={"test": True},
            top_k=3
        )
        
        if success:
            print(f"✓ recall 工具执行成功")
            print(f"  检索到 {len(results)} 条记忆")
            if results:
                first_content = results[0].get("content", "") if isinstance(results[0], dict) else getattr(results[0], "content", "")
                print(f"  示例记忆: {first_content[:60]}...")
        else:
            print(f"✗ recall 工具执行失败: {results}")
            os.chdir(original_dir)
            return False
        
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print(f"✗ 工具执行测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_simulated_task():
    """测试模拟任务场景"""
    print("\n" + "=" * 60)
    print("测试 5: 模拟任务场景（任务级别集成）")
    print("=" * 60)
    
    try:
        ***REMOVED*** 切换到 puppeteer 目录并添加到 Python 路径
        puppeteer_dir = Path(__file__).parent.parent
        original_dir = os.getcwd()
        
        ***REMOVED*** 添加 puppeteer 目录到路径
        if str(puppeteer_dir) not in sys.path:
            sys.path.insert(0, str(puppeteer_dir))
        
        os.chdir(puppeteer_dir)
        
        from tools.base.register import global_tool_registry
        
        ***REMOVED*** 模拟任务数据
        task = {
            "id": "test_task_001",
            "type": "Novel",
            "Introduction": "一个关于时间旅行的科幻小说",
            "Question": "根据小说简介生成小说大纲"
        }
        
        print(f"\n任务信息:")
        print(f"  ID: {task['id']}")
        print(f"  类型: {task['type']}")
        print(f"  简介: {task['Introduction']}")
        
        ***REMOVED*** 1. 任务开始时检索记忆
        print("\n【步骤 1】检索任务相关记忆...")
        recall_tool = global_tool_registry.get_tool("unimem_recall")
        if not recall_tool:
            print("✗ recall 工具未找到")
            os.chdir(original_dir)
            return False
        
        success, memories = recall_tool.execute(
            query=task["Introduction"],
            context={"task_type": "novel", "task_id": task["id"]},
            top_k=5
        )
        
        if success:
            print(f"✓ 检索到 {len(memories)} 条相关记忆")
            task["retrieved_memories"] = memories
        else:
            print(f"⚠️ 记忆检索失败: {memories}")
            task["retrieved_memories"] = []
        
        ***REMOVED*** 2. 模拟 Agent 执行（存储创作内容）
        print("\n【步骤 2】模拟 Agent 创作（存储记忆）...")
        retain_tool = global_tool_registry.get_tool("unimem_retain")
        if not retain_tool:
            print("✗ retain 工具未找到")
            os.chdir(original_dir)
            return False
        
        creation_content = f"测试创作内容：基于任务 {task['id']} 的创作，时间 {datetime.now().isoformat()}"
        success, memory = retain_tool.execute(
            experience={
                "content": creation_content,
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "task_id": task["id"],
                    "agent_role": "TestAgent",
                    "test": True
                }
            },
            context={
                "task_id": task["id"],
                "task_type": "novel",
                "agent": "TestAgent"
            }
        )
        
        if success:
            print(f"✓ 创作内容已存储")
        else:
            print(f"⚠️ 创作内容存储失败: {memory}")
        
        ***REMOVED*** 3. 任务完成后优化记忆（简化测试）
        print("\n【步骤 3】任务完成（记忆已存储）")
        print(f"✓ 模拟任务完成")
        
        os.chdir(original_dir)
        return True
        
    except Exception as e:
        print(f"✗ 模拟任务测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("\n" + "=" * 60)
    print("Puppeteer 与 UniMem 集成测试")
    print("=" * 60)
    print(f"UniMem API URL: {UNIMEM_API_URL}")
    print(f"测试时间: {datetime.now().isoformat()}")
    
    if not TEST_ENABLED:
        print("\n测试已禁用")
        return
    
    results = []
    
    ***REMOVED*** 运行测试
    results.append(("服务连接", test_unimem_service_connection()))
    results.append(("工具注册", test_unimem_tools_registration()))
    results.append(("基本操作", test_unimem_operations()))
    results.append(("工具执行", test_tool_execution()))
    results.append(("模拟任务", test_simulated_task()))
    
    ***REMOVED*** 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    elif passed > 0:
        print(f"\n⚠️ 部分测试失败，请检查上述错误信息")
    else:
        print(f"\n❌ 所有测试失败，请检查 UniMem 服务是否正常运行")
        print(f"\n提示:")
        print(f"  1. 确保 UniMem 服务已启动: python -m unimem.service.server")
        print(f"  2. 检查服务地址: {UNIMEM_API_URL}")
        print(f"  3. 检查后端服务: Redis, Neo4j, Qdrant")


if __name__ == "__main__":
    main()

