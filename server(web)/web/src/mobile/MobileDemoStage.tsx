import { ArrowLeft, ExternalLink, RefreshCw, Smartphone } from 'lucide-react';
import './mobile-demo-stage.css';

const demoFrames = [
  { key: 'patient', label: '患者端', caption: '触发 SOS' },
  { key: 'prime', label: '核心施救', caption: 'CPR 与 AED 分析' },
  { key: 'runner', label: 'AED 保障', caption: '取送设备' },
  { key: 'guide', label: '清障接驳', caption: '通道与救护车接应' },
];

const runbookSteps = [
  '患者端启动 SOS',
  '等待智能分派',
  '核心施救开始 CPR',
  'AED 保障取送设备',
  '清障接驳完成交接',
  '归档并下载证据包',
];

function MobileDemoStage() {
  const incidentId = new URLSearchParams(window.location.search).get('incidentId')?.trim() ?? '';

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
            <h1>4端协同演示台</h1>
          </div>
        </div>
        <button className="mobile-demo-stage-icon-button" onClick={reloadAll} aria-label="刷新四端">
          <RefreshCw size={18} />
        </button>
      </header>

      <section className="mobile-demo-stage-runbook" aria-label="演示导播步骤">
        {runbookSteps.map((step, index) => (
          <div className="mobile-demo-stage-runbook-step" key={step}>
            <span>{index + 1}</span>
            <strong>{step}</strong>
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
            <article className="mobile-demo-stage-panel" key={frame.key}>
              <div className="mobile-demo-stage-panel-head">
                <div>
                  <strong>{frame.label}</strong>
                  <span>{frame.caption}</span>
                </div>
                <a href={src} target="_blank" rel="noreferrer" aria-label={`打开${frame.label}`}>
                  <ExternalLink size={16} />
                </a>
              </div>
              <iframe className="mobile-demo-stage-frame" title={frame.label} src={src} />
            </article>
          );
        })}
      </section>
    </main>
  );
}

export default MobileDemoStage;
