/**
 * 实时 Agent 工作流图 — 参考 WorkflowOrchestrator
 * 画布网格 + 可配置节点/边，支持动态 agents，运行工作流 / 进度 / 状态 / 实时编排
 */
import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import {
  SearchOutlined,
  EditOutlined,
  PictureOutlined,
  CodeOutlined,
  CheckCircleOutlined,
  ThunderboltOutlined,
  LoadingOutlined,
} from '@ant-design/icons';
import { INTRO_THEME } from './creatorTheme';

const T = INTRO_THEME;

const DEFAULT_AGENTS = [
  { id: 'research', name: '研究Agent', icon: <SearchOutlined />, color: '#3b82f6' },
  { id: 'writing', name: '写作Agent', icon: <EditOutlined />, color: '#10b981' },
  { id: 'image', name: '图像Agent', icon: <PictureOutlined />, color: '#f59e0b' },
  { id: 'code', name: '代码Agent', icon: <CodeOutlined />, color: '#06b6d4' },
  { id: 'review', name: '审核Agent', icon: <CheckCircleOutlined />, color: '#ec4899' },
] as const;

const DEFAULT_POSITIONS: Record<string, { x: number; y: number }> = {
  research: { x: 100, y: 200 },
  writing: { x: 300, y: 140 },
  image: { x: 300, y: 260 },
  code: { x: 500, y: 140 },
  review: { x: 700, y: 200 },
};

const DEFAULT_LINKS = [
  { source: 'research', target: 'writing' },
  { source: 'research', target: 'image' },
  { source: 'writing', target: 'code' },
  { source: 'writing', target: 'review' },
  { source: 'image', target: 'review' },
  { source: 'code', target: 'review' },
];

const DEFAULT_RUN_ORDER = ['research', 'writing', 'image', 'code', 'review'];

export interface WorkflowAgent {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
}

export interface WorkflowGraphProps {
  /** 动态 agents，不传则用默认 研究/写作/图像/代码/审核 */
  agents?: WorkflowAgent[];
  /** 边：source -> target */
  links?: { source: string; target: string }[];
  /** 节点位置，不传则用默认布局 */
  positions?: Record<string, { x: number; y: number }>;
  /** 运行顺序，不传则用 DEFAULT_RUN_ORDER */
  runOrder?: string[];
  /** 是否 demo 自动循环运行 */
  demo?: boolean;
  /** 画布高度 */
  height?: number;
  /** 画布逻辑宽度，与 positions 坐标系一致 */
  width?: number;
  /** 画布与内容等比放大倍率，默认 1 */
  scale?: number;
  /** 左侧是否显示 Agent 指挥中心 */
  showAgentCenter?: boolean;
  className?: string;
}

type AgentStatus = 'idle' | 'running' | 'completed';

