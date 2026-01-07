"""
集成 UniMem 的小说创作任务

基于原有的 novel.py，集成 UniMem 记忆系统：
1. 使用 GraphReasoningWithMemory
2. 使用带记忆的提示词
3. 使用带记忆的 Agent（personas_with_memory.jsonl）
4. 自动检索和存储记忆
"""

import os
import sys
import json
import yaml
from tqdm import tqdm

***REMOVED*** 确保当前目录在 Python 路径中
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

***REMOVED*** 导入带记忆的推理组件
from inference.reasoning.reasoning_with_memory import GraphReasoningWithMemory
from inference.graph.agent_graph import AgentGraph
from agent.register.register_with_memory import agent_global_registry_with_memory

***REMOVED*** 确保 UniMem 工具被导入和注册
try:
    from tools.unimem_tool import UniMemRetainTool, UniMemRecallTool, UniMemReflectTool
    print("✓ UniMem 工具已导入并注册")
except ImportError as e:
    print(f"⚠ 无法导入 UniMem 工具: {e}")
from agent.register.register import agent_global_registry


def load_dataset(data_limit=None):
    """加载数据集"""
    path = "./data/Novel/novel.jsonl"
    with open(path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return data[:data_limit] if data_limit else data


def format_question(q, idx):
    """格式化问题"""
    question = f'根据小说简介生成小说大纲。\n***REMOVED******REMOVED*** 小说简介\n{q["introduction"]}\n\n输出：'
    return {
        "type": "Novel",
        "Question": question,
        "Answer": q["outline"],
        "Introduction": q["introduction"],
        "id": idx
    }


def filter_tool_agents():
    """过滤掉工具类 Agent，只保留推理类 Agent（保留 TerminatorAgent）"""
    drop_tool_agent_names = {
        "FileAgent",
        "ArxivAgent",
        "BingAgent",
        "WebsiteAgent",
        "PythonAgent_qwen"
    }
    ***REMOVED*** 注意：TerminatorAgent 必须保留，因为它用于终止推理
    
    all_agents = list(agent_global_registry_with_memory.unique_agents.values())
    all_agent_names = list(agent_global_registry_with_memory.agents.keys())
    
    filtered_agents = {
        agent.hash: agent 
        for agent in all_agents 
        if agent.role not in drop_tool_agent_names
    }
    
    filtered_agent_names = {
        name: agent 
        for name, agent in agent_global_registry_with_memory.agents.items()
        if agent.role not in drop_tool_agent_names
    }
    
    ***REMOVED*** 更新注册表
    agent_global_registry_with_memory.unique_agents = filtered_agents
    agent_global_registry_with_memory.agents = filtered_agent_names
    
    filtered_roles = [a.role for a in filtered_agents.values()]
    removed_roles = [a.role for a in all_agents if a.role in drop_tool_agent_names]
    print(f"过滤掉 {len(removed_roles)} 个工具类 Agent: {removed_roles}")
    print(f"保留 {len(filtered_roles)} 个推理类 Agent: {filtered_roles}")
    
    ***REMOVED*** 验证 TerminatorAgent 是否存在
    terminator_exists = any(a.role == "TerminatorAgent" for a in filtered_agents.values())
    if not terminator_exists:
        print("警告: TerminatorAgent 不存在，推理可能无法正常终止")


def run(runner, evaluator, results_dir, mode, data_limit=None, unimem_enabled=True, personas_path=None):
    """
    运行集成 UniMem 的小说创作任务
    
    Args:
        runner: 任务运行器（可以为 None，使用内部逻辑）
        evaluator: 评估器（可以为 None）
        results_dir: 结果目录
        mode: 模式（validation/test）
        data_limit: 数据限制
        unimem_enabled: 是否启用 UniMem（默认启用）
        personas_path: personas 文件路径（默认使用带记忆版本）
    """
    ***REMOVED*** 加载全局配置
    with open("config/global.yaml", "r") as f:
        global_config = yaml.safe_load(f)
    
    ***REMOVED*** 设置默认的 personas 路径
    if personas_path is None:
        personas_path = "personas/personas_with_memory.jsonl" if unimem_enabled else "personas/personas.jsonl"
    
    dataset = load_dataset(data_limit)
    result_path = os.path.join(results_dir, "novel_with_memory.jsonl")
    os.makedirs(results_dir, exist_ok=True)
    
    print(f"\n{'='*60}")
    print(f"小说创作任务（集成 UniMem）")
    print(f"{'='*60}")
    print(f"UniMem 启用: {unimem_enabled}")
    print(f"Personas 文件: {personas_path}")
    print(f"数据量: {len(dataset)}")
    print(f"{'='*60}\n")
    
    ***REMOVED*** 获取 max_step_num
    max_step_num = global_config.get('graph', {}).get('max_step_num', 5)
    
    with open(result_path, "w", encoding="utf-8") as fd:
        for idx, q in enumerate(tqdm(dataset, desc="处理任务")):
            task = format_question(q, idx)
            
            ***REMOVED*** 注册所有 Agent（使用带记忆的注册器）
            agent_global_registry_with_memory.register_all_agents(personas_path, unimem_enabled=unimem_enabled)
            agent_global_registry_with_memory.reset_all_agents()
            
            ***REMOVED*** 过滤工具类 Agent（必须在创建 AgentGraph 之前）
            filter_tool_agents()
            
            ***REMOVED*** 将带记忆的注册表同步到全局注册表（因为 AgentGraph 使用全局注册表）
            agent_global_registry.agents = agent_global_registry_with_memory.agents
            agent_global_registry.unique_agents = agent_global_registry_with_memory.unique_agents
            
            ***REMOVED*** 创建 AgentGraph（使用同步后的注册表）
            graph = AgentGraph()
            
            ***REMOVED*** 使用带记忆的 GraphReasoning
            reasoning = GraphReasoningWithMemory(
                task, 
                graph, 
                unimem_enabled=unimem_enabled
            )
            
            ***REMOVED*** 执行推理
            reasoning.start(None)
            final_ans, _ = reasoning.n_step(max_step_num)
            
            ***REMOVED*** 可视化（可选）
            reasoning.visualize_path()
            reasoning.visualize_graph()
            
            ***REMOVED*** 保存结果
            record = {
                "id": task["id"],
                "pred": final_ans,
                "unimem_enabled": unimem_enabled,
                "memories_retrieved": len(reasoning.retrieved_memories) if unimem_enabled else 0,
                "memories_stored": len(reasoning.stored_memories) if unimem_enabled else 0
            }
            fd.write(json.dumps(record, ensure_ascii=False) + "\n")
            fd.flush()
            
            ***REMOVED*** 输出记忆使用情况
            if unimem_enabled:
                print(f"\n任务 {idx}:")
                print(f"  检索记忆: {len(reasoning.retrieved_memories)} 条")
                print(f"  存储记忆: {len(reasoning.stored_memories)} 条")
                if reasoning.retrieved_memories:
                    print(f"  记忆示例: {reasoning.retrieved_memories[0].get('content', '')[:50]}...")


if __name__ == "__main__":
    ***REMOVED*** 使用示例
    from tasks.evaluator import BenchmarkEvaluator
    
    evaluator = BenchmarkEvaluator()
    results_dir = "./results/Novel_with_memory_validation"
    
    ***REMOVED*** 运行任务（启用 UniMem，使用带记忆的 personas）
    run(
        runner=None,
        evaluator=evaluator, 
        results_dir=results_dir, 
        mode="validation", 
        data_limit=2, 
        unimem_enabled=True,
        personas_path="personas/personas_with_memory.jsonl"
    )
