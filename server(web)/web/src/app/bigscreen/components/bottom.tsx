import { useState } from 'react';
import type { DashboardViewModel } from '../hooks/useDashboard';
import { DemoDriver } from './DemoDriver';
import arrowBig from '../assets/zj-arrow-big.svg';
import arrowSmall from '../assets/zj-arrow-small.svg';

export function BottomBar({ vm }: { vm: DashboardViewModel }) {
  const [showAdmin, setShowAdmin] = useState(false);
  const [showDriver, setShowDriver] = useState(false);
  return (
    <>
      <DemoDriver vm={vm} open={showDriver} onClose={() => setShowDriver(false)} />
      {showAdmin && (
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            bottom: 90,
            zIndex: 40,
            padding: '12px 24px',
            background: 'rgba(3,12,24,0.96)',
            borderTop: '1px solid rgba(78,190,255,0.3)',
            display: 'flex',
            alignItems: 'center',
            gap: 16,
          }}
        >
          <span style={{ fontSize: 12, color: 'var(--lra-text-dim)' }}>演示密码</span>
          <input
            value={vm.demoAdminToken}
            onChange={(event) => vm.actions.setdemoAdminToken(event.target.value)}
            type="password"
            placeholder="输入演示密码"
            style={{
              height: 30,
              width: 160,
              background: 'rgba(4,16,31,0.8)',
              border: '1px solid rgba(78,190,255,0.35)',
              color: '#eafaff',
              padding: '0 10px',
              fontSize: 12,
              outline: 'none',
            }}
          />
          <span style={{ fontSize: 11, color: 'var(--lra-text-faint)' }}>
            仅演示口令验证，服务器配置 LRA_demo_ADMIN_TOKEN 后填写；未配置则无需密码
          </span>
          <button className="lra-btn" onClick={() => setShowAdmin(false)} style={{ marginLeft: 'auto' }}>
            收起
          </button>
        </div>
      )}
      <footer className="lra-bottombar">
        <div className="lra-bottom-arrow">
          <img src={arrowBig} alt="" />
          <img src={arrowSmall} alt="" />
        </div>
        <div className="lra-bottom-menu">
          <button className="lra-menu-item is-active" onClick={() => void vm.actions.bootstrapDemo()}>
            <span>演示场景</span>
          </button>
          <button className="lra-menu-item" onClick={vm.actions.openMobileDemoStage}>
            <span>4端演示</span>
          </button>
          <button className="lra-menu-item" onClick={() => void vm.actions.openAllMobileTerminals()}>
            <span>打开手机端</span>
          </button>
          <button className="lra-menu-item" onClick={() => void vm.actions.exportExperiment()}>
            <span>导出数据</span>
          </button>
          <button className="lra-menu-item" onClick={() => void vm.actions.exportExperimentPackage()}>
            <span>证据包</span>
          </button>
          <button className="lra-menu-item" onClick={vm.actions.exportPreflightReport}>
            <span>自检</span>
          </button>
          <button className="lra-menu-item" onClick={() => void vm.actions.loadAuditEvents()}>
            <span>审计</span>
          </button>
          <button className="lra-menu-item" onClick={() => setShowDriver((visible) => !visible)}>
            <span>单屏演示</span>
          </button>
          <button className="lra-menu-item" onClick={() => setShowAdmin((visible) => !visible)}>
            <span>管理</span>
          </button>
          <button className="lra-menu-item" onClick={() => void vm.actions.resetCurrentIncident()} title="重置当前事件">
            <span>重置</span>
          </button>
        </div>
        <div className="lra-bottom-status">
          {vm.readinessReady ? '演示前置条件就绪' : `${vm.visibleReadinessWarnings.length || 1} 项待确认`}
          {vm.errorMessage && <span style={{ color: 'var(--lra-red)' }}> · {vm.errorMessage}</span>}
          {vm.successMessage && <span style={{ color: 'var(--lra-green)' }}> · {vm.successMessage}</span>}
        </div>
        <div className="lra-bottom-arrow is-reverse">
          <img src={arrowBig} alt="" />
          <img src={arrowSmall} alt="" />
        </div>
      </footer>
    </>
  );
}
