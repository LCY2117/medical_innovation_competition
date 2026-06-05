from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import shutil
import sys
import tempfile
import time
import zipfile
from datetime import datetime
from io import StringIO
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SERVER_ROOT = ROOT / "server(web)"
if str(SERVER_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVER_ROOT))

from app.core.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402
from summarize_evidence_rounds import summarize_packages, write_csv  # noqa: E402
from analyze_round_summary import (  # noqa: E402
    generate_chart_rows,
    generate_report,
    generate_review_action_rows,
    write_chart_csv,
    write_review_action_csv,
)
from verify_evidence_package import verify_package  # noqa: E402


SCENARIOS = [
    {
        "name": "campus_standard_handover",
        "label": "校园标准交接流程",
        "dispatch": 5,
        "cpr": 18,
        "aed_pickup": 42,
        "aed_delivery": 78,
        "aed_analysis": 86,
        "ambulance": 126,
        "handover": 148,
        "shock": None,
    },
    {
        "name": "fast_aed_route",
        "label": "AED 取送链路较快流程",
        "dispatch": 4,
        "cpr": 13,
        "aed_pickup": 31,
        "aed_delivery": 63,
        "aed_analysis": 70,
        "ambulance": 116,
        "handover": 139,
        "shock": None,
    },
    {
        "name": "ambulance_early_arrival",
        "label": "救护车较早接近现场流程",
        "dispatch": 5,
        "cpr": 16,
        "aed_pickup": 37,
        "aed_delivery": 98,
        "aed_analysis": 106,
        "ambulance": 83,
        "handover": 128,
        "shock": None,
    },
    {
        "name": "coordination_delay",
        "label": "现场协同稍慢流程",
        "dispatch": 6,
        "cpr": 27,
        "aed_pickup": 55,
        "aed_delivery": 94,
        "aed_analysis": 103,
        "ambulance": 146,
        "handover": 178,
        "shock": None,
    },
    {
        "name": "aed_analysis_complete",
        "label": "含 AED 分析与除颤确认流程",
        "dispatch": 5,
        "cpr": 20,
        "aed_pickup": 40,
        "aed_delivery": 82,
        "aed_analysis": 91,
        "shock": 102,
        "ambulance": 131,
        "handover": 156,
    },
]

KEY_FILES = [
    "README.md",
    "review_index.md",
    "expert_summary.md",
    "expert_review_checklist.md",
    "expert_feedback_form.md",
    "facilitator_run_sheet.md",
    "analysis_guide.md",
    "evidence_quality_report.json",
    "pre_experiment_round_summary.csv",
    "timeline.csv",
    "metrics.csv",
    "dispatch_rationale.csv",
    "observer_record_form.csv",
    "participant_questionnaire.csv",
    "baseline_vs_system_comparison.csv",
    "expert_feedback_summary.csv",
    "manifest.json",
]


def _settings(db_path: Path) -> Settings:
    return Settings(
        app_name="Life Reflex Arc Pre Experiment",
        api_prefix="/api",
        host="127.0.0.1",
        port=8080,
        reload=False,
        sos_duration_sec=5,
        dispatch_delay_sec=0,
        cors_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        db_path=db_path,
        web_dist_dir=db_path.parent / "web-dist",
        local_model_base_url=None,
        prefer_local_model=False,
        dispatch_llm_budget_sec=0.05,
        beta_admin_token=None,
        map_provider="beta",
        audit_log_enabled=True,
        rate_limit_enabled=False,
    )


def _post_ok(client: TestClient, url: str, payload: dict | None = None) -> dict:
    response = client.post(url, json=payload) if payload is not None else client.post(url)
    if response.status_code >= 300:
        raise RuntimeError(f"{url} failed: {response.status_code} {response.text}")
    return response.json()


