import React, { useMemo } from 'react';
import { Map } from 'lucide-react';
import { SceneMap } from '../scene/SceneMap';
import { buildSceneModel } from '../scene/sceneModel';
import type { DashboardViewModel } from '../hooks/useDashboard';

class MapErrorBoundary extends React.Component<{ children: React.ReactNode }, { error: Error | null }> {
  state: { error: Error | null } = { error: null };
  static getDerivedStateFromError(error: Error) {
    return { error };
  }
  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('[SceneMap] crashed:', error, info.componentStack);
  }
  render() {
    if (this.state.error) {
      return (
        <div style={{ position: 'absolute', inset: 0, display: 'grid', placeItems: 'center', background: 'rgba(3,12,24,0.92)', color: '#ffb4c0', fontSize: 13, padding: 24, textAlign: 'center', zIndex: 30 }}>
          <div>
<div style={{ fontSize: 15, fontWeight: 700, marginBottom: 8, color: '#fff' }}>Map component crashed (isolated, other panels unaffected)</div>
            <div style={{ opacity: 0.9, wordBreak: 'break-all' }}>{String(this.state.error.message ?? this.state.error)}</div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export function CenterPanel({ vm }: { vm: DashboardViewModel }) {
  const model = useMemo(
    () => buildSceneModel(vm.incidentState, vm.clients, vm.visibleAedSites, vm.spotlight?.target ?? null),
    [vm.incidentState, vm.clients, vm.visibleAedSites, vm.spotlight?.target],
  );
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14, height: '100%', overflow: 'hidden' }}>
      <div className="lra-scene" style={{ flex: 1, minHeight: 0 }}>
        <div
          style={{
            position: 'absolute',
            left: 16,
            top: 14,
            zIndex: 12,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            fontSize: 14,
            fontWeight: 800,
            letterSpacing: 2,
            color: '#eaffff',
            textShadow: '0 0 12px rgba(78,190,255,0.6)',
          }}
        >
          <Map size={16} style={{ color: 'var(--lra-cyan)' }} />
          现场协同态势
        </div>
        <div
          style={{
            position: 'absolute',
            right: 16,
            top: 14,
            zIndex: 12,
            fontSize: 12,
            color: 'var(--lra-text-dim)',
          }}
        >
          阶段 · {vm.phaseLabel}
        </div>
        <div className="lra-scene-legend">
          <div className="item"><span className="swatch" style={{ background: '#ff4d6d' }} />患者</div>
          <div className="item"><span className="swatch" style={{ background: '#34f5a8' }} />核心施救</div>
          <div className="item"><span className="swatch" style={{ background: '#4be3ff' }} />AED 保障</div>
          <div className="item"><span className="swatch" style={{ background: '#ffc857' }} />环境清障</div>
          <div className="item"><span className="swatch" style={{ background: '#17e5c3' }} />AED 点位</div>
          <div className="item"><span className="swatch" style={{ background: '#eef6ff' }} />120 急救</div>
        </div>
        <MapErrorBoundary>
          <SceneMap model={model} />
        </MapErrorBoundary>
      </div>

      <div
        style={{
          height: 120,
          border: '1px solid rgba(78,190,255,0.25)',
          background: 'linear-gradient(160deg, rgba(7,26,44,0.8), rgba(3,12,24,0.75))',
          padding: '0 14px',
          flexShrink: 0,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, height: 28, fontSize: 12, letterSpacing: 2, color: 'var(--lra-text-dim)', fontWeight: 700 }}>
          演示流程时间线
        </div>
        <div className="lra-timeline">
          {vm.demoFlowSteps.map((step, index) => (
            <div key={step.title} className={`lra-timeline-item ${step.active ? 'active' : ''} ${step.complete ? 'active' : ''}`}>
              <span className="node" />
              <div className="tl-label">{step.title}</div>
              <div className="tl-detail">{step.detail}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
