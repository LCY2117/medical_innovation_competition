import { useEffect, useLayoutEffect, useMemo, useState } from 'react';
import {
  Activity,
  Archive,
  ArrowLeft,
  ExternalLink,
  FileCheck2,
  RefreshCw,
  ShieldCheck,
  Smartphone,
  Zap,
} from 'lucide-react';
import { fetchCurrentIncident, fetchDemoTerminals, fetchIncident } from '@/shared/api';
import type { DemoTerminal } from '../shared/api';
import type { IncidentState, RoleName } from '../shared/types';
import './mobile-demo-stage.css';

const demoFrames = [
  { key: 'patient', label: '患者', caption: 'SOS 触发', tone: 'patient', role: null },
  { key: 'prime', label: '施救', caption: 'CPR / AED', tone: 'prime', role: 'PRIME' as const },
  { key: 'runner', label: 'AED', caption: '取送设备', tone: 'runner', role: 'RUNNER' as const },
  { key: 'guide', label: '接应', caption: '通道清障', tone: 'guide', role: 'GUIDE' as const },
];

type TerminalSlot = {
  key: string;
  label: string;
  caption: string;
  tone: string;
  role: RoleName | null;
};

const personaRole: Record<string, RoleName | null> = {
  patient: null,
  prime: 'PRIME',
  runner: 'RUNNER',
  runner2: null,
  runner3: null,
  guide: 'GUIDE',
};

const personaTone: Record<string, string> = {
  patient: 'patient',
  prime: 'prime',
  runner: 'runner',
  runner2: 'runner',
  runner3: 'runner',
  guide: 'guide',
};

// 舞台默认只挂主线 4 端；AI 任务派发后，候选跑腿端再动态加入
const CORE_TERMINAL_KEYS = ['demo-patient', 'demo-prime', 'demo-runner', 'demo-guide'];
const TERMINAL_ORDER: Record<string, number> = {
  'demo-patient': 0,
  'demo-prime': 1,
  'demo-runner': 2,
  'demo-guide': 3,
  'demo-runner2': 4,
  'demo-runner3': 5,
  patient: 0,
  prime: 1,
  runner: 2,
  guide: 3,
  runner2: 4,
  runner3: 5,
};

function toSlot(terminal: DemoTerminal): TerminalSlot {
  const persona = terminal.userId.replace('demo-', '');
  const role = personaRole[persona] ?? null;
  const tone = personaTone[persona] ?? (role ? role.toLowerCase() : 'runner');
  const caption =
    persona === 'patient' ? 'SOS 触发' : terminal.isPatient ? '患者端' : terminal.assignedRole ? terminal.assignedRole : terminal.organization || '响应端';
  return { key: terminal.userId, label: terminal.displayName, caption, tone, role };
}

function fallbackSlots(): TerminalSlot[] {
  return demoFrames.map((frame) => ({
    key: frame.key,
    label: frame.label,
    caption: frame.caption,
    tone: frame.tone,
    role: frame.role,
  }));
}

const runbookSteps = [
  'SOS',
  '分派',
  '响应',
  'CPR',
  'AED',
  '接应',
  '归档',
];

const roleNames: RoleName[] = ['PRIME', 'RUNNER', 'GUIDE'];
const activeResponderPhases = new Set([
  'DISPATCHED',
  'CPR',
  'AED_PICKED',
  'AED_DELIVERED',
  'AED_ANALYZING',
  'SHOCK_DELIVERED',
  'HANDOVER',
  'ARCHIVED',
]);

const phaseLabels: Record<string, string> = {
  CREATED: '事件创建',
  DISPATCHING: '智能分派',
  DISPATCHED: '任务已下发',
  CPR: 'CPR 进行中',
  AED_PICKED: 'AED 已取到',
  AED_DELIVERED: 'AED 已送达',
  AED_ANALYZING: 'AED 分析中',
  SHOCK_DELIVERED: '已完成除颤',
  HANDOVER: '急救接应',
  ARCHIVED: '证据归档',
};

