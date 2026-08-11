import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  Activity,
  BadgeInfo,
  CheckCircle2,
  ChevronDown,
  Clock,
  Copy,
  ExternalLink,
  HeartPulse,
  LogOut,
  MapPin,
  Moon,
  Navigation,
  Radio,
  RefreshCw,
  Shield,
  Siren,
  Sun,
  UserRound,
  Zap,
} from 'lucide-react';
import {
  autoJoinCurrent,
  downloadExperimentPackage,
  fetchAedSites,
  fetchClients,
  fetchCurrentIncident,
  fetchIncident,
  fetchMe,
  joinIncident,
  loginAccount,
  logindemoPersona,
  logoutAccount,
  openIncidentSocket,
  patientSosCancel,
  patientSosStart,
  postIncidentAction,
  registerAccount,
  registerClient,
  updateClientHealth,
  updateClientLocation,
  getStoreddemoAdminToken,
  type RegisterForm,
} from '@/shared/api';
import {
  findUserRole,
  formatDistanceLabel,
  formatHealthRiskTags,
  formatHealthSignalSummary,
  formatLocationLabel,
  formatTimeLabel,
  getResuscitationGuidance,
  hasPrimeStarted,
  hasRunnerDelivered,
  hasRunnerPicked,
  isAedAnalyzing,
  isRoleJoined,
  isShockDelivered,
  mergeIncidentState,
  translatePhaseLabel,
  translateHealthSource,
  translateRoleLabel,
  translateRoleStatus,
} from '@/shared/domain';
import type { AedSite, AuthUser, ClientInfo, GeoPoint, HealthSignalSummary, IncidentState, RoleName } from '@/shared/types';
import aedRouteUrl from './assets/aed-route.svg';
import emergencySceneUrl from './assets/emergency-scene.svg';
import responseRolesUrl from './assets/response-roles.svg';
import './mobile.css';

type AuthMode = 'login' | 'register';
type SyncStatus = 'idle' | 'connecting' | 'live' | 'reconnecting' | 'offline';
type MobileView = 'home' | 'mission' | 'scene' | 'logs';
type MobileTheme = 'light' | 'dark';
type Notice = { kind: 'ok' | 'error' | 'info'; text: string } | null;
type demoPersona = 'patient' | 'prime' | 'runner' | 'guide';

interface StoredSession {
  token: string;
  user: AuthUser;
  tokenExpiresAt?: number | null;
  demoPersona?: demoPersona;
}

const SESSION_KEY = 'lra_mobile_session';
const TAB_SESSION_KEY = 'lra_mobile_tab_session';
const INCIDENT_KEY = 'lra_mobile_incident_id';
const LOCATION_KEY = 'lra_mobile_location';
const MOBILE_THEME_KEY = 'lra_mobile_theme';
const demo_ADMIN_TOKEN_KEY = 'lra_demo_admin_token';

const demoPersonas: Array<{
  key: demoPersona;
  label: string;
  title: string;
  description: string;
  location: GeoPoint;
}> = [
  {
    key: 'patient',
    label: '患者端',
    title: '患者端',
    description: '触发 SOS，观察系统分派',
    location: {
      latitude: 39.916156,
      longitude: 116.465571,
      accuracyMeters: 25,
      label: '交通和苑 8 号楼前广场',
      floor: '2F',
      source: 'mobile-demo',
    },
  },
  {
    key: 'prime',
    label: '核心施救',
    title: '核心施救端',
    description: '接单、CPR、AED 分析',
    location: {
      latitude: 39.916030,
      longitude: 116.466039,
      accuracyMeters: 18,
      label: '交通和苑中心花园',
      floor: '1F',
      source: 'mobile-demo',
    },
  },
  {
    key: 'runner',
    label: 'AED 保障',
    title: 'AED 保障端',
    description: '取 AED 并送达患者',
    location: {
      latitude: 39.915868,
      longitude: 116.466566,
      accuracyMeters: 18,
      label: '交通和苑物业用房',
      floor: '1F',
      source: 'mobile-demo',
    },
  },
  {
    key: 'guide',
    label: '清障接驳',
    title: '清障接驳端',
    description: '疏通通道，接引救护车',
    location: {
      latitude: 39.915509,
      longitude: 116.464892,
      accuracyMeters: 20,
      label: '交通和苑北门出入口',
      floor: '1F',
      source: 'mobile-demo',
    },
  },
];

const defaultLocation: GeoPoint = {
  latitude: 39.915976,
  longitude: 116.465922,
  accuracyMeters: 25,
  label: '交通和苑小区现场',
  floor: '二层',
  source: 'mobile-demo',
};

function readdemoPersonaFromUrl(): demoPersona | null {
  const raw = new URLSearchParams(window.location.search).get('demo')?.trim().toLowerCase();
  if (raw === 'patient' || raw === 'prime' || raw === 'runner' || raw === 'guide') {
    return raw;
  }
  return null;
}

function readIncidentIdFromUrl(): string {
  return new URLSearchParams(window.location.search).get('incidentId')?.trim() ?? '';
}

function readInitialIncidentId(urlIncidentId: string, demoPersona: demoPersona | null): string {
  if (urlIncidentId) {
    return urlIncidentId;
  }
  if (demoPersona) {
    return '';
  }
  return window.localStorage.getItem(INCIDENT_KEY) ?? '';
}

function readdemoSlotFromUrl(): string {
  const raw = new URLSearchParams(window.location.search).get('slot')?.trim().toLowerCase() || 'default';
  return raw.replace(/[^a-z0-9_-]/g, '').slice(0, 24) || 'default';
}

function tabSessionKey(): string {
  return `${TAB_SESSION_KEY}_${readdemoSlotFromUrl()}`;
}

function tabLocationKey(): string {
  return `${LOCATION_KEY}_${readdemoSlotFromUrl()}`;
}

async function copyTextToClipboard(text: string): Promise<boolean> {
  if (typeof window === 'undefined' || typeof document === 'undefined') {
    return false;
  }
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {
    // Continue with the textarea fallback below.
  }
  const textarea = document.createElement('textarea');
  textarea.value = text;
  textarea.setAttribute('readonly', 'true');
  textarea.style.position = 'fixed';
  textarea.style.left = '-9999px';
  textarea.style.top = '0';
  document.body.appendChild(textarea);
  textarea.select();
  let copied = false;
  try {
    copied = document.execCommand('copy');
  } finally {
    textarea.remove();
  }
  return copied;
}

function demoLocationFor(persona?: demoPersona | null): GeoPoint {
  return demoPersonas.find((item) => item.key === persona)?.location ?? defaultLocation;
}

function mockHealthSignalsFor(user: AuthUser, persona?: demoPersona): HealthSignalSummary {
  const text = `${user.healthCondition} ${user.professionIdentity} ${user.profileBio} ${persona ?? ''}`;
  const now = Date.now();
  if (text.includes('心脏') || persona === 'patient') {
    return {
      source: 'mock',
      authorizationStatus: 'sample',
      provider: 'OPPO_HEALTH',
      heartRateBpm: 118,
      bloodOxygenPercent: 92,
      pressureScore: 82,
      activityLevel: 'low',
      sleepQuality: 'poor',
      riskTags: ['tachycardia', 'low_spo2', 'high_pressure'],
      updatedTs: now,
      note: '演示健康摘要：患者端风险样例',
    };
  }
  if (text.includes('体育') || text.includes('跑') || persona === 'runner') {
    return {
      source: 'mock',
      authorizationStatus: 'sample',
      provider: 'OPPO_HEALTH',
      heartRateBpm: 84,
      bloodOxygenPercent: 99,
      pressureScore: 28,
      activityLevel: 'high',
      sleepQuality: 'good',
      riskTags: [],
      updatedTs: now,
      note: '演示健康摘要：AED 保障端体能样例',
    };
  }
  return {
    source: 'mock',
    authorizationStatus: 'sample',
    provider: 'OPPO_HEALTH',
    heartRateBpm: text.includes('医生') ? 76 : 80,
    bloodOxygenPercent: 98,
    pressureScore: text.includes('安保') ? 44 : 35,
    activityLevel: 'normal',
    sleepQuality: 'good',
    riskTags: [],
    updatedTs: now,
    note: '演示健康摘要：移动浏览器端',
  };
}

