本地模型接入与验证指南

概述

本项目支持优先使用本地模型服务（兼容 SiliconFlow 风格的 /v1/chat/completions），当本地不可用时自动回退到远程 API 或内部规则引擎。

启动本地模型服务（示例）

1. 进入训练/微调仓库：

```bash
cd model_training
```

2. 根据 `model_training/README.md` 启动本地推理 API。示例（若仓库提供）：

```bash
# 如果仓库有 LLaMA-Factory 并提供 start_api.sh
cd LLaMA-Factory
./start_api.sh
```

3. 默认本地服务地址示例：`http://localhost:8008/v1`。

配置后端使用本地模型

1. 复制并编辑后端环境文件：

```bash
cd server(web)
cp .env.example .env
# 编辑 .env：设置 LRA_LOCAL_MODEL_BASE_URL=http://localhost:8008/v1
```

2. 可选：确认并设置 `LRA_PREFER_LOCAL_MODEL=true`（默认 true，表示优先尝试本地模型）。

启动后端（开发）

```bash
python -m app.cli --with-web --reload
```

快速验证本地模型可用性

1. 直接向本地模型发起简单请求：

```bash
curl -s -X POST "http://localhost:8008/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -d '{"model":"Qwen/Qwen2.5-7B-Instruct","messages":[{"role":"system","content":"ping"}],"temperature":0.0}' | jq .
```

若能返回 JSON（含 choices 等字段），说明本地服务可用。

2. 查看后端的调度元信息（会显示 localModelAlive 与 provider）

```bash
curl -s http://127.0.0.1:8080/api/dispatch/meta | jq .
```

- `provider` 字段：`local_model` / `siliconflow` / `fallback`
- `localModelAlive`：布尔，表示短探测是否成功

3. 模拟一次调度（需先有注册客户端和当前 incident）：

```bash
# 举例：把某个 userId 设为患者并触发调度
curl -s -X POST http://127.0.0.1:8080/api/incidents/current/designate_patient \
  -H "Content-Type: application/json" \
  -d '{"patientUserId":"user_123"}' | jq .
```

响应中的 `source` 字段会告诉你使用的是 `local_model` 还是 `siliconflow` 或 `fallback`。

验证回退逻辑

- 停止本地模型服务后，再次执行调度；后端应自动回退到远程 API（如果配置了 `LRA_SILICONFLOW_API_KEY`），否则使用内部评分回退并返回 `fallback`。

故障排查要点

- 如果 `localModelAlive` 为 false：确认本地服务是否在运行、端口与路径是否正确、是否需要认证头。
- 后端不会把占位 API Key（例如空字符串或 "EMPTY"）发送到本地服务。
- 查看后端日志（运行时输出）以获取具体超时或解析错误信息。

附录

- 配置变量：`LRA_LOCAL_MODEL_BASE_URL`、`LRA_LOCAL_MODEL_NAME`、`LRA_LOCAL_MODEL_TIMEOUT_SEC`、`LRA_PREFER_LOCAL_MODEL`。
- 本文档不执行 git 提交，所有修改为工作区文件，待人工 review 后提交。