/** 记忆图谱 mock：实体、事实、原子笔记 → 节点；关系 → 边 */

export type NodeType = 'entity' | 'fact' | 'atom';

export interface GraphNode {
  id: string;
  label: string;
  type: NodeType;
  brief?: string;
  source?: string;
  /** 原子笔记正文片段 */
  body?: string;
  /** 关联节点（来自 /api/memory/note 时使用） */
  related?: Array<{ node: { id: string; label: string }; relation?: string }>;
}

export interface GraphLink {
  source: string;
  target: string;
  relation?: string;
}

export interface MemoryGraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export const MEMORY_GRAPH_DATA: MemoryGraphData = {
  nodes: [
    { id: 'n1', label: '林彻', type: 'entity', brief: '主角，异常值零点七' },
    { id: 'n2', label: '赫拉', type: 'entity', brief: '系统联络员' },
    { id: 'n3', label: '阿九', type: 'entity', brief: '林彻好友' },
    { id: 'n4', label: '小满', type: 'entity', brief: '同学' },
    { id: 'n5', label: '零点七', type: 'entity', brief: '异常值阈值' },
    { id: 'n6', label: '灰布兔子', type: 'entity', brief: '与母亲芯片相关' },
    { id: 'f1', label: '林彻拒绝情绪微调', type: 'fact', source: '第1章' },
    { id: 'f2', label: '异常值零点九者被送深度优化', type: 'fact', source: '第1章' },
    { id: 'a1', label: '母亲芯片', type: 'atom', brief: '线索物', body: '赫拉核心、认亲与自毁指令相关。' },
  ],
  links: [
    { source: 'n1', target: 'n3', relation: '好友' },
    { source: 'n1', target: 'n4', relation: '同学' },
    { source: 'n1', target: 'n5', relation: '异常值' },
    { source: 'n2', target: 'n1', relation: '联络' },
    { source: 'n1', target: 'f1', relation: '涉及' },
    { source: 'n5', target: 'f2', relation: '涉及' },
    { source: 'n6', target: 'a1', relation: '关联' },
    { source: 'n1', target: 'a1', relation: '关联' },
    { source: 'n2', target: 'a1', relation: '关联' },
  ],
};
