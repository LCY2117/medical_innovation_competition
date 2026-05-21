# 生命反射弧早晨交接报告

## 当前可演示状态

- 公网 Web 调度台：`https://lifereflex.mddcommunity.top/`
- REST API：`https://lifereflex.mddcommunity.top/api/*`
- WebSocket：`wss://lifereflex.mddcommunity.top/ws`
- 1Panel/OpenResty 反代：正常，证书为 Let's Encrypt E7，有效期到 2026-07-28。
- PM2 后端：`mspc-backend`，监听 `127.0.0.1:8029`，已重启验证。

## 已完成的核心能力

- Web 一键初始化医创赛演示场景：患者、医生、体育生、安保、2 个 AED 点位。
- 云端调度会结合人员画像、患者距离、AED 距离和健康风险，输出 PRIME/RUNNER/GUIDE。
- 调度结果包含可解释理由、评分、到患者距离、到 AED 距离。
- 预实验证据包可导出 ZIP，包含原始 JSON、匿名化 JSON/CSV、结构化时间线、指标 CSV、调度依据、专家摘要和 manifest 校验信息。
- 客户端和 AED 点位已持久化到 SQLite，PM2 重启后仍能恢复。
- Web 控制台新增“演示口令”输入，公网演示管理接口已启用口令保护。
- Android 默认后端改为 `https://lifereflex.mddcommunity.top/` 和 `wss://lifereflex.mddcommunity.top/ws`。
- Android 现场总览新增 AED 点位和调度依据展示。
- OPPO 健康增强一期已形成 mock/fallback 闭环：后端、Web、移动 Web、Android 都能同步和展示健康摘要。
- 调度评分已经纳入健康摘要，高心率、低血氧、高压力等风险会降低高强度角色分派优先级。
- 预实验证据包已升级为 ZIP：包含原始 JSON、匿名化 JSON/CSV、结构化时间线、指标 CSV、调度依据、专家摘要和 manifest 校验信息。
- 证据包 `manifest.json` 已补充匿名化使用建议、内部复核文件边界和 SHA-256 校验说明。
- `/api/health/detail` 增加 `demoReadiness`，可检查演示前的终端数量、AED、定位、健康摘要覆盖和导出状态。
- Web 总控台新增 5 步演示流程条；`/mobile-demo` 新增 4 端导播脚本。
- 移动 Web 患者 SOS 增加二次确认，第一次点击只进入确认态，避免误触发。
- 移动 Web 任务页默认优先“自动接单”，PRIME/RUNNER/GUIDE 手动抢接折叠为“演示备用”，减少绕过 AI 分派叙事的误操作。
- 移动 Web PRIME 任务卡新增 CPR/AED 下一动作提示，会随 AED 取回、送达、分析、除颤状态切换。
- Android 首页和事件页已接通“自动接单”，登录后可直接加入当前事件并进入任务页。
- Android 任务页和现场总览新增“最近现场时间线”，APK 端可以直接看到患者触发、角色响应、AED 取送、交接等日志。
- Android AED 保障者全屏任务页会显示目标 AED 名称、位置楼层、取用说明、到 AED 距离和回送患者距离。
- Android “我的”页新增演示位置切换，可一键上报患者走廊、一层大厅、校门岗亭、操场入口，方便演示调度距离变化。
- Android “我的”页新增位置同步：可申请系统定位权限、同步系统最近定位，并显示位置来源、经纬度和精度；未授权或没有定位时自动回退演示坐标。
- 预实验方案已补 S01-S08 系统截图清单和 3-5 分钟专家/PPT 演示脚本。
- `/api/health/detail` 可检查前端构建产物：index、assets 数量、mobile chunk、desktop chunk、最新资源时间。
- Web 总控和移动端已加入简短安全边界：仅用于模拟演练、训练复盘和预实验，不替代 120、AED 语音提示、专业医护判断或真实医疗诊断。
- Android 本地归档会展示参与者视角任务总结，患者、PRIME、RUNNER、GUIDE、待命终端都有不同复盘要点。
- 部署手册已补生产备份、SQLite 在线备份、1Panel/OpenResty 检查、数据库回滚和本地 DB 不提交的 Git 注意事项。
- Android 首页快速入口已改为优先“进入当前事件/自动接单”，新建事件降级为“演示备用”。
- 最终 P0/P1 验证已通过：后端 30 项测试、Web typecheck/build、Android debug APK 构建均通过。
- 第三方资源文档新增 provider/fallback 接入契约：地图、AI、健康、推送、短信都按真实 provider + demo fallback 设计。
- 后端增加输入边界校验：经纬度、定位精度、健康指标、AED 状态会拒绝明显非法值。
- 后端新增 SQLite 审计日志和轻量频控：登录、demo 管理、患者指定、角色响应、现场动作、实验导出均有脱敏留痕，`/api/health/detail` 可查看安全控制状态。
- Web 总控台新增“审计”按钮，可用演示口令查看最近操作留痕，适合作为比赛答辩中的安全合规截图。
- Android session/token 已从普通 SharedPreferences 迁移到 AndroidX Security 加密存储，并兼容旧明文登录态迁移；若设备安全存储不可用，不再把 token 落盘。
- Android Gradle JVM 堆已提高到 2GB，避免新增安全依赖后 Windows 构建出现 GC thrashing。
- 后端地图距离 provider 已抽象：默认 demo/Haversine，`LRA_MAP_PROVIDER=amap` + `LRA_AMAP_SERVICE_KEY` 可启用高德 WebService 距离；健康检查和调度元数据会显示 provider、距离来源和 fallback 原因。
- Android 原生定位 provider 已预埋：无需第三方 Key 即可走系统最近定位 + 演示坐标 fallback，后续高德 Android SDK 可作为 adapter 接入。
- 后端通知 provider 已抽象：比赛版默认 `LRA_PUSH_PROVIDER=websocket`，未来 `jpush`/`vendor` provider 未接入时会显示 pending 并回退 WebSocket。
- 后端最小 RBAC 已预埋：`LRA_ADMIN_PHONES` 可配置正式管理员手机号白名单，白名单用户登录后 `/auth/me` 返回 `admin` 权限，管理接口接受 Bearer token 或旧演示口令。
- 移动端患者 SOS 正延迟分派已修复：`/mobile?demo=patient` 等待倒计时后不会再卡在 `DISPATCHING`，会继续完成角色分派。
- Web 总控台在服务器配置 `LRA_ADMIN_PHONES` 后会显示正式管理员登录入口，管理请求优先使用 Bearer token，演示口令仍可作为备用。
- Web 总控台与 `/mobile-demo` 已进一步去除评委可见的英文/内部码：演示阶段、审计留痕、AED 状态、四端角色标题和现场日志都优先显示中文。
- Debug APK 已生成：`lifereflex(app)/app/build/outputs/apk/debug/app-debug.apk`。

