import { useState } from "react";
import Countdown from "../components/Countdown";
import ConfirmModal from "../components/ConfirmModal";
import InfoDrawer from "../components/InfoDrawer";
import ProgressCard from "../components/ProgressCard";
import StatusBadge from "../components/StatusBadge";
import { useStore } from "../lib/store";
import type { AvailableAction } from "../lib/types";

/** 患者端：无事件 → 巨大 SOS；已触发 → 救援进度 + 黄金时间倒计时。 */
export default function PatientPage() {
  const event = useStore((s) => s.event);
  const currentEventId = useStore((s) => s.currentEventId);
  const triggerSOS = useStore((s) => s.triggerSOS);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [busy, setBusy] = useState(false);

  const doSOS = async () => {
    setConfirmOpen(false);
    setBusy(true);
    await triggerSOS();
    setBusy(false);
  };

  const hasActiveEvent =
    event !== null && event.status !== "ARCHIVED" && event.status !== "CREATED";

  const secondary: AvailableAction[] = [];

  return (
    <>
      {!hasActiveEvent ? (
        // ---- 无进行中事件：巨大 SOS 按钮（二次确认）----
        <div className="sos-wrap">
          <button className="sos-btn" onClick={() => setConfirmOpen(true)}>
            SOS
          </button>
          <div className="sos-hint">紧急情况 · 立即求助</div>
          {event?.status === "ARCHIVED" && (
            <div className="text-faint" style={{ fontSize: 12 }}>
              上次救援（#{event.id}）已完成，可发起新求助
            </div>
          )}
        </div>
      ) : (
        // ---- 救援进行中：进度 + 黄金时间 ----
        <>
          <div className="row">
            <StatusBadge status={event!.status} />
            <span className="text-faint" style={{ fontSize: 12 }}>
              事件 #{currentEventId}
            </span>
          </div>
          <Countdown startedAt={event!.started_at} />
          <ProgressCard event={event!} />
          <button className="drawer-tab" onClick={() => setDrawerOpen(true)}>
            {"健康数据与时间线"}
          </button>
        </>
      )}

      <ConfirmModal
        open={confirmOpen}
        title="确认发起 SOS？"
        text="您已确认此交互方式：点击后将立即向最近的救援单元发出求救信号。请确认您处于紧急情况。"
        confirmLabel="确认求助"
        onConfirm={() => void doSOS()}
        onCancel={() => setConfirmOpen(false)}
      />

      <InfoDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        secondary={secondary}
      >
        {hasActiveEvent && (
          <div className="drawer-section">
            <h5 className="card-title">事件信息</h5>
            <div className="kv">
              <span className="k">事发地点</span>
              <span className="v">{event!.location || "—"}</span>
            </div>
          </div>
        )}
      </InfoDrawer>

      {busy && <div className="toast">正在发起 SOS…</div>}
    </>
  );
}
