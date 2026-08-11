import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type {
  AedSite,
  ClientInfo,
  DispatchMeta,
  HealthDetail,
  HealthSignalSummary,
  IncidentState,
  RoleName,
} from '@/shared/types';
import {
  buildAuthHeaders,
  builddemoAdminHeaders,
  explainResponseError,
  getApiBase,
  getStoreddemoAdminToken,
  getWsBase,
} from '@/shared/api';
import {
  hasGuideCompleted,
  hasPrimeStarted,
  hasRunnerDelivered,
  hasRunnerPicked,
  isAedAnalyzing,
  isRoleJoined,
  isShockDelivered,
  mergeIncidentState,
  roleNames,
  translateHealthAuthorization,
  translateHealthSource,
  translatePhaseLabel,
  translateRoleLabel,
  translateRoleStatus,
} from '@/shared/domain';
import {
  computeSpotlightDirective,
  parseServerSpotlight,
  spotlightTargetLabel,
  type SpotlightDirective,
  type SpotlightTarget,
} from '@/shared/spotlight';
import { copyTextToClipboard, downloadJson, downloadResponseBlob, downloadText } from '../download';
import {
  buildDemoFlowSteps,
  buildDispatchStream,
  describeClientMission,
  formatElapsed,
  formatPhaseLabel,
} from '../helpers';
import type {
  AdminSession,
  AuditEvent,
  DemoFlowStep,
  DemoShareLink,
  LogEntry,
  PackageDownloadInfo,
  ReadinessItem,
} from '../types';

const ADMIN_SESSION_KEY = 'lra_admin_session';

export interface DashboardActions {
  loginAdmin: (phone: string, password: string) => Promise<void>;
  logoutAdmin: () => Promise<void>;
  createIncident: () => Promise<void>;
  loadCurrentIncident: () => Promise<void>;
  loadClients: () => Promise<void>;
  loadAedSites: () => Promise<void>;
  loadAuditEvents: () => Promise<void>;
  bootstrapDemo: () => Promise<void>;
  designatePatient: (userId: string) => Promise<void>;
  resetCurrentIncident: () => Promise<void>;
  exportExperiment: () => Promise<void>;
  exportExperimentPackage: () => Promise<void>;
  copyLastPackageSha: () => Promise<void>;
  exportPreflightReport: () => void;
  openMobileDemoStage: () => void;
  openAllMobileTerminals: () => Promise<void>;
  openDemoLink: (url: string, key: string) => void;
  copyDemoLink: (key: string, text: string) => Promise<boolean>;
  setdemoAdminToken: (token: string) => void;
  setAdminPhone: (phone: string) => void;
  setAdminPassword: (password: string) => void;
  setManualFocus: (target: SpotlightTarget | null) => void;
  joinRole: (role: RoleName) => Promise<void>;
  postRoleAction: (action: string, role: RoleName) => Promise<void>;
}

export interface DashboardViewModel {
  incidentId: string | null;
  incidentState: IncidentState | null;
  clients: ClientInfo[];
  aedSites: AedSite[];
  dispatchMeta: DispatchMeta | null;
  healthDetail: HealthDetail | null;
  auditEvents: AuditEvent[];
  showAuditPanel: boolean;
  setShowAuditPanel: (visible: boolean) => void;
  wsConnected: boolean;
  wsError: string | null;
  errorMessage: string | null;
  successMessage: string | null;
  lastPackageDownload: PackageDownloadInfo | null;
  demoAdminToken: string;
  adminSession: AdminSession | null;
  adminPhone: string;
  adminPassword: string;
  adminLoginBusy: boolean;
  liveNowMs: number;
  elapsedSeconds: number;
  phaseLabel: string;
  responderCount: number;
  primeActive: boolean;
  runnerActive: boolean;
  guideActive: boolean;
  primeJoined: boolean;
  runnerJoined: boolean;
  guideJoined: boolean;
  archived: boolean;
  logs: LogEntry[];
  dispatchStream: ReturnType<typeof buildDispatchStream>;
  demoFlowSteps: DemoFlowStep[];
  readinessItems: ReadinessItem[];
  readinessReady: boolean;
  visibleReadinessWarnings: string[];
  demoShareLinks: DemoShareLink[];
  spotlight: SpotlightDirective | null;
  spotlightTimeline: SpotlightDirective[];
  manualFocus: SpotlightTarget | null;
  visibleAedSites: AedSite[];
  getClientDisplayName: (userId?: string | null) => string;
  describeClientMission: (client: ClientInfo) => string;
  actions: DashboardActions;
}

