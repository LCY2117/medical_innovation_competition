/** AedPanel：AED 点位实时状态。 */
import { useStore } from "../../lib/store";
import type { AedDevice } from "../../lib/types";

interface Props {
  aeds: AedDevice[];
}

export default function AedPanel({ aeds }: Props) {
  const event = useStore((s) => s.event);
  // AED 相关阶段高亮
  const aedActive = event
    ? ["AED_PICKED", "AED_DELIVERED", "AED_ANALYZING", "SHOCK_DELIVERED"].includes(event.status)
    : false;
  const delivered = event ? event.status === "AED_DELIVERED" : false;

  return (
    <section className="panel aed-panel">
      <div className="panel-title">
        <span className="t">AED 点位 ASSET</span>
        <span className="tag">{aeds.length} 台{delivered ? " · 已送达" : aedActive ? " · 转运中" : ""}</span>
      </div>
      <div className="aed-scroll">
        {aeds.length === 0 ? (
          <div className="tl-empty">暂无 AED 数据</div>
        ) : (
          aeds.map((a) => (
            <div key={a.id} className="aed-row">
              <span className={`ic ${a.available ? "on" : "off"}`} />
              <span className="nm">{a.name}</span>
              <span className="loc">{a.location}</span>
              <span className="st">{a.available ? "可用" : "占用"}</span>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