const profilePresets = [
  {
    label: '患者端',
    values: {
      organization: '演示社区',
      healthCondition: '存在心脏骤停风险',
      professionIdentity: '患者侧',
      profileBio: '冠心病病史，需要重点监护，可用于患者端协同流程。',
    },
  },
  {
    label: '医生',
    values: {
      organization: '市医院急救科',
      healthCondition: '身体状态一般',
      professionIdentity: '医生 / 专业急救人员',
      profileBio: '熟悉 CPR 和 AED，可承担核心施救任务。',
    },
  },
  {
    label: 'AED 保障',
    values: {
      organization: '朝阳大悦城物业',
      healthCondition: '身体素质良好',
      professionIdentity: '有一定急救常识',
      profileBio: '商场物业员工，熟悉各楼层动线，可快速取送 AED。',
    },
  },
  {
    label: '清障接驳',
    values: {
      organization: '商场安保部',
      healthCondition: '身体状态一般',
      professionIdentity: '安保 / 物业 / 场地协调人员',
      profileBio: '熟悉商场出入口、电梯与救护车通道。',
    },
  },
];

function readStoredSession(): StoredSession | null {
  try {
    const raw = window.sessionStorage.getItem(tabSessionKey()) || window.sessionStorage.getItem(TAB_SESSION_KEY) || window.localStorage.getItem(SESSION_KEY);
    return raw ? (JSON.parse(raw) as StoredSession) : null;
  } catch {
    return null;
  }
}

function readStoredLocation(): GeoPoint {
  try {
    const raw = window.sessionStorage.getItem(tabLocationKey()) || window.sessionStorage.getItem(LOCATION_KEY) || window.localStorage.getItem(LOCATION_KEY);
    return raw ? { ...defaultLocation, ...(JSON.parse(raw) as GeoPoint) } : defaultLocation;
  } catch {
    return defaultLocation;
  }
}

function readStoredTheme(): MobileTheme {
  try {
    const stored = window.localStorage.getItem(MOBILE_THEME_KEY);
    if (stored === 'light' || stored === 'dark') {
      return stored;
    }
    return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  } catch {
    return 'light';
  }
}

function saveSession(session: StoredSession | null): void {
  if (!session) {
    window.sessionStorage.removeItem(tabSessionKey());
    window.sessionStorage.removeItem(TAB_SESSION_KEY);
    window.localStorage.removeItem(SESSION_KEY);
    return;
  }
  const storage = session.demoPersona ? window.sessionStorage : window.localStorage;
  const key = session.demoPersona ? tabSessionKey() : SESSION_KEY;
  storage.setItem(key, JSON.stringify(session));
  if (session.demoPersona) {
    window.localStorage.removeItem(SESSION_KEY);
  }
}

type RoleAction = {
  title: string;
  buttonLabel: string;
  action: string;
  disabled?: boolean;
  hint: string;
};

