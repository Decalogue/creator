import os
import json
import string
import pandas as pd
from tqdm import tqdm
from tasks.base.base_task import BaseTask
from agent.register.register import agent_global_registry
from inference.graph.agent_graph import AgentGraph
from inference.reasoning.reasoning import GraphReasoning


def load_dataset(data_limit=None):
    path = "./data/Novel/novel.jsonl"
    with open(path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f]
    return data[:data_limit] if data_limit else data


def format_question(q, idx):
    question = f'根据小说简介生成小说大纲。\n***REMOVED******REMOVED*** 小说简介\n{q["introduction"]}\n\n输出：'
    return {
        "type": "Novel",
        "Question": question,
        "Answer": q["outline"],
        "Introduction": q["introduction"],  ***REMOVED*** 添加简介，用于评估
        "id": idx
    }


def filter_tool_agents():
    """
    过滤掉工具类 Agent，只保留推理类 Agent
    对于 MMLU-Pro 选择题任务，不需要工具类 Agent（文件读取、网络搜索、代码执行等）
    """
    ***REMOVED*** 需要过滤掉的工具类 Agent 名称
    drop_tool_agent_names = {
        "FileAgent",       ***REMOVED*** 文件读取
        "ArxivAgent",      ***REMOVED*** arXiv 搜索
        "BingAgent",       ***REMOVED*** Bing 搜索
        "WebsiteAgent",    ***REMOVED*** 网站访问
        "PythonAgent_qwen" ***REMOVED*** Python 代码执行
    }
    
    ***REMOVED*** 获取所有已注册的 Agent，包括 unique_agents 和 agents
    all_agents = list(agent_global_registry.unique_agents.values())
    all_agent_names = list(agent_global_registry.agents.keys())
    
    ***REMOVED*** 过滤
    filtered_agents = {
        agent.hash: agent 
        for agent in all_agents 
        if agent.role not in drop_tool_agent_names
    }
    
    filtered_agent_names = {
        name: agent 
        for name, agent in agent_global_registry.agents.items()
        if agent.role not in drop_tool_agent_names
    }
    
    ***REMOVED*** 更新注册表中的 unique_agents 和 agents
    agent_global_registry.unique_agents = filtered_agents
    agent_global_registry.agents = filtered_agent_names
    
    ***REMOVED*** 打印过滤结果
    filtered_roles = [a.role for a in filtered_agents.values()]
    removed_roles = [a.role for a in all_agents if a.role in drop_tool_agent_names]
    print(f"Filtered out {len(removed_roles)} tool agents: {removed_roles}")
    print(f"Remaining {len(filtered_roles)} reasoning agents: {filtered_roles}")


def run(runner, evaluator, results_dir, mode, data_limit=None):
    dataset = load_dataset(data_limit)
    result_path = os.path.join(results_dir, "novel.jsonl")

    with open(result_path, "w", encoding="utf-8") as fd:
        for idx, q in enumerate(tqdm(dataset)):
            task = format_question(q, idx)

            ***REMOVED*** 注册所有 Agent
            agent_global_registry.register_all_agents(runner.personas_path)
            agent_global_registry.reset_all_agents()
            
            ***REMOVED*** 在每次推理前过滤工具类 Agent
            ***REMOVED*** 注意：需要在 setup_reasoning 之前调用，因为 AgentGraph 在 setup_reasoning 中初始化
            filter_tool_agents()
            
            ***REMOVED*** 创建过滤后的 AgentGraph
            graph = AgentGraph()
            ***REMOVED*** 创建一个自定义的 setup_reasoning
            reasoning = GraphReasoning(task, graph)
            
            ***REMOVED*** 执行推理
            reasoning.start(runner.save_state if runner.save_state else None)
            runner.save_state = False
            
            final_ans, _ = reasoning.n_step(runner.max_step_num)
            
            reasoning.visualize_path()
            reasoning.visualize_graph()

            record = {
                "id": task["id"],
                "pred": final_ans,
            }
            fd.write(json.dumps(record, ensure_ascii=False) + "\n")
