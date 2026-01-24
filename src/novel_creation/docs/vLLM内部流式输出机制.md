# vLLM 内部流式输出机制

vLLM 的流式输出在 **引擎层** 通过 **asyncio.Queue + 异步生成器** 实现，与 HTTP/SSE 解耦。本文梳理引擎内部如何 `yield` 增量结果。

---

## 0. 引擎与模型端：谁封装谁？模型端输出是什么？

**是的，引擎封装了模型端。** 引擎负责调度、请求管理、把模型输出整理成 `RequestOutput`；**模型端**（Worker / Model Runner）负责真正的 forward、采样，跑在单独进程或 Ray worker 里。

### 0.1 模型端的输出链路（Worker / Model Runner）

模型端每 **一步 decoding** 的产出大致如下：

```
model(input_ids, positions, ...)
    → hidden_states   # [batch, seq, hidden_dim]，Decoder 最后一层隐状态

model.compute_logits(hidden_states[logits_indices])
    → logits         # [num_tokens, vocab_size]，每个位置对词表未归一化分数

Sampler(logits, sampling_metadata)   # softmax + temperature / top_p / top_k 等
    → SamplerOutput:
         - sampled_token_ids: Tensor  # 本步采样的 token id
         - logprobs_tensors: 可选     # 各候选的 log 概率

封装并返回
    → ModelRunnerOutput:
         - req_ids, req_id_to_index
         - sampled_token_ids: list[list[int]]  # 按请求的本步新 token ids
         - logprobs: LogprobsLists 或 None
```

- **模型 forward** 只产出 **hidden_states**；**logits** 由 `model.compute_logits(...)` 在 **模型端** 内算出来。
- **Sampler** 在模型端内，消费 logits，产出 **token ids + logprobs**。  
因此，**模型端对引擎暴露的“输出”** 是 **token ids（及可选的 logprobs）**，即 `ModelRunnerOutput`，**没有** 原始 logits / hidden_states 再往上传。

### 0.2 引擎侧：从模型端输出到 RequestOutput

引擎拿到 `ModelRunnerOutput` 后，由 **Scheduler** 和 **OutputProcessor** 再加工：

```
Scheduler.update_from_output(scheduler_output, model_output)
    → EngineCoreOutputs   # 按 request_id 的列表，每项包含：
         - new_token_ids: list[int]   # 本步新生成的 token id
         - finish_reason, stop_reason # 是否结束、stop 原因
         - pooling_output 等（embedding 等非生成场景）

OutputProcessor.process_outputs(engine_core_outputs)
    for each EngineCoreOutput:
        Detokenizer.update(new_token_ids, ...)   # 增量 decode → 文本，stop 串检查
        make_request_output(...)
            → RequestOutput   # 含 outputs[].text, token_ids, logprobs, finish_reason
```

- **Detokenizer** 在引擎侧，对 **new_token_ids** 做增量解码 → **文本**，并做 stop 串检测。
- **RequestOutput** 里的 `outputs[0].text` 等，都是引擎在 **模型端之上** 叠的一层；模型端本身只给 **token ids**。

### 0.3 小结

| 层级 | 输出物 | 说明 |
|------|--------|------|
| **模型 forward** | `hidden_states` | 最后一层隐状态 |
| **模型端内** | `logits` → **SamplerOutput** | `compute_logits` + 采样 → token ids、logprobs |
| **模型端→引擎** | **ModelRunnerOutput** | 按请求的 `sampled_token_ids`、`logprobs` |
| **引擎** | **EngineCoreOutput** | `new_token_ids`、`finish_reason` 等 |
| **引擎→调用方** | **RequestOutput** | 经 **Detokenizer** 得到的 `text`、`token_ids`、`logprobs` |

**一句话**：**引擎封装模型端**；模型端输出 **token ids（+ logprobs）**，引擎再 **detokenize** 成 **RequestOutput** 的 `text` 等，供流式或非流式 API 使用。

### 0.4 模型端输出代码位置

**核心文件**：`vllm/v1/worker/gpu_model_runner.py`

#### 1. 模型 forward 与 logits 计算（约 2298-2331 行）

```python
# 2298-2304: 模型 forward
model_output = self.model(
    input_ids=input_ids,
    positions=positions,
    intermediate_tensors=intermediate_tensors,
    inputs_embeds=inputs_embeds,
    **model_kwargs,
)

# 2306-2312: 提取 hidden_states
if self.use_aux_hidden_state_outputs:
    hidden_states, aux_hidden_states = model_output
else:
    hidden_states = model_output
    aux_hidden_states = None

# 2330-2331: 计算 logits
sample_hidden_states = hidden_states[logits_indices]
logits = self.model.compute_logits(sample_hidden_states)
```