function roleAction(role: RoleName, state: IncidentState | null): RoleAction {
  if (state?.phase === 'ARCHIVED') {
    return { title: '已完成归档', buttonLabel: '流程已结束', action: 'WAIT', disabled: true, hint: '本轮协同流程已结束' };
  }
  if (role === 'PRIME') {
    if (!state || !isRoleJoined(state.roles.PRIME?.status)) {
      return { title: '核心施救待响应', buttonLabel: '确认响应', action: 'JOIN', hint: '确认接单后立即前往患者位置' };
    }
    if (!state.roles.PRIME?.status || state.roles.PRIME.status === 'ASSIGNED' || state.roles.PRIME.status === 'JOINED') {
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
  if (role === 'RUNNER') {
    if (!state || !isRoleJoined(state.roles.RUNNER?.status)) {
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
  if (!state || !isRoleJoined(state.roles.GUIDE?.status)) {
    return { title: '清障接驳待响应', buttonLabel: '确认响应', action: 'JOIN', hint: '确认接单后疏通通道' };
  }
  if (state.phase === 'HANDOVER') {
    return { title: '现场交接中', buttonLabel: '确认完成交接归档', action: 'HANDOVER_COMPLETED', hint: '急救人员接管后归档' };
  }
  if (state.phase !== 'ARCHIVED') {
    return {
      title: '等待救护车接应',
      buttonLabel: '确认救护车已到场',
      action: 'AMBULANCE_ARRIVED',
      hint: state.roles.GUIDE?.status === 'AMBULANCE_ARRIVED'
        ? '正在同步交接状态，请再次确认救护车到场'
        : '救护车到场是外部事实，可随时确认并进入现场交接',
    };
  }
  return { title: '已完成归档', buttonLabel: '流程已结束', action: 'WAIT', disabled: true, hint: '本轮协同流程已结束' };
}

function primeNextStep(state: IncidentState | null): { title: string; body: string; tone: 'wait' | 'ready' | 'danger' } | null {
  if (!state) {
    return null;
  }
  if (isAedAnalyzing(state)) {
    return {
      title: '停止接触患者',
      body: '等待 AED 分析结果，仅在设备明确建议时记录一次除颤。',
      tone: 'danger',
    };
  }
  if (isShockDelivered(state)) {
    return {
      title: '立即恢复 CPR',
      body: '除颤完成后回到 30:2 基础复苏循环，约 2 分钟后再进入下一轮 AED 分析。',
      tone: 'ready',
    };
  }
  if (hasRunnerDelivered(state)) {
    return {
      title: '贴附电极片',
      body: '连接 AED，确认周围安全后启动心律分析。',
      tone: 'ready',
    };
  }
  if (hasRunnerPicked(state)) {
    return {
      title: 'AED 正在回送',
      body: '继续胸外按压，AED 到场后短暂停止并贴附电极片。',
      tone: 'wait',
    };
  }
  if (hasPrimeStarted(state)) {
    return {
      title: '等待 AED 到场',
      body: '保持 100-120 次/分钟按压节律，按 30:2 循环持续复苏。',
      tone: 'wait',
    };
  }
  return {
    title: '先启动 CPR',
    body: '确认患者无意识且无正常呼吸后，立即开始胸外按压。',
    tone: 'danger',
  };
}

function getLatestLogTs(state: IncidentState | null, keyword: string): number | null {
  const normalizedKeyword = keyword.toLowerCase();
  for (let index = (state?.logs?.length ?? 0) - 1; index >= 0; index -= 1) {
    const entry = state?.logs[index];
    if (entry?.msg.toLowerCase().includes(normalizedKeyword)) {
      return entry.ts;
    }
  }
  return null;
}

function selectPrimaryAed(state: IncidentState | null, aedSites: AedSite[], role: RoleName | null): AedSite | null {
  const sites = state?.aedSites?.length ? state.aedSites : aedSites;
  if (!sites.length) {
    return null;
  }
  const targetId = role ? state?.dispatchRationale?.[role]?.nearestAedSiteId : null;
  return sites.find((site) => site.siteId === targetId) ?? sites[0];
}

function isIncidentReadyForResponderTask(state: IncidentState | null): boolean {
  return Boolean(state && state.phase !== 'CREATED' && state.phase !== 'DISPATCHING');
}

function shortId(value?: string | null): string {
  if (!value) {
    return '未记录';
  }
  return value.length > 8 ? value.slice(0, 8) : value;
}

function translateDispatchSource(source?: string): string {
  switch (source) {
    case 'fallback':
      return '规则兜底';
    case 'local_model':
      return '本地模型';
    case 'siliconflow':
      return '云端模型';
    default:
      return source && !/[A-Za-z]/.test(source) ? source : '系统';
  }
}

function formatElapsedLabel(startTs: number | null | undefined, now: number): string {
  if (!startTs) {
    return '未开始';
  }
  const totalSec = Math.max(0, Math.floor((now - startTs) / 1000));
  const days = Math.floor(totalSec / 86400);
  if (days > 0) {
    const hours = Math.floor((totalSec % 86400) / 3600);
    return `${days}d ${hours}h`;
  }
  const hours = Math.floor(totalSec / 3600);
  if (hours > 0) {
    const minutes = Math.floor((totalSec % 3600) / 60);
    return `${hours}h ${minutes}m`;
  }
  const minutes = Math.floor(totalSec / 60);
  const seconds = totalSec % 60;
  if (minutes <= 0) {
    return `${seconds}s`;
  }
  return `${minutes}m ${seconds.toString().padStart(2, '0')}s`;
}

function compactAedLabel(site?: AedSite | null): string {
  if (!site) {
    return '待同步';
  }
  const floor = site.location.floor ? ` · ${site.location.floor}` : '';
  return `${site.name}${floor}`;
}

function mobileToneClass(role: RoleName | null, isPatient: boolean, isdemoResponder: boolean): string {
  if (isPatient) {
    return 'patient';
  }
  if (role) {
    return `role-${role.toLowerCase()}`;
  }
  if (isdemoResponder) {
    return 'standby';
  }
  return 'neutral';
}

function healthStatItems(summary?: HealthSignalSummary | null): Array<{ label: string; value: string; tone?: 'danger' | 'ok' }> {
  return [
    {
      label: '心率',
      value: summary?.heartRateBpm ? `${summary.heartRateBpm}` : '--',
      tone: summary?.heartRateBpm && summary.heartRateBpm >= 110 ? 'danger' : undefined,
    },
    {
      label: '血氧',
      value: summary?.bloodOxygenPercent ? `${summary.bloodOxygenPercent}%` : '--',
      tone: summary?.bloodOxygenPercent && summary.bloodOxygenPercent < 95 ? 'danger' : 'ok',
    },
    {
      label: '压力',
      value: summary?.pressureScore !== undefined && summary?.pressureScore !== null ? `${summary.pressureScore}` : '--',
      tone: summary?.pressureScore && summary.pressureScore >= 70 ? 'danger' : undefined,
    },
  ];
}

function translateLogMessage(message: string, clients: ClientInfo[]): string {
  const displayUser = (userId?: string | null) => {
    const client = clients.find((item) => item.userId === userId);
    return client?.displayName || shortId(userId);
  };
  const assigned = message.match(/^(PRIME|RUNNER|GUIDE) assigned \(([^)]+)\) via (.+)$/);
  if (assigned) {
    return `${translateRoleLabel(assigned[1])}已分配给 ${displayUser(assigned[2])}，来源：${translateDispatchSource(assigned[3])}`;
  }
  const joined = message.match(/^(PRIME|RUNNER|GUIDE) joined \(([^)]+)\)$/);
  if (joined) {
    return `${translateRoleLabel(joined[1])}已响应，用户：${displayUser(joined[2])}`;
  }
  const autoJoined = message.match(/^(PRIME|RUNNER|GUIDE) auto-joined \(([^)]+)\)$/);
  if (autoJoined) {
    return `${translateRoleLabel(autoJoined[1])}自动接单，用户：${displayUser(autoJoined[2])}`;
  }
  const patientDesignated = message.match(/^Patient designated by (.+) \(([^)]+)\)$/);
  if (patientDesignated) {
    const rawSource = patientDesignated[1];
    const source = rawSource.startsWith('patient SOS') ? '患者 SOS' : rawSource === 'dashboard' ? '调度台' : '系统';
    return `患者事件已由${source} 触发，患者：${displayUser(patientDesignated[2])}`;
  }
  const patientSos = message.match(/^Patient SOS (alerting started|confirmed|alerting canceled) \(([^)]+)\)$/);
  if (patientSos) {
    const label =
      patientSos[1] === 'alerting started'
        ? '患者 SOS 已启动'
        : patientSos[1] === 'confirmed'
          ? '患者 SOS 已确认'
          : '患者 SOS 已取消';
    return `${label}，患者：${displayUser(patientSos[2])}`;
  }
  const cpr = message.match(/^CPR started by (.+)$/);
  if (cpr) {
    return `CPR 已开始，执行者：${displayUser(cpr[1])}`;
  }
  const aedPicked = message.match(/^AED picked by (.+)$/);
  if (aedPicked) {
    return `AED 已取到，执行者：${displayUser(aedPicked[1])}`;
  }
  const aedDelivered = message.match(/^AED delivered by (.+)$/);
  if (aedDelivered) {
    return `AED 已送达，执行者：${displayUser(aedDelivered[1])}`;
  }
  const analysis = message.match(/^AED analysis started by (.+)$/);
  if (analysis) {
    return `AED 分析已开始，执行者：${displayUser(analysis[1])}`;
  }
  const shock = message.match(/^AED shock delivered by (.+)$/);
  if (shock) {
    return `AED 除颤已记录，执行者：${displayUser(shock[1])}`;
  }
  const ambulance = message.match(/^Ambulance arrived \(reported by (.+)\)$/);
  if (ambulance) {
    return `救护车已到场，上报者：${displayUser(ambulance[1])}`;
  }
  const handover = message.match(/^Handover completed by (.+)$/);
  if (handover) {
    return `交接已完成，确认者：${displayUser(handover[1])}`;
  }
  const aedUpdated = message.match(/^AED site updated \((.+)\)$/);
  if (aedUpdated) {
    return `AED 点位已更新：${aedUpdated[1]}`;
  }
  switch (message) {
    case 'AI dispatching started':
      return '智能调度已启动';
    case 'Incident reset':
      return '事件已重置';
    case 'Incident created':
      return '事件已创建';
    case 'demo scenario bootstrapped':
      return '演示场景已初始化';
    case 'SOS alerting started':
      return 'SOS 已启动';
    case 'SOS alerting canceled':
      return 'SOS 已取消';
    case 'Incident auto-triggered':
      return '事件已自动触发';
    default:
      return /[A-Za-z]/.test(message) ? '系统记录已更新' : message;
  }
}

