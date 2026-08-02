import React, { useState } from 'react';
import { HeartPulse, MapPin, Shield, Zap } from 'lucide-react';
import { formatLocationLabel, translateRoleStatus } from '../lib/domain';
import type { ClientInfo, GeoPoint, HealthSignalSummary, IncidentState, RoleName } from '../lib/types';
import { formatElapsedLabel, healthStatItems, primeNextStep, roleAction, roleLabelFor } from '../lib/rescue';
import { CprMetronome } from './CprMetronome';

interface ScreenProps {
  session: { user: { userId: string; displayName: string; organization: string; professionIdentity: string }; demoPersona?: string };
  incident: IncidentState | null;
  phaseLabel: string;
  syncLabel: string;
  notice: { kind: 'ok' | 'error' | 'info'; text: string } | null;
  busyAction: string | null;
  now: number;
  incidentStartedAt: number | null;
  activeRole: RoleName | null;
  action: ReturnType<typeof roleAction> | null;
  primeStep: ReturnType<typeof primeNextStep> | null;
  healthStats: ReturnType<typeof healthStatItems>;
  location: GeoPoint | null;
  currentClient: ClientInfo | null;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  onLogout: () => void;
  onJoinRole: (role: RoleName) => void;
  onExecuteAction: () => void;
  onReportLocation: () => void;
}

