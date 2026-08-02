import { useEffect } from "react";
import Header from "./components/Header";
import { useStore } from "./lib/store";
import AdminPage from "./pages/AdminPage";
import ConsolePage from "./pages/console/ConsolePage";
import GuidePage from "./pages/GuidePage";
import LoginPage from "./pages/LoginPage";
import PatientPage from "./pages/PatientPage";
import PrimePage from "./pages/PrimePage";
import RunnerPage from "./pages/RunnerPage";

/** 应用根：登录态 + 按角色分发到对应端（一屏一动作）。
 *  路径 /console 时进入 M3 调度台大屏（独立全屏布局）。 */
export default function App() {
  const role = useStore((s) => s.role);
  const initialized = useStore((s) => s.initialized);
  const error = useStore((s) => s.error);
  const clearError = useStore((s) => s.clearError);

  const isConsole =
    typeof window !== "undefined" &&
    window.location.pathname.startsWith("/console");

  // 恢复持久化会话（token + 上次事件）
  useEffect(() => {
    useStore.getState().init();
  }, []);

  // 大屏路由：独立于移动端布局
  if (isConsole) {
    return <ConsolePage />;
  }

  // 错误自动消失
  useEffect(() => {
    if (!error) return;
    const t = setTimeout(() => clearError(), 6000);
    return () => clearTimeout(t);
  }, [error, clearError]);

  let page;
  switch (role) {
    case "PATIENT":
      page = <PatientPage />;
      break;
    case "PRIME":
      page = <PrimePage />;
      break;
    case "RUNNER":
      page = <RunnerPage />;
      break;
    case "GUIDE":
      page = <GuidePage />;
      break;
    case "SYSTEM":
    case "ADMIN":
      page = <AdminPage />;
      break;
    default:
      page = <LoginPage />;
  }

  if (!initialized) {
    return (
      <div className="app" style={{ alignItems: "center", justifyContent: "center" }}>
        <span className="spin" />
      </div>
    );
  }

  return (
    <div className="app">
      {role ? <Header /> : null}
      <main className="app-content">{page}</main>
      {error && (
        <div className="toast" onClick={clearError}>
          {error}
        </div>
      )}
    </div>
  );
}
