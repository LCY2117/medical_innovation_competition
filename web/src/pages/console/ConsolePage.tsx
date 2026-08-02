/** M3 调度台大屏：独立路由 /console。
 *
 * 职责：
 *   - 仅 SYSTEM/ADMIN 可进入（POST /auth/login），否则显示大屏登录页；
 *   - 登录后自动发现当前活跃事件并订阅 WS（复用 store 的版本合并）；
 *   - 深空背景 + 六大面板 + 演示控制台。
 */
import { useEffect, useState } from "react";
import { getActiveEvent, getAedDevices } from "../../lib/api";
import { useStore } from "../../lib/store";
import type { AedDevice } from "../../lib/types";
import AedPanel from "./AedPanel";
import AuditPanel from "./AuditPanel";
import DemoConsole from "./DemoConsole";
import RolePanel from "./RolePanel";
import SpaceBackground from "./SpaceBackground";
import StageBanner from "./StageBanner";
import TimelinePanel from "./TimelinePanel";
import VitalsPanel from "./VitalsPanel";
import "../../console.css";

/** 大屏登录页（仅 SYSTEM/ADMIN）。 */
function ConsoleLogin() {
  const loginForm = useStore((s) => s.loginForm);
  const error = useStore((s) => s.error);
  const [u, setU] = useState("system");
  const [p, setP] = useState("admin1234");
  const [busy, setBusy] = useState(false);

  const submit = async (ev?: React.FormEvent) => {
    ev?.preventDefault();
    setBusy(true);
    try {
      await loginForm(u.trim(), p);
    } catch {
      /* 错误已写入 store */
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="console-root">
      <SpaceBackground />
      <div className="console-login">
        <div className="console-login-card">
          <div className="console-login-title">生命反射弧 · 调度大屏</div>
          <div className="console-login-sub">M3 DISPATCH CONSOLE</div>
          <form onSubmit={(e) => void submit(e)}>
            <div className="field">
              <label>用户名</label>
              <input
                value={u}
                onChange={(e) => setU(e.target.value)}
                autoComplete="username"
              />
            </div>
            <div className="field">
              <label>密码</label>
              <input
                type="password"
                value={p}
                onChange={(e) => setP(e.target.value)}
                autoComplete="current-password"
              />
            </div>
            <button className="action-btn primary" type="submit" disabled={busy}>
              {busy ? <span className="spin" /> : "进入大屏"}
            </button>
          </form>
          <div className="console-quick">
            <button
              onClick={() => {
                setU("system");
                setP("admin1234");
                void submit();
              }}
            >
              system 一键登录
            </button>
            <button
              onClick={() => {
                setU("admin");
                setP("admin1234");
                void submit();
              }}
            >
              admin 一键登录
            </button>
          </div>
          {error && <div className="toast" style={{ position: "static", marginTop: 14 }}>{error}</div>}
        </div>
      </div>
    </div>
  );
}

export default function ConsolePage() {
  const role = useStore((s) => s.role);
  const token = useStore((s) => s.token);
  const username = useStore((s) => s.username);
  const event = useStore((s) => s.event);
  const currentEventId = useStore((s) => s.currentEventId);
  const wsStatus = useStore((s) => s.wsStatus);
  const logout = useStore((s) => s.logout);

  const [aeds, setAeds] = useState<AedDevice[]>([]);

  const isOperator = token !== null && (role === "SYSTEM" || role === "ADMIN");

  // 运营者登录后：自动发现活跃事件并订阅 + 拉取 AED 点位
  useEffect(() => {
    if (!isOperator) return;
    let cancelled = false;
    const boot = async () => {
      try {
        const [active, devices] = await Promise.all([
          getActiveEvent(),
          getAedDevices(),
        ]);
        if (cancelled) return;
        setAeds(devices);
        if (active.event) {
          const st = useStore.getState();
          if (st.currentEventId !== active.event.id) {
            await st.attachEvent(active.event.id);
          } else {
            await st.refreshEvent();
          }
        }
      } catch {
        /* 错误由 store / 面板兜底显示 */
      }
    };
    void boot();
    return () => {
      cancelled = true;
    };
  }, [isOperator]);

  if (!isOperator) {
    return <ConsoleLogin />;
  }

  return (
    <div className="console-root">
      <SpaceBackground />
      <div className="console-topbar">
        <span>
          {role === "SYSTEM" ? "自动调度系统" : "管理员"} · {username ?? ""}
        </span>
        <span className={wsStatus === "connected" ? "ws-live" : ""}>
          {wsStatus === "connected" ? "● WS 实时在线" : "● 连接中…"}
        </span>
        <a href="/">移动端入口</a>
        <button onClick={logout}>退出</button>
      </div>
      <div className="console-grid">
        <StageBanner event={event} currentEventId={currentEventId} />
        <RolePanel />
        <TimelinePanel />
        <div className="right-col">
          <VitalsPanel />
          <AedPanel aeds={aeds} />
        </div>
        <div className="bottom-row">
          <AuditPanel />
          <DemoConsole />
        </div>
      </div>
    </div>
  );
}
