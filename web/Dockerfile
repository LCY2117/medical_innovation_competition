# 生命反射弧 · 前端（Vite + React PWA）
# 多阶段构建：node 构建产物 → nginx 托管 + 反代 /api 与 /ws
# 构建：docker build -t lifereflex-web .

# ---------- 阶段 1：构建 ----------
FROM node:20-alpine AS build
WORKDIR /app

# 先拷依赖清单，利用 Docker 层缓存（package-lock 不变则跳过 npm ci）
COPY package.json package-lock.json ./
RUN npm ci

# 拷贝源码并构建
COPY . .
RUN npm run build

# ---------- 阶段 2：运行（nginx） ----------
FROM nginx:1.27-alpine

# 站点配置（SPA fallback + /api + /ws 反代 + gzip + 缓存策略）
COPY nginx.conf /etc/nginx/conf.d/default.conf
# 静态产物
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
