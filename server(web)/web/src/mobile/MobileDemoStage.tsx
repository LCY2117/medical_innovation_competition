import { ArrowLeft, ExternalLink, RefreshCw, ShieldCheck, Smartphone } from 'lucide-react';
import './mobile-demo-stage.css';

const demoFrames = [
  { key: 'patient', label: '患者', caption: 'SOS 触发', tone: 'patient' },
  { key: 'prime', label: '施救', caption: 'CPR / AED', tone: 'prime' },
  { key: 'runner', label: 'AED', caption: '取送设备', tone: 'runner' },
  { key: 'guide', label: '接应', caption: '通道清障', tone: 'guide' },
];

const runbookSteps = [
  'SOS',
  '分派',
  'CPR',
  'AED',
  '接应',
  '归档',
];

function MobileDemoStage() {
  const incidentId = new URLSearchParams(window.location.search).get('incidentId')?.trim() ?? '';
  const shortIncidentId = incidentId ? `${incidentId.slice(0, 8)}...${incidentId.slice(-4)}` : '未绑定';
  const incidentStatus = incidentId ? '已绑定当前事件' : '未绑定事件';
  const incidentHint = incidentId
    ? '四个终端将共享同一事件编号，适合现场导播和评委同步观察。'
    : '请先从总控台初始化演示场景，再打开 4 端导播台。';

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
        <ol className="mobile-demo-stage-runbook" aria-label="演示导播步骤">
          {runbookSteps.map((step, index) => (
            <li className="mobile-demo-stage-runbook-step" key={step}>
              <span>{index + 1}</span>
              <strong>{step}</strong>
            </li>
          ))}
        </ol>
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
                  <span>{frame.caption}</span>
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
