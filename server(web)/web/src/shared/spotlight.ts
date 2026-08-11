import type { ClientInfo, IncidentState, RoleName } from './types';
import { translateRoleLabel, translateRoleStatus } from './domain';

/**
 * AI / 规则引擎驱动的“动态聚焦”指令。
 *
 * 大屏的注意力模型：任意时刻只重点呈现一个目标（终端 / 调度过程 / 系统状态），
 * 由 SpotlightEngine 根据事件状态机推导；后端后续可在 IncidentState 上增加
 * `spotlight` 字段（由 AI 调度引擎输出），前端无需改动即可接管。
 */
export type SpotlightTarget =
  | 'PATIENT'
  | 'PRIME'
  | 'RUNNER'
  | 'GUIDE'
  | 'AI_DISPATCH'
  | 'AED'
  | 'SYSTEM';

export type SpotlightSeverity = 'info' | 'active' | 'critical';
export type SpotlightSource = 'STATE_MACHINE' | 'AI' | 'SERVER';

export interface SpotlightDirective {
  id: string;
  target: SpotlightTarget;
  severity: SpotlightSeverity;
  title: string;
  message: string;
  source: SpotlightSource;
  ts: number;
}

export interface SpotlightSnapshot {
  current: SpotlightDirective | null;
  timeline: SpotlightDirective[];
}

const LOG_KEYWORDS: Array<{
  keyword: string;
  target: SpotlightTarget;
  severity: SpotlightSeverity;
  title: string;
  message: string;
}> = [
  {
    keyword: 'AED shock delivered',
    target: 'PRIME',
    severity: 'active',
    title: '除颤完成',
    message: '核心施救端已完成一次 AED 除颤，继续胸外按压。',
  },
  {
    keyword: 'AED analysis',
    target: 'PRIME',
    severity: 'active',
    title: 'AED 分析中',
    message: '核心施救端正在执行 AED 心律分析。',
  },
  {
    keyword: 'AED delivered',
    target: 'RUNNER',
    severity: 'active',
    title: 'AED 已送达',
    message: 'AED 保障端已把设备送达患者位置。',
  },
  {
    keyword: 'AED picked',
    target: 'RUNNER',
    severity: 'active',
    title: 'AED 已取到',
    message: '取送者已取到 AED，正在返回患者位置。',
  },
  {
    keyword: 'CPR started',
    target: 'PRIME',
    severity: 'active',
    title: 'CPR 已启动',
    message: '核心施救端开始胸外按压，节拍器已同步。',
  },
  {
    keyword: 'ambulance arrived',
    target: 'GUIDE',
    severity: 'active',
    title: '救护车已到场',
    message: '清障接驳端已引导救护车进入现场。',
  },
  {
    keyword: 'handover',
    target: 'GUIDE',
    severity: 'info',
    title: '完成交接',
    message: '专业急救力量已接管，事件进入交接归档。',
  },
  {
    keyword: 'dispatch',
    target: 'AI_DISPATCH',
    severity: 'active',
    title: 'AI 智能分派',
    message: '调度引擎正在生成三类协同任务。',
  },
];

const STATUS_DIRECTIVES: Array<{
  role: RoleName;
  status: string;
  severity: SpotlightSeverity;
  title: string;
  message: string;
}> = [
  {
    role: 'PRIME',
    status: 'AED_SHOCK_DELIVERED',
    severity: 'active',
    title: '除颤完成',
    message: '核心施救端已完成一次 AED 除颤。',
  },
  {
    role: 'PRIME',
    status: 'AED_ANALYZING',
    severity: 'active',
    title: 'AED 分析中',
    message: '核心施救端正在执行 AED 心律分析。',
  },
  {
    role: 'PRIME',
    status: 'CPR_STARTED',
    severity: 'active',
    title: 'CPR 进行中',
    message: '核心施救端已开始胸外按压。',
  },
  {
    role: 'RUNNER',
    status: 'AED_DELIVERED',
    severity: 'active',
    title: 'AED 已送达',
    message: 'AED 保障端已把设备送达患者位置。',
  },
  {
    role: 'RUNNER',
    status: 'AED_PICKED',
    severity: 'active',
    title: 'AED 已取到',
    message: '取送者已取到 AED，正在返回患者位置。',
  },
  {
    role: 'GUIDE',
    status: 'HANDOVER_COMPLETED',
    severity: 'info',
    title: '交接归档完成',
    message: '专业急救力量已接管，事件进入归档。',
  },
  {
    role: 'GUIDE',
    status: 'AMBULANCE_ARRIVED',
    severity: 'active',
    title: '救护车已到场',
    message: '清障接驳端已引导救护车进入现场。',
  },
];

