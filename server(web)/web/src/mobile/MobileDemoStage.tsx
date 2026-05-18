import { ArrowLeft, ExternalLink, RefreshCw, Smartphone } from 'lucide-react';
import './mobile-demo-stage.css';

const demoFrames = [
  { key: 'patient', label: 'Patient', caption: '患者端' },
  { key: 'prime', label: 'PRIME', caption: '核心施救' },
  { key: 'runner', label: 'RUNNER', caption: 'AED 保障' },
  { key: 'guide', label: 'GUIDE', caption: '清障接驳' },
];

function MobileDemoStage() {
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
            <p>Life Reflex Arc</p>
            <h1>4端协同演示台</h1>
          </div>
        </div>
        <button className="mobile-demo-stage-icon-button" onClick={reloadAll} aria-label="刷新四端">
          <RefreshCw size={18} />
        </button>
      </header>

      <section className="mobile-demo-stage-grid">
        {demoFrames.map((frame) => {
          const src = `/mobile?demo=${frame.key}&slot=${frame.key}`;
          return (
            <article className="mobile-demo-stage-panel" key={frame.key}>
              <div className="mobile-demo-stage-panel-head">
                <div>
                  <strong>{frame.label}</strong>
                  <span>{frame.caption}</span>
                </div>
                <a href={src} target="_blank" rel="noreferrer" aria-label={`打开${frame.caption}`}>
                  <ExternalLink size={16} />
                </a>
              </div>
              <iframe className="mobile-demo-stage-frame" title={frame.caption} src={src} />
            </article>
          );
        })}
      </section>
    </main>
  );
}

export default MobileDemoStage;