const roleStatusLabels: Record<string, string> = {
  ASSIGNED: '已分派',
  JOINED: '已响应',
  CPR_STARTED: 'CPR 中',
  AED_PICKED: '已取 AED',
  AED_DELIVERED: 'AED 到场',
  AED_ANALYZING: '分析心律',
  AED_SHOCK_DELIVERED: '已除颤',
  AMBULANCE_ARRIVED: '救护车到场',
  HANDOVER_COMPLETED: '交接归档',
};

function shortId(value: string): string {
  return value.length > 14 ? `${value.slice(0, 8)}...${value.slice(-4)}` : value;
}

function translatePhase(phase?: string | null): string {
  if (!phase) {
    return '未接入';
  }
  return phaseLabels[phase] ?? phase;
}

function translateRoleStatus(status?: string | null): string {
  if (!status) {
    return '待分派';
  }
  return roleStatusLabels[status] ?? status;
}

function logContains(state: IncidentState | null, keyword: string): boolean {
  return Boolean(state?.logs?.some((log) => log.msg.toLowerCase().includes(keyword.toLowerCase())));
}

function hasJoined(status?: string | null): boolean {
  return Boolean(status && status !== 'ASSIGNED' && status !== 'PENDING');
}

function hasAnyResponder(state: IncidentState | null): boolean {
  return Boolean(state && roleNames.some((role) => hasJoined(state.roles?.[role]?.status)));
}

function hasAssignedRoles(state: IncidentState | null): boolean {
  return Boolean(state && activeResponderPhases.has(state.phase) && roleNames.some((role) => state.roles?.[role]?.userId || state.roles?.[role]?.status));
}

function hasPrimeStarted(state: IncidentState | null): boolean {
  return (
    ['CPR_STARTED', 'AED_ANALYZING', 'AED_SHOCK_DELIVERED'].includes(state?.roles?.PRIME?.status ?? '') ||
    ['CPR', 'AED_ANALYZING', 'SHOCK_DELIVERED', 'HANDOVER', 'ARCHIVED'].includes(state?.phase ?? '') ||
    logContains(state, 'CPR started')
  );
}

function hasRunnerPicked(state: IncidentState | null): boolean {
  return (
    ['AED_PICKED', 'AED_DELIVERED'].includes(state?.roles?.RUNNER?.status ?? '') ||
    ['AED_PICKED', 'AED_DELIVERED', 'AED_ANALYZING', 'SHOCK_DELIVERED', 'HANDOVER', 'ARCHIVED'].includes(state?.phase ?? '') ||
    logContains(state, 'AED picked')
  );
}

function hasRunnerDelivered(state: IncidentState | null): boolean {
  return (
    state?.roles?.RUNNER?.status === 'AED_DELIVERED' ||
    ['AED_DELIVERED', 'AED_ANALYZING', 'SHOCK_DELIVERED', 'HANDOVER', 'ARCHIVED'].includes(state?.phase ?? '') ||
    logContains(state, 'AED delivered')
  );
}

function hasGuideCompleted(state: IncidentState | null): boolean {
  return (
    state?.roles?.GUIDE?.status === 'AMBULANCE_ARRIVED' ||
    state?.roles?.GUIDE?.status === 'HANDOVER_COMPLETED' ||
    state?.phase === 'HANDOVER' ||
    state?.phase === 'ARCHIVED'
  );
}

function hasShockDelivered(state: IncidentState | null): boolean {
  return state?.phase === 'SHOCK_DELIVERED' || state?.roles?.PRIME?.status === 'AED_SHOCK_DELIVERED' || logContains(state, 'AED shock delivered');
}

function getRunbookIndex(state: IncidentState | null): number {
  if (!state) {
    return -1;
  }
  if (state.phase === 'ARCHIVED' || logContains(state, 'archived')) {
    return 6;
  }
  if (state.phase === 'HANDOVER' || hasGuideCompleted(state)) {
    return 5;
  }
  if (
    state.phase === 'AED_PICKED' ||
    state.phase === 'AED_DELIVERED' ||
    state.phase === 'AED_ANALYZING' ||
    state.phase === 'SHOCK_DELIVERED' ||
    hasRunnerPicked(state) ||
    hasRunnerDelivered(state) ||
    hasShockDelivered(state)
  ) {
    return 4;
  }
  if (state.phase === 'CPR' || hasPrimeStarted(state)) {
    return 3;
  }
  if (hasAnyResponder(state)) {
    return 2;
  }
  if (state.phase === 'DISPATCHING' || state.phase === 'DISPATCHED' || hasAssignedRoles(state)) {
    return 1;
  }
  return state.sos?.status === 'ALERTING' || state.patientUserId ? 0 : -1;
}

