import type { GeoPoint, HealthSignalSummary, IncidentState, RoleName } from './types';

export const roleNames: RoleName[] = ['PRIME', 'RUNNER', 'GUIDE'];

const phaseRank: Record<string, number> = {
  CREATED: 0,
  DISPATCHING: 1,
  DISPATCHED: 2,
  CPR: 3,
  AED_PICKED: 4,
  AED_DELIVERED: 5,
  AED_ANALYZING: 6,
  SHOCK_DELIVERED: 7,
  HANDOVER: 8,
  ARCHIVED: 9,
};

export function getStateLatestTs(state?: IncidentState | null): number {
  return Math.max(0, ...(state?.logs ?? []).map((entry) => entry.ts));
}

export function hasAssignedRoles(state?: IncidentState | null): boolean {
  return roleNames.some((role) => Boolean(state?.roles?.[role]?.userId));
}

function getDispatchRationaleCount(state?: IncidentState | null): number {
  return Object.keys(state?.dispatchRationale ?? {}).length;
}

function getPhaseRank(phase?: string | null): number {
  return phase ? phaseRank[phase] ?? 2 : -1;
}

function isIncidentResetState(state: IncidentState): boolean {
  return state.logs.length === 1 && state.logs[0]?.msg === 'Incident reset';
}

export function mergeIncidentState(current: IncidentState | null, next: IncidentState): IncidentState {
  if (!current || current.incidentId !== next.incidentId) {
    return next;
  }

  const currentTs = getStateLatestTs(current);
  const nextTs = getStateLatestTs(next);
  if (nextTs < currentTs) {
    return current;
  }

  const currentRationaleCount = getDispatchRationaleCount(current);
  const nextRationaleCount = getDispatchRationaleCount(next);
  const currentAssigned = hasAssignedRoles(current);
  const nextAssigned = hasAssignedRoles(next);
  const nextIsNewReset = isIncidentResetState(next) && nextTs >= currentTs;

  if (!nextIsNewReset && nextTs === currentTs) {
    if (currentRationaleCount > 0 && nextRationaleCount === 0) {
      return current;
    }
    if (currentAssigned && !nextAssigned && getPhaseRank(next.phase) <= getPhaseRank(current.phase)) {
      return current;
    }
  }

  if (!nextIsNewReset && currentRationaleCount > 0 && nextRationaleCount === 0 && getPhaseRank(next.phase) >= getPhaseRank(current.phase)) {
    return {
      ...next,
      dispatchRationale: current.dispatchRationale,
    };
  }

  return next;
}

export function isRoleJoined(status?: string | null): boolean {
  if (!status) {
    return false;
  }
  return new Set([
    'ASSIGNED',
    'JOINED',
    'AED_PICKED',
    'AED_DELIVERED',
    'CPR_STARTED',
    'AMBULANCE_ARRIVED',
    'CPR',
  ]).has(status);
}

export function hasPrimeStarted(state?: IncidentState | null): boolean {
  return state?.roles?.PRIME?.status === 'CPR_STARTED';
}

export function hasRunnerPicked(state?: IncidentState | null): boolean {
  const status = state?.roles?.RUNNER?.status;
  return status === 'AED_PICKED' || status === 'AED_DELIVERED';
}

export function hasRunnerDelivered(state?: IncidentState | null): boolean {
  return state?.roles?.RUNNER?.status === 'AED_DELIVERED';
}

export function hasGuideCompleted(state?: IncidentState | null): boolean {
  return (
    state?.roles?.GUIDE?.status === 'AMBULANCE_ARRIVED' ||
    state?.roles?.GUIDE?.status === 'HANDOVER_COMPLETED' ||
    state?.phase === 'HANDOVER' ||
    state?.phase === 'ARCHIVED'
  );
}

export function isAedAnalyzing(state?: IncidentState | null): boolean {
  return state?.roles?.PRIME?.status === 'AED_ANALYZING' || state?.phase === 'AED_ANALYZING';
}

export function isShockDelivered(state?: IncidentState | null): boolean {
  return state?.roles?.PRIME?.status === 'AED_SHOCK_DELIVERED' || state?.phase === 'SHOCK_DELIVERED';
}

export function translatePhaseLabel(phase?: string | null): string {
  switch (phase) {
    case 'CREATED':
      return '监测中';
    case 'DISPATCHING':
      return '智能分派中';
    case 'DISPATCHED':
      return '任务已下发';
    case 'CPR':
      return 'CPR 进行中';
    case 'AED_PICKED':
      return 'AED 已取到';
    case 'AED_DELIVERED':
      return 'AED 已送达';
    case 'AED_ANALYZING':
      return 'AED 分析中';
    case 'SHOCK_DELIVERED':
      return '已完成除颤';
    case 'HANDOVER':
      return '完成交接';
    case 'ARCHIVED':
      return '已归档';
    default:
      return phase ?? '未开始';
  }
}

export function translateRoleLabel(role?: string | null): string {
  switch (role) {
    case 'PRIME':
      return '核心施救';
    case 'RUNNER':
      return 'AED 保障';
    case 'GUIDE':
      return '环境清障';
    default:
      return '未分配';
  }
}

