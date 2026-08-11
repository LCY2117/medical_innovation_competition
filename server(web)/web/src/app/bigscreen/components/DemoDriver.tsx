import { Play, RotateCcw, X } from 'lucide-react';
import type { RoleName } from '@/shared/types';
import {
  hasGuideCompleted,
  hasPrimeStarted,
  hasRunnerDelivered,
  hasRunnerPicked,
  isAedAnalyzing,
  isRoleJoined,
  isShockDelivered,
  translatePhaseLabel,
} from '@/shared/domain';
import type { DashboardViewModel } from '../hooks/useDashboard';

const PHASE_RANK: Record<string, number> = {
  CREATED: 0,
  DISPATCHING: 1,
  DISPATCHED: 2,
  CPR: 3,
  AED_PICKED: 4,
  AED_DELIVERED: 5,
  AED_ANALYZING: 6,
  SHOCK_DELIVERED: 7,
  HANDOVER: 8,
  ARCHIVED: 9,
};

export function DemoDriver({ vm, open, onClose }: { vm: DashboardViewModel; open: boolean; onClose: () => void }) {
  if (!open) {
    return null;
  }

  const phase = vm.incidentState?.phase ?? null;
  const phaseRank = phase ? PHASE_RANK[phase] ?? 2 : -1;
  const primeJoined = isRoleJoined(vm.incidentState?.roles?.PRIME?.status);
  const runnerJoined = isRoleJoined(vm.incidentState?.roles?.RUNNER?.status);
  const guideJoined = isRoleJoined(vm.incidentState?.roles?.GUIDE?.status);
  const allJoined = primeJoined && runnerJoined && guideJoined;

  interface Step {
    key: string;
    label: string;
    detail: string;
    done: boolean;
    active: boolean;
    enabled: boolean;
    run: () => void;
  }

  const steps: Step[] = [
    {
      key: 'init',
      label: '初始化场景',
      detail: '生成患者、救援者、AED 点位',
      done: phaseRank >= 0,
      active: phaseRank < 0,
      enabled: true,
      run: () => void vm.actions.bootstrapDemo(),
    },
    {
      key: 'sos',
      label: '患者 SOS · AI 分派',
      detail: '触发告警并启动智能调度',
      done: phaseRank >= 1 || Boolean(vm.incidentState?.patientUserId),
      active: phaseRank === 0,
      enabled: phaseRank === 0,
      run: () => void vm.actions.designatePatient('demo-patient'),
    },
    {
      key: 'join',
      label: '三端响应',
      detail: '核心施救 / AED 保障 / 环境清障确认响应',
      done: allJoined,
      active: phaseRank >= 2 && !allJoined,
      enabled: phaseRank >= 2 && !allJoined,
      run: () => {
        void vm.actions.joinRole('PRIME');
        void vm.actions.joinRole('RUNNER');
        void vm.actions.joinRole('GUIDE');
      },
    },
    {
      key: 'cpr',
      label: 'CPR 开始',
      detail: '核心施救端启动胸外按压',
      done: hasPrimeStarted(vm.incidentState),
      active: phaseRank === 3 && !hasPrimeStarted(vm.incidentState),
      enabled: primeJoined && !hasPrimeStarted(vm.incidentState),
      run: () => void vm.actions.postRoleAction('CPR_STARTED', 'PRIME'),
    },
    {
      key: 'pick',
      label: 'AED 取到',
      detail: '取送者取到 AED 并回送',
      done: hasRunnerPicked(vm.incidentState),
      active: phaseRank === 4 && !hasRunnerPicked(vm.incidentState),
      enabled: runnerJoined && phaseRank >= 3 && !hasRunnerPicked(vm.incidentState),
      run: () => void vm.actions.postRoleAction('AED_PICKED', 'RUNNER'),
    },
    {
      key: 'deliver',
      label: 'AED 送达',
      detail: '设备送达患者位置',
      done: hasRunnerDelivered(vm.incidentState),
      active: phaseRank === 5 && !hasRunnerDelivered(vm.incidentState),
      enabled: hasRunnerPicked(vm.incidentState) && !hasRunnerDelivered(vm.incidentState),
      run: () => void vm.actions.postRoleAction('AED_DELIVERED', 'RUNNER'),
    },
    {
      key: 'analyze',
      label: 'AED 分析',
      detail: '核心施救端执行心律分析',
      done: isAedAnalyzing(vm.incidentState),
      active: phaseRank === 6 && !isAedAnalyzing(vm.incidentState),
      enabled: hasRunnerDelivered(vm.incidentState) && !isAedAnalyzing(vm.incidentState),
      run: () => void vm.actions.postRoleAction('AED_ANALYSIS_STARTED', 'PRIME'),
    },
    {
      key: 'shock',
      label: '除颤',
      detail: '记录一次 AED 除颤',
      done: isShockDelivered(vm.incidentState),
      active: phaseRank === 7 && !isShockDelivered(vm.incidentState),
      enabled: isAedAnalyzing(vm.incidentState) && !isShockDelivered(vm.incidentState),
      run: () => void vm.actions.postRoleAction('AED_SHOCK_DELIVERED', 'PRIME'),
    },
    {
      key: 'ambulance',
      label: '救护车到场',
      detail: '清障接驳端引导救护车',
      done: hasGuideCompleted(vm.incidentState),
      active: phaseRank === 8 && !hasGuideCompleted(vm.incidentState),
      enabled: isShockDelivered(vm.incidentState) && !hasGuideCompleted(vm.incidentState),
      run: () => void vm.actions.postRoleAction('AMBULANCE_ARRIVED', 'GUIDE'),
    },
    {
      key: 'handover',
      label: '交接归档',
      detail: '专业急救力量接管并归档',
      done: phaseRank >= 9,
      active: phaseRank === 8 && hasGuideCompleted(vm.incidentState),
      enabled: hasGuideCompleted(vm.incidentState) && phaseRank < 9,
      run: () => void vm.actions.postRoleAction('HANDOVER_COMPLETED', 'GUIDE'),
    },
    {
      key: 'reset',
      label: '重置',
      detail: '回到监测状态重新演示',
      done: false,
      active: false,
      enabled: true,
      run: () => void vm.actions.resetCurrentIncident(),
    },
  ];

  const nextStep = steps.find((step) => step.active && step.enabled) ?? null;

  return (
    <div
      style={{
        position: 'absolute',
        right: 20,
        top: 100,
        bottom: 90,
        width: 340,
        zIndex: 45,
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid rgba(23,229,195,0.4)',
        background: 'rgba(3,14,26,0.96)',
        boxShadow: '0 0 30px rgba(23,229,195,0.18)',
      }}
    >
      <div className="lra-panel-head" style={{ height: 44, padding: '0 12px' }}>
        <span className="lra-panel-hd-title" style={{ left: 16, fontSize: 16 }}>
          单屏演示推进器
        </span>
        <button
          onClick={onClose}
          style={{ marginLeft: 'auto', background: 'none', border: 'none', color: 'var(--lra-text-dim)', cursor: 'pointer' }}
        >
          <X size={16} />
        </button>
      </div>

      <div style={{ padding: '10px 14px', borderBottom: '1px solid rgba(78,190,255,0.15)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 12, color: 'var(--lra-text-dim)' }}>
          当前阶段
          <span style={{ marginLeft: 'auto', color: 'var(--lra-cyan-soft)', fontWeight: 700 }}>
            {translatePhaseLabel(phase)}
          </span>
        </div>
        {nextStep && (
          <div style={{ marginTop: 6, fontSize: 11, color: 'var(--lra-amber)' }}>
            下一步：{nextStep.label}
          </div>
        )}
        {vm.errorMessage && (
          <div style={{ marginTop: 6, fontSize: 11, color: 'var(--lra-red)' }}>{vm.errorMessage}</div>
        )}
        {vm.successMessage && (
          <div style={{ marginTop: 6, fontSize: 11, color: 'var(--lra-green)' }}>{vm.successMessage}</div>
        )}
      </div>

      <div className="lra-scroll" style={{ flex: 1, overflowY: 'auto', padding: '10px 12px' }}>
        {steps.map((step, index) => (
          <button
            key={step.key}
            onClick={step.run}
            disabled={!step.enabled}
            className={`lra-driver-step ${step.done ? 'done' : ''} ${step.active ? 'active' : ''}`}
          >
            <span className="badge">{step.done ? '✓' : index + 1}</span>
            <span style={{ flex: 1, minWidth: 0 }}>
              <span className="label">{step.label}</span>
              <span className="detail">{step.detail}</span>
            </span>
            <Play size={13} style={{ opacity: step.enabled ? 1 : 0.25, flexShrink: 0 }} />
          </button>
        ))}
        <div style={{ marginTop: 10, fontSize: 10, lineHeight: 1.7, color: 'var(--lra-text-faint)' }}>
          说明：单屏演示时所有终端动作由大屏代替完成，无需打开手机端。
        </div>
      </div>
    </div>
  );
}

export type { RoleName };
