import type { HealthSignalSummary, IncidentState, RoleName } from './types';
import {
  hasPrimeStarted,
  hasRunnerDelivered,
  hasRunnerPicked,
  isAedAnalyzing,
  isRoleJoined,
  isShockDelivered,
  translateRoleLabel,
} from './domain';

export interface RoleAction {
  title: string;
  buttonLabel: string;
  action: string;
  disabled?: boolean;
  hint?: string;
}

export interface RescueProgressItem {
  role: RoleName;
  label: string;
  state: 'pending' | 'onway' | 'arrived';
}

export function roleAction(role: RoleName, state: IncidentState | null): RoleAction {
  if (!state) {
    return { title: '等待任务', buttonLabel: '等待', action: 'WAIT', disabled: true };
  }
  const roles = state.roles;
  if (state.phase === 'ARCHIVED') {
    return { title: '已完成归档', buttonLabel: '流程已结束', action: 'WAIT', disabled: true };
  }
  switch (role) {
    case 'PRIME': {
      const status = roles.PRIME?.status;
      if (!isRoleJoined(status)) {
        return { title: '核心施救待响应', buttonLabel: '确认响应', action: 'JOIN', hint: '确认接单后立即前往患者位置' };
      }
      if (status === 'ASSIGNED' || status === 'JOINED') {
        return { title: '到达患者并准备 CPR', buttonLabel: '确认开始 CPR', action: 'CPR_STARTED', hint: '打开按压节拍与 30:2 提示' };
      }
      if (hasRunnerDelivered(state) && !isAedAnalyzing(state) && !isShockDelivered(state)) {
        return { title: '准备 AED 分析', buttonLabel: '确认启动 AED 分析', action: 'AED_ANALYSIS_STARTED', hint: '确认电极片贴附后操作' };
      }
      if (isAedAnalyzing(state)) {
        return { title: '等待 AED 电击建议', buttonLabel: '记录一次除颤', action: 'AED_SHOCK_DELIVERED', hint: '仅在 AED 建议电击后记录' };
      }
      if (isShockDelivered(state)) {
        return { title: '继续 CPR 并准备二轮分析', buttonLabel: '确认二轮 AED 分析', action: 'AED_ANALYSIS_STARTED', hint: '继续 CPR 后可再次分析' };
      }
      return { title: '等待 AED 到场', buttonLabel: '等待 AED', action: 'WAIT', disabled: true, hint: 'AED 保障送达后才能进入分析' };
    }
    case 'RUNNER': {
      const status = roles.RUNNER?.status;
      if (!isRoleJoined(status)) {
        return { title: 'AED 保障待响应', buttonLabel: '确认响应', action: 'JOIN', hint: '确认接单后前往最近 AED 点位' };
      }
      if (!hasRunnerPicked(state)) {
        return { title: '前往 AED 点位', buttonLabel: '确认已取到 AED', action: 'AED_PICKED', hint: '到达 AED 箱并取出设备后点击' };
      }
      if (!hasRunnerDelivered(state)) {
        return { title: '送回患者位置', buttonLabel: '确认 AED 已送达', action: 'AED_DELIVERED', hint: '回到患者身边并交给施救者后点击' };
      }
      return { title: 'AED 已完成送达', buttonLabel: '保持待命', action: 'WAIT', disabled: true, hint: '保持通信，协助核心施救' };
    }
    case 'GUIDE': {
      const status = roles.GUIDE?.status;
      if (!isRoleJoined(status)) {
        return { title: '清障接驳待响应', buttonLabel: '确认响应', action: 'JOIN', hint: '确认接单后疏通通道' };
      }
      if (state.phase === 'HANDOVER') {
        return { title: '现场交接中', buttonLabel: '确认完成交接归档', action: 'HANDOVER_COMPLETED', hint: '急救人员接管后归档' };
      }
      return { title: '等待救护车接应', buttonLabel: '确认救护车已到场', action: 'AMBULANCE_ARRIVED', hint: '若状态已是到场，请再次确认同步交接' };
    }
  }
}

export function primeNextStep(state: IncidentState | null): { title: string; body: string; tone: 'wait' | 'ready' | 'danger' } | null {
  if (!state || state.roles.PRIME?.status !== 'CPR_STARTED') return null;
  if (isAedAnalyzing(state)) {
    return { title: '停止接触患者', body: '等待 AED 分析结果，仅在设备明确建议时记录一次除颤。', tone: 'danger' };
  }
  if (isShockDelivered(state)) {
    return { title: '立即恢复 CPR', body: '除颤完成后回到 30:2 循环，约 2 分钟后再进入下一轮分析。', tone: 'ready' };
  }
  if (hasRunnerDelivered(state)) {
    return { title: '贴附电极片', body: '连接 AED，确认周围安全后启动心律分析。', tone: 'ready' };
  }
  if (hasRunnerPicked(state)) {
    return { title: 'AED 正在回送', body: '继续胸外按压，AED 到场后短暂停止并贴附电极片。', tone: 'wait' };
  }
  if (hasPrimeStarted(state)) {
    return { title: '等待 AED 到场', body: '保持 100-120 次/分钟按压节律，按 30:2 循环持续复苏。', tone: 'wait' };
  }
  return { title: '先启动 CPR', body: '确认患者无意识且无正常呼吸后，立即开始胸外按压。', tone: 'danger' };
}

