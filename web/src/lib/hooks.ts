import { useEffect, useState } from "react";
import { ensureAudio } from "./audio";
import { useStore } from "./store";

/** 每秒触发的 now 时间戳（用于倒计时/计时渲染）。 */
export function useNow(active = true, intervalMs = 1000): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!active) return;
    const id = setInterval(() => setNow(Date.now()), intervalMs);
    return () => clearInterval(id);
  }, [active, intervalMs]);
  return now;
}

/** 提交动作的统一封装：先恢复 AudioContext（浏览器要求用户手势）。 */
export function useAction() {
  const submitting = useStore((s) => s.submitting);
  const submitAction = useStore((s) => s.submitAction);
  return {
    submitting,
    run: (action: string, metadata?: Record<string, unknown>) => {
      ensureAudio();
      void submitAction(action, metadata);
    },
  };
}

/**
 * 响应端自动发现活跃事件：登录后立即查询 /events/active，
 * 有活跃事件则自动订阅；暂无则每 pollMs 轮询直到发现（演示中患者端
 * 触发 SOS 后，本端无需手输编号即可自动接入）。
 */
export function useAutoDiscover(pollMs = 4000): void {
  useEffect(() => {
    let disposed = false;
    const tryDiscover = () => {
      const s = useStore.getState();
      if (disposed) return;
      if (s.currentEventId !== null) return; // 已订阅
      void s.autoDiscoverEvent();
    };
    tryDiscover();
    const id = setInterval(() => {
      const s = useStore.getState();
      if (s.currentEventId !== null || s.discovery === "found") return;
      tryDiscover();
    }, pollMs);
    return () => {
      disposed = true;
      clearInterval(id);
    };
  }, [pollMs]);
}
