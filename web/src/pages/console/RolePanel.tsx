/** RolePanel：PRIME / RUNNER / GUIDE 三角色实时状态卡。 */
import { useStore } from "../../lib/store";
import type { Assignment } from "../../lib/types";

interface RoleCfg {
  key: "PRIME" | "RUNNER" | "GUIDE";
  label: string;
  mark: string;
  cls: string;
}

const ROLES: RoleCfg[] = [
  { key: "PRIME", label: "核心施救", mark: "CPR", cls: "prime" },
  { key: "RUNNER", label: "AED 保障", mark: "AED", cls: "runner" },
  { key: "GUIDE", label: "环境清障", mark: "引", cls: "guide" },
];

function mainAssignment(assignments: Assignment[] | undefined, role: string): Assignment | null {
  if (!assignments || assignments.length === 0) return null;
  const list = assignments
    .filter((a) => a.role === role)
    .sort((a, b) => a.priority - b.priority);
  return list[0] ?? null;
}

function chipOf(confirmed: boolean, assignment: Assignment | null) {
  if (confirmed) return { text: "已确认响应", cls: "ok" };
  if (!assignment) return { text: "未分派", cls: "off" };
  switch (assignment.status) {
    case "CONFIRMED":
      return { text: "已确认", cls: "ok" };
    case "DECLINED":
      return { text: "已婉拒", cls: "off" };
    case "BACKUP":
      return { text: "递补中", cls: "busy" };
    default:
      return { text: "待确认", cls: "wait" };
  }
}

export default function RolePanel() {
  const event = useStore((s) => s.event);

  return (
    <section className="panel role-panel">
      <div className="panel-title">
        <span className="t">角色部署 ROLE DEPLOY</span>
        <span className="tag">3 UNITS</span>
      </div>
      <div className="role-stack">
        {ROLES.map((role) => {
          const confirmed = event
            ? Boolean(event[`${role.key.toLowerCase()}_confirmed` as "prime_confirmed"])
            : false;
          const assignment = mainAssignment(event?.assignments, role.key);
          const chip = chipOf(confirmed, assignment);
          const progress = confirmed ? 100 : assignment ? 55 : 18;
          const name = assignment?.responder_name || "尚未指派";
          const sub = assignment
            ? `评分 ${(assignment.score * 100).toFixed(1)} · 优先级 ${assignment.priority}`
            : "等待分派引擎匹配";
          return (
            <div key={role.key} className={`role-card-mini ${confirmed ? "active" : ""}`}>
              <div className="role-card-head">
                <span className={`role-ic ${role.cls}`}>{role.mark}</span>
                <div className="role-meta-mini">
                  <div className="role-name-mini">{role.label}</div>
                  <div className="role-sub-mini">{name} · {sub}</div>
                </div>
                <span className={`role-chip ${chip.cls}`}>{chip.text}</span>
              </div>
              <div className="role-bar">
                <i style={{ width: `${progress}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
