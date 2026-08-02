import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  fetchAedSites,
  fetchClients,
  fetchCurrentIncident,
  fetchIncident,
  fetchMe,
  joinIncident,
  logindemoPersona,
  loginAccount,
  openIncidentSocket,
  patientSosCancel,
  patientSosStart,
  postIncidentAction,
  registerAccount,
  registerClient,
  updateClientHealth,
  updateClientLocation,
} from './lib/api';
import {
  findUserRole,
  formatLocationLabel,
  mergeIncidentState,
  translatePhaseLabel,
} from './lib/domain';
import type { AedSite, ClientInfo, GeoPoint, IncidentState, RoleName } from './lib/types';
import {
  clearSession,
  readStoredLocation,
  readStoredSession,
  readStoredTheme,
  saveLocation,
  saveSession,
  saveTheme,
  type MobileTheme,
  type StoredSession,
} from './lib/session';
import {
  demoLocationLabel,
  demoPersonaInfo,
  healthStatItems,
  isIncidentReadyForResponderTask,
  mockHealthSignalsFor,
  primeNextStep,
  rescueProgress,
  roleAction,
  roleLabelFor,
} from './lib/rescue';
import { AuthPanel } from './components/AuthPanel';
import { PatientScreen } from './components/PatientScreen';
import { ResponderScreen } from './components/ResponderScreen';
import './styles/index.css';

type SyncStatus = 'idle' | 'connecting' | 'live' | 'reconnecting' | 'offline';

const urldemoPersona = (() => {
  if (typeof window === 'undefined') return null;
  const raw = new URLSearchParams(window.location.search).get('demo');
  const valid = ['patient', 'prime', 'runner', 'guide'];
  return raw && valid.includes(raw) ? (raw as StoredSession['demoPersona']) : null;
})();

const urlIncidentId = (() => {
  if (typeof window === 'undefined') return null;
  return new URLSearchParams(window.location.search).get('incidentId');
})();

