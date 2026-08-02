/** VitalsPanel：心率 / 血氧 / 压力 实时曲线（发光数字 + SVG sparkline）。 */
import { useMemo } from "react";
import { useStore } from "../../lib/store";
import type { HealthReading } from "../../lib/types";

interface MetricMeta {
  label: string;
  unit: string;
  cls: string;
  /** 危急阈值（超过变红）。 */
  warn: (v: number) => boolean;
}

const METRICS: Record<string, MetricMeta> = {
  heart_rate: {
    label: "心率",
    unit: "bpm",
    cls: "cyan",
    warn: (v) => v < 40 || v > 140,
  },
  spo2: {
    label: "血氧",
    unit: "%",
    cls: "green",
    warn: (v) => v < 90,
  },
  stress: {
    label: "压力",
    unit: "",
    cls: "amber",
    warn: () => false,
  },
};

const DEFAULT_META: MetricMeta = {
  label: "体征",
  unit: "",
  cls: "amber",
  warn: () => false,
};

function Sparkline({ values, cls }: { values: number[]; cls: string }) {
  const points = useMemo(() => {
    const W = 280;
    const H = 42;
    if (values.length === 0) return "";
    const min = Math.min(...values);
    const max = Math.max(...values);
    const span = max - min || 1;
    return values
      .map((v, i) => {
        const x = (i / Math.max(1, values.length - 1)) * (W - 8) + 4;
        const y = H - 4 - ((v - min) / span) * (H - 8);
        return `${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(" ");
  }, [values]);

  const color =
    cls === "cyan" ? "#00e5ff" : cls === "green" ? "#34d399" : cls === "red" ? "#ff3b5c" : "#ffc107";

  if (values.length === 0) {
    return (
      <svg className="metric-spark" viewBox="0 0 280 42" preserveAspectRatio="none">
        <line x1="4" y1="21" x2="276" y2="21" stroke="rgba(148,190,255,0.12)" strokeWidth="1" strokeDasharray="3 3" />
      </svg>
    );
  }
  return (
    <svg className="metric-spark" viewBox="0 0 280 42" preserveAspectRatio="none">
      <defs>
        <linearGradient id={`glow-${cls}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.35" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={`4,42 ${points} 276,42`} fill={`url(#glow-${cls})`} />
      <polyline
        points={points}
        fill="none"
        stroke={color}
        strokeWidth="1.6"
        style={{ filter: `drop-shadow(0 0 4px ${color})` }}
      />
    </svg>
  );
}

export default function VitalsPanel() {
  const health = useStore((s) => s.health);

  // 按 reading_type 聚合
  const groups = useMemo(() => {
    const map = new Map<string, HealthReading[]>();
    for (const r of health) {
      if (!map.has(r.reading_type)) map.set(r.reading_type, []);
      map.get(r.reading_type)!.push(r);
    }
    const out: { key: string; meta: MetricMeta; latest: number; values: number[] }[] = [];
    for (const [key, list] of map) {
      const sorted = [...list].sort(
        (a, b) => Date.parse(a.recorded_at || "") - Date.parse(b.recorded_at || ""),
      );
      const meta = METRICS[key] ?? DEFAULT_META;
      out.push({
        key,
        meta,
        latest: sorted[sorted.length - 1]?.value ?? 0,
        values: sorted.slice(-24).map((r) => r.value),
      });
    }
    // 预置空指标展示（无数据时也有占位）
    if (out.length === 0) {
      return [
        { key: "heart_rate", meta: METRICS.heart_rate, latest: 0, values: [] },
        { key: "spo2", meta: METRICS.spo2, latest: 0, values: [] },
        { key: "stress", meta: METRICS.stress, latest: 0, values: [] },
      ];
    }
    return out;
  }, [health]);

  return (
    <section className="panel vitals-panel">
      <div className="panel-title">
        <span className="t">生命体征 VITALS</span>
        <span className="tag">LIVE</span>
      </div>
      <div className="vitals-scroll">
        {groups.map((g) => {
          const cls = g.meta.warn(g.latest) ? "red" : g.meta.cls;
          return (
            <div className="metric-row" key={g.key}>
              <div className="metric-head">
                <span className="metric-name">
                  {g.meta.label} · {g.key}
                </span>
                <span className={`metric-val ${cls}`}>
                  {g.latest}
                  {g.meta.unit && <small style={{ fontSize: 12, marginLeft: 3 }}>{g.meta.unit}</small>}
                </span>
              </div>
              <Sparkline values={g.values} cls={cls} />
            </div>
          );
        })}
      </div>
    </section>
  );
}