## 线上已验证

- `/api/health/detail` 正常，显示 `registeredClients=4`、`registeredAedSites=2`。
- `POST /api/demo/bootstrap` 正常生成演示数据。
- `POST /api/incidents/current/designate_patient` 正常分派：
  - PRIME：`demo-doctor`
  - RUNNER：`demo-runner`
  - GUIDE：`demo-guide`
- `GET /api/experiments/current/export` 正常导出；ZIP 证据包可通过 `/api/experiments/current/package` 下载。
- PM2 重启后再次读取客户端、AED、导出数据均正常。
- 线上前端构建产物包含“演示口令”、`X-Demo-Admin-Token`、演示场景和导出控件。
- 远端 `.env` 已设置 `LRA_DEMO_ADMIN_TOKEN`，当前演示口令为 `LCY`；不带口令访问 `/api/demo/bootstrap` 会返回 403。

## 本地验证结果

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)"
& "..\.venv\Scripts\python.exe" -m unittest tests.test_server tests.test_link_mechanism
```

结果：33 项通过。

地图 provider 增量目标测试：4 项通过，覆盖 `/api/health/detail`、`/api/dispatch/meta`、高德缺 Key 回退和演示导出距离指标。

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)\web"
npm run typecheck
npm run build
```

结果：均通过。

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\lifereflex(app)"
gradle tasks --no-daemon
```

结果：通过。

```powershell
gradle :app:assembleDebug --no-daemon
```

结果：通过，APK 大小约 12 MB，使用 Android debug 签名。当前构建会提示 AndroidX Security API deprecation warning，以及 `PhoneAppRoot.kt` 一个非阻塞 Kotlin warning，不影响 debug APK 生成。

## 本轮新增检查点

- `7c2bcac`：强化预实验证据包，加入匿名化导出、专家摘要、manifest hash、结构化 timeline 和历史事件角色修正。
- `2752c24`：接通 Android 自动接单入口。
- `befc1f7`：增加 Web 总控台流程条和 4 端演示台导播脚本。
- `9272fdb`：移动 Web SOS 增加二次确认。
- `48106e9`：增加实验输入边界校验。
- `a8104ca`：更新早晨交接与演示脚本。
- `d33d038`：健康风险标签本地化，用户界面不再暴露 mock/fallback 工程词。
- `69d7cc8`：补齐证据包文档口径、manifest 隐私/校验说明、移动 Web 备用手动接单折叠、Android 最近现场时间线。
- `6342bb7`：记录检查点已推送状态。
- `5cc9534`：Android AED 保障者全屏任务页显示目标 AED 与回送距离。
- `b2c0370`：记录 AED 目标卡检查点已推送。
- `5a18fc5`：移动 Web PRIME 任务卡增加 CPR/AED 下一动作提示。
- `449815f`：记录移动 Web 下一动作提示检查点已推送。
- `261b05d`：Android “我的”页加入演示位置切换。
- `e8e23b8`：记录演示位置检查点已推送。
- `71b9834`：记录本轮轻量验证结果。
- `fb8d3e2`：补充专家截图清单和 3-5 分钟演示脚本。
- `4aa7317`：记录专家材料检查点已推送。
- `af96cae`：扩展健康检查中的前端构建产物诊断。
- `3526ca0`：记录健康检查诊断检查点已推送。
- `95b4e88`：Web/移动端加入安全边界和数据使用提示。
- `7e39ee3`：记录安全边界检查点已推送。
- `b2b650f`：Android 本地归档加入参与者视角任务总结。
- `9e48785`：记录 Android 归档总结检查点已推送。
- `aa0160b`：补充部署备份、回滚和 1Panel/OpenResty 检查命令。
- `7e9c65e`：记录部署手册检查点已推送。
- `4600663`：Android 首页优先进入当前事件/自动接单，新建事件降级为演示备用。
- `6b832e7`：记录 Android 首页 CTA 检查点已推送。
- `f0ce716`：记录最终 P0/P1 验证结果。
- `4b0f11f`：后端审计日志/频控、Web 审计面板、Android 加密 token 存储、Gradle 构建稳定性，已推送。
- `1259394`：地图距离 provider 抽象与高德 WebService 预埋，已推送。
- `f30be6d`：Android 系统定位 provider 与位置同步 UI，已推送。
- `5855cf4`：后端通知 provider 与 WebSocket fallback，已推送。
- `a635129`：后端正式管理员账号最小 RBAC，已推送。
- `337496d`：前端共享类型补齐 `AuthUser.privileges`，已推送。
- `9b373f4`：患者 SOS 正延迟修复与 Web 总控台管理员登录，已推送。
- 待本轮提交：Web 总控台和 `/mobile-demo` 可见标签中文化。

## 你醒来后最该做的三件事

1. 真机安装并走一遍 App 演示流程：

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\lifereflex(app)"
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r "app\build\outputs\apk\debug\app-debug.apk"
```

