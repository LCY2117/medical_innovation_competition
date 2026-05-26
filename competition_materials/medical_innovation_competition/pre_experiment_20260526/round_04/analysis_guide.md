# 生命反射弧预实验数据分析说明

事件编号：0a4df7a4-d506-420e-975f-f936735222c2
生成时间：2026-05-26T04:22:15.698000+00:00

## 一、先读哪些文件

建议按以下顺序整理材料：

1. `pre_experiment_round_summary.csv`：每轮系统预实验的核心指标汇总。
2. `baseline_vs_system_comparison.csv`：把无系统基线轮与系统轮配对，计算差值和百分比变化。
3. `participant_questionnaire.csv`：参与者主观评分，建议按题号计算均值、中位数和典型反馈。
4. `observer_record_form.csv`：观察员补充记录，用于解释系统日志无法覆盖的迟疑、误触和沟通问题。
5. `timeline.csv` 与 `metrics.csv`：复核关键时间点和系统自动指标。
6. `dispatch_rationale.csv`：挑选 1-2 个角色分派案例，说明 AI/规则如何结合能力、距离、AED 与健康风险。

## 二、多轮 ZIP 一键汇总

多轮系统级预实验结束后，把每轮下载的 ZIP 放到同一目录，在项目根目录运行：

```powershell
python scripts\build_pre_experiment_report.py "D:\path\to\evidence-zips" --output-dir "D:\path\to\analysis-output"
```

输出文件：

- `round-summary.csv`：合并每轮 `pre_experiment_round_summary.csv`，并附带包 SHA-256、校验状态、事件编号和生成时间。
- `round-analysis.md`：面向 PPT 的谨慎分析摘要，包含样本数、阶段分布、关键指标的均值/中位数/范围和不可夸大结论边界。
- `round-chart-data.csv`：面向 Excel/PPT 的图表数据，按时间指标、覆盖率和场景上下文输出均值、中位数、最小值和最大值。
- `round-review-actions.csv`：面向数据整理同学的复核行动清单，标出可采用、带备注采用、需重跑/人工补充或暂不使用的轮次。

如果需要定位异常证据包，可分步运行 `summarize_evidence_rounds.py` 和 `analyze_round_summary.py`。

## 三、T1-T6 指标解释

| 指标 | 当前系统轮记录 | 建议解释 |
| --- | --- | --- |
| T1 触发到分派完成 | 6s | 越短表示系统越快完成并行任务组织 |
| T2 触发到核心施救响应 | 27s | 用于观察核心施救者是否能及时接单或启动处置 |
| T3 触发到 CPR 开始 | 27s | 反映核心施救动作启动速度 |
| T4 触发到 AED 取到 | 55s | 反映 AED 保障者找到并取出 AED 的速度 |
| T5 触发到 AED 送达 | 94s | 反映 AED 取送链路总效率 |
| T6 触发到救护接管 | 146s | 反映环境清障、接应和交接流程 |

## 四、基线轮与系统轮对照

`baseline_vs_system_comparison.csv` 已填入系统轮事件编号和系统轮 T1/T2/T3/T4/T5/T6 数据。请把无系统基线轮观察到的时间和主观评分补入 baseline 列，再用 Excel 计算：

- `delta = system - baseline`
- `changePercent = (system - baseline) / baseline * 100`

解释时可以写“系统轮较基线轮在某指标上缩短/延长 X 秒”。样本量较小时，不建议写显著性结论。

## 五、主观评分整理

`participant_questionnaire.csv` 中 1-5 分题建议按题号计算：

- 平均分和中位数。
- 最高/最低题项。
- 典型开放反馈 2-3 条。

可以把评分归为三类：任务可理解性、协同减负、急救提示/安全边界。

## 六、可用于 PPT 的谨慎表述

推荐写法：

- “在模拟心脏骤停场景中，系统能够生成结构化时间线和可解释分派结果。”
- “预实验用于验证流程可行性、任务可理解性和专家接受度。”
- “初步记录提示系统有助于把 CPR、AED 取送、环境清障从串行口头协调转为并行任务协同。”

避免写法：

- “提高抢救成功率。”
- “改善患者预后。”
- “系统可替代 120、AED 语音提示或专业医护判断。”
- “模拟健康摘要等同真实健康监测数据。”
