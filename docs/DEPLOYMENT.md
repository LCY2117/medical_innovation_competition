# 落地配置清单

本文档列出系统从"演示可用"到"完整落地"所需的全部外部配置项。每项标注当前状态、影响与获取途径。

## 当前部署信息

| 项 | 值 |
|---|---|
| 服务器 | `111.230.52.99`（Ubuntu 24.04，腾讯云） |
| 域名 | `https://www.yclsm.top/`（正式 Let's Encrypt 证书） |
| API | `https://www.yclsm.top/api` |
| WebSocket | `wss://www.yclsm.top/ws` |
| Web 调度台 | `https://www.yclsm.top/` |
| 后端 | Docker Compose（`/opt/lifereflex/server(web)`），容器只绑 `127.0.0.1:8080`，Nginx 443 反代 |
| 数据库 | SQLite `server(web)/data/lifereflexarc.db`（挂载卷，不提交 Git） |
| Android | `local.properties` 指向 `https://www.yclsm.top/` |

## 演示管理员口令（已配置）

`LRA_demo_ADMIN_TOKEN` 已设置在服务器 `server(web)/.env`，用于保护调度台的敏感操作
（事件重置、demo 初始化、证据包导出）。该值**不提交到 Git**，请保存在安全位置。

- Web 调度台首次使用敏感功能时，会提示输入该口令（存于浏览器 localStorage）
- 作用范围：`/incidents/current/reset`、`/demo/bootstrap`、`/experiments/*/export`、`/incidents` 创建
- 普通 demo 登录与急救操作（SOS、CPR、AED 等）不受影响，仍用各自 Bearer token

如需更换：编辑服务器 `server(web)/.env` 的 `LRA_demo_ADMIN_TOKEN`，然后
`cd server(web) && docker compose up -d`。

## 待配置项（按优先级）

### 1. AI 智能分派（影响演示"智能感"）

| 配置 | 当前 | 说明 |
|---|---|---|
| `LRA_SILICONFLOW_API_KEY` | 空 | 硅基流动 API Key，开通：https://cloud.siliconflow.cn |
| `LRA_SILICONFLOW_MODEL` | `Qwen/Qwen2-7B-Instruct` | 默认模型，可按需调整 |

- 当前状态：`dispatch/meta` 返回 `"configured": false`，走 fallback 规则分派
- 设置后：分派会调用 LLM 生成 PRIME/RUNNER/GUIDE 决策，`dispatch/meta` 返回 `"configured": true`

### 2. 高德地图（影响"真实感"）

| 配置 | 当前 | 说明 |
|---|---|---|
| `LRA_MAP_PROVIDER` | `demo` | 改为 `amap` 启用真实地图 |
| `LRA_AMAP_WEB_KEY` | 空 | Web 端 JS API 密钥（控制台：https://console.amap.com） |
| `LRA_AMAP_WEB_SECURITY_JS_CODE` | 空 | Web 端安全密钥 |
| `LRA_AMAP_SERVICE_KEY` | 空 | 服务器端 Web 服务密钥 |
| Android `LRA_AMAP_ANDROID_KEY` | 空 | 在 `local.properties` 配置 |

- 当前状态：`mapProvider.requestedProvider = "demo"`，距离用 haversine 计算
- 设置后：启用真实地理编码、路线规划、AED 距离打分

### 3. 真实健康数据（影响"真实感"）

| 项 | 当前 | 说明 |
|---|---|---|
| Android Health Connect | 代码就绪未真机验证 | 需在带 Google Play 的模拟器或真机实测 |
| `LRA_HEALTH_PROVIDER` | `mock` | 服务器端健康摘要，保持 mock 即可（客户端真实数据优先） |

Health Connect 验证步骤：
1. 真机/带 Play 的 AVD 安装 Health Connect App
2. 安装 APK，设置页 → 设备能力 → 授权健康数据
3. 欢太健康 App → 连接 Health Connect，开启数据同步
4. 回到 App 查看心率/血氧/睡眠是否显示真实值

### 4. 可选增强

| 项 | 当前 | 说明 |
|---|---|---|
| `LRA_ADMIN_PHONES` | 空 | 正式管理员手机号（注册用户获得 admin 权限） |
| `LRA_AUTH_TOKEN_TTL_SEC` | 604800 | 登录有效期，比赛可调短 |
| `LRA_SOS_DURATION_SEC` | 5 | SOS 倒计时秒数（比赛节奏控制） |
| `LRA_PUSH_PROVIDER` | `websocket` | 推送方式，保持默认 |

## 本地模型（可选）

如需完全离线分派，参考 `server(web)/LOCAL_MODEL.md`：
- 配置 `LRA_LOCAL_MODEL_BASE_URL` 指向本地模型服务
- `LRA_PREFER_LOCAL_MODEL=true` 优先本地模型

## 服务器运维备忘

- 证书：Let's Encrypt 自动续期（snap timer 每天检查），覆盖 `www.yclsm.top`、`api.yclsm.top`
- 端口：Nginx 80/443/4443（4443 → opencode web），后端 8080 仅本机
- 容器：`lifereflex-server`（restart unless-stopped），数据在 `server(web)/data/`
- 更新部署：服务器 `cd /opt/lifereflex && git pull`，再 `cd server(web) && docker compose up -d --build`
- 测试：`docker exec lifereflex-server python -m unittest tests.test_server tests.test_link_mechanism`
