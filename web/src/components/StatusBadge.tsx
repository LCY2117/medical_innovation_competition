import { STATUS_LABELS } from "../lib/types";

/** 事件状态徽章。 */
export default function StatusBadge({ status }: { status: string }) {
  const tone =
    status === "ARCHIVED" || status === "CREATED"
      ? "gray"
      : status === "SOS" || status === "CPR" || status === "SHOCK_DELIVERED"
        ? "red"
        : status === "AED_ANALYZING" || status === "HANDOVER"
          ? "amber"
          : "cyan";
  return (
    <span className={`badge ${tone}`}>
      <span className="dot" />
      {STATUS_LABELS[status] ?? status}
    </span>
  );
}
