import type { ReactNode } from 'react';
import {
  Activity,
  Ambulance,
  HeartPulse,
  MapPin,
  Radio,
  ShieldCheck,
  Siren,
  Users,
  Zap,
} from 'lucide-react';
import type { AiTaskState, ClientInfo, HealthSignalSummary } from '@/shared/types';
import {
  formatHealthRiskTags,
  formatLocationLabel,
  translateHealthAuthorization,
  translateHealthSource,
  translateRoleLabel,
  translateRoleStatus,
} from '@/shared/domain';
import type { DashboardViewModel } from '../hooks/useDashboard';
import { EChart } from './EChart';
import { formatElapsed } from '../helpers';
import { DemoQr } from './DemoQr';

/** 浙江大屏同款数据卡：titlebg 标题条 + 内容区 */
export function ZjCard({
  title,
  children,
  delay = 0,
  extra,
}: {
  title: string;
  children: ReactNode;
  delay?: number;
  extra?: ReactNode;
}) {
  return (
    <div className="lra-zj-panel" style={{ animationDelay: `${delay}s` }}>
      <div className="lra-zj-panel-hd">
        <span className="lra-zj-panel-hd-title">{title}</span>
        <span className="lra-zj-panel-hd-dot">
          <span className="dot dot1" />
          <span className="dot dot2" />
          <span className="dot dot3" />
        </span>
        {extra && <div className="lra-zj-panel-hd-extra">{extra}</div>}
      </div>
      <div className="lra-zj-panel-bd">{children}</div>
    </div>
  );
}

function KpiTile({ label, value, tone }: { label: string; value: string; tone?: 'red' | 'cyan' | 'amber' }) {
  return (
    <div className="lra-kpi-tile">
      <div className="lra-kpi-tile-label">{label}</div>
      <div className={`lra-kpi-tile-value ${tone ?? ''}`}>{value}</div>
    </div>
  );
}

function HealthChips({ summary }: { summary?: HealthSignalSummary | null }) {
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
      <span className="lra-chip" style={{ height: 22, fontSize: 11, padding: '0 8px' }}>
        {summary?.heartRateBpm ? `${summary.heartRateBpm} bpm` : '心率 --'}
      </span>
      <span className="lra-chip" style={{ height: 22, fontSize: 11, padding: '0 8px' }}>
        {summary?.bloodOxygenPercent ? `${summary.bloodOxygenPercent}% SpO2` : '血氧 --'}
      </span>
      <span className="lra-chip" style={{ height: 22, fontSize: 11, padding: '0 8px' }}>
        {summary?.pressureScore !== undefined && summary?.pressureScore !== null
          ? `压力 ${summary.pressureScore}`
          : '压力 --'}
      </span>
    </div>
  );
}

