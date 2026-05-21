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
LRA_MAP_PROVIDER=demo
LRA_SILICONFLOW_API_KEY=
```

`LRA_DEMO_ADMIN_TOKEN` 建议在公网演示环境启用。启用后，创建事件、初始化演示场景、重置事件、指定患者、更新 AED 点位、导出实验数据等管理接口必须携带 `X-Demo-Admin-Token`。Web 调度台右上角“演示口令”会把该值保存在当前浏览器本地，并自动附加到管理请求中。不要把真实口令写入 Git、PPT 或聊天记录。

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
```

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

## 6. 验收清单

| 项目 | 验收方式 |
| --- | --- |
| Web 首页可访问 | 打开 `https://lifereflex.mddcommunity.top/` |
| API 健康检查 | `curl https://lifereflex.mddcommunity.top/api/health/detail` |
| WebSocket | Web 调度台显示“实时同步” |
| 演示场景 | 点击“初始化医创赛演示场景”后出现 4 个终端和 AED 点位 |
| 调度解释 | 触发患者后出现三类角色评分和理由 |
| 数据导出 | 点击“导出预实验数据”获得 JSON |
| 公网演示保护 | 配置 `LRA_DEMO_ADMIN_TOKEN` 后，未带口令的管理接口返回 403 |
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

1Panel/OpenResty 回滚：

- 恢复修改前的站点配置备份。
- 恢复 `/opt/1panel/db/agent.db` 备份。
- 运行 OpenResty `nginx -t`。
- reload OpenResty。

## 8. 比赛演示脚本

1. 打开 Web 调度台。
2. 点击“初始化医创赛演示场景”。
3. 展示患者、医生、体育生、安保和 AED 点位。
4. 选择患者端触发心脏骤停模拟。
5. 展示 AI/规则分派过程和调度解释。
6. 在 Android App 或 Web 端完成 CPR、AED、接应动作。
7. 点击“导出预实验数据”，展示时间线和指标。
8. 总结：系统价值是缩短协同组织链路、明确角色任务、记录演练数据，不直接宣称临床疗效。
