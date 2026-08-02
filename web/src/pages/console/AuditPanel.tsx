/** AuditPanel：底部审计流（追加式日志，按严重度着色，自动滚动）。 */
import { useEffect, useMemo, useRef, useState } from "react";
import { useStore } from "../../lib/store";
import type { Transition } from "../../lib/types";
import { ACTION_LABELS, fmtClock } from "./meta";

interface Line {
  ts: string;
  sev: 0 | 1 | 2;
  msg: string;
}

function severity(action: string): 0 | 1 | 2 {
  if (action === "SOS_TRIGGERED" || action === "AED_SHOCK_DELIVERED") return 2;
  if (action === "DISPATCH" || action === "HANDOVER_COMPLETED" || action === "ARCHIVE") return 1;
  return 0;
}

function toLine(t: Transition): Line {
  const label = ACTION_LABELS[t.action] ?? t.action;
  const who = t.actor_role || "SYSTEM";
  return {
    ts: fmtClock(t.created_at),
    sev: severity(t.action),
    msg: `[${who}] ${label}${t.duplicate ? "（幂等跳过）" : ""} · ${t.from_status} → ${t.to_status}`,
  };
}

export default function AuditPanel() {
  const timeline = useStore((s) => s.timeline);
  const event = useStore((s) => s.event);
  const wsStatus = useStore((s) => s.wsStatus);
  const scrollRef = useRef<HTMLDivElement>(null);

  const [lines, setLines] = useState<Line[]>([]);
  const lastCount = useRef(0);
  const lastAssignSig = useRef("");

  // 追加新时间线条目
  useEffect(() => {
    if (timeline.length === 0) {
      lastCount.current = 0;
      return;
    }
    if (timeline.length > lastCount.current) {
      const fresh = timeline.slice(lastCount.current);
      lastCount.current = timeline.length;
      setLines((prev) => [...prev, ...fresh.map(toLine)].slice(-80));
    }
  }, [timeline]);

  // 分派/状态变化 → 审计一行
  const assignSig = useMemo(
    () =>
      event
        ? event.assignments
            ?.map((a) => `${a.role}:${a.status}:${a.responder_name}`)
            .join("|") ?? ""
        : "",
    [event],
  );
  useEffect(() => {
    if (!event) return;
    if (assignSig && assignSig !== lastAssignSig.current) {
      lastAssignSig.current = assignSig;
      setLines((prev) =>
        [
          ...prev,
          {
            ts: fmtClock(event.updated_at),
            sev: 1 as const,
            msg: `分派审计 · ${event.assignments?.length ?? 0} 条分派记录（seq=${event.seq}）`,
          },
        ].slice(-80),
      );
    }
  }, [assignSig, event]);

  // 自动滚动
  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [lines.length]);

  return (
    <section className="panel audit-panel">
      <div className="panel-title">
        <span className="t">审计流 AUDIT</span>
        <span className="tag">
          {wsStatus === "connected" ? "WS·LIVE" : wsStatus.toUpperCase()}
        </span>
      </div>
      <div className="audit-scroll" ref={scrollRef}>
        {lines.length === 0 ? (
          <div className="tl-empty">审计流待命 · 等待系统动作</div>
        ) : (
          lines.map((l, i) => (
            <div key={i} className={`audit-line sev${l.sev}`}>
              <span className="ts">[{l.ts}]</span>
              <span className="msg">{l.msg}</span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
