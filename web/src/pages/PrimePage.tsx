import { useState } from "react";
import ActionButton from "../components/ActionButton";
import InfoDrawer from "../components/InfoDrawer";
import Metronome from "../components/Metronome";
import ResponderStandby from "../components/ResponderStandby";
import StatusBadge from "../components/StatusBadge";
import { useAction, useAutoDiscover } from "../lib/hooks";
import { useStore } from "../lib/store";
import type { AvailableAction } from "../lib/types";

/** 一屏一动作的主行动变体映射。 */
function variantOf(action: string): "primary" | "danger" | "amber" | "neutral" {
  if (action === "AED_SHOCK_DELIVERED") return "danger";
  if (action === "AED_ANALYSIS_STARTED") return "amber";
  if (action === "HANDOVER_COMPLETED") return "primary";
  return "primary";
}

/** 核心施救端（PRIME）：确认响应 → CPR 节拍器 → AED 分析 → 除颤 → 交接。 */
export default function PrimePage() {
  const event = useStore((s) => s.event);
  const currentEventId = useStore((s) => s.currentEventId);
  const wsStatus = useStore((s) => s.wsStatus);
  const { submitting, run } = useAction();
  const [drawerOpen, setDrawerOpen] = useState(false);

  // M2 体验修复：登录后自动发现活跃事件并订阅，无需手输事件编号
  useAutoDiscover();

  if (!event || currentEventId === null) {
    return <ResponderStandby title="等待任务分派" sub="您将被匹配为核心施救（PRIME）" />;
  }

  const actions: AvailableAction[] = event.available_actions ?? [];
  const primary = actions[0];
  const secondary = actions.slice(1);
  const status = event.status;

  // CPR 进行中（PRIME 无可用动作）→ 节拍器主屏
  const showMetronome =
    primary === undefined && (status === "CPR" || status === "AED_PICKED");

  return (
    <>
      <div className="row">
        <StatusBadge status={status} />
        <span className="text-faint" style={{ fontSize: 12 }}>
          事件 #{currentEventId} · PRIME
        </span>
      </div>

      <div className="app-content" style={{ flex: 1 }}>
        {showMetronome ? (
          <Metronome running={status === "CPR" || status === "AED_PICKED"} shockCount={event.shock_count} />
        ) : primary ? (
          <div className="flex-col" style={{ flex: 1, justifyContent: "center", gap: 24 }}>
            <ActionButton
              label={primary.label}
              action={primary.action}
              variant={variantOf(primary.action)}
              disabled={submitting}
              submitting={submitting}
              onClick={() => run(primary.action)}
            />
            <div className="text-dim" style={{ textAlign: "center", fontSize: 13 }}>
              {primary.action === "CPR_STARTED"
                ? "确认后进入 110 BPM 按压节拍器"
                : primary.action === "AED_SHOCK_DELIVERED"
                  ? "电击将自动释放 · 请确保无人接触患者"
                  : "根据救援流程推进"}
            </div>
          </div>
        ) : (
          <WaitingScreen status={status} shockCount={event.shock_count} />
        )}
      </div>

      <button className="drawer-tab" onClick={() => setDrawerOpen(true)}>
        查看事件详情
      </button>

      <InfoDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        secondary={secondary}
      />
      {wsStatus === "reconnecting" && <div className="toast">连接断开，正在重连…</div>}
    </>
  );
}

function WaitingScreen({ status, shockCount }: { status: string; shockCount: number }) {
  return (
    <div className="standby">
      <div className="standby-title">
        {status === "AED_ANALYZING"
          ? "AED 分析中"
          : status === "HANDOVER"
            ? "交接中"
            : status === "ARCHIVED"
              ? "事件已归档"
              : "等待下一步"}
      </div>
      <div className="standby-sub">
        {status === "AED_ANALYZING"
          ? "请远离患者，等待分析结果"
          : status === "HANDOVER"
            ? "等待调度系统归档事件"
            : shockCount >= 3
              ? "已达除颤上限（3 次）"
              : "无可用操作，请等待"}
      </div>
    </div>
  );
}
