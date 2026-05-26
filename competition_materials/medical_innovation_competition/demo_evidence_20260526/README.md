# 生命反射弧演示证据材料包

生成日期：2026-05-26

用途：医创赛国赛 PPT、讲稿、专家反馈和系统级模拟预实验材料准备。所有内容均为模拟演示数据，不作为临床疗效、抢救成功率或患者预后改善证据。

## 1. 可直接放入 PPT 的截图

目录：`screenshots/`

建议使用顺序：

| 文件 | 建议用途 |
| --- | --- |
| `01_public_dashboard.png` | Web 总控台、公网部署证明 |
| `02_public_mobile_demo_stage.png` | 一键四端演示入口 |
| `03_public_mobile_prime.png` | 移动端任务页示例 |
| `04_mobile_patient.png` | 患者端/SOS 流程 |
| `05_mobile_prime.png` | 核心施救端/CPR 流程 |
| `06_mobile_runner.png` | AED 保障端/取送 AED |
| `07_mobile_guide.png` | 清障接驳端/救护车接应 |
| `08_dashboard_preflight.png` | 总控台演示准备状态 |

## 2. 正式归档证据包

优先使用：

`evidence_package/lifereflex_evidence_round_01_archived_20260526.zip`

该包对应事件：

`1b6545bb-c46d-4add-baae-9143a6a18324`

HTTP 下载证明：

`evidence_package/round_01_archived_http_headers.txt`

证据包 SHA-256：

`4264b8f126bb7385e7e590dc60df81d26bc4baddb38ae27ad34b0203964e2193`

解压目录：

`evidence_package/round_01_archived_contents/`

其中优先给 PPT、专家或队友看的文件：

| 文件 | 用途 |
| --- | --- |
| `review_index.md` | 评审材料阅读顺序 |
| `expert_summary.md` | 专家快速摘要 |
| `experiment_anonymized.json` | 匿名化事件数据 |
| `clients_anonymized.csv` | 匿名化参与者数据 |
| `timeline.csv` | 时间线和关键节点 |
| `metrics.csv` | 自动指标 |
| `dispatch_rationale.csv` | 分派依据 |
| `evidence_quality_report.json` | 证据质量报告 |
| `expert_feedback_form.md` | 专家反馈签字表 |
| `observer_record_form.csv` | 观察员记录表 |
| `participant_questionnaire.csv` | 参与者问卷 |
| `manifest.json` | 文件清单与哈希校验 |

## 3. 证据质量摘要

文件：

`runtime_proof/round_01_evidence_quality_report.json`

当前归档版结果：

- 事件阶段：`ARCHIVED`
- 质量等级：`ready_for_low_cost_pre_experiment_summary`
- 质量分：`97`
- 关键节点：患者触发、角色分派、CPR 开始、AED 取到、AED 送达、救护接管、交接归档均已覆盖
- 注意：本轮使用规则/备用分派路径，适合演示闭环；PPT 中不要写成第三方 AI 或真实临床能力验证

## 4. 公网运行证明

目录：`runtime_proof/`

| 文件 | 说明 |
| --- | --- |
| `public_health_detail_20260526.json` | 归档前公网健康详情 |
| `public_health_detail_after_archive_20260526.json` | 归档后公网健康详情 |
| `current_incident_before_archive.json` | 归档前事件状态 |
| `current_incident_after_archive.json` | 归档后事件状态 |
| `round_01_timeline.csv` | 归档版时间线副本 |
| `round_01_manifest.json` | 归档版 manifest 副本 |

## 5. 尚未完成

- 5 分钟正式演示录屏还没有生成。
- 3-5 轮系统级模拟预实验还没有批量跑完。
- 参与者问卷和专家反馈需要团队人工填写或请专家审阅签字。

## 6. PPT 安全表述

推荐写法：

> 本轮系统级模拟预实验完成了从患者触发、AI/规则角色分派、多端任务同步、CPR/AED 流程推进、救护接管到证据包导出的闭环，证据质量报告显示关键节点完整覆盖。该结果用于证明工程闭环和数据记录能力，不推断临床疗效，不替代 120、专业医护或 AED 设备说明。
