import { ACTION_HINTS } from "../lib/meta";

type Variant = "primary" | "danger" | "amber" | "neutral";

interface Props {
  label: string;
  action: string;
  variant?: Variant;
  disabled?: boolean;
  submitting?: boolean;
  onClick: () => void;
  small?: boolean;
}

/** 一屏一动作的主按钮：根据后端下发的动作渲染。 */
export default function ActionButton({
  label,
  action,
  variant = "primary",
  disabled,
  submitting,
  onClick,
  small,
}: Props) {
  return (
    <button
      className={`action-btn ${variant} ${small ? "small" : ""}`}
      disabled={disabled || submitting}
      onClick={onClick}
    >
      {submitting ? <span className="spin" /> : label}
      <span className="sub">{ACTION_HINTS[action] ?? ""}</span>
    </button>
  );
}
