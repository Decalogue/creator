import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Input,
  Button,
  Space,
  Typography,
  Avatar,
  Tag,
  Tooltip,
  Spin,
  Segmented,
  Select,
  Modal,
  List,
  Checkbox,
  InputNumber,
  Popconfirm,
  message,
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  DatabaseOutlined,
  EditOutlined,
  ThunderboltOutlined,
  BulbOutlined,
  SafetyCertificateOutlined,
  MenuUnfoldOutlined,
  MenuFoldOutlined,
  LinkOutlined,
  ReloadOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { motion, AnimatePresence } from 'framer-motion';
import { OrchestrationFlow } from '@/components/creator/OrchestrationFlow';
import { MemoryGraphD3 } from '@/components/creator/MemoryGraphD3';
import { MemoryGraphThree } from '@/components/creator/MemoryGraphThree';
import { MemoryDetailDrawer } from '@/components/creator/MemoryDetailDrawer';
import type { GraphNode, MemoryGraphData } from '@/components/creator/memoryGraphData';
import { CREATOR_THEME } from '@/components/creator/creatorTheme';
import { md } from '@/utils/markdown';

declare const API_URL: string;

const T = CREATOR_THEME;
/** 顶栏表单控件统一字号，保证前卷/本卷/当前作品视觉一致 */
const HEADER_CONTROL_FONT_SIZE = 13;

const CREATOR_STORAGE_KEYS = {
  projectId: 'creator_projectId',
  mode: 'creator_mode',
  messages: 'creator_messages',
} as const;
const CREATOR_MESSAGES_MAX = 50;
const CREATOR_MESSAGE_CONTENT_MAX = 3000;

const { TextArea } = Input;
const { Text } = Typography;

const API_BASE = API_URL;

/** 提交创作任务：仅等待返回 task_id，短超时即可 */
const CREATOR_SUBMIT_TIMEOUT_MS = 15 * 1000;
/** 轮询间隔 */
const CREATOR_POLL_INTERVAL_MS = 2500;
/** Stream 超时（单次创作/续写） */
/** 流式创作单次请求最长等待 300s，超时则前端 abort */
const CREATOR_STREAM_TIMEOUT_MS = 300 * 1000;

/** 后端 step 与前端 Agent 映射（P1 编排事件） */
function stepToAgentKey(step: string): AgentKey | null {
  const map: Record<string, AgentKey> = { plan: 'planner', memory: 'memory', write: 'writer' };
  return map[step] ?? null;
}

/** 创作流式 API：POST /api/creator/stream，解析 SSE 事件并回调；返回 stream_end 的 payload */
async function fetchCreatorStream(
  body: Record<string, unknown>,
  onEvent: (ev: { type: string; step?: string; data?: Record<string, unknown>; code?: number; message?: string; content?: string; project_id?: string; chapter_number?: number }) => void
): Promise<{ code: number; message: string; content?: string; project_id?: string; chapter_number?: number }> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CREATOR_STREAM_TIMEOUT_MS);
  const res = await fetch(`${API_BASE}/api/creator/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: controller.signal,
  }).finally(() => clearTimeout(timeoutId));
  if (!res.ok || !res.body) {
    throw new Error(res.status === 503 ? '创作服务未就绪' : res.status === 400 ? 'stream 仅支持 mode=create 或 continue' : `HTTP ${res.status}`);
  }
  const reader = res.body.getReader();
  const dec = new TextDecoder();
  let buffer = '';
  let streamEnd: { code?: number; message?: string; content?: string; project_id?: string; chapter_number?: number } = { code: 1, message: '未收到 stream_end' };
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += dec.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() ?? '';
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const json = JSON.parse(line.slice(6).trim()) as {
            type?: string;
            step?: string;
            data?: Record<string, unknown>;
            code?: number;
            message?: string;
            content?: string;
            project_id?: string;
            chapter_number?: number;
          };
          onEvent(json);
          if (json.type === 'stream_end') {
            streamEnd = {
              code: json.code ?? 0,
              message: json.message ?? '',
              content: json.content,
              project_id: json.project_id,
              chapter_number: json.chapter_number,
            };
          }
        } catch (_) {
          // ignore parse
        }
      }
    }
  }
  if (buffer.startsWith('data: ')) {
    try {
      const json = JSON.parse(buffer.slice(6).trim()) as { type?: string; step?: string; data?: Record<string, unknown>; code?: number; message?: string; content?: string };
      onEvent(json);
      if (json.type === 'stream_end') {
        streamEnd = { code: json.code ?? 0, message: json.message ?? '', content: json.content, project_id: json.project_id, chapter_number: json.chapter_number };
      }
    } catch (_) {}
  }
  return streamEnd as { code: number; message: string; content?: string; project_id?: string; chapter_number?: number };
}

function fetchCreatorSubmit(body: Record<string, unknown>): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), CREATOR_SUBMIT_TIMEOUT_MS);
  return fetch(`${API_BASE}/api/creator/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal: controller.signal,
  }).finally(() => clearTimeout(timeoutId));
}

/** 轮询任务状态直至 done 或 failed */
async function pollCreatorTask(
  taskId: string
): Promise<{
  status: 'done' | 'failed';
  code?: number;
  message?: string;
  content?: string;
  project_id?: string;
  chapter_number?: number;
  error?: string;
}> {
  for (;;) {
    const res = await fetch(`${API_BASE}/api/creator/task/${encodeURIComponent(taskId)}`);
    const raw = await res.json().catch(() => ({}));
    const status = raw.status as string;
    if (status === 'done') {
      return {
        status: 'done',
        code: raw.code,
        message: raw.message,
        content: raw.content,
        project_id: raw.project_id,
        chapter_number: raw.chapter_number,
      };
    }
    if (status === 'failed' || status === 'unknown') {
      return { status: 'failed', error: raw.error || raw.message || '任务失败' };
    }
    await new Promise((r) => setTimeout(r, CREATOR_POLL_INTERVAL_MS));
  }
}

/** 安全解析创作 API 响应：提交返回 task_id，轮询结果返回 code/content 等 */
async function parseCreatorRunResponse(
  res: Response
): Promise<{
  data: { code?: number; message?: string; content?: string; chapter_number?: number; project_id?: string; task_id?: string };
  error: string | null;
}> {
  let data: {
    code?: number;
    message?: string;
    content?: string;
    chapter_number?: number;
    project_id?: string;
    task_id?: string;
  } = { code: 1, message: '' };
  try {
    const raw = await res.json();
    if (raw && typeof raw === 'object') data = raw;
  } catch {
    return {
      data: { code: 1, message: '' },
      error: res.ok ? '后端返回格式异常' : `后端异常 (HTTP ${res.status})，请确认服务已启动且地址正确`,
    };
  }
  if (!res.ok) {
    const msg = (data && data.message) || `HTTP ${res.status}`;
    return { data: { ...data, code: 1, message: msg }, error: msg };
  }
  return { data, error: null };
}

// 智能体定义：记忆为通用支撑（实体/关系/事实/原子笔记），排首位；其余为创作流水线
const AGENTS = [
  { key: 'memory', name: '记忆', icon: <DatabaseOutlined />, color: '#06b6d4' },
  { key: 'planner', name: '大纲', icon: <BulbOutlined />, color: '#f59e0b' },
  { key: 'writer', name: '写手', icon: <EditOutlined />, color: '#8b5cf6' },
  { key: 'editor', name: '润色', icon: <EditOutlined />, color: '#10b981' },
  { key: 'qa', name: '质检', icon: <SafetyCertificateOutlined />, color: '#ec4899' },
] as const;

type AgentKey = (typeof AGENTS)[number]['key'];

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  ts: Date;
  agent?: AgentKey;
  streaming?: boolean;
}

const CreatorPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<'create' | 'continue' | 'polish' | 'chat'>('create');
  const [orchestrationOpen, setOrchestrationOpen] = useState(true);
  const [memoryOpen, setMemoryOpen] = useState(true);
  const [memoryView, setMemoryView] = useState<'list' | 'graph'>('list');
  const [graphMode, setGraphMode] = useState<'2d' | '3d'>('2d');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [orchestration, setOrchestration] = useState<AgentKey[]>([]);
  const [activeAgent, setActiveAgent] = useState<AgentKey | null>(null);
  const [graphSize, setGraphSize] = useState({ width: 420, height: 340 });
  const [projectId, setProjectId] = useState('完美之墙');
  const [projectList, setProjectList] = useState<string[]>([]);
  const [projectChapters, setProjectChapters] = useState<{ number: number; title: string; summary?: string; has_file: boolean }[]>([]);
  const [chapterListOpen, setChapterListOpen] = useState(false);
  /** 新作大纲目标章数（默认 100）；接续前卷时用 volumeTargetChapters */
  const [createTargetChapters, setCreateTargetChapters] = useState(100);
  /** 章节续写时是否注入 EverMemOS 云端检索结果（可关闭以对比测试） */
  const [useEvermemosContext, setUseEvermemosContext] = useState(true);
  /** 接续前卷（仅大纲模式）：前卷作品、本卷起始章、本卷章数、本卷作品名 */
  const [continueFromVolume, setContinueFromVolume] = useState(false);
  const [previousProjectId, setPreviousProjectId] = useState('');
  const [volumeStartChapter, setVolumeStartChapter] = useState(101);
  const [volumeTargetChapters, setVolumeTargetChapters] = useState(100);
  const [newVolumeProjectId, setNewVolumeProjectId] = useState('');
  const [memoryListPage, setMemoryListPage] = useState(1);
  const MEMORY_LIST_PAGE_SIZE = 10;
  /** 云端记忆分页与展开 */
  const [cloudPage, setCloudPage] = useState(1);
  const CLOUD_PAGE_SIZE = 8;
  const [expandedCloudKey, setExpandedCloudKey] = useState<string | null>(null);

  const [memoryEntities, setMemoryEntities] = useState<Array<{ id: string; name: string; type?: string; brief?: string }>>([]);
  const [memoryGraph, setMemoryGraph] = useState<MemoryGraphData>({ nodes: [], links: [] });
  const [memoryRecents, setMemoryRecents] = useState<string[]>([]);
  /** 云端记忆（EverMemOS）：列表视图下展示 */
  const [memoryCloud, setMemoryCloud] = useState<Array<{ content: string; id?: string }>>([]);
  const [evermemosAvailable, setEvermemosAvailable] = useState(false);
  const [memoryLoading, setMemoryLoading] = useState(false);
  const [retrievalDemoLoading, setRetrievalDemoLoading] = useState(false);
  const [retrievalDemoResult, setRetrievalDemoResult] = useState<Array<{ query_type: string; query: string; result_count: number; excerpts: string[] }> | null>(null);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const streamEndRef = useRef<Set<string>>(new Set());
  /** 刷新后是否已追加过「可输入写N章继续」提示，避免重复追加 */
  const hasAppendedResumeHintRef = useRef(false);

  /** 刷新后恢复：当前作品、模式、最近对话 */
  useEffect(() => {
    try {
      const savedProjectId = localStorage.getItem(CREATOR_STORAGE_KEYS.projectId);
      if (savedProjectId && typeof savedProjectId === 'string' && savedProjectId.trim()) {
        setProjectId(savedProjectId.trim());
      }
      const savedMode = localStorage.getItem(CREATOR_STORAGE_KEYS.mode);
      if (savedMode && ['create', 'continue', 'polish', 'chat'].includes(savedMode)) {
        setMode(savedMode as 'create' | 'continue' | 'polish' | 'chat');
      }
      const raw = localStorage.getItem(CREATOR_STORAGE_KEYS.messages);
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) {
          const restored: Message[] = parsed.slice(0, CREATOR_MESSAGES_MAX).map((m: { id?: string; role?: string; content?: string; agent?: AgentKey; ts?: string }) => ({
            id: typeof m.id === 'string' ? m.id : `restored_${Date.now()}_${Math.random().toString(36).slice(2)}`,
            role: m.role === 'user' || m.role === 'assistant' ? m.role : 'assistant',
            content: typeof m.content === 'string' ? m.content : '',
            ts: m.ts ? new Date(m.ts) : new Date(),
            agent: m.agent,
            streaming: false,
          }));
          setMessages(restored);
          // 刷新后任务已中断，不再恢复写手为「执行中」，指挥中心保持待机，避免误导
        }
      }
    } catch (_) {
      // ignore parse/storage errors
    }
  }, []);

  /** 持久化当前作品、模式 */
  useEffect(() => {
    try {
      if (projectId) localStorage.setItem(CREATOR_STORAGE_KEYS.projectId, projectId);
      localStorage.setItem(CREATOR_STORAGE_KEYS.mode, mode);
    } catch (_) {}
  }, [projectId, mode]);

  /** 持久化最近对话（保留进度可见） */
  useEffect(() => {
    if (messages.length === 0) return;
    try {
      const toSave = messages.slice(-CREATOR_MESSAGES_MAX).map((m) => ({
        id: m.id,
        role: m.role,
        content: typeof m.content === 'string' && m.content.length > CREATOR_MESSAGE_CONTENT_MAX
          ? m.content.slice(0, CREATOR_MESSAGE_CONTENT_MAX) + '…'
          : m.content,
        agent: m.agent,
        ts: m.ts instanceof Date ? m.ts.toISOString() : new Date().toISOString(),
      }));
      localStorage.setItem(CREATOR_STORAGE_KEYS.messages, JSON.stringify(toSave));
    } catch (_) {}
  }, [messages]);

  useEffect(() => {
    const el = graphContainerRef.current;
    if (!el || memoryView !== 'graph') return;
    const ro = new ResizeObserver((entries) => {
      const { width, height } = entries[0].contentRect;
      setGraphSize({ width: Math.max(280, width), height: Math.max(260, height) });
    });
    ro.observe(el);
    return () => ro.disconnect();
  }, [memoryView]);

  const fetchMemory = useCallback(() => {
    setMemoryLoading(true);
    const q = new URLSearchParams({ project_id: projectId });
    Promise.all([
      fetch(`${API_BASE}/api/memory/entities?${q}`).then((r) => (r.ok ? r.json() : [])),
      fetch(`${API_BASE}/api/memory/graph?${q}`).then((r) => (r.ok ? r.json() : { nodes: [], links: [] })),
      fetch(`${API_BASE}/api/memory/recents?${q}`).then((r) => (r.ok ? r.json() : [])),
      fetch(`${API_BASE}/api/memory/evermemos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ project_id: projectId, top_k: 50 }),
      }).then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([entities, graph, recents, cloud]) => {
        setMemoryEntities(Array.isArray(entities) ? entities : []);
        setMemoryGraph(
          graph && Array.isArray(graph.nodes)
            ? { nodes: graph.nodes, links: graph.links || [] }
            : { nodes: [], links: [] }
        );
        setMemoryRecents(Array.isArray(recents) ? recents : []);
        setMemoryCloud(Array.isArray(cloud) ? cloud : []);
      })
      .catch(() => {})
      .finally(() => setMemoryLoading(false));
  }, [projectId]);

  useEffect(() => {
    if (!memoryOpen) return;
    fetchMemory();
  }, [memoryOpen, projectId, fetchMemory]);

  /** 拉取后端配置（EverMemOS 是否已配置），用于云端记忆空状态文案 */
  useEffect(() => {
    fetch(`${API_BASE}/api/config`)
      .then((r) => (r.ok ? r.json() : {}))
      .then((c: { evermemos_available?: boolean }) => setEvermemosAvailable(Boolean(c.evermemos_available)))
      .catch(() => {});
  }, []);

  useEffect(() => {
    setMemoryListPage(1);
  }, [projectId]);

  useEffect(() => {
    setCloudPage(1);
    setExpandedCloudKey(null);
  }, [projectId]);

  useEffect(() => {
    const maxPage = Math.ceil(memoryCloud.length / CLOUD_PAGE_SIZE) || 1;
    setCloudPage((p) => Math.min(p, maxPage));
  }, [memoryCloud.length]);

  const fetchProjectList = useCallback(() => {
    fetch(`${API_BASE}/api/creator/projects`)
      .then((r) => (r.ok ? r.json() : []))
      .then((list: string[]) => setProjectList(Array.isArray(list) ? list : []))
      .catch(() => setProjectList([]));
  }, []);
  useEffect(() => {
    fetchProjectList();
  }, [fetchProjectList]);

  useEffect(() => {
    if (!projectId) return;
    fetch(`${API_BASE}/api/creator/chapters?project_id=${encodeURIComponent(projectId)}`)
      .then((r) => (r.ok ? r.json() : { chapters: [], total: 0 }))
      .then((data: { chapters?: { number: number; title: string; summary?: string; has_file: boolean }[]; total?: number }) => {
        setProjectChapters(Array.isArray(data.chapters) ? data.chapters : []);
      })
      .catch(() => setProjectChapters([]));
  }, [projectId]);

  /** 刷新后：若最后一条是「撰写中」且当前作品已有章节写入，追加一次「可输入写N章继续」提示 */
  useEffect(() => {
    if (hasAppendedResumeHintRef.current || messages.length === 0 || projectChapters.length === 0) return;
    const last = messages[messages.length - 1];
    if (last?.role !== 'assistant' || typeof last.content !== 'string') return;
    const c = last.content;
    if (!c.includes('撰写中') || c.includes('共完成') || c.includes('已写入，可输入')) return;
    const writtenCount = projectChapters.filter((ch) => ch.has_file).length;
    if (writtenCount < 1) return;
    const totalMatch = c.match(/正在连续撰写\s*(\d+)\s*章/);
    const total = totalMatch ? Math.min(100, Math.max(1, parseInt(totalMatch[1], 10))) : writtenCount + 1;
    const remaining = Math.max(0, total - writtenCount);
    const hint =
      remaining > 0
        ? `\n\n（第 ${writtenCount} 章已写入，可输入「写 ${remaining} 章」继续剩余章节）`
        : `\n\n（全部 ${writtenCount} 章已写入）`;
    hasAppendedResumeHintRef.current = true;
    setMessages((prev) =>
      prev.map((m, i) => (i === prev.length - 1 ? { ...m, content: m.content + hint } : m))
    );
  }, [messages, projectChapters]);

  useEffect(() => {
    const maxPage = Math.ceil(memoryEntities.length / MEMORY_LIST_PAGE_SIZE) || 1;
    setMemoryListPage((p) => Math.min(p, maxPage));
  }, [memoryEntities.length]);

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' });
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const runOrchestration = useCallback(async () => {
    const order: AgentKey[] = ['memory', 'planner', 'writer', 'editor', 'qa'];
    setOrchestration([]);
    for (const a of order) {
      setActiveAgent(a);
      setOrchestration((prev) => [...prev, a]);
      await new Promise((r) => setTimeout(r, 400));
    }
    setActiveAgent(null);
  }, []);

  const clearConversation = useCallback(() => {
    setMessages([]);
    setInput('');
    setOrchestration([]);
    setActiveAgent(null);
    hasAppendedResumeHintRef.current = false;
    try {
      localStorage.removeItem(CREATOR_STORAGE_KEYS.messages);
    } catch (_) {}
  }, []);

  const handleSend = async () => {
    const raw = input.trim();
    if (!raw || loading) return;

    if (raw === '清空历史' || raw === '清空') {
      clearConversation();
      return;
    }

    const userMsg: Message = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: raw,
      ts: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const aid = `a-${Date.now()}`;
    const useCreatorApi = mode === 'create' || mode === 'continue' || mode === 'polish';
    const messageAgent: AgentKey =
      mode === 'create' ? 'planner' : mode === 'continue' ? 'writer' : mode === 'polish' ? 'editor' : 'writer';
    const assistantMsg: Message = {
      id: aid,
      role: 'assistant',
      content: '',
      ts: new Date(),
      agent: messageAgent,
      streaming: !useCreatorApi,
    };
    setMessages((prev) => [...prev, assistantMsg]);
    // 创作 API：指挥中心与真实请求同步，不跑假动画
    if (useCreatorApi) {
      if (mode === 'create') {
        setOrchestration([]);
        setActiveAgent('planner');
      } else if (mode === 'continue') {
        setOrchestration(['planner', 'memory']);
        setActiveAgent('writer');
      } else {
        setOrchestration(['planner', 'memory', 'writer']);
        setActiveAgent('editor');
      }
    } else {
      runOrchestration();
    }

    try {
      if (useCreatorApi) {
        const batchMatch = mode === 'continue' ? raw.match(/(?:写|连续\s*写)?\s*(\d+)\s*章/) || raw.match(/^(\d+)\s*章$/) : null;
        const batchN = batchMatch ? Math.min(Math.max(1, parseInt(batchMatch[1], 10)), 100) : 1;

        if (mode === 'continue' && batchN > 1) {
          let progress = `正在连续撰写 ${batchN} 章…\n\n`;
          setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: progress + '第 1 章撰写中…' } : m)));
          scrollToBottom();
          let lastChapter = 0;
          let lastContent = '';
          let completedCount = 0;
          for (let i = 0; i < batchN; i++) {
            let res: Response;
            try {
              res = await fetchCreatorSubmit({ mode: 'continue', input: '', project_id: projectId });
            } catch (e) {
              const detail = e instanceof Error ? e.message : String(e);
              const msg =
                (e instanceof Error && e.name === 'AbortError')
                  ? '提交超时，请检查网络'
                  : `无法连接后端（${detail}）。请确认 creator_api 已启动且浏览器能访问 API_URL。`;
              progress += `\n第 ${i + 1} 章失败：${msg}`;
              setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: progress, streaming: false } : m)));
              break;
            }
            const { data: submitData, error } = await parseCreatorRunResponse(res);
            if (error) {
              progress += `\n第 ${i + 1} 章失败：${error}`;
              setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: progress, streaming: false } : m)));
              break;
            }
            const taskId = submitData.task_id as string | undefined;
            let data: { code?: number; message?: string; content?: string; chapter_number?: number };
            if (taskId) {
              const pollResult = await pollCreatorTask(taskId);
              if (pollResult.status === 'failed') {
                progress += `\n第 ${i + 1} 章失败：${pollResult.error || '任务失败'}`;
                setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: progress, streaming: false } : m)));
                break;
              }
              data = {
                code: pollResult.code,
                message: pollResult.message,
                content: pollResult.content,
                chapter_number: pollResult.chapter_number,
              };
            } else {
              data = submitData;
            }
            if (data.code !== 0) {
              progress += `\n第 ${i + 1} 章失败：${data.message || '请求失败'}`;
              setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: progress, streaming: false } : m)));
              break;
            }
            completedCount = i + 1;
            lastChapter = data.chapter_number ?? i + 1;
            lastContent = (data.content || '').slice(0, 300);
            progress += `第 ${i + 1}/${batchN} 章完成 ✓`;
            if (data.chapter_number) progress += `（已写入 chapter_${String(data.chapter_number).padStart(3, '0')}.txt）`;
            progress += '\n';
            if (i < batchN - 1) progress += `第 ${i + 2} 章撰写中…\n`;
            setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: progress, streaming: false } : m)));
            scrollToBottom();
          }
          progress += `\n---\n✅ 共完成 ${completedCount} 章。`;
          if (lastChapter) progress += ` 最后章节已写入 \`chapters/chapter_${String(lastChapter).padStart(3, '0')}.txt\`。`;
          if (lastContent) progress += `\n\n最后章节摘要：\n${lastContent}…`;
          streamEndRef.current.add(aid);
          setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: progress, streaming: false } : m)));
          try {
            if (completedCount > 0 && memoryOpen) await fetchMemory();
            if (completedCount > 0) await fetchProjectChapters();
          } catch (_) {
            // 刷新记忆/章节列表失败不覆盖已展示的成功内容
          }
          setOrchestration(['planner', 'memory', 'writer', 'editor', 'qa']);
          setActiveAgent(null);
        } else {
          // 单次 create/continue：走流式 API，用编排事件驱动指挥中心
          const streamBody = {
            mode,
            input: raw,
            ...(mode !== 'create' ? { project_id: projectId } : {}),
            ...(mode === 'create' && continueFromVolume && previousProjectId
              ? {
                  previous_project_id: previousProjectId,
                  start_chapter: volumeStartChapter,
                  target_chapters: volumeTargetChapters,
                  project_id: newVolumeProjectId.trim() || undefined,
                }
              : mode === 'create' ? { target_chapters: createTargetChapters } : {}),
            ...(mode === 'continue' ? { use_evermemos_context: useEvermemosContext } : {}),
          };
          let streamEnd: { code: number; message: string; content?: string; project_id?: string; chapter_number?: number };
          try {
            streamEnd = await fetchCreatorStream(streamBody, (ev) => {
              if (ev.type === 'step_start' && ev.step) {
                const agentKey = stepToAgentKey(ev.step);
                if (agentKey) setActiveAgent(agentKey);
              } else if (ev.type === 'step_done' && ev.step) {
                const agentKey = stepToAgentKey(ev.step);
                if (agentKey) {
                  setOrchestration((prev) => (prev.includes(agentKey) ? prev : [...prev, agentKey]));
                  setActiveAgent(null);
                }
              } else if (ev.type === 'step_error' && ev.data?.error) {
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === aid ? { ...m, content: `${m.content}\n\n⚠️ 步骤异常: ${ev.data!.error}` } : m
                  )
                );
                setActiveAgent(null);
              } else if (ev.type === 'stream_end') {
                const code = ev.code ?? 1;
                const msg = ev.message ?? '';
                const content = ev.content ?? '';
                let text = code === 0 ? content : msg;
                if (code === 0 && mode === 'create' && ev.project_id) {
                  setProjectId(ev.project_id);
                  setProjectList((prev) => (prev.includes(ev.project_id!) ? prev : [...prev, ev.project_id!].sort()));
                  text += '\n\n---\n💡 大纲已生成。请切换到「章节」并发送任意内容（如「写第一章」或「写10章」），将按大纲逐章生成正文。';
                }
                if (code === 0 && mode === 'continue' && ev.chapter_number != null) {
                  const ch = ev.chapter_number;
                  text += `\n\n---\n📄 第 ${ch} 章已写入项目目录 \`chapters/chapter_${String(ch).padStart(3, '0')}.txt\`。继续点击「章节」可写下一章。`;
                }
                setMessages((prev) => prev.map((m) => (m.id === aid ? { ...m, content: text, streaming: false } : m)));
                setOrchestration(['planner', 'memory', 'writer', 'editor', 'qa']);
                setActiveAgent(null);
                if (code === 0 && memoryOpen) fetchMemory().catch(() => {});
                if (code === 0 && mode === 'continue') fetchProjectChapters().catch(() => {});
              }
            });
          } catch (e) {
            const detail = e instanceof Error ? e.message : String(e);
            const msg =
              e instanceof Error && e.name === 'AbortError'
                ? '提交超时，请检查网络'
                : `无法连接后端（${detail}）。请确认 creator_api 已启动、API_URL 正确，且当前浏览器能访问该地址（若 API 在服务器端口映射，需从能访问该映射的终端打开前端）。`;
            streamEndRef.current.add(aid);
            setMessages((prev) =>
              prev.map((m) => (m.id === aid ? { ...m, content: msg, streaming: false } : m))
            );
            setOrchestration([]);
            setActiveAgent(null);
            setLoading(false);
            scrollToBottom();
            return;
          }
          // 若 SSE 未携带 stream_end 或需兜底展示，用返回值再更新一次
          if (streamEnd.code !== 0 && streamEnd.message) {
            setMessages((prev) =>
              prev.map((m) =>
                m.id === aid ? { ...m, content: m.content ? `${m.content}\n\n${streamEnd.message}` : streamEnd.message, streaming: false } : m
              )
            );
          }
          streamEndRef.current.add(aid);
          setOrchestration(['planner', 'memory', 'writer', 'editor', 'qa']);
          setActiveAgent(null);
        }
      } else {
        const res = await fetch(`${API_BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: [
              ...messages.map((m) => ({ role: m.role, content: m.content })),
              { role: 'user', content: raw },
            ],
            model: 'DeepSeek-v3-2',
            stream: true,
          }),
        });

        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const contentType = res.headers.get('content-type') || '';
        if (contentType.includes('application/json')) throw new Error('fallback');

        const reader = res.body?.getReader();
        if (!reader) throw new Error('no reader');

        const dec = new TextDecoder();
        let full = '';
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          full += dec.decode(value, { stream: true });
          setMessages((prev) =>
            prev.map((m) => (m.id === aid ? { ...m, content: full, streaming: true } : m))
          );
          scrollToBottom();
        }
        streamEndRef.current.add(aid);
        setMessages((prev) =>
          prev.map((m) => (m.id === aid ? { ...m, content: full, streaming: false } : m))
        );
      }
    } catch {
      streamEndRef.current.add(aid);
      const fallback = useCreatorApi
        ? '创作服务请求失败，请确认后端已启动且创作接口（/api/creator/run 或 /api/creator/stream）可用。'
        : '多智能体创作助手已就绪。当前为演示模式，正在模拟编排流程；实际创作需对接后端编排与记忆服务。';
      setMessages((prev) =>
        prev.map((m) => (m.id === aid ? { ...m, content: fallback, streaming: false } : m))
      );
      if (useCreatorApi) {
        setOrchestration([]);
        setActiveAgent(null);
      }
    } finally {
      setLoading(false);
      setActiveAgent(null);
      scrollToBottom();
    }
  };

  const getAgent = (k?: AgentKey) => AGENTS.find((a) => a.key === k);
  const modeLabels: Record<typeof mode, string> = {
    create: '大纲',
    continue: '章节',
    polish: '润色',
    chat: '对话',
  };

  return (
    <div
      className="creator-root"
      style={{
        flex: 1,
        minHeight: 0,
        display: 'flex',
        flexDirection: 'column',
        background: T.bgPage,
        fontFamily: T.fontFamily,
        color: T.text,
      }}
    >
      {/* 顶栏 — 玻璃拟态 */}
      <header
        className="creator-header"
        style={{
          minHeight: 64,
          borderBottom: `1px solid ${T.borderHeader}`,
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
          flexShrink: 0,
          background: T.bgHeader,
          backdropFilter: T.headerBlur,
          WebkitBackdropFilter: T.headerBlur,
        }}
      >
        {/* 左侧：Logo + 标题 */}
        <div style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
          <Space size="middle">
            <Avatar
              icon={<RobotOutlined />}
              style={{
                background: T.avatarBot,
                width: 36,
                height: 36,
                fontSize: 16,
              }}
            />
            <div>
              <div
                style={{
                  color: T.textBright,
                  fontSize: 17,
                  fontWeight: T.fontWeightSemibold,
                  letterSpacing: '-0.02em',
                  lineHeight: 1.3,
                }}
              >
                创作助手
              </div>
              <div style={{ fontSize: 12, color: T.textMuted, marginTop: 2 }}>
                多智能体动态编排 · 记忆系统
              </div>
            </div>
          </Space>
        </div>
        {/* 中部：模式 + 接续设置（居中） */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: 8,
            padding: '8px 16px',
            minWidth: 0,
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap', justifyContent: 'center' }}>
            <Segmented
              className="creator-segmented-mode"
              value={mode}
              onChange={(v) => setMode(v as typeof mode)}
              options={[
                { value: 'create', label: '大纲' },
                { value: 'continue', label: '章节' },
                { value: 'polish', label: '润色' },
                { value: 'chat', label: '对话' },
              ]}
              style={{ background: T.segBg }}
            />
            {mode === 'create' && (
              <Checkbox
                checked={continueFromVolume}
                onChange={(e) => {
                  setContinueFromVolume(e.target.checked);
                  if (e.target.checked && !newVolumeProjectId && previousProjectId) {
                    setNewVolumeProjectId(previousProjectId.replace(/_第一卷$/, '_第二卷') || previousProjectId + '_第二卷');
                  }
                }}
                style={{ color: T.textMuted, fontSize: HEADER_CONTROL_FONT_SIZE }}
              >
                接续前卷
              </Checkbox>
            )}
            {mode === 'create' && !continueFromVolume && (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: HEADER_CONTROL_FONT_SIZE, color: T.textMuted }}>目标章数</span>
                <InputNumber
                  min={1}
                  max={500}
                  value={createTargetChapters}
                  onChange={(v) => setCreateTargetChapters(typeof v === 'number' ? v : 100)}
                  style={{ width: 72, fontSize: HEADER_CONTROL_FONT_SIZE }}
                />
              </div>
            )}
          </div>
          {mode === 'create' && continueFromVolume && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: 16,
                justifyContent: 'center',
                padding: '10px 20px',
                borderRadius: 10,
                background: 'rgba(255,255,255,0.06)',
                border: `1px solid ${T.border}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: HEADER_CONTROL_FONT_SIZE, color: T.textMuted, width: 56, textAlign: 'right' }}>前卷</span>
                <Select
                  placeholder="选择前卷作品"
                  value={previousProjectId || undefined}
                  onChange={(v) => {
                    setPreviousProjectId(v || '');
                    if (!newVolumeProjectId && v) setNewVolumeProjectId((v as string).replace(/_第一卷$/, '_第二卷') || (v as string) + '_第二卷');
                  }}
                  options={projectList.map((id) => ({ value: id, label: id }))}
                  style={{ width: 160, fontSize: HEADER_CONTROL_FONT_SIZE }}
                  styles={{ selector: { fontSize: HEADER_CONTROL_FONT_SIZE } as React.CSSProperties }}
                  allowClear
                  showSearch
                  optionFilterProp="label"
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: HEADER_CONTROL_FONT_SIZE, color: T.textMuted, width: 56, textAlign: 'right' }}>起始章</span>
                <InputNumber
                  min={2}
                  max={9999}
                  value={volumeStartChapter}
                  onChange={(v) => setVolumeStartChapter(typeof v === 'number' ? v : 101)}
                  style={{ width: 72, fontSize: HEADER_CONTROL_FONT_SIZE }}
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: HEADER_CONTROL_FONT_SIZE, color: T.textMuted, width: 56, textAlign: 'right' }}>本卷章数</span>
                <InputNumber
                  min={1}
                  max={500}
                  value={volumeTargetChapters}
                  onChange={(v) => setVolumeTargetChapters(typeof v === 'number' ? v : 100)}
                  style={{ width: 72, fontSize: HEADER_CONTROL_FONT_SIZE }}
                />
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <span style={{ fontSize: HEADER_CONTROL_FONT_SIZE, color: T.textMuted, width: 56, textAlign: 'right' }}>本卷名</span>
                <Input
                  placeholder="如：完美之墙_第二卷"
                  value={newVolumeProjectId}
                  onChange={(e) => setNewVolumeProjectId(e.target.value)}
                  style={{ width: 168, fontSize: HEADER_CONTROL_FONT_SIZE }}
                />
              </div>
            </div>
          )}
        </div>
        {/* 右侧：当前作品 + 刷新 + 章节数 */}
        <div style={{ display: 'flex', alignItems: 'center', flexShrink: 0 }}>
          <Space size="middle">
            <span style={{ fontSize: HEADER_CONTROL_FONT_SIZE, color: T.textMuted }}>当前作品</span>
            <Select
              value={projectId}
              onChange={(v) => setProjectId(v || '完美之墙')}
              onDropdownVisibleChange={(open) => { if (open) fetchProjectList(); }}
              options={[
                ...(projectId && !projectList.includes(projectId)
                  ? [{ value: projectId, label: `${projectId}（当前）` }]
                  : []),
                ...projectList.map((id) => ({ value: id, label: id })),
              ]}
              placeholder="选择作品"
              style={{ width: 180, background: T.segBg, fontSize: HEADER_CONTROL_FONT_SIZE }}
              styles={{ selector: { fontSize: HEADER_CONTROL_FONT_SIZE } as React.CSSProperties }}
              allowClear
              showSearch
              optionFilterProp="label"
              filterOption={(input, opt) => (opt?.label ?? '').toString().toLowerCase().includes(input.toLowerCase())}
            />
            <Tooltip title="刷新作品列表">
              <Button
                type="text"
                size="small"
                icon={<ReloadOutlined />}
                onClick={fetchProjectList}
                style={{ color: T.textMuted }}
                className="creator-icon-btn"
              />
            </Tooltip>
            <Tooltip title="点击查看完整章节列表">
              <span
                role="button"
                tabIndex={0}
                onClick={() => setChapterListOpen(true)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setChapterListOpen(true); } }}
                style={{
                  fontSize: HEADER_CONTROL_FONT_SIZE,
                  color: projectChapters.length > 0 ? T.accent : T.textMuted,
                  cursor: 'pointer',
                  textDecoration: 'underline',
                  userSelect: 'none',
                }}
              >
                共 {projectChapters.length} 章，已写 {projectChapters.filter((c) => c.has_file).length} 章
              </span>
            </Tooltip>
          </Space>
        </div>
        <Modal
          title={`章节列表 · ${projectId}`}
          open={chapterListOpen}
          onCancel={() => setChapterListOpen(false)}
          footer={null}
          width={520}
          styles={{ body: { maxHeight: '70vh', overflowY: 'auto' } }}
        >
          <List
            dataSource={projectChapters}
            renderItem={(ch) => (
              <List.Item style={{ alignItems: 'flex-start' }}>
                <div style={{ width: '100%' }}>
                  <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
                    <span style={{ color: 'rgba(0,0,0,0.45)', fontVariantNumeric: 'tabular-nums', flexShrink: 0 }}>
                      第 {ch.number} 章
                    </span>
                    <span style={{ fontWeight: 600, color: 'rgba(0,0,0,0.88)', flex: 1, minWidth: 0 }}>
                      {ch.title}
                    </span>
                    {ch.has_file && (
                      <Tag color="green" style={{ margin: 0, flexShrink: 0 }}>已写</Tag>
                    )}
                  </div>
                  {ch.summary && (
                    <div style={{ fontSize: 12, color: 'rgba(0,0,0,0.45)', marginTop: 4, lineHeight: 1.5 }}>
                      {ch.summary}
                    </div>
                  )}
                </div>
              </List.Item>
            )}
          />
        </Modal>
      </header>

      <div style={{ flex: 1, minHeight: 0, display: 'flex', overflow: 'hidden' }}>
        {/* 左侧：游戏化编排流水线 */}
        <motion.aside
          initial={false}
          animate={{ width: orchestrationOpen ? 272 : 56 }}
          className="creator-sidebar"
          style={{
            borderRight: `1px solid ${T.border}`,
            background: T.bgSidebar,
            backdropFilter: T.sidebarBlur,
            WebkitBackdropFilter: T.sidebarBlur,
            boxShadow: T.shadowPanel,
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              padding: '18px 20px 14px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderBottom: orchestrationOpen ? `1px solid ${T.border}` : 'none',
              background: 'rgba(255,255,255,0.02)',
            }}
          >
            {orchestrationOpen ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 10px',
                    borderRadius: 8,
                    background: 'rgba(255,75,47,0.1)',
                    border: '1px solid rgba(255,75,47,0.2)',
                  }}
                >
                  <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#22c55e' }} />
                  <span style={{ fontSize: 10, fontWeight: T.fontWeightSemibold, color: T.accent, letterSpacing: '0.04em' }}>实时编排</span>
                </div>
                <span style={{ fontSize: 11, color: T.textMuted, letterSpacing: '0.04em' }}>工作流</span>
              </div>
            ) : null}
            <Button
              type="text"
              size="small"
              icon={orchestrationOpen ? <MenuFoldOutlined /> : <MenuUnfoldOutlined />}
              onClick={() => setOrchestrationOpen(!orchestrationOpen)}
              style={{ color: T.textMuted }}
              className="creator-icon-btn"
            />
          </div>
          {orchestrationOpen && (
            <div style={{ padding: '0 16px 24px', overflowY: 'auto', flex: 1 }}>
              <OrchestrationFlow
                agents={AGENTS.map((a) => ({ key: a.key, name: a.name, icon: a.icon, color: a.color }))}
                completed={orchestration}
                active={activeAgent}
                flow
              />
            </div>
          )}
        </motion.aside>

        {/* 中间：创作画布（minHeight:0 保证在 flex 中可收缩，消息区单独滚动、输入框始终贴底） */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
            minHeight: 0,
            position: 'relative',
            background: T.bgCanvas,
            overflow: 'hidden',
          }}
        >
          {/* 网格背景 */}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              opacity: 0.12,
              pointerEvents: 'none',
              backgroundImage: `
                linear-gradient(to right, rgba(255,75,47,0.15) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255,75,47,0.15) 1px, transparent 1px)
              `,
              backgroundSize: '32px 32px',
            }}
          />
          {/* 装饰光晕 */}
          <div
            style={{
              position: 'absolute',
              top: '15%',
              left: '10%',
              width: 280,
              height: 280,
              borderRadius: '50%',
              background: 'rgba(255,75,47,0.06)',
              filter: 'blur(48px)',
              pointerEvents: 'none',
            }}
          />
          <div
            style={{
              position: 'absolute',
              bottom: '20%',
              right: '8%',
              width: 240,
              height: 240,
              borderRadius: '50%',
              background: 'rgba(59,130,246,0.05)',
              filter: 'blur(40px)',
              pointerEvents: 'none',
            }}
          />
          <div
            ref={containerRef}
            style={{
              flex: 1,
              minHeight: 0,
              overflowY: 'auto',
              overflowX: 'hidden',
              padding: 40,
              paddingBottom: 120,
              position: 'relative',
              zIndex: 1,
            }}
          >
            {messages.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: [0.25, 0.46, 0.45, 0.94] }}
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  minHeight: 440,
                  gap: 40,
                }}
              >
                <motion.div
                  animate={{
                    scale: [1, 1.04, 1],
                  }}
                  transition={{ repeat: Infinity, duration: 2.8, ease: 'easeInOut' }}
                  style={{
                    width: 96,
                    height: 96,
                    borderRadius: T.radiusXl,
                    background: T.emptyIconBg,
                    boxShadow: `0 0 32px 4px ${T.emptyIconGlow}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: 36,
                    color: '#fff',
                  }}
                >
                  <ThunderboltOutlined />
                </motion.div>
                <div style={{ textAlign: 'center', maxWidth: 520 }}>
                  <div
                    style={{
                      fontSize: 22,
                      fontWeight: T.fontWeightSemibold,
                      color: T.textBright,
                      letterSpacing: '-0.02em',
                      lineHeight: 1.35,
                      marginBottom: 12,
                    }}
                  >
                    多智能体创作助手
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      color: T.textMuted,
                      lineHeight: 1.65,
                    }}
                  >
                    大纲、写手、记忆、润色、质检等智能体按任务动态编排，结合记忆系统保持设定与风格一致。
                    <br />
                    选择模式：大纲 → 章节 → 润色/对话。
                  </div>
                </div>
                <Space size="middle" wrap style={{ justifyContent: 'center' }}>
                  {(['create', 'continue', 'polish'] as const).map((m, i) => (
                    <motion.div
                      key={m}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.1 + i * 0.05, duration: 0.35 }}
                    >
                      <Button
                        type="primary"
                        ghost
                        size="large"
                        className="creator-ghost-btn"
                        onClick={() => {
                          setMode(m);
                          setInput(m === 'create' ? '输入主题，例如：穿越到玄灵大陆的科学家' : m === 'continue' ? '写下一章，或输入「写10章」连续写多章' : '润色这段文字');
                        }}
                        style={{
                          borderColor: T.ghostBorder,
                          color: T.ghostText,
                          borderRadius: T.radiusMd,
                          height: 44,
                          paddingLeft: 20,
                          paddingRight: 20,
                        }}
                      >
                        {modeLabels[m]}
                      </Button>
                    </motion.div>
                  ))}
                </Space>
              </motion.div>
            ) : (
              <div style={{ maxWidth: 680, margin: '0 auto' }}>
                <AnimatePresence>
                  {messages.map((msg, i) => (
                    <motion.div
                      key={msg.id}
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
                      style={{ marginBottom: 28 }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          gap: 14,
                          alignItems: 'flex-start',
                          flexDirection: msg.role === 'user' ? 'row-reverse' : 'row',
                        }}
                      >
                        <Avatar
                          icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                          style={{
                            background: msg.role === 'user' ? T.avatarUser : T.avatarBot,
                            flexShrink: 0,
                            width: 40,
                            height: 40,
                          }}
                        />
                        <div
                          style={{
                            maxWidth: msg.role === 'user' ? '75%' : '100%',
                            padding: '16px 20px',
                            borderRadius: T.radiusLg,
                            background: msg.role === 'user' ? T.bgMsgUser : T.bgMsgBot,
                            border: `1px solid ${msg.role === 'user' ? T.borderMsgUser : T.borderMsgBot}`,
                            boxShadow: T.shadowCard,
                          }}
                        >
                          {msg.role === 'assistant' && msg.agent && (
                            <Tag
                              color={getAgent(msg.agent)?.color}
                              style={{
                                marginBottom: 10,
                                fontSize: 11,
                                fontWeight: T.fontWeightMedium,
                                borderRadius: 6,
                              }}
                              icon={getAgent(msg.agent)?.icon}
                            >
                              {getAgent(msg.agent)?.name} Agent
                            </Tag>
                          )}
                          {msg.role === 'user' ? (
                            <Text style={{ color: T.textMsgUser, whiteSpace: 'pre-wrap' }}>{msg.content}</Text>
                          ) : (
                            <>
                              <div
                                className="creator-markdown"
                                dangerouslySetInnerHTML={{ __html: md.render(msg.content || '') }}
                                style={{ lineHeight: 1.8, wordBreak: 'break-word' }}
                              />
                              {msg.streaming && <Spin size="small" style={{ marginLeft: 8 }} />}
                            </>
                          )}
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </AnimatePresence>
                <div ref={endRef} />
              </div>
            )}
          </div>

          {/* 输入区：固定视窗底部，仅占中间内容区（左右侧栏之间），内容居中不偏左 */}
          <div
            style={{
              position: 'fixed',
              bottom: 0,
              left: orchestrationOpen ? 272 : 56,
              right: memoryOpen ? (memoryView === 'graph' ? 520 : 320) : 56,
              zIndex: 100,
              borderTop: `1px solid ${T.border}`,
              padding: '24px 40px 28px',
              background: T.bgInput,
              boxShadow: '0 -4px 24px rgba(0,0,0,0.15)',
            }}
          >
            <div style={{ maxWidth: 760, margin: '0 auto', display: 'flex', gap: 12, alignItems: 'flex-end' }}>
              <TextArea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSend();
                  }
                }}
                placeholder={`${modeLabels[mode]}模式 · 输入意图或内容…`}
                autoSize={{ minRows: 1, maxRows: 5 }}
                disabled={loading}
                style={{
                  flex: 1,
                  background: 'rgba(24, 24, 32, 0.8)',
                  border: `1px solid ${T.borderStrong}`,
                  borderRadius: T.radiusMd,
                  color: T.text,
                  resize: 'none',
                  fontSize: 14,
                }}
              />
              <Tooltip title="发送">
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSend}
                  loading={loading}
                  disabled={!input.trim()}
                  className="creator-send-btn"
                  style={{
                    height: 36,
                    minWidth: 36,
                    background: T.primaryBg,
                    border: 'none',
                    borderRadius: T.radiusMd,
                  }}
                />
              </Tooltip>
              <Tooltip title="清空对话历史">
                <Button
                  type="text"
                  size="small"
                  onClick={clearConversation}
                  disabled={loading}
                  style={{ color: T.textMuted, height: 36, minWidth: 36, padding: '0 8px' }}
                >
                  清空
                </Button>
              </Tooltip>
            </div>
            <div
              style={{
                maxWidth: 760,
                margin: '10px auto 0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: 8,
                fontSize: 12,
                color: T.textDim,
              }}
            >
              {mode === 'continue' && (
                <Checkbox
                  checked={useEvermemosContext}
                  onChange={(e) => setUseEvermemosContext(e.target.checked)}
                  style={{ color: T.textMuted, fontSize: 12 }}
                >
                  续写时注入云端记忆（EverMemOS）
                </Checkbox>
              )}
              <span style={{ marginLeft: 'auto' }}>{loading ? '智能体编排中…' : 'Enter 发送 · Shift+Enter 换行'}</span>
            </div>
          </div>
        </div>

        {/* 右侧：记忆面板（列表 / 图谱） */}
        <motion.aside
          initial={false}
          animate={{ width: memoryOpen ? (memoryView === 'graph' ? 520 : 320) : 56 }}
          className="creator-sidebar"
          style={{
            overflow: 'hidden',
            borderLeft: `1px solid ${T.border}`,
            background: T.bgSidebar,
            backdropFilter: T.sidebarBlur,
            WebkitBackdropFilter: T.sidebarBlur,
            boxShadow: T.shadowPanel,
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
          }}
        >
          {memoryOpen ? (
            <>
              <div
                style={{
                  padding: '18px 20px 14px',
                  borderBottom: `1px solid ${T.border}`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: 8,
                  flexShrink: 0,
                  background: 'rgba(255,255,255,0.02)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: 6,
                      padding: '4px 10px',
                      borderRadius: 10,
                      background: 'rgba(255,75,47,0.12)',
                      border: '1px solid rgba(255,75,47,0.25)',
                    }}
                  >
                    <DatabaseOutlined style={{ color: T.accent, fontSize: 12 }} />
                    <span style={{ fontSize: 11, fontWeight: T.fontWeightSemibold, color: T.accent, letterSpacing: '0.04em' }}>
                      {memoryView === 'graph' ? '记忆网络在线' : 'AI 记忆系统'}
                    </span>
                    {memoryView === 'graph' && memoryGraph.nodes.length > 0 && (
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e' }} />
                    )}
                  </div>
                  <Segmented
                    className="creator-segmented-memory"
                    size="small"
                    value={memoryView}
                    onChange={(v) => setMemoryView(v as 'list' | 'graph')}
                    options={[
                      { value: 'list', label: '列表' },
                      { value: 'graph', label: '图谱' },
                    ]}
                    style={{ background: T.segBg }}
                  />
                </div>
                <Button
                  type="text"
                  size="small"
                  icon={<MenuFoldOutlined style={{ transform: 'rotate(180deg)' }} />}
                  onClick={() => setMemoryOpen(false)}
                  style={{ color: T.textMuted }}
                  className="creator-icon-btn"
                />
              </div>
              <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column', minHeight: 0 }}>
                {memoryView === 'list' ? (
                  <div
                    style={{
                      flex: 1,
                      minHeight: 0,
                      overflowY: 'auto',
                      display: 'flex',
                      flexDirection: 'column',
                      background: 'linear-gradient(180deg, rgba(10,10,16,0.6) 0%, rgba(26,26,46,0.5) 100%)',
                    }}
                  >
                    {memoryLoading ? (
                      <div style={{ padding: 24, textAlign: 'center', color: T.textDim }}>加载中…</div>
                    ) : (
                      <>
                        <div style={{ padding: 12, borderBottom: `1px solid ${T.border}`, flexShrink: 0 }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8, flexWrap: 'wrap', gap: 6 }}>
                            <span style={{ fontSize: 11, fontWeight: T.fontWeightSemibold, color: T.textMuted, letterSpacing: '0.04em' }}>云端记忆（EverMemOS）</span>
                            <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                              {memoryCloud.length > 0 && (
                                <span style={{ fontSize: 11, color: T.textMuted }}>共 {memoryCloud.length} 条</span>
                              )}
                              {evermemosAvailable && (
                                <Button
                                  type="link"
                                  size="small"
                                  loading={retrievalDemoLoading}
                                  onClick={async () => {
                                    setRetrievalDemoLoading(true);
                                    setRetrievalDemoResult(null);
                                    try {
                                      const r = await fetch(
                                        `${API_BASE}/api/memory/evermemos/retrieval-demo`,
                                        {
                                          method: 'POST',
                                          headers: { 'Content-Type': 'application/json' },
                                          body: JSON.stringify({ project_id: projectId, top_k: 8 }),
                                        }
                                      );
                                      const data = r.ok ? await r.json() : {};
                                      if (data.ok && Array.isArray(data.entries)) {
                                        setRetrievalDemoResult(data.entries);
                                        const summary = data.entries
                                          .map((e: { query_type: string; result_count: number }) => `${e.query_type} ${e.result_count} 条`)
                                          .join('，');
                                        message.success(`已记录检索测试：${summary}`);
                                        fetchMemory();
                                      } else {
                                        message.warning(data.message || '检索测试失败');
                                      }
                                    } catch {
                                      message.error('请求失败');
                                    } finally {
                                      setRetrievalDemoLoading(false);
                                    }
                                  }}
                                  style={{ fontSize: 11, padding: 0 }}
                                >
                                  跑检索测试
                                </Button>
                              )}
                            </span>
                          </div>
                          {retrievalDemoResult && retrievalDemoResult.length > 0 && (
                            <div style={{ marginBottom: 8, padding: 8, background: 'rgba(6,182,212,0.06)', borderRadius: T.radiusSm, fontSize: 11 }}>
                              {retrievalDemoResult.map((e, i) => (
                                <div key={i} style={{ marginBottom: i < retrievalDemoResult!.length - 1 ? 6 : 0 }}>
                                  <span style={{ color: T.textMuted }}>{e.query_type}</span>
                                  <span style={{ color: T.textDim, marginLeft: 6 }}>{e.result_count} 条</span>
                                  {e.excerpts.slice(0, 2).map((ex, j) => (
                                    <div key={j} style={{ color: T.textMuted, marginTop: 2, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={ex}>
                                      {ex}
                                    </div>
                                  ))}
                                </div>
                              ))}
                            </div>
                          )}
                          {memoryCloud.length > 0 ? (
                            <>
                              <div
                                style={{
                                  maxHeight: 320,
                                  overflowY: 'auto',
                                  display: 'flex',
                                  flexDirection: 'column',
                                  gap: 6,
                                  paddingRight: 4,
                                }}
                              >
                                {memoryCloud
                                  .slice((cloudPage - 1) * CLOUD_PAGE_SIZE, cloudPage * CLOUD_PAGE_SIZE)
                                  .map((item, i) => {
                                    const key = item.id ?? `cloud_${(cloudPage - 1) * CLOUD_PAGE_SIZE + i}`;
                                    const isExpanded = expandedCloudKey === key;
                                    const text = (item.content || '').trim() || '—';
                                    const canDelete = Boolean(item.id);
                                    return (
                                      <div
                                        key={key}
                                        role="button"
                                        tabIndex={0}
                                        onClick={() => setExpandedCloudKey((k) => (k === key ? null : key))}
                                        onKeyDown={(ev) => {
                                          if (ev.key === 'Enter' || ev.key === ' ') {
                                            ev.preventDefault();
                                            setExpandedCloudKey((k) => (k === key ? null : key));
                                          }
                                        }}
                                        style={{
                                          fontSize: 11,
                                          color: T.textMuted,
                                          padding: '8px 12px',
                                          background: 'rgba(6,182,212,0.08)',
                                          borderRadius: T.radiusSm,
                                          border: `1px solid rgba(6,182,212,0.2)`,
                                          lineHeight: 1.45,
                                          overflow: 'hidden',
                                          textOverflow: isExpanded ? undefined : 'ellipsis',
                                          display: isExpanded ? 'block' : '-webkit-box',
                                          WebkitLineClamp: isExpanded ? undefined : 3,
                                          WebkitBoxOrient: 'vertical' as const,
                                          cursor: 'pointer',
                                        }}
                                      >
                                        {text}
                                        {isExpanded && canDelete && (
                                          <div
                                            style={{ marginTop: 8 }}
                                            onClick={(e) => e.stopPropagation()}
                                          >
                                            <Popconfirm
                                              title="确定删除这条云端记忆？"
                                              onConfirm={async (e) => {
                                                e?.stopPropagation();
                                                try {
                                                  const r = await fetch(
                                                    `${API_BASE}/api/memory/evermemos`,
                                                    {
                                                      method: 'DELETE',
                                                      headers: { 'Content-Type': 'application/json' },
                                                      body: JSON.stringify({ memory_id: item.id }),
                                                    }
                                                  );
                                                  const data = r.ok ? await r.json() : {};
                                                  if (data.ok) {
                                                    setMemoryCloud((prev) => prev.filter((x) => x.id !== item.id));
                                                    setExpandedCloudKey(null);
                                                  }
                                                } catch (_) {}
                                              }}
                                            >
                                              <Button
                                                type="text"
                                                size="small"
                                                danger
                                                icon={<DeleteOutlined />}
                                                style={{ fontSize: 11, padding: '0 6px' }}
                                              >
                                                删除
                                              </Button>
                                            </Popconfirm>
                                          </div>
                                        )}
                                      </div>
                                    );
                                  })}
                              </div>
                              {memoryCloud.length > CLOUD_PAGE_SIZE && (
                                <div
                                  style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: 8,
                                    marginTop: 8,
                                  }}
                                >
                                  <Button
                                    type="text"
                                    size="small"
                                    disabled={cloudPage <= 1}
                                    onClick={() => setCloudPage((p) => Math.max(1, p - 1))}
                                    style={{ color: T.textMuted, fontSize: 11 }}
                                  >
                                    上一页
                                  </Button>
                                  <span style={{ fontSize: 11, color: T.textMuted }}>
                                    {cloudPage} / {Math.ceil(memoryCloud.length / CLOUD_PAGE_SIZE)}
                                  </span>
                                  <Button
                                    type="text"
                                    size="small"
                                    disabled={cloudPage >= Math.ceil(memoryCloud.length / CLOUD_PAGE_SIZE)}
                                    onClick={() =>
                                      setCloudPage((p) =>
                                        Math.min(Math.ceil(memoryCloud.length / CLOUD_PAGE_SIZE), p + 1)
                                      )
                                    }
                                    style={{ color: T.textMuted, fontSize: 11 }}
                                  >
                                    下一页
                                  </Button>
                                </div>
                              )}
                            </>
                          ) : (
                            <div style={{ fontSize: 11, color: T.textDim, lineHeight: 1.5 }}>
                              {evermemosAvailable
                                ? '暂无云端记忆。创作或续写后将自动写入并在此展示。'
                                : <>申请并配置 <code style={{ fontSize: 10, background: 'rgba(255,255,255,0.06)', padding: '2px 6px', borderRadius: 4 }}>EVERMEMOS_API_KEY</code> 后，创作与续写将自动写入并在此展示。</>}
                            </div>
                          )}
                        </div>
                        <div
                          style={{
                            flex: 1,
                            minHeight: 0,
                            display: 'flex',
                            flexDirection: 'column',
                            borderBottom: memoryRecents.length > 0 ? `1px solid ${T.border}` : undefined,
                          }}
                        >
                          <div style={{ padding: '16px 20px 8px', borderBottom: `1px solid ${T.border}`, flexShrink: 0 }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                              <span style={{ fontSize: 14, fontWeight: T.fontWeightSemibold, color: T.textBright }}>记忆列表</span>
                              <span style={{ fontSize: 11, color: T.textMuted }}>{memoryEntities.length} 条</span>
                            </div>
                          </div>
                          <div
                            style={{
                              padding: 16,
                              maxHeight: 380,
                              overflowY: 'auto',
                            }}
                            title="每页 10 条，可在此区域滚动查看；下方有翻页"
                          >
                            {memoryEntities
                            .slice((memoryListPage - 1) * MEMORY_LIST_PAGE_SIZE, memoryListPage * MEMORY_LIST_PAGE_SIZE)
                            .map((e, idx) => (
                            <div
                              key={e.id}
                              role="button"
                              tabIndex={0}
                              onClick={async () => {
                                try {
                                  const r = await fetch(`${API_BASE}/api/memory/note/${encodeURIComponent(e.id)}?project_id=${encodeURIComponent(projectId)}`);
                                  if (r.ok) {
                                    const note = await r.json();
                                    setSelectedNode({ ...note, related: note.related } as GraphNode);
                                  } else {
                                    setSelectedNode({ id: e.id, label: e.name, type: (e.type as 'entity' | 'fact' | 'atom') || 'entity', brief: e.brief } as GraphNode);
                                  }
                                } catch {
                                  setSelectedNode({ id: e.id, label: e.name, type: (e.type as 'entity' | 'fact' | 'atom') || 'entity', brief: e.brief } as GraphNode);
                                }
                              }}
                              onKeyDown={(ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); (ev.currentTarget as HTMLDivElement).click(); } }}
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 12,
                                padding: '14px 16px',
                                marginBottom: 8,
                                background: 'rgba(255,255,255,0.03)',
                                borderRadius: 12,
                                border: '1px solid transparent',
                                cursor: 'pointer',
                              }}
                              className="creator-memory-list-item"
                            >
                              <div
                                style={{
                                  width: 28,
                                  height: 28,
                                  borderRadius: 8,
                                  background: 'rgba(255,255,255,0.06)',
                                  color: T.textMuted,
                                  fontSize: 11,
                                  fontFamily: 'monospace',
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  flexShrink: 0,
                                }}
                              >
                                {String((memoryListPage - 1) * MEMORY_LIST_PAGE_SIZE + idx + 1).padStart(2, '0')}
                              </div>
                              <div
                                style={{
                                  width: 36,
                                  height: 36,
                                  borderRadius: 10,
                                  background: 'rgba(255,75,47,0.15)',
                                  color: T.accent,
                                  fontSize: 14,
                                  display: 'flex',
                                  alignItems: 'center',
                                  justifyContent: 'center',
                                  flexShrink: 0,
                                }}
                              >
                                ◆
                              </div>
                              <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2, flexWrap: 'wrap' }}>
                                  <span style={{ fontSize: 13, fontWeight: T.fontWeightMedium, color: T.textBright, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    {e.name}
                                  </span>
                                  <span
                                    style={{
                                      fontSize: 10,
                                      padding: '2px 6px',
                                      borderRadius: 6,
                                      background: 'rgba(255,75,47,0.2)',
                                      color: T.accent,
                                      flexShrink: 0,
                                    }}
                                  >
                                    {e.type || '实体'}
                                  </span>
                                </div>
                                {e.brief && (
                                  <div style={{ fontSize: 11, color: T.textMuted, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                    {e.brief}
                                  </div>
                                )}
                              </div>
                              <span style={{ color: 'rgba(255,255,255,0.2)', fontSize: 12 }}>→</span>
                            </div>
                          ))}
                        </div>
                        </div>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: 12,
                            padding: '12px 16px',
                            borderTop: `1px solid ${T.border}`,
                            flexShrink: 0,
                            background: T.bgSidebar ?? 'rgba(12,12,18,0.98)',
                            minHeight: 44,
                          }}
                          aria-label="记忆列表翻页"
                        >
                          <Button
                            type="text"
                            size="small"
                            disabled={memoryEntities.length === 0 || memoryListPage <= 1}
                            onClick={() => setMemoryListPage((p) => Math.max(1, p - 1))}
                            style={{ color: T.textMuted, fontSize: 12 }}
                          >
                            上一页
                          </Button>
                          <span style={{ fontSize: 12, color: T.textMuted }}>
                            {memoryListPage} / {Math.max(1, Math.ceil(memoryEntities.length / MEMORY_LIST_PAGE_SIZE))}
                          </span>
                          <Button
                            type="text"
                            size="small"
                            disabled={memoryEntities.length === 0 || memoryListPage >= Math.ceil(memoryEntities.length / MEMORY_LIST_PAGE_SIZE)}
                            onClick={() =>
                              setMemoryListPage((p) =>
                                Math.min(Math.ceil(memoryEntities.length / MEMORY_LIST_PAGE_SIZE), p + 1)
                              )
                            }
                            style={{ color: T.textMuted, fontSize: 12 }}
                          >
                            下一页
                          </Button>
                        </div>
                        {memoryRecents.length > 0 && (
                          <div style={{ padding: 12, borderTop: `1px solid ${T.border}`, flexShrink: 0 }}>
                            <div style={{ fontSize: 11, fontWeight: T.fontWeightSemibold, color: T.textMuted, marginBottom: 8, letterSpacing: '0.04em' }}>最近检索</div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 6, maxHeight: 160, overflowY: 'auto' }}>
                              {memoryRecents.slice(0, 10).map((r, i) => {
                                const looksLikeNoteId = /^voted_\d+_\d+$|^chapter_\d{3}$|^unimem_[\w-]+$/i.test((r || '').trim());
                                return (
                                <div
                                  key={i}
                                  role="button"
                                  tabIndex={0}
                                  onClick={async () => {
                                    if (looksLikeNoteId) {
                                      try {
                                        const res = await fetch(`${API_BASE}/api/memory/note/${encodeURIComponent(r)}?project_id=${encodeURIComponent(projectId)}`);
                                        if (res.ok) {
                                          const note = await res.json();
                                          setSelectedNode({ ...note, related: note.related } as GraphNode);
                                          return;
                                        }
                                      } catch (_) {}
                                    }
                                    setSelectedNode({ id: r, label: r, type: 'entity' as const, brief: '' } as GraphNode);
                                  }}
                                  onKeyDown={(ev) => { if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); (ev.currentTarget as HTMLDivElement).click(); } }}
                                  style={{
                                    fontSize: 11,
                                    color: T.textMuted,
                                    padding: '8px 12px',
                                    background: T.bgRecall,
                                    borderRadius: T.radiusSm,
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 8,
                                    cursor: 'pointer',
                                  }}
                                >
                                  <LinkOutlined style={{ color: T.accent, fontSize: 12 }} /> <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{r}</span>
                                </div>
                              ); })}
                            </div>
                          </div>
                        )}
                      </>
                    )}
                  </div>
                ) : (
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, padding: 20 }}>
                    {/* 参考 MemoryGraphSection：统计条 + 2D/3D 切换 */}
                    <div
                      style={{
                        display: 'flex',
                        flexWrap: 'wrap',
                        gap: 8,
                        marginBottom: 12,
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            padding: '6px 10px',
                            borderRadius: 10,
                            background: 'rgba(255,255,255,0.05)',
                            border: `1px solid ${T.border}`,
                          }}
                        >
                          <span style={{ fontSize: 12, fontWeight: T.fontWeightBold, color: T.accent }}>
                            {memoryGraph.nodes.length}
                          </span>
                          <span style={{ fontSize: 10, color: T.textMuted }}>节点</span>
                        </div>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: 6,
                            padding: '6px 10px',
                            borderRadius: 10,
                            background: 'rgba(255,255,255,0.05)',
                            border: `1px solid ${T.border}`,
                          }}
                        >
                          <span style={{ fontSize: 12, fontWeight: T.fontWeightBold, color: '#22c55e' }}>
                            {memoryGraph.links?.length ?? 0}
                          </span>
                          <span style={{ fontSize: 10, color: T.textMuted }}>连接</span>
                        </div>
                      </div>
                      <Segmented
                        className="creator-segmented-graph"
                        size="small"
                        value={graphMode}
                        onChange={(v) => setGraphMode(v as '2d' | '3d')}
                        options={[
                          { value: '2d', label: '2D' },
                          { value: '3d', label: '3D' },
                        ]}
                        style={{ background: T.segBg }}
                      />
                    </div>
                    <div ref={graphContainerRef} style={{ flex: 1, minHeight: 280, maxHeight: 420 }}>
                      {memoryLoading ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: T.textDim }}>加载中…</div>
                      ) : !memoryGraph.nodes.length ? (
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: T.textDim, fontSize: 13 }}>暂无图谱数据</div>
                      ) : (
                        graphMode === '2d' ? (
                          <MemoryGraphD3
                            data={memoryGraph}
                            width={graphSize.width}
                            height={graphSize.height}
                            onNodeClick={async (n) => {
                              try {
                                const r = await fetch(`${API_BASE}/api/memory/note/${encodeURIComponent(n.id)}?project_id=${encodeURIComponent(projectId)}`);
                                if (r.ok) {
                                  const note = await r.json();
                                  setSelectedNode({ ...note, related: note.related } as GraphNode);
                                } else {
                                  setSelectedNode(n);
                                }
                              } catch {
                                setSelectedNode(n);
                              }
                            }}
                          />
                        ) : (
                          <MemoryGraphThree
                            data={memoryGraph}
                            width={graphSize.width}
                            height={graphSize.height}
                            onNodeClick={async (n) => {
                              try {
                                const r = await fetch(`${API_BASE}/api/memory/note/${encodeURIComponent(n.id)}?project_id=${encodeURIComponent(projectId)}`);
                                if (r.ok) {
                                  const note = await r.json();
                                  setSelectedNode({ ...note, related: note.related } as GraphNode);
                                } else {
                                  setSelectedNode(n);
                                }
                              } catch {
                                setSelectedNode(n);
                              }
                            }}
                          />
                        )
                      )}
                    </div>
                    {/* 参考 MemoryGraphSection 底部提示 */}
                    {memoryGraph.nodes.length > 0 && (
                      <div
                        style={{
                          marginTop: 8,
                          paddingTop: 8,
                          borderTop: `1px solid ${T.border}`,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: 6,
                          flexShrink: 0,
                        }}
                      >
                        <span style={{ width: 5, height: 5, borderRadius: '50%', background: T.accent }} />
                        <span style={{ fontSize: 10, color: T.textDim }}>
                          点击节点查看记忆详情
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div
              style={{
                width: 56,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                paddingTop: 20,
              }}
            >
              <Tooltip title="展开记忆" placement="left">
                <Button
                  type="text"
                  size="small"
                  icon={<DatabaseOutlined />}
                  onClick={() => setMemoryOpen(true)}
                  style={{ color: T.textMuted }}
                  className="creator-icon-btn"
                />
              </Tooltip>
            </div>
          )}
        </motion.aside>
      </div>

      <MemoryDetailDrawer
        open={!!selectedNode}
        onClose={() => setSelectedNode(null)}
        node={selectedNode}
        graphData={memoryGraph}
      />

      <style>{`
        .creator-root .creator-segmented-mode .ant-segmented-item-selected,
        .creator-root .creator-segmented-memory .ant-segmented-item-selected,
        .creator-root .creator-segmented-graph .ant-segmented-item-selected {
          background: ${T.segSelectedBg} !important;
          color: ${T.segSelectedText} !important;
          font-weight: ${T.fontWeightMedium};
        }
        .creator-root .creator-segmented-mode .ant-segmented-item:not(.ant-segmented-item-selected),
        .creator-root .creator-segmented-memory .ant-segmented-item:not(.ant-segmented-item-selected),
        .creator-root .creator-segmented-graph .ant-segmented-item:not(.ant-segmented-item-selected) {
          color: ${T.segUnselectedText};
        }
        .creator-root .creator-ghost-btn:hover {
          border-color: ${T.ghostHoverBorder} !important;
          color: ${T.ghostText} !important;
          background: ${T.ghostHoverBg} !important;
        }
        .creator-root .creator-icon-btn:hover {
          color: ${T.textBright} !important;
        }
        .creator-root .creator-memory-list-item:hover {
          background: rgba(255,255,255,0.06) !important;
          border-color: rgba(255,255,255,0.12) !important;
        }
        .creator-root .creator-send-btn:hover:not(:disabled) {
          background: ${T.primaryHover} !important;
          transform: translateY(-1px);
        }
        .creator-markdown { color: ${T.text}; line-height: 1.7; }
        .creator-markdown h1,.creator-markdown h2,.creator-markdown h3 { color: ${T.textBright}; margin: 16px 0 10px; font-weight: ${T.fontWeightSemibold}; }
        .creator-markdown p { margin: 10px 0; }
        .creator-markdown code { background: rgba(255,75,47,0.12); padding: 2px 8px; border-radius: 6px; font-size: 0.9em; }
        .creator-markdown pre { background: rgba(24,24,32,0.9); padding: 16px; border-radius: ${T.radiusMd}px; overflow-x: auto; margin: 14px 0; border: 1px solid ${T.border}; }
        .creator-markdown ul,.creator-markdown ol { padding-left: 22px; margin: 10px 0; }
        .creator-markdown a { color: ${T.accent}; }
        .creator-markdown blockquote { border-left: 3px solid ${T.accent}; padding-left: 14px; margin: 14px 0; color: ${T.textMuted}; }
      `}</style>
    </div>
  );
};

export default CreatorPage;
