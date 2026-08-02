import type { ReactNode } from "react";

interface Props {
  open: boolean;
  title: string;
  text: string;
  confirmLabel: string;
  cancelLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  children?: ReactNode;
}

/** 二次确认弹窗（SOS 等高风险操作前必须确认）。 */
export default function ConfirmModal({
  open,
  title,
  text,
  confirmLabel,
  cancelLabel = "取消",
  danger = true,
  onConfirm,
  onCancel,
  children,
}: Props) {
  if (!open) return null;
  return (
    <div className="modal" onClick={onCancel}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-title">{title}</div>
        <div className="modal-text">{text}</div>
        {children}
        <div className="modal-actions">
          <button className="btn-ghost" style={{ flex: 1 }} onClick={onCancel}>
            {cancelLabel}
          </button>
          <button
            className={`action-btn ${danger ? "danger" : "primary"} small`}
            style={{ flex: 1.4 }}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
