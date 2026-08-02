# 生命反射弧（Life Reflex Arc）

面向城市公共场所的**急救应急协同系统**：患者一键 SOS → 系统按规则自动分派施救者 → 各端「一屏一动作」协同救援 → 调度大屏全程监控 → 归档生成证据包。

设计哲学：**把「一屏一动作」从口号变成系统约束** —— 每个角色在每个状态能做什么，由后端状态机根据 `status + role + 守卫` 推导，随 WebSocket 下推 `available_actions`，前端永远只渲染后端允许的动作。救援过程是一个严格单调的事件状态机，不可回退、可幂等、全程留痕。

---

## 快速开始

### 方式一：Docker 一键启动（生产/演示推荐）

要求：Docker Engine 20.10+ 与 Docker Compose v2。

```bash
docker compose up -d --build
```

- 访问系统：<http://localhost:8080>（前端 PWA / 各端）
- 调度大屏：<http://localhost:8080/console>
- 后端 API 文档：<http://localhost:8080/api/v1/docs>（经 Nginx 反代，或用 `docker exec` 在容器内访问 8000）

常用命令：

```bash
docker compose up -d --build   # 构建并后台启动
docker compose logs -f backend # 跟踪后端日志
docker compose down            # 停止
docker compose down -v         # 停止并删除数据卷（清空 data/）
```

宿主端口可配置（默认 8080）：

```bash
WEB_PORT=80 docker compose up -d    # 映射到 80 端口
```

环境变量一览：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `WEB_PORT` | `8080` | Nginx 暴露到宿主的端口 |
| `SECRET_KEY` | `change-me-in-production` | JWT 签名密钥，生产务必覆盖 |
| `CORS_ORIGINS` | `http://localhost:8080` | 允许的跨域来源 |
| `DATABASE_URL` | `sqlite:////app/data/lifereflex.db` | SQLite 位置（卷挂载 `./data`） |

SQLite 数据持久化在宿主机 `./data/`（已被 `.gitignore` 排除）。

### 方式二：本地开发模式

需要 Python 3.10+ 与 Node 18+。

**后端**（端口 8000）：

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows；macOS/Linux 用 source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端**（端口 5173，Vite 已配置代理 `/api`、`/ws` → `127.0.0.1:8000`）：

```bash
cd web
npm install
npm run dev
```

访问 <http://localhost:5173>，Vite 热更新。

---

## 系统组成（三端）

| 端 | 访问入口 | 角色 | 核心体验 |
| --- | --- | --- | --- |
| **移动端 PWA** | `/`（登录后按角色分发） | PATIENT / PRIME / RUNNER / GUIDE | 一屏一动作：每屏只渲染一个主行动按钮，操作由后端约束 |
| **调度大屏** | `/console` | ADMIN / SYSTEM | 深空主题监控面板：StageBanner + 角色面板 + 时间线 + 体征 + AED 点位 + 审计 + 演示控制台 |
| **后端 API** | `/api/v1/*`（REST）、`/ws/events`（WebSocket） | 全角色 | 状态机引擎 + 分派引擎 + 证据导出，SQLite 持久化 |

---

## 演示流程

> 演示前请保证系统处于空闲状态（无进行中事件）；可在任意端页面按 F12 打开多个窗口分别扮演不同角色，或直接在多个浏览器标签页登录不同角色。

### 完整救援链路（推荐用「大屏演示控制台」驱动）

1. **打开调度大屏** <http://localhost:8080/console>，用 `admin / admin1234` 登录。
2. 大屏「演示控制台」点击 **触发SOS**：系统自动创建事件并立即分派 PRIME/RUNNER/GUIDE。
   - 若提示冲突，先点击 **重置** 再重新触发。
3. **患者端**（另开标签页，PATIENT 一键登录）：显示救援进度与「黄金时间」倒计时。
4. **核心施救端 PRIME**：确认响应 → **开始CPR**（进入 110BPM 节拍器）→ 等 AED 送达后 **开始AED分析** → **实施除颤**（上限 3 次）→ **完成交接**。
5. **AED保障端 RUNNER**：确认响应 → **已取AED** → **AED已送达**。
6. **环境清障端 GUIDE**：确认响应 → **救护车已到场**（此后可完成交接）。
7. 回到大屏：**模拟体征** 采集 HR/SpO₂/压力读数 → 观察 VitalsPanel 实时刷新；时间线/审计面板记录每一步。
8. 任一端 **完成交接** 后，大屏用 `admin` 点击 **归档**（或 ARCHIVE 动作），事件进入 ARCHIVED。
9. 大屏 **导出JSON / 导出ZIP**：一键导出完整证据包（时间线 + 体征 + 分派记录）。