#### 2. 采样（约 2054-2092 行）

```python
def _sample(
    self, logits: Optional[torch.Tensor],
    spec_decode_metadata: Optional[SpecDecodeMetadata]
) -> SamplerOutput:
    sampling_metadata = self.input_batch.sampling_metadata
    if spec_decode_metadata is None:
        sampler_output = self.sampler(
            logits=logits,
            sampling_metadata=sampling_metadata,
        )
    else:
        # speculative decoding 分支
        ...
    return sampler_output
```

**调用位置**（约 2366-2367 行）：
```python
sampler_output = self._sample(logits, spec_decode_metadata)
```

#### 3. 构造并返回 ModelRunnerOutput（约 2426-2445 行）

```python
output = ModelRunnerOutput(
    req_ids=req_ids_output_copy,
    req_id_to_index=req_id_to_index_output_copy,
    sampled_token_ids=valid_sampled_token_ids,  # list[list[int]]
    logprobs=logprobs_lists,                     # LogprobsLists 或 None
    prompt_logprobs_dict=prompt_logprobs_dict,
    pooler_output=[],
    kv_connector_output=kv_connector_output,
    num_nans_in_logits=num_nans_in_logits,
)

if not self.use_async_scheduling:
    return output
else:
    return AsyncGPUModelRunnerOutput(...)  # 异步调度包装
```

#### 4. 数据类定义

- **SamplerOutput**：`vllm/v1/outputs.py` 约 74-81 行
  ```python
  @dataclass
  class SamplerOutput:
      sampled_token_ids: torch.Tensor  # [num_reqs, max_num_generated_tokens]
      logprobs_tensors: Optional[LogprobsTensors]
  ```

- **ModelRunnerOutput**：`vllm/v1/outputs.py` 约 99-120 行
  ```python
  @dataclass
  class ModelRunnerOutput:
      req_ids: list[str]
      req_id_to_index: dict[str, int]
      sampled_token_ids: list[list[int]]  # num_reqs x num_generated_tokens
      logprobs: Optional[LogprobsLists]
      prompt_logprobs_dict: dict[str, ...]
      ...
  ```

#### 5. 完整流程（execute_model 方法，约 2231-2445 行）

```python
@torch.inference_mode()
def execute_model(self, scheduler_output, ...) -> ModelRunnerOutput:
    # 1. 预处理：准备输入
    ...
    
    # 2. 模型 forward（2298-2304）
    model_output = self.model(...)
    hidden_states = model_output  # 或 model_output[0]
    
    # 3. 计算 logits（2330-2331）
    logits = self.model.compute_logits(hidden_states[logits_indices])
    
    # 4. 采样（2366-2367）
    sampler_output = self._sample(logits, spec_decode_metadata)
    
    # 5. 后处理：bookkeeping、整理数据（2404-2415）
    valid_sampled_token_ids, logprobs_lists, ... = self._bookkeeping_sync(...)
    
    # 6. 构造并返回 ModelRunnerOutput（2426-2435）
    return ModelRunnerOutput(
        req_ids=...,
        sampled_token_ids=valid_sampled_token_ids,
        logprobs=logprobs_lists,
        ...
    )
```

**总结**：模型端输出的核心代码在 **`gpu_model_runner.py` 的 `execute_model` 方法**（约 2231-2445 行），其中：
- **模型 forward**：2298-2304 行
- **logits 计算**：2330-2331 行
- **采样**：`_sample` 方法（2054-2092 行），在 2366-2367 行调用
- **返回 ModelRunnerOutput**：2426-2435 行

### 0.5 模型端的流式实现：模型端本身不做流式

**重要结论**：**模型端本身不做流式**，它只是**每步返回一次结果**。流式是在**引擎层**通过**循环调用模型端**实现的。

#### 模型端：同步、每步返回

模型端的 `execute_model` 方法是**同步的**（不是 async generator，没有 yield）：

```python
@torch.inference_mode()
def execute_model(
    self,
    scheduler_output: "SchedulerOutput",
    ...
) -> ModelRunnerOutput:  # 返回单个 ModelRunnerOutput，不是 Iterator/Generator
    # 1. 模型 forward
    model_output = self.model(...)
    
    # 2. 计算 logits、采样
    logits = self.model.compute_logits(...)
    sampler_output = self._sample(logits, ...)
    
    # 3. 返回本步的 ModelRunnerOutput
    return ModelRunnerOutput(
        sampled_token_ids=valid_sampled_token_ids,  # 本步的 token ids
        logprobs=logprobs_lists,
        ...
    )
```

- **每次调用** `execute_model`，只返回**本步**的 `ModelRunnerOutput`（包含本步新生成的 token ids）。
- **没有** yield、没有 async generator、没有流式迭代。

