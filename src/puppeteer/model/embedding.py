import os
import yaml
import openai
import torch
import numpy as np
from typing import List
from chromadb import EmbeddingFunction, Embeddings
from model.model_utils import model_log_and_print
from tenacity import retry, stop_after_attempt, wait_exponential
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    with open("./config/global.yaml", "r", encoding="utf-8") as f:
        GLOBAL_CONFIG = yaml.safe_load(f)
except FileNotFoundError:
    raise FileNotFoundError("Global config file './config/global.yaml' not found!")

OPENAI_API_KEY = GLOBAL_CONFIG.get("api_keys", {}).get("openai_api_key")
BASE_URL = GLOBAL_CONFIG.get("api_keys", {}).get("openai_base_url", None)
MAX_RETRY_TIMES = GLOBAL_CONFIG.get("max_retry_times", 10)
MODEL_WEIGHT_PATH = GLOBAL_CONFIG.get("model_weight_path")

if BASE_URL:
    client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)
else:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)


class OpenAIEmbedding(EmbeddingFunction):
    @staticmethod
    @retry(wait=wait_exponential(min=5, max=10), stop=stop_after_attempt(MAX_RETRY_TIMES))
    def get_embedding(text) -> Embeddings:
        embedding_model = "text-embedding-ada-002"
        model_log_and_print(f"[Embedding] embedding from {embedding_model}")

        if isinstance(text, str):
            text = [text.replace("\n", " ")]
        else:
            text = [t.replace("\n", " ") for t in text]

        text = [t[:8191] if len(t) > 8191 else t for t in text]
        text = ["none"] if all(len(t) == 0 for t in text) else text

        model_log_and_print(f"[Embedding] {text}")

        response = client.embeddings.create(input=text, model=embedding_model)
        embeddings = [data.embedding for data in response.data]

        prompt_tokens = response.usage.prompt_tokens
        total_tokens = response.usage.total_tokens
        model_log_and_print(f"[Embedding] Token Usage\nPrompt Tokens: {prompt_tokens}\nTotal Tokens: {total_tokens}")

        return embeddings
    
    @property
    def dim(self):
        return 1536


class RewardModelTokenRepresentation():
    def __init__(self):
        self.model_name = "Skywork-Reward-V2-Qwen3-4B"
        ***REMOVED*** 从配置文件读取模型参数
        model_config = GLOBAL_CONFIG.get("model", {})
        self.batch_size = model_config.get("batch_size", 1)
        self.max_new_tokens = model_config.get("max_new_tokens", 1)
        self.max_length = model_config.get("max_length", 4096)
        self.truncate_length = model_config.get("truncate_length", 12000)
        
        ***REMOVED*** 使用更节省显存的配置
        ***REMOVED*** 尝试使用 CPU offload 来减少显存使用
        import os
        if os.getenv("USE_CPU_OFFLOAD", "false").lower() == "true":
            ***REMOVED*** 使用 CPU offload 将部分层移到 CPU
            device_map = "balanced_low_0"  ***REMOVED*** 将模型分层加载，部分在 CPU
        else:
            device_map = "auto"
        
        self.model = AutoModelForCausalLM.from_pretrained(
            MODEL_WEIGHT_PATH, 
            torch_dtype=torch.bfloat16, 
            device_map=device_map,
            low_cpu_mem_usage=True,  ***REMOVED*** 降低 CPU 内存使用
            max_memory={0: "10GiB", "cpu": "30GiB"} if device_map == "auto" else None  ***REMOVED*** 限制 GPU 显存使用
        )
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_WEIGHT_PATH)
        print("device: {}".format(self.model.device))
        print(f"Model config: batch_size={self.batch_size}, max_length={self.max_length}, truncate_length={self.truncate_length}")
        
    def truncate(self, messages):
        length = sum(len(message["content"]) for message in messages)
        
        while length > self.truncate_length:
            for message in messages:
                message["content"] = message["content"][-int(len(message["content"]) * 0.75):]  
            length = sum(len(message["content"]) for message in messages)  
        
        return messages

    def __call__(self, messages:List):
        with torch.no_grad():
            messages = self.truncate(messages)
            model_log_and_print("tokenizing")
            model_log_and_print(messages)
            tokenized_message = self.tokenizer.apply_chat_template(
                messages, 
                tokenize=True, 
                add_generation_prompt=False, 
                return_tensors="pt", 
                return_dict=True, 
                max_length=self.max_length,
                truncation=True  ***REMOVED*** 确保截断
            )
            model_log_and_print("tokenized done")
            
            ***REMOVED*** 获取模型设备（可能是 cuda 或 cpu）
            model_device = next(self.model.parameters()).device
            input_ids = tokenized_message['input_ids'].to(model_device)
            attention_mask = tokenized_message['attention_mask'].to(model_device)
            
            ***REMOVED*** 显存优化：清理缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            
            ***REMOVED*** 使用配置的批次大小和生成参数
            with torch.no_grad():  ***REMOVED*** 确保不使用梯度计算
                response_token_ids = self.model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,  
                    max_new_tokens=self.max_new_tokens, 
                    return_dict_in_generate=True, 
                    output_scores=True,
                    output_logits=True,
                    output_hidden_states=True,
                    do_sample=False,  ***REMOVED*** 禁用采样以节省显存
                    use_cache=True,  ***REMOVED*** 使用 KV cache 加速
                    pad_token_id=self.tokenizer.eos_token_id  ***REMOVED*** 设置 pad token
                )
            
            ***REMOVED*** 再次清理缓存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            reward = response_token_ids['scores'][0][0][0].item()
            hidden_states = response_token_ids.hidden_states  
            state = hidden_states[0][-1]
            last_state = state[:,-1,:]
            print(reward)
            return last_state, reward

    @property
    def dim(self):
        return 2560