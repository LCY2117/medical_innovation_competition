import type { EventData } from "../lib/types";

interface RoleInfo {
  key: "PRIME" | "RUNNER" | "GUIDE";
  mark: string;
  name: string;
  css: string;
}

const ROLES: RoleInfo[] = [
  { key: "PRIME", mark: "CPR", name: "核心施救", css: "prime" },
  { key: "RUNNER", mark: "AED", name: "AED 保障", css: "runner" },
  { key: "GUIDE", mark: "引", name: "环境清障", css: "guide" },
];

function stateOf(event: EventData, role: RoleInfo["key"]): { text: string; cls: string } {
  const confirmed =
    role === "PRIME"
      ? event.prime_confirmed
      : role === "RUNNER"
        ? event.runner_confirmed
        : event.guide_confirmed;
  if (confirmed) return { text: "已响应 · 赶赴中", cls: "ok" };

  const assignments = event.assignments ?? [];
  const mine = assignments
    .filter((a) => a.role === role && a.status !== "DECLINED")
    .sort((a, b) => a.priority - b.priority)[0];
  if (mine) {
    if (mine.status === "PENDING") return { text: `已分派 · ${mine.responder_name || "待命"}`, cls: "busy" };
    return { text: "已分派", cls: "busy" };
  }
  return { text: "等待分派中", cls: "wait" };
}

/** 救援进度卡：PRIME / RUNNER / GUIDE 谁来救、到哪了（从 assignments 推导）。 */
export default function ProgressCard({ event }: { event: EventData }) {
  const assignments = event.assignments ?? [];

  return (
    <div className="card">
      <h4 className="card-title">救援力量</h4>
      <div className="role-progress">
        {ROLES.map((r) => {
          const st = stateOf(event, r.key);
          return (
            <div className="role-row" key={r.key}>
              <div className={`role-icon ${r.css}`}>{r.mark}</div>
              <div className="role-meta">
                <div className="role-name">{r.name}</div>
                <div className={`role-state ${st.cls}`}>{st.text}</div>
              </div>
            </div>
          );
        })}
        {assignments.length === 0 && (
          <div className="text-faint" style={{ fontSize: 12, textAlign: "center", padding: 8 }}>
            分派引擎即将为事件匹配最近响应单元…
          </div>
        )}
      </div>
    </div>
  );
}