function formatLogTime(ts: number): string {
  return new Intl.DateTimeFormat('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  }).format(new Date(ts));
}

function getAedStatus(state: IncidentState | null): string {
  if (!state) {
    return '待接入事件';
  }
  if (hasShockDelivered(state)) {
    return '除颤记录已生成';
  }
  if (state.phase === 'AED_ANALYZING' || state.roles.PRIME?.status === 'AED_ANALYZING' || logContains(state, 'AED analysis')) {
    return '心律分析中';
  }
  if (hasRunnerDelivered(state)) {
    return 'AED 已送达患者点';
  }
  if (hasRunnerPicked(state)) {
    return 'AED 已取出，返回中';
  }
  const nearestSiteId = state.dispatchRationale?.RUNNER?.nearestAedSiteId ?? state.dispatchRationale?.PRIME?.nearestAedSiteId;
  if (nearestSiteId) {
    return `已锁定点位 ${nearestSiteId}`;
  }
  return state.aedSites?.length ? 'AED 点位可用' : '等待 AED 点位';
}

function getEvidenceStatus(state: IncidentState | null): string {
  if (!state) {
    return '未开始采集';
  }
  if (state.phase === 'ARCHIVED' || logContains(state, 'archived')) {
    return '已归档，可导出证据包';
  }
  if (state.phase === 'HANDOVER' || hasGuideCompleted(state)) {
    return '接应完成，归档待生成';
  }
  return `实时采集中，日志 ${state.logs?.length ?? 0} 条`;
}

function getTerminalStatus(frame: TerminalSlot, state: IncidentState | null): string {
  if (!state) {
    return '未接入事件';
  }
  if (!frame.role) {
    return state.sos?.status === 'ALERTING' ? 'SOS 倒计时中' : translatePhase(state.phase);
  }
  if (state.phase === 'CREATED' || state.phase === 'DISPATCHING') {
    return '待患者端启动';
  }
  return translateRoleStatus(state.roles?.[frame.role]?.status);
}

const PHONE_W = 390;
const PHONE_H = 780;

function usePhoneScale(gridSelector: string): number {
  const [scale, setScale] = useState(1);
  useLayoutEffect(() => {
    const compute = () => {
      const grid = document.querySelector<HTMLElement>(gridSelector);
      if (!grid) {
        return;
      }
      const availW = grid.clientWidth;
      const gap = 12;
      if (!window.matchMedia('(min-width: 901px)').matches) {
        // narrow screens: shrink so two phones can sit side by side
        const next = Math.max(0.35, Math.min(1, (availW - gap) / 2 / PHONE_W));
        setScale((current) => (Math.abs(current - next) < 0.01 ? current : next));
        return;
      }
      // fit both width and height so the four phones always show fully on screen
      const maxScaleW = (availW - gap * 3) / 4 / PHONE_W;
      const availH = grid.clientHeight - 96;
      const maxScaleH = Math.max(0.2, availH / PHONE_H);
      const next = Math.max(0.2, Math.min(1, maxScaleW, maxScaleH));
      setScale((current) => (Math.abs(current - next) < 0.01 ? current : next));
    };
    compute();
    window.addEventListener('resize', compute);
    const observer = new ResizeObserver(compute);
    const gridEl = document.querySelector<HTMLElement>(gridSelector);
    if (gridEl) {
      observer.observe(gridEl);
    }
    return () => {
      window.removeEventListener('resize', compute);
      observer.disconnect();
    };
  }, [gridSelector]);
  return scale;
}

function MobiledemoStage() {
  const [incidentId, setIncidentId] = useState(() => new URLSearchParams(window.location.search).get('incidentId')?.trim() ?? '');
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [loadError, setLoadError] = useState('');
  const [lastUpdatedAt, setLastUpdatedAt] = useState<number | null>(null);
  const [terminalPool, setTerminalPool] = useState<DemoTerminal[]>([]);
  const [activeTerminalKeys, setActiveTerminalKeys] = useState<string[] | null>(null);
  const [focusedKey, setFocusedKey] = useState<string | null>(null);
  const [showAddMenu, setShowAddMenu] = useState(false);
  const shortIncidentId = incidentId ? `${incidentId.slice(0, 8)}...${incidentId.slice(-4)}` : '未绑定';
  const incidentStatus = incidentId ? '已绑定当前事件' : '未绑定事件';
  const incidentHint = incidentId
    ? '四个终端共享同一事件编号，状态面板每 3 秒刷新一次。'
    : '请先从总控台初始化演示场景，再打开 4 端导播台。';
  const boundIncidentId = incident?.incidentId || incidentId;
  const currentRunbookIndex = getRunbookIndex(incident);
  const latestLogs = useMemo(() => [...(incident?.logs ?? [])].slice(-3).reverse(), [incident?.logs]);
  const lastUpdatedLabel = lastUpdatedAt ? formatLogTime(lastUpdatedAt) : '--:--:--';

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;

    const loadIncident = async () => {
      try {
        const state = incidentId ? await fetchIncident(incidentId) : await fetchCurrentIncident();
        if (!cancelled) {
          setIncident(state);
          if (!incidentId && state.incidentId) {
            setIncidentId(state.incidentId);
            const url = new URL(window.location.href);
            url.searchParams.set('incidentId', state.incidentId);
            window.history.replaceState(null, '', url.toString());
          }
          setLoadError('');
          setLastUpdatedAt(Date.now());
        }
      } catch (error) {
        if (!cancelled) {
          setLoadError(error instanceof Error ? error.message : '加载事件失败');
        }
      }
    };

    void loadIncident();
    if (incidentId) {
      timer = window.setInterval(loadIncident, 3000);
    }

    return () => {
      cancelled = true;
      if (timer) {
        window.clearInterval(timer);
      }
    };
  }, [incidentId]);

  const phoneScale = usePhoneScale('.mobile-demo-stage-grid');

  useEffect(() => {
    let cancelled = false;
    const loadTerminals = async () => {
      try {
        const list = await fetchDemoTerminals();
        if (!cancelled) {
          setTerminalPool(list);
          setActiveTerminalKeys((current) => current ?? list.filter((t) => CORE_TERMINAL_KEYS.includes(t.userId)).map((t) => t.userId));
        }
      } catch (error) {
        if (!cancelled) {
          setTerminalPool([]);
          setActiveTerminalKeys((current) => current ?? fallbackSlots().map((s) => s.key));
        }
      }
    };
    void loadTerminals();
    return () => {
      cancelled = true;
    };
  }, []);

  // AI 任务派发后，候选跑腿端自动加入舞台
  useEffect(() => {
    const tasks = Object.values(incident?.aiTasks ?? {});
    if (tasks.length === 0) {
      return;
    }
    const candidateKeys = new Set<string>();
    for (const task of tasks) {
      for (const uid of task.assignableUserIds) {
        candidateKeys.add(uid);
      }
    }
    if (candidateKeys.size === 0) {
      return;
    }
    setActiveTerminalKeys((current) => {
      const base = current ?? CORE_TERMINAL_KEYS;
      const merged = [...new Set([...base, ...candidateKeys])];
      return merged.length === base.length ? current : merged;
    });
  }, [incident?.aiTasks]);

  const activeSlots: TerminalSlot[] = useMemo(() => {
    const usingPool = terminalPool.length > 0;
    const pool = usingPool ? terminalPool : fallbackSlots();
    const keys = activeTerminalKeys ?? pool.map((t) => ('userId' in t ? t.userId : t.key));
    const slotByKey = new Map(
      usingPool ? pool.map((t) => [t.userId, toSlot(t)]) : pool.map((s) => [s.key, s]),
    );
    return keys
      .map((key) => slotByKey.get(key) ?? fallbackSlots().find((s) => s.key === key))
      .filter((slot): slot is TerminalSlot => Boolean(slot))
      .sort((a, b) => (TERMINAL_ORDER[a.key] ?? 99) - (TERMINAL_ORDER[b.key] ?? 99));
  }, [terminalPool, activeTerminalKeys]);

  const addTerminal = (userId: string) => {
    setActiveTerminalKeys((current) => (current ? [...current, userId] : [userId]));
    setShowAddMenu(false);
  };

  const removeTerminal = (userId: string) => {
    setActiveTerminalKeys((current) => (current ? current.filter((key) => key !== userId) : current));
    setFocusedKey((current) => (current === userId ? null : current));
  };

  const renderFrame = (slot: TerminalSlot, options: { focused?: boolean; thumb?: boolean } = {}) => {
    const params = new URLSearchParams({ demo: slot.key.replace('demo-', ''), slot: slot.key });
    if (boundIncidentId) {
      params.set('incidentId', boundIncidentId);
    }
    const src = `/mobile?${params.toString()}`;
    const deviceScale = options.thumb ? 0.36 : phoneScale;
    const deviceW = PHONE_W * deviceScale;
    const deviceH = PHONE_H * deviceScale;
    return (
      <article
        className={`mobile-demo-stage-panel is-${slot.tone}${options.focused ? ' is-focused' : ''}${options.thumb ? ' is-thumb' : ''}`}
        key={slot.key}
      >
        <div className="mobile-demo-stage-panel-head">
          <div>
            <strong>{slot.label}</strong>
            <span>{slot.caption} · {getTerminalStatus(slot, incident)}</span>
            <small title={incident?.incidentId || incidentId || undefined}>事件 {incident?.incidentId ? shortId(incident.incidentId) : shortIncidentId}</small>
          </div>
          <div className="mobile-demo-stage-panel-actions">
            <a href={src} target="_blank" rel="noreferrer" aria-label={`打开${slot.label}`}>
              <ExternalLink size={16} />
            </a>
            <button className="mobile-demo-stage-remove" onClick={() => removeTerminal(slot.key)} aria-label={`移除${slot.label}`} title="移除终端">
              ×
            </button>
          </div>
        </div>
        <div className="mobile-demo-stage-device">
          <div className="lra-stage-phone" style={{ width: deviceW, height: deviceH }}>
            <iframe
              className="mobile-demo-stage-frame"
              title={slot.label}
              src={src}
              loading="eager"
              style={{ width: PHONE_W, height: PHONE_H, transform: `scale(${deviceScale})` }}
            />
          </div>
        </div>
      </article>
    );
  };

  const poolKeys = new Set(terminalPool.map((t) => t.userId));
  const addable = terminalPool.filter((t) => !(activeTerminalKeys ?? []).includes(t.userId));

  const reloadAll = () => {
    document.querySelectorAll<HTMLIFrameElement>('.mobile-demo-stage-frame').forEach((frame) => {
      frame.contentWindow?.location.reload();
    });
  };

  return (
    <main className="mobile-demo-stage">
      <header className="mobile-demo-stage-header">
        <a href="/" className="mobile-demo-stage-icon-link" aria-label="返回总控台">
          <ArrowLeft size={18} />
        </a>
        <div className="mobile-demo-stage-title">
          <Smartphone size={20} />
          <div>
            <p>生命反射弧</p>
            <h1>四端协同演示台</h1>
          </div>
        </div>
        <button className="mobile-demo-stage-icon-button" onClick={reloadAll} aria-label="刷新四端" title="刷新四端">
          <RefreshCw size={18} />
        </button>
      </header>

      <section className="mobile-demo-stage-strip" aria-label="演示状态">
        <div className={`mobile-demo-stage-context ${incidentId ? 'is-bound' : 'is-unbound'}`}>
          <ShieldCheck size={16} />
          <div>
            <strong>{incidentStatus}</strong>
            <span title={incidentId || undefined}>{shortIncidentId}</span>
          </div>
        </div>
        <p>{incidentHint}</p>
        <div className="mobile-demo-stage-safety">
          <ShieldCheck size={15} />
          <span>安全边界：仅用于协同训练与预实验展示，不触发真实急救调度。</span>
        </div>
        <ol className="mobile-demo-stage-runbook" aria-label="演示导播步骤">
          {runbookSteps.map((step, index) => (
            <li
              className={`mobile-demo-stage-runbook-step ${
                index < currentRunbookIndex ? 'is-done' : index === currentRunbookIndex ? 'is-active' : 'is-waiting'
              }`}
              key={step}
            >
              <span>{index + 1}</span>
              <strong>{step}</strong>
            </li>
          ))}
        </ol>
      </section>

      <section className="mobile-demo-stage-dashboard" aria-label="事件动态">
        <div className="mobile-demo-stage-metric is-phase">
          <Activity size={18} />
          <span>事件阶段</span>
          <strong>{translatePhase(incident?.phase)}</strong>
          <small>刷新 {lastUpdatedLabel}</small>
        </div>
        <div className="mobile-demo-stage-metric is-aed">
          <Zap size={18} />
          <span>AED 状态</span>
          <strong>{getAedStatus(incident)}</strong>
          <small>{incident?.aedSites?.length ? `${incident.aedSites.length} 个点位` : '点位待同步'}</small>
        </div>
        <div className="mobile-demo-stage-metric is-archive">
          <FileCheck2 size={18} />
          <span>证据 / 归档</span>
          <strong>{getEvidenceStatus(incident)}</strong>
          <small>{loadError || '日志、角色、AED 轨迹进入证据链'}</small>
        </div>
        <div className="mobile-demo-stage-log-card">
          <div className="mobile-demo-stage-log-title">
            <Archive size={17} />
            <strong>最近日志</strong>
          </div>
          {latestLogs.length ? (
            latestLogs.map((log) => (
              <p key={`${log.ts}-${log.msg}`}>
                <time>{formatLogTime(log.ts)}</time>
                <span>{log.msg}</span>
              </p>
            ))
          ) : (
            <p>
              <time>--:--:--</time>
              <span>{incidentId ? '等待事件日志同步' : '未绑定 incidentId'}</span>
            </p>
          )}
        </div>
      </section>

            <section className="mobile-demo-stage-toolbar" aria-label="终端管理">
        <span className="mobile-demo-stage-toolbar-count">{activeSlots.length} 个终端在线</span>
        {addable.length > 0 && (
          <div className="mobile-demo-stage-addwrap">
            <button className="mobile-demo-stage-add" onClick={() => setShowAddMenu((v) => !v)}>
              + 添加终端
            </button>
            {showAddMenu && (
              <div className="mobile-demo-stage-addmenu">
                {addable.map((t) => (
                  <button key={t.userId} onClick={() => addTerminal(t.userId)}>
                    {t.displayName}
                    <small>{t.organization || t.userId}</small>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        {focusedKey && (
          <button className="mobile-demo-stage-unfocus" onClick={() => setFocusedKey(null)}>
            退出聚焦（网格视图）
          </button>
        )}
      </section>

      <section className={`mobile-demo-stage-grid${focusedKey ? ' is-focused' : ''}`}>
        {focusedKey ? (
          <>
            {activeSlots.filter((s) => s.key === focusedKey).map((slot) => renderFrame(slot, { focused: true }))}
            <div className="mobile-demo-stage-thumbs">
              {activeSlots.filter((s) => s.key !== focusedKey).map((slot) => (
                <button
                  type="button"
                  key={slot.key}
                  className="mobile-demo-stage-thumb"
                  onClick={() => setFocusedKey(slot.key)}
                  aria-label={`聚焦${slot.label}`}
                >
                  {renderFrame(slot, { thumb: true })}
                  <span className="mobile-demo-stage-thumb-name">{slot.label}</span>
                </button>
              ))}
            </div>
          </>
        ) : (
          activeSlots.map((slot) => (
            <div key={slot.key} className="mobile-demo-stage-focus-wrap" onClick={() => setFocusedKey(slot.key)}>
              {renderFrame(slot)}
            </div>
          ))
        )}
      </section>
    </main>
  );
}

export default MobiledemoStage;