def _run_round(client: TestClient, scenario: dict) -> str:
    bootstrapped = _post_ok(client, "/api/beta/bootstrap")
    incident_id = bootstrapped["incidentId"]
    _post_ok(client, "/api/incidents/current/designate_patient", {"patientUserId": "beta-patient"})

    action_plan = [
        ("CPR_STARTED", "beta-prime"),
        ("AED_PICKED", "beta-runner"),
    ]
    if scenario["ambulance"] < scenario["aed_delivery"]:
        action_plan.append(("AMBULANCE_ARRIVED", "beta-guide"))
    action_plan.extend(
        [
            ("AED_DELIVERED", "beta-runner"),
            ("AED_ANALYSIS_STARTED", "beta-prime"),
        ]
    )
    if scenario.get("shock") is not None:
        action_plan.append(("AED_SHOCK_DELIVERED", "beta-prime"))
    if scenario["ambulance"] >= scenario["aed_delivery"]:
        action_plan.append(("AMBULANCE_ARRIVED", "beta-guide"))
    action_plan.append(("HANDOVER_COMPLETED", "beta-guide"))

    for action, user_id in action_plan:
        _post_ok(
            client,
            f"/api/incidents/{incident_id}/actions",
            {"action": action, "userId": user_id},
        )

    service = client.app.state.incident_service
    state = service.incidents[incident_id]
    base = int(time.time() * 1000) - int((scenario["handover"] + 20) * 1000)
    state.sos = state.sos.model_copy(update={"startTs": base})

    assigned_offsets = {
        "PRIME assigned": scenario["dispatch"] * 1000 - 220,
        "RUNNER assigned": scenario["dispatch"] * 1000 - 110,
        "GUIDE assigned": scenario["dispatch"] * 1000,
    }
    action_offsets = {
        "CPR started": scenario["cpr"] * 1000,
        "AED picked": scenario["aed_pickup"] * 1000,
        "AED delivered": scenario["aed_delivery"] * 1000,
        "AED analysis started": scenario["aed_analysis"] * 1000,
        "Ambulance arrived": scenario["ambulance"] * 1000,
        "Handover completed": scenario["handover"] * 1000,
    }
    if scenario.get("shock") is not None:
        action_offsets["AED shock delivered"] = scenario["shock"] * 1000

    aed_update_count = 0
    for entry in state.logs:
        message = entry.msg
        if message == "Incident created":
            entry.ts = base - 4000
        elif message.startswith("AED site updated"):
            entry.ts = base - 3500 + aed_update_count * 120
            aed_update_count += 1
        elif message == "beta scenario bootstrapped":
            entry.ts = base - 3000
        elif message.startswith("Patient designated"):
            entry.ts = base
        elif message == "AI dispatching started":
            entry.ts = base + 250
        else:
            for marker, offset in assigned_offsets.items():
                if message.startswith(marker):
                    entry.ts = base + offset
                    break
            else:
                for marker, offset in action_offsets.items():
                    if marker in message:
                        entry.ts = base + offset
                        break

    state.logs.sort(key=lambda item: (item.ts, item.msg))
    service._persist()
    return incident_id


def _update_manifest(manifest: dict, files: dict[str, bytes]) -> bytes:
    entries = []
    for name in sorted(name for name in files if name != "manifest.json"):
        raw = files[name]
        try:
            text = raw.decode("utf-8")
            line_count = text.count("\n") + (1 if text else 0)
        except UnicodeDecodeError:
            line_count = 0
        entries.append(
            {
                "fileName": name,
                "bytes": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "lineCount": line_count,
            }
        )
    manifest["files"] = entries
    manifest["fileCountExcludingManifest"] = len(entries)
    return json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")


def _relabel_round(package_content: bytes, round_code: str) -> bytes:
    with zipfile.ZipFile(io.BytesIO(package_content)) as source:
        files = {name: source.read(name) for name in source.namelist()}
    manifest = json.loads(files["manifest.json"].decode("utf-8"))

    for name, raw in list(files.items()):
        if name == "manifest.json":
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        files[name] = text.replace("R001", round_code).encode("utf-8")

    files["manifest.json"] = _update_manifest(manifest, files)
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.writestr(name, files[name], compress_type=zipfile.ZIP_DEFLATED)
    return target.getvalue()


def _extract_key_files(zip_path: Path, round_dir: Path) -> None:
    round_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        for name in KEY_FILES:
            if name in archive.namelist():
                (round_dir / name).write_bytes(archive.read(name))


def _read_round_summary(zip_path: Path) -> dict[str, str]:
    with zipfile.ZipFile(zip_path) as archive:
        raw = archive.read("pre_experiment_round_summary.csv").decode("utf-8-sig")
    rows = list(csv.DictReader(StringIO(raw)))
    return dict(rows[0]) if rows else {}


def _quality_counts(quality: dict) -> dict[str, str]:
    counts = {"critical": 0, "warning": 0, "info": 0}
    warnings = quality.get("warnings", [])
    if not isinstance(warnings, list):
        warnings = []
    for item in warnings:
        if not isinstance(item, dict):
            continue
        severity = str(item.get("severity", "")).lower()
        if severity in counts:
            counts[severity] += 1
    return {
        "qualityIssueCount": str(sum(counts.values())),
        "qualityCriticalCount": str(counts["critical"]),
        "qualityWarningCount": str(counts["warning"]),
        "qualityInfoCount": str(counts["info"]),
    }


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _build_analysis(zip_paths: list[Path], output_dir: Path) -> None:
    fieldnames, rows = summarize_packages(zip_paths, include_invalid=False)
    summary_path = output_dir / "round-summary.csv"
    report_path = output_dir / "round-analysis.md"
    chart_path = output_dir / "round-chart-data.csv"
    review_path = output_dir / "round-review-actions.csv"
    write_csv(fieldnames, rows, summary_path)
    report_path.write_text(generate_report(rows, source_name=str(summary_path)), encoding="utf-8")
    write_chart_csv(generate_chart_rows(rows), chart_path)
    write_review_action_csv(generate_review_action_rows(rows), review_path)


