# OpenAI 库流式输出（stream=True）机制说明

针对 `client.chat.completions.create(..., stream=True)`，流式输出的核心逻辑分布在 **OpenAI** 与 **httpx** 两层。

---

## 1. 调用入口与参数传递

**你的代码**（`deepseek.py`）：

```python
response = client.chat.completions.create(
    model="ep-20251209150604-gxb42",
    messages=messages,
    stream=True,   # 触发流式
    max_tokens=max_new_tokens,
)
# response 实为 Stream[ChatCompletionChunk]，可 for chunk in response 迭代
```

**OpenAI 库内部**：

- `resources/chat/completions/completions.py` 里 `create()` 调用 `_post(..., stream=stream, stream_cls=Stream[ChatCompletionChunk])`
- `_base_client.py` 的 `request()` 把 `stream` 传给 **httpx**，并在解析响应时使用 `stream_cls`

---

## 2. HTTP 层：httpx 的 `stream=True`

**位置**：`openai/_base_client.py` 约 982–985 行

```python
response = self._client.send(
    request,
    stream=stream or self._should_stream_response_body(request=request),
    **kwargs,
)
```

当 `stream=True` 时，httpx 的 `Client.send(stream=True)`：

- **不**一次性读取完响应体
- 返回的 `httpx.Response` 的 `response.stream` 是一个 **按块生成字节的迭代器**，数据来自底层 transport（如 HTTP/1.1 分块传输）

---

## 3. httpx.Response 的 `iter_bytes()`：字节流迭代

**位置**：`httpx/_models.py` 约 884–905、935–958 行

```python
def iter_bytes(self, chunk_size: int | None = None) -> typing.Iterator[bytes]:
    """ decoded response content 的字节迭代器 """
    # ...
    for raw_bytes in self.iter_raw():   # 实际从 self.stream 读
        decoded = decoder.decode(raw_bytes)
        for chunk in chunker.decode(decoded):
            yield chunk
    # ...

def iter_raw(self, chunk_size: int | None = None) -> typing.Iterator[bytes]:
    """ 原始响应体的字节迭代 """
    # ...
    for raw_stream_bytes in self.stream:   # 关键：遍历 response.stream
        self._num_bytes_downloaded += len(raw_stream_bytes)
        for chunk in chunker.decode(raw_stream_bytes):
            yield chunk
    # ...
    self.close()
```

要点：

- `iter_bytes()` 内部用 `iter_raw()`
- `iter_raw()` 直接 **`for raw_stream_bytes in self.stream`**，即按网络到达顺序逐块 `yield` 字节
- 因此 **“流式”** 的本质是：**response.stream 的迭代**，每迭代一次就消费一块从服务端刚到达的数据

---

## 4. OpenAI 的 SSE 解析与 `Stream` 迭代

**位置**：`openai/_streaming.py`

### 4.1 `Stream` 类（同步）

```python
class Stream(Generic[_T]):
    def __init__(self, *, cast_to, response: httpx.Response, client):
        self.response = response
        self._decoder = client._make_sse_decoder()   # SSEDecoder
        self._iterator = self.__stream__()

    def __iter__(self):
        for item in self._iterator:
            yield item

    def _iter_events(self) -> Iterator[ServerSentEvent]:
        yield from self._decoder.iter_bytes(self.response.iter_bytes())  # 关键

    def __stream__(self) -> Iterator[_T]:
        # ...
        for sse in self._iter_events():   # 遍历 SSE 事件
            if sse.data.startswith("[DONE]"):
                break
            data = sse.json()
            # 解析 error、thread.* 等
            yield process_data(data=data, cast_to=cast_to, response=response)  # 转为 ChatCompletionChunk
        finally:
            response.close()
```

流程概括：

1. 用 **`response.iter_bytes()`** 拿到 httpx 的字节流（即上一节的按块迭代）
2. 交给 **`SSEDecoder.iter_bytes()`**，按 SSE 协议解析成一个个 **`ServerSentEvent`**
3. 对每个 SSE 的 `data` 做 `json()`，再 `process_data` 成 `ChatCompletionChunk`
4. **`__stream__`** 里 `yield` 这些 chunk，所以 **`for chunk in response`** 实际就是在消费这个生成器

因此，**控制流式输出的核心** 有两处：

- **字节级**：`httpx.Response.iter_bytes()` → `iter_raw()` → **`self.stream` 的迭代**
- **事件级**：`SSEDecoder.iter_bytes()` 把字节流切成 SSE 事件，再 `__stream__` 里逐个 `yield` 解析后的 chunk

### 4.2 `SSEDecoder`：按 SSE 规范切事件

**位置**：`openai/_streaming.py` 约 269–371 行