export function rescueProgress(state: IncidentState | null): RescueProgressItem[] {
  const items: RescueProgressItem[] = [
    { role: 'PRIME', label: '急救', state: 'pending' },
    { role: 'RUNNER', label: 'AED', state: 'pending' },
    { role: 'GUIDE', label: '接应', state: 'pending' },
  ];
  if (!state) return items;
  for (const item of items) {
    const status = state.roles[item.role]?.status;
    const assigned = Boolean(state.roles[item.role]?.userId);
    const arrived =
      status === 'CPR_STARTED' ||
      status === 'AED_DELIVERED' ||
      status === 'AED_ANALYZING' ||
      status === 'AED_SHOCK_DELIVERED' ||
      status === 'AMBULANCE_ARRIVED' ||
      status === 'HANDOVER_COMPLETED';
    if (arrived) item.state = 'arrived';
    else if (assigned) item.state = 'onway';
  }
  return items;
}

export function healthStatItems(summary?: HealthSignalSummary | null): Array<{ label: string; value: string; tone?: 'danger' | 'ok' }> {
  const hr = summary?.heartRateBpm;
  const spo2 = summary?.bloodOxygenPercent;
  const pressure = summary?.pressureScore;
  return [
    {
      label: '心率',
      value: hr != null ? `${hr}` : '--',
      tone: hr != null ? (hr >= 110 || hr <= 60 ? 'danger' : hr <= 80 ? 'ok' : undefined) : undefined,
    },
    {
      label: '血氧',
      value: spo2 != null ? `${Math.round(spo2)}%` : '--',
      tone: spo2 != null ? (spo2 < 95 ? 'danger' : spo2 >= 97 ? 'ok' : undefined) : undefined,
    },
    {
      label: '压力',
      value: pressure != null ? `${pressure}` : '--',
      tone: pressure != null ? (pressure >= 70 ? 'danger' : pressure <= 30 ? 'ok' : undefined) : undefined,
    },
  ];
}

export function mockHealthSignalsFor(user: { userId: string; displayName: string; professionIdentity: string }, persona?: string): HealthSignalSummary {
  if (persona === 'patient') {
    return {
      source: 'mock',
      authorizationStatus: 'sample',
      heartRateBpm: 118,
      bloodOxygenPercent: 92.0,
      pressureScore: 82,
      activityLevel: 'low',
      sleepQuality: 'poor',
      riskTags: ['tachycardia', 'low_spo2'],
      updatedTs: Date.now(),
      note: '演示健康摘要：患者端风险样例',
    };
  }
  if (persona === 'runner') {
    return {
      source: 'mock',
      authorizationStatus: 'sample',
      heartRateBpm: 84,
      bloodOxygenPercent: 99.0,
      pressureScore: 24,
      activityLevel: 'high',
      sleepQuality: 'good',
      riskTags: [],
      updatedTs: Date.now(),
      note: '演示健康摘要：AED 保障端体能样例',
    };
  }
  return {
    source: 'mock',
    authorizationStatus: 'sample',
    heartRateBpm: user.professionIdentity.includes('医生') ? 76 : 80,
    bloodOxygenPercent: 98.0,
    pressureScore: 35,
    activityLevel: 'normal',
    sleepQuality: 'good',
    riskTags: [],
    updatedTs: Date.now(),
    note: '演示健康摘要：移动浏览器终端',
  };
}

export function formatElapsedLabel(startTs: number | null, now: number): string {
  if (!startTs) return '未开始';
  const totalSec = Math.max(0, Math.floor((now - startTs) / 1000));
  const d = Math.floor(totalSec / 86400);
  const h = Math.floor((totalSec % 86400) / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;
  if (d > 0) return `${d}天${h}小时`;
  if (h > 0) return `${h}时${m}分`;
  if (m > 0) return `${m}分${s.toString().padStart(2, '0')}秒`;
  return `${s}秒`;
}

export function shortId(value: string | null | undefined): string {
  if (!value) return '未记录';
  return value.length > 8 ? value.slice(0, 8) : value;
}

export function isIncidentReadyForResponderTask(state: IncidentState | null): boolean {
  if (!state) return false;
  return state.phase !== 'CREATED' && state.phase !== 'DISPATCHING';
}

export function demoPersonaInfo(): Array<{
  key: 'patient' | 'prime' | 'runner' | 'guide';
  label: string;
  title: string;
  description: string;
  locationLabel: string;
}> {
  return [
    { key: 'patient', label: '患者端', title: '患者端', description: '触发 SOS，观察系统分派', locationLabel: '教学楼 A 座 2 层走廊' },
    { key: 'prime', label: '核心施救', title: '核心施救端', description: '接单、CPR、AED 分析', locationLabel: '教学楼 A 座 1 层大厅' },
    { key: 'runner', label: 'AED 保障', title: 'AED 保障端', description: '取 AED 并送达患者', locationLabel: '操场入口' },
    { key: 'guide', label: '环境清障', title: '清障接驳端', description: '疏通通道，接引救护车', locationLabel: '校门入口' },
  ];
}

export function demoLocationLabel(persona: string): string {
  return demoPersonaInfo().find((item) => item.key === persona)?.locationLabel ?? '未知位置';
}

export function roleLabelFor(role: RoleName | null | undefined): string {
  if (!role) return '待命终端';
  return translateRoleLabel(role);
}
