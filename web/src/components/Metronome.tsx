import { useEffect, useRef, useState } from "react";
import { playBeat } from "../lib/audio";
import { useNow } from "../lib/hooks";

/** CPR 节拍器参数：110 BPM 按压 + 30:2 循环。 */
const BPM = 110;
const BEAT_MS = 60000 / BPM; // ≈545ms
const COMPRESSIONS = 30;
/** 吹气阶段时长（秒），保证 2 次吹气有足够时间。 */
const BREATH_PHASE_SEC = 6;

interface Props {
  /** 是否运行（false 时静止显示当前计数）。 */
  running?: boolean;
  /** 除颤次数（展示额外信息用）。 */
  shockCount?: number;
  cycleLimit?: number;
}

interface MetronomeState {
  phase: "press" | "breath";
  count: number; // 按压计数 1..30 或吹气计数 1..2
  cycle: number; // 30:2 循环次数
}

/** 心肺复苏节拍器：视觉脉冲 + Web Audio 滴答 + 30:2 循环。 */
export default function Metronome({ running = true, shockCount = 0 }: Props) {
  const [state, setState] = useState<MetronomeState>({
    phase: "press",
    count: 1,
    cycle: 1,
  });
  const [beating, setBeating] = useState(false);
  const stateRef = useRef(state);
  stateRef.current = state;

  const now = useNow(running, 200);

  useEffect(() => {
    if (!running) return;
    // 0 表示 phase 起点，1 表示 phase 中段（用于吹气阶段视觉区分）
    let phaseStart = performance.now();
    let beatCount = 0;

    const interval = setInterval(() => {
      const elapsed = performance.now() - phaseStart;
      const s = stateRef.current;

      if (s.phase === "press") {
        // 按压 30 次后切换吹气
        if (beatCount >= COMPRESSIONS) {
          setState((p) => ({ phase: "breath", count: 1, cycle: p.cycle }));
          phaseStart = performance.now();
          beatCount = 0;
          playBeat("breath");
          return;
        }
        // 一次按压脉冲
        setBeating(true);
        playBeat("press");
        setState((p) =>
          p.phase === "press"
            ? { ...p, count: Math.min(p.count + 1, COMPRESSIONS) }
            : p,
        );
        beatCount += 1;
        setTimeout(() => setBeating(false), 90);
      } else {
        // 吹气阶段：BREATH_PHASE_SEC 秒后回到按压
        if (elapsed >= BREATH_PHASE_SEC * 1000) {
          setState((p) => ({ phase: "press", count: 1, cycle: p.cycle + 1 }));
          phaseStart = performance.now();
          beatCount = 0;
          return;
        }
        // 2 次吹气提示音（前半段与后半段各一次）
        const half = (BREATH_PHASE_SEC * 1000) / 2;
        if (beatCount === 0 && elapsed >= 400) {
          playBeat("breath");
          beatCount = 1;
        } else if (beatCount === 1 && elapsed >= half + 400) {
          playBeat("breath");
          beatCount = 2;
        }
      }
    }, BEAT_MS);

    return () => clearInterval(interval);
  }, [running]);

  // 让每帧重渲染按拍点缩放（简化：直接复用 interval 已足够，此处仅供 breathing 视觉）
  void now;

  const isBreath = state.phase === "breath";
  const displayNum = isBreath
    ? "2次"
    : String(state.count);

  return (
    <div className="metronome">
      <div className="bpm-bar">
        <span className="val">110</span>
        <span className="unit">BPM</span>
      </div>

      <div className={`pulse-ring ${isBreath ? "breath" : beating ? "beat" : ""}`}>
        <div className={`pulse-num ${isBreath ? "amber" : ""}`}>{displayNum}</div>
        <div className="pulse-label">{isBreath ? "人工呼吸" : "胸外按压"}</div>
      </div>

      <div className="cycle-box">
        <span className={`cycle-chip ${!isBreath ? "active" : ""}`}>
          按压 {state.phase === "press" ? state.count : COMPRESSIONS}/{COMPRESSIONS}
        </span>
        <span className={`cycle-chip ${isBreath ? "active" : ""}`}>吹气 2 次</span>
        <span className="cycle-chip">循环 {state.cycle}</span>
        {shockCount > 0 && <span className="cycle-chip">除颤 {shockCount}/3</span>}
      </div>
    </div>
  );
}