export function LeftPanel({ vm }: { vm: DashboardViewModel }) {
  const responseRate = vm.incidentState ? Math.round((vm.responderCount / 3) * 100) : 0;
  const aedAvailable = vm.visibleAedSites.filter((site) => site.status === 'AVAILABLE').length;
  const aedTotal = vm.visibleAedSites.length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'center' }}>
      <ZjCard title="事件态势" delay={0.2}>
        <div className="lra-kpi-grid">
          <KpiTile
            label="当前阶段"
            value={vm.phaseLabel}
            tone={vm.incidentState?.sos?.status === 'ALERTING' ? 'red' : undefined}
          />
          <KpiTile label="响应率" value={`${responseRate}%`} tone="cyan" />
          <KpiTile label="黄金时间" value={vm.incidentId ? formatElapsed(vm.elapsedSeconds) : '--:--'} tone="amber" />
          <KpiTile
            label="救护接管"
            value={
              vm.incidentState?.phase === 'ARCHIVED' || vm.incidentState?.phase === 'HANDOVER'
                ? '已到场'
                : vm.incidentState
                  ? '进行中'
                  : '--'
            }
          />
        </div>
        <div className="lra-flow-mini">
          {vm.demoFlowSteps.map((step, index) => (
            <div key={step.title} className={`lra-flow-mini-item ${step.complete ? 'done' : ''} ${step.active ? 'active' : ''}`}>
              <span className="dot" />
              <span className="label">{index + 1}</span>
            </div>
          ))}
          <div className="lra-flow-mini-text">
            {vm.demoFlowSteps.find((step) => step.active)?.title ?? (vm.demoFlowSteps.every((s) => s.complete) ? '演示完成' : '待开始')}
          </div>
        </div>
      </ZjCard>

      <ZjCard
        title="AI 智能调度"
        delay={0.42}
        extra={
          <span style={{ fontSize: 11, color: vm.dispatchMeta?.configured ? 'var(--lra-green)' : 'var(--lra-amber)' }}>
            {vm.dispatchMeta?.configured ? '智能分派' : '规则兜底'}
          </span>
        }
      >
        {vm.dispatchStream.length === 0 ? (
          <div style={{ fontSize: 12, color: 'var(--lra-text-faint)', textAlign: 'center', padding: '38px 0' }}>
            尚未触发患者端事件
          </div>
        ) : (
          <div className="lra-dispatch-list">
            {vm.dispatchStream
              .filter((step) => step.visible)
              .slice(0, 5)
              .map((step, index) => (
                <div key={step.key} className={`lra-dispatch-row ${step.done ? 'done' : ''} ${step.active ? 'active' : ''}`}>
                  <span className="idx">{step.done ? '✓' : index + 1}</span>
                  <span className="title">{step.title}</span>
                  <span className="status">{step.active ? '执行中' : step.done ? '完成' : '等待'}</span>
                </div>
              ))}
          </div>
        )}
      </ZjCard>

      <ZjCard
        title="AI 聚焦轨迹"
        delay={0.64}
        extra={<span style={{ fontSize: 10, color: 'var(--lra-text-faint)' }}>点击条目手动聚焦</span>}
      >
        {vm.spotlightTimeline.length === 0 ? (
          <div style={{ fontSize: 12, color: 'var(--lra-text-faint)', textAlign: 'center', padding: '38px 0' }}>
            暂无聚焦记录
          </div>
        ) : (
          <div className="lra-tl">
            {vm.spotlightTimeline.slice(0, 6).map((entry) => (
              <button
                key={entry.id}
                className={`lra-tl-entry ${entry.severity === 'critical' ? 'critical' : ''} ${
                  vm.spotlight?.target === entry.target && vm.manualFocus === entry.target ? 'active' : ''
                }`}
                onClick={() =>
                  vm.actions.setManualFocus(vm.manualFocus === entry.target ? null : entry.target)
                }
                title={entry.message}
              >
                <span className="node" />
                <span className="time">
                  {new Date(entry.ts).toLocaleTimeString('zh-CN', { hour12: false })}
                </span>
                <span className="title">{entry.title}</span>
              </button>
            ))}
          </div>
        )}
      </ZjCard>

      <ZjCard title="AED 点位库" delay={0.86} extra={<span style={{ fontSize: 11, color: 'var(--lra-cyan-soft)' }}>{aedAvailable}/{aedTotal} 可用</span>}>
        {vm.visibleAedSites.length === 0 ? (
          <div style={{ fontSize: 12, color: 'var(--lra-text-faint)', textAlign: 'center', padding: '38px 0' }}>
            暂无 AED 点位
          </div>
        ) : (
          <div className="lra-aed-list">
            {vm.visibleAedSites.map((site) => (
              <div key={site.siteId} className="lra-aed-row">
                <Zap size={13} style={{ color: site.status === 'AVAILABLE' ? 'var(--lra-cyan)' : 'var(--lra-amber)', flexShrink: 0 }} />
                <span className="name">{site.name}</span>
                <span className={`status ${site.status === 'AVAILABLE' ? 'ok' : 'busy'}`}>
                  {site.status === 'AVAILABLE' ? '可用' : '占用'}
                </span>
              </div>
            ))}
          </div>
        )}
      </ZjCard>
    </div>
  );
}