function AuthPanel({ onAuthenticated }: { onAuthenticated: (session: StoredSession, location?: GeoPoint) => void }) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [busy, setBusy] = useState<string | null>(null);
  const [notice, setNotice] = useState<Notice>(null);
  const [form, setForm] = useState<RegisterForm>({
    displayName: '移动端用户',
    phone: '',
    password: '',
    organization: profilePresets[0].values.organization,
    healthCondition: profilePresets[0].values.healthCondition,
    professionIdentity: profilePresets[0].values.professionIdentity,
    profileBio: profilePresets[0].values.profileBio,
  });

  const updateForm = (key: keyof RegisterForm, value: string) => setForm((current) => ({ ...current, [key]: value }));

  async function submit() {
    if (!form.phone.trim() || !form.password.trim()) {
      setNotice({ kind: 'error', text: '请输入手机号和密码。' });
      return;
    }
    setBusy('auth');
    setNotice(null);
    try {
      const auth =
        mode === 'login'
          ? await loginAccount(form.phone.trim(), form.password)
          : await registerAccount({ ...form, phone: form.phone.trim() });
      const session = { token: auth.token, user: auth.user, tokenExpiresAt: auth.tokenExpiresAt };
      saveSession(session);
      onAuthenticated(session);
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '认证失败' });
    } finally {
      setBusy(null);
    }
  }

  async function enterdemo(persona: demoPersona) {
    setBusy(persona);
    setNotice(null);
    try {
      const auth = await logindemoPersona(persona);
      const session = { token: auth.token, user: auth.user, tokenExpiresAt: auth.tokenExpiresAt, demoPersona: persona };
      const location = demoLocationFor(persona);
      saveSession(session);
      window.sessionStorage.setItem(tabLocationKey(), JSON.stringify(location));
      onAuthenticated(session, location);
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '进入演示模式失败' });
    } finally {
      setBusy(null);
    }
  }

  return (
    <main className="mobile-shell mobile-auth-shell">
      <section className="mobile-hero">
        <div className="mobile-app-mark">
          <HeartPulse size={28} />
        </div>
        <p className="mobile-kicker">生命反射弧移动端</p>
        <h1>浏览器应急端</h1>
        <p>无需安装应用，手机浏览器即可登录、接入事件、触发 SOS、执行急救任务。</p>
        <p className="mobile-safety-copy">仅用于协同训练、训练复盘与研究验证，不替代 120、AED 语音提示、专业医护判断或真实医疗诊断。</p>
      </section>

      <section className="mobile-panel" id="top">
        <div className="mobile-demo-entry">
          <div className="mobile-section-head">
            <div>
              <p className="mobile-kicker">演示模式</p>
              <h2>演示模式直达</h2>
            </div>
          </div>
          <div className="mobile-demo-grid">
            {demoPersonas.map((persona) => (
              <button key={persona.key} type="button" onClick={() => enterdemo(persona.key)} disabled={Boolean(busy)}>
                <strong>{busy === persona.key ? '进入中...' : persona.label}</strong>
                <span>{persona.description}</span>
              </button>
            ))}
          </div>
        </div>

        <div className="mobile-segment">
          <button className={mode === 'login' ? 'active' : ''} onClick={() => setMode('login')}>
            登录
          </button>
          <button className={mode === 'register' ? 'active' : ''} onClick={() => setMode('register')}>
            注册
          </button>
        </div>

        {mode === 'register' && (
          <div className="mobile-presets">
            {profilePresets.map((preset) => (
              <button
                key={preset.label}
                onClick={() => setForm((current) => ({ ...current, ...preset.values }))}
                type="button"
              >
                {preset.label}
              </button>
            ))}
          </div>
        )}

        <label>
          手机号
          <input
            inputMode="tel"
            autoComplete="tel"
            value={form.phone}
            onChange={(event) => updateForm('phone', event.target.value)}
            placeholder="用于登录演示账号"
          />
        </label>
        <label>
          密码
          <input
            type="password"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            value={form.password}
            onChange={(event) => updateForm('password', event.target.value)}
            placeholder="至少 6 位"
          />
        </label>

        {mode === 'register' && (
          <>
            <label>
              昵称
              <input value={form.displayName} onChange={(event) => updateForm('displayName', event.target.value)} />
            </label>
            <label>
              组织
              <input value={form.organization} onChange={(event) => updateForm('organization', event.target.value)} />
            </label>
            <label>
              身体状况
              <input value={form.healthCondition} onChange={(event) => updateForm('healthCondition', event.target.value)} />
            </label>
            <label>
              职业身份
              <input
                value={form.professionIdentity}
                onChange={(event) => updateForm('professionIdentity', event.target.value)}
              />
            </label>
            <label>
              个人介绍
              <textarea value={form.profileBio} onChange={(event) => updateForm('profileBio', event.target.value)} rows={3} />
            </label>
          </>
        )}

        {notice && <div className={`mobile-notice ${notice.kind}`}>{notice.text}</div>}
        <button className="mobile-primary-button" onClick={submit} disabled={Boolean(busy)}>
          {busy === 'auth' ? '处理中...' : mode === 'login' ? '进入移动端' : '创建账号并进入'}
        </button>
      </section>
    </main>
  );
}

