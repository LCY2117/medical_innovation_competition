/** TimelinePanel：状态机时间线（滚动转场 + 关键高亮 2s + 气泡弹入）。 */
import { useEffect, useRef, useState } from "react";
import { useStore } from "../../lib/store";
import type { Transition } from "../../lib/types";
import { ACTION_LABELS, fmtClock } from "./meta";

function dotClass(action: string): string {
  if (action === "AED_SHOCK_DELIVERED" || action === "SOS_TRIGGERED") return "shock";
  if (action === "DISPATCH") return "dispatch";
  return "";
}

function actionText(t: Transition): string {
  const label = ACTION_LABELS[t.action] ?? t.action;
  if (t.from_status === t.to_status || !t.to_status) return label;
  return `${label}  ${t.from_status} → ${t.to_status}`;
}

export default function TimelinePanel() {
  const timeline = useStore((s) => s.timeline);
  const eventSeq = useStore((s) => s.event?.seq);
  const scrollRef = useRef<HTMLDivElement>(null);
  const prevLen = useRef(0);
  const [hot, setHot] = useState<Set<number>>(new Set());

  // 新条目 → 弹入 + 高亮 2s
  useEffect(() => {
    if (timeline.length > prevLen.current) {
      const fresh = timeline.slice(prevLen.current).map((t) => t.id);
      setHot((prev) => new Set([...prev, ...fresh]));
      const timer = setTimeout(() => {
        setHot((prev) => {
          const next = new Set(prev);
          fresh.forEach((id) => next.delete(id));
          return next;
        });
      }, 2000);
      prevLen.current = timeline.length;
      return () => clearTimeout(timer);
    }
    if (timeline.length === 0) prevLen.current = 0;
  }, [timeline]);

  // 自动滚动到底部
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [timeline.length]);

  return (
    <section className="panel timeline-panel">
      <div className="panel-title">
        <span className="t">事件时间线 TIMELINE</span>
        <span className="tag">seq {eventSeq ?? 0} · {timeline.length} 条</span>
      </div>
      <div className="timeline-scroll" ref={scrollRef}>
        {timeline.length === 0 ? (
          <div className="tl-empty">暂无时间线记录 · 等待第一个动作</div>
        ) : (
          timeline.map((t) => (
            <div key={t.id} className={`tl-item ${hot.has(t.id) ? "hot" : ""}`}>
              <span className="tl-seq">#{t.seq}</span>
              <span className={`tl-dot ${dotClass(t.action)}`} />
              <div className="tl-body">
                <div className="tl-action">{actionText(t)}</div>
                <div className="tl-meta">
                  {fmtClock(t.created_at)} · {t.actor_role || "SYSTEM"}
                  {t.duplicate ? " · 幂等跳过" : ""}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
