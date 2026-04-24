# Life Reflex Arc Server + Web

先把环境配置文件填好，再启动项目。

另外，Android 端如果要正常联调，也要先配置它自己的地址：去 `lifereflex(app)/gradle.properties` 里修改 `LRA_API_BASE` 和 `LRA_WS_BASE`，把它们改成当前后端/Web 所在机器的 IP 和端口。

例如：

- `LRA_API_BASE=http://192.168.1.20:8080/`
- `LRA_WS_BASE=ws://192.168.1.20:8080/ws`

这两个值必须指向同一台主机、同一个端口；如果换了电脑 IP、模拟器、真机网络，记得一起改。

接着是后端本身的配置文件位置：

- `server(web)/.env.example`：环境变量模板，先从这里复制一份
- `server(web)/.env`：本地实际生效的配置文件

```bash
copy .env.example .env
```

至少先确认这些变量已经按你的本地环境填写，并了解它们的作用：

- `LRA_SILICONFLOW_API_KEY`：SiliconFlow 的 API Key，用来启用 AI 调度；不填时会自动退回本地规则分配
- `LRA_DB_PATH`：SQLite 数据库文件路径，用来保存事件状态和恢复信息
- `LRA_WEB_DIST_DIR`：前端构建产物目录，后端做一体化托管时会从这里读取静态文件

如果这是第一次运行 Web 端，先安装前端依赖：

```bash
cd "server(web)\web"
npm install --verbose
cd ..
```

## 快速启动

云端服务和 Web 一起启动：

```bash
cd "server(web)"
python -m app.cli --with-web --reload
```

如果你也要先把 Android 端编出来：

```bash
cd "lifereflex(app)"
.\gradlew.bat :app:assembleDebug
```

## 上云最短流程（Linux）

在云服务器中执行：

```bash
cd server(web)
cp .env.example .env
bash scripts/deploy_linux.sh
```

脚本会自动完成：

- 安装 Python 依赖（FastAPI + Uvicorn）
- 安装并构建 Web 前端（Vite build）
- 后台启动后端服务并写入日志

上云后，Android 端只需要改一个文件：

- `lifereflex(app)/gradle.properties`

把其中两项改成你的云地址（建议域名）：

- `LRA_API_BASE=https://你的域名/`
- `LRA_WS_BASE=wss://你的域名/ws`

## 项目介绍

这是已经完成 `server + web` 合并后的统一工程。后端现在不再是单文件 MVP，而是一个分层的 FastAPI 项目。

## 目录结构

```text
server(web)/
├─ app/
│  ├─ api/        # REST / WebSocket 路由
│  ├─ core/       # 配置与前端托管
│  ├─ models/     # Pydantic schemas
│  ├─ services/   # 事件状态机与广播逻辑
│  ├─ storage/    # SQLite 持久化
│  ├─ cli.py      # 固定启动入口
│  └─ main.py     # FastAPI app factory
├─ web/           # 合并后的 Vite 可视化端
├─ tests/         # 后端回归测试
├─ .env.example   # 后端配置模板
└─ server.py      # 兼容入口
```

## 后端单独启动（可选）

### 1. 安装后端依赖

```bash
cd server(web)
python -m venv .venv
.venv\Scripts\activate
pip install "fastapi>=0.115,<1.0" "uvicorn[standard]>=0.30,<1.0"
```

### 2. 配置环境变量

```bash
copy .env.example .env
```

默认配置已经够本地开发使用，主要参数有：

- `LRA_HOST`：FastAPI 监听地址，默认本地开发一般用 `127.0.0.1`
- `LRA_PORT`：FastAPI 监听端口，默认和 README 中的启动命令保持一致
- `LRA_RELOAD`：是否开启热重载，开发时通常设为 `true`
- `LRA_API_PREFIX`：REST API 的统一前缀，便于前后端路由统一管理
- `LRA_SOS_DURATION_SEC`：SOS 急救流程的默认倒计时或持续时长
- `LRA_CORS_ORIGINS`：允许跨域访问的前端来源地址列表
- `LRA_DB_PATH`：SQLite 数据库文件路径，保存当前事件、状态和恢复数据
- `LRA_WEB_DIST_DIR`：前端构建产物目录，后端一体化运行时从这里托管静态页面
- `LRA_WEB_DEV_HOST`：Web 开发服务器监听地址
- `LRA_WEB_DEV_PORT`：Web 开发服务器监听端口

### 3. 只启动后端

开发模式：

```bash
python -m app.cli --reload
```

生产模式：

```bash
python -m app.cli
```

如果你还想兼容旧命令，也仍然可以用：

```bash
uvicorn server:app --host 0.0.0.0 --port 8080 --reload
```

## Web 开发

推荐直接用一条命令同时启动后端和前端：

```bash
python -m app.cli --with-web --reload
```

默认会同时启动：

- FastAPI: `http://127.0.0.1:8080`
- Vite: `http://127.0.0.1:5173`

如果你还没装过前端依赖，先执行一次：

```bash
cd web
npm install
cd ..
```

也仍然支持分开启动：

```bash
cd web
npm install
npm run dev
```

Vite 已代理：

- `/api` -> `http://127.0.0.1:8080`
- `/ws` -> `ws://127.0.0.1:8080`

所以前端本地开发时不需要再写死公网 IP。

## 一体化运行

先构建前端：

```bash
cd web
npm install
npm run build
```

再启动后端：

```bash
cd ..
python -m app.cli
```

构建完成后，后端会直接托管 `web/dist`：

- 页面入口: `/`
- 静态资源: `/assets/*`
- 推荐 API: `/api/*`
- 兼容旧 API: `/incidents*`, `/health`
- 详细健康检查: `/api/health/detail`
- WebSocket: `/ws`

## 测试

```bash
python -m unittest tests.test_server
```

当前测试覆盖：

- 旧接口与 `/api` 双路由兼容
- SQLite 持久化后重启恢复当前事件
- `/api/health/detail` 的存储与前端状态输出

## AI 调度说明

SiliconFlow 的配置文件放在：

- `server（云端服务）/.env`

最少需要关心这些变量：

- `LRA_DISPATCH_DELAY_SEC=3`
- `LRA_SILICONFLOW_API_KEY=你的 key`
- `LRA_SILICONFLOW_MODEL=Qwen/Qwen2-7B-Instruct`
- `LRA_SILICONFLOW_BASE_URL=https://api.siliconflow.cn/v1`
- `LRA_SILICONFLOW_TIMEOUT_SEC=8`

如果不填 `LRA_SILICONFLOW_API_KEY`，系统会自动退回本地规则分配，不会阻塞演示。

当前发给 AI 的候选画像字段包括：

- `userId`
- `displayName`
- `organization`
- `healthCondition`
- `professionIdentity`
- `profileBio`
- `deviceType`
- `online`
- `patientCandidate`
- `isPatient`

当前要求模型返回的格式固定为：

```json
{
  "PRIME": "userId or null",
  "RUNNER": "userId or null",
  "GUIDE": "userId or null"
}
```

前端调度台也可以直接查看这些说明：

- `GET /api/dispatch/meta`
