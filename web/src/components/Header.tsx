import { ROLE_META } from "../lib/meta";
import { useStore } from "../lib/store";
import type { Role } from "../lib/types";

const STATUS_DOT: Record<string, string> = {
  connected: "connected",
  connecting: "connecting",
  reconnecting: "reconnecting",
  closed: "closed",
};

export default function Header() {
  const role = useStore((s) => s.role);
  const username = useStore((s) => s.username);
  const wsStatus = useStore((s) => s.wsStatus);
  const logout = useStore((s) => s.logout);

  const meta = (role ? ROLE_META[role as Role] : null) ?? null;

  return (
    <header className="header">
      <div className="header-logo">
        <svg viewBox="0 0 64 64" width="26" height="26" aria-hidden>
          <path
            d="M8 34 L22 34 L28 22 L36 46 L42 32 L56 32"
            fill="none"
            stroke="#22d3ee"
            strokeWidth="6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="56" cy="32" r="4" fill="#ff2d55" />
        </svg>
      </div>
      <div className="header-title">
        生命反射弧
        <div className="header-sub">{meta ? meta.label : "应急协同系统"}</div>
      </div>
      <div className="header-right">
        <span className="text-faint" style={{ fontSize: 12 }}>
          {username ?? ""}
        </span>
        <span className={`ws-dot ${STATUS_DOT[wsStatus] ?? "closed"}`} title={`连接状态：${wsStatus}`} />
        <button className="btn-ghost" onClick={logout} style={{ padding: "8px 12px" }}>
          退出
        </button>
      </div>
    </header>
  );
}
