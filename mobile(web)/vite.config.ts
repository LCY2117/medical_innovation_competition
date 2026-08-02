import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { VitePWA } from 'vite-plugin-pwa';
import { fileURLToPath, URL } from 'node:url';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg', 'apple-touch-icon.png'],
      manifest: {
        name: '生命反射弧 - 移动应急端',
        short_name: '生命反射弧',
        description: '心脏骤停院前应急协同移动端，无需安装应用即可登录、触发 SOS、执行急救任务。',
        start_url: '/mobile/',
        scope: '/mobile/',
        display: 'standalone',
        background_color: '#071014',
        theme_color: '#071014',
        orientation: 'portrait',
        icons: [
          {
            src: '/mobile/pwa-icon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        navigateFallback: '/mobile/index.html',
        globPatterns: ['**/*.{js,css,html,svg,png,webmanifest}'],
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  base: '/mobile/',
});