function terminalFor(vm: DashboardViewModel, kind: 'PATIENT' | 'PRIME' | 'RUNNER' | 'GUIDE'): ClientInfo | null {
  if (kind === 'PATIENT') {
    return vm.clients.find((client) => client.isPatient) ?? null;
  }
  const role = kind === 'PRIME' ? 'PRIME' : kind === 'RUNNER' ? 'RUNNER' : 'GUIDE';
  const userId = vm.incidentState?.roles?.[role]?.userId;
  return vm.clients.find((client) => client.userId === userId) ?? null;
}

function focusClass(target: string | null | undefined, kind: string): string {
  return target === kind ? ' focused' : '';
}

function aiTaskRows(task: AiTaskState): { uid: string; isRunner: boolean }[] {
  if (task.status === 'ACTIVE' && task.runnerUserId) {
    return [task.runnerUserId, ...task.supportUserIds].map((uid) => ({ uid, isRunner: uid === task.runnerUserId }));
  }
  if (task.status === 'COMPLETED') {
    return (task.runnerUserId ? [task.runnerUserId] : []).map((uid) => ({ uid, isRunner: true }));
  }
  return task.assignableUserIds.map((uid) => ({ uid, isRunner: false }));
}

function AiTaskBadge({ status }: { status: string }) {
  const label = status === 'PENDING' ? '待接单' : status === 'ACTIVE' ? '执行中' : status === 'COMPLETED' ? '已完成' : status;
  return <span className={`lra-ai-task-status s-${status.toLowerCase()}`}>{label}</span>;
}

