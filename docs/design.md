# 生命反射弧（Life Reflex Arc）系统设计方案 v1.0

> 由独立子智能体从零设计，未参考旧项目代码。
> 状态：待评审 → 确认后进入 M1 后端编码。

## 1. 架构总览

### 系统架构图

```
        浏览器 / 设备层
   移动端PWA(施救/保障)  患者端PWA(仅SOS+进度)  调度大屏(监控/控制)
        │                   │                   │
        │     HTTPS: REST + WSS                  │
        └───────────────────┼───────────────────┘
                        Nginx (网关层)
            · 静态资源(前端构建产物) · /api/* 反代 → backend:8000 · /ws/* 反代+Upgrade
                        │
                   FastAPI 应用层 (backend)
            ┌────────────┐   ┌────────────────┐
            │ REST 路由层  │   │ WebSocket 路由  │
            └─────┬──────┘   └───────┬────────┘
            ┌─────▼──────────────────▼────────┐
            │ 事件状态机 (StateMachineEngine)   │
            │ 分派引擎 (DispatchEngine)         │
            │   RuleBasedStrategy (默认)        │
            │   LLMStrategy (预留)              │
            └─────┬───────────────────┬────────┘
            ┌─────▼─────┐      ┌────▼────────┐
            │  SQLite    │      │ 证据导出器   │
            └───────────┘      └─────────────┘
```

## 2. 核心设计决策（评审重点）

### 2.1 状态机（严格实现）
`CREATED → SOS → DISPATCHED → CPR → AED_PICKED → AED_DELIVERED → AED_ANALYZING → SHOCK_DELIVERED → HANDOVER → ARCHIVED`

- **并行标志**：`prime/runner/guide_confirmed`、`ambulance_arrived`、`shock_count`、`seq`（WS 版本号）
- **单调性守卫**：禁止状态回退（`rank(to) >= rank(from)`）
- **幂等**：同一 `(event, action, actor)` 重复提交 → `duplicate=true`，seq 不增长
- **角色校验**：动作必须由对应角色提交
- **关键守卫**：`AED_ANALYSIS_STARTED` 需 RUNNER 已送达；`HANDOVER_COMPLETED` 需救护车已到场；除颤上限 3 次

### 2.2 ★ 最重要的决策：`available_actions` 由服务端下发
前端"一屏一动作"的依据，由后端根据 `status + role + 守卫` 推导并随 WS 下推。
前端只渲染第一个主行动，**永远不会渲染后端不允许的动作** —— 把"一屏一动作"从口号变成系统约束。

### 2.3 WS 协议（防旧消息回退）
- 消息携带单调 `version = event.seq`
- 客户端 reducer：`version < lastVersion` 丢弃；`>` 应用；`==` 仅字段级合并
- 重连后先 `SUBSCRIBE_EVENT` 拿快照，忽略一切 `version <= V` 的增量
- 乐观更新 + 服务端权威校正

### 2.4 分派引擎（可插拔）
- `DispatchStrategy` 协议接口
- `RuleBasedStrategy`（默认）：PRIME 看技能+距离+体能+状态；RUNNER 看距离+AED 距离；GUIDE 看距离+场地熟悉度
- `LLMStrategy` 预留占位（比赛 AI 加分点，不阻塞核心流程）

## 3. 数据库 Schema（SQLite, WAL）
`users` / `responder_profiles` / `events` / `event_assignments` / `event_transitions` / `health_readings` / `aed_devices`

关键字段：`events.status/seq/patient_id/started_at/*_confirmed/ambulance_arrived/shock_count`；`event_transitions` 是时间线/证据唯一来源。

## 4. REST API（/api/v1）
认证（login/demo/me）、事件（sos/详情/actions/timeline/evidence/evidence.zip）、AED（CRUD）、健康（readings）、管理（dispatch/archive/demo/reset/audit）

## 5. 移动端 PWA（一屏一动作）
- 患者端：巨大SOS按钮(二次确认+脉冲) → 救援进度(谁来救/到哪了) + 黄金时间
- 核心施救端：确认响应 → CPR(节拍器110BPM+30:2) → AED分析 → 除颤 → 交接
- AED保障端：确认响应 → 取AED → 送AED
- 环境清障端：确认响应 → 救护车到场 → 交接
- 所有端信息按角色裁剪，健康/时间线进折叠抽屉

## 6. 调度大屏
- 布局：StageBanner + RolePanel + TimelinePanel + VitalsPanel + AedPanel + AuditPanel + DemoConsole
- 视觉：深空渐变 + Canvas 星云粒子/扫描线 + 发光数字(青/红/琥珀)

## 7. 部署
Docker Compose：backend(SQLite) + web(Nginx 多页) 两个服务；WS 反代带 Upgrade 头。

## 8. 测试
状态机表驱动测试(全链路+边界) + 分派打分测试 + REST/WS 集成测试 + 前端版本合并单测。

## 9. 分阶段实施
M1 后端(3-4天) → M2 移动端PWA(3-4天) → M3 大屏(2-3天) → M4 联调打磨(2天)
