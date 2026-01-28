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

const { TextArea } = Input;
const { Text } = Typography;

const API_BASE = API_URL;

// 智能体定义
const AGENTS = [
  { key: 'planner', name: '大纲', icon: <BulbOutlined />, color: '***REMOVED***f59e0b' },
  { key: 'writer', name: '写手', icon: <EditOutlined />, color: '***REMOVED***8b5cf6' },
  { key: 'memory', name: '记忆', icon: <DatabaseOutlined />, color: '***REMOVED***06b6d4' },
  { key: 'editor', name: '润色', icon: <EditOutlined />, color: '***REMOVED***10b981' },
  { key: 'qa', name: '质检', icon: <SafetyCertificateOutlined />, color: '***REMOVED***ec4899' },
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
  const projectId = '完美之墙';

  const [memoryEntities, setMemoryEntities] = useState<Array<{ id: string; name: string; type?: string; brief?: string }>>([]);
  const [memoryGraph, setMemoryGraph] = useState<MemoryGraphData>({ nodes: [], links: [] });
  const [memoryRecents, setMemoryRecents] = useState<string[]>([]);
  const [memoryLoading, setMemoryLoading] = useState(false);
  const graphContainerRef = useRef<HTMLDivElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const streamEndRef = useRef<Set<string>>(new Set());

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

  useEffect(() => {
    if (!memoryOpen) return;
    setMemoryLoading(true);
    const q = new URLSearchParams({ project_id: projectId });
    Promise.all([
      fetch(`${API_BASE}/api/memory/entities?${q}`).then((r) => (r.ok ? r.json() : [])),
      fetch(`${API_BASE}/api/memory/graph?${q}`).then((r) => (r.ok ? r.json() : { nodes: [], links: [] })),
      fetch(`${API_BASE}/api/memory/recents?${q}`).then((r) => (r.ok ? r.json() : [])),
    ])
      .then(([entities, graph, recents]) => {
        setMemoryEntities(Array.isArray(entities) ? entities : []);
        setMemoryGraph(
          graph && Array.isArray(graph.nodes)
            ? { nodes: graph.nodes, links: graph.links || [] }
            : { nodes: [], links: [] }
        );
        setMemoryRecents(Array.isArray(recents) ? recents : []);
      })
      .catch(() => {})
      .finally(() => setMemoryLoading(false));
  }, [memoryOpen, projectId]);

  const scrollToBottom = useCallback(() => {
    requestAnimationFrame(() => {
      containerRef.current?.scrollTo({ top: containerRef.current.scrollHeight, behavior: 'smooth' });
    });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const runOrchestration = useCallback(async () => {
    const order: AgentKey[] = ['planner', 'memory', 'writer', 'editor', 'qa'];
    setOrchestration([]);
    for (const a of order) {
      setActiveAgent(a);
      setOrchestration((prev) => [...prev, a]);
      await new Promise((r) => setTimeout(r, 400));
    }
    setActiveAgent(null);
  }, []);

  const handleSend = async () => {
    const raw = input.trim();
    if (!raw || loading) return;

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
    const assistantMsg: Message = {
      id: aid,
      role: 'assistant',
      content: '',
      ts: new Date(),
      agent: 'writer',
      streaming: !useCreatorApi,
    };
    setMessages((prev) => [...prev, assistantMsg]);
    runOrchestration();

    try {
      if (useCreatorApi) {
        const res = await fetch(`${API_BASE}/api/creator/run`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mode, input: raw, project_id: projectId }),
        });
        const data = (await res.json()) as { code?: number; message?: string; content?: string };
        const text = data.code === 0 ? (data.content || '') : (data.message || '请求失败');
        streamEndRef.current.add(aid);
        setMessages((prev) =>
          prev.map((m) => (m.id === aid ? { ...m, content: text, streaming: false } : m))
        );
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
        ? '创作服务请求失败，请确认后端已启动且 /api/creator/run 可用。'
        : '多智能体创作助手已就绪。当前为演示模式，正在模拟编排流程；实际创作需对接后端编排与记忆服务。';
      setMessages((prev) =>
        prev.map((m) => (m.id === aid ? { ...m, content: fallback, streaming: false } : m))
      );
    } finally {
      setLoading(false);
      scrollToBottom();
    }
  };

  const getAgent = (k?: AgentKey) => AGENTS.find((a) => a.key === k);
  const modeLabels: Record<typeof mode, string> = {
    create: '创作',
    continue: '续写',
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
          height: 64,
          borderBottom: `1px solid ${T.borderHeader}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          flexShrink: 0,
          background: T.bgHeader,
          backdropFilter: T.headerBlur,
          WebkitBackdropFilter: T.headerBlur,
        }}
      >
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
        <Segmented
          className="creator-segmented-mode"
          value={mode}
          onChange={(v) => setMode(v as typeof mode)}
          options={[
            { value: 'create', label: '创作' },
            { value: 'continue', label: '续写' },
            { value: 'polish', label: '润色' },
            { value: 'chat', label: '对话' },
          ]}
          style={{ background: T.segBg }}
        />
      </header>

      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
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
                  <span style={{ width: 5, height: 5, borderRadius: '50%', background: '***REMOVED***22c55e' }} />
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

        {/* 中间：创作画布 */}
        <div
          style={{
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            minWidth: 0,
            position: 'relative',
            background: T.bgCanvas,
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
              overflowY: 'auto',
              overflowX: 'hidden',
              padding: 40,
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
                    color: '***REMOVED***fff',
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
                    选择模式后输入意图，开始创作。
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
                          setInput(m === 'create' ? '写一个科幻短篇，主题：完美之墙' : m === 'continue' ? '从上一章结尾续写' : '润色这段文字');
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

          {/* 输入区 */}
          <div
            style={{
              borderTop: `1px solid ${T.border}`,
              padding: '24px 40px 28px',
              background: T.bgInput,
            }}
          >
            <div style={{ maxWidth: 760, margin: '0 auto', display: 'flex', gap: 16, alignItems: 'flex-end' }}>
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
                    height: 44,
                    minWidth: 44,
                    background: T.primaryBg,
                    border: 'none',
                    borderRadius: T.radiusMd,
                  }}
                />
              </Tooltip>
            </div>
            <div
              style={{
                maxWidth: 760,
                margin: '10px auto 0',
                fontSize: 12,
                color: T.textDim,
                textAlign: 'right',
              }}
            >
              {loading ? '智能体编排中…' : 'Enter 发送 · Shift+Enter 换行'}
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
                      <span style={{ width: 6, height: 6, borderRadius: '50%', background: '***REMOVED***22c55e' }} />
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
                        <div style={{ padding: '16px 20px', borderBottom: `1px solid ${T.border}` }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <span style={{ fontSize: 14, fontWeight: T.fontWeightSemibold, color: T.textBright }}>记忆列表</span>
                            <span style={{ fontSize: 11, color: T.textMuted }}>{memoryEntities.length} 条</span>
                          </div>
                        </div>
                        <div style={{ flex: 1, padding: 16, overflowY: 'auto' }}>
                          {memoryEntities.slice(0, 60).map((e, idx) => (
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
                                {String(idx + 1).padStart(2, '0')}
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
                        {memoryRecents.length > 0 && (
                          <div style={{ padding: 12, borderTop: `1px solid ${T.border}` }}>
                            <div style={{ fontSize: 11, fontWeight: T.fontWeightSemibold, color: T.textMuted, marginBottom: 8, letterSpacing: '0.04em' }}>最近检索</div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                              {memoryRecents.slice(0, 3).map((r, i) => (
                                <div
                                  key={i}
                                  style={{
                                    fontSize: 11,
                                    color: T.textMuted,
                                    padding: '8px 12px',
                                    background: T.bgRecall,
                                    borderRadius: T.radiusSm,
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 8,
                                  }}
                                >
                                  <LinkOutlined style={{ color: T.accent, fontSize: 12 }} /> {r}
                                </div>
                              ))}
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
                          <span style={{ fontSize: 12, fontWeight: T.fontWeightBold, color: '***REMOVED***22c55e' }}>
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
                    <div ref={graphContainerRef} style={{ flex: 1, minHeight: 380 }}>
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
