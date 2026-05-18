
import { createRoot } from "react-dom/client";
import React, { Suspense } from "react";
import "./styles/index.css";

const DesktopApp = React.lazy(() => import("./app/App"));
const MobileApp = React.lazy(() => import("./mobile/MobileApp"));

function isMobileRoute() {
  return window.location.pathname === "/mobile" || window.location.pathname.startsWith("/mobile/");
}

function cleanMobileUrlState() {
  if (!isMobileRoute() || !window.location.search) {
    return;
  }

  const url = new URL(window.location.href);
  if (!url.searchParams.has("incidentId")) {
    return;
  }

  url.searchParams.delete("incidentId");
  window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
}

cleanMobileUrlState();

function Root() {
  const App = isMobileRoute() ? MobileApp : DesktopApp;

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
    navigator.serviceWorker.register("/mobile-sw.js").catch(() => {
      // PWA support should never block emergency browser access.
    });
  });
}

createRoot(document.getElementById("root")!).render(<Root />);
