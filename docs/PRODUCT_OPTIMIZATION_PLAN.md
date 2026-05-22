# LifeReflexArc Product Optimization Plan

## Goal

把“生命反射弧”从能跑通的医创赛 Demo，继续打磨成可展示、可安装、可预实验、可维护的准产品形态：

- Web 调度台可用于现场演示、数据导出和讲解 AI 分派依据。
- Android APK 能让不同参与者低门槛登录、接入事件、执行任务、查看归档。
- 后端具备基础认证、会话、安全边界、实验数据和运维可观测能力。
- 第三方地图、推送、短信、AI Key 未申请前，系统仍能用 demo/fallback 模式完整演练。

## Non-Goals

- 不替用户完成实名、支付、法律协议、微信/QQ/邮箱验证码等账号动作。
- 不把 API Key、演示口令、SSH 密钥、证书私钥写入 Git。
- 不宣称临床有效性；当前定位是院前急救协同与低成本预实验系统。
- 不在没有回滚路径时做生产破坏性操作。

## P0: Competition Demo Must Look Like A Product

### Web Console

- [x] 深色/浅色模式切换，记忆用户偏好。
- [x] 顶栏明确显示实时连接、事件编号、耗时、演示口令状态。
- [x] 错误、空状态、离线重连状态更清楚，避免演示时“没反应”。
- [x] 一键协同演示场景、指定患者、导出实验数据流程足够醒目。
- [x] 首屏提供演示入口链接面板，可复制或打开 4 端导播台、患者端、核心施救端、AED 保障端和清障接驳端，并自动绑定当前事件编号。
- [x] AI 调度过程、AED 点位、角色分派理由适合直接截图放进 PPT。
- [x] Web 控制台模拟手机动作使用一致 userId，避免 CPR/AED/交接演示被后端拒绝。
- [x] 公网演示受保护时，Web 控制台 join/action 也携带演示管理员 header。

Acceptance:

- `npm run typecheck` passes.
- `npm run build` passes.
- 暗色/亮色切换后主要界面可读，无明显文字重叠。

### Android APK

- [x] 登录/注册表单更像真实 App：密码隐藏、错误更明确、加载不可重复提交。
- [x] App 启动后校验已保存登录态，过期时提示重新登录。
- [x] 首页强调“进入当前事件/查看任务”，避免公共站点下误点创建事件失败。
- [x] 现场总览展示 AED 点位、调度依据、任务状态和归档结果。
- [x] Debug APK 保持可安装；Release APK 等待发布签名决策。
- [x] Android join/action/auto-join 携带登录 token，适配公网演示口令保护。
- [x] WebSocket incidentId 做 URL 编码，避免特殊事件 ID 破坏连接 URL。

Acceptance:

- `gradle :app:assembleDebug --no-daemon` passes.
- 真机或模拟器可注册/登录/进入当前事件。

### Backend/Auth

- [x] 增加 `/auth/me`，客户端可校验当前 token。
- [x] 增加 `/auth/logout`，客户端可主动撤销 token。
- [x] Token 带过期时间，默认有效期可配置。
- [x] demo 管理端点继续由 `LRA_DEMO_ADMIN_TOKEN` 保护。
- [x] 测试覆盖注册、登录、me、logout、过期/无效 token。
- [x] 公网演示开启口令后，角色 join/action 需要本人 token 或演示管理员 token。

Acceptance:

- `python -m unittest tests.test_server tests.test_link_mechanism` passes.
- 现有 demo bootstrap/export/designate 流程不回退。

## P1: Experiment And Evidence Readiness

- [x] 实验导出增加 CSV 友好结构和稳定 JSON schema。
- [x] 每次事件归档包含时间线、角色响应耗时、AED 取送耗时、交接耗时。
- [x] Web 增加“预实验记录包”下载入口：事件 JSON、匿名化 JSON/CSV、审阅索引、说明、专家摘要、专家复核清单、专家反馈签字表、主持人跑场单、数据分析说明、数据字典、参与者知情与安全边界简表、观察员记录表、参与者问卷、基线-系统对照分析表、单轮汇总表和 manifest 校验清单。
- [x] Android 本地归档可展示参与者视角的任务总结。
- [x] 补充专家反馈模板中的证据包审阅材料、系统截图清单、参与者问卷、安全边界简表和 3-5 分钟演示脚本。

Acceptance:

- 一次完整演练后可导出足够支撑“低成本预实验”的数据。
- 文档能指导团队成员独立完成 3-5 人模拟测试。