function MobileApp() {
  const urldemoPersona = useMemo(() => readdemoPersonaFromUrl(), []);
  const urlIncidentId = useMemo(() => readIncidentIdFromUrl(), []);
  const [theme, setTheme] = useState<MobileTheme>(() => readStoredTheme());
  const [session, setSession] = useState<StoredSession | null>(() => (urldemoPersona ? null : readStoredSession()));
  const [booting, setBooting] = useState(Boolean(urldemoPersona) || Boolean(readStoredSession()));
  const [incidentIdInput, setIncidentIdInput] = useState(() => readInitialIncidentId(urlIncidentId, urldemoPersona));
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [clients, setClients] = useState<ClientInfo[]>([]);
  const [aedSites, setAedSites] = useState<AedSite[]>([]);
  const [location, setLocation] = useState<GeoPoint>(() => readStoredLocation());
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle');
  const [notice, setNotice] = useState<Notice>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const busyActionRef = useRef<string | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [activeView, setActiveView] = useState<MobileView>('home');
  const [sosConfirming, setSosConfirming] = useState(false);
  const [showManualJoin, setShowManualJoin] = useState(false);
  const [showSceneDetails, setShowSceneDetails] = useState(false);
  const [demoAdminToken, setdemoAdminToken] = useState(getStoreddemoAdminToken);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<number | null>(null);

  const token = session?.token ?? '';
  const user = session?.user ?? null;
  const userRole = useMemo(() => findUserRole(incident, user?.userId), [incident, user?.userId]);
  const isPatient = Boolean(incident?.patientUserId && incident.patientUserId === user?.userId);
  const isPatientTerminal = isPatient || session?.demoPersona === 'patient';
  const isdemoResponder = Boolean(session?.demoPersona && session.demoPersona !== 'patient');
  const demoResponderLabel = session?.demoPersona ? demoPersonas.find((item) => item.key === session.demoPersona)?.label : null;
  const currentClient = useMemo(
    () => clients.find((client) => client.userId === user?.userId) ?? null,
    [clients, user?.userId],
  );
  const candidateRole = userRole ?? (currentClient?.assignedRole as RoleName | null) ?? null;
  const responderTaskReady = isIncidentReadyForResponderTask(incident);
  const activeRole = responderTaskReady ? candidateRole : null;
  const primaryAed = useMemo(() => selectPrimaryAed(incident, aedSites, activeRole), [incident, aedSites, activeRole]);
  const elapsedSec = incident?.sos?.startTs ? Math.max(0, Math.floor((now - incident.sos.startTs) / 1000)) : 0;
  const sosRemaining =
    incident?.phase === 'CREATED' && incident?.sos?.status === 'ALERTING'
      ? Math.max(0, (incident.sos.durationSec ?? 0) - elapsedSec)
      : null;
  const cprAnchorTs = getLatestLogTs(incident, isShockDelivered(incident) ? 'AED shock delivered' : 'CPR started');
  const cprElapsedSec = cprAnchorTs ? Math.max(0, Math.floor((now - cprAnchorTs) / 1000)) : 0;
  const cprGuidance = getResuscitationGuidance(cprElapsedSec);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const trimmed = demoAdminToken.trim();
    if (trimmed) {
      window.localStorage.setItem(demo_ADMIN_TOKEN_KEY, trimmed);
    } else {
      window.localStorage.removeItem(demo_ADMIN_TOKEN_KEY);
    }
  }, [demoAdminToken]);

  const toggleTheme = () => {
    setTheme((current) => {
      const next = current === 'light' ? 'dark' : 'light';
      window.localStorage.setItem(MOBILE_THEME_KEY, next);
      return next;
    });
  };

  const loadPeripheralData = useCallback(async () => {
    const [nextClients, nextAeds] = await Promise.all([fetchClients(), fetchAedSites()]);
    setClients(nextClients);
    setAedSites(nextAeds);
  }, []);

  const connectIncident = useCallback(
    (incidentId: string) => {
      if (!incidentId) {
        return;
      }
      const previousSocket = wsRef.current;
      wsRef.current = null;
      previousSocket?.close();
      if (reconnectRef.current) {
        window.clearTimeout(reconnectRef.current);
        reconnectRef.current = null;
      }
      setSyncStatus('connecting');
      const socket = openIncidentSocket(incidentId);
      wsRef.current = socket;
      socket.onopen = () => {
        if (wsRef.current === socket) {
          setSyncStatus('live');
        }
      };
      socket.onmessage = (event) => {
        if (wsRef.current !== socket) {
          return;
        }
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === 'STATE') {
            setIncident((current) => mergeIncidentState(current, msg.payload as IncidentState));
          }
        } catch {
          setNotice({ kind: 'error', text: '实时消息解析失败。' });
        }
      };
      socket.onerror = () => {
        if (wsRef.current === socket) {
          setSyncStatus('offline');
        }
      };
      socket.onclose = () => {
        if (wsRef.current !== socket) {
          return;
        }
        if (reconnectRef.current) {
          return;
        }
        setSyncStatus('reconnecting');
        reconnectRef.current = window.setTimeout(() => connectIncident(incidentId), 1800);
      };
    },
    [],
  );

  const openCurrentIncident = useCallback(async () => {
    const state = await fetchCurrentIncident();
    setIncident((current) => mergeIncidentState(current, state));
    setIncidentIdInput(state.incidentId);
    window.localStorage.setItem(INCIDENT_KEY, state.incidentId);
    connectIncident(state.incidentId);
    await loadPeripheralData();
  }, [connectIncident, loadPeripheralData]);

  async function afterAuthenticated(next: StoredSession, nextLocation = location) {
    setSession(next);
    setLocation(nextLocation);
    setBooting(false);
    await ensurePresence(next, nextLocation);
    if (urlIncidentId) {
      const state = await fetchIncident(urlIncidentId);
      setIncident((current) => mergeIncidentState(current, state));
      setIncidentIdInput(state.incidentId);
      window.localStorage.setItem(INCIDENT_KEY, state.incidentId);
      connectIncident(state.incidentId);
      await loadPeripheralData();
    } else {
      await openCurrentIncident();
    }
  }

  async function ensurePresence(activeSession = session, activeLocation = location) {
    if (!activeSession) {
      return;
    }
    await registerClient(activeSession.user, activeSession.token, activeLocation);
    await updateClientHealth(
      activeSession.user.userId,
      activeSession.token,
      mockHealthSignalsFor(activeSession.user, activeSession.demoPersona),
    );
  }

  useEffect(() => {
    document.documentElement.dataset.mobileRoute = 'true';
    document.documentElement.dataset.mobileTheme = theme;
    return () => {
      delete document.documentElement.dataset.mobileTheme;
    };
  }, [theme]);

  useEffect(() => {
    document.documentElement.dataset.mobileRoute = 'true';
    let mounted = true;
    async function restore() {
      if (!session && urldemoPersona) {
        try {
          const auth = await logindemoPersona(urldemoPersona);
          const nextLocation = demoLocationFor(urldemoPersona);
          const next = { token: auth.token, user: auth.user, tokenExpiresAt: auth.tokenExpiresAt, demoPersona: urldemoPersona };
          saveSession(next);
          window.sessionStorage.setItem(tabLocationKey(), JSON.stringify(nextLocation));
          if (!mounted) {
            return;
          }
          setSession(next);
          setLocation(nextLocation);
          await ensurePresence(next, nextLocation);
          if (urlIncidentId) {
            const state = await fetchIncident(urlIncidentId);
            setIncident((current) => mergeIncidentState(current, state));
            setIncidentIdInput(state.incidentId);
            window.localStorage.setItem(INCIDENT_KEY, state.incidentId);
            connectIncident(state.incidentId);
            await loadPeripheralData();
          } else {
            await openCurrentIncident();
          }
          setNotice({ kind: 'ok', text: `已进入${demoPersonas.find((item) => item.key === urldemoPersona)?.label ?? '演示'}身份。` });
        } catch (error) {
          saveSession(null);
          if (mounted) {
            setNotice({ kind: 'error', text: error instanceof Error ? error.message : '演示模式启动失败。' });
          }
        } finally {
          if (mounted) {
            setBooting(false);
          }
        }
        return;
      }
      if (!session) {
        setBooting(false);
        return;
      }
      try {
        const me = await fetchMe(session.token);
        if (!mounted) {
          return;
        }
        const next = { token: session.token, user: me.user, tokenExpiresAt: me.tokenExpiresAt };
        saveSession(next);
        setSession(next);
        await ensurePresence(next, location);
        if (incidentIdInput) {
          const state = await fetchIncident(incidentIdInput);
          setIncident((current) => mergeIncidentState(current, state));
          connectIncident(state.incidentId);
        } else {
          await openCurrentIncident();
        }
        await loadPeripheralData();
      } catch (error) {
        saveSession(null);
        setSession(null);
        setNotice({ kind: 'error', text: error instanceof Error ? error.message : '登录态已失效，请重新登录。' });
      } finally {
        if (mounted) {
          setBooting(false);
        }
      }
    }
    restore();
    return () => {
      mounted = false;
      document.documentElement.removeAttribute('data-mobile-route');
    };
  }, []);

  useEffect(() => {
    const timer = window.setInterval(() => setNow(Date.now()), document.visibilityState === 'hidden' ? 5000 : 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!incident || incident.phase !== 'CREATED' || incident.sos?.status === 'ALERTING' || isdemoResponder) {
      setSosConfirming(false);
    }
  }, [incident?.incidentId, incident?.phase, incident?.sos?.status, isdemoResponder]);

  useEffect(() => {
    return () => {
      const socket = wsRef.current;
      wsRef.current = null;
      socket?.close();
      if (reconnectRef.current) {
        window.clearTimeout(reconnectRef.current);
        reconnectRef.current = null;
      }
    };
  }, []);

  async function runAction(label: string, work: () => Promise<void | string>, okText?: string) {
    if (busyActionRef.current) {
      return;
    }
    busyActionRef.current = label;
    setBusyAction(label);
    setNotice(null);
    try {
      const resultText = await work();
      if (incident) {
        const next = await fetchIncident(incident.incidentId);
        setIncident((current) => mergeIncidentState(current, next));
      }
      await loadPeripheralData();
      const successText = typeof resultText === 'string' ? resultText : okText;
      if (successText) {
        setNotice({ kind: 'ok', text: successText });
      }
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '操作失败' });
    } finally {
      busyActionRef.current = null;
      setBusyAction(null);
    }
  }

  async function openByInput() {
    const id = incidentIdInput.trim();
    if (!id) {
      setNotice({ kind: 'error', text: '请输入事件编号，或直接打开当前事件。' });
      return;
    }
    await runAction('open', async () => {
      const state = await fetchIncident(id);
      setIncident((current) => mergeIncidentState(current, state));
      window.localStorage.setItem(INCIDENT_KEY, state.incidentId);
      connectIncident(state.incidentId);
      await loadPeripheralData();
    });
  }

  async function reportLocation() {
    if (!session) {
      return;
    }
    await runAction(
      'location',
      async () => {
        let next = { ...location, updatedTs: Date.now() };
        if (navigator.geolocation) {
          try {
            const pos = await new Promise<GeolocationPosition>((resolve, reject) => {
              navigator.geolocation.getCurrentPosition(resolve, reject, {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 30000,
              });
            });
            next = {
              latitude: pos.coords.latitude,
              longitude: pos.coords.longitude,
              accuracyMeters: pos.coords.accuracy,
              label: '浏览器定位',
              source: 'browser',
              updatedTs: Date.now(),
            };
          } catch {
            next = { ...next, source: 'mobile-demo', label: location.label || '手动/演示点位' };
          }
        }
        setLocation(next);
        const locationStorage = session.demoPersona ? window.sessionStorage : window.localStorage;
        locationStorage.setItem(session.demoPersona ? tabLocationKey() : LOCATION_KEY, JSON.stringify(next));
        await updateClientLocation(session.user.userId, session.token, next);
      },
      '位置已上报。',
    );
  }

  async function doLogout() {
    if (session?.token) {
      try {
        await logoutAccount(session.token);
      } catch {
        // Local logout is still useful if the network is unavailable.
      }
    }
    saveSession(null);
    setSession(null);
    setIncident(null);
    const socket = wsRef.current;
    wsRef.current = null;
    socket?.close();
    if (reconnectRef.current) {
      window.clearTimeout(reconnectRef.current);
      reconnectRef.current = null;
    }
    setSyncStatus('idle');
  }

  async function handlePatientSos() {
    if (!incident || !session) {
      return;
    }
    if (incident.phase !== 'CREATED') {
      setSosConfirming(false);
      setNotice({ kind: 'info', text: '当前事件已进入协同处置，不能重复启动 SOS。' });
      return;
    }
    if (isdemoResponder) {
      setSosConfirming(false);
      setNotice({ kind: 'info', text: `${demoResponderLabel ?? '当前演示端'}仅响应分派任务，请等待患者端启动 SOS。` });
      return;
    }
    if (!sosConfirming) {
      setSosConfirming(true);
      setNotice({ kind: 'info', text: '再次点击确认启动 SOS。' });
      return;
    }
    setSosConfirming(false);
    await runAction(
      'sos',
      async () => patientSosStart(incident.incidentId, session.token),
      'SOS 已启动，系统会自动确认并分派任务。',
    );
  }

  async function cancelPatientSos() {
    if (!incident || !session) {
      return;
    }
    setSosConfirming(false);
    await runAction('sosCancel', async () => patientSosCancel(incident.incidentId, session.token), 'SOS 已取消。');
  }

  async function joinRole(role: RoleName) {
    if (!incident || !session) {
      return;
    }
    await runAction(role, async () => joinIncident(incident.incidentId, role, session.user.userId, session.token), '已响应任务。');
  }

  async function autoJoin() {
    if (!session) {
      return;
    }
    if (!isIncidentReadyForResponderTask(incident)) {
      setNotice({ kind: 'info', text: '请先从患者端启动 SOS，系统分派任务后再接单。' });
      return;
    }
    await runAction('autoJoin', async () => {
      const joined = await autoJoinCurrent(session.user.userId, session.token);
      setIncidentIdInput(joined.incidentId);
      window.localStorage.setItem(INCIDENT_KEY, joined.incidentId);
      connectIncident(joined.incidentId);
      const state = await fetchIncident(joined.incidentId);
      setIncident((current) => mergeIncidentState(current, state));
    });
  }

  async function executeRoleAction() {
    if (!activeRole || !incident || !session) {
      return;
    }
    const action = roleAction(activeRole, incident);
    if (action.action === 'WAIT') {
      return;
    }
    if (action.action === 'JOIN') {
      await joinRole(activeRole);
      return;
    }
    await runAction(action.action, async () =>
      postIncidentAction(incident.incidentId, action.action, session.user.userId, session.token),
    );
  }

  async function downloadArchivePackage() {
    if (!incident) {
      setNotice({ kind: 'error', text: '请先打开本轮事件，再下载事件证据包。' });
      return;
    }
    await runAction(
      'package',
      async () => {
        const download = await downloadExperimentPackage(session?.token, demoAdminToken, incident.incidentId);
        return download.packageSha256
          ? `事件证据包已下载：${download.filename}；SHA-256 ${download.packageSha256}`
          : `事件证据包已下载：${download.filename}。未读取到 SHA-256 响应头，请以 ZIP 内 manifest 为准。`;
      },
    );
  }

  async function copyArchiveLink() {
    if (!incident) {
      return;
    }
    const url = new URL('/mobile', window.location.origin);
    url.searchParams.set('incidentId', incident.incidentId);
    if (session.demoPersona) {
      url.searchParams.set('demo', session.demoPersona);
      url.searchParams.set('slot', session.demoPersona);
    }
    const copied = await copyTextToClipboard(url.toString());
    setNotice({
      kind: copied ? 'ok' : 'error',
      text: copied ? '本轮移动端链接已复制。' : '复制失败，请从地址栏手动复制链接。',
    });
  }

  if (booting) {
    return (
      <main className="mobile-shell mobile-loading">
        <HeartPulse size={36} />
        <p>正在恢复移动端登录态...</p>
      </main>
    );
  }

  if (!session || !user) {
    return <AuthPanel onAuthenticated={afterAuthenticated} />;
  }

  const logs = [...(incident?.logs ?? [])].slice(-8).reverse();
  const assignedUsers = responderTaskReady ? clients.filter((client) => client.assignedRole) : [];
  const action = activeRole ? roleAction(activeRole, incident) : null;
  const primeStep = activeRole === 'PRIME' ? primeNextStep(incident) : null;
  const phaseLabel = incident ? translatePhaseLabel(incident.phase) : '未接入事件';
  const syncLabel =
    syncStatus === 'live'
      ? '实时在线'
      : syncStatus === 'connecting'
        ? '连接中'
        : syncStatus === 'reconnecting'
          ? '恢复连接中'
          : syncStatus === 'offline'
            ? '连接离线'
            : '待连接';
  const roleLabel = isPatientTerminal
    ? '患者端'
    : activeRole
      ? translateRoleLabel(activeRole)
      : '待命终端';
  const nextActionSummary = isPatientTerminal
    ? '保持当前位置，等待协同成员到场'
    : activeRole && action
      ? `${translateRoleLabel(activeRole)}：${action.title}`
      : incident
        ? '保持在线，等待本轮任务'
        : '打开或加入事件';
  const commandTitle =
    activeRole && action && !isPatientTerminal
      ? action.title
      : isPatientTerminal && sosRemaining !== null
        ? `SOS 倒计时 ${sosRemaining}s`
        : isPatientTerminal && incident?.phase !== 'CREATED'
          ? '等待救援'
          : isPatientTerminal
            ? '我出事了，需要帮助'
            : incident
              ? '在线待命'
              : '接入当前事件';
  const commandBody =
    activeRole && action && !isPatientTerminal
      ? action.hint
      : isPatientTerminal && incident?.phase === 'CREATED'
        ? '点击下方按钮发出求救，系统会自动呼叫最近的急救力量。'
        : isPatientTerminal && incident?.phase !== 'CREATED'
          ? '救援人员正在赶来，请留在当前位置等待。'
          : '';
  const incidentStartedAt = incident?.logs?.[0]?.ts ?? null;
  const incidentElapsedLabel = formatElapsedLabel(incidentStartedAt, now);
  const commandTone = mobileToneClass(activeRole, isPatientTerminal, isdemoResponder);
  const healthStats = healthStatItems(currentClient?.healthSignals);
  const visibleClients = clients.slice(0, 5);
  const viewTabs: Array<{ key: MobileView; label: string; icon: React.ReactNode }> = [
    { key: 'home', label: '总览', icon: <Activity size={18} /> },
    { key: 'mission', label: '任务', icon: <Radio size={18} /> },
    { key: 'scene', label: '现场', icon: <MapPin size={18} /> },
    { key: 'logs', label: '记录', icon: <Clock size={18} /> },
  ];

  return (
    <main className="mobile-shell">
      <header className="mobile-topbar">
        <div>
          <p className="mobile-kicker">生命反射弧移动端</p>
          <h1>应急协同端</h1>
        </div>
        <div className="mobile-top-actions">
          <button className="mobile-icon-button" onClick={toggleTheme} aria-label={theme === 'light' ? '切换深色模式' : '切换浅色模式'}>
            {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
          </button>
          <button className="mobile-icon-button" onClick={doLogout} aria-label="退出登录">
            <LogOut size={18} />
          </button>
        </div>
      </header>

      <section className={`mobile-command-header ${commandTone}`}>
        <div className="mobile-command-status">
          <span className={`sync-dot ${syncStatus}`} />
          <span>{syncLabel}</span>
          <strong>{phaseLabel}</strong>
        </div>
        <div className="mobile-command-main">
          <div>
            <p className="mobile-kicker">{roleLabel}</p>
            <h2>{commandTitle}</h2>
            {commandBody && <p>{commandBody}</p>}
          </div>
          {incidentStartedAt && (
            <div className="mobile-command-metric">
              <span>黄金时间</span>
              <strong>{incidentElapsedLabel}</strong>
            </div>
          )}
        </div>
      </section>

      {incident && activeRole && action && !isPatientTerminal && (
        <section className="mobile-context-strip" aria-label="当前行动指引">
          <BadgeInfo size={15} />
          <strong>{nextActionSummary}</strong>
        </section>
      )}

      {notice && <div className={`mobile-notice ${notice.kind}`}>{notice.text}</div>}

      <nav className="mobile-view-tabs" aria-label="移动端信息分层">
        {viewTabs.map(({ key, label, icon }) => (
          <button key={key} className={activeView === key ? 'active' : ''} onClick={() => setActiveView(key)}>
            {icon}
            {label}
          </button>
        ))}
      </nav>

      {activeView === 'home' && (
        <>
          {activeRole && action && !isPatientTerminal ? (
            <section className={`mobile-emergency-panel responder role-${activeRole.toLowerCase()}`}>
              <div className="mobile-action-row">
                <div>
                  {activeRole === 'PRIME' ? <HeartPulse size={28} /> : activeRole === 'RUNNER' ? <Zap size={28} /> : <Shield size={28} />}
                  <p className="mobile-kicker">当前动作</p>
                  <h2>{action.title}</h2>
                  <p>{action.hint}</p>
                </div>
                <img className="mobile-action-illustration" src={responseRolesUrl} alt="" loading="lazy" aria-hidden="true" />
              </div>
              {primeStep && (
                <div className={`mobile-next-step ${primeStep.tone}`}>
                  <strong>{primeStep.title}</strong>
                  <p>{primeStep.body}</p>
                </div>
              )}
              <button className="mobile-primary-button" onClick={executeRoleAction} disabled={action.disabled || Boolean(busyAction)}>
                {busyAction ? '提交中...' : action.buttonLabel}
              </button>
            </section>
          ) : (
            <section className={`mobile-emergency-panel ${isPatient ? 'patient' : ''} ${isdemoResponder ? 'readonly' : ''}`}>
              {isdemoResponder ? (
                <div className="mobile-emergency-actions single">
                  <button className="mobile-ghost-button" type="button" disabled>
                    {incident?.sos?.status === 'ALERTING' ? '等待任务分派...' : '待命中，等待患者端触发求救'}
                  </button>
                </div>
              ) : (
                <>
                  {isPatientTerminal && incident && incident.phase !== 'CREATED' && (
                    <div className="mobile-rescue-progress" aria-label="救援力量进度">
                      {[
                        { role: 'PRIME', label: '急救' },
                        { role: 'RUNNER', label: 'AED' },
                        { role: 'GUIDE', label: '接应' },
                      ].map(({ role, label }) => {
                        const status = incident.roles?.[role as 'PRIME' | 'RUNNER' | 'GUIDE']?.status;
                        const arrived = status === 'CPR_STARTED' || status === 'AED_DELIVERED' || status === 'AMBULANCE_ARRIVED' || status === 'HANDOVER_COMPLETED';
                        const dispatched = Boolean(incident.roles?.[role as 'PRIME' | 'RUNNER' | 'GUIDE']?.userId);
                        return (
                          <div key={role} className={`mobile-rescue-item ${arrived ? 'arrived' : dispatched ? 'onway' : 'pending'}`}>
                            <span className="mobile-rescue-dot" />
                            <span>{label}</span>
                            <small>{arrived ? '已到' : dispatched ? '赶来中' : '待分派'}</small>
                          </div>
                        );
                      })}
                    </div>
                  )}
                  <div className="mobile-emergency-actions">
                    <button
                      className={`mobile-danger-button ${sosConfirming ? 'confirming' : ''}`}
                      onClick={handlePatientSos}
                      disabled={!incident || busyAction === 'sos'}
                    >
                      {busyAction === 'sos' ? '启动中...' : sosConfirming ? '再次点击确认 SOS' : '启动 SOS'}
                    </button>
                    <button
                      className="mobile-ghost-button"
                      onClick={cancelPatientSos}
                      disabled={!incident || incident.sos?.status !== 'ALERTING' || !isPatientTerminal || busyAction === 'sosCancel'}
                    >
                      取消
                    </button>
                  </div>
                </>
              )}
            </section>
          )}

          <section className="mobile-identity-card" id="top">
            <div className="mobile-identity-main">
              <div className="mobile-user-avatar">
                <UserRound size={22} />
              </div>
              <div>
                <p className="mobile-kicker">当前终端</p>
                <strong>{user.displayName}</strong>
                <p>{user.organization} · {user.professionIdentity}</p>
              </div>
            </div>
            <div className="mobile-location-line">
              <MapPin size={14} />
              <span>{formatLocationLabel(location)}</span>
            </div>
            {healthStats.length > 0 && (
              <details className="mobile-health-details">
                <summary className="mobile-health-summary">
                  <HeartPulse size={14} />
                  健康数据
                  <span className="mobile-chevron" />
                </summary>
                <div className="mobile-health-stats">
                  {healthStats.map((item) => (
                    <div key={item.label} className={item.tone ? `tone-${item.tone}` : ''}>
                      <span>{item.label}</span>
                      <strong>{item.value}</strong>
                    </div>
                  ))}
                </div>
                <div className="mobile-health-line">
                  <HeartPulse size={14} />
                  <span>{formatHealthSignalSummary(currentClient?.healthSignals)}</span>
                </div>
              </details>
            )}
          </section>

          {!incident && (
            <section className="mobile-panel mobile-incident-panel">
              <div className="mobile-section-head">
                <div>
                  <p className="mobile-kicker">事件</p>
                  <h2>接入当前事件</h2>
                </div>
                <button className="mobile-small-button" onClick={() => runAction('refresh', openCurrentIncident)} disabled={busyAction === 'refresh'}>
                  <RefreshCw size={14} />
                  同步
                </button>
              </div>
              <div className="mobile-input-row mobile-compact-input-row">
                <input
                  value={incidentIdInput}
                  onChange={(event) => setIncidentIdInput(event.target.value)}
                  placeholder="事件编号"
                />
                <button onClick={openByInput} disabled={busyAction === 'open'}>打开</button>
              </div>
            </section>
          )}
        </>
      )}

      {activeView === 'mission' && (
      <section className="mobile-panel">
        <div className="mobile-section-head">
          <div>
            <p className="mobile-kicker">任务</p>
            <h2>我的任务</h2>
          </div>
          <button className="mobile-small-button" onClick={autoJoin} disabled={!responderTaskReady || busyAction === 'autoJoin'}>
            <Radio size={14} />
            {responderTaskReady ? '自动接单' : '待启动'}
          </button>
        </div>
        {activeRole && action ? (
          <div className={`mobile-role-card role-${activeRole.toLowerCase()}`}>
            <img className="mobile-card-visual" src={responseRolesUrl} alt="" loading="lazy" aria-hidden="true" />
            <div className="mobile-role-title">
              {activeRole === 'PRIME' ? <HeartPulse size={24} /> : activeRole === 'RUNNER' ? <Zap size={24} /> : <Shield size={24} />}
              <div>
                <p className="mobile-kicker">当前任务</p>
                <h3>{translateRoleLabel(activeRole)}</h3>
                <p>{translateRoleStatus(incident?.roles?.[activeRole]?.status)}</p>
              </div>
            </div>
            <p>{action.hint}</p>
            {primeStep && (
              <div className={`mobile-next-step ${primeStep.tone}`}>
                <strong>{primeStep.title}</strong>
                <p>{primeStep.body}</p>
              </div>
            )}
            {activeRole === 'PRIME' && incident?.roles.PRIME?.status === 'CPR_STARTED' && (
              <div className="mobile-cpr-meter">
                <div>
                  <strong>{cprGuidance.stageAction}</strong>
                  <span>{cprGuidance.stageTitle} · {cprGuidance.stageRemaining}s</span>
                </div>
                <p>{cprGuidance.stageBody}</p>
              </div>
            )}
            <button className="mobile-primary-button" onClick={executeRoleAction} disabled={action.disabled || Boolean(busyAction)}>
              {busyAction ? '提交中...' : action.buttonLabel}
            </button>
          </div>
        ) : (
          <div className="mobile-empty-state">
            <Radio size={28} />
            <p>{responderTaskReady ? '尚未分配到你的任务。保持在线，必要时可点击自动接单。' : '患者端启动 SOS 并完成分派后，本终端会显示对应任务。'}</p>
          </div>
        )}

        <div className="mobile-manual-join">
          <button
            type="button"
            className="mobile-manual-toggle"
            onClick={() => setShowManualJoin((visible) => !visible)}
            aria-expanded={showManualJoin}
          >
            <span>备用：手动选择角色</span>
            <ChevronDown size={16} />
          </button>
          {showManualJoin && (
            <div className="mobile-role-grid">
              {(['PRIME', 'RUNNER', 'GUIDE'] as RoleName[]).map((role) => (
                <button key={role} onClick={() => joinRole(role)} disabled={!incident || !responderTaskReady || Boolean(busyAction)}>
                  <strong>{translateRoleLabel(role)}</strong>
                  <span>{translateRoleStatus(incident?.roles?.[role]?.status)}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </section>
      )}

      {activeView === 'scene' && (
      <>
      <section className="mobile-panel">
        <div className="mobile-section-head">
          <div>
            <p className="mobile-kicker">现场</p>
            <h2>位置与 AED</h2>
          </div>
          <button className="mobile-small-button" onClick={reportLocation} disabled={busyAction === 'location'}>
            <Navigation size={14} />
            上报位置
          </button>
        </div>
        <img className="mobile-card-visual mobile-route-visual" src={aedRouteUrl} alt="" loading="lazy" aria-hidden="true" />
        {primaryAed ? (
          <div className="mobile-aed-card">
            <MapPin size={20} />
            <div>
              <strong>{primaryAed.name}</strong>
              <p>{formatLocationLabel(primaryAed.location)}</p>
              <p>{primaryAed.accessNotes || primaryAed.status}</p>
            </div>
          </div>
        ) : (
          <div className="mobile-empty-state compact">暂无 AED 点位，可在 Web 调度台初始化演示场景。</div>
        )}
      </section>

      <section className="mobile-panel">
        <div className="mobile-section-head">
          <div>
            <p className="mobile-kicker">协同</p>
            <h2>协同状态</h2>
          </div>
          <span className="mobile-count">{assignedUsers.length}/{clients.length}</span>
        </div>
        <div className="mobile-team-list">
          {visibleClients.map((client) => (
            <div key={client.userId}>
              <span className={client.online ? 'online' : ''} />
              <div>
                <strong>{client.displayName}</strong>
                <p>{client.isPatient ? '患者端' : translateRoleLabel(responderTaskReady ? client.assignedRole : null)} · {formatLocationLabel(client.location)}</p>
                <p className="mobile-health-copy">{client.online ? '保持在线' : '等待重连'} · {translateRoleStatus(responderTaskReady && client.assignedRole ? incident?.roles?.[client.assignedRole]?.status : null)}</p>
              </div>
            </div>
          ))}
          {clients.length === 0 && <div className="mobile-empty-state compact">暂无在线终端。</div>}
          {clients.length > visibleClients.length && (
            <div className="mobile-empty-state compact">另有 {clients.length - visibleClients.length} 台终端在线，可在 Web 调度台查看完整列表。</div>
          )}
        </div>
        <div className="mobile-manual-join">
          <button
            type="button"
            className="mobile-manual-toggle"
            onClick={() => setShowSceneDetails((visible) => !visible)}
            aria-expanded={showSceneDetails}
          >
            <span>分派依据与健康摘要</span>
            <ChevronDown size={16} />
          </button>
          {showSceneDetails && (
            <div className="mobile-scene-details">
              {activeRole && incident?.dispatchRationale?.[activeRole] && (
                <div className="mobile-rationale">
                  <div>
                    <span>智能评分</span>
                    <strong>{incident.dispatchRationale[activeRole].score.toFixed(1)}</strong>
                  </div>
                  <div>
                    <span>距患者</span>
                    <strong>{formatDistanceLabel(incident.dispatchRationale[activeRole].distanceToPatientMeters)}</strong>
                  </div>
                  <p>{incident.dispatchRationale[activeRole].reasons.join('；') || '基于画像、距离和任务适配度分派。'}</p>
                </div>
              )}
              <div className="mobile-team-list">
                {visibleClients.map((client) => (
                  <div key={`${client.userId}-health`}>
                    <span className={client.healthSignals ? 'online' : ''} />
                    <div>
                      <strong>{client.displayName}</strong>
                      <p className="mobile-health-copy">
                        {formatHealthSignalSummary(client.healthSignals)}
                      </p>
                      {Boolean(client.healthSignals?.riskTags?.length) && (
                        <p className="mobile-health-copy warning">
                          风险标记：{formatHealthRiskTags(client.healthSignals?.riskTags)}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>
      </>
      )}

      {activeView === 'logs' && (
      <section className="mobile-panel">
        <div className="mobile-section-head">
          <div>
            <p className="mobile-kicker">记录</p>
            <h2>最近动态</h2>
          </div>
          <Clock size={18} />
        </div>
        <div className="mobile-log-list">
          {logs.map((log) => (
            <div key={`${log.ts}-${log.msg}`}>
              <time>{formatTimeLabel(log.ts)}</time>
              <p>{translateLogMessage(log.msg, clients)}</p>
            </div>
          ))}
          {logs.length === 0 && <div className="mobile-empty-state compact">等待事件触发。</div>}
        </div>
      </section>
      )}

      {incident?.phase === 'ARCHIVED' && (
        <section className="mobile-panel mobile-summary">
          <CheckCircle2 size={26} />
          <h2>本次预实验已归档</h2>
          <p>事件日志、角色响应和 AED 取送信息已经进入事件证据包。对外展示请优先使用匿名化文件、专家复核清单和观察员记录表，本系统不宣称真实临床疗效。</p>
          <label className="mobile-token-field">
            <span>演示口令</span>
            <input
              value={demoAdminToken}
              onChange={(event) => setdemoAdminToken(event.target.value)}
              placeholder="输入演示口令"
              autoComplete="off"
            />
          </label>
          <button className="mobile-primary-button mobile-summary-action" onClick={downloadArchivePackage} disabled={busyAction === 'package'}>
            {busyAction === 'package' ? '下载中...' : '下载事件证据包'}
          </button>
          <div className="mobile-summary-actions">
            <button className="mobile-ghost-button" type="button" onClick={copyArchiveLink}>
              <Copy size={16} />
              复制本轮链接
            </button>
            <a className="mobile-summary-link" href="/">
              <ExternalLink size={16} />
              返回总控台
            </a>
          </div>
          <p className="mobile-summary-note">手机端会保存该口令并与 Web 总控台共享；若你已用正式管理员账号登录，也可直接下载。</p>
        </section>
      )}
    </main>
  );
}

export default MobileApp;
