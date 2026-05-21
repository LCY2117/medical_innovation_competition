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
- 预实验证据包可导出 ZIP，包含审阅索引、原始 JSON、匿名化 JSON/CSV、结构化时间线、指标 CSV、调度依据、专家摘要、专家复核清单、专家反馈签字表、主持人跑场单、数据分析说明、数据字典、参与者知情与安全边界简表、观察员记录表、参与者问卷、基线-系统对照分析表、单轮汇总表和 manifest 校验信息。
- 客户端和 AED 点位已持久化到 SQLite，PM2 重启后仍能恢复。
- Web 控制台新增“演示口令”输入，公网演示管理接口已启用口令保护。
- Android 默认后端改为 `https://lifereflex.mddcommunity.top/` 和 `wss://lifereflex.mddcommunity.top/ws`。
- Android 现场总览新增 AED 点位和调度依据展示。
- OPPO 健康增强一期已形成 mock/fallback 闭环：后端、Web、移动 Web、Android 都能同步和展示健康摘要。
- 调度评分已经纳入健康摘要，高心率、低血氧、高压力等风险会降低高强度角色分派优先级。
- 预实验证据包已升级为 ZIP：包含审阅索引、原始 JSON、匿名化 JSON/CSV、结构化时间线、指标 CSV、调度依据、专家摘要、专家复核清单、专家反馈签字表、主持人跑场单、数据分析说明、数据字典、参与者知情与安全边界简表、观察员记录表、参与者问卷、基线-系统对照分析表、单轮汇总表和 manifest 校验信息。
- 证据包 `review_index.md` 已提供专家/评委快速审阅顺序；`manifest.json` 已补充匿名化使用建议、内部复核文件边界和 SHA-256 校验说明。
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
- 最终 P0/P1 验证已通过：后端 37 项测试、Web typecheck/build、Android debug APK 构建均通过。
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
- Web 总控台默认已降噪：首屏保留演示流程、智能分派摘要、任务单、现场拓扑和四端状态；AI 配置、调度评分、在线终端调试列表、审计和系统日志统一放入“技术详情”展开区。
- Web 总控台新增“演示准备度”检查卡：终端数量、AED 可用性、定位覆盖、健康摘要覆盖、证据导出状态会直接显示在首屏，便于正式展示前快速排雷。
- Web 总控台新增“演示入口”面板：可复制或打开 4 端导播台、患者端、核心施救端、AED 保障端和清障接驳端链接，也可同步打开 4 个手机端标签页；初始化演示场景后自动绑定当前 `incidentId`，方便发给队友手机或评委浏览器。
- `/mobile?incidentId=...` 深链已恢复可用，入口和 PWA service worker 不再清理事件编号；`/mobile-demo?incidentId=...` 会把同一个事件编号透传给四个移动端 iframe，便于专家远程或多标签复现实验。
- 移动 Web 首页已把 SOS/当前动作卡放在用户资料卡之前，急救状态下先看到行动按钮；移动演示入口也改为中文优先文案。
- 移动 Web “现场/协同”页已进一步分层：默认只展示 AED 位置、队友角色、在线状态和任务状态；分派评分、理由、健康摘要和风险标记收进“分派依据与健康摘要”展开区。
- 移动 Web 演示入口和 4 端演示台进一步弱化 PRIME/RUNNER/GUIDE 辅助代号，优先展示“核心施救端、AED 保障端、清障接驳端”和具体职责。
- 移动 Web 归档页新增“下载预实验证据包”按钮，沿用正式管理员或演示口令权限；手机端可直接输入演示口令并保存到与 Web 总控台相同的权限状态。
- Web 手机预览和 Android 归档页已移除固定 `04:35`、`3人`、`成功 (1次)` 与未实现的 NFC 传输承诺，改为按事件日志/角色状态生成总耗时、协同任务和 AED 记录摘要。
- `/mobile-demo` 导播步骤已补“归档并下载证据包”，总控台和移动/Android 可见文案进一步收敛为“智能分派/协同演示/事件证据包”等审慎表述。
- 移动 Web 和 Android 健康卡已把“模拟现场/预实验证据包/OPPO 健康摘要”等界面词进一步收敛为“协同演示现场/事件证据包/健康摘要”，减少评委视角的内部项目感。
- 移动 Web 归档态新增“复制本轮链接”和“返回总控台”，并修复归档后仍提示“响应清障接驳”的动作卡问题。
- Android 全屏急救态进一步弱化 PRIME/RUNNER/GUIDE 辅助代号，调度中、AED 回送和送达提示均改为中文职责表述。
- Android CPR 节律辅助页已将可见英文标题改为中文，减少评委演示时的语言割裂。
- Android 核心施救导航页已移除 `AHEAD`、`Start CPR` 和固定 `15 m` 占位距离；现在优先显示调度距离，没有精确距离时提示按现场指引前往患者位置。
- Android 现场总览、AED 目标卡和“我的”页已把楼层、AED 状态、定位来源等可见字段转成中文表述，避免展示 `1F/AVAILABLE/app-demo-fallback` 这类工程内部值。
- 最新完整三端验证扫尾为 `b02c634`：后端 37 项测试、Web typecheck、Web build、Android debug APK 构建均通过；Web 产物为 `App-OIunfMkh.js`、`MobileApp-DTIoJNCQ.js`。后续证据包材料增量已通过后端目标测试和全量 37 项测试。
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
& "..\.venv\Scripts\python.exe" -m unittest discover -s tests -v
```

结果：37 项通过。

地图 provider 增量目标测试：4 项通过，覆盖 `/api/health/detail`、`/api/dispatch/meta`、高德缺 Key 回退和演示导出距离指标。

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)\web"
npm run typecheck
npm run build
```