### 也可纯患者端触发（不经大屏）

患者端（PATIENT）点击巨大 **SOS** 按钮 → 二次确认 → 触发求救并自动分派；其后各施救端自动发现活跃事件（`GET /events/active`）并订阅，无需手输事件编号。

---

## 演示账号

| 角色 | 用户名 | 密码 | 用途 |
| --- | --- | --- | --- |
| 患者 | `patient` | `demo1234` | 触发 SOS、查看救援进度 |
| 核心施救 | `prime` | `demo1234` | CPR → AED → 除颤 → 交接 |
| AED保障 | `runner` | `demo1234` | 取 AED、送 AED |
| 环境清障 | `guide` | `demo1234` | 救护车到场确认、交接 |
| 系统管理员 | `admin` | `admin1234` | 大屏登录、触发/重置/归档 |
| 自动调度系统 | `system` | `admin1234` | 系统级动作（SYSTEM 角色） |

> 移动端登录页提供了 4 个演示角色的一键登录卡片，无需手动输账号。管理账号走下方「账号登录」表单。

---

## 状态机（简要）

`CREATED → SOS → DISPATCHED → CPR → AED_PICKED → AED_DELIVERED → AED_ANALYZING → SHOCK_DELIVERED → HANDOVER → ARCHIVED`

关键约束：

- **单调性守卫**：禁止状态回退（除颤往返 `SHOCK_DELIVERED → AED_ANALYZING` 例外，受 3 次上限约束）。
- **幂等**：同一 `(event, action, actor)` 重复提交 → `duplicate=true`，`seq` 不增长。
- **角色校验**：动作必须由对应角色提交（如仅 PRIME 可 CPR，仅 RUNNER 可取/送 AED）。
- **关键守卫**：`AED_ANALYSIS_STARTED` 需 RUNNER 已送达；`HANDOVER_COMPLETED` 需救护车已到场；除颤上限 3 次。
- **并行标志**：`prime/runner/guide_confirmed`、`ambulance_arrived`、`shock_count`、`seq`（WS 版本号）。
- **WS 协议**：所有事件消息携带单调 `version = seq`，客户端按版本丢弃旧消息/合并同版本，重连后取快照防回退。

---

## 目录结构

```
lifereflex-new/
├── docker-compose.yml        # 一键部署编排
├── .gitignore
├── README.md
├── docs/
│   └── design.md             # 完整设计方案
├── backend/                  # FastAPI 后端
│   ├── Dockerfile            # python:3.12-slim
│   ├── healthcheck.py        # 容器健康检查（登录 + /auth/me）
│   ├── requirements.txt
│   ├── pyproject.toml        # pytest 配置
│   ├── app/
│   │   ├── main.py           # 应用工厂/入口
│   │   ├── config.py         # 环境变量配置
│   │   ├── db.py             # SQLite + WAL
│   │   ├── seed.py           # 演示种子数据
│   │   ├── api/              # REST + WS 路由
│   │   ├── core/             # 状态机 / 分派 / 证据 / WS Hub
│   │   ├── models/           # SQLModel 模型
│   │   └── schemas/          # Pydantic schema
│   └── tests/                # pytest 测试
└── web/                      # Vite + React PWA + 调度大屏
    ├── Dockerfile            # node 构建 → nginx 运行（多阶段）
    ├── nginx.conf            # SPA + /api + /ws 反代 + gzip + 缓存
    ├── package.json
    ├── vite.config.ts        # dev 代理 /api、/ws
    └── src/                  # 各角色页面 + 大屏面板
```

---

## 测试

**后端**（39 个测试：状态机全链路/边界、分派打分、REST/WS 集成、证据导出）：

```bash
cd backend
.venv\Scripts\activate          # 先激活虚拟环境
pytest                           # 全部测试
pytest -q                        # 简洁输出
```

**前端**（类型检查 + 生产构建）：

```bash
cd web
npm run typecheck                # tsc --noEmit
npm run build                    # 类型检查 + 产物构建到 dist/
```

---

## 已知限制

- **单实例**：当前为单容器部署（SQLite + 单进程 uvicorn），适合演示/比赛规模；高并发需多 worker + 独立数据库。
- **WS 与多 worker**：WebSocket Hub 与分派定时器为进程内状态，多 worker 需引入外部存储/消息通道。
- **认证**：演示密码 `demo1234`/`admin1234` 为明文默认值，生产必须通过环境变量覆盖并改用强密钥。
- **证据导出**：ZIP 由后端内存构建，大事件体积较大，当前规模无影响。
- **HTTPS/WSS**：Nginx 默认 HTTP/WS；生产需在 `web/nginx.conf` 前置 TLS（证书 + 443 + `wss`），前端会自动切换 `wss://`。
