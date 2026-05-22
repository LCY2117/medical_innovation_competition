# 生命反射弧部署运行手册

## 1. 目标架构

推荐公开入口：

- Web 调度台：`https://lifereflex.mddcommunity.top/`
- REST API：`https://lifereflex.mddcommunity.top/api/*`
- WebSocket：`wss://lifereflex.mddcommunity.top/ws`

推荐服务器目录：

- 项目目录：`/opt/lifereflex`
- 运行用户：优先 `deploy`，必要时才使用 `root`
- 应用监听：`127.0.0.1:8029` 或其它空闲本地端口
- 对外代理：1Panel / OpenResty 管理 HTTPS 和反向代理

## 2. 环境变量

生产 `.env` 不提交 Git。可从 `server(web)/.env.example` 复制：

```bash
LRA_HOST=127.0.0.1
LRA_PORT=8029
LRA_RELOAD=false
LRA_API_PREFIX=/api
LRA_CORS_ORIGINS=https://lifereflex.mddcommunity.top
LRA_DB_PATH=data/lifereflexarc.db
LRA_WEB_DIST_DIR=web/dist
LRA_SOS_DURATION_SEC=10
LRA_DISPATCH_DELAY_SEC=3
LRA_DEMO_ADMIN_TOKEN=
LRA_ADMIN_PHONES=
LRA_AUDIT_LOG_ENABLED=true
LRA_RATE_LIMIT_ENABLED=true
LRA_RATE_LIMIT_AUTH_PER_MINUTE=20
LRA_RATE_LIMIT_ADMIN_PER_MINUTE=60
LRA_RATE_LIMIT_ACTOR_PER_MINUTE=120
LRA_PUSH_PROVIDER=websocket
LRA_MAP_PROVIDER=demo
LRA_AMAP_SERVICE_KEY=
LRA_MAP_DISTANCE_TIMEOUT_SEC=3
LRA_SILICONFLOW_API_KEY=
```

`LRA_DEMO_ADMIN_TOKEN` 建议在公网演示环境启用。启用后，创建事件、初始化演示场景、重置事件、指定患者、更新 AED 点位、导出实验数据等管理接口必须携带 `X-Demo-Admin-Token`。Web 调度台右上角“演示口令”会把该值保存在当前浏览器本地，并自动附加到管理请求中。不要把真实口令写入 Git、PPT 或聊天记录。

`LRA_ADMIN_PHONES` 是正式管理员账号白名单，可填写逗号分隔手机号。白名单用户仍通过普通注册/登录拿到 Bearer token，`/auth/me` 会返回 `privileges=["admin"]`，并可用该 token 调用初始化、重置、AED 更新、导出和审计等管理接口。若同时配置 `LRA_DEMO_ADMIN_TOKEN`，旧的演示口令仍可作为比赛现场备用通道；不要把手机号白名单当作密码或密钥提交到 Git。

`LRA_AUDIT_LOG_ENABLED` 默认开启，会在 SQLite 中记录登录、演示管理、角色响应、现场动作、实验导出和审计读取事件。Web 总控台“审计”按钮读取 `GET /api/audit/events`，该接口需要正式管理员 token 或演示管理员口令。审计事件不保存密码、token 或 API Key，仅保留 actor/target、结果、脱敏请求 hash 和结构化元数据。

`LRA_RATE_LIMIT_*` 是轻量级进程内滑动窗口限流，适合比赛公开演示和小规模预实验防误刷。多进程/多实例生产部署时，应在 OpenResty、1Panel WAF、Redis 或网关层补充集中限流。

`LRA_PUSH_PROVIDER=websocket` 是比赛版默认通知 provider，复用现有 WebSocket 状态同步。未来可设置 `jpush` 或 `vendor` 作为厂商推送预留值；在 adapter 和凭据未配置前，系统会在健康检查中显示 fallback 原因并继续走 WebSocket。

如果配置 AI：

```bash
LRA_SILICONFLOW_MODEL=Qwen/Qwen2-7B-Instruct
LRA_SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1
LRA_SILICONFLOW_TIMEOUT_SEC=8
```

如果配置高德：

```bash
LRA_MAP_PROVIDER=amap
LRA_AMAP_WEB_KEY=
LRA_AMAP_WEB_SECURITY_JS_CODE=
LRA_AMAP_SERVICE_KEY=
LRA_MAP_DISTANCE_TIMEOUT_SEC=3
```

后端距离 provider 已接入健康检查和调度解释。配置高德服务端 Key 后，调度评分、AED 最近点和预实验 `runnerRouteMeters` 会优先使用高德 WebService 距离；接口失败、超时或未配置 Key 时会自动回退到 demo/Haversine 距离，并在 `/api/health/detail.mapProvider` 中显示 fallback 原因。