结果：均通过。最新 Web 演示入口增量构建产物为桌面 `App-DRfENPpz.js`、移动 `MobileApp-BoXW44GW.js`；证据包材料增量本身未改前端代码。

浏览器烟测：使用临时本地后端 `127.0.0.1:18086`、临时 SQLite DB、演示口令 `LCY` 通过。确认总控页默认隐藏技术细节、展开后可见 AI/日志诊断，`/mobile-demo?incidentId=...` 四个 iframe 均保留同一事件编号，`/mobile?demo=patient&slot=...&incidentId=...` 不丢失深链且 SOS 动作卡排在资料卡前。

移动现场页烟测：使用临时本地后端 `127.0.0.1:18087` 通过。确认“现场”页默认不展示“智能评分/风险标记”，展开“分派依据与健康摘要”后再展示健康与风险信息。

演示准备度烟测：使用临时本地后端 `127.0.0.1:18088` 通过。确认 Web 总控台显示“演示准备度”、终端/AED/定位/健康摘要/证据导出五项检查，初始化演示后状态为“准备就绪”。

演示入口烟测：使用临时本地后端 `127.0.0.1:18089`、临时 SQLite DB、演示口令 `LCY` 和本机 Edge 通过。确认 Web 总控台显示“演示入口”、复制全部按钮反馈“已复制”，4 端导播台和四个移动端链接均带同一个 `incidentId`。

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\lifereflex(app)"
gradle tasks --no-daemon
```

结果：通过。

```powershell
gradle :app:assembleDebug --no-daemon
```

结果：通过，APK 大小约 12 MB，使用 Android debug 签名。当前构建仅提示既有 `android.overridePathCheck=true` 实验性配置警告，不影响 debug APK 生成。

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
- `a648ad8`：Web 总控台和 `/mobile-demo` 可见标签中文化，已推送。
- `c15d60f`：记录后端/Web 验证扫尾，已推送。
- `36b818b`：记录 Android debug APK 验证扫尾，已推送。
- `169a615`：预实验证据包新增 `expert_review_checklist.md` 和 `observer_record_form.csv`，并同步测试与材料口径，已推送。
- `de3107e`：移动 Web 演示入口和 4 端演示台进一步中文职责化，已推送。
- `b885b96`：移动 Web 归档页新增受保护的证据包下载入口，已推送。
- `4e08911`：Android 全屏急救态进一步中文职责化，已推送。
- `7b8392b`：Android CPR 节律辅助页可见英文标题中文化，已推送。
- `b02c634`：记录后端/Web/Android 最新验证扫尾结果，已推送。
- `a852318`：预实验证据包新增 `pre_experiment_round_summary.csv` 单轮汇总表，方便多轮模拟合并统计，已推送。
- `3e8b2ca`：README 补齐当前演示入口、验证命令、证据包、管理员口令和 provider fallback 说明，已推送。
- `3432d11`：记录 README handoff，修正长任务状态与早晨交接，已推送。
- `e4fca63`：预实验证据包新增 `participant_consent_safety_brief.md` 和 `participant_questionnaire.csv`，并同步测试与材料口径，已推送。
- `92a5a77`：记录参与者材料 checkpoint 已推送。
- `be93e14`：预实验证据包新增 `baseline_vs_system_comparison.csv` 基线-系统对照分析模板，并同步测试与材料口径，已推送。
- `1f99b31`：预实验证据包新增 `analysis_guide.md` 数据分析说明，并同步测试与材料口径，已推送。
- `0674344`：预实验证据包新增 `expert_feedback_form.md` 事件级专家反馈与签字表，并同步测试与材料口径，已推送。
- `5dc86eb`：Web 总控台新增“演示入口”链接面板，已通过 Web typecheck/build 和本地 Edge 烟测，已推送。
- `0a97fda`：预实验证据包新增 `facilitator_run_sheet.md` 主持人/观察员跑场单，已通过后端目标测试和全量 37 项测试，已推送。
- `f775954`：Web 总控台“演示入口”新增“打开4个手机端”同步打开和弹窗拦截复制兜底，已通过 Web typecheck/build 和本地浏览器烟测，已推送。
- `56ea748`：Android 核心施救导航页移除英文/占位距离，改为中文距离提示与基础复苏按钮，已通过 debug APK 构建，已推送。
- `4116432`：预实验证据包新增 `review_index.md` 审阅索引，已通过后端目标测试和全量 37 项测试，已推送。
- `35768d6`：移动 Web 归档页可直接输入演示口令下载证据包，已通过 Web typecheck/build 和本地移动端烟测，已推送。
- 最新验证扫尾：后端 37 项测试、Web typecheck、Web build、Android debug APK 构建均通过；Web 产物为桌面 `App-DAHq5Wl1.js`、移动 `MobileApp-BiCFGvZL.js`、4 端导播台 `MobileDemoStage-DKdt3ZAL.js`。

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

2. 打开 Web 调度台时，若服务器配置了 `LRA_ADMIN_PHONES`，优先用正式管理员账号登录；否则右上角“演示口令”输入 `LCY`。之后初始化、触发、重置、导出才会成功。

3. 申请第三方资源，按 `docs/THIRD_PARTY_RESOURCES.md` 走：

- 高德/腾讯/百度地图 Key。
- Android 包名 + SHA1。
- AI API Key。
- 后续推送/短信先不强依赖。

## 演示脚本

1. 打开 `https://lifereflex.mddcommunity.top/`。
2. 点击“演示场景”或“初始化医创赛演示场景”。
3. 在“演示入口”面板复制或打开患者端、核心施救端、AED 保障端、清障接驳端和 4 端导播台链接。
4. 展示 4 类终端画像和 AED 点位。
5. 触发患者 `demo-patient`。
6. 展示核心施救、AED 保障、环境清障三类任务的分派过程和理由。
7. 用 Web、Android 或 `/mobile-demo` 四端演示台完成 CPR、AED 取送、救护车到达、交接动作。
8. 点击“证据包”，下载 ZIP 作为低成本预实验记录。对外给专家/PPT 优先使用 `review_index.md`、`experiment_anonymized.json`、`clients_anonymized.csv`、`expert_summary.md`、`expert_review_checklist.md`、`expert_feedback_form.md`、`facilitator_run_sheet.md`、`analysis_guide.md`、`data_dictionary.md`、`participant_consent_safety_brief.md`、`observer_record_form.csv`、`participant_questionnaire.csv`、`baseline_vs_system_comparison.csv` 和 `pre_experiment_round_summary.csv`。

## 仍需谨慎表达

- 这是模拟急救协同和训练系统，不宣称真实临床疗效。
- AI 是辅助分派与解释，不替代 120、AED 语音提示或专业医护判断。
- 预实验验证流程可行性、可用性和专家接受度，不验证抢救成功率。
