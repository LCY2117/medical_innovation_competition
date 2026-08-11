import { useEffect, useState } from 'react';
import { ShieldCheck } from 'lucide-react';
import gsap from 'gsap';
import autofit from 'autofit.js';
import { useDashboard } from './hooks/useDashboard';
import { TopBar, SpotlightBanner } from './components/chrome';
import { LeftPanel, RightPanel } from './components/panels';
import { CenterPanel } from './components/center';
import { BottomBar } from './components/bottom';
import { IntroScreen } from './components/intro';
import { LoadingOverlay } from './components/LoadingOverlay';
import './bigscreen.css';

export default function LraBigScreen() {
  const vm = useDashboard();
  const [progress, setProgress] = useState(0);
  const [booted, setBooted] = useState(false);
  const [showIntro, setShowIntro] = useState(() => {
    if (typeof window === 'undefined') {
      return true;
    }
    const params = new URLSearchParams(window.location.search);
    return !params.get('incidentId');
  });

  // 浙江大屏同款 LOADING 进度
  useEffect(() => {
    const timer = window.setInterval(() => {
      setProgress((current) => {
        if (current >= 100) {
          window.clearInterval(timer);
          return 100;
        }
        return Math.min(100, current + 3 + Math.random() * 7);
      });
    }, 45);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (progress < 100) {
      return;
    }
    const timer = window.setTimeout(() => setBooted(true), 420);
    return () => window.clearTimeout(timer);
  }, [progress]);

  // 浙江大屏同款入场时间线：顶栏/底栏滑入 + 左右卡片横向错峰滑入
  useEffect(() => {
    if (!booted || showIntro) {
      return;
    }
    const timeline = gsap.timeline();
    timeline
      .to('.lra-topbar', { y: 0, opacity: 1, duration: 1.5, ease: 'power4.out' }, 0.5)
      .to('.lra-bottombar', { y: 0, opacity: 1, duration: 1.5, ease: 'power4.out' }, 0.5)
      .to('.lra-left-cards .lra-zj-panel', { x: 0, opacity: 1, stagger: 0.2, duration: 1.5, ease: 'power4.out' }, 1.0)
      .to('.lra-right-cards .lra-zj-panel', { x: 0, opacity: 1, stagger: 0.2, duration: 1.5, ease: 'power4.out' }, 1.0)
      .to('.lra-center-stage', { y: 0, opacity: 1, duration: 1.5, ease: 'power4.out' }, 1.0);
    return () => {
      timeline.kill();
    };
  }, [booted, showIntro]);

  // 浙江大屏同款缩放：autofit.js（dw 1920 / dh 1080 / resize）
  useEffect(() => {
    if (!booted) {
      return;
    }
    autofit.init({ el: '#lra-stage', dw: 1920, dh: 1080, resize: true });
    return () => {
      autofit.off();
    };
  }, [booted]);

  const handleIntroStart = async () => {
    setShowIntro(false);
    await vm.actions.bootstrapDemo();
  };

  return (
    <>
      <LoadingOverlay progress={progress} hidden={booted} />
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: '#01060d',
          overflow: 'hidden',
        }}
      >
        <div id="lra-stage" className="lra-stage">
          {showIntro ? (
            <IntroScreen onStart={() => void handleIntroStart()} />
          ) : (
            <div className="lra-screen">
              <div className="lra-frame lra-frame-left" />
              <div className="lra-frame lra-frame-right" />
              <TopBar
                wsConnected={vm.wsConnected}
                incidentId={vm.incidentId}
                elapsedSeconds={vm.elapsedSeconds}
                phaseLabel={vm.phaseLabel}
                demoAdminReady={!vm.visibleReadinessWarnings.some((item) => item.includes('管理权限'))}
              />

              <SpotlightBanner directive={vm.spotlight} />

              <div className="lra-main">
                <div className="lra-left-cards">
                  <LeftPanel vm={vm} />
                </div>
                <div className="lra-center-stage">
                  <CenterPanel vm={vm} />
                </div>
                <div className="lra-right-cards">
                  <RightPanel vm={vm} />
                </div>
              </div>

              <BottomBar vm={vm} />

              {vm.showAuditPanel && (
                <div
                  style={{
                    position: 'absolute',
                    right: 24,
                    top: 108,
                    width: 520,
                    maxHeight: 620,
                    zIndex: 50,
                    border: '1px solid rgba(52,245,168,0.4)',
                    background: 'rgba(3,16,28,0.96)',
                    boxShadow: '0 0 30px rgba(52,245,168,0.2)',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  <div className="lra-panel-head" style={{ borderBottomColor: 'rgba(52,245,168,0.3)' }}>
                    <div className="lra-panel-title" style={{ color: 'var(--lra-green)' }}>
                      <ShieldCheck size={15} />
                      安全审计留痕
                    </div>
                    <button
                      className="lra-btn"
                      onClick={() => vm.setShowAuditPanel(false)}
                      style={{ marginLeft: 'auto', height: 26, fontSize: 11 }}
                    >
                      收起
                    </button>
                  </div>
                  <div className="lra-panel-body lra-scroll" style={{ maxHeight: 560 }}>
                    {vm.auditEvents.length === 0 ? (
                      <div style={{ fontSize: 12, color: 'var(--lra-text-faint)', textAlign: 'center', padding: '30px 0' }}>
                        暂无审计事件，或当前口令无权读取。
                      </div>
                    ) : (
                      vm.auditEvents.slice(0, 12).map((event) => (
                        <div
                          key={event.eventId}
                          style={{
                            padding: '8px 10px',
                            marginBottom: 8,
                            border: '1px solid rgba(52,245,168,0.25)',
                            background: 'rgba(4,16,31,0.6)',
                            fontSize: 12,
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', color: '#dff7ff' }}>
                            <span>{event.eventType}</span>
                            <span className="lra-mono" style={{ color: 'var(--lra-text-faint)' }}>
                              {new Date(event.ts).toLocaleTimeString('zh-CN', { hour12: false })}
                            </span>
                          </div>
                          <div style={{ color: 'var(--lra-text-dim)', marginTop: 3 }}>
                            操作者 {event.actorId || event.actorType || '--'} · 结果 {event.outcome}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