## 3. 本地构建验证

后端：

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)"
& "..\.venv\Scripts\python.exe" -m unittest tests.test_server tests.test_link_mechanism
```

前端：

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\server(web)\web"
npm install
npm run typecheck
npm run build
```

Android：

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\lifereflex(app)"
gradle :app:assembleDebug --no-daemon
```

当前本机已安装 Android SDK command-line tools，路径为 `C:\Users\LCY\AppData\Local\Android\Sdk`。如换电脑，需要设置 `ANDROID_HOME` 或创建 `lifereflex(app)/local.properties`：

```properties
sdk.dir=C\:\\Users\\LCY\\AppData\\Local\\Android\\Sdk
```

当前 debug APK 输出路径：

```text
lifereflex(app)/app/build/outputs/apk/debug/app-debug.apk
```

正式展示前如需 release APK，请按 `docs/ANDROID_RELEASE_READINESS.md` 准备 release keystore、SHA1 和第三方 Android Key。Gradle 会在 `LRA_RELEASE_STORE_FILE`、`LRA_RELEASE_STORE_PASSWORD`、`LRA_RELEASE_KEY_ALIAS`、`LRA_RELEASE_KEY_PASSWORD` 四项齐全时自动签名 release；这些值只能放在 `local.properties` 或环境变量中，不提交 Git。

## 4. 服务器部署步骤

### 4.1 连接与目录

```bash
ssh deploy@104.248.151.6
sudo mkdir -p /opt/lifereflex
sudo chown -R deploy:deploy /opt/lifereflex
```

如果 `deploy` 不可用，再使用 `root` 排查，不建议长期用 root 直接运行应用。

### 4.2 拉取代码

```bash
cd /opt/lifereflex
git clone git@github.com:LCY2117/medical_innovation_competition.git app
cd app
```

如服务器不能访问 GitHub，可从本地打包上传。

### 4.3 安装后端依赖

```bash
cd "/opt/lifereflex/app/server(web)"
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### 4.4 构建前端

```bash
cd "/opt/lifereflex/app/server(web)/web"
npm ci
npm run build
```

### 4.5 启动服务

推荐使用 systemd：

```ini
[Unit]
Description=LifeReflexArc API and Web
After=network.target

[Service]
User=deploy
WorkingDirectory=/opt/lifereflex/app/server(web)
EnvironmentFile=/opt/lifereflex/app/server(web)/.env
ExecStart=/opt/lifereflex/app/server(web)/.venv/bin/python -m app.cli
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

保存为 `/etc/systemd/system/lifereflex.service` 后：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now lifereflex
sudo systemctl status lifereflex --no-pager
curl -fsS http://127.0.0.1:8029/api/health/detail
```

### 4.6 生产备份

每次部署前建议先备份代码版本、环境变量和 SQLite 数据：

```bash
cd /opt/lifereflex/app
git rev-parse --short HEAD
backup_dir="/opt/lifereflex/backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup_dir"
cp -a "server(web)/.env" "$backup_dir/server.env"
cp -a "server(web)/data/lifereflexarc.db" "$backup_dir/lifereflexarc.db"
```

如数据库正在高频写入，优先使用 SQLite 在线备份：

```bash
sqlite3 "/opt/lifereflex/app/server(web)/data/lifereflexarc.db" ".backup '/opt/lifereflex/backups/lifereflexarc-$(date +%Y%m%d-%H%M%S).db'"
```

## 5. 1Panel / OpenResty

在 1Panel 中配置：

- 主域名：`lifereflex.mddcommunity.top`
- 反代目标：`http://127.0.0.1:8029`
- WebSocket：开启
- HTTPS：Let's Encrypt 自动申请，开启自动续签

命令行自动化时必须：

- 先确认 DNS 指向 `104.248.151.6`。
- 确认 `/opt/1panel/www/conf.d/lifereflex.mddcommunity.top.conf` 不存在或属于当前站点。
- 备份 `/opt/1panel/db/agent.db`。
- 写入 1Panel 数据库记录，确保面板网站列表可管理。
- `nginx -t` 成功后再 reload OpenResty。

常用检查命令：

```bash
dig +short lifereflex.mddcommunity.top
sudo cp -a /opt/1panel/db/agent.db /opt/1panel/db/agent.db.bak.$(date +%Y%m%d-%H%M%S)
sudo openresty -t || sudo nginx -t
sudo systemctl reload openresty || sudo systemctl reload nginx
curl -I https://lifereflex.mddcommunity.top/
curl -fsS https://lifereflex.mddcommunity.top/api/health/detail
```

