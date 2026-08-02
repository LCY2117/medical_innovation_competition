import { useState } from "react";
import { ROLE_META } from "../lib/meta";
import { useStore } from "../lib/store";
import type { Role } from "../lib/types";

const DEMO_ROLES: Role[] = ["PATIENT", "PRIME", "RUNNER", "GUIDE"];

/** 登录页：4 个演示角色一键登录 + 账号密码表单。 */
export default function LoginPage() {
  const loginDemo = useStore((s) => s.loginDemo);
  const loginForm = useStore((s) => s.loginForm);
  const error = useStore((s) => s.error);
  const [busy, setBusy] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const doDemo = async (role: Role) => {
    setBusy(true);
    try {
      await loginDemo(role);
    } catch {
      /* 错误已写入 store */
    } finally {
      setBusy(false);
    }
  };

  const doLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    try {
      await loginForm(username.trim(), password);
    } catch {
      /* 错误已写入 store */
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="login-wrap">
      <div className="login-hero">
        <svg viewBox="0 0 64 64" width="56" height="56" style={{ filter: "drop-shadow(0 0 14px rgba(34,211,238,0.5))" }}>
          <path
            d="M8 34 L22 34 L28 22 L36 46 L42 32 L56 32"
            fill="none"
            stroke="#22d3ee"
            strokeWidth="4.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <circle cx="56" cy="32" r="4" fill="#ff2d55" />
        </svg>
        <h1>生命反射弧</h1>
        <p>应急协同系统 · MOBILE</p>
      </div>

      <div className="role-grid">
        {DEMO_ROLES.map((role) => {
          const m = ROLE_META[role];
          return (
            <button
              key={role}
              className="role-card"
              onClick={() => void doDemo(role)}
              disabled={busy}
            >
              <span className="ic" style={{ color: "var(--cyan)", fontFamily: "var(--font-num)", fontWeight: 800 }}>
                {m.mark}
              </span>
              <span className="name">{m.label}</span>
              <span className="desc">{m.desc}</span>
            </button>
          );
        })}
      </div>

      <div className="login-divider">账号登录（管理 / 调度）</div>

      <form className="card login-form-card" onSubmit={doLogin}>
        <div className="field">
          <label>用户名</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        </div>
        <div className="field">
          <label>密码</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </div>
        <ActionSubmit disabled={busy} />
      </form>

      {error && <div className="toast">{error}</div>}
    </div>
  );
}

function ActionSubmit({ disabled }: { disabled: boolean }) {
  return (
    <button type="submit" className="action-btn primary" disabled={disabled}>
      {disabled ? <span className="spin" /> : "登 录"}
    </button>
  );
}
