/** StageBanner：事件阶段 + 大字倒计时（发光+每秒翻转）+ 事件ID/地点。 */
import { useNow } from "../../lib/hooks";
import type { EventData } from "../../lib/types";
import { fmtClock, pad, stageSeverity, STATUS_LABELS } from "./meta";

interface Props {
  event: EventData | null;
  currentEventId: number | null;
}

function parseBase(startedAt: string | null): number {
  if (!startedAt) return 0;
  const iso = /Z|[+-]\d{2}:?\d{2}$/i.test(startedAt) ? startedAt : `${startedAt}Z`;
  const t = Date.parse(iso);
  return Number.isNaN(t) ? 0 : t;
}

/** 已耗时（HH:MM:SS），每秒重渲染触发翻转动画。 */
function ElapsedCount({ startedAt }: { startedAt: string | null }) {
  const now = useNow(Boolean(startedAt));
  const base = parseBase(startedAt);
  const elapsed = base > 0 ? Math.max(0, Math.floor((now - base) / 1000)) : 0;
  const hh = pad(Math.floor(elapsed / 3600));
  const mm = pad(Math.floor((elapsed % 3600) / 60));
  const ss = pad(elapsed % 60);
  const fmt = `${hh}:${mm}:${ss}`;
  const sev = elapsed < 240 ? "" : "danger";
  return (
    <div className="stage-count-wrap">
      <div>
        <div key={fmt} className={`stage-count ${sev} flip`}>{fmt}</div>
        <div className="stage-count-cap">救援已进行 · 黄金窗口 240s</div>
      </div>
    </div>
  );
}

export default function StageBanner({ event, currentEventId }: Props) {
  if (!event) {
    return (
      <header className="stage-banner">
        <div className="stage-left">
          <div className="stage-label">SYSTEM ONLINE</div>
          <div className="stage-name">待接入</div>
        </div>
        <div className="console-idle-inner" style={{ flex: 1 }}>
          <div className="big">WAITING FOR EVENT</div>
          <div className="sub">调度台已就绪，等待事件接入</div>
        </div>
      </header>
    );
  }

  const sev = stageSeverity(event.status);
  const label = STATUS_LABELS[event.status] ?? event.status;

  return (
    <header className="stage-banner">
      <div className="stage-left">
        <div className="stage-label">
          事件阶段 STAGE · seq {event.seq}
        </div>
        <div className={`stage-name ${sev === "warn" ? "warn" : sev === "amber" ? "done" : ""}`}>
          {label}
        </div>
      </div>

      <ElapsedCount startedAt={event.started_at} />

      <div className="stage-right">
        <div className="stage-meta-k">事件编号 EVENT ID</div>
        <div className="stage-meta-v accent">#{currentEventId ?? event.id}</div>
        <div className="stage-meta-k" style={{ marginTop: 6 }}>事发地点 LOCATION</div>
        <div className="stage-meta-v">{event.location || "—"}</div>
        <div className="stage-meta-k" style={{ marginTop: 6 }}>更新时间</div>
        <div className="stage-meta-v">{fmtClock(event.updated_at)}</div>
      </div>
    </header>
  );
}