1Panel/OpenResty 配置文件位置可能随安装版本变化，常见路径包括：

- `/opt/1panel/www/sites/<domain>/proxy/*.conf`
- `/opt/1panel/www/conf.d/<domain>.conf`
- `/usr/local/openresty/nginx/conf/conf.d/*.conf`

自动化脚本必须先探测实际路径并备份原文件，不要盲写固定路径。

## 6. 验收清单

| 项目 | 验收方式 |
| --- | --- |
| Web 首页可访问 | 打开 `https://lifereflex.mddcommunity.top/` |
| API 健康检查 | `curl https://lifereflex.mddcommunity.top/api/health/detail`，确认 `frontend.indexReady`、`frontend.mobileChunkReady`、`frontend.desktopChunkReady`、DB、WebSocket、认证和 `demoReadiness` |
| 安全控制 | `health.detail.security` 显示审计和限流配置，`storage.auditEventCount` 会随关键动作增加 |
| WebSocket | Web 调度台显示“实时同步” |
| 演示场景 | 点击“初始化协同演示场景”后出现 4 个终端和 AED 点位 |
| 调度解释 | 触发患者后出现三类角色评分和理由 |
| 地图距离 provider | `health.detail.mapProvider` 显示 `mode`、`distanceSource`、`configured` 和 fallback 原因；未配置 Key 时仍可完整演示 |
| 推送 provider | `health.detail.pushProvider` 显示 `mode=websocket`、`channel=websocket_state`；配置未来 provider 时应显示 fallback 原因 |
| 数据导出 | 点击“证据包”获得 ZIP，包内含审阅索引、匿名化 JSON/CSV、专家摘要、数据字典和 manifest 校验信息 |
| 公网演示保护 | 配置 `LRA_DEMO_ADMIN_TOKEN` 后，未带口令的管理接口返回 403 |
| 正式管理员账号 | 配置 `LRA_ADMIN_PHONES` 后，白名单手机号注册/登录的 `/auth/me.user.privileges` 含 `admin`，Bearer token 可访问管理接口 |
| 审计日志 | Web 总控台点击“审计”可看到最近登录、演示、导出和现场动作；无口令读取返回 403 |
| Android | App 安装后能登录并连接同一事件 |

## 7. 回滚

应用回滚：

```bash
sudo systemctl stop lifereflex
cd /opt/lifereflex/app
git log --oneline -5
git checkout <previous-commit-or-tag>
cd "server(web)/web" && npm ci && npm run build
cd .. && . .venv/bin/activate && pip install -r requirements.txt
sudo systemctl restart lifereflex
```

数据库回滚：

```bash
sudo systemctl stop lifereflex
cp -a /opt/lifereflex/backups/<backup-dir>/lifereflexarc.db "/opt/lifereflex/app/server(web)/data/lifereflexarc.db"
sudo chown deploy:deploy "/opt/lifereflex/app/server(web)/data/lifereflexarc.db"
sudo systemctl start lifereflex
curl -fsS http://127.0.0.1:8029/api/health/detail
```

Git 注意事项：

- `server(web)/data/lifereflexarc.db` 是本地/演示运行数据，部署前后都不要把临时运行产生的 DB diff 提交进功能检查点。
- 如必须提交数据库结构样例，先停服务、脱敏、说明用途，并单独提交。

1Panel/OpenResty 回滚：

- 恢复修改前的站点配置备份。
- 恢复 `/opt/1panel/db/agent.db` 备份。
- 运行 OpenResty `nginx -t`。
- reload OpenResty。

## 8. 比赛演示脚本

1. 打开 Web 调度台。
2. 点击“初始化协同演示场景”。
3. 在“演示入口”面板复制或打开 4 端导播台、患者端、核心施救端、AED 保障端和清障接驳端链接，确认链接均绑定当前事件编号。
4. 展示患者、医生、体育生、安保和 AED 点位。
5. 选择患者端触发疑似心脏骤停协同流程。
6. 展示 AI/规则分派过程和调度解释。
7. 在 Android App 或 Web 端完成 CPR、AED、接应动作。
8. 点击“证据包”，展示 `review_index.md`、`timeline.csv`、`metrics.csv`、`dispatch_rationale.csv`、`experiment_anonymized.json`、`expert_summary.md` 和 `expert_feedback_form.md`。
9. 总结：系统价值是缩短协同组织链路、明确角色任务、记录演练数据，不直接宣称临床疗效。

## 9. 预实验证据包说明