const ROLE_JOIN_MESSAGE: Record<RoleName, string> = {
  PRIME: '核心施救端已确认响应，正在前往患者位置。',
  RUNNER: 'AED 保障端已确认响应，正在前往最近 AED 点位。',
  GUIDE: '清障接驳端已确认响应，正在疏通通道。',
};

function findLatestLogDirective(state: IncidentState | null): SpotlightDirective | null {
  if (!state) {
    return null;
  }
  const logs = [...(state.logs ?? [])].sort((a, b) => b.ts - a.ts);
  for (const log of logs) {
    const lower = log.msg.toLowerCase();
    for (const rule of LOG_KEYWORDS) {
      if (lower.includes(rule.keyword)) {
        return {
          id: `log-${log.ts}-${rule.keyword}`,
          target: rule.target,
          severity: rule.severity,
          title: rule.title,
          message: rule.message,
          source: 'STATE_MACHINE',
          ts: log.ts,
        };
      }
    }
  }
  return null;
}

function findRoleDirective(state: IncidentState | null): SpotlightDirective | null {
  if (!state) {
    return null;
  }
  const candidates: SpotlightDirective[] = [];
  for (const rule of STATUS_DIRECTIVES) {
    const roleState = state.roles?.[rule.role];
    if (roleState?.status === rule.status) {
      candidates.push({
        id: `role-${rule.role}-${rule.status}`,
        target: rule.role === 'PRIME' ? 'PRIME' : rule.role === 'RUNNER' ? 'RUNNER' : 'GUIDE',
        severity: rule.severity,
        title: rule.title,
        message: rule.message,
        source: 'STATE_MACHINE',
        ts: state.logs?.[state.logs.length - 1]?.ts ?? Date.now(),
      });
    }
  }
  // 最新发生的角色状态优先
  candidates.sort((a, b) => b.ts - a.ts);
  return candidates[0] ?? null;
}

function findJoinedDirective(state: IncidentState | null): SpotlightDirective | null {
  if (!state) {
    return null;
  }
  const joined: Array<{ role: RoleName; ts: number }> = [];
  for (const role of ['PRIME', 'RUNNER', 'GUIDE'] as RoleName[]) {
    const roleState = state.roles?.[role];
    if (roleState?.status === 'JOINED') {
      joined.push({ role, ts: state.logs?.[state.logs.length - 1]?.ts ?? 0 });
    }
  }
  joined.sort((a, b) => b.ts - a.ts);
  const latest = joined[0];
  if (!latest) {
    return null;
  }
  const role = latest.role;
  return {
    id: `join-${role}-${latest.ts}`,
    target: role === 'PRIME' ? 'PRIME' : role === 'RUNNER' ? 'RUNNER' : 'GUIDE',
    severity: 'active',
    title: `${translateRoleLabel(role)}已响应`,
    message: ROLE_JOIN_MESSAGE[role],
    source: 'STATE_MACHINE',
    ts: latest.ts,
  };
}

function findPatientDirective(state: IncidentState | null): SpotlightDirective | null {
  if (!state) {
    return null;
  }
  const sos = state.sos;
  if (sos?.status === 'ALERTING' && state.phase === 'CREATED') {
    return {
      id: `patient-sos-${sos.startTs ?? state.logs?.[0]?.ts ?? Date.now()}`,
      target: 'PATIENT',
      severity: 'critical',
      title: '疑似心脏骤停',
      message: '患者端 SOS 已触发，系统正在确认现场并启动 AI 分派。',
      source: 'STATE_MACHINE',
      ts: sos.startTs ?? Date.now(),
    };
  }
  if (state.phase === 'DISPATCHING') {
    return {
      id: `dispatch-${state.logs?.[state.logs.length - 1]?.ts ?? Date.now()}`,
      target: 'AI_DISPATCH',
      severity: 'active',
      title: 'AI 智能分派中',
      message: '调度引擎正在根据画像、距离、AED 可达性和健康风险生成任务。',
      source: 'STATE_MACHINE',
      ts: state.logs?.[state.logs.length - 1]?.ts ?? Date.now(),
    };
  }
  return null;
}

