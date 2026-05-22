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


def _phase_counts(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("manifestPhase") or row.get("phase") or "unknown" for row in rows)
    return "，".join(f"{phase}: {count}" for phase, count in sorted(counts.items()))


def generate_report(rows: list[dict[str, str]], *, source_name: str) -> str:
    if not rows:
        raise ValueError("round summary CSV has no data rows")

    valid_rows = [row for row in rows if row.get("verificationStatus", "OK") == "OK"]
    failed_rows = [row for row in rows if row.get("verificationStatus", "OK") != "OK"]
    analyzed_rows = valid_rows or rows
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
    args = parser.parse_args(argv)

    summary_path = Path(args.summary_csv)
    try:
        report = generate_report(_read_rows(summary_path), source_name=str(summary_path))
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
