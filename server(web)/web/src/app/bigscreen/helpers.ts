import type { ClientInfo, DispatchMeta, IncidentState } from '@/shared/types';
import {
  hasGuideCompleted,
  hasPrimeStarted,
  hasRunnerDelivered,
  hasRunnerPicked,
  isAedAnalyzing,
  isShockDelivered,
  translatePhaseLabel,
} from '@/shared/domain';
import type { DemoFlowStep, DispatchStreamStep, LogEntry, LogEntryType } from './types';

export function classifyLogType(message: string): LogEntryType {
  const lower = message.toLowerCase();
  if (
    lower.includes('sos') ||
    lower.includes('alert') ||
    lower.includes('critical') ||
    lower.includes('shock') ||
    lower.includes('patient designated')
  ) {
    return 'alert';
  }
  if (
    lower.includes('archived') ||
    lower.includes('delivered') ||
    lower.includes('completed') ||
    lower.includes('handover') ||
    lower.includes('assigned') ||
    lower.includes('joined')
  ) {
    return 'success';
  }
  return 'info';
}

export function buildLogEntries(state: IncidentState | null): LogEntry[] {
  return (state?.logs ?? [])
    .map((log, index) => ({
      id: `${log.ts}-${index}`,
      time: new Date(log.ts).toLocaleTimeString('zh-CN', { hour12: false }),
      source: '服务端',
      message: log.msg,
      type: classifyLogType(log.msg),
    }))
    .reverse();
}

export function getDispatchStartTs(state?: IncidentState | null): number | null {
  if (!state) {
    return null;
  }
  const log = [...(state.logs ?? [])]
    .reverse()
    .find((entry) => entry.msg.includes('AI dispatching started') || entry.msg.includes('Patient designated'));
  return log?.ts ?? state.logs?.[0]?.ts ?? null;
}

export function buildDispatchStream(
  state: IncidentState | null,
  clients: ClientInfo[],
  dispatchMeta: DispatchMeta | null,
  nowMs: number,
): DispatchStreamStep[] {
  if (!state?.patientUserId) {
    return [];
  }
  const patient = clients.find((client) => client.userId === state.patientUserId);
  const candidates = clients.filter((client) => client.userId !== state.patientUserId);
  const primeName = clients.find((client) => client.userId === state.roles.PRIME.userId)?.displayName ?? '未分配';
  const runnerName = clients.find((client) => client.userId === state.roles.RUNNER.userId)?.displayName ?? '未分配';
  const guideName = clients.find((client) => client.userId === state.roles.GUIDE.userId)?.displayName ?? '未分配';
  const startTs = getDispatchStartTs(state);
  const delayMs = Math.max(1, (dispatchMeta?.dispatchDelaySec ?? 3) * 1000);
  const elapsedMs = startTs ? Math.max(0, nowMs - startTs) : delayMs;
  const stepCount = 6;
  const visibleCount =
    state.phase === 'DISPATCHING'
      ? Math.min(stepCount, Math.max(1, Math.ceil((elapsedMs / delayMs) * stepCount)))
      : stepCount;

  const steps = [
    {
      key: 'patient',
      title: '锁定患者画像',
      detail: patient
        ? `患者端：${patient.displayName}，画像为 ${patient.healthCondition} / ${patient.professionIdentity}`
        : '根据当前事件中的患者端信息构建画像',
    },
    {
      key: 'pool',
      title: '汇总在线终端',
      detail: `当前在线 ${clients.length} 台终端，可参与协同 ${candidates.length} 台`,
    },
    {
      key: 'prime',
      title: '筛选核心施救',
      detail: dispatchMeta?.selectionRules.PRIME ?? '优先医生和系统培训急救者',
    },
    {
      key: 'runner',
      title: '筛选 AED 保障',
      detail: dispatchMeta?.selectionRules.RUNNER ?? '优先体能好、跑得快、熟悉路线的人',
    },
    {
      key: 'guide',
      title: '筛选环境清障',
      detail: dispatchMeta?.selectionRules.GUIDE ?? '优先安保、物业和现场协调人员',
    },
    {
      key: 'result',
      title: '生成任务单',
      detail:
        state.phase === 'DISPATCHED'
          ? `已完成分配：核心施救 → ${primeName}；AED 保障 → ${runnerName}；环境清障 → ${guideName}`
          : '正在生成可执行任务单，并推送到各终端',
    },
  ];

  return steps.map((step, index) => ({
    ...step,
    visible: index < visibleCount,
    done: state.phase !== 'DISPATCHING' || index + 1 < visibleCount,
    active: state.phase === 'DISPATCHING' && index + 1 === visibleCount,
  }));
}

