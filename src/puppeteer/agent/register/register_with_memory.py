"""
带记忆功能的 Agent 注册器

支持使用 Reasoning_Agent_With_Memory 创建 Agent
"""

from typing import Any
from agent.reasoning_agent_with_memory import Reasoning_Agent_With_Memory
from utils.file_utils import iter_jsonl


class AgentRegisterWithMemory:
    """带记忆功能的 Agent 注册器"""
    
    def __init__(self, use_memory_agent=True):
        """
        初始化
        
        Args:
            use_memory_agent: 是否使用带记忆的 Agent（默认 True）
        """
        self.agents = {}
        self.unique_agents = {}
        self.use_memory_agent = use_memory_agent

    def _register_agent(self, name, agent):
        """注册 Agent"""
        if agent.hash in self.unique_agents:
            return 
        self.agents[name] = agent
        self.unique_agents[agent.hash] = agent
    
    @property 
    def agent_config(self):
        """获取 Agent 配置"""
        return self._agent_personas
    
    @property
    def agent_num(self):
        """获取 Agent 数量"""
        return len(self.unique_agents)
    
    @property
    def agent_names(self):
        """获取 Agent 名称列表"""
        return self.agents.keys()
    
    @property
    def agent_identifiers(self):
        """获取 Agent 标识符列表"""
        return self.unique_agents.keys()
    
    def get_agent_from_name(self, name):
        """根据名称获取 Agent"""
        return self.agents.get(name)
    
    def get_agent_from_idx(self, idx):
        """根据索引获取 Agent"""
        return self.unique_agents.get(idx) 

    def create_agent(self, name):
        """创建新的 Agent 实例"""
        agent = self.get_agent_from_name(name).reinitialize()
        if agent.hash in self.unique_agents:
            raise ValueError(f"Agent {name} with hash {agent.hash} already registered")
        self.unique_agents[agent.hash] = agent
        if agent is None:
            raise ValueError(f"Agent {name} not registered")
        return agent

    def register_all_agents(self, personas_path, unimem_enabled=True):
        """
        注册所有 Agent
        
        Args:
            personas_path: personas 文件路径
            unimem_enabled: 是否启用 UniMem（默认 True）
        """
        self._agent_personas = list(iter_jsonl(personas_path))
        self._total_agent_num = len(self._agent_personas)
        for index in range(self._total_agent_num):
            self._initialize_agent(index, unimem_enabled)
    
    def reset_all_agents(self):
        """重置所有 Agent"""
        for agent in self.unique_agents.values():
            agent.reset()
            
    def _initialize_agent(self, index, unimem_enabled=True):
        """
        初始化 Agent
        
        Args:
            index: Agent 索引
            unimem_enabled: 是否启用 UniMem
        """
        agent_role_name = self._agent_personas[index].get("name")
        agent_role_prompt = self._agent_personas[index].get("role_prompt")
        agent_model_type = self._agent_personas[index].get("model_type", None)
        agent_actions = self._agent_personas[index].get("actions", None)
        agent_policy = self._agent_personas[index].get("policy", None)
        
        if self._agent_personas[index].get("agent_type") == "reasoning":
            ***REMOVED*** 检查是否使用带记忆的 Agent
            if self.use_memory_agent and unimem_enabled:
                agent = Reasoning_Agent_With_Memory(
                    role=agent_role_name, 
                    role_prompt=agent_role_prompt, 
                    index=index,
                    model=agent_model_type,
                    actions=agent_actions,
                    policy=agent_policy,
                    unimem_enabled=unimem_enabled
                )
            else:
                ***REMOVED*** 使用原始的 Reasoning_Agent
                from agent.reasoning_agent import Reasoning_Agent
                agent = Reasoning_Agent(
                    role=agent_role_name, 
                    role_prompt=agent_role_prompt, 
                    index=index,
                    model=agent_model_type,
                    actions=agent_actions,
                    policy=agent_policy
                )
        
        self._register_agent(agent_role_name, agent)

    def __getattribute__(self, name: str) -> Any:
        return super().__getattribute__(name)


***REMOVED*** 全局注册器实例
agent_global_registry_with_memory = AgentRegisterWithMemory(use_memory_agent=True)

