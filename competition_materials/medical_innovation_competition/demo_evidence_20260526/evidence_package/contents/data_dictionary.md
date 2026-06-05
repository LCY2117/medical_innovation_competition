# 生命反射弧证据包数据字典

事件编号：1b6545bb-c46d-4add-baae-9143a6a18324
生成时间：2026-05-26T01:39:13.827000+00:00

## 一、核心文件

| 文件 | 内容 | 建议用途 |
| --- | --- | --- |
| `review_index.md` | 3 分钟审阅顺序、材料用途和公开边界 | 专家或评委先打开 |
| `experiment_anonymized.json` | 匿名化后的事件、角色、指标和健康摘要 | PPT、专家审阅、内部复盘 |
| `clients_anonymized.csv` | 匿名化参与者列表，含角色、位置、健康摘要字段 | Excel 汇总、问卷匹配 |
| `timeline.csv` | 事件日志的结构化时间线，使用匿名参与者代号和脱敏日志文本 | 复核 T0-T6 节点 |
| `metrics.csv` | 系统自动计算的核心指标 | 低成本预实验结果表 |
| `dispatch_rationale.csv` | 角色分派评分、距离、理由和警示，使用匿名参与者代号 | 展示智能协同解释性 |
| `observer_record_form.csv` | 观察员补充记录模板 | 记录系统无法自动采集的现场行为 |
| `participant_questionnaire.csv` | 参与者主观问卷模板 | 计算可理解性、压力、可用性评分 |
| `baseline_vs_system_comparison.csv` | 无系统基线轮与系统轮对照模板 | 描述性对照分析 |
| `pre_experiment_round_summary.csv` | 单轮汇总行 | 多轮合并统计 |
| `round-summary.csv` / `round-analysis.md` / `round-chart-data.csv` / `round-review-actions.csv` | 由一键分析脚本在 ZIP 外生成 | 多轮描述性统计、PPT 谨慎摘要、图表数据和复核行动清单 |
| `manifest.json` | 文件 hash、生成时间、隐私边界 | 复核证据包完整性 |

## 二、自动指标

| 字段 | 当前值 | 含义 | 解释边界 |
| --- | --- | --- | --- |
| `dispatchSeconds` | 1s | T1，患者触发到三类任务分派完成的秒数 | 仅表示系统流程耗时 |
| `firstResponderResponseSeconds` | 0s | T2，患者触发到核心施救端接单或启动处置的秒数 | 不等同真实到达患者身边 |
| `cprStartSeconds` | 2s | T3，患者触发到核心施救端记录 CPR 开始的秒数 | 不等同真实高质量 CPR |
| `aedPickupSeconds` | 6s | T4，患者触发到 AED 保障端记录取到 AED 的秒数 | 取决于预实验路径和道具点位 |
| `aedDeliverySeconds` | 9s | T5，患者触发到 AED 送达患者位置的秒数 | 不代表真实除颤完成 |
| `ambulanceArriveSeconds` | 12s | T6，患者触发到清障接驳端记录救护接管的秒数 | 可由观察员补充真实口令时间 |
| `roleAssignmentCompleteness` | 1.0 | PRIME/RUNNER/GUIDE 三类角色是否完整分派，1.0 表示三类均有终端 | 仅表示任务分派完整性 |
| `locationCoveragePercent` | 100.0% | 有位置摘要的终端占比 | 演示坐标不等同真实定位精度 |
| `healthCoveragePercent` | 100.0% | 有健康摘要的终端占比 | 演示健康摘要不等同真实诊断 |
| `runnerRouteMeters` | 41.6 | AED 保障端到 AED 点位再回患者位置的估算总距离 | 地图 Key 未接入时可能为 beta/Haversine 估算 |

## 三、角色代码

| 代码 | 对外中文 | 说明 |
| --- | --- | --- |
| `PATIENT` | 患者端 | 触发 SOS、保持位置、等待协同成员到场 |
| `PRIME` | 核心施救 | 前往患者位置并执行 CPR/AED 操作提示 |
| `RUNNER` | AED 保障 | 就近取用 AED 并回送患者位置 |
| `GUIDE` | 环境清障 | 疏通通道、接引救护车、协助交接 |

## 四、关键 CSV 字段

| 字段 | 常见文件 | 含义 |
| --- | --- | --- |
| `participantCode` | `clients_anonymized.csv`、`timeline.csv`、`dispatch_rationale.csv`、问卷、汇总表 | 匿名参与者代号，如 P001/R001 |
| `eventType` | `timeline.csv` | 系统从日志归类出的事件类型 |
| `elapsedSec` | `timeline.csv` | 相对本轮第一条日志的秒数 |
| `msg` | `timeline.csv` | 脱敏后的日志文本，内部 userId 已替换为参与者代号 |
| `score` | `dispatch_rationale.csv` | 角色候选综合评分 |
| `reasons` | `dispatch_rationale.csv` | 分派理由，通常包含能力、距离、AED 可达性或健康风险 |
| `warnings` | `dispatch_rationale.csv` | 候选终端风险或降权提示 |
| `observerValue` | `observer_record_form.csv` | 观察员人工补充值 |
| `score1to5` | 问卷、观察员表 | 1-5 分主观评分 |
| `baseline...` / `system...` | `baseline_vs_system_comparison.csv` | 基线轮与系统轮配对数据 |

## 五、匿名化与禁止表述

- 对外材料优先使用 `review_index.md`、`experiment_anonymized.json`、`clients_anonymized.csv`、`timeline.csv`、`dispatch_rationale.csv` 和本数据字典。
- `review_index.md`、`timeline.csv` 与 `dispatch_rationale.csv` 已使用 `participantCode` 做公开审阅匿名化，不应再手工补回原始 userId。
- `experiment.json`、`clients.csv` 可能包含原始 userId、显示名、组织等内部复核信息，不建议直接放入 PPT。
- 可以写“用于模拟急救协同、训练复盘、预实验记录和专家反馈准备”。
- 不要写“提高抢救成功率”“改善患者预后”“替代 120/AED/医护判断”。
- 样例健康摘要、演示位置或演示健康摘要只能作为演示/预实验数据来源说明，不能写成真实临床监测结论。
