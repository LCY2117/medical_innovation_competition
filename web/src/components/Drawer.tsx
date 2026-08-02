import type { ReactNode } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
}

/** 底部折叠抽屉：一屏一动作下，其余信息/操作都收进这里。 */
export default function Drawer({ open, onClose, title, children }: Props) {
  if (!open) return null;
  return (
    <>
      <div className="drawer-overlay" onClick={onClose} />
      <div className="drawer" role="dialog" aria-label={title ?? "更多信息"}>
        <div className="drawer-handle" />
        {title && (
          <h4 className="card-title" style={{ marginTop: 0 }}>
            {title}
          </h4>
        )}
        {children}
      </div>
    </>
  );
}