## P1: Deployment And Operations

- [x] 健康检查暴露版本、前端构建状态、DB、WebSocket、认证状态，并检查 mobile/desktop chunk 是否存在。
- [x] 部署文档补充回滚、备份、1Panel/OpenResty 检查命令。
- [x] `.env.example` 覆盖 token TTL、地图 provider、第三方占位配置。
- [x] 服务器上项目默认在 `/opt`，保持 1Panel 可管理。
- [x] 不把本地 debug 数据库作为生产数据提交。

Acceptance:

- 本地和云端健康检查能解释当前运行状态。
- 后续部署不依赖“记忆里的命令”。

## P2: Third-Party Integration Readiness

- [x] 地图 provider 抽象：高德/腾讯/百度/纯 demo 坐标。
- [x] Android 定位权限、手动定位、地图 SDK 接入点预留。
- [x] 推送 provider 抽象：极光/厂商推送/本地 WebSocket fallback。
- [x] AI provider 抽象：本地模型、硅基流动、OpenAI-compatible API。
- [x] 短信/验证码作为未来真实注册增强，不作为当前演示阻塞项。

Acceptance:

- 申请到 Key 后只改 `.env`/安全配置和少量 adapter，不重写业务流程。

## P2: Security And Compliance Hardening

- [x] 管理后台改为正式管理员账号或最小化 RBAC。
- [x] Token 存储从普通 SharedPreferences 迁移到加密存储。
- [x] 请求频率限制、审计日志、敏感操作保护。
- [x] 用户数据匿名化导出，预实验记录不暴露手机号。
- [x] 医疗免责声明和数据使用说明补齐到 Web、移动端和预实验/专家材料口径中。

Acceptance:

- 对外展示时不暴露真实个人信息或服务端秘密。
- 后续专家评审材料中的合规表述一致。

Implementation notes:

- Android 使用 AndroidX Security 的 `EncryptedSharedPreferences` 存储 session/token，并将旧版 `lra_session` 明文登录态迁移到 `lra_session_secure`；若个别设备 Keystore 不可用，则不落盘 token，重启后要求重新登录。
- 后端新增最小 RBAC：`LRA_ADMIN_PHONES` 配置正式管理员手机号白名单，白名单用户通过普通登录获得 Bearer token，`/auth/me` 返回 `privileges=["admin"]`，管理接口接受管理员 token 或旧版 `X-Demo-Admin-Token`。只配置白名单不配置演示口令时，未登录的管理接口仍保持关闭。
- 后端新增 SQLite 审计表，记录登录、demo 管理、患者指定、角色响应、现场动作、实验导出和审计读取事件；审计记录只保留 actor/target、结果、脱敏请求 hash 和结构化元数据，不保存密码、token、API Key。
- `/api/audit/events` 由正式管理员 token 或演示管理员口令保护，Web 总控台新增“审计”按钮，可在比赛演示中展示最近留痕。
- 后端新增 auth/admin/actor 三类滑动窗口频率限制；阈值可通过 `.env` 配置，`/api/health/detail` 会暴露当前安全控制状态。
- 预实验证据包包含审阅索引、匿名化 JSON/CSV、专家摘要、专家复核清单、专家反馈签字表、主持人跑场单、数据分析说明、数据字典、参与者知情与安全边界简表、观察员记录表、参与者问卷、基线-系统对照分析表、单轮汇总表和 manifest 校验，外部材料默认使用审阅索引、数据字典和匿名化文件。
- 后端新增 `SpatialProvider`，统一调度评分、调度解释、AED 最近点和预实验指标中的距离计算；默认 `demo` 使用内置坐标 + Haversine，配置 `LRA_MAP_PROVIDER=amap` 且填入 `LRA_AMAP_SERVICE_KEY` 后会优先调用高德 WebService 距离接口，失败或缺 Key 时结构化回退到 demo 距离。
- Android 新增 `LocationProvider` 抽象和系统定位 provider：注册终端与“我的”页同步位置时优先使用系统最近定位，未授权、定位关闭或无最近定位时自动回退演示坐标；高德/腾讯 Android SDK 后续可作为 adapter 替换 provider，不影响 UI 和上报链路。
- 后端新增 `NotificationProvider` 抽象，当前 `LRA_PUSH_PROVIDER=websocket` 使用既有 WebSocket 状态同步作为比赛版实时通知；若设置 `jpush`/`vendor` 等未来 provider，会在 `/api/health/detail.pushProvider` 明确显示 adapter pending 并自动回退 WebSocket，不阻塞演示。

