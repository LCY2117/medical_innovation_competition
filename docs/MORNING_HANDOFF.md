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
- 实验数据可导出 JSON，包含时间线、指标、终端画像、AED 点位、调度依据。
- 客户端和 AED 点位已持久化到 SQLite，PM2 重启后仍能恢复。
- Web 控制台新增“演示口令”输入，公网演示管理接口已启用口令保护。
- Android 默认后端改为 `https://lifereflex.mddcommunity.top/` 和 `wss://lifereflex.mddcommunity.top/ws`。
- Android 现场总览新增 AED 点位和调度依据展示。
- Debug APK 已生成：`lifereflex(app)/app/build/outputs/apk/debug/app-debug.apk`。

## 线上已验证

- `/api/health/detail` 正常，显示 `registeredClients=4`、`registeredAedSites=2`。
- `POST /api/demo/bootstrap` 正常生成演示数据。
- `POST /api/incidents/current/designate_patient` 正常分派：
  - PRIME：`demo-doctor`
  - RUNNER：`demo-runner`
  - GUIDE：`demo-guide`
- `GET /api/experiments/current/export` 正常导出，当前演示导出为 `DISPATCHED`，9 条时间线。
- PM2 重启后再次读取客户端、AED、导出数据均正常。
- 线上前端构建产物包含“演示口令”、`X-Demo-Admin-Token`、演示场景和导出控件。
- 远端 `.env` 已设置 `LRA_DEMO_ADMIN_TOKEN`，当前演示口令为 `LCY`；不带口令访问 `/api/demo/bootstrap` 会返回 403。

## 本地验证结果

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)"
& "..\.venv\Scripts\python.exe" -m unittest tests.test_server tests.test_link_mechanism
```

结果：22 项通过。

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
6. 用 Web 或 Android 完成 CPR、AED 取送、救护车到达、交接动作。
7. 点击“导出数据”，把 JSON 作为低成本预实验记录。

## 仍需谨慎表达

- 这是模拟急救协同和训练系统，不宣称真实临床疗效。
- AI 是辅助分派与解释，不替代 120、AED 语音提示或专业医护判断。
- 预实验验证流程可行性、可用性和专家接受度，不验证抢救成功率。
