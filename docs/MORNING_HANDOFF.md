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
- 后端增加输入边界校验：经纬度、定位精度、健康指标、AED 状态会拒绝明显非法值。
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

结果：30 项通过。

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

结果：通过，APK 大小约 12 MB，使用 Android debug 签名。

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
