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
  loginDemoPersona,
  logoutAccount,
  openIncidentSocket,
  patientSosCancel,
  patientSosStart,
  postIncidentAction,
  registerAccount,
  registerClient,
  updateClientHealth,
  updateClientLocation,
  getStoredDemoAdminToken,
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
import './mobile.css';

type AuthMode = 'login' | 'register';
type SyncStatus = 'idle' | 'connecting' | 'live' | 'reconnecting' | 'offline';
type MobileView = 'home' | 'mission' | 'scene' | 'logs';
type MobileTheme = 'light' | 'dark';
type Notice = { kind: 'ok' | 'error' | 'info'; text: string } | null;
type DemoPersona = 'patient' | 'prime' | 'runner' | 'guide';

interface StoredSession {
  token: string;
  user: AuthUser;
  tokenExpiresAt?: number | null;
  demoPersona?: DemoPersona;
}

const SESSION_KEY = 'lra_mobile_session';
const TAB_SESSION_KEY = 'lra_mobile_tab_session';
const INCIDENT_KEY = 'lra_mobile_incident_id';
const LOCATION_KEY = 'lra_mobile_location';
const MOBILE_THEME_KEY = 'lra_mobile_theme';
const DEMO_ADMIN_TOKEN_KEY = 'lra_demo_admin_token';

const demoPersonas: Array<{
  key: DemoPersona;
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
      latitude: 39.90412,
      longitude: 116.40721,
      accuracyMeters: 25,
      label: '教学楼 A 座 2 层走廊',
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
      latitude: 39.90421,
      longitude: 116.40726,
      accuracyMeters: 18,
      label: '教学楼 A 座 1 层大厅',
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
      latitude: 39.90392,
      longitude: 116.40702,
      accuracyMeters: 18,
      label: '操场入口',
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
      latitude: 39.9045,
      longitude: 116.40762,
      accuracyMeters: 20,
      label: '校门岗亭',
      floor: '1F',
      source: 'mobile-demo',
    },
  },
];

const defaultLocation: GeoPoint = {
  latitude: 39.90412,
  longitude: 116.40721,
  accuracyMeters: 25,
  label: '协同演示现场',
  floor: '二层',
  source: 'mobile-demo',
};

function readDemoPersonaFromUrl(): DemoPersona | null {
  const raw = new URLSearchParams(window.location.search).get('demo')?.trim().toLowerCase();
  if (raw === 'patient' || raw === 'prime' || raw === 'runner' || raw === 'guide') {
    return raw;
  }
  return null;
}

function readIncidentIdFromUrl(): string {
  return new URLSearchParams(window.location.search).get('incidentId')?.trim() ?? '';
}

function readDemoSlotFromUrl(): string {
  const raw = new URLSearchParams(window.location.search).get('slot')?.trim().toLowerCase() || 'default';
  return raw.replace(/[^a-z0-9_-]/g, '').slice(0, 24) || 'default';
}

function tabSessionKey(): string {
  return `${TAB_SESSION_KEY}_${readDemoSlotFromUrl()}`;
}