def _write_readme(output_dir: Path, rows: list[dict[str, str]]) -> None:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        "# LifeReflexArc Pre-Experiment Evidence",
        "",
        f"生成时间：{generated_at}",
        "",
        "本目录用于医创赛国赛准备，文件夹和文件名均采用英文命名；文件正文、表格字段说明和分析结论保留中文，方便指导老师和答辩团队阅读。",
        "",
        "## 使用边界",
        "",
        "- 这些材料来自电脑端系统级预实验流程，不是临床试验，也不是患者真实救治数据。",
        "- 可用于说明：协同流程闭环、任务分派可解释性、时间线可追踪、证据包可导出。",
        "- 不可用于声称：提高真实抢救成功率、改善患者预后、替代 120 或替代专业医护判断。",
        "",
        "## Directory Map",
        "",
        "- `evidence_zips/`：每轮导出的原始证据包 ZIP，可用校验脚本复查。",
        "- `round_01/` 至 `round_05/`：每轮抽取出的关键材料，便于人工快速查看。",
        "- `analysis_output/`：多轮汇总表、PPT 图表底表、复核动作表和 Markdown 分析报告。",
        "- `round-index.csv`：轮次索引表，把每个英文文件名、事件编号和核心指标对应起来。",
        "- `pre-experiment-method.md`：电脑端预实验方法说明，可给 PPT 或答辩稿引用。",
        "",
        "## Round Index",
        "",
        "| Round | Scenario | Incident | Phase | Dispatch | CPR | AED Delivery | Ambulance | Quality |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                [
                    row["externalRoundId"],
                    row["scenarioLabel"],
                    row["incidentId"],
                    row["phase"],
                    row["dispatchSeconds"],
                    row["cprStartSeconds"],
                    row["aedDeliverySeconds"],
                    row["ambulanceArriveSeconds"],
                    f"{row['qualityScore']} ({row['qualityLevel']})",
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Quick Review",
            "",
            "优先打开：",
            "",
            "1. `analysis_output/round-analysis.md`：多轮摘要和 PPT 安全表述。",
            "2. `analysis_output/round-chart-data.csv`：做柱状图或折线图的数据底表。",
            "3. `round_01/review_index.md`：单轮证据包如何给专家/老师审阅。",
            "4. `round-index.csv`：总览 5 轮核心指标。",
        ]
    )
    (output_dir / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_method(output_dir: Path) -> None:
    text = """# LifeReflexArc Computer-Run Pre-Experiment Method

## 目的

在没有足够真人参与和真实场地排练时间的情况下，先用系统自身的桌面端流程跑通 5 轮院前急救协同闭环，形成可复查的事件日志、角色分派、AED 取送、救护接管和交接归档证据材料。

## 流程

1. 初始化标准校园急救场景：患者端、核心施救端、AED 取送端、救护接驳端和 2 个 AED 点位。
2. 由患者触发或总控指定患者，系统生成 PRIME、RUNNER、GUIDE 三类任务。
3. 按不同场景节奏记录 CPR 开始、AED 取到、AED 送达、AED 分析、救护到场、完成交接归档。
4. 每轮导出 ZIP 证据包，并用 SHA-256 manifest 校验文件完整性。
5. 汇总 5 轮数据，输出描述性统计、图表底表和复核动作表。

## 数据性质

本批数据是系统级预实验和演示流程数据，不涉及真实患者、真实医疗处置或临床疗效判断。它适合证明系统具备流程闭环、日志可追踪、证据材料可导出和专家复核入口，不应被表述为临床有效性证据。

## PPT 建议表述

可写：初步系统级预实验显示，平台能够稳定完成多角色任务分派、AED 取送协同、救护接管记录和交接归档，并自动导出结构化复盘材料。

不要写：系统已经验证能提升真实抢救成功率，或可以替代 120/专业医护判断。
"""
    (output_dir / "pre-experiment-method.md").write_text(text, encoding="utf-8")


def _assert_ascii_names(output_dir: Path) -> None:
    bad = [
        path.relative_to(output_dir)
        for path in output_dir.rglob("*")
        if any(ord(char) > 127 for char in path.name)
    ]
    if bad:
        formatted = "\n".join(str(item) for item in bad[:20])
        raise RuntimeError(f"Non-ASCII file or folder names found:\n{formatted}")


def generate(output_dir: Path, rounds: int, force: bool) -> None:
    if rounds < 3 or rounds > 5:
        raise ValueError("rounds must be between 3 and 5")
    if output_dir.exists():
        if not force:
            raise FileExistsError(f"{output_dir} already exists; pass --force to replace it")
        shutil.rmtree(output_dir)

    evidence_dir = output_dir / "evidence_zips"
    analysis_dir = output_dir / "analysis_output"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    zip_paths: list[Path] = []
    index_rows: list[dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="lifereflex_pre_experiment_") as tmp:
        settings = _settings(Path(tmp) / "data" / "pre_experiment.db")
        with TestClient(create_app(settings)) as client:
            for idx, scenario in enumerate(SCENARIOS[:rounds], start=1):
                incident_id = _run_round(client, scenario)
                package_response = client.get(f"/api/experiments/{incident_id}/package")
                if package_response.status_code != 200:
                    raise RuntimeError(
                        f"package export failed for {incident_id}: "
                        f"{package_response.status_code} {package_response.text}"
                    )

                round_code = f"R{idx:03d}"
                package_content = _relabel_round(package_response.content, round_code)
                zip_path = evidence_dir / f"round_{idx:02d}_evidence.zip"
                zip_path.write_bytes(package_content)
                problems = verify_package(str(zip_path))
                if problems:
                    raise RuntimeError(f"{zip_path} verification failed: {'; '.join(problems)}")

                round_dir = output_dir / f"round_{idx:02d}"
                _extract_key_files(zip_path, round_dir)
                zip_paths.append(zip_path)

                summary = _read_round_summary(zip_path)
                quality = json.loads((round_dir / "evidence_quality_report.json").read_text(encoding="utf-8"))
                quality_counts = _quality_counts(quality)
                index_rows.append(
                    {
                        "externalRoundId": f"round_{idx:02d}",
                        "roundCode": round_code,
                        "scenarioName": scenario["name"],
                        "scenarioLabel": scenario["label"],
                        "evidenceZip": zip_path.name,
                        "incidentId": summary.get("incidentId", incident_id),
                        "phase": summary.get("phase", ""),
                        "dispatchSource": summary.get("dispatchSource", ""),
                        "dispatchSeconds": summary.get("dispatchSeconds", ""),
                        "firstResponderResponseSeconds": summary.get("firstResponderResponseSeconds", ""),
                        "cprStartSeconds": summary.get("cprStartSeconds", ""),
                        "aedPickupSeconds": summary.get("aedPickupSeconds", ""),
                        "aedDeliverySeconds": summary.get("aedDeliverySeconds", ""),
                        "ambulanceArriveSeconds": summary.get("ambulanceArriveSeconds", ""),
                        "runnerRouteMeters": summary.get("runnerRouteMeters", ""),
                        "qualityLevel": str(quality.get("qualityLevel", "")),
                        "qualityScore": str(quality.get("qualityScore", "")),
                        **quality_counts,
                    }
                )

    _build_analysis(zip_paths, analysis_dir)
    _write_csv(
        output_dir / "round-index.csv",
        [
            "externalRoundId",
            "roundCode",
            "scenarioName",
            "scenarioLabel",
            "evidenceZip",
            "incidentId",
            "phase",
            "dispatchSource",
            "dispatchSeconds",
            "firstResponderResponseSeconds",
            "cprStartSeconds",
            "aedPickupSeconds",
            "aedDeliverySeconds",
            "ambulanceArriveSeconds",
            "runnerRouteMeters",
            "qualityLevel",
            "qualityScore",
            "qualityIssueCount",
            "qualityCriticalCount",
            "qualityWarningCount",
            "qualityInfoCount",
        ],
        index_rows,
    )
    _write_method(output_dir)
    _write_readme(output_dir, index_rows)
    _assert_ascii_names(output_dir)


def main(argv: list[str] | None = None) -> int:
    default_dir = (
        ROOT
        / "competition_materials"
        / "medical_innovation_competition"
        / f"pre_experiment_{datetime.now().strftime('%Y%m%d')}"
    )
    parser = argparse.ArgumentParser(description="Generate LifeReflexArc computer-run pre-experiment evidence rounds.")
    parser.add_argument("--rounds", type=int, default=5, help="Number of rounds to generate, 3 to 5.")
    parser.add_argument("--output-dir", type=Path, default=default_dir, help="English-named output directory.")
    parser.add_argument("--force", action="store_true", help="Replace output directory if it already exists.")
    args = parser.parse_args(argv)

    generate(args.output_dir, args.rounds, args.force)
    print(f"OK: generated {args.rounds} pre-experiment round(s)")
    print(f"- Output: {args.output_dir}")
    print(f"- Evidence ZIPs: {args.output_dir / 'evidence_zips'}")
    print(f"- Analysis: {args.output_dir / 'analysis_output'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
