import type { ReactNode } from 'react';
import { Activity, Lock, Unlock } from 'lucide-react';
import type { SpotlightDirective } from '@/shared/spotlight';
import { spotlightTargetLabel } from '@/shared/spotlight';
import { useClockText } from '../hooks/useDashboard';
import { formatElapsed } from '../helpers';

export function EcgLogo() {
  return (
    <div className="lra-title-eclogo">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 12h4l2-5 4 10 2-5h6" />
      </svg>
    </div>
  );
}

export function PanelFrame({
  title,
  icon,
  children,
  className = '',
  bodyClassName = '',
  headExtra,
}: {
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
  headExtra?: ReactNode;
}) {
  return (
    <div className={`lra-panel ${className}`}>
      <span className="lra-panel-corner-tr" />
      <span className="lra-panel-corner-bl" />
      <div className="lra-panel-head">
        <div className="lra-panel-title">
          {icon}
          <span>{title}</span>
        </div>
        <div style={{ marginLeft: 'auto' }}>{headExtra}</div>
      </div>
      <div className={`lra-panel-body lra-scroll ${bodyClassName}`}>{children}</div>
    </div>
  );
}

export function TopBar({
  wsConnected,
  incidentId,
  elapsedSeconds,
  phaseLabel,
  demoAdminReady,
}: {
  wsConnected: boolean;
  incidentId: string | null;
  elapsedSeconds: number;
  phaseLabel: string;
  demoAdminReady: boolean;
}) {
  const { time, date } = useClockText();
  return (
    <header className="lra-topbar">
      <div className="lra-title">
        <div className="lra-title-main">
          <EcgLogo />
          <h1>生命反射弧</h1>
          <span className="lra-title-sub">AI 应急指挥中心</span>
        </div>
      </div>
      <div className="lra-topbar-left">
        <div className={`lra-chip ${incidentId ? 'alert' : ''}`}>
          <span className="dot" />
          <span>{incidentId ? `事件 ${incidentId.slice(0, 8)} · ${phaseLabel}` : '待接入事件'}</span>
        </div>
        <div className={`lra-chip golden`}>
          <span className="dot" />
          <span>黄金时间 {incidentId ? formatElapsed(elapsedSeconds) : '--:--'}</span>
        </div>
        <div className={`lra-chip ${wsConnected ? '' : 'alert'}`}>
          {wsConnected ? <Unlock size={14} style={{ color: 'var(--lra-green)' }} /> : <Lock size={14} />}
          <span>{wsConnected ? '实时同步' : '恢复连接'}</span>
        </div>
      </div>
      <div className="lra-topbar-right">
        <div className={`lra-chip ${demoAdminReady ? '' : 'alert'}`}>
          <Activity size={14} />
          <span>{demoAdminReady ? '操作权限就绪' : '需要操作权限'}</span>
        </div>
        <div className="lra-header-date">
          <span>{date.split(' ')[0]}</span>
          <span>{time}</span>
        </div>
      </div>
    </header>
  );
}

export function SpotlightBanner({ directive }: { directive: SpotlightDirective | null }) {
  if (!directive) {
    return null;
  }
  return (
    <div
      key={directive.id}
      className={`lra-spotlight-banner ${directive.severity === 'critical' ? 'critical' : ''}`}
    >
      <div className="pulse-ring">
        <Activity size={18} />
      </div>
      <div>
        <div className="lra-spotlight-title">
          AI 聚焦 · {spotlightTargetLabel(directive.target)} · {directive.title}
        </div>
        <div className="lra-spotlight-message">{directive.message}</div>
      </div>
      <div style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--lra-text-faint)', whiteSpace: 'nowrap' }}>
        {directive.source === 'AI' ? 'AI 指令' : '状态机'}
      </div>
    </div>
  );
}