export function translateRoleStatus(status?: string | null): string {
  switch (status) {
    case '':
      return '待命';
    case 'ASSIGNED':
      return '已分配';
    case 'JOINED':
      return '已响应';
    case 'CPR_STARTED':
      return '已开始 CPR';
    case 'AED_PICKED':
      return '已取到 AED';
    case 'AED_DELIVERED':
      return '已送达 AED';
    case 'AED_ANALYZING':
      return 'AED 分析中';
    case 'AED_SHOCK_DELIVERED':
      return '已完成一次除颤';
    case 'AMBULANCE_ARRIVED':
      return '救护车已到场';
    case 'HANDOVER_COMPLETED':
      return '交接已完成';
    case 'CPR':
      return 'CPR 进行中';
    default:
      return status ?? '待命';
  }
}

export function formatTimeLabel(ts?: number | null): string {
  if (!ts) {
    return '--:--:--';
  }
  return new Date(ts).toLocaleTimeString('zh-CN', { hour12: false });
}

export function formatDistanceLabel(value?: number | null): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return '--';
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)} 公里`;
  }
  return `${Math.round(value)} 米`;
}

function formatFloorLabel(floor?: string | null): string {
  if (!floor) {
    return '';
  }
  const normalized = floor.trim().toUpperCase();
  const match = normalized.match(/^(\d+)F$/);
  if (!match) {
    return floor;
  }
  const labels: Record<string, string> = {
    '1': '一层',
    '2': '二层',
    '3': '三层',
    '4': '四层',
    '5': '五层',
    '6': '六层',
    '7': '七层',
    '8': '八层',
    '9': '九层',
  };
  return labels[match[1]] ?? `${match[1]}层`;
}

export function formatLocationLabel(location?: GeoPoint | null): string {
  if (!location) {
    return '未上报位置';
  }
  const floorLabel = formatFloorLabel(location.floor);
  const floor = floorLabel ? ` · ${floorLabel}` : '';
  const accuracy = location.accuracyMeters ? ` · 精度 ${formatDistanceLabel(location.accuracyMeters)}` : '';
  return `${location.label ?? '演示点位'}${floor}${accuracy}`;
}

export function translateHealthSource(source?: string | null): string {
  switch (source) {
    case 'oppo':
    case 'oppo_health':
      return 'OPPO 健康';
    case 'mock':
      return '演示健康摘要';
    case 'manual':
      return '手动录入';
    case 'unavailable':
      return '健康数据未接入';
    default:
      return source ?? '健康数据未接入';
  }
}

export function translateHealthAuthorization(status?: string | null): string {
  switch (status) {
    case 'authorized':
      return '已授权';
    case 'sample':
      return '样例接入';
    case 'denied':
      return '未授权';
    case 'not_connected':
    case undefined:
    case null:
      return '未接入';
    default:
      return status;
  }
}

export function translateHealthRiskTag(tag: string): string {
  switch (tag) {
    case 'tachycardia':
      return '心率偏快';
    case 'bradycardia':
      return '心率偏慢';
    case 'low_spo2':
      return '血氧偏低';
    case 'high_pressure':
      return '压力偏高';
    case 'limited_mobility':
      return '行动能力受限';
    default:
      return tag;
  }
}

export function formatHealthRiskTags(tags?: string[] | null): string {
  return (tags ?? []).map(translateHealthRiskTag).join('、');
}

export function formatHealthSignalSummary(summary?: HealthSignalSummary | null): string {
  if (!summary) {
    return '健康数据未接入';
  }
  const parts = [
    translateHealthAuthorization(summary.authorizationStatus),
    summary.heartRateBpm ? `心率 ${summary.heartRateBpm} bpm` : null,
    summary.bloodOxygenPercent ? `血氧 ${summary.bloodOxygenPercent}%` : null,
    summary.pressureScore !== undefined && summary.pressureScore !== null ? `压力 ${summary.pressureScore}` : null,
  ].filter(Boolean);
  if (!parts.length) {
    return translateHealthSource(summary.source);
  }
  return `${translateHealthSource(summary.source)} · ${parts.join(' · ')}`;
}

export function findUserRole(state: IncidentState | null, userId?: string | null): RoleName | null {
  if (!state || !userId) {
    return null;
  }
  for (const role of ['PRIME', 'RUNNER', 'GUIDE'] as RoleName[]) {
    if (state.roles[role]?.userId === userId) {
      return role;
    }
  }
  return null;
}

export function getResuscitationGuidance(elapsedSec: number) {
  const cycleTotal = 120;
  const cycleRemaining = cycleTotal - (elapsedSec % cycleTotal);
  const blockElapsed = elapsedSec % 20;
  const breathing = blockElapsed >= 16;
  const blockRemaining = breathing ? 20 - blockElapsed : 16 - blockElapsed;
  return {
    cycleRemaining: Math.max(0, cycleRemaining),
    stageRemaining: Math.max(0, blockRemaining),
    stageTitle: breathing ? '人工呼吸阶段' : '胸外按压阶段',
    stageAction: breathing ? '2 次人工呼吸' : '30 次胸外按压',
    stageBody: breathing
      ? '保持气道开放，完成 2 次人工呼吸后立刻恢复胸外按压。'
      : '保持 100-120 次/分钟按压节律，深度 5-6 厘米，尽量减少中断。',
  };
}