如未连接手机，也可以直接把这个 APK 发到手机安装：

```powershell
app\build\outputs\apk\debug\app-debug.apk
```

2. 打开 Web 调度台时，右上角“演示口令”输入 `LCY`。之后初始化、触发、重置、导出才会成功。

3. 申请第三方资源，按 `docs/THIRD_PARTY_RESOURCES.md` 走：

- 高德/腾讯/百度地图 Key。
- Android 包名 + SHA1。
- AI API Key。
- 后续推送/短信先不强依赖。

## 演示脚本

1. 打开 `https://lifereflex.mddcommunity.top/`。
2. 点击“演示场景”或“初始化医创赛演示场景”。
3. 展示 4 类终端画像和 AED 点位。
4. 触发患者 `demo-patient`。
5. 展示 PRIME/RUNNER/GUIDE 的分派过程和理由。
6. 用 Web、Android 或 `/mobile-demo` 四端演示台完成 CPR、AED 取送、救护车到达、交接动作。
7. 点击“证据包”，下载 ZIP 作为低成本预实验记录。对外给专家/PPT 优先使用 `experiment_anonymized.json`、`clients_anonymized.csv` 和 `expert_summary.md`。

## 仍需谨慎表达

- 这是模拟急救协同和训练系统，不宣称真实临床疗效。
- AI 是辅助分派与解释，不替代 120、AED 语音提示或专业医护判断。
- 预实验验证流程可行性、可用性和专家接受度，不验证抢救成功率。