Validation:

- Backend unittest discovery: 36 tests OK after RBAC slice.
- Web typecheck/build: passed.
- Android debug APK build: passed after increasing Gradle heap for AndroidX Security + Compose builds.

## Validation Commands

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)"
& "..\.venv\Scripts\python.exe" -m unittest tests.test_server tests.test_link_mechanism
```

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)\web"
npm run typecheck
npm run build
```

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\lifereflex(app)"
gradle :app:assembleDebug --no-daemon
```

## Current First Implementation Slice

1. Web 调度台主题切换与演示口令状态提示。
2. 后端认证补 `/auth/me`、`/auth/logout`、token 过期时间。
3. Android 登录体验补密码隐藏与启动登录态校验。
4. 跑后端、Web、Android 构建验证。

Status: completed on 2026-05-17.

Validation:

- Backend unittest: 23 tests OK.
- Web typecheck: passed.
- Web production build: passed.
- Android debug APK build: passed.
- Browser smoke: local dashboard opened; theme button changed `dark` to `light`; admin-token status was visible.

## Current Mobile Web Implementation Slice

Goal: provide a dedicated mobile-browser URL that can substitute for the Android app during urgent or low-friction demonstrations.

Route:

- `/mobile`

Required capabilities:

- [x] Mobile login/register with the same backend account model as Android.
- [x] Persist and validate browser session through `/auth/me`.
- [x] Register the browser terminal as a rescue client with demo/manual location fallback.
- [x] Open current incident or a pasted incident ID.
- [x] Real-time WebSocket state sync with reconnect status.
- [x] Patient-side SOS start/cancel flow.
- [x] Role-aware task execution for PRIME/RUNNER/GUIDE.
- [x] Show AED sites, dispatch rationale, role status, and latest logs.
- [x] Archive/summary state is understandable on mobile.
- [x] Works from phone browser without installing APK.

Performance requirements:

- [x] `/mobile` must lazy-load separately from the desktop command console.
- [x] Mobile implementation must avoid `motion`, large Radix UI bundles, charting, and desktop-only components.
- [x] Mobile build chunk should be meaningfully smaller than the desktop dashboard chunk.
- [x] Register optional mobile service worker/manifest for installable PWA behavior without blocking normal use.
- [x] Mobile first screen should render with no desktop layout overflow at 390px width.

Validation:

- `npm run typecheck` passes.
- `npm run build` passes and emits separate mobile chunk(s).
- Browser smoke opens `/mobile`, completes auth screen rendering, and verifies key controls/text.
- Backend tests still pass.

Status: completed locally on 2026-05-18.

Implementation notes:

- `main.tsx` now selects `/mobile` at runtime and lazy-loads the mobile app separately from the desktop command console.
- Mobile uses `src/mobile/MobileApp.tsx` and `src/mobile/mobile.css`; it shares contracts through `src/shared/api.ts`, `src/shared/domain.ts`, and `src/shared/types.ts`.
- Backend now supports authenticated `patient_sos_start` / `patient_sos_cancel`, so a logged-in phone-browser user can become the patient and trigger automatic dispatch instead of relying on the dashboard-only designate endpoint.
- PWA shell assets live in `public/manifest.webmanifest`, `public/mobile-sw.js`, and `public/pwa-icon.svg`.

Validation results:

- Backend unittest: 24 tests OK.
- Web typecheck: passed.
- Web production build: passed.
- Build split: mobile JS `26.27 kB` raw / `8.80 kB` gzip; mobile CSS `9.74 kB` raw / `2.55 kB` gzip; desktop app remains a separate `App-*` chunk.
- Mobile browser smoke at `390x844`: login/register screen rendered, no horizontal overflow, manifest detected.
- Mobile SOS smoke at `390x844`: registered a browser user, opened current event, started SOS, auto-dispatched to `任务已下发`, showed patient mode, role statuses, timeline logs, and no horizontal overflow.
- Mobile UX polish smoke at `390x844`: emergency content is separated into `总览 / 任务 / 现场 / 记录`; `总览` keeps only status, identity, and the current high-priority action/patient guidance.
- Mobile theme and localization smoke: light/dark mode switches through `data-mobile-theme`; mobile logs and visible labels no longer expose raw dispatch English, `1F/2F`, or demo user IDs during the checked flow.