export function RightPanel({ vm }: { vm: DashboardViewModel }) {
  const patient = terminalFor(vm, 'PATIENT');
  const prime = terminalFor(vm, 'PRIME');
  const runner = terminalFor(vm, 'RUNNER');
  const guide = terminalFor(vm, 'GUIDE');
  const spotlight = vm.spotlight?.target ?? null;
  const heartRate = patient?.healthSignals?.heartRateBpm ?? 72;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 10, alignItems: 'center' }}>
      <ZjCard
        title="患者端"
        delay={0.3}
        extra={
          vm.incidentState?.sos?.status === 'ALERTING' ? (
            <span style={{ fontSize: 11, color: 'var(--lra-red)', fontWeight: 700 }}>SOS 告警中</span>
          ) : undefined
        }
      >
        <div className={`lra-term-compact patient${focusClass(spotlight, 'PATIENT')}`}>
          <div className="lra-term-compact-head">
            <div className="icon"><Siren size={18} /></div>
            <div>
              <div className="name">{patient?.displayName ?? '患者端'}</div>
              <div className="meta">
                {patient ? formatLocationLabel(patient.location) : '未上报位置'}
              </div>
            </div>
            <span className={`online ${patient?.online ? 'on' : ''}`}>{patient?.online ? '在线' : '离线'}</span>
          </div>
          <div className="lra-term-compact-body">
            <EChart
              height={104}
              option={{
                series: [
                  {
                    type: 'gauge',
                    startAngle: 200,
                    endAngle: -20,
                    min: 0,
                    max: 200,
                    radius: '100%',
                    center: ['50%', '62%'],
                    axisLine: { lineStyle: { width: 10, color: [[0.5, '#34f5a8'], [0.8, '#ffc857'], [1, '#ff4d6d']] } },
                    pointer: { length: '55%', width: 3, itemStyle: { color: '#eafaff' } },
                    axisTick: { show: false },
                    splitLine: { show: false },
                    axisLabel: { show: false },
                    detail: {
                      valueAnimation: true,
                      formatter: '{value} bpm',
                      color: '#eafaff',
                      fontSize: 18,
                      fontWeight: 700,
                      offsetCenter: [0, '55%'],
                    },
                    data: [{ value: heartRate }],
                  },
                ],
              }}
            />
          </div>
        </div>
      </ZjCard>

      <ZjCard title="核心施救" delay={0.52}>
        <div className={`lra-term-compact prime${focusClass(spotlight, 'PRIME')}`}>
          <div className="lra-term-compact-head">
            <div className="icon"><HeartPulse size={18} /></div>
            <div>
              <div className="name">{prime?.displayName ?? '核心施救'}</div>
              <div className="meta">{translateRoleStatus(vm.incidentState?.roles?.PRIME?.status)}</div>
            </div>
            <span className={`online ${prime?.online ? 'on' : ''}`}>{prime?.online ? '在线' : '离线'}</span>
          </div>
          <div className="lra-term-mission">
            {prime ? vm.describeClientMission(prime) : '等待 AI 分派'}
          </div>
          <HealthChips summary={prime?.healthSignals} />
        </div>
      </ZjCard>

      <ZjCard title="AED 保障 · 环境清障" delay={0.74}>
        <div className="lra-term-duo">
          <div className={`lra-term-mini runner${focusClass(spotlight, 'RUNNER')}`}>
            <div className="icon"><Zap size={16} /></div>
            <div className="info">
              <div className="name">{runner?.displayName ?? 'AED 保障'}</div>
              <div className="meta">{translateRoleStatus(vm.incidentState?.roles?.RUNNER?.status)}</div>
            </div>
          </div>
          <div className={`lra-term-mini guide${focusClass(spotlight, 'GUIDE')}`}>
            <div className="icon"><Ambulance size={16} /></div>
            <div className="info">
              <div className="name">{guide?.displayName ?? '环境清障'}</div>
              <div className="meta">{translateRoleStatus(vm.incidentState?.roles?.GUIDE?.status)}</div>
            </div>
          </div>
        </div>
        <div className="lra-term-mission" style={{ marginTop: 8 }}>
          {runner
            ? vm.describeClientMission(runner)
            : guide
              ? vm.describeClientMission(guide)
              : '等待 AI 分派'}
        </div>
      </ZjCard>

      <ZjCard
        title="AI 临时任务"
        delay={0.9}
        extra={
          <span style={{ fontSize: 11, color: 'var(--lra-cyan-soft)' }}>
            {vm.incidentState?.aiTasks ? Object.keys(vm.incidentState.aiTasks).length : 0} 个
          </span>
        }
      >
        {vm.incidentState?.aiTasks && Object.keys(vm.incidentState.aiTasks).length > 0 ? (
          <div className="lra-ai-task-list">
            {Object.values(vm.incidentState.aiTasks)
              .sort((a, b) => b.createdAt - a.createdAt)
              .map((task) => (
                <div key={task.taskId} className="lra-ai-task">
                  <div className="lra-ai-task-head">
                    <AiTaskBadge status={task.status} />
                    <strong>{task.title}</strong>
                    <span className="lra-ai-task-priority">P{task.priority}</span>
                  </div>
                  <div className="lra-ai-task-meta">
                    {task.locationLabel ? <span>📍 {task.locationLabel}</span> : null}
                    {task.requires.length > 0 ? <span>物资：{task.requires.join('、')}</span> : null}
                  </div>
                  <div className="lra-ai-task-lines">
                    {aiTaskRows(task)
                      .slice(0, 3)
                      .map((row) => {
                        const score = task.matchScores[row.uid];
                        return (
                          <div key={row.uid} className={`lra-ai-task-line${row.isRunner ? ' runner' : ''}`}>
                            <span>{vm.clients.find((c) => c.userId === row.uid)?.displayName ?? row.uid}</span>
                            {row.isRunner && <em>runner</em>}
                            <b>{score != null ? score.toFixed(1) : '—'}</b>
                          </div>
                        );
                      })}
                  </div>
                </div>
              ))}
          </div>
        ) : (
          <div className="lra-ai-task-empty">暂无 AI 临时任务，手机端发起自然语言任务后在此联动展示。</div>
        )}
      </ZjCard>

      <ZjCard title="演示入口" delay={0.96}>
        <DemoQr incidentId={vm.incidentId} />
        <div className="lra-links-grid">
          {vm.demoShareLinks.map((link) => (
            <div key={link.key} className="lra-link-row">
              <span className="name">{link.label}</span>
              <button onClick={() => void vm.actions.copyDemoLink(link.key, link.url)}>复制</button>
            </div>
          ))}
        </div>
        <div className="lra-safety-note">
          仅用于协同训练与预实验展示，不替代 120、AED 语音提示或专业医护判断。
        </div>
      </ZjCard>
    </div>
  );
}