Web 调度台提供两个导出接口：

- `GET /api/experiments/current/export`：返回当前事件的完整结构化 JSON，适合开发调试和接口联调。
- `GET /api/experiments/current/package`：返回 ZIP 证据包，适合医创赛材料、专家反馈、预实验归档和 Excel 统计。

ZIP 包当前包含：

- `review_index.md`：专家/评委快速审阅索引，说明建议打开顺序、材料用途和公开边界。
- `experiment.json`：完整事件数据，保留终端、AED、调度依据和健康摘要。
- `experiment_anonymized.json`：匿名化事件数据，优先用于 PPT、专家反馈和对外展示。
- `clients.csv` / `clients_anonymized.csv`：终端画像、角色、位置和健康摘要表。
- `timeline.csv`：含 `ts`、`tsIso`、`elapsedSec`、`eventType`、`participantCode`、`role`、`msg` 的结构化时间线，公开审阅时不暴露原始 userId。
- `metrics.csv`：响应耗时、AED 取送、交接、角色完整度、定位/健康覆盖率等指标。
- `aed_sites.csv`：AED 点位、可用状态、楼层和取用说明。
- `dispatch_rationale.csv`：每个角色的匿名参与者代号、评分因素和解释。
- `expert_summary.md`：给专家/指导教师快速审阅的预实验摘要。
- `expert_review_checklist.md`：专家现场复核清单，覆盖演示材料、关键指标、医学流程、AI 分派和安全边界。
- `expert_feedback_form.md`：事件级专家反馈与签字表，用于专家评分、100-300 字意见和签字留档。
- `facilitator_run_sheet.md`：主持人/观察员跑场单，用于按步骤完成演练、记录 T1-T6 并导出证据包。
- `analysis_guide.md`：预实验数据分析说明，解释 T1-T6、问卷、基线对照和谨慎结论写法。
- `data_dictionary.md`：证据包数据字典，解释核心指标、CSV 字段、角色代码和对外表述边界。
- `participant_consent_safety_brief.md`：参与者知情与安全边界简表，用于演练前说明、签名或口头确认记录。
- `observer_record_form.csv`：观察员补充记录表，用于填写系统无法自动采集的现场行为、评分和开放反馈。
- `participant_questionnaire.csv`：参与者主观问卷表，用于收集任务理解、协同减负、移动端提示和安全边界评分。
- `baseline_vs_system_comparison.csv`：无系统基线轮与系统轮对照分析模板，用于汇总 T1-T6 差值、百分比变化和主观评分差异。
- `pre_experiment_round_summary.csv`：单轮预实验汇总行，适合多轮演练合并到 Excel 做描述性统计。
- `expert_feedback_summary.csv`：专家意见汇总与整改闭环表，用于合并多名专家评分、风险点、负责人、处理状态和二次复核意见。
- `README.md`：证据包使用说明。
- `manifest.json`：文件清单、SHA256 校验、生成时间和事件编号。

对外材料默认使用审阅索引、匿名化文件、专家摘要、专家复核清单、专家反馈签字表、专家意见汇总表、主持人跑场单、分析说明、数据字典、参与者安全简表、观察员记录表、参与者问卷、基线对照分析表和单轮汇总表。完整 `experiment.json` 只用于内部复核，不应直接发给专家或放入公开 PPT。

下载 ZIP 后建议先在本地复核 manifest 和 SHA-256：

```powershell
python scripts\verify_evidence_package.py "D:\path\to\lifereflex-experiment.zip"
```

通过时脚本会输出 `OK`；如果提示 hash 不一致、缺文件、路径异常或公开/内部材料边界冲突，应重新导出证据包并保留问题记录。

多轮预实验结束后，可以把每轮下载的 ZIP 放到同一目录，生成一张汇总 CSV：

```powershell
python scripts\summarize_evidence_rounds.py "D:\path\to\evidence-zips" --output "D:\path\to\round-summary.csv"
```

该脚本会先复用 manifest/SHA-256 校验，再合并每个包内的 `pre_experiment_round_summary.csv`，输出包路径、包 hash、校验状态、事件编号、生成时间和 T1-T6/覆盖率/角色完整度等核心字段。若需要把异常包也写入汇总表用于排查，可追加 `--include-invalid`。

汇总 CSV 生成后，可以再导出一份 Markdown 分析摘要：

```powershell
python scripts\analyze_round_summary.py "D:\path\to\round-summary.csv" --output "D:\path\to\round-analysis.md"
```

该报告只做描述性统计，并给出适合 PPT 改写的谨慎结论模板；不要把它写成真实临床疗效证明。
