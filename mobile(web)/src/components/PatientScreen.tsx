import React, { useState } from 'react';
import { HeartPulse, MapPin, RefreshCw, Siren } from 'lucide-react';
import { formatLocationLabel } from '../lib/domain';
import type { ClientInfo, GeoPoint, IncidentState, HealthSignalSummary } from '../lib/types';
import { formatElapsedLabel, healthStatItems, rescueProgress, shortId } from '../lib/rescue';

interface ScreenProps {
  session: { user: { userId: string; displayName: string; organization: string; professionIdentity: string } };
  incident: IncidentState | null;
  phaseLabel: string;
  syncLabel: string;
  notice: { kind: 'ok' | 'error' | 'info'; text: string } | null;
  busyAction: string | null;
  now: number;
  incidentStartedAt: number | null;
  progress: ReturnType<typeof rescueProgress>;
  healthStats: ReturnType<typeof healthStatItems>;
  location: GeoPoint | null;
  currentClient: ClientInfo | null;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  onLogout: () => void;
  onPatientSos: () => void;
  onCancelSos: () => void;
  onReportLocation: () => void;
  onOpenCurrent: () => void;
}

export function PatientScreen(props: ScreenProps) {
  const [sosConfirming, setSosConfirming] = useState(false);
  const {
    session, incident, phaseLabel, syncLabel, notice, busyAction,
    now, incidentStartedAt, progress, healthStats, location, currentClient,
    onToggleTheme, onLogout, onPatientSos, onCancelSos, onReportLocation, onOpenCurrent,
  } = props;

  const sosActive = incident?.sos?.status === 'ALERTING';
  const inRescue = incident && incident.phase !== 'CREATED';

  const handleSos = () => {
    if (!sosConfirming) {
      setSosConfirming(true);
      return;
    }
    setSosConfirming(false);
    onPatientSos();
  };

  const handleCancel = () => {
    setSosConfirming(false);
    onCancelSos();
  };

  return (
    <main className="mobile-shell">
      <header className="mobile-topbar">
        <div>
          <p className="mobile-kicker">生命反射弧</p>
          <h1>患者端</h1>
        </div>
        <div className="mobile-top-actions">
          <button className="mobile-icon-button" onClick={onToggleTheme} aria-label="切换主题">
            {props.theme === 'light' ? '🌙' : '☀️'}
          </button>
          <button className="mobile-icon-button" onClick={onLogout} aria-label="退出登录">⏻</button>
        </div>
      </header>

      <section className={`mobile-command-header patient`}>
        <div className="mobile-command-status">
          <span className={`sync-dot ${propsSyncClass(props)}`} />
          <span>{syncLabel}</span>
          <strong>{phaseLabel}</strong>
        </div>
        <div className="mobile-command-main">
          <div>
            <p className="mobile-kicker">{session.user.displayName}</p>
            <h2>{inRescue ? '等待救援' : sosActive ? 'SOS 已启动' : '我出事了，需要帮助'}</h2>
            <p>{inRescue ? '救援人员正在赶来，请留在当前位置等待。' : sosActive ? '系统正在确认并分派最近的急救力量。' : '点击下方按钮发出求救，系统会自动呼叫最近的急救力量。'}</p>
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

      <section className={`mobile-emergency-panel patient`}>
        {inRescue ? (
          <div className="mobile-rescue-block">
            <div className="mobile-rescue-head">
              <HeartPulse size={20} />
              <span>救援力量</span>
              <small>{progress.filter((p) => p.state === 'arrived').length}/{progress.length} 已到</small>
            </div>
            <div className="mobile-rescue-progress">
              {progress.map((item) => (
                <div key={item.role} className={`mobile-rescue-item ${item.state}`}>
                  <span className="mobile-rescue-dot" />
                  <span>{item.label}</span>
                  <small>{item.state === 'arrived' ? '已到' : item.state === 'onway' ? '赶来中' : '待分派'}</small>
                </div>
              ))}
            </div>
            {sosActive && (
              <button className="mobile-ghost-button" onClick={handleCancel} disabled={busyAction === 'sosCancel'}>
                取消 SOS
              </button>
            )}
          </div>
        ) : (
          <div className="mobile-sos-block">
            <p className="mobile-sos-lead">{sosConfirming ? '再次点击确认发出求救' : '请确认您确实需要帮助'}</p>
            <button
              className={`mobile-danger-button ${sosConfirming ? 'confirming' : ''}`}
              onClick={handleSos}
              disabled={!incident || busyAction === 'sos'}
            >
              {busyAction === 'sos' ? '启动中...' : sosConfirming ? <><Siren size={24} /> 确认 SOS</> : <><Siren size={24} /> 启动 SOS</>}
            </button>
            {sosConfirming && (
              <button className="mobile-ghost-button" onClick={() => setSosConfirming(false)}>
                取消
              </button>
            )}
          </div>
        )}
      </section>

      {!incident && (
        <section className="mobile-panel mobile-incident-panel">
          <div className="mobile-section-head">
            <div>
              <p className="mobile-kicker">事件</p>
              <h2>接入当前事件</h2>
            </div>
            <button className="mobile-small-button" onClick={onOpenCurrent}>
              <RefreshCw size={14} /> 同步
            </button>
          </div>
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
        {incident && (
          <div className="mobile-event-meta">
            <span>事件 {shortId(incident.incidentId)}</span>
            {incident.roles && <span>{Object.values(incident.roles).filter((r) => r.userId).length} 人已响应</span>}
          </div>
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