#### 引擎层：循环调用模型端，实现流式

流式是在**引擎层**实现的，通过**循环调用模型端**：

```python
# vllm/v1/engine/core.py 约 272-291 行
def step(self) -> tuple[dict[int, EngineCoreOutputs], bool]:
    """每步：调度、执行模型、更新 scheduler"""
    scheduler_output = self.scheduler.schedule()
    model_output = self.execute_model_with_error_logging(
        self.model_executor.execute_model,  # 调用模型端
        scheduler_output)
    engine_core_outputs = self.scheduler.update_from_output(
        scheduler_output, model_output)
    return engine_core_outputs, ...

# 引擎的后台循环（run_engine_loop）会不断调用 step()
async def run_engine_loop(self):
    while True:
        has_requests = await self.engine_step()  # 内部调用 step()
        if has_requests:
            # 每步产生一批 RequestOutput，通过 AsyncStream 推给调用方
            for request_output in request_outputs:
                stream.put(request_output)
        await asyncio.sleep(0)
```

**流程**：
1. **引擎的 `step()`** 调用 **模型端的 `execute_model()`**，得到本步的 `ModelRunnerOutput`。
2. 引擎把 `ModelRunnerOutput` 转成 `EngineCoreOutput`，再转成 `RequestOutput`。
3. 引擎通过 **`AsyncStream.put(request_output)`** 把本步的 `RequestOutput` 推给调用方。
4. **引擎循环**：继续 `step()` → 调用模型端 → 得到下一步结果 → `put` 进 stream → ...

#### 流式粒度

- **模型端**：每调用一次 `execute_model`，返回**本步**的 token ids（可能 1 个或多个 token，取决于 scheduler）。
- **引擎**：每 `step()` 一次，调用一次模型端，产生一个 `RequestOutput`，推给调用方。
- **调用方**：通过 `async for request_output in stream` 收到每个 `RequestOutput`，实现流式。

**因此**：模型端的"流式"实际上是**引擎循环调用模型端**，每次调用产生一步结果，引擎把这些结果**流式地推给调用方**。模型端本身是**同步、非流式**的。

---

## 1. 整体架构

```
AsyncLLMEngine.generate(prompt, sampling_params, request_id, ...)
    │
    ├─ add_request(...)  →  创建 AsyncStream，登记到 RequestTracker，加入引擎等待队列
    │
    └─ async for request_output in stream:   →  从 AsyncStream 的 asyncio.Queue 取
           yield request_output                   每次取到即 yield 给调用方

后台循环 run_engine_loop：
    │
    └─ engine_step()
           ├─ 从 RequestTracker 取 new_requests → 调用 engine.add_request_async 塞入引擎
           ├─ engine.step_async()  →  一次解码迭代，返回 List[RequestOutput]
           └─ 对每个 request_output：RequestTracker.process_request_output(ro)
                  → 找到对应 AsyncStream，stream.put(request_output)
```

- **generate** 返回的是 **async generator**，每次 `yield` 一个 `RequestOutput`。
- **AsyncStream** 内部用 **asyncio.Queue** 接收 `RequestOutput`；`generate` 通过 **async for ... in stream** 消费该 queue，即 **“有就取、取到就 yield”**。
- **RequestOutput** 的来源是 **LLMEngine 每轮 step** 产生的解码结果；通常 **每轮 step 产生一批新 token**，对应一次 `yield`。

---

## 2. 核心组件

### 2.1 AsyncStream（`vllm.engine.async_llm_engine`）

```python
class AsyncStream:
    """ 单个请求的 RequestOutput 流，可异步迭代 """

    def __init__(self, request_id: str) -> None:
        self.request_id = request_id
        self._queue: asyncio.Queue = asyncio.Queue()
        self._finished = False

    def put(self, item: Union[RequestOutput, Exception]) -> None:
        if self._finished:
            return
        self._queue.put_nowait(item)

    def finish(self) -> None:
        self._queue.put_nowait(StopAsyncIteration)
        self._finished = True

    async def __anext__(self) -> RequestOutput:
        result = await self._queue.get()
        if isinstance(result, Exception):
            raise result
        return result   # 通常是 RequestOutput
```

- **流式输出的“管道”**：引擎把 `RequestOutput` 往 `put()` 里塞，调用方通过 `async for x in stream` 触发 `__anext__`，即 `await self._queue.get()`，**边生产边消费**。
- `finish()` 往 queue 里放 `StopAsyncIteration`，消费端拿到的就是结束信号，迭代结束。

### 2.2 RequestTracker

