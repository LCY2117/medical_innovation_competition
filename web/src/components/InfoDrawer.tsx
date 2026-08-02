import type { ReactNode } from "react";
import { useAction } from "../lib/hooks";
import { useStore } from "../lib/store";
import type { AvailableAction } from "../lib/types";
import ActionButton from "./ActionButton";
import Drawer from "./Drawer";
import HealthList from "./HealthList";
import TimelineList from "./TimelineList";

interface Props {
  open: boolean;
  onClose: () => void;
  /** 除主行动外，后端允许的其他操作（收进抽屉）。 */
  secondary: AvailableAction[];
  children?: ReactNode;
}

/** 折叠抽屉：次级动作 + 健康数据 + 时间线。 */
export default function InfoDrawer({ open, onClose, secondary, children }: Props) {
  const timeline = useStore((s) => s.timeline);
  const health = useStore((s) => s.health);
  const { submitting, run } = useAction();

  return (
    <Drawer open={open} onClose={onClose} title="更多信息">
      {secondary.length > 0 && (
        <div className="drawer-section">
          <h5 className="card-title">其他可用操作</h5>
          <div className="flex-col">
            {secondary.map((a) => (
              <ActionButton
                key={a.action}
                label={a.label}
                action={a.action}
                variant="neutral"
                small
                disabled={submitting}
                onClick={() => run(a.action)}
              />
            ))}
          </div>
        </div>
      )}
      {children}
      <div className="drawer-section">
        <h5 className="card-title">健康数据</h5>
        <HealthList health={health} />
      </div>
      <div className="drawer-section">
        <h5 className="card-title">时间线</h5>
        <TimelineList timeline={timeline} />
      </div>
    </Drawer>
  );
}
