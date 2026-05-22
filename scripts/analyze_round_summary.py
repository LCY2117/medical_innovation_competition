from __future__ import annotations

import argparse
import csv
import statistics
import sys
from collections import Counter
from pathlib import Path


TIME_FIELDS = [
    ("dispatchSeconds", "T1 触发到分派完成"),
    ("cprStartSeconds", "T3 触发到 CPR 开始"),
    ("aedPickupSeconds", "T4 触发到 AED 取到"),
    ("aedDeliverySeconds", "T5 触发到 AED 送达"),
    ("ambulanceArriveSeconds", "T6 触发到救护接管"),
]

COVERAGE_FIELDS = [
    ("roleAssignmentCompleteness", "角色分派完整度", 100.0),
    ("locationCoveragePercent", "定位覆盖率", 1.0),
    ("healthCoveragePercent", "健康摘要覆盖率", 1.0),
]

CONTEXT_FIELDS = [
    ("participantCount", "参与终端数"),
    ("aedSiteCount", "AED 点位数"),
    ("availableAedSiteCount", "可用 AED 点位数"),
    ("runnerRouteMeters", "AED 保障路线距离"),
]

QUALITY_FIELDS = [
    ("qualityScore", "质量分"),
]

QUALITY_COUNT_FIELDS = [
    ("qualityCriticalCount", "Critical 问题数"),
    ("qualityWarningCount", "Warning 问题数"),
    ("qualityInfoCount", "Info 提醒数"),
    ("missingKeyEventCount", "缺失关键节点数"),
]

CHART_FIELDS = [
    ("time", "seconds", "时间指标", field, label, 1.0)
    for field, label in TIME_FIELDS
] + [
    ("coverage", "percent", "覆盖率与完整度", field, label, scale)
    for field, label, scale in COVERAGE_FIELDS
] + [
    ("quality", "score", "证据质量", "qualityScore", "质量分", 1.0),
    ("quality", "count", "证据质量", "qualityCriticalCount", "Critical 问题数", 1.0),
    ("quality", "count", "证据质量", "qualityWarningCount", "Warning 问题数", 1.0),
    ("quality", "count", "证据质量", "missingKeyEventCount", "缺失关键节点数", 1.0),
] + [
    ("context", "count", "场景上下文", "participantCount", "参与终端数", 1.0),
    ("context", "count", "场景上下文", "aedSiteCount", "AED 点位数", 1.0),
    ("context", "count", "场景上下文", "availableAedSiteCount", "可用 AED 点位数", 1.0),
    ("context", "meters", "场景上下文", "runnerRouteMeters", "AED 保障路线距离", 1.0),
]

CHART_FIELDNAMES = [
    "metricGroup",
    "metricKey",
    "metricLabel",
    "unit",
    "validRoundCount",
    "mean",
    "median",
    "min",
    "max",
    "chartHint",
    "pptSafeUse",
]

REVIEW_ACTION_FIELDNAMES = [
    "roundId",
    "incidentId",
    "verificationStatus",
    "qualityLevel",
    "qualityScore",
    "reviewDecision",
    "reviewReason",
    "criticalCount",
    "warningCount",
    "missingKeyEventCount",
    "missingKeyEvents",
    "warningCodes",
    "recommendedAction",
    "pptUseBoundary",
]


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _number(value: str | None) -> float | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _values(rows: list[dict[str, str]], field: str) -> list[float]:
    return [value for row in rows if (value := _number(row.get(field))) is not None]


def _scaled_values(rows: list[dict[str, str]], field: str, scale: float) -> list[float]:
    return [value * scale for value in _values(rows, field)]


def _fmt(value: float | None) -> str:
    if value is None:
        return "-"
    if abs(value - round(value)) < 0.005:
        return str(int(round(value)))
    return f"{value:.2f}"


def _stats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None}
    return {
        "count": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
    }


def _analyzed_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    valid_rows = [row for row in rows if row.get("verificationStatus", "OK") == "OK"]
    return valid_rows or rows


