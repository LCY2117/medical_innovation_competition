import { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  Archive,
  ArrowLeft,
  ExternalLink,
  FileCheck2,
  HeartPulse,
  RefreshCw,
  ShieldCheck,
  Smartphone,
  Zap,
} from 'lucide-react';
import { fetchIncident } from '@/shared/api';
import type { IncidentState, RoleName } from '../shared/types';
import './mobile-demo-stage.css';

const demoFrames = [
  { key: 'patient', label: '患者', caption: 'SOS 触发', tone: 'patient', role: null },
  { key: 'prime', label: '施救', caption: 'CPR / AED', tone: 'prime', role: 'PRIME' as const },
  { key: 'runner', label: 'AED', caption: '取送设备', tone: 'runner', role: 'RUNNER' as const },
  { key: 'guide', label: '接应', caption: '通道清障', tone: 'guide', role: 'GUIDE' as const },
];

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
    return '待响应';
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
  return Boolean(state && roleNames.some((role) => state.roles?.[role]?.userId || state.roles?.[role]?.status));
}

function hasPrimeStarted(state: IncidentState | null): boolean {
  return state?.roles?.PRIME?.status === 'CPR_STARTED' || logContains(state, 'CPR started');
}

function hasRunnerPicked(state: IncidentState | null): boolean {
  return state?.roles?.RUNNER?.status === 'AED_PICKED' || logContains(state, 'AED picked');
}

function hasRunnerDelivered(state: IncidentState | null): boolean {
  return state?.roles?.RUNNER?.status === 'AED_DELIVERED' || logContains(state, 'AED delivered');
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
  return 0;
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

function getTerminalStatus(frame: (typeof demoFrames)[number], state: IncidentState | null): string {
  if (!state) {
    return '未接入事件';
  }
  if (!frame.role) {
    return state.sos?.status === 'ALERTING' ? 'SOS 倒计时中' : translatePhase(state.phase);
  }
  return translateRoleStatus(state.roles?.[frame.role]?.status);
}

function MobileDemoStage() {
  const incidentId = new URLSearchParams(window.location.search).get('incidentId')?.trim() ?? '';
  const [incident, setIncident] = useState<IncidentState | null>(null);
  const [loadError, setLoadError] = useState('');
  const [lastUpdatedAt, setLastUpdatedAt] = useState<number | null>(null);
  const shortIncidentId = incidentId ? `${incidentId.slice(0, 8)}...${incidentId.slice(-4)}` : '未绑定';
  const incidentStatus = incidentId ? '已绑定当前事件' : '未绑定事件';
  const incidentHint = incidentId
    ? '四个终端共享同一事件编号，状态面板每 3 秒刷新一次。'
    : '请先从总控台初始化演示场景，再打开 4 端导播台。';
  const currentRunbookIndex = getRunbookIndex(incident);
  const latestLogs = useMemo(() => [...(incident?.logs ?? [])].slice(-3).reverse(), [incident?.logs]);
  const roleSummary = roleNames.map((role) => ({
    role,
    label: role === 'PRIME' ? '施救' : role === 'RUNNER' ? 'AED' : '接应',
    status: translateRoleStatus(incident?.roles?.[role]?.status),
  }));
  const lastUpdatedLabel = lastUpdatedAt ? formatLogTime(lastUpdatedAt) : '--:--:--';

  useEffect(() => {
    let cancelled = false;
    let timer: number | undefined;

    const loadIncident = async () => {
      if (!incidentId) {
        setIncident(null);
        setLoadError('');
        return;
      }
      try {
        const state = await fetchIncident(incidentId);
        if (!cancelled) {
          setIncident(state);
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
          <span>安全边界：仅使用模拟数据与演示终端，不触发真实急救调度。</span>
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

      <section className="mobile-demo-stage-roles" aria-label="角色状态">
        {roleSummary.map((role) => (
          <div className="mobile-demo-stage-role" key={role.role}>
            <HeartPulse size={16} />
            <span>{role.label}</span>
            <strong>{role.status}</strong>
          </div>
        ))}
      </section>

      <section className="mobile-demo-stage-grid">
        {demoFrames.map((frame) => {
          const params = new URLSearchParams({ demo: frame.key, slot: frame.key });
          if (incidentId) {
            params.set('incidentId', incidentId);
          }
          const src = `/mobile?${params.toString()}`;
          return (
            <article className={`mobile-demo-stage-panel is-${frame.tone}`} key={frame.key}>
              <div className="mobile-demo-stage-panel-head">
                <div>
                  <strong>{frame.label}</strong>
                  <span>{frame.caption} · {getTerminalStatus(frame, incident)}</span>
                  <small title={incident?.incidentId || incidentId || undefined}>事件 {incident?.incidentId ? shortId(incident.incidentId) : shortIncidentId}</small>
                </div>
                <a href={src} target="_blank" rel="noreferrer" aria-label={`打开${frame.label}`}>
                  <ExternalLink size={16} />
                </a>
              </div>
              <div className="mobile-demo-stage-device">
                <iframe className="mobile-demo-stage-frame" title={frame.label} src={src} loading="eager" />
              </div>
            </article>
          );
        })}
      </section>
    </main>
  );
}

export default MobileDemoStage;
