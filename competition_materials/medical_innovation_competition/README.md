# 医创赛国赛材料入口

更新时间：2026-05-25

本文件夹集中存放本轮针对第十二届全国大学生医学创新大赛“交叉学科 / AI 创新设计”准备的材料。当前主线已经收窄为：

**Web 总控台 + `/mobile` 子路由四端协同 + 系统级模拟预实验 + 证据包导出。**

Android 原型保留为长期扩展和备用端，不作为本轮国赛主展示依赖。

## 文件说明

| 文件或文件夹 | 用途 |
| --- | --- |
| `NATIONAL_COMPETITION_EXECUTION_CHECKLIST.md` | 国赛执行清单：评分项、证据链、分工、时间安排、风险口径 |
| `PPT_ABSTRACT_EXPERIMENT_RECORD_TEMPLATES.md` | PPT 10 页主线、摘要模板、预实验记录模板和答辩问答 |
| `system_simulation_experiment/` | 系统级模拟预实验方案、记录表、PPT 安全表述 |
| `aed_marking/` | 云南大学 AED 人工标记模板和导入说明 |

## 推荐使用顺序

1. 先读 `NATIONAL_COMPETITION_EXECUTION_CHECKLIST.md`，统一团队方向。
2. 做 PPT 时直接按 `PPT_ABSTRACT_EXPERIMENT_RECORD_TEMPLATES.md` 的 10 页结构写。
3. 没时间真人实验时，按 `system_simulation_experiment/` 跑电脑模拟预实验。
4. 如果要补 AED 点位，填写 `aed_marking/YNU_AED_MARKING_TEMPLATE.csv`。
5. 当前已砍掉 SDK 申请线，不把 OPPO 健康 SDK、Android 地图 SDK 或短信推送作为本轮任务。