function getStoredAdminSession(): AdminSession | null {
  if (typeof window === 'undefined') {
    return null;
  }
  try {
    const raw = window.localStorage.getItem(ADMIN_SESSION_KEY);
    return raw ? (JSON.parse(raw) as AdminSession) : null;
  } catch {
    return null;
  }
}

function getReadinessValue(value: number | null | undefined): string {
  if (value === undefined || value === null) {
    return '--';
  }
  return `${Math.round(value)}%`;
}

export function useDashboard(): DashboardViewModel {
  const [incidentId, setIncidentId] = useState<string | null>(() => {
    if (typeof window === 'undefined') {
      return null;
    }
    return new URLSearchParams(window.location.search).get('incidentId');
  });
  const [incidentState, setIncidentState] = useState<IncidentState | null>(null);
  const [clients, setClients] = useState<ClientInfo[]>([]);
  const [aedSites, setAedSites] = useState<AedSite[]>([]);
  const [dispatchMeta, setDispatchMeta] = useState<DispatchMeta | null>(null);
  const [healthDetail, setHealthDetail] = useState<HealthDetail | null>(null);
  const [auditEvents, setAuditEvents] = useState<AuditEvent[]>([]);
  const [showAuditPanel, setShowAuditPanel] = useState(false);
  const [demoAdminToken, setdemoAdminToken] = useState(getStoreddemoAdminToken);
  const [adminSession, setAdminSession] = useState<AdminSession | null>(getStoredAdminSession);
  const [adminPhone, setAdminPhone] = useState('');
  const [adminPassword, setAdminPassword] = useState('');
  const [adminLoginBusy, setAdminLoginBusy] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [lastPackageDownload, setLastPackageDownload] = useState<PackageDownloadInfo | null>(null);
  const [liveNowMs, setLiveNowMs] = useState(Date.now());
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [copiedLinkKey, setCopiedLinkKey] = useState<string | null>(null);
  const [manualFocus, setManualFocus] = useState<SpotlightTarget | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const manualCloseRef = useRef(false);
  const copyLinkTimeoutRef = useRef<number | null>(null);
  const prevStateRef = useRef<IncidentState | null>(null);

  const getClientDisplayName = useCallback(
    (userId?: string | null) => clients.find((client) => client.userId === userId)?.displayName ?? userId ?? '未分配',
    [clients],
  );

  const phaseLabel = formatPhaseLabel(incidentState?.phase);
  const responderCount = incidentState
    ? Object.values(incidentState.roles).filter((role) => isRoleJoined(role.status)).length
    : 0;
  const primeActive = isRoleJoined(incidentState?.roles?.PRIME?.status);
  const runnerActive = isRoleJoined(incidentState?.roles?.RUNNER?.status);
  const guideActive = isRoleJoined(incidentState?.roles?.GUIDE?.status);
  const primeJoined = isRoleJoined(incidentState?.roles?.PRIME?.status);
  const runnerJoined = isRoleJoined(incidentState?.roles?.RUNNER?.status);
  const guideJoined = isRoleJoined(incidentState?.roles?.GUIDE?.status);
  const archived = incidentState?.phase === 'ARCHIVED';
  const incidentStartTs = incidentState?.logs?.[0]?.ts ?? null;
  const logs = useMemo(() => {
    return (incidentState?.logs ?? [])
      .map((log, index) => ({
        id: `${log.ts}-${index}`,
        time: new Date(log.ts).toLocaleTimeString('zh-CN', { hour12: false }),
        source: '服务端',
        message: log.msg,
        type: (log.msg.toLowerCase().includes('sos') ||
        log.msg.toLowerCase().includes('alert') ||
        log.msg.toLowerCase().includes('shock')
          ? 'alert'
          : log.msg.toLowerCase().includes('delivered') ||
              log.msg.toLowerCase().includes('completed') ||
              log.msg.toLowerCase().includes('handover') ||
              log.msg.toLowerCase().includes('assigned')
            ? 'success'
            : 'info') as 'alert' | 'success' | 'info',
      }))
      .reverse();
  }, [incidentState]);

  const dispatchStream = useMemo(
    () => buildDispatchStream(incidentState, clients, dispatchMeta, liveNowMs),
    [incidentState, clients, dispatchMeta, liveNowMs],
  );
  const demoFlowSteps = useMemo(() => buildDemoFlowSteps(incidentState), [incidentState]);

  const visibleAedSites = incidentState?.aedSites?.length ? incidentState.aedSites : aedSites;

  const healthDetailExt = healthDetail as HealthDetail & {
    demoReadiness?: {
      ready?: boolean;
      clientCount?: number;
      availableAedSiteCount?: number;
      locationCoveragePercent?: number | null;
      healthCoveragePercent?: number | null;
      exportReady?: boolean;
      warnings?: string[];
    };
    auth?: { adminAccountAuthEnabled?: boolean };
    demoAdminAuthEnabled?: boolean;
  };
  const demoReadiness = healthDetailExt?.demoReadiness;
  const readinessItems: ReadinessItem[] = [
    {
      label: '终端',
      value: `${demoReadiness?.clientCount ?? clients.length}/4`,
      ready: (demoReadiness?.clientCount ?? clients.length) >= 4,
    },
    {
      label: 'AED',
      value: `${demoReadiness?.availableAedSiteCount ?? visibleAedSites.length}`,
      ready: (demoReadiness?.availableAedSiteCount ?? visibleAedSites.length) >= 1,
    },
    {
      label: '定位',
      value: getReadinessValue(demoReadiness?.locationCoveragePercent),
      ready: (demoReadiness?.locationCoveragePercent ?? 0) >= 100,
    },
    {
      label: '健康摘要',
      value: getReadinessValue(demoReadiness?.healthCoveragePercent),
      ready: (demoReadiness?.healthCoveragePercent ?? 0) >= 100,
    },
    {
      label: '证据导出',
      value: demoReadiness?.exportReady ? '可用' : '待事件日志',
      ready: Boolean(demoReadiness?.exportReady),
    },
  ];
  const adminAccountEnabled = Boolean(healthDetailExt?.auth?.adminAccountAuthEnabled);
  const adminSessionReady = Boolean(adminSession?.token && adminSession.user.privileges?.includes('admin'));
  const demoAdminRequired = Boolean(healthDetailExt?.demoAdminAuthEnabled || adminAccountEnabled);
  const demoAdminReady = !demoAdminRequired || adminSessionReady || demoAdminToken.trim().length > 0;
  const readinessWarnings = demoReadiness?.warnings ?? [];
  const visibleReadinessWarnings = [
    ...readinessWarnings,
    ...(!demoAdminReady ? ['管理权限未就绪：请先登录正式管理员账号或填写演示口令。'] : []),
  ];
  const readinessReady = Boolean(demoReadiness?.ready && demoAdminReady);

  const buildDemoUrl = useCallback(
    (path: '/mobile' | '/mobile-demo', params?: Record<string, string>): string => {
      if (typeof window === 'undefined') {
        return path;
      }
      const url = new URL(path, window.location.origin);
      if (incidentId) {
        url.searchParams.set('incidentId', incidentId);
      }
      Object.entries(params ?? {}).forEach(([key, value]) => {
        if (value) {
          url.searchParams.set(key, value);
        }
      });
      return url.toString();
    },
    [incidentId],
  );

  const mobileDemoEntries = [
    { key: 'patient', label: '患者端', caption: '触发 SOS，观察系统分派', url: '' },
    { key: 'prime', label: '核心施救', caption: '接单、CPR、AED 分析', url: '' },
    { key: 'runner', label: 'AED 保障', caption: '取 AED 并送达患者', url: '' },
    { key: 'guide', label: '环境清障', caption: '疏通通道，接引救护车', url: '' },
  ];
  const demoShareLinks: DemoShareLink[] = [
    {
      key: 'stage',
      label: '4端导播台',
      caption: '一屏预览患者与三类任务端',
      url: buildDemoUrl('/mobile-demo'),
    },
    ...mobileDemoEntries.map((entry) => ({
      ...entry,
      url: buildDemoUrl('/mobile', { demo: entry.key, slot: entry.key }),
    })),
  ];

  // ---- 聚焦引擎 ----
  const spotlight = useMemo(() => {
    const serverDirective = parseServerSpotlight((incidentState as { spotlight?: unknown } | null)?.spotlight);
    const computed = computeSpotlightDirective(incidentState, serverDirective);
    if (!manualFocus) {
      return computed;
    }
    // 患者 SOS 危急告警始终优先；其余情况允许手动聚焦
    if (computed?.severity === 'critical') {
      return computed;
    }
    return {
      id: `manual-${manualFocus}`,
      target: manualFocus,
      severity: 'active' as const,
      title: spotlightTargetLabel(manualFocus),
      message: '已手动聚焦该终端，点击其他条目或重置可切换',
      source: 'STATE_MACHINE' as const,
      ts: Date.now(),
    };
  }, [incidentState, manualFocus]);
  const spotlightTimeline = useMemo(() => {
    const timeline: SpotlightDirective[] = [];
    if (incidentState?.sos?.status === 'ALERTING') {
      timeline.push({
        id: 'patient-sos',
        target: 'PATIENT',
        severity: 'critical',
        title: '患者端告警',
        message: '疑似心脏骤停，SOS 已触发。',
        source: 'STATE_MACHINE',
        ts: incidentState.sos.startTs ?? Date.now(),
      });
    }
    const logs = [...(incidentState?.logs ?? [])].sort((a, b) => a.ts - b.ts);
    for (const log of logs) {
      const lower = log.msg.toLowerCase();
      const rule = [
        ['shock', 'PRIME', '除颤完成', '核心施救端完成一次 AED 除颤。'],
        ['analysis', 'PRIME', 'AED 分析中', '核心施救端正在执行 AED 心律分析。'],
        ['aed delivered', 'RUNNER', 'AED 已送达', 'AED 保障端已送达设备。'],
        ['aed picked', 'RUNNER', 'AED 已取到', '取送者正在回送 AED。'],
        ['cpr started', 'PRIME', 'CPR 已启动', '核心施救端开始胸外按压。'],
        ['ambulance arrived', 'GUIDE', '救护车已到场', '清障接驳端已引导救护车。'],
        ['handover', 'GUIDE', '完成交接', '专业急救力量已接管。'],
      ] as Array<[string, SpotlightDirective['target'], string, string]>;
      for (const [keyword, target, title, message] of rule) {
        if (lower.includes(keyword)) {
          timeline.push({
            id: `tl-${log.ts}-${keyword}`,
            target,
            severity: 'active',
            title,
            message,
            source: 'STATE_MACHINE',
            ts: log.ts,
          });
          break;
        }
      }
    }
    return timeline.slice(-10).reverse();
  }, [incidentState]);

  // ---- 基础加载 ----
  const loadHealthDetail = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/health/detail`);
      if (!res.ok) {
        return;
      }
      const data = (await res.json()) as HealthDetail;
      setHealthDetail(data);
    } catch {
      setHealthDetail(null);
    }
  }, []);

  const loadClients = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/clients`);
      if (!res.ok) {
        return;
      }
      const data = (await res.json()) as { clients?: ClientInfo[] };
      setClients(Array.isArray(data?.clients) ? data.clients : []);
    } catch {
      // best-effort
    }
  }, []);

  const loadAedSites = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/aed-sites`);
      if (!res.ok) {
        return;
      }
      const data = (await res.json()) as { aedSites?: AedSite[] };
      setAedSites(Array.isArray(data?.aedSites) ? data.aedSites : []);
    } catch {
      // best-effort
    }
  }, []);

  const loadDispatchMeta = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/dispatch/meta`);
      if (!res.ok) {
        return;
      }
      setDispatchMeta((await res.json()) as DispatchMeta);
    } catch {
      // best-effort
    }
  }, []);

  const loadCurrentIncident = useCallback(async () => {
    try {
      const res = await fetch(`${getApiBase()}/incidents/current`);
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '加载当前事件失败'));
      }
      const data = (await res.json()) as IncidentState;
      if (data?.incidentId) {
        setIncidentId(data.incidentId);
        setIncidentState((current) => mergeIncidentState(current, data));
        if (typeof window !== 'undefined') {
          const url = new URL(window.location.href);
          url.searchParams.set('incidentId', data.incidentId);
          window.history.replaceState(null, '', url.toString());
        }
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '加载当前事件失败');
    }
  }, []);

  // ---- WebSocket ----
  const connectWs = useCallback((id: string) => {
    if (!id) {
      return;
    }
    manualCloseRef.current = false;
    const previousWs = wsRef.current;
    wsRef.current = null;
    previousWs?.close();
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    setWsError(null);
    const ws = new WebSocket(`${getWsBase()}?incidentId=${encodeURIComponent(id)}`);
    wsRef.current = ws;

    ws.onopen = () => {
      if (wsRef.current !== ws) {
        return;
      }
      reconnectAttemptRef.current = 0;
      setWsConnected(true);
      setWsError(null);
    };
    ws.onclose = () => {
      if (wsRef.current !== ws) {
        return;
      }
      setWsConnected(false);
      if (!manualCloseRef.current && id) {
        const attempt = reconnectAttemptRef.current;
        const delay = Math.min(10000, 1000 * Math.pow(2, attempt));
        reconnectAttemptRef.current += 1;
        reconnectTimeoutRef.current = window.setTimeout(() => connectWs(id), delay);
      }
    };
    ws.onerror = () => {
      if (wsRef.current === ws) {
        setWsError('WebSocket 连接异常');
      }
    };
    ws.onmessage = (event) => {
      if (wsRef.current !== ws) {
        return;
      }
      try {
        const msg = JSON.parse(event.data) as { type?: string; payload?: IncidentState };
        if (msg?.type === 'STATE' && msg.payload?.incidentId === id) {
          prevStateRef.current = incidentState;
          setIncidentState((current) => mergeIncidentState(current, msg.payload as IncidentState));
        } else if (msg?.type === 'ERROR') {
          setWsError(String(msg.payload ?? 'WebSocket error'));
        }
      } catch {
        setWsError('Invalid WebSocket message');
      }
    };
  }, []);

  useEffect(() => {
    if (!incidentId) {
      return;
    }
    manualCloseRef.current = false;
    connectWs(incidentId);
    return () => {
      manualCloseRef.current = true;
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      const ws = wsRef.current;
      wsRef.current = null;
      ws?.close();
    };
  }, [incidentId, connectWs]);

  // ---- 时钟 ----
  useEffect(() => {
    const interval = window.setInterval(() => setLiveNowMs(Date.now()), 500);
    return () => window.clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!incidentStartTs) {
      setElapsedSeconds(0);
      return;
    }
    const updateElapsed = () => {
      setElapsedSeconds(Math.max(0, Math.floor((Date.now() - incidentStartTs) / 1000)));
    };
    updateElapsed();
    const interval = window.setInterval(updateElapsed, 1000);
    return () => window.clearInterval(interval);
  }, [incidentStartTs]);

  // ---- 轮询 ----
  useEffect(() => {
    void loadHealthDetail();
    void loadClients();
    void loadAedSites();
    void loadDispatchMeta();
    void loadCurrentIncident();
    const clientTimer = window.setInterval(() => void loadClients(), 3000);
    const aedTimer = window.setInterval(() => void loadAedSites(), 15000);
    return () => {
      window.clearInterval(clientTimer);
      window.clearInterval(aedTimer);
    };
  }, [loadHealthDetail, loadClients, loadAedSites, loadDispatchMeta, loadCurrentIncident]);

  // ---- 管理登录 ----
  const loginAdmin = useCallback(async (phone: string, password: string) => {
    if (!phone || !password) {
      setErrorMessage('请输入管理员手机号和密码');
      return;
    }
    try {
      setAdminLoginBusy(true);
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, password }),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '管理员登录失败'));
      }
      const data = (await res.json()) as {
        token: string;
        user: { userId: string; displayName: string; phone: string; privileges?: string[] };
        tokenExpiresAt?: number | null;
      };
      if (!data.user.privileges?.includes('admin')) {
        throw new Error('管理员登录失败：该账号不在管理员白名单');
      }
      const session: AdminSession = {
        token: data.token,
        user: data.user,
        tokenExpiresAt: data.tokenExpiresAt ?? null,
      };
      setAdminSession(session);
      window.localStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify(session));
      setAdminPassword('');
    } catch (error) {
      setAdminSession(null);
      setErrorMessage(error instanceof Error ? error.message : '管理员登录失败');
    } finally {
      setAdminLoginBusy(false);
    }
  }, []);

  const logoutAdmin = useCallback(async () => {
    const token = adminSession?.token;
    setAdminSession(null);
    window.localStorage.removeItem(ADMIN_SESSION_KEY);
    if (!token) {
      return;
    }
    try {
      await fetch(`${getApiBase()}/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch {
      // local logout still succeeds
    }
  }, [adminSession]);

  const buildAdminHeaders = useCallback(
    (extra?: HeadersInit): HeadersInit => {
      const headers = builddemoAdminHeaders(demoAdminToken, buildAuthHeaders(adminSession?.token, extra));
      return headers;
    },
    [demoAdminToken, adminSession],
  );

  // ---- 事件操作 ----
  const createIncident = useCallback(async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/incidents`, {
        method: 'POST',
        headers: buildAdminHeaders(),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '创建事件失败'));
      }
      const data = (await res.json()) as { incidentId?: string };
      if (data?.incidentId) {
        setIncidentId(data.incidentId);
        if (typeof window !== 'undefined') {
          const url = new URL(window.location.href);
          url.searchParams.set('incidentId', data.incidentId);
          window.history.replaceState(null, '', url.toString());
        }
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '创建事件失败');
    }
  }, [buildAdminHeaders]);

  const bootstrapDemo = useCallback(async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/demo/bootstrap`, {
        method: 'POST',
        headers: buildAdminHeaders(),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '初始化演示场景失败'));
      }
      const data = (await res.json()) as {
        incidentId?: string;
        clients?: ClientInfo[];
        aedSites?: AedSite[];
      };
      if (data?.incidentId) {
        setIncidentId(data.incidentId);
        if (typeof window !== 'undefined') {
          const url = new URL(window.location.href);
          url.searchParams.set('incidentId', data.incidentId);
          window.history.replaceState(null, '', url.toString());
        }
      }
      setClients(Array.isArray(data?.clients) ? data.clients : []);
      setAedSites(Array.isArray(data?.aedSites) ? data.aedSites : []);
      await loadCurrentIncident();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '初始化演示场景失败');
    }
  }, [buildAdminHeaders, loadCurrentIncident]);

  const designatePatient = useCallback(
    async (patientUserId: string) => {
      try {
        setErrorMessage(null);
        const res = await fetch(`${getApiBase()}/incidents/current/designate_patient`, {
          method: 'POST',
          headers: buildAdminHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify({ patientUserId }),
        });
        if (!res.ok) {
          throw new Error(await explainResponseError(res, '标记患者告警失败'));
        }
        await loadCurrentIncident();
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : '标记患者告警失败');
      }
    },
    [buildAdminHeaders, loadCurrentIncident],
  );

  const joinRole = useCallback(
    async (role: RoleName) => {
      if (!incidentId) {
        setErrorMessage('请先初始化演示场景');
        return;
      }
      try {
        setErrorMessage(null);
        const res = await fetch(`${getApiBase()}/incidents/${encodeURIComponent(incidentId)}/join`, {
          method: 'POST',
          headers: buildAdminHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify({ role, userId: `demo-${role.toLowerCase()}` }),
        });
        if (!res.ok) {
          throw new Error(await explainResponseError(res, '响应任务失败'));
        }
        await loadCurrentIncident();
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : '响应任务失败');
      }
    },
    [incidentId, buildAdminHeaders, loadCurrentIncident],
  );

  const postRoleAction = useCallback(
    async (action: string, role: RoleName) => {
      if (!incidentId) {
        setErrorMessage('请先初始化演示场景');
        return;
      }
      try {
        setErrorMessage(null);
        const res = await fetch(`${getApiBase()}/incidents/${encodeURIComponent(incidentId)}/actions`, {
          method: 'POST',
          headers: buildAdminHeaders({ 'Content-Type': 'application/json' }),
          body: JSON.stringify({ action, userId: `demo-${role.toLowerCase()}` }),
        });
        if (!res.ok) {
          throw new Error(await explainResponseError(res, '提交动作失败'));
        }
        await loadCurrentIncident();
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : '提交动作失败');
      }
    },
    [incidentId, buildAdminHeaders, loadCurrentIncident],
  );

  const resetCurrentIncident = useCallback(async () => {
    try {
      setErrorMessage(null);
      setSuccessMessage(null);
      const res = await fetch(`${getApiBase()}/incidents/current/reset`, {
        method: 'POST',
        headers: buildAdminHeaders(),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '重置当前事件失败'));
      }
      await loadCurrentIncident();
      await loadClients();
      await loadAedSites();
      setSuccessMessage('当前事件已重置，回到监测状态');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '重置当前事件失败');
    }
  }, [buildAdminHeaders, loadCurrentIncident, loadClients, loadAedSites]);

  const loadAuditEvents = useCallback(async () => {
    try {
      setErrorMessage(null);
      const res = await fetch(`${getApiBase()}/audit/events?limit=30`, {
        headers: buildAdminHeaders(),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '加载审计日志失败'));
      }
      const data = (await res.json()) as { events?: AuditEvent[] };
      setAuditEvents(Array.isArray(data?.events) ? data.events : []);
      setShowAuditPanel(true);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '加载审计日志失败');
    }
  }, [buildAdminHeaders]);

  // ---- 导出 ----
  const exportExperiment = useCallback(async () => {
    try {
      setErrorMessage(null);
      setSuccessMessage(null);
      const res = await fetch(`${getApiBase()}/experiments/current/export`, {
        headers: buildAdminHeaders(),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '导出实验数据失败'));
      }
      const data = (await res.json()) as { incidentId?: string };
      downloadJson(`lifereflex-experiment-${data?.incidentId ?? 'current'}.json`, data);
      setSuccessMessage(`实验数据已下载：lifereflex-experiment-${data?.incidentId ?? 'current'}.json`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '导出实验数据失败');
    }
  }, [buildAdminHeaders]);

  const exportExperimentPackage = useCallback(async () => {
    try {
      setErrorMessage(null);
      setSuccessMessage(null);
      setLastPackageDownload(null);
      const targetIncidentId = incidentState?.incidentId ?? incidentId;
      const packagePath = targetIncidentId
        ? `/experiments/${encodeURIComponent(targetIncidentId)}/package`
        : '/experiments/current/package';
      const res = await fetch(`${getApiBase()}${packagePath}`, {
        headers: buildAdminHeaders(),
      });
      if (!res.ok) {
        throw new Error(await explainResponseError(res, '导出事件证据包失败'));
      }
      const download = await downloadResponseBlob(
        res,
        `lifereflex-experiment-${incidentId ?? 'current'}.zip`,
      );
      setLastPackageDownload(download);
      setSuccessMessage(
        download.packageSha256
          ? `证据包已下载：${download.filename}；SHA-256 ${download.packageSha256}`
          : `证据包已下载：${download.filename}。未读取到 SHA-256 响应头，请以 ZIP 内 manifest 为准。`,
      );
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : '导出事件证据包失败');
    }
  }, [buildAdminHeaders, incidentId, incidentState]);

  const copyLastPackageSha = useCallback(async () => {
    const sha = lastPackageDownload?.packageSha256;
    if (!sha) {
      return;
    }
    const ok = await copyTextToClipboard(sha);
    if (!ok) {
      setErrorMessage('复制 SHA-256 失败，请手动复制下载提示中的哈希值。');
      return;
    }
    setErrorMessage(null);
    setSuccessMessage(`已复制证据包 SHA-256：${sha}`);
  }, [lastPackageDownload]);

  const exportPreflightReport = useCallback(() => {
    const generatedAt = new Date();
    const targetIncidentId = incidentState?.incidentId ?? incidentId ?? '未创建';
    const currentPhase = translatePhaseLabel(incidentState?.phase);
    const statusLabel = readinessReady ? '准备就绪' : '仍需确认';
    const warningList = [...visibleReadinessWarnings, ...(wsError ? [`实时连接异常：${wsError}`] : [])];
    const roleRows = roleNames.map((role) => {
      const roleState = incidentState?.roles?.[role];
      return [
        translateRoleLabel(role),
        getClientDisplayName(roleState?.userId),
        translateRoleStatus(roleState?.status),
      ];
    });
    const clientRows = clients.map((client) => [
      client.displayName,
      client.isPatient ? '患者端' : translateRoleLabel(client.assignedRole),
      client.deviceType || '移动终端',
      client.online ? '在线' : '离线',
      client.location?.label ?? '未上报位置',
      `${translateHealthSource(client.healthSignals?.source)} / ${translateHealthAuthorization(
        client.healthSignals?.authorizationStatus,
      )}`,
    ]);
    const aedRows = visibleAedSites.map((site) => [
      site.name,
      site.status,
      site.location?.label ?? '--',
      site.accessNotes || '无补充说明',
    ]);
    const shareLinkRows = demoShareLinks.map((link) => [link.label, link.url]);
    const table = (headers: string[], rows: Array<Array<string | number | boolean | null | undefined>>) => {
      const normalize = (value: string | number | boolean | null | undefined) =>
        String(value ?? '--').replace(/\|/g, '/');
      return [
        `| ${headers.map(normalize).join(' | ')} |`,
        `| ${headers.map(() => '---').join(' | ')} |`,
        ...rows.map((row) => `| ${row.map(normalize).join(' | ')} |`),
      ].join('\n');
    };
    const lines = [
      '# 生命反射弧演示自检报告',
      '',
      `- 生成时间：${generatedAt.toLocaleString('zh-CN', { hour12: false })}`,
      `- 事件编号：${targetIncidentId}`,
      `- 当前阶段：${currentPhase}`,
      `- 总体状态：${statusLabel}`,
      '- 安全边界：本报告仅用于协同演示、训练复盘和低成本预实验，不构成临床疗效证明。',
      '',
      '## 一、准备度检查',
      '',
      table(
        ['检查项', '当前值', '状态'],
        readinessItems.map((item) => [item.label, item.value, item.ready ? '通过' : '待确认']),
      ),
      '',
      warningList.length
        ? ['## 二、待确认项', '', ...warningList.map((item) => `- ${item}`)].join('\n')
        : '## 二、待确认项\n\n- 暂无阻塞项。正式演示前仍建议完成真机走查。',
      '',
      '## 三、角色任务单',
      '',
      table(['角色', '终端', '状态'], roleRows),
      '',
      '## 四、在线终端',
      '',
      table(['终端', '角色', '设备', '在线', '位置', '健康数据'], clientRows),
      '',
      '## 五、AED 点位',
      '',
      table(['点位', '状态', '位置', '取用说明'], aedRows),
      '',
      '## 六、演示入口',
      '',
      table(['入口', '地址'], shareLinkRows),
      '',
      '> 本报告自动生成，用于赛前自检与团队交接。',
    ];
    downloadText(`lifereflex-preflight-${targetIncidentId}.md`, lines.join('\n'));
    setSuccessMessage(`自检报告已导出：lifereflex-preflight-${targetIncidentId}.md`);
  }, [
    incidentState,
    incidentId,
    readinessReady,
    visibleReadinessWarnings,
    wsError,
    getClientDisplayName,
    clients,
    visibleAedSites,
    demoShareLinks,
    readinessItems,
  ]);

  // ---- 演示入口 ----
  const openMobileDemoStage = useCallback(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const url = new URL('/mobile-demo', window.location.origin);
    if (incidentId) {
      url.searchParams.set('incidentId', incidentId);
    }
    const opened = window.open(url.toString(), '_blank');
    if (!opened) {
      setErrorMessage('浏览器拦截了 4端演示台，请允许本站弹出窗口后重试。');
      return;
    }
    setErrorMessage(null);
  }, [incidentId]);

  const openDemoLink = useCallback(
    (url: string, key: string) => {
      const opened = window.open(url, key);
      if (!opened) {
        setErrorMessage(`浏览器拦截了「${key}」弹窗，请允许本站弹窗后重试。`);
        return;
      }
      setErrorMessage(null);
    },
    [],
  );

  const openAllMobileTerminals = useCallback(async () => {
    if (typeof window === 'undefined') {
      return;
    }
    const links = demoShareLinks.filter((link) => link.key !== 'stage');
    let blocked = false;
    links.forEach((link) => {
      const opened = window.open(link.url, link.key);
      if (!opened) {
        blocked = true;
      }
    });
    if (blocked) {
      setErrorMessage('浏览器拦截了部分终端窗口，请允许本站弹窗后重试。');
      return;
    }
    setErrorMessage(null);
  }, [demoShareLinks]);

  const copyDemoLink = useCallback(
    async (key: string, text: string): Promise<boolean> => {
      const ok = await copyTextToClipboard(text);
      if (ok) {
        setCopiedLinkKey(key);
        if (copyLinkTimeoutRef.current) {
          window.clearTimeout(copyLinkTimeoutRef.current);
        }
        copyLinkTimeoutRef.current = window.setTimeout(() => setCopiedLinkKey(null), 2000);
      }
      return ok;
    },
    [],
  );

  const actions: DashboardActions = {
    loginAdmin,
    logoutAdmin,
    createIncident,
    loadCurrentIncident,
    loadClients,
    loadAedSites,
    loadAuditEvents,
    bootstrapDemo,
    designatePatient,
    resetCurrentIncident,
    exportExperiment,
    exportExperimentPackage,
    copyLastPackageSha,
    exportPreflightReport,
    openMobileDemoStage,
    openAllMobileTerminals,
    openDemoLink,
    copyDemoLink,
    setdemoAdminToken,
    setAdminPhone,
    setAdminPassword,
    setManualFocus,
    joinRole,
    postRoleAction,
  };

  return {
    incidentId,
    incidentState,
    clients,
    aedSites,
    dispatchMeta,
    healthDetail,
    auditEvents,
    showAuditPanel,
    setShowAuditPanel,
    wsConnected,
    wsError,
    errorMessage,
    successMessage,
    lastPackageDownload,
    demoAdminToken,
    adminSession,
    adminPhone,
    adminPassword,
    adminLoginBusy,
    liveNowMs,
    elapsedSeconds,
    phaseLabel,
    responderCount,
    primeActive,
    runnerActive,
    guideActive,
    primeJoined,
    runnerJoined,
    guideJoined,
    archived,
    logs,
    dispatchStream,
    demoFlowSteps,
    readinessItems,
    readinessReady,
    visibleReadinessWarnings,
    demoShareLinks,
    spotlight,
    spotlightTimeline,
    manualFocus,
    visibleAedSites,
    getClientDisplayName,
    describeClientMission: (client) => describeClientMission(client, incidentState),
    actions,
  };
}

export function useClockText(): { time: string; date: string } {
  const [now, setNow] = useState(() => new Date());
  useEffect(() => {
    const timer = window.setInterval(() => setNow(new Date()), 1000);
    return () => window.clearInterval(timer);
  }, []);
  return {
    time: now.toLocaleTimeString('zh-CN', { hour12: false }),
    date: `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} ${
      ['周日', '周一', '周二', '周三', '周四', '周五', '周六'][now.getDay()]
    }`,
  };
}

export { formatElapsed, formatPhaseLabel };
