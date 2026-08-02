import { useState } from "react";
import { demoTrigger } from "../lib/api";
import { useStore } from "../lib/store";
import { STATUS_LABELS } from "../lib/types";

/** 调度控制台（SYSTEM/ADMIN）：M3 大屏前的最小占位 + 演示触发。 */
export default function AdminPage() {
  const role = useStore((s) => s.role);
  const event = useStore((s) => s.event);
  const attachEvent = useStore((s) => s.attachEvent);
  const [result, setResult] = useState<string>("");
  const [busy, setBusy] = useState(false);

  const trigger = async () => {
    setBusy(true);
    try {
      const ev = await demoTrigger();
      setResult(`事件 #${ev.id} 已创建 · 状态：${STATUS_LABELS[ev.status] ?? ev.status}`);
      try {
        localStorage.setItem("lifereflex.lastEventId", String(ev.id));
      } catch {
        /* ignore */
      }
      await attachEvent(ev.id);
    } catch (e) {
      setResult(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <div className="row">
        <StatusBadgeMini status={event?.status} />
        <span className="text-faint" style={{ fontSize: 12 }}>
          {role === "SYSTEM" ? "自动调度系统" : "管理员"}已登录
        </span>
      </div>

      <div className="standby">
        <div className="standby-title">调度控制台</div>
        <div className="standby-sub">M3 阶段将交付多端调度大屏，当前为最小控制入口</div>
        <button className="action-btn primary" onClick={() => void trigger()} disabled={busy}>
          {busy ? <span className="spin" /> : "一键触发演示事件"}
        </button>
        {result && <div className="text-dim" style={{ fontSize: 13 }}>{result}</div>}
        {event && (
          <div className="card" style={{ width: "100%" }}>
            <h4 className="card-title">当前事件</h4>
            <div className="kv"><span className="k">事件编号</span><span className="v">#{event.id}</span></div>
            <div className="kv"><span className="k">状态</span><span className="v">{STATUS_LABELS[event.status] ?? event.status}</span></div>
            <div className="kv"><span className="k">序列版本</span><span className="v">seq {event.seq}</span></div>
            <div className="kv"><span className="k">已确认</span><span className="v">P {event.prime_confirmed ? "✓" : "—"} R {event.runner_confirmed ? "✓" : "—"} G {event.guide_confirmed ? "✓" : "—"}</span></div>
          </div>
        )}
      </div>
    </>
  );
}

function StatusBadgeMini({ status }: { status?: string }) {
  if (!status) return <span className="badge gray">未连接事件</span>;
  return (
    <span className={`badge ${status === "ARCHIVED" ? "gray" : "cyan"}`}>
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