- **add_request**：为每个请求创建一个 `AsyncStream`，并把 `(stream, request_dict)` 放入 `_new_requests`；下次 `engine_step` 会把这些请求真正 `add` 进 LLMEngine，并持有 `stream`。
- **process_request_output**：引擎 `step` 返回的 `RequestOutput` 按 `request_id` 找到对应 `AsyncStream`，调用 **`stream.put(request_output)`**，即把本轮步进产生的输出推给消费端。
- **abort_request**：结束请求时对对应 `stream` 调 **`finish()`**，往 queue 里放 `StopAsyncIteration`。

### 2.3 后台循环 `run_engine_loop`

```python
async def run_engine_loop(self):
    while True:
        if not has_requests_in_progress:
            await self._request_tracker.wait_for_new_requests()
        has_requests_in_progress = await self.engine_step()
        await asyncio.sleep(0)
```

- 有等待中的新请求就 `engine_step`；没有则 `wait_for_new_requests` 阻塞。
- **engine_step** 里：
  1. 从 `RequestTracker` 取 **new_requests**，调 `engine.add_request_async` 加入引擎；
  2. 调 **`engine.step_async()`** 做 **一次解码迭代**；
  3. 对返回的 **`request_outputs`** 逐个 **`process_request_output`** → **`stream.put(...)`**。

因此，**流式节奏**由 **step 频率** 决定：每 step 一次，就产生一批 `RequestOutput` 并 `put` 进 queue，`generate` 的 `async for` 就多 `yield` 一批。

### 2.4 AsyncLLMEngine.generate

```python
async def generate(self, prompt, sampling_params, request_id, ...) -> AsyncIterator[RequestOutput]:
    stream = await self.add_request(request_id, prompt, sampling_params, ...)
    async for request_output in stream:
        yield request_output
```

- **generate** 不做业务逻辑，只 **转发 stream 的迭代**；真正“谁在写流”的是 **engine_step → process_request_output → stream.put**。

---

## 3. 流式粒度：step 与 RequestOutput

- **LLMEngine.step_async()**（及其 sync 版 `step`）每轮做 **一次解码**：调度当前 batch、执行 model、更新 scheduler、解码得到新一轮 **token**，再封装成 **`RequestOutput`**。
- 每个 **RequestOutput** 里通常包含 **本轮新生成的内容**（例如 `outputs[0].text` 是 **到当前为止的完整生成文本**）；**增量** 一般由上层自己算，例如：

```python
# 例如 LlamaFactory vllm_engine 的 stream_chat
generated_text = ""
async for result in generator:
    delta_text = result.outputs[0].text[len(generated_text):]
    generated_text = result.outputs[0].text
    yield delta_text
```

- 所以 **vLLM 内部流式** 的粒度是 **“每个 engine step 一次 `RequestOutput`”**，而不是“每个 token 一次”。step 内部可能一次生成 1 个或多个 token，取决于 scheduler 与配置。

---

## 4. 与 OpenAI HTTP 流式的关系

- **vLLM 引擎层**：`AsyncStream` + `asyncio.Queue` + `generate()` 的 async generator，在 **进程内** 实现 **RequestOutput 的流式推送**。
- **OpenAI 兼容 API**（如 `/v1/chat/completions`，`stream=True`）：通常再包一层，把 `RequestOutput` 转成 **ChatCompletionChunk**，通过 **HTTP chunked / SSE** 推给客户端。
- 客户端用 **OpenAI SDK** 时，`stream=True` 对应的是 **HTTP 流式**；其底层即 [OpenAI 流式输出机制](./OpenAI流式输出机制.md) 里说的 **httpx stream → SSE → Stream[ChatCompletionChunk]**。  
- 因此：**vLLM 内部流式** 负责 **“何时、何内容” yield**；**HTTP/SSE 流式** 负责 **“如何通过网络推给调用方”**。

---

## 5. 小结

| 环节 | 机制 | 作用 |
|------|------|------|
| **AsyncStream** | `asyncio.Queue` + `put` / `__anext__` | 按请求缓存 `RequestOutput`，供 `generate` 按序消费 |
| **RequestTracker** | `add_request` / `process_request_output` / `abort` | 绑定 request ↔ stream，把引擎输出 `put` 进对应 stream |
| **run_engine_loop** | 循环 `engine_step` | 不断 step 引擎，产出新的 `RequestOutput` 并 `process` |
| **generate** | `async for ... in stream` 再 `yield` | 把 queue 里的 `RequestOutput` 以 async generator 形式交给上游 |
| **step_async** | 每轮一次解码 | 决定 **流式粒度**：每 step 一批 `RequestOutput` |

**一句话**：vLLM 的流式输出 = **引擎每 step 产生 `RequestOutput` → `process_request_output` 推入 `AsyncStream` 的 queue → `generate` 通过 `async for stream` 消费并 `yield`**；上层再据此算 delta 或转成 HTTP/SSE。