```python
class SSEDecoder:
    def iter_bytes(self, iterator: Iterator[bytes]) -> Iterator[ServerSentEvent]:
        """ 输入字节迭代器，输出 ServerSentEvent 迭代器 """
        for chunk in self._iter_chunks(iterator):
            for raw_line in chunk.splitlines():
                line = raw_line.decode("utf-8")
                sse = self.decode(line)   # 解析 event/data/id/retry
                if sse:
                    yield sse

    def _iter_chunks(self, iterator: Iterator[bytes]) -> Iterator[bytes]:
        """ 按 SSE 事件边界（双换行）切分 """
        data = b""
        for chunk in iterator:
            for line in chunk.splitlines(keepends=True):
                data += line
                if data.endswith((b"\r\r", b"\n\n", b"\r\n\r\n")):
                    yield data
                    data = b""
        if data:
            yield data

    def decode(self, line: str) -> ServerSentEvent | None:
        # 解析 event: / data: / id: / retry:，空行时返回一个 ServerSentEvent
        # 见 https://html.spec.whatwg.org/multipage/server-sent-events.html
```

SSE 的 **事件边界** 是双换行（`\n\n` / `\r\n\r\n` 等）。**`_iter_chunks`** 在拿到字节块后拼 buffer，遇到双换行就 `yield` 一个完整事件，**`decode`** 再拆成 `event`、`data` 等字段。

---

## 5. 响应解析时如何返回 `Stream`

**位置**：`openai/_response.py` 约 141–166 行

当 `stream=True` 且使用默认 `stream_cls` 时，`BaseAPIResponse._parse()` 会：

```python
if self._is_sse_stream:
    # ...
    return self._stream_cls(
        cast_to=extract_stream_chunk_type(self._stream_cls),
        response=self.http_response,   # 原始 httpx.Response
        client=cast(Any, self._client),
    )
```

也就是说，**`create(..., stream=True)` 的返回值** 是这个 `Stream` 实例，它包装了 **同一个 httpx.Response**。  
你在 **`for chunk in response`** 时，才会驱动：

1. `Stream.__iter__` → `__stream__`
2. `_iter_events` → `decoder.iter_bytes(response.iter_bytes())`
3. `response.iter_bytes()` → `iter_raw()` → **`response.stream` 的迭代**
4. 网络上一有数据，transport 就往 `stream` 里塞，迭代就能拿到新块，从而形成 **真正的流式消费**。

---

## 6. 总结：流式输出的控制链

| 层级 | 位置 | 作用 |
|------|------|------|
| **API** | `completions.create(stream=True)` | 传 `stream`、`stream_cls`，决定用流式解析 |
| **HTTP** | `_base_client.request` → `httpx.Client.send(stream=True)` | 响应体不一次性读入，`Response.stream` 为按块迭代器 |
| **字节流** | `httpx.Response.iter_raw()` | `for raw_stream_bytes in self.stream`，**真正按网络到达顺序 yield 字节** |
| **解码** | `Response.iter_bytes()` | 对 `iter_raw()` 做 decode（如 gzip 等） |
| **SSE** | `_streaming.SSEDecoder.iter_bytes()` | 按 `\n\n` 等切 SSE 事件，`decode()` 成 `ServerSentEvent` |
| **业务** | `_streaming.Stream.__stream__()` | 解析 JSON、`process_data`，**yield `ChatCompletionChunk`** |

因此，**OpenAI 库控制流式输出的机制** 可以归纳为：

1. **`stream=True`** 传给 httpx → 响应体通过 **`response.stream`** 按块迭代，不缓冲整份 body。
2. **`Stream`** 通过 **`response.iter_bytes()`** 消费该字节流，经 **SSEDecoder** 拆成 SSE 事件。
3. 每得到一个 SSE 的 `data`，就解析成一个 **`ChatCompletionChunk`** 并 **`yield`**，供 `for chunk in response` 使用。

若要 **改动流式行为**（例如缓冲、节流、截断），最底层可改 **transport / `response.stream`** 的消费方式；在 OpenAI 侧可改 **`Stream.__stream__`** 或 **`SSEDecoder.iter_bytes` / `_iter_chunks`** 的逻辑。

---

## 7. 相关源码路径（本机）

- **OpenAI**
  - `.../site-packages/openai/_streaming.py`：`Stream`、`AsyncStream`、`SSEDecoder`、`ServerSentEvent`
  - `.../site-packages/openai/_response.py`：`BaseAPIResponse._parse` 里构造 `Stream`
  - `.../site-packages/openai/_base_client.py`：`request` 里 `send(stream=...)`、`_process_response`
  - `.../site-packages/openai/resources/chat/completions/completions.py`：`create` 传 `stream`、`stream_cls`
- **httpx**
  - `.../site-packages/httpx/_models.py`：`Response.iter_bytes`、`iter_raw`、`self.stream` 的迭代
  - `.../site-packages/httpx/_client.py`：`send(stream=...)` 及 `ResponseStream` 等

---

## 8. 与 vLLM 的关系

当后端是 **vLLM**（或 swift deploy + vLLM）时，**服务端** 的流式在 vLLM **引擎内部** 实现：通过 **AsyncStream + asyncio.Queue** 每 step 产出 `RequestOutput`，再转成 SSE 通过 HTTP 推给客户端。  

客户端用 **OpenAI SDK `stream=True`** 消费的，即是上述 HTTP/SSE 流；**vLLM 内部** 的流式机制见 → [vLLM 内部流式输出机制](./vLLM内部流式输出机制.md)。
