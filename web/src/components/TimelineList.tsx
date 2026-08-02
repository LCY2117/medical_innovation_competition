import type { Transition } from "../lib/types";

/** 时间线列表（折叠抽屉内容）。 */
export default function TimelineList({ timeline }: { timeline: Transition[] }) {
  if (timeline.length === 0) {
    return <div className="text-faint" style={{ fontSize: 12 }}>暂无时间线记录</div>;
  }
  return (
    <div>
      {timeline.map((t) => (
        <div className="timeline-item" key={t.id}>
          <span className={`timeline-dot ${t.duplicate ? "repeat" : ""}`} />
          <div className="timeline-body">
            <div className="timeline-action">{t.action}</div>
            <div className="timeline-meta">
              {t.from_status} → {t.to_status} · {t.actor_role}
              {t.duplicate ? " · 重复提交" : ""}
            </div>
          </div>
          <div className="timeline-meta" style={{ alignSelf: "center" }}>
            #{t.seq}
          </div>
        </div>
      ))}
    </div>
  );
}
