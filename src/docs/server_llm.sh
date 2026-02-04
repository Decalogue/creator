***REMOVED*** 查看vllm进程
***REMOVED*** ps aux | grep -i vllm | grep -v grep

CUDA_VISIBLE_DEVICES=1 \
swift deploy \
    --model /root/data/AI/pretrain/Qwen2.5-7B-Instruct \
    --infer_backend vllm \
    --host 0.0.0.0 \
    --port 6002 \
    --vllm_gpu_memory_utilization 0.9 \
    --vllm_max_model_len 8192 \
    --max_new_tokens 4096 \
    --served_model_name qwen-2.5
