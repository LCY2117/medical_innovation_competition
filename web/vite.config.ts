import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

// 后端地址（M1）：开发时走 Vite 代理，生产由 Nginx 反代同源 /api、/ws
const BACKEND = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["favicon.svg", "icons/icon-192.png", "icons/icon-512.png"],
      manifest: {
        name: "生命反射弧 · 应急协同",
        short_name: "生命反射弧",
        description: "移动端急救响应协同系统：一屏一动作",
        theme_color: "#05070f",
        background_color: "#05070f",
        display: "standalone",
        orientation: "portrait",
        start_url: "/",
        lang: "zh-CN",
        icons: [
          {
            src: "icons/icon-192.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "any maskable",
          },
          {
            src: "icons/icon-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable",
          },
        ],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,svg,png,woff2}"],
        navigateFallback: "/index.html",
        runtimeCaching: [
          {
            // API 请求走网络优先，避免缓存陈旧事件数据
            urlPattern: ({ url }) => url.pathname.startsWith("/api/"),
            handler: "NetworkFirst",
            options: { cacheName: "lifereflex-api", networkTimeoutSeconds: 5 },
          },
        ],
      },
    }),
  ],
  server: {
    host: true,
    port: 5173,
    proxy: {
      // REST：/api/v1/* → http://127.0.0.1:8000/api/v1/*
      "/api": {
        target: BACKEND,
        changeOrigin: true,
      },
      // WebSocket：/ws/events → ws://127.0.0.1:8000/ws/events
      "/ws": {
        target: BACKEND,
        ws: true,
        changeOrigin: true,
      },
    },
  },
});
