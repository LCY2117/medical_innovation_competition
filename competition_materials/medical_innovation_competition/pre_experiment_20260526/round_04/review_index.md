# 生命反射弧证据包审阅索引

事件编号：0a4df7a4-d506-420e-975f-f936735222c2
导出时间：2026-05-26T04:22:15.698000+00:00
事件阶段：ARCHIVED
患者代号：P001
角色分派：PRIME=R004-PRIME；RUNNER=R002-RUNNER；GUIDE=R003-GUIDE

## 一、建议 3 分钟打开顺序

1. `expert_summary.md`：先看项目场景、分派结果、T1-T6 指标和安全边界。
2. `facilitator_run_sheet.md`：确认这轮预实验是否按预实验流程执行，特别是 T0-T6 记录点。
3. `timeline.csv` 与 `metrics.csv`：核对自动记录的事件时间线和核心耗时。
4. `dispatch_rationale.csv`：查看核心施救、AED 保障、环境清障的分派依据。
5. `expert_feedback_form.md`：填写专家评分、意见和签字。

## 二、材料用途速查

| 材料 | 建议读者 | 主要证明什么 | 公开边界 |
| --- | --- | --- | --- |
| `expert_summary.md` | 专家、指导教师、PPT 制作者 | 这轮预实验的医学场景、协同流程、指标和谨慎结论 | 可外部展示 |
| `expert_review_checklist.md` | 专家、指导教师 | 医学安全边界、AI 分派、数据记录是否可接受 | 可外部展示 |
| `expert_feedback_form.md` | 专家 | 事件级评分、改进意见和签字材料 | 可外部展示 |
| `expert_feedback_summary.csv` | 项目负责人、指导教师 | 汇总专家意见、风险点和整改闭环 | 可外部展示，需去除专家联系方式 |
| `facilitator_run_sheet.md` | 主持人、观察员 | 现场跑场流程、T0-T6 记录提示、预实验后整理步骤 | 可外部展示 |
| `analysis_guide.md` | 数据整理同学、PPT 制作者 | 如何解释 T1-T6、问卷、基线对照和不可夸大结论 | 可外部展示 |
| `data_dictionary.md` | 数据整理同学、专家、PPT 制作者 | 指标、CSV 字段、角色代码和数据边界说明 | 可外部展示 |
| `observer_record_form.csv` | 观察员 | 系统无法自动采集的现场行为、错误、理解度 | 可外部展示 |
| `participant_questionnaire.csv` | 参与者、数据整理同学 | 参与者主观评分和反馈 | 可外部展示，需匿名 |
| `baseline_vs_system_comparison.csv` | 数据整理同学 | 无系统基线轮与系统轮的描述性对照 | 可外部展示 |
| `pre_experiment_round_summary.csv` | 数据整理同学 | 多轮预实验合并统计的一行摘要 | 可外部展示 |
| `manifest.json` | 复核者 | 文件清单、SHA-256 校验和隐私边界 | 可外部展示 |

## 三、自动指标快照

| 指标 | 本轮记录 |
| --- | --- |
| T1 触发到分派完成 | 6s |
| T2 触发到核心施救响应 | 27s |
| T3 触发到 CPR 开始 | 27s |
| T4 触发到 AED 取到 | 55s |
| T5 触发到 AED 送达 | 94s |
| T6 触发到救护接管 | 146s |
| 角色完整度 | 1.0 |
| 定位覆盖率 | 100.0% |
| 健康摘要覆盖率 | 100.0% |

## 四、对外材料优先使用

- `review_index.md`
- `experiment_anonymized.json`
- `clients_anonymized.csv`
- `expert_summary.md`
- `expert_review_checklist.md`
- `expert_feedback_form.md`
- `facilitator_run_sheet.md`
- `analysis_guide.md`
- `data_dictionary.md`
- `participant_consent_safety_brief.md`
- `observer_record_form.csv`
- `participant_questionnaire.csv`
- `baseline_vs_system_comparison.csv`
- `pre_experiment_round_summary.csv`
- `expert_feedback_summary.csv`

## 五、内部复核材料

- `experiment.json` 与 `clients.csv` 保留原始 userId、终端画像和完整事件内容，只建议团队内部排查或复核使用。
- `aed_sites.csv` 可用于核对 AED 点位和访问备注；若点位来自真实场地，外部展示前应检查是否涉及不宜公开的位置细节。

## 六、必须避免的结论

- 不宣称提高抢救成功率或改善患者预后。
- 不宣称系统可替代 120、AED 语音提示或专业医护判断。
- 不把样例健康摘要或演示健康摘要描述成真实临床监测、诊断或疗效依据。
- 小样本预实验只写流程可行性、可用性、协同清晰度和专家接受度，不写统计显著性临床结论。