export default function App() {
  const [theme, setTheme] = useState<MobileTheme>(readStoredTheme);
  const [session, setSession] = useState<StoredSession | null>(() =>
    urldemoPersona ? null : readStoredSession(),
  );
  const [booting, setBooting] = useState<boolean>(Boolean(urldemoPersona || readStoredSession()));
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [clients, setClients] = useState<ClientInfo[]>([]);
  const [aedSites, setAedSites] = useState<AedSite[]>([]);
  const [location, setLocation] = useState<GeoPoint | null>(readStoredLocation);
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle');
  const [notice, setNotice] = useState<{ kind: 'ok' | 'error' | 'info'; text: string } | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [now, setNow] = useState(() => Date.now());

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectRef = useRef<number | null>(null);
  const busyActionRef = useRef<string | null>(null);

  const currentClient = useMemo(
    () => (session ? clients.find((c) => c.userId === session.user.userId) ?? null : null),
    [clients, session],
  );

  const userRole = useMemo(
    () => (session ? findUserRole(incident, session.user.userId) : null),
    [incident, session],
  );

  const isPatient = Boolean(incident && session && incident.patientUserId === session.user.userId);
  const isPatientTerminal = isPatient || session?.demoPersona === 'patient';
  const isdemoResponder = Boolean(session?.demoPersona && session.demoPersona !== 'patient');
  const candidateRole = userRole ?? currentClient?.assignedRole as RoleName | null ?? null;
  const responderTaskReady = isIncidentReadyForResponderTask(incident);
  const activeRole = responderTaskReady ? candidateRole : null;
  const action = activeRole ? roleAction(activeRole, incident) : null;
  const primeStep = activeRole === 'PRIME' ? primeNextStep(incident) : null;
  const progress = rescueProgress(incident);
  const healthStats = healthStatItems(currentClient?.healthSignals);
  const phaseLabel = incident ? translatePhaseLabel(incident.phase) : '未接入事件';
  const incidentStartedAt = incident?.logs?.[0]?.ts ?? null;

  const applyTheme = useCallback(() => {
    document.documentElement.dataset.mobileRoute = 'true';
    document.documentElement.dataset.mobileTheme = theme;
    document.documentElement.style.colorScheme = theme;
    saveTheme(theme);
  }, [theme]);

  useEffect(() => {
    applyTheme();
  }, [applyTheme]);

  useEffect(() => {
    const interval = window.setInterval(() => setNow(Date.now()), 1000);
    return () => window.clearInterval(interval);
  }, []);

  const loadPeripheralData = useCallback(async () => {
    try {
      const [nextClients, nextAeds] = await Promise.all([fetchClients(), fetchAedSites()]);
      setClients(nextClients);
      setAedSites(nextAeds);
    } catch {
      // peripheral data best-effort
    }
  }, []);

  const connectIncident = useCallback((incidentId: string) => {
    const previous = wsRef.current;
    wsRef.current = null;
    previous?.close();
    if (reconnectRef.current) {
      window.clearTimeout(reconnectRef.current);
      reconnectRef.current = null;
    }
    setSyncStatus('connecting');
    const socket = openIncidentSocket(incidentId);
    wsRef.current = socket;
    socket.onopen = () => {
      if (wsRef.current === socket) setSyncStatus('live');
    };
    socket.onmessage = (event) => {
      if (wsRef.current !== socket) return;
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'STATE') {
          setIncident((current) => mergeIncidentState(current, msg.payload as IncidentState));
        }
      } catch {
        // ignore malformed frames
      }
    };
    socket.onerror = () => {
      if (wsRef.current === socket) setSyncStatus('offline');
    };
    socket.onclose = () => {
      if (wsRef.current !== socket) return;
      if (reconnectRef.current) return;
      setSyncStatus('reconnecting');
      reconnectRef.current = window.setTimeout(() => connectIncident(incidentId), 1800);
    };
  }, []);

  const openCurrentIncident = useCallback(async () => {
    try {
      const state = await fetchCurrentIncident();
      setIncident((current) => mergeIncidentState(current, state));
      connectIncident(state.incidentId);
      await loadPeripheralData();
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '接入事件失败' });
    }
  }, [connectIncident, loadPeripheralData]);

  const runAction = useCallback(
    async (label: string, work: () => Promise<unknown>, okText: string) => {
      if (busyActionRef.current) return;
      busyActionRef.current = label;
      setBusyAction(label);
      setNotice(null);
      try {
        await work();
        if (incident?.incidentId) {
          const latest = await fetchIncident(incident.incidentId);
          setIncident((current) => mergeIncidentState(current, latest));
          await loadPeripheralData();
        }
        setNotice({ kind: 'ok', text: okText });
      } catch (error) {
        setNotice({ kind: 'error', text: error instanceof Error ? error.message : '操作失败' });
      } finally {
        busyActionRef.current = null;
        setBusyAction(null);
      }
    },
    [incident, loadPeripheralData],
  );

  const ensurePresence = useCallback(
    async (next: StoredSession, loc: GeoPoint | null) => {
      if (!next.token || !next.user) return;
      const resolvedLoc = loc ?? {
        latitude: 39.904,
        longitude: 116.407,
        label: demoLocationLabel(next.demoPersona ?? ''),
        source: 'mobile-demo',
      };
      try {
        await registerClient(next.user, next.token, resolvedLoc);
        await updateClientHealth(next.user.userId, next.token, mockHealthSignalsFor(next.user, next.demoPersona));
      } catch {
        // presence best-effort
      }
    },
    [],
  );

  const afterAuthenticated = useCallback(
    async (next: StoredSession, nextLocation?: GeoPoint | null) => {
      setSession(next);
      setLocation(nextLocation ?? null);
      setBooting(false);
      if (nextLocation) saveLocation(nextLocation);
      await ensurePresence(next, nextLocation ?? null);
      if (urlIncidentId) {
        try {
          const state = await fetchIncident(urlIncidentId);
          setIncident((current) => mergeIncidentState(current, state));
          connectIncident(state.incidentId);
          await loadPeripheralData();
        } catch {
          await openCurrentIncident();
        }
      } else {
        await openCurrentIncident();
      }
    },
    [connectIncident, ensurePresence, loadPeripheralData, openCurrentIncident],
  );

  const doLogout = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
    if (reconnectRef.current) window.clearTimeout(reconnectRef.current);
    clearSession();
    setSession(null);
    setIncident(null);
    setClients([]);
    setAedSites([]);
    setNotice(null);
  }, []);

  const handlePatientSos = useCallback(async () => {
    if (!incident || !session) return;
    if (incident.phase !== 'CREATED') {
      setNotice({ kind: 'info', text: '当前事件已进入协同处置，不能重复启动 SOS' });
      return;
    }
    setNotice({ kind: 'info', text: '再次点击确认启动 SOS' });
    await runAction('sos', () => patientSosStart(incident.incidentId, session.token), 'SOS 已启动，系统会自动确认并分派任务');
  }, [incident, runAction, session]);

  const cancelPatientSos = useCallback(async () => {
    if (!incident || !session) return;
    await runAction('sosCancel', () => patientSosCancel(incident.incidentId, session.token), 'SOS 已取消');
  }, [incident, runAction, session]);

  const joinRole = useCallback(
    (role: RoleName) => {
      if (!incident || !session) return;
      void runAction(role, () => joinIncident(incident.incidentId, role, session.user.userId, session.token), '已响应任务');
    },
    [incident, runAction, session],
  );

  const executeRoleAction = useCallback(() => {
    if (!activeRole || !action || !incident || !session) return;
    if (action.action === 'JOIN') {
      void runAction(activeRole, () => joinIncident(incident.incidentId, activeRole, session.user.userId, session.token), '已响应任务');
    } else if (action.action !== 'WAIT') {
      void runAction(
        action.action,
        () => postIncidentAction(incident.incidentId, action.action, session.user.userId, session.token),
        `${action.buttonLabel} 已记录`,
      );
    }
  }, [action, activeRole, incident, runAction, session]);

  const reportLocation = useCallback(async () => {
    if (!session) return;
    const loc = {
      latitude: 39.904,
      longitude: 116.407,
      label: demoLocationLabel(session.demoPersona ?? ''),
      source: 'mobile-demo',
    };
    try {
      await updateClientLocation(session.user.userId, session.token, loc);
      setLocation(loc);
      saveLocation(loc);
      setNotice({ kind: 'ok', text: '位置已上报' });
    } catch (error) {
      setNotice({ kind: 'error', text: error instanceof Error ? error.message : '位置上报失败' });
    }
  }, [session]);

  const onLogin = useCallback(
    async (phone: string, password: string) => {
      const auth = await loginAccount(phone, password);
      const stored: StoredSession = { token: auth.token, user: auth.user, tokenExpiresAt: auth.tokenExpiresAt };
      saveSession(stored);
      await afterAuthenticated(stored);
    },
    [afterAuthenticated],
  );

  const onRegister = useCallback(
    async (form: { displayName: string; phone: string; password: string; organization: string; healthCondition: string; professionIdentity: string; profileBio: string }) => {
      const auth = await registerAccount(form);
      const stored: StoredSession = { token: auth.token, user: auth.user, tokenExpiresAt: auth.tokenExpiresAt };
      saveSession(stored);
      await afterAuthenticated(stored);
    },
    [afterAuthenticated],
  );

  const onEnterdemo = useCallback(
    async (persona: 'patient' | 'prime' | 'runner' | 'guide') => {
      const auth = await logindemoPersona(persona);
      const stored: StoredSession = {
        token: auth.token,
        user: auth.user,
        tokenExpiresAt: auth.tokenExpiresAt,
        demoPersona: persona,
      };
      const loc = {
        latitude: 39.904,
        longitude: 116.407,
        label: demoLocationLabel(persona),
        source: 'mobile-demo',
      };
      saveSession(stored);
      await afterAuthenticated(stored, loc);
    },
    [afterAuthenticated],
  );

  const toggleTheme = useCallback(() => {
    setTheme((current) => (current === 'dark' ? 'light' : 'dark'));
  }, []);

  if (booting) {
    return (
      <div className="mobile-shell mobile-loading">
        <div className="mobile-app-mark"><HeartPulseIcon /></div>
        <p>正在恢复移动端登录态...</p>
      </div>
    );
  }

  if (!session || !session.user) {
    return <AuthPanel onLogin={onLogin} onRegister={onRegister} onEnterdemo={onEnterdemo} />;
  }

  const renderProps = {
    session,
    incident,
    phaseLabel,
    syncStatus,
    syncLabel: syncLabelFor(syncStatus),
    notice,
    busyAction,
    now,
    incidentStartedAt,
    isPatientTerminal,
    isdemoResponder,
    activeRole,
    action,
    primeStep,
    progress,
    healthStats,
    location,
    currentClient,
    theme,
    onToggleTheme: toggleTheme,
    onLogout: doLogout,
    onPatientSos: handlePatientSos,
    onCancelSos: cancelPatientSos,
    onJoinRole: joinRole,
    onExecuteAction: executeRoleAction,
    onReportLocation: reportLocation,
    onOpenCurrent: openCurrentIncident,
  };

  if (isPatientTerminal && !activeRole) {
    return <PatientScreen {...renderProps} />;
  }
  return <ResponderScreen {...renderProps} />;
}

function syncLabelFor(status: SyncStatus): string {
  switch (status) {
    case 'live': return '实时在线';
    case 'connecting': return '连接中';
    case 'reconnecting': return '恢复连接中';
    case 'offline': return '连接离线';
    default: return '待连接';
  }
}

function HeartPulseIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
    </svg>
  );
}

export { formatLocationLabel, roleLabelFor };