function tabLocationKey(): string {
  return `${LOCATION_KEY}_${readDemoSlotFromUrl()}`;
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

function demoLocationFor(persona?: DemoPersona | null): GeoPoint {
  return demoPersonas.find((item) => item.key === persona)?.location ?? defaultLocation;
}

function mockHealthSignalsFor(user: AuthUser, persona?: DemoPersona): HealthSignalSummary {
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
      organization: '大学校园',
      healthCondition: '身体素质良好',
      professionIdentity: '有一定急救常识',
      profileBio: '跑动能力强，熟悉路线，可快速取送 AED。',
    },
  },
  {
    label: '清障接驳',
    values: {
      organization: '校园安保',
      healthCondition: '身体状态一般',
      professionIdentity: '安保 / 物业 / 场地协调人员',
      profileBio: '熟悉出入口、电梯与救护车通道。',
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

function roleAction(role: RoleName, state: IncidentState | null): { label: string; action: string; disabled?: boolean; hint: string } {
  if (state?.phase === 'ARCHIVED') {
    return { label: '已完成归档', action: 'WAIT', disabled: true, hint: '本轮协同流程已结束' };
  }
  if (role === 'PRIME') {
    if (!state || !isRoleJoined(state.roles.PRIME?.status)) {
      return { label: '响应核心施救', action: 'JOIN', hint: '确认接单后立即前往患者位置' };
    }
    if (!state.roles.PRIME?.status || state.roles.PRIME.status === 'ASSIGNED' || state.roles.PRIME.status === 'JOINED') {
      return { label: '开始 CPR', action: 'CPR_STARTED', hint: '打开按压节拍与 30:2 提示' };
    }
    if (hasRunnerDelivered(state) && !isAedAnalyzing(state) && !isShockDelivered(state)) {
      return { label: '启动 AED 分析', action: 'AED_ANALYSIS_STARTED', hint: '确认电极片贴附后操作' };
    }
    if (isAedAnalyzing(state)) {
      return { label: '记录一次除颤', action: 'AED_SHOCK_DELIVERED', hint: '仅在 AED 建议电击后记录' };
    }
    if (isShockDelivered(state)) {
      return { label: '二轮 AED 分析', action: 'AED_ANALYSIS_STARTED', hint: '继续 CPR 后可再次分析' };
    }
    return { label: '等待 AED 到场', action: 'WAIT', disabled: true, hint: 'AED 保障送达后才能进入分析' };
  }
  if (role === 'RUNNER') {
    if (!state || !isRoleJoined(state.roles.RUNNER?.status)) {
      return { label: '响应 AED 保障', action: 'JOIN', hint: '确认接单后前往最近 AED 点位' };
    }
    if (!hasRunnerPicked(state)) {
      return { label: '已取到 AED', action: 'AED_PICKED', hint: '到达 AED 箱后点击' };
    }
    if (!hasRunnerDelivered(state)) {
      return { label: 'AED 已送达', action: 'AED_DELIVERED', hint: '回到患者身边后点击' };
    }
    return { label: 'AED 已完成送达', action: 'WAIT', disabled: true, hint: '保持通信，协助核心施救' };
  }
  if (!state || !isRoleJoined(state.roles.GUIDE?.status)) {
    return { label: '响应清障接驳', action: 'JOIN', hint: '确认接单后疏通通道' };
  }
  if (state.roles.GUIDE?.status !== 'AMBULANCE_ARRIVED' && state.phase !== 'HANDOVER' && state.phase !== 'ARCHIVED') {
    return { label: '救护车已到场', action: 'AMBULANCE_ARRIVED', hint: '完成接驳后点击' };
  }
  if (state.phase !== 'ARCHIVED') {
    return { label: '完成交接归档', action: 'HANDOVER_COMPLETED', hint: '急救人员接管后归档' };
  }
  return { label: '已完成归档', action: 'WAIT', disabled: true, hint: '本轮协同流程已结束' };
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
    case 'Demo scenario bootstrapped':
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

  async function enterDemo(persona: DemoPersona) {
    setBusy(persona);
    setNotice(null);
    try {
      const auth = await loginDemoPersona(persona);
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
        <p className="mobile-safety-copy">仅用于协同演练、训练复盘与研究验证，不替代 120、AED 语音提示、专业医护判断或真实医疗诊断。</p>
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
              <button key={persona.key} type="button" onClick={() => enterDemo(persona.key)} disabled={Boolean(busy)}>
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
  const urlDemoPersona = useMemo(() => readDemoPersonaFromUrl(), []);
  const urlIncidentId = useMemo(() => readIncidentIdFromUrl(), []);
  const [theme, setTheme] = useState<MobileTheme>(() => readStoredTheme());
  const [session, setSession] = useState<StoredSession | null>(() => (urlDemoPersona ? null : readStoredSession()));
  const [booting, setBooting] = useState(Boolean(urlDemoPersona) || Boolean(readStoredSession()));
  const [incidentIdInput, setIncidentIdInput] = useState(() => urlIncidentId || (window.localStorage.getItem(INCIDENT_KEY) ?? ''));
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [clients, setClients] = useState<ClientInfo[]>([]);
  const [aedSites, setAedSites] = useState<AedSite[]>([]);
  const [location, setLocation] = useState<GeoPoint>(() => readStoredLocation());
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle');
  const [notice, setNotice] = useState<Notice>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());
  const [activeView, setActiveView] = useState<MobileView>('home');
  const [sosConfirming, setSosConfirming] = useState(false);
  const [showManualJoin, setShowManualJoin] = useState(false);
  const [showSceneDetails, setShowSceneDetails] = useState(false);
  const [demoAdminToken, setDemoAdminToken] = useState(getStoredDemoAdminToken);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<number | null>(null);

  const token = session?.token ?? '';
  const user = session?.user ?? null;
  const userRole = useMemo(() => findUserRole(incident, user?.userId), [incident, user?.userId]);
  const isPatient = Boolean(incident?.patientUserId && incident.patientUserId === user?.userId);
  const currentClient = useMemo(
    () => clients.find((client) => client.userId === user?.userId) ?? null,
    [clients, user?.userId],
  );
  const activeRole = userRole ?? (currentClient?.assignedRole as RoleName | null) ?? null;
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
      window.localStorage.setItem(DEMO_ADMIN_TOKEN_KEY, trimmed);
    } else {
      window.localStorage.removeItem(DEMO_ADMIN_TOKEN_KEY);
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
      if (!session && urlDemoPersona) {
        try {
          const auth = await loginDemoPersona(urlDemoPersona);
          const nextLocation = demoLocationFor(urlDemoPersona);
          const next = { token: auth.token, user: auth.user, tokenExpiresAt: auth.tokenExpiresAt, demoPersona: urlDemoPersona };
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
          setNotice({ kind: 'ok', text: `已进入${demoPersonas.find((item) => item.key === urlDemoPersona)?.label ?? '演示'}身份。` });
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
    if (!incident || incident.phase !== 'CREATED' || incident.sos?.status === 'ALERTING') {
      setSosConfirming(false);
    }
  }, [incident?.incidentId, incident?.phase, incident?.sos?.status]);

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

  async function runAction(label: string, work: () => Promise<void>, okText?: string) {
    setBusyAction(label);
    setNotice(null);
    try {
      await work();
      if (incident) {
        const next = await fetchIncident(incident.incidentId);
        setIncident((current) => mergeIncidentState(current, next));
      }
      await loadPeripheralData();
      if (okText) {
        setNotice({ kind: 'ok', text: okText });
      }
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '操作失败' });
    } finally {
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
      () => downloadExperimentPackage(session?.token, demoAdminToken, incident.incidentId),
      '事件证据包已开始下载。',
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
  const assignedUsers = clients.filter((client) => client.assignedRole);
  const action = activeRole ? roleAction(activeRole, incident) : null;
  const primeStep = activeRole === 'PRIME' ? primeNextStep(incident) : null;
  const nextActionSummary = isPatient
    ? '保持当前位置，等待协同成员到场'
    : activeRole && action
      ? `${translateRoleLabel(activeRole)}：${action.label}`
      : incident
        ? '保持在线，等待本轮任务'
        : '打开或加入事件';
  const visibleClients = clients.slice(0, 5);
  const incidentShortId = incident?.incidentId ? incident.incidentId.slice(0, 8) : null;
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

      <section className="mobile-status-strip">
        <div>
          <span className={`sync-dot ${syncStatus}`} />
          <span>{syncStatus === 'live' ? '实时在线' : syncStatus === 'connecting' ? '连接中' : syncStatus === 'reconnecting' ? '重连中' : '待连接'}</span>
        </div>
        <strong>{incident ? translatePhaseLabel(incident.phase) : '未接入事件'}</strong>
      </section>

      {incident && (
        <section className="mobile-context-strip" aria-label="当前事件状态">
          <BadgeInfo size={15} />
          <span>事件 {incidentShortId}</span>
          <span>{syncStatus === 'live' ? '实时同步中' : syncStatus === 'reconnecting' ? '正在恢复连接' : '最近状态已保留'}</span>
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
          {activeRole && action && !isPatient ? (
            <section className="mobile-emergency-panel responder">
              <div>
                {activeRole === 'PRIME' ? <HeartPulse size={28} /> : activeRole === 'RUNNER' ? <Zap size={28} /> : <Shield size={28} />}
                <p className="mobile-kicker">当前动作</p>
                <h2>{action.label}</h2>
                <p>{action.hint}</p>
              </div>
              <button className="mobile-primary-button" onClick={executeRoleAction} disabled={action.disabled || Boolean(busyAction)}>
                {busyAction ? '提交中...' : action.label}
              </button>
            </section>
          ) : (
            <section className={`mobile-emergency-panel ${isPatient ? 'patient' : ''}`}>
              <div>
                <Siren size={28} />
                <p className="mobile-kicker">高优先级</p>
                <h2>{isPatient ? '患者应急模式' : '患者 SOS'}</h2>
                <p>
                  {sosRemaining !== null
                    ? `倒计时 ${sosRemaining}s，结束后进入本轮演示分派`
                    : isPatient && incident?.phase !== 'CREATED'
                      ? '保持当前位置，等待核心施救、AED 保障和环境清障人员到场'
                    : incident?.phase === 'CREATED'
                      ? '如你是患者端，可直接触发当前事件'
                      : '当前事件已进入协同处置'}
                </p>
              </div>
              <div className="mobile-emergency-actions">
                <button
                  className={`mobile-danger-button ${sosConfirming ? 'confirming' : ''}`}
                  onClick={handlePatientSos}
                  disabled={!incident || incident.phase !== 'CREATED' || busyAction === 'sos'}
                >
                  {busyAction === 'sos' ? '启动中...' : sosConfirming ? '再次点击确认 SOS' : '启动 SOS'}
                </button>
                <button
                  className="mobile-ghost-button"
                  onClick={cancelPatientSos}
                  disabled={!incident || incident.sos?.status !== 'ALERTING' || !isPatient || busyAction === 'sosCancel'}
                >
                  取消
                </button>
              </div>
            </section>
          )}

          <section className="mobile-panel mobile-user-panel" id="top">
            <div className="mobile-user-avatar">
              <UserRound size={22} />
            </div>
            <div>
              <strong>{user.displayName}</strong>
              <p>{user.organization} · {user.professionIdentity}</p>
              <p>{formatLocationLabel(location)}</p>
              <div className="mobile-health-line">
                <HeartPulse size={14} />
                <span>{formatHealthSignalSummary(currentClient?.healthSignals)}</span>
              </div>
            </div>
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
          <button className="mobile-small-button" onClick={autoJoin} disabled={busyAction === 'autoJoin'}>
            <Radio size={14} />
            自动接单
          </button>
        </div>
        {activeRole && action ? (
          <div className={`mobile-role-card role-${activeRole.toLowerCase()}`}>
            <div className="mobile-role-title">
              {activeRole === 'PRIME' ? <HeartPulse size={24} /> : activeRole === 'RUNNER' ? <Zap size={24} /> : <Shield size={24} />}
              <div>
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
              {busyAction ? '提交中...' : action.label}
            </button>
          </div>
        ) : (
          <div className="mobile-empty-state">
            <Radio size={28} />
            <p>尚未分配到你的任务。保持在线，或在演示模式下点击自动接单。</p>
          </div>
        )}

        <div className="mobile-manual-join">
          <button
            type="button"
            className="mobile-manual-toggle"
            onClick={() => setShowManualJoin((visible) => !visible)}
            aria-expanded={showManualJoin}
          >
            <span>演示备用：手动选择角色</span>
            <ChevronDown size={16} />
          </button>
          {showManualJoin && (
            <div className="mobile-role-grid">
              {(['PRIME', 'RUNNER', 'GUIDE'] as RoleName[]).map((role) => (
                <button key={role} onClick={() => joinRole(role)} disabled={!incident || Boolean(busyAction)}>
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
                <p>{client.isPatient ? '患者端' : translateRoleLabel(client.assignedRole)} · {formatLocationLabel(client.location)}</p>
                <p className="mobile-health-copy">{client.online ? '保持在线' : '等待重连'} · {translateRoleStatus(client.assignedRole ? incident?.roles?.[client.assignedRole]?.status : null)}</p>
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
          <h2>本次演练已归档</h2>
          <p>事件日志、角色响应和 AED 取送信息已经进入事件证据包。对外展示请优先使用匿名化文件、专家复核清单和观察员记录表，本系统不宣称真实临床疗效。</p>
          <label className="mobile-token-field">
            <span>演示口令</span>
            <input
              value={demoAdminToken}
              onChange={(event) => setDemoAdminToken(event.target.value)}
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
