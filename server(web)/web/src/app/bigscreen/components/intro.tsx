import { Heart, Navigation, Smartphone, ChevronRight } from 'lucide-react';

export function IntroScreen({ onStart }: { onStart: () => void }) {
  return (
    <div className="lra-intro">
      <svg className="ecg" viewBox="0 0 520 90" fill="none" stroke="#17e5c3" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
        <path
          d="M0 45 H120 L150 45 L165 14 L190 78 L208 45 H300 L330 45 L345 20 L368 70 L386 45 H520"
          strokeDasharray="620"
        >
          <animate attributeName="stroke-dashoffset" values="620;0" dur="2.2s" fill="freeze" />
        </path>
        <circle cx="208" cy="45" r="4" fill="#17e5c3">
          <animate attributeName="cx" values="0;520" dur="5s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="1;0.2;1" dur="5s" repeatCount="indefinite" />
        </circle>
      </svg>
      <h1>生命反射弧</h1>
      <div className="sub">基于端侧 AI 的分布式急救任务协同系统</div>

      <div className="lra-intro-cards">
          <div className="lra-zj-card">
            <div className="lra-zj-card-hd">
              <span className="lra-zj-card-hd-title">痛点 · 时间错配</span>
              <span className="lra-zj-card-hd-dot" />
            </div>
            <div className="lra-zj-card-bd">
              <div className="ic-icon" style={{ color: 'var(--lra-red)', borderColor: 'rgba(255,77,109,0.55)' }}>
                <Heart size={22} />
              </div>
              <p>
                急救车平均到达 12-15 分钟，心脏骤停黄金抢救仅 4 分钟。
                现场协同存在空窗风险。
              </p>
            </div>
          </div>
          <div className="lra-zj-card">
            <div className="lra-zj-card-hd">
              <span className="lra-zj-card-hd-title">方案 · 任务拆解</span>
              <span className="lra-zj-card-hd-dot" />
            </div>
            <div className="lra-zj-card-bd">
              <div className="ic-icon" style={{ color: 'var(--lra-cyan)', borderColor: 'rgba(23,229,195,0.55)' }}>
                <Navigation size={22} />
              </div>
              <p>
                核心施救单（CPR）· 资源保障单（AED 转运）· 环境清障单（通道疏通），
                AI 将应急任务秒级拆分并分发。
              </p>
            </div>
          </div>
          <div className="lra-zj-card">
            <div className="lra-zj-card-hd">
              <span className="lra-zj-card-hd-title">核心 · 端侧协同</span>
              <span className="lra-zj-card-hd-dot" />
            </div>
            <div className="lra-zj-card-bd">
              <div className="ic-icon" style={{ color: 'var(--lra-amber)', borderColor: 'rgba(255,200,87,0.55)' }}>
                <Smartphone size={22} />
              </div>
              <p>
                多源感知触发、毫秒级任务分发、物理与数字握手，
                全链路实时状态同步。
              </p>
            </div>
          </div>
        </div>

        <button className="lra-intro-start" onClick={onStart}>
          开始全流程预实验
          <ChevronRight size={20} />
        </button>
    </div>
  );
}