def _metric_table(rows: list[dict[str, str]], fields: list[tuple[str, str]], unit: str) -> list[str]:
    lines = [f"| 指标 | 有效轮次 | 均值{unit} | 中位数{unit} | 最小{unit} | 最大{unit} |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for field, label in fields:
        stat = _stats(_values(rows, field))
        lines.append(
            f"| {label} `{field}` | {stat['count']} | {_fmt(stat['mean'])} | {_fmt(stat['median'])} | {_fmt(stat['min'])} | {_fmt(stat['max'])} |"
        )
    return lines


def _scaled_metric_table(rows: list[dict[str, str]], fields: list[tuple[str, str, float]], unit: str) -> list[str]:
    lines = [f"| 指标 | 有效轮次 | 均值{unit} | 中位数{unit} | 最小{unit} | 最大{unit} |", "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for field, label, scale in fields:
        stat = _stats(_scaled_values(rows, field, scale))
        lines.append(
            f"| {label} `{field}` | {stat['count']} | {_fmt(stat['mean'])} | {_fmt(stat['median'])} | {_fmt(stat['min'])} | {_fmt(stat['max'])} |"
        )
    return lines


def generate_chart_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        raise ValueError("round summary CSV has no data rows")

    analyzed_rows = _analyzed_rows(rows)
    chart_rows: list[dict[str, str]] = []
    for metric_group, unit, chart_hint, field, label, scale in CHART_FIELDS:
        stat = _stats(_scaled_values(analyzed_rows, field, scale))
        chart_rows.append(
            {
                "metricGroup": metric_group,
                "metricKey": field,
                "metricLabel": label,
                "unit": unit,
                "validRoundCount": str(stat["count"]),
                "mean": _fmt(stat["mean"]),
                "median": _fmt(stat["median"]),
                "min": _fmt(stat["min"]),
                "max": _fmt(stat["max"]),
                "chartHint": chart_hint,
                "pptSafeUse": "descriptive_pre_experiment_only",
            }
        )
    return chart_rows


def write_chart_csv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CHART_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _round_id(row: dict[str, str]) -> str:
    return row.get("roundId") or row.get("manifestIncidentId") or row.get("incidentId") or "-"


def _count_text(row: dict[str, str], field: str) -> str:
    value = _number(row.get(field))
    if value is None:
        return row.get(field) or ""
    return str(int(value))


def _review_decision(row: dict[str, str]) -> tuple[str, str, str, str]:
    verification_status = row.get("verificationStatus", "OK") or "OK"
    quality_level = row.get("qualityLevel", "")
    critical_count = _number(row.get("qualityCriticalCount")) or 0
    warning_count = _number(row.get("qualityWarningCount")) or 0
    missing_count = _number(row.get("missingKeyEventCount")) or 0

    if verification_status != "OK":
        return (
            "exclude_from_summary",
            "证据包校验未通过，不能进入多轮描述性统计。",
            "重新导出或修复证据包后再运行分析脚本。",
            "do_not_use",
        )
    if not quality_level:
        return (
            "manual_review_required",
            "该轮来自旧版证据包或缺少 evidence_quality_report.json。",
            "优先用新版系统重跑；如必须保留，需观察员人工说明关键节点完整性。",
            "do_not_use_until_reviewed",
        )
    if (
        quality_level == "ready_for_low_cost_pre_experiment_summary"
        and critical_count == 0
        and warning_count == 0
        and missing_count == 0
    ):
        return (
            "use_for_summary",
            "关键节点和质量检查已满足低成本预实验汇总要求。",
            "可进入多轮描述性统计和 PPT 图表底表。",
            "descriptive_pre_experiment_only",
        )
    if critical_count > 0 or missing_count > 0 or quality_level == "needs_rerun_or_manual_review":
        return (
            "rerun_or_manual_supplement",
            "存在 critical 问题、缺失关键节点，或质量等级要求重跑/人工复核。",
            "优先重跑该轮；如现场无法重跑，需在观察员记录和 PPT 备注中补充说明。",
            "do_not_use_until_resolved",
        )
    if warning_count > 0 or quality_level == "usable_with_notes":
        return (
            "use_with_notes",
            "该轮可作为流程可行性材料，但存在 warning，需要备注。",
            "可进入描述性汇总，但 PPT/专家材料必须保留限制说明。",
            "descriptive_with_notes_only",
        )
    return (
        "manual_review_required",
        "质量等级或提示代码未落入预设规则。",
        "由数据整理同学复核 timeline、dispatch_rationale 和观察员记录后决定。",
        "do_not_use_until_reviewed",
    )


def generate_review_action_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    if not rows:
        raise ValueError("round summary CSV has no data rows")

    action_rows: list[dict[str, str]] = []
    for row in rows:
        decision, reason, action, boundary = _review_decision(row)
        action_rows.append(
            {
                "roundId": _round_id(row),
                "incidentId": row.get("manifestIncidentId") or row.get("incidentId") or "",
                "verificationStatus": row.get("verificationStatus", "OK") or "OK",
                "qualityLevel": row.get("qualityLevel") or "missing_quality_report",
                "qualityScore": row.get("qualityScore") or "",
                "reviewDecision": decision,
                "reviewReason": reason,
                "criticalCount": _count_text(row, "qualityCriticalCount"),
                "warningCount": _count_text(row, "qualityWarningCount"),
                "missingKeyEventCount": _count_text(row, "missingKeyEventCount"),
                "missingKeyEvents": row.get("missingKeyEvents") or "",
                "warningCodes": row.get("qualityWarningCodes") or "",
                "recommendedAction": action,
                "pptUseBoundary": boundary,
            }
        )
    return action_rows


def write_review_action_csv(rows: list[dict[str, str]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REVIEW_ACTION_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def _phase_counts(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("manifestPhase") or row.get("phase") or "unknown" for row in rows)
    return "，".join(f"{phase}: {count}" for phase, count in sorted(counts.items()))


def _quality_level_counts(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("qualityLevel") or "missing_quality_report" for row in rows)
    return "，".join(f"{level}: {count}" for level, count in sorted(counts.items()))


def _sum_field(rows: list[dict[str, str]], field: str) -> int:
    return int(sum(_values(rows, field)))


def _quality_review_rows(rows: list[dict[str, str]]) -> list[str]:
    review_rows = [
        row
        for row in rows
        if not row.get("qualityLevel")
        or (
            row.get("qualityLevel") != "ready_for_low_cost_pre_experiment_summary"
            or _number(row.get("qualityCriticalCount")) not in (None, 0)
            or _number(row.get("qualityWarningCount")) not in (None, 0)
            or _number(row.get("missingKeyEventCount")) not in (None, 0)
        )
    ]
    if not review_rows:
        return ["- 暂未发现需要重跑或人工补充说明的轮次。"]

    lines = [
        "| 轮次/事件 | 质量等级 | 质量分 | Critical | Warning | 缺失节点 | 主要提示代码 |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in review_rows:
        round_id = row.get("roundId") or row.get("manifestIncidentId") or row.get("incidentId") or "-"
        warning_codes = row.get("qualityWarningCodes") or "-"
        lines.append(
            "| "
            + " | ".join(
                [
                    round_id,
                    row.get("qualityLevel") or "missing_quality_report",
                    row.get("qualityScore") or "-",
                    row.get("qualityCriticalCount") or "-",
                    row.get("qualityWarningCount") or "-",
                    row.get("missingKeyEventCount") or "-",
                    warning_codes,
                ]
            )
            + " |"
        )
    return lines


def generate_report(rows: list[dict[str, str]], *, source_name: str) -> str:
    if not rows:
        raise ValueError("round summary CSV has no data rows")

    valid_rows = [row for row in rows if row.get("verificationStatus", "OK") == "OK"]
    failed_rows = [row for row in rows if row.get("verificationStatus", "OK") != "OK"]
    analyzed_rows = _analyzed_rows(rows)
    incident_ids = sorted({row.get("manifestIncidentId") or row.get("incidentId") or "" for row in analyzed_rows if row.get("manifestIncidentId") or row.get("incidentId")})

    lines = [
        "# 生命反射弧预实验多轮分析摘要",
        "",
        "## 数据来源",
        "",
        f"- 汇总表：`{source_name}`",
        f"- 样本轮次：{len(analyzed_rows)}",
        f"- 校验通过轮次：{len(valid_rows)}",
        f"- 校验异常轮次：{len(failed_rows)}",
        f"- 事件编号数：{len(incident_ids)}",
        f"- 事件编号：{', '.join(incident_ids) if incident_ids else '-'}",
        f"- 事件阶段分布：{_phase_counts(analyzed_rows)}",
        "",
        "## 证据质量",
        "",
        f"- 质量等级分布：{_quality_level_counts(analyzed_rows)}",
        f"- Critical 问题数：{_sum_field(analyzed_rows, 'qualityCriticalCount')}",
        f"- Warning 问题数：{_sum_field(analyzed_rows, 'qualityWarningCount')}",
        f"- Info 提醒数：{_sum_field(analyzed_rows, 'qualityInfoCount')}",
        f"- 缺失关键节点数：{_sum_field(analyzed_rows, 'missingKeyEventCount')}",
        "",
        *_metric_table(analyzed_rows, QUALITY_FIELDS, ""),
        "",
        "### 需复核轮次",
        "",
        *_quality_review_rows(analyzed_rows),
        "",
        "## 关键时间指标",
        "",
        *_metric_table(analyzed_rows, TIME_FIELDS, "秒"),
        "",
        "## 覆盖率与完整度",
        "",
        *_scaled_metric_table(analyzed_rows, COVERAGE_FIELDS, "%"),
        "",
        "## 场景上下文",
        "",
        *_metric_table(analyzed_rows, CONTEXT_FIELDS, ""),
        "",
        "## 可写入 PPT 的谨慎表述",
        "",
        "- 本轮汇总仅基于模拟演练和系统日志，适合说明流程闭环、数据可追踪性和可解释分派能力。",
        "- 可以表述为：初步结果提示系统能够稳定生成多角色任务、结构化时间线和事件证据包，便于校园/社区急救演练复盘。",
        "- 可以表述为：多轮演练数据为后续专家复核、交互优化和定位/AED 策略改进提供了量化线索。",
        "- 不应表述为：提高真实抢救成功率、改善患者预后、替代 120 或替代专业医护判断。",
        "",
        "## 下一步建议",
        "",
        "- 继续补齐无系统基线轮数据，并与系统轮做描述性对照。",
        "- 将观察员记录、参与者问卷和专家反馈汇总到同一轮次编号下。",
        "- 对异常或耗时偏长的轮次回看 `timeline.csv` 和 `dispatch_rationale.csv`，定位流程卡点。",
    ]
    if failed_rows:
        lines.extend(
            [
                "",
                "## 校验异常包",
                "",
                "| 包路径 | 问题 |",
                "| --- | --- |",
            ]
        )
        for row in failed_rows:
            lines.append(f"| `{row.get('packagePath', '')}` | {row.get('verificationProblems', '')} |")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a PPT-safe Markdown analysis report from LifeReflexArc round-summary CSV.",
    )
    parser.add_argument("summary_csv", help="CSV produced by scripts/summarize_evidence_rounds.py")
    parser.add_argument("-o", "--output", help="Output Markdown path. Defaults to stdout.")
    parser.add_argument("--chart-output", help="Optional PPT/Excel-friendly chart data CSV path.")
    parser.add_argument("--review-output", help="Optional round review/action checklist CSV path.")
    args = parser.parse_args(argv)

    summary_path = Path(args.summary_csv)
    try:
        rows = _read_rows(summary_path)
        report = generate_report(rows, source_name=str(summary_path))
        chart_rows = generate_chart_rows(rows) if args.chart_output else []
        review_rows = generate_review_action_rows(rows) if args.review_output else []
    except (OSError, csv.Error, ValueError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
        print(f"OK: wrote pre-experiment analysis report -> {output}")
    else:
        sys.stdout.write(report)
    if args.chart_output:
        chart_output = Path(args.chart_output)
        write_chart_csv(chart_rows, chart_output)
        print(f"OK: wrote chart data CSV -> {chart_output}")
    if args.review_output:
        review_output = Path(args.review_output)
        write_review_action_csv(review_rows, review_output)
        print(f"OK: wrote review action CSV -> {review_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
