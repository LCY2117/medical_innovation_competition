import { useState } from "react";
import ActionButton from "../components/ActionButton";
import InfoDrawer from "../components/InfoDrawer";
import ResponderStandby from "../components/ResponderStandby";
import StatusBadge from "../components/StatusBadge";
import { useAction, useAutoDiscover } from "../lib/hooks";
import { useStore } from "../lib/store";
import type { AvailableAction, Role } from "../lib/types";

interface Config {
  role: Role;
  roleName: string;
  standbyTitle: string;
  standbySub: string;
  /** action → 按钮变体。 */
  variant: Record<string, "primary" | "danger" | "amber" | "neutral">;
  /** 无可用动作时的提示。 */
  waiting: (status: string) => { title: string; sub: string };
}

/** 通用响应端流程页：一屏一动作，按后端 available_actions 渲染主行动。 */
export default function ResponderFlowPage({ cfg }: { cfg: Config }) {
  const event = useStore((s) => s.event);
  const currentEventId = useStore((s) => s.currentEventId);
  const { submitting, run } = useAction();
  const [drawerOpen, setDrawerOpen] = useState(false);

  // M2 体验修复：登录后自动发现活跃事件并订阅，无需手输事件编号
  useAutoDiscover();

  if (!event || currentEventId === null) {
    return (
      <ResponderStandby title={cfg.standbyTitle} sub={cfg.standbySub} />
    );
  }

  const actions: AvailableAction[] = event.available_actions ?? [];
  const primary = actions[0];
  const secondary = actions.slice(1);
  const status = event.status;

  const w = cfg.waiting(status);

  return (
    <>
      <div className="row">
        <StatusBadge status={status} />
        <span className="text-faint" style={{ fontSize: 12 }}>
          事件 #{currentEventId} · {cfg.roleName}
        </span>
      </div>

      <div className="app-content" style={{ flex: 1 }}>
        {primary ? (
          <div className="flex-col" style={{ flex: 1, justifyContent: "center", gap: 24 }}>
            <ActionButton
              label={primary.label}
              action={primary.action}
              variant={cfg.variant[primary.action] ?? "primary"}
              disabled={submitting}
              submitting={submitting}
              onClick={() => run(primary.action)}
            />
            <div className="text-dim" style={{ textAlign: "center", fontSize: 13 }}>
              {primary.action === "HANDOVER_COMPLETED" ? "确认患者已交接给急救人员" : "按流程推进"}
            </div>
          </div>
        ) : (
          <div className="standby">
            <div className="standby-title">{w.title}</div>
            <div className="standby-sub">{w.sub}</div>
          </div>
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
    </>
  );
}
