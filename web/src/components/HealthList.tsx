import type { HealthReading } from "../lib/types";

const TYPE_LABELS: Record<string, string> = {
  heart_rate: "心率",
  spo2: "血氧",
  cpr_cycles: "CPR 循环",
  note: "备注",
};

/** 健康读数列表（折叠抽屉内容）。 */
export default function HealthList({ health }: { health: HealthReading[] }) {
  if (health.length === 0) {
    return <div className="text-faint" style={{ fontSize: 12 }}>暂无健康读数</div>;
  }
  return (
    <div>
      {health.map((h) => (
        <div className="kv" key={h.id}>
          <span className="k">{TYPE_LABELS[h.reading_type] ?? h.reading_type}</span>
          <span className="v">
            {h.value}
            {h.unit && <span style={{ marginLeft: 2, color: "var(--text-dim)" }}>{h.unit}</span>}
          </span>
        </div>
      ))}
    </div>
  );
}
