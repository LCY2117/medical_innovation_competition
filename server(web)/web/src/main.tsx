
import { createRoot } from "react-dom/client";
import React, { Suspense } from "react";
import "./styles/index.css";

const DesktopApp = React.lazy(() => import("./app/App"));
const MobileApp = React.lazy(() => import("./mobile/MobileApp"));
const MobileDemoStage = React.lazy(() => import("./mobile/MobileDemoStage"));

function isMobileRoute() {
  return window.location.pathname === "/mobile" || window.location.pathname.startsWith("/mobile/");
}

function isMobileDemoRoute() {
  return window.location.pathname === "/mobile-demo" || window.location.pathname.startsWith("/mobile-demo/");
}

function Root() {
  const App = isMobileDemoRoute() ? MobileDemoStage : isMobileRoute() ? MobileApp : DesktopApp;

  return (
    <Suspense
      fallback={
        <div style={{ minHeight: "100dvh", display: "grid", placeItems: "center", background: "#071014", color: "#eff8f6" }}>
          生命反射弧正在加载...
        </div>
      }
    >
      <App />
    </Suspense>
  );
}

if ("serviceWorker" in navigator && isMobileRoute()) {
  window.addEventListener("load", () => {
    navigator.serviceWorker
      .register("/mobile-sw.js")
      .then((registration) => {
        registration.waiting?.postMessage({ type: "SKIP_WAITING" });
        registration.addEventListener("updatefound", () => {
          registration.installing?.addEventListener("statechange", () => {
            registration.waiting?.postMessage({ type: "SKIP_WAITING" });
          });
        });
      })
      .catch(() => {
        // PWA support should never block emergency browser access.
      });
  });
}

createRoot(document.getElementById("root")!).render(<Root />);