export function buildDemoFlowSteps(state: IncidentState | null): DemoFlowStep[] {
  const phase = state?.phase;
  const hasIncident = Boolean(state);
  const dispatchStarted = Boolean(
    state?.patientUserId ||
      phase === 'DISPATCHING' ||
      phase === 'DISPATCHED' ||
      phase === 'CPR' ||
      phase === 'AED_PICKED' ||
      phase === 'AED_DELIVERED' ||
      phase === 'AED_ANALYZING' ||
      phase === 'SHOCK_DELIVERED' ||
      phase === 'HANDOVER' ||
      phase === 'ARCHIVED',
  );
  const rolesAssigned = Boolean(
    state?.roles?.PRIME?.userId || state?.roles?.RUNNER?.userId || state?.roles?.GUIDE?.userId,
  );
  const rescueStarted = Boolean(hasPrimeStarted(state) || hasRunnerPicked(state) || hasGuideCompleted(state));
  const archived = phase === 'ARCHIVED';
  const handover = archived || phase === 'HANDOVER' || hasGuideCompleted(state);
  const definitions = [
    { title: '初始化场景', detail: '准备患者、救援者、AED 点位', complete: hasIncident, active: !hasIncident },
    { title: '患者 SOS', detail: '患者端触发告警并锁定位置', complete: dispatchStarted, active: hasIncident && !dispatchStarted },
    { title: '智能分派', detail: '生成核心施救、AED 保障、环境清障任务', complete: rolesAssigned, active: dispatchStarted && !rolesAssigned },
    { title: '现场处置', detail: 'CPR、AED 取送、清障接车', complete: rescueStarted || handover, active: rolesAssigned && !handover },
    { title: '交接归档', detail: '导出事件证据包', complete: archived, active: handover && !archived },
  ];
  return definitions;
}

export function describeClientMission(client: ClientInfo, state: IncidentState | null): string {
  if (!state?.patientUserId) {
    return client.patientCandidate ? '重点监测中，尚未触发事件' : '在线待命，等待事件触发';
  }
  if (client.isPatient) {
    if (state.phase === 'DISPATCHING') {
      return '患者端已发出告警，系统正在广播协同通知并进行智能分派';
    }
    if (state.phase === 'HANDOVER') {
      return '救护车已完成现场接管，进入交接阶段';
    }
    return '保持当前位置，等待周边协同成员与救护车到场';
  }
  switch (client.assignedRole) {
    case 'PRIME':
      if (isShockDelivered(state)) {
        return '已完成一次 AED 除颤，当前应继续 CPR 并观察患者反应';
      }
      if (isAedAnalyzing(state)) {
        return 'AED 正在分析心律，等待设备给出是否建议电击';
      }
      if (hasRunnerDelivered(state)) {
        return 'AED 已送达，核心施救者正在贴附电极片并准备分析';
      }
      return hasPrimeStarted(state) ? '已在患者旁持续执行 CPR' : '立即前往患者位置，确认后开始 CPR';
    case 'RUNNER':
      if (hasRunnerDelivered(state)) {
        return 'AED 已送达现场，保持通信畅通';
      }
      if (hasRunnerPicked(state)) {
        return '已取到 AED，正在回送患者位置';
      }
      return '前往最近 AED 点位并尽快回送';
    case 'GUIDE':
      return hasGuideCompleted(state) ? '已引导救护车到场并完成交接' : '正在疏通通道并引导救护车';
    default:
      return state.phase === 'DISPATCHING' ? '正在等待智能分派结果' : '本轮未分配任务，保持待命';
  }
}

export function formatElapsed(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

export function formatPhaseLabel(phase?: string | null): string {
  return translatePhaseLabel(phase);
}