function useWorkflowRun(
  agentIds: string[],
  runOrder: string[],
  demo: boolean,
  agentNames: Record<string, string>
) {
  const [status, setStatus] = useState<Record<string, AgentStatus>>(() =>
    Object.fromEntries(agentIds.map((id) => [id, 'idle']))
  );
  const [completed, setCompleted] = useState<string[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const runRef = useRef<number>(0);
  const scheduleRef = useRef<() => void>(() => {});

  const name = (id: string) => agentNames[id] ?? id;

  const runWorkflow = useCallback(() => {
    setIsRunning(true);
    setCompleted([]);
    setStatus(() => Object.fromEntries(agentIds.map((id) => [id, 'idle'])));
    setLogs(['🚀 启动工作流编排...']);
    const runId = ++runRef.current;

    const order = runOrder.filter((id) => agentIds.includes(id));
    let idx = 0;

    const next = () => {
      if (runId !== runRef.current) return;
      if (idx >= order.length) {
        setIsRunning(false);
        setLogs((l) => [...l, '✅ 工作流执行完成！']);
        if (demo) {
          setTimeout(() => {
            if (runId !== runRef.current) return;
            setCompleted([]);
            setStatus(() => Object.fromEntries(agentIds.map((id) => [id, 'idle'])));
            setTimeout(() => scheduleRef.current(), 1200);
          }, 1500);
        }
        return;
      }

      const id = order[idx];
      setStatus((s) => ({ ...s, [id]: 'running' }));
      setLogs((l) => [...l, `▶️ ${name(id)} 开始执行...`]);

      setTimeout(() => {
        if (runId !== runRef.current) return;
        setStatus((s) => ({ ...s, [id]: 'completed' }));
        setCompleted((c) => [...c, id]);
        setLogs((l) => [...l, `✓ ${name(id)} 执行完成`]);
        idx += 1;
        setTimeout(next, 400);
      }, 1800);
    };

    next();
  }, [agentIds, runOrder, demo, agentNames]);

  scheduleRef.current = runWorkflow;

  useEffect(() => {
    if (!demo) return;
    const t = setTimeout(() => scheduleRef.current(), 600);
    return () => clearTimeout(t);
  }, [demo]);

  return { status, completed, logs, isRunning, runWorkflow };
}

function bezierPath(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  padding = 50
): string {
  const cx1 = x1 + padding;
  const cy1 = y1;
  const cx2 = x2 - padding;
  const cy2 = y2;
  return `M ${x1} ${y1} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${x2} ${y2}`;
}

const AGENT_CENTER_WIDTH = 220;

export const WorkflowGraph: React.FC<WorkflowGraphProps> = ({
  agents = DEFAULT_AGENTS as unknown as WorkflowAgent[],
  links = DEFAULT_LINKS,
  positions = DEFAULT_POSITIONS,
  runOrder = DEFAULT_RUN_ORDER,
  demo = false,
  height = 420,
  width = 800,
  scale: scaleProp = 1,
  showAgentCenter = false,
  className,
}) => {
  const agentIds = useMemo(() => agents.map((a) => a.id), [agents]);
  const agentNames = useMemo(
    () => Object.fromEntries(agents.map((a) => [a.id, a.name])),
    [agents]
  );
  const { status, completed, logs, isRunning, runWorkflow } = useWorkflowRun(
    agentIds,
    runOrder,
    demo,
    agentNames
  );

  const scale = Math.max(0.5, Math.min(2, scaleProp));
  const w = Math.round(width * scale);
  const h = Math.round(height * scale);
  const nodeSize = useMemo(
    () => ({ w: Math.round(88 * scale), h: Math.round(76 * scale) }),
    [scale]
  );
  const positionsScaled = useMemo(
    () =>
      Object.fromEntries(
        Object.entries(positions).map(([id, p]) => [
          id,
          { x: p.x * scale, y: p.y * scale },
        ])
      ),
    [positions, scale]
  );

  const getNodeCenter = useCallback(
    (id: string) => {
      const p = positionsScaled[id] ?? { x: 0, y: 0 };
      return { x: p.x + nodeSize.w / 2, y: p.y + nodeSize.h / 2 };
    },
    [positionsScaled, nodeSize]
  );

  const linkPaths = useMemo(() => {
    return links.map((l) => {
      const a = getNodeCenter(l.source);
      const b = getNodeCenter(l.target);
      const dx = b.x - a.x;
      const dy = b.y - a.y;
      const dist = Math.hypot(dx, dy) || 1;
      const nx = dx / dist;
      const ny = dy / dist;
      const trim = Math.min(24, dist * 0.35);
      const off = nodeSize.w / 2 + trim;
      const x1 = a.x + nx * off;
      const y1 = a.y + ny * off;
      const x2 = b.x - nx * off;
      const y2 = b.y - ny * off;
      return { path: bezierPath(x1, y1, x2, y2), source: l.source, target: l.target };
    });
  }, [links, getNodeCenter]);

  const completedCount = completed.length;
  const fs = (n: number) => Math.round(n * scale);
  const totalWidth = showAgentCenter ? AGENT_CENTER_WIDTH + w : w;

  const graphDiv = (
    <div
      style={{
        position: 'relative',
        width: w,
        height: h,
        flexShrink: 0,
        background: 'linear-gradient(135deg, #f8f8f8 0%, #ffffff 100%)',
        borderRadius: 16,
        border: `1px solid ${T.border}`,
        overflow: 'hidden',
        boxShadow: T.shadowCard,
      }}
    >
      {/* 网格背景 */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity: 0.4,
          backgroundImage: `
            linear-gradient(to right, #e5e5e5 1px, transparent 1px),
            linear-gradient(to bottom, #e5e5e5 1px, transparent 1px)
          `,
          backgroundSize: `${fs(40)}px ${fs(40)}px`,
        }}
      />

      {/* 边 */}
      <svg
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          overflow: 'visible',
        }}
        viewBox={`0 0 ${w} ${h}`}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <marker
            id="workflow-arrow"
            markerWidth="8"
            markerHeight="6"
            refX="7"
            refY="3"
            orient="auto"
          >
            <path d="M0 0 L8 3 L0 6 Z" fill="rgba(255,75,47,0.5)" />
          </marker>
          <marker
            id="workflow-arrow-active"
            markerWidth="8"
            markerHeight="6"
            refX="7"
            refY="3"
            orient="auto"
          >
            <path d="M0 0 L8 3 L0 6 Z" fill={T.accent} />
          </marker>
        </defs>
        {linkPaths.map(({ path, source, target }, i) => {
          const srcRunning = status[source] === 'running';
          const tgtRunning = status[target] === 'running';
          const isActive = srcRunning || tgtRunning;
          return (
            <g key={i}>
              <path
                d={path}
                fill="none"
                stroke="rgba(255,75,47,0.25)"
                strokeWidth={2}
                strokeDasharray="6 10"
                markerEnd="url(#workflow-arrow)"
              />
              {isActive && (
                <path
                  d={path}
                  fill="none"
                  stroke={T.accent}
                  strokeWidth={2.5}
                  markerEnd="url(#workflow-arrow-active)"
                />
              )}
            </g>
          );
        })}
      </svg>

      {/* 节点 */}
      {agents.map((agent) => {
        const pos = positionsScaled[agent.id] ?? { x: 0, y: 0 };
        const st = status[agent.id];
        const isRunning = st === 'running';
        const isDone = st === 'completed';
        return (
          <motion.div
            key={agent.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            style={{
              position: 'absolute',
              left: pos.x,
              top: pos.y,
              width: nodeSize.w,
              height: nodeSize.h,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: `${fs(8)}px ${fs(6)}px`,
              borderRadius: fs(12),
              background: '#fff',
              border: `2px solid ${isRunning ? T.accent : isDone ? '#22c55e' : '#e5e5e5'}`,
              boxShadow: isRunning
                ? `0 0 0 3px ${T.accent}20`
                : '0 2px 8px rgba(0,0,0,0.06)',
              cursor: 'default',
              transition: 'border-color 0.2s, box-shadow 0.2s',
            }}
          >
            <div
              style={{
                width: fs(36),
                height: fs(36),
                borderRadius: fs(10),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: fs(4),
                background: `${agent.color}18`,
                color: agent.color,
                fontSize: fs(16),
              }}
            >
              {isRunning ? (
                <LoadingOutlined spin />
              ) : (
                agent.icon
              )}
            </div>
            <div
              style={{
                fontSize: fs(11),
                fontWeight: T.fontWeightSemibold,
                color: T.textBright,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                maxWidth: '100%',
                textAlign: 'center',
              }}
            >
              {agent.name}
            </div>
            {(isRunning || isDone) && (
              <div
                style={{
                  position: 'absolute',
                  top: fs(4),
                  right: fs(4),
                  width: fs(8),
                  height: fs(8),
                  borderRadius: '50%',
                  background: isRunning ? T.accent : '#22c55e',
                  border: '2px solid #fff',
                }}
              />
            )}
          </motion.div>
        );
      })}

      {/* 底部控制栏 */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: fs(12),
          padding: `${fs(12)}px ${fs(16)}px`,
          background: 'rgba(255,255,255,0.95)',
          borderTop: `1px solid ${T.border}`,
          backdropFilter: 'blur(8px)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: fs(12) }}>
          <button
            type="button"
            onClick={runWorkflow}
            disabled={isRunning || demo}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: fs(8),
              padding: `${fs(8)}px ${fs(16)}px`,
              borderRadius: fs(10),
              border: 'none',
              background: isRunning || demo ? '#f0f0f0' : T.primaryBg,
              color: isRunning || demo ? T.textDim : '#fff',
              fontSize: fs(13),
              fontWeight: T.fontWeightSemibold,
              cursor: isRunning || demo ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s, transform 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!isRunning && !demo) {
                e.currentTarget.style.background = T.primaryHover;
                e.currentTarget.style.transform = 'scale(1.02)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isRunning && !demo) {
                e.currentTarget.style.background = T.primaryBg;
                e.currentTarget.style.transform = 'scale(1)';
              }
            }}
          >
            {isRunning ? (
              <>
                <LoadingOutlined spin style={{ fontSize: fs(14) }} />
                执行中…
              </>
            ) : (
              <>
                <ThunderboltOutlined style={{ fontSize: fs(14) }} />
                运行工作流
              </>
            )}
          </button>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: fs(6),
              padding: `${fs(6)}px ${fs(12)}px`,
              borderRadius: fs(10),
              background: 'rgba(0,0,0,0.04)',
              border: `1px solid ${T.border}`,
            }}
          >
            <span style={{ fontSize: fs(14), color: T.accent }}>◎</span>
            <span style={{ fontSize: fs(12), color: T.textMuted, fontFamily: 'monospace' }}>
              {completedCount}/{agents.length} 完成
            </span>
          </div>
        </div>

        <div
          style={{
            flex: 1,
            maxWidth: fs(280),
            margin: `0 ${fs(12)}px`,
            padding: `${fs(6)}px ${fs(12)}px`,
            borderRadius: fs(8),
            background: 'rgba(0,0,0,0.04)',
            fontSize: fs(12),
            fontFamily: 'monospace',
            color: T.textMuted,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}
        >
          {logs[logs.length - 1] ?? '等待启动…'}
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: fs(6) }}>
          <ThunderboltOutlined style={{ fontSize: fs(14), color: T.accent }} />
          <span style={{ fontSize: fs(12), color: T.textMuted }}>实时编排</span>
        </div>
      </div>
    </div>
  );

  const agentCenter = showAgentCenter ? (
    <div
      style={{
        width: AGENT_CENTER_WIDTH,
        height: h,
        flexShrink: 0,
        display: 'flex',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #f8f8f8 0%, #ffffff 100%)',
        border: `1px solid ${T.border}`,
        borderRadius: 16,
        overflow: 'hidden',
        boxShadow: T.shadowCard,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 14px',
          borderBottom: `1px solid ${T.border}`,
          background: 'rgba(0,0,0,0.03)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <ThunderboltOutlined style={{ fontSize: 16, color: T.accent }} />
          <span style={{ fontSize: 13, fontWeight: T.fontWeightBold, color: T.textBright }}>
            Agent 指挥中心
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
          <span
            style={{
              width: 6,
              height: 6,
              borderRadius: '50%',
              background: '#22c55e',
            }}
          />
          <span style={{ fontSize: 10, color: '#22c55e', fontFamily: 'monospace' }}>
            系统正常
          </span>
        </div>
      </div>
      <div style={{ padding: 10, display: 'flex', flexDirection: 'column', gap: 8, flex: 1, overflowY: 'auto' }}>
        {agents.map((a) => {
          const st = status[a.id];
          const task = st === 'running' ? '执行中' : st === 'completed' ? '已完成' : '等待输入';
          return (
            <div
              key={a.id}
              style={{
                padding: 10,
                borderRadius: 10,
                background: st === 'running' ? `${a.color}12` : 'rgba(0,0,0,0.02)',
                border: `1px solid ${st === 'running' ? `${a.color}30` : 'transparent'}`,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 8,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: `${a.color}20`,
                    color: a.color,
                    fontSize: 14,
                  }}
                >
                  {a.icon}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, fontWeight: T.fontWeightSemibold, color: T.textBright, marginBottom: 2 }}>
                    {a.name}
                  </div>
                  <div style={{ fontSize: 10, color: T.textMuted }}>{task}</div>
                </div>
                {(st === 'running' || st === 'completed') && (
                  <span
                    style={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      background: st === 'running' ? T.accent : '#22c55e',
                    }}
                  />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  ) : null;

  return (
    <div
      className={className}
      style={{
        display: 'flex',
        flexDirection: 'row',
        alignItems: 'stretch',
        gap: 16,
        width: '100%',
        maxWidth: totalWidth,
        height: showAgentCenter ? h : undefined,
        margin: '0 auto',
      }}
    >
      {showAgentCenter && agentCenter}
      {graphDiv}
    </div>
  );
};