/**
 * 事件阶段是“当前最重要进展”的权威信号：
 * 阶段推进到 AED_PICKED 就聚焦取送者，推进到 CPR 就聚焦施救者……
 * 这正好实现“取送者拿到 AED 后，系统着重显示取送者状态”。
 */
const PHASE_DIRECTIVES: Array<{
  phase: string;
  target: SpotlightTarget;
  severity: SpotlightSeverity;
  title: string;
  message: string;
}> = [
  {
    phase: 'AED_PICKED',
    target: 'RUNNER',
    severity: 'active',
    title: 'AED 已取到',
    message: '取送者已取到 AED，系统正在跟踪回送路线。',
  },
  {
    phase: 'AED_DELIVERED',
    target: 'RUNNER',
    severity: 'active',
    title: 'AED 已送达',
    message: '取送者已将 AED 送达患者位置，交接给核心施救。',
  },
  {
    phase: 'CPR',
    target: 'PRIME',
    severity: 'active',
    title: 'CPR 进行中',
    message: '核心施救端正在执行胸外按压。',
  },
  {
    phase: 'AED_ANALYZING',
    target: 'PRIME',
    severity: 'active',
    title: 'AED 分析中',
    message: '核心施救端正在执行 AED 心律分析。',
  },
  {
    phase: 'SHOCK_DELIVERED',
    target: 'PRIME',
    severity: 'active',
    title: '除颤完成',
    message: '核心施救端已完成一次 AED 除颤。',
  },
  {
    phase: 'HANDOVER',
    target: 'GUIDE',
    severity: 'info',
    title: '完成交接',
    message: '专业急救力量已接管，事件进入交接归档。',
  },
];

function findPhaseDirective(state: IncidentState | null): SpotlightDirective | null {
  if (!state) {
    return null;
  }
  for (const rule of PHASE_DIRECTIVES) {
    if (state.phase === rule.phase) {
      return {
        id: `phase-${rule.phase}`,
        target: rule.target,
        severity: rule.severity,
        title: rule.title,
        message: rule.message,
        source: 'STATE_MACHINE',
        ts: state.logs?.[state.logs.length - 1]?.ts ?? Date.now(),
      };
    }
  }
  return null;
}

function findSystemDirective(state: IncidentState | null): SpotlightDirective | null {
  if (!state) {
    return null;
  }
  if (state.phase === 'ARCHIVED') {
    return {
      id: `archived-${state.logs?.[state.logs.length - 1]?.ts ?? Date.now()}`,
      target: 'SYSTEM',
      severity: 'info',
      title: '事件已归档',
      message: '本轮协同演示完成，可导出事件证据包用于复盘。',
      source: 'STATE_MACHINE',
      ts: state.logs?.[state.logs.length - 1]?.ts ?? Date.now(),
    };
  }
  return null;
}

/**
 * 事件状态机 → 聚焦指令。
 *
 * 优先级：患者告警 > AI 分派 > 最新角色状态变化 > 日志关键词 > 归档提示。
 * 后端 AI 调度引擎将来可以在 IncidentState.spotlight 直接下发指令，
 * 届时该函数会优先采纳服务端指令。
 */
export function computeSpotlightDirective(
  state: IncidentState | null,
  externalSpotlight?: SpotlightDirective | null,
): SpotlightDirective | null {
  if (externalSpotlight) {
    return externalSpotlight;
  }
  return (
    findPatientDirective(state) ??
    findPhaseDirective(state) ??
    findRoleDirective(state) ??
    findJoinedDirective(state) ??
    findLatestLogDirective(state) ??
    findSystemDirective(state)
  );
}