export function ResponderScreen(props: ScreenProps) {
  const {
    session, incident, phaseLabel, syncLabel, notice, busyAction, now, incidentStartedAt,
    activeRole, action, primeStep, healthStats, location, currentClient,
    onToggleTheme, onLogout, onExecuteAction, onReportLocation,
  } = props;
  const [showManualJoin, setShowManualJoin] = useState(false);

  const roleIcon = (role: RoleName | null) => {
    if (role === 'PRIME') return <HeartPulse size={28} />;
    if (role === 'RUNNER') return <Zap size={28} />;
    return <Shield size={28} />;
  };

  const actionDisabled = action?.disabled || Boolean(busyAction);
  const roleTone = activeRole ? `role-${activeRole.toLowerCase()}` : 'standby';

  return (
    <main className="mobile-shell">
      <header className="mobile-topbar">
        <div>
          <p className="mobile-kicker">生命反射弧</p>
          <h1>{roleLabelFor(activeRole)}</h1>
        </div>
        <div className="mobile-top-actions">
          <button className="mobile-icon-button" onClick={onToggleTheme} aria-label="切换主题">
            {props.theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button className="mobile-icon-button" onClick={onLogout} aria-label="退出登录">⏻</button>
        </div>
      </header>

      <section className={`mobile-command-header ${roleTone}`}>
        <div className="mobile-command-status">
          <span className={`sync-dot ${propsSyncClass(props)}`} />
          <span>{syncLabel}</span>
          <strong>{phaseLabel}</strong>
        </div>
        <div className="mobile-command-main">
          <div>
            <p className="mobile-kicker">{roleLabelFor(activeRole)}</p>
            <h2>{action ? action.title : '在线待命'}</h2>
            {action?.hint && <p>{action.hint}</p>}
            {!action && incident && <p>等待患者端启动 SOS 后，系统会自动分配任务。</p>}
          </div>
          {incidentStartedAt && (
            <div className="mobile-command-metric">
              <span>黄金时间</span>
              <strong>{formatElapsedLabel(incidentStartedAt, now)}</strong>
            </div>
          )}
        </div>
      </section>

      {notice && <div className={`mobile-notice ${notice.kind}`}>{notice.text}</div>}

      <section className={`mobile-emergency-panel responder ${roleTone}`}>
        {action ? (
          <div className="mobile-action-row">
            <div>
              {roleIcon(activeRole)}
              <p className="mobile-kicker">当前动作</p>
              <h2>{action.title}</h2>
              {action.hint && <p>{action.hint}</p>}
            </div>
          </div>
        ) : (
          <div className="mobile-action-row">
            <div>
              <Shield size={28} />
              <p className="mobile-kicker">待命终端</p>
              <h2>等待任务分配</h2>
              <p>保持页面在线，患者端启动 SOS 后系统会自动分配角色。</p>
            </div>
          </div>
        )}

        {primeStep && (
          <div className={`mobile-next-step ${primeStep.tone}`}>
            <strong>{primeStep.title}</strong>
            <p>{primeStep.body}</p>
          </div>
        )}

        {activeRole === 'PRIME' && incident?.roles.PRIME?.status === 'CPR_STARTED' && (
          <CprMetronome active />
        )}

        {action && !action.disabled ? (
          <button className={`mobile-primary-button ${activeRole === 'PRIME' ? 'prime' : activeRole === 'RUNNER' ? 'runner' : 'guide'}`} onClick={onExecuteAction} disabled={actionDisabled}>
            {busyAction ? '提交中...' : action.buttonLabel}
          </button>
        ) : (
          <button className="mobile-ghost-button" disabled>
            {activeRole ? '等待下一步' : '待命中'}
          </button>
        )}
      </section>

      {activeRole && (
        <section className="mobile-role-status-card">
          <div className="mobile-role-status-head">
            <p className="mobile-kicker">我的任务</p>
            <strong>{activeRole === 'PRIME' ? '核心施救' : activeRole === 'RUNNER' ? 'AED 保障' : '环境清障'}</strong>
          </div>
          {incident && (
            <div className="mobile-role-status-line">
              <span>状态</span>
              <strong>{translateRoleStatus(incident.roles[activeRole]?.status)}</strong>
            </div>
          )}
        </section>
      )}

      {!activeRole && incident && (
        <section className="mobile-panel mobile-join-panel">
          <div className="mobile-section-head">
            <div>
              <p className="mobile-kicker">任务</p>
              <h2>手动接单</h2>
            </div>
            <button className="mobile-small-button" onClick={() => setShowManualJoin((v) => !v)}>
              {showManualJoin ? '收起' : '展开'}
            </button>
          </div>
          {showManualJoin && (
            <div className="mobile-role-grid">
              {(['PRIME', 'RUNNER', 'GUIDE'] as RoleName[]).map((role) => (
                <button key={role} className="mobile-role-join" onClick={() => props.onJoinRole(role)} disabled={Boolean(busyAction)}>
                  {roleLabelFor(role)}
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      <section className="mobile-identity-card">
        <div className="mobile-identity-main">
          <div className="mobile-user-avatar">
            <HeartPulse size={22} />
          </div>
          <div>
            <p className="mobile-kicker">当前终端</p>
            <strong>{session.user.displayName}</strong>
            <p>{session.user.organization} · {session.user.professionIdentity}</p>
          </div>
        </div>
        <div className="mobile-location-line">
          <MapPin size={14} />
          <span>{location ? formatLocationLabel(location) : '未上报位置'}</span>
          <button className="mobile-location-refresh" onClick={onReportLocation} title="上报位置">定位</button>
        </div>
        {healthStats.length > 0 && (
          <details className="mobile-health-details">
            <summary className="mobile-health-summary">
              <HeartPulse size={14} />
              健康数据
            </summary>
            <div className="mobile-health-stats">
              {healthStats.map((item) => (
                <div key={item.label} className={item.tone ? `tone-${item.tone}` : ''}>
                  <span>{item.label}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
            {currentClient?.healthSignals?.note && (
              <div className="mobile-health-line">{currentClient.healthSignals.note}</div>
            )}
          </details>
        )}
      </section>
    </main>
  );
}

function propsSyncClass(props: ScreenProps): string {
  const map: Record<string, string> = {
    live: 'live', connecting: 'connecting', reconnecting: 'reconnecting', offline: 'offline',
  };
  return map[props.syncLabel] ?? '';
}
