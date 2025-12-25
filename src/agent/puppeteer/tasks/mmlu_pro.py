import os
import json
import string
import pandas as pd
from tqdm import tqdm
from tasks.base.base_task import BaseTask
from agent.register.register import agent_global_registry
from inference.graph.agent_graph import AgentGraph
from inference.reasoning.reasoning import GraphReasoning


def load_dataset(mode, data_limit=None):
    path = os.path.join("data", "MMLU-Pro", f"{mode}.parquet")
    data = pd.read_parquet(path)
    return data[:data_limit] if data_limit else data


def format_question(task):
    options = [f"{letter}: {op}" for letter, op in zip(string.ascii_uppercase, task["options"])]
    prompt = f"The following are multiple choice questions (with answers) about {task['category']}."
    question = prompt + "\n" + task["question"] + "\n" + " ".join(options)
    return {
        "type": "MMLU-Pro",
        "Question": question,
        "Answer": task["answer"],
        "id": task["question_id"]
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
    dataset = load_dataset(mode, data_limit)
    result_path = os.path.join(results_dir, f"MMLU-Pro_{mode}.jsonl")
    acc = 0

    with open(result_path, "w", encoding="utf-8") as fd:
        for _, row in tqdm(dataset.iterrows(), total=len(dataset)):
            task = format_question(row)
            
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
            
            flag = evaluator.check_mmlu(final_ans, task["Answer"])
            if flag: 
                acc += 1
            record = {
                "id": task["id"],
                "pred": final_ans,
                "correct": flag
            }
            fd.write(json.dumps(record, ensure_ascii=False) + "\n")