/** 当前事件开始以来产生的聚焦轨迹（最多 12 条），用于左侧“AI 聚焦轨迹”面板。 */
export function buildSpotlightTimeline(state: IncidentState | null): SpotlightDirective[] {
  const timeline: SpotlightDirective[] = [];
  const logs = [...(state?.logs ?? [])].sort((a, b) => a.ts - b.ts);
  for (const log of logs) {
    const lower = log.msg.toLowerCase();
    for (const rule of LOG_KEYWORDS) {
      if (lower.includes(rule.keyword)) {
        timeline.push({
          id: `timeline-${log.ts}-${rule.keyword}`,
          target: rule.target,
          severity: rule.severity,
          title: rule.title,
          message: rule.message,
          source: 'STATE_MACHINE',
          ts: log.ts,
        });
        break;
      }
    }
  }
  if (state?.sos?.status === 'ALERTING' || state?.phase === 'CREATED') {
    const sosTs = state.sos?.startTs ?? state.logs?.[0]?.ts ?? Date.now();
    if (!timeline.some((entry) => entry.target === 'PATIENT')) {
      timeline.unshift({
        id: `timeline-patient-${sosTs}`,
        target: 'PATIENT',
        severity: 'critical',
        title: '患者端告警',
        message: '疑似心脏骤停，SOS 已触发。',
        source: 'STATE_MACHINE',
        ts: sosTs,
      });
    }
  }
  if (state?.phase === 'ARCHIVED') {
    timeline.push({
      id: `timeline-archived-${state.logs?.[state.logs.length - 1]?.ts ?? Date.now()}`,
      target: 'SYSTEM',
      severity: 'info',
      title: '事件归档',
      message: '证据包可导出。',
      source: 'STATE_MACHINE',
      ts: state.logs?.[state.logs.length - 1]?.ts ?? Date.now(),
    });
  }
  return timeline.slice(-12).reverse();
}

/** 由服务端 IncidentState.spotlight 字段（未来 AI 输出）转换为指令。 */
export function parseServerSpotlight(
  value: unknown,
): SpotlightDirective | null {
  if (!value || typeof value !== 'object') {
    return null;
  }
  const raw = value as Record<string, unknown>;
  const target = raw.target as SpotlightTarget;
  const validTargets: SpotlightTarget[] = [
    'PATIENT',
    'PRIME',
    'RUNNER',
    'GUIDE',
    'AI_DISPATCH',
    'AED',
    'SYSTEM',
  ];
  if (!validTargets.includes(target)) {
    return null;
  }
  return {
    id: `server-${raw.ts ?? Date.now()}`,
    target,
    severity: (raw.severity as SpotlightSeverity) ?? 'active',
    title: String(raw.title ?? 'AI 聚焦'),
    message: String(raw.message ?? ''),
    source: 'AI',
    ts: Number(raw.ts ?? Date.now()),
  };
}

export function spotlightTargetLabel(target: SpotlightTarget): string {
  switch (target) {
    case 'PATIENT':
      return '患者端';
    case 'PRIME':
      return '核心施救';
    case 'RUNNER':
      return 'AED 保障';
    case 'GUIDE':
      return '环境清障';
    case 'AI_DISPATCH':
      return 'AI 调度';
    case 'AED':
      return 'AED 点位';
    case 'SYSTEM':
      return '系统';
  }
}

export function findClientByRole(
  clients: ClientInfo[],
  target: SpotlightTarget,
  state: IncidentState | null,
): ClientInfo | null {
  const roleMap: Partial<Record<SpotlightTarget, RoleName>> = {
    PATIENT: undefined,
    PRIME: 'PRIME',
    RUNNER: 'RUNNER',
    GUIDE: 'GUIDE',
  };
  const role = roleMap[target];
  if (role && state) {
    const userId = state.roles[role]?.userId;
    const byRole = clients.find((client) => client.userId === userId);
    if (byRole) {
      return byRole;
    }
  }
  if (target === 'PATIENT') {
    return clients.find((client) => client.isPatient) ?? null;
  }
  if (role && state?.roles[role]?.userId) {
    return null;
  }
  return null;
}

export function spotlightRoleStatus(
  state: IncidentState | null,
  role: RoleName,
): string {
  return translateRoleStatus(state?.roles?.[role]?.status);
}
