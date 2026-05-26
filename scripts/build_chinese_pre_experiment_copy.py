from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "competition_materials" / "medical_innovation_competition"

ROUND_DIR_NAMES = {
    "round_01": "第一轮 校园标准交接流程",
    "round_02": "第二轮 AED取送较快流程",
    "round_03": "第三轮 救护车较早接近现场流程",
    "round_04": "第四轮 现场协同稍慢流程",
    "round_05": "第五轮 含AED分析与除颤确认流程",
}

ROUND_ZIP_NAMES = {
    "round_01_evidence.zip": "第一轮证据包.zip",
    "round_02_evidence.zip": "第二轮证据包.zip",
    "round_03_evidence.zip": "第三轮证据包.zip",
    "round_04_evidence.zip": "第四轮证据包.zip",
    "round_05_evidence.zip": "第五轮证据包.zip",
}

FILE_NAMES = {
    "README.md": "单轮说明.md",
    "review_index.md": "审阅索引.md",
    "expert_summary.md": "专家摘要.md",
    "expert_review_checklist.md": "专家审阅清单.md",
    "expert_feedback_form.md": "专家反馈表.md",
    "facilitator_run_sheet.md": "主持人跑场单.md",
    "analysis_guide.md": "分析说明.md",
    "evidence_quality_report.json": "证据质量报告.json",
    "pre_experiment_round_summary.csv": "单轮汇总表.csv",
    "timeline.csv": "时间线.csv",
    "metrics.csv": "指标表.csv",
    "dispatch_rationale.csv": "分派依据.csv",
    "observer_record_form.csv": "观察员记录表.csv",
    "participant_questionnaire.csv": "参与者问卷.csv",
    "baseline_vs_system_comparison.csv": "基线对照表.csv",
    "expert_feedback_summary.csv": "专家反馈汇总.csv",
    "manifest.json": "证据包清单.json",
    "aed_sites.csv": "AED点位表.csv",
    "clients.csv": "终端列表.csv",
    "clients_anonymized.csv": "匿名终端列表.csv",
    "data_dictionary.md": "数据字典.md",
    "experiment.json": "事件完整数据.json",
    "experiment_anonymized.json": "事件匿名数据.json",
    "participant_consent_safety_brief.md": "参与者知情与安全说明.md",
}

ANALYSIS_NAMES = {
    "round-summary.csv": "多轮汇总表.csv",
    "round-analysis.md": "多轮分析报告.md",
    "round-chart-data.csv": "图表数据底表.csv",
    "round-review-actions.csv": "复核动作表.csv",
}

TOP_LEVEL_NAMES = {
    "README.md": "目录说明.md",
    "pre-experiment-method.md": "预实验方法说明.md",
    "round-index.csv": "轮次索引.csv",
}

TEXT_REPLACEMENTS = {
    "competition_materials\\medical_innovation_competition\\pre_experiment_20260526": "医创赛预实验数据",
    "pre_experiment_20260526": "医创赛预实验数据",
    "evidence_zips": "证据包",
    "analysis_output": "多轮分析",
    "round_01_evidence.zip": "第一轮证据包.zip",
    "round_02_evidence.zip": "第二轮证据包.zip",
    "round_03_evidence.zip": "第三轮证据包.zip",
    "round_04_evidence.zip": "第四轮证据包.zip",
    "round_05_evidence.zip": "第五轮证据包.zip",
    "round_01": "第一轮",
    "round_02": "第二轮",
    "round_03": "第三轮",
    "round_04": "第四轮",
    "round_05": "第五轮",
    "round-summary.csv": "多轮汇总表.csv",
    "round-analysis.md": "多轮分析报告.md",
    "round-chart-data.csv": "图表数据底表.csv",
    "round-review-actions.csv": "复核动作表.csv",
    "round-index.csv": "轮次索引.csv",
    "pre-experiment-method.md": "预实验方法说明.md",
    "README.md": "说明.md",
    "review_index.md": "审阅索引.md",
    "expert_summary.md": "专家摘要.md",
    "expert_review_checklist.md": "专家审阅清单.md",
    "expert_feedback_form.md": "专家反馈表.md",
    "facilitator_run_sheet.md": "主持人跑场单.md",
    "analysis_guide.md": "分析说明.md",
    "evidence_quality_report.json": "证据质量报告.json",
    "pre_experiment_round_summary.csv": "单轮汇总表.csv",
    "timeline.csv": "时间线.csv",
    "metrics.csv": "指标表.csv",
    "dispatch_rationale.csv": "分派依据.csv",
    "observer_record_form.csv": "观察员记录表.csv",
    "participant_questionnaire.csv": "参与者问卷.csv",
    "baseline_vs_system_comparison.csv": "基线对照表.csv",
    "expert_feedback_summary.csv": "专家反馈汇总.csv",
    "manifest.json": "证据包清单.json",
    "aed_sites.csv": "AED点位表.csv",
    "clients.csv": "终端列表.csv",
    "clients_anonymized.csv": "匿名终端列表.csv",
    "data_dictionary.md": "数据字典.md",
    "experiment.json": "事件完整数据.json",
    "experiment_anonymized.json": "事件匿名数据.json",
    "participant_consent_safety_brief.md": "参与者知情与安全说明.md",
    "ARCHIVED": "已归档",
    "fallback": "规则备用分派",
    "OK": "通过",
    "Critical": "严重",
    "Warning": "警告",
    "Info": "提示",
    "ready_for_low_cost_pre_experiment_summary": "可用于低成本预实验汇总",
    "descriptive_pre_experiment_only": "仅用于描述性预实验",
    "dispatch_fallback_used": "使用规则备用分派",
    "packagePath": "证据包路径",
    "packageSha256": "证据包SHA256",
    "verificationStatus": "校验状态",
    "verificationProblems": "校验问题",
    "manifestIncidentId": "清单事件编号",
    "manifestGeneratedAtIso": "清单生成时间",
    "manifestPhase": "清单事件阶段",
    "qualityLevel": "质量等级",
    "qualityIssueCount": "质量提示总数",
    "missingKeyEvents": "缺失关键节点",
    "qualityWarningCodes": "质量提示代码",
    "roundId": "轮次编号",
    "incidentId": "事件编号",
    "generatedAtIso": "生成时间",
    "phase": "事件阶段",
    "patientCode": "患者代号",
    "primeCode": "核心施救者代号",
    "runnerCode": "AED取送者代号",
    "guideCode": "救护接驳者代号",
    "dispatchSource": "分派来源",
    "observerName": "观察员",
    "scenarioLocation": "场景地点",
    "roleAssignmentClarityScore": "角色分派清晰度评分",
    "taskInstructionClarityScore": "任务指令清晰度评分",
    "stressOperabilityScore": "压力场景可操作性评分",
    "dispatchReasonablenessScore": "分派合理性评分",
    "aedPromptUsefulnessScore": "AED提示有用性评分",
    "notes": "备注",
    "metricGroup": "指标分组",
    "metricKey": "指标键",
    "metricLabel": "指标名称",
    "unit": "单位",
    "validRoundCount": "有效轮次数",
    "mean": "均值",
    "median": "中位数",
    "min": "最小值",
    "max": "最大值",
    "chartHint": "图表建议",
    "pptSafeUse": "PPT使用边界",
    "reviewDecision": "复核结论",
    "reviewReason": "复核原因",
    "criticalCount": "严重问题数",
    "warningCount": "警告问题数",
    "recommendedAction": "建议动作",
    "pptUseBoundary": "PPT使用边界",
    "dispatchSeconds": "触发到分派完成秒数",
    "firstResponderResponseSeconds": "触发到核心施救响应秒数",
    "cprStartSeconds": "触发到CPR开始秒数",
    "aedPickupSeconds": "触发到AED取到秒数",
    "aedDeliverySeconds": "触发到AED送达秒数",
    "ambulanceArriveSeconds": "触发到救护接管秒数",
    "roleAssignmentCompleteness": "角色分派完整度",
    "locationCoveragePercent": "定位覆盖率",
    "healthCoveragePercent": "健康摘要覆盖率",
    "qualityScore": "质量分",
    "qualityCriticalCount": "严重问题数",
    "qualityWarningCount": "警告问题数",
    "qualityInfoCount": "提示项数",
    "missingKeyEventCount": "缺失关键节点数",
    "participantCount": "参与终端数",
    "aedSiteCount": "AED点位数",
    "availableAedSiteCount": "可用AED点位数",
    "runnerRouteMeters": "AED保障路线距离米",
    "LifeReflexArc pre-experiment evidence package": "生命反射弧预实验证据包",
    "all package files except 证据包清单.json": "除证据包清单.json以外的全部文件",
    "schemaVersion": "结构版本",
    "packageType": "证据包类型",
    "privacyGuidance": "隐私使用说明",
    "publicOrExpertReview": "公开或专家审阅材料",
    "internalReviewOnly": "仅内部复核材料",
    "files": "文件列表",
    "fileName": "文件名",
    "bytes": "字节数",
    "sha256": "SHA256哈希",
    "lineCount": "行数",
    "fileCountExcludingManifest": "清单外文件数量",
    "verification": "完整性校验",
    "algorithm": "算法",
    "covers": "覆盖范围",
    "generatedAt": "生成时间戳",
    "timeline": "时间线",
    "clients": "终端列表",
    "aedSites": "AED点位",
    "assignments": "角色分派",
    "metrics": "指标",
    "dispatchRationale": "分派依据",
    "patientUserId": "患者用户ID",
    "userId": "用户ID",
    "displayName": "显示名称",
    "organization": "组织",
    "healthCondition": "健康情况",
    "professionIdentity": "职业身份",
    "profileBio": "个人说明",
    "deviceType": "设备类型",
    "online": "在线",
    "lastSeenTs": "最后在线时间",
    "assignedRole": "分派角色",
    "patientCandidate": "患者候选",
    "isPatient": "是否患者",
    "location": "位置",
    "healthSignals": "健康摘要",
    "latitude": "纬度",
    "longitude": "经度",
    "accuracyMeters": "精度米",
    "label": "位置标签",
    "floor": "楼层",
    "source": "来源",
    "updatedTs": "更新时间",
    "authorizationStatus": "授权状态",
    "provider": "提供方",
    "heartRateBpm": "心率",
    "bloodOxygenPercent": "血氧",
    "pressureScore": "压力评分",
    "activityLevel": "活动水平",
    "sleepQuality": "睡眠质量",
    "riskTags": "风险标签",
    "note": "备注",
    "siteId": "点位ID",
    "name": "名称",
    "status": "状态",
    "accessNotes": "取用说明",
    "lastCheckedTs": "最后检查时间",
    "role": "角色",
    "score": "评分",
    "reasons": "理由",
    "warnings": "提示",
    "distanceToPatientMeters": "到患者距离米",
    "nearestAedSiteId": "最近AED点位ID",
    "distanceToAedMeters": "到AED距离米",
    "aedToPatientMeters": "AED到患者距离米",
    "tsIso": "时间",
    "ts": "时间戳",
    "elapsedSec": "相对秒数",
    "eventType": "事件类型",
    "participantCode": "参与者代号",
    "msg": "日志内容",
    "INCIDENT_CREATED": "事件创建",
    "AED_SITE_UPDATED": "AED点位更新",
    "DEMO_BOOTSTRAPPED": "演示场景初始化完成",
    "PATIENT_DESIGNATED": "患者指定",
    "PATIENT_SOS": "患者SOS",
    "DISPATCH_STARTED": "分派开始",
    "ROLE_ASSIGNED": "角色已分派",
    "ROLE_JOINED": "角色已接单",
    "ROLE_AUTO_JOINED": "角色自动接单",
    "CPR_STARTED": "CPR开始",
    "AED_PICKED": "AED已取到",
    "AED_DELIVERED": "AED已送达",
    "AED_ANALYSIS_STARTED": "AED分析开始",
    "AED_SHOCK_DELIVERED": "AED除颤确认",
    "AMBULANCE_ARRIVED": "救护车到场",
    "HANDOVER_COMPLETED": "交接归档完成",
    "Incident created": "事件创建",
    "AED site updated": "AED点位更新",
    "Demo scenario bootstrapped": "演示场景初始化完成",
    "Patient designated by dashboard": "总控指定患者",
    "AI dispatching started": "AI分派开始",
    "assigned": "已分派",
    "CPR started by": "CPR开始，记录人",
    "AED picked by": "AED已取到，记录人",
    "AED delivered by": "AED已送达，记录人",
    "AED analysis started by": "AED分析开始，记录人",
    "AED shock delivered by": "AED除颤确认，记录人",
    "Ambulance arrived (reported by": "救护车到场（记录人",
    "Handover completed by": "完成交接归档，记录人",
    "PRIME": "核心施救",
    "RUNNER": "AED取送",
    "GUIDE": "救护接驳",
    "PATIENT": "患者",
    "AVAILABLE": "可用",
    "ANDROID": "安卓端",
    "true": "是",
    "false": "否",
    "null": "空",
    "mock": "样例",
    "sample": "样例",
    "normal": "正常",
    "high": "高",
    "low": "低",
    "good": "良好",
    "poor": "较差",
    "fair": "一般",
    "tachycardia": "心率偏快",
    "low_spo2": "血氧偏低",
    "high_pressure": "压力偏高",
}

INDEX_HEADERS = {
    "externalRoundId": "轮次目录",
    "roundCode": "轮次编号",
    "scenarioName": "场景标识",
    "scenarioLabel": "场景名称",
    "evidenceZip": "证据包文件",
    "incidentId": "事件编号",
    "phase": "事件阶段",
    "dispatchSource": "分派来源",
    "dispatchSeconds": "触发到分派完成秒数",
    "firstResponderResponseSeconds": "触发到核心施救响应秒数",
    "cprStartSeconds": "触发到CPR开始秒数",
    "aedPickupSeconds": "触发到AED取到秒数",
    "aedDeliverySeconds": "触发到AED送达秒数",
    "ambulanceArriveSeconds": "触发到救护接管秒数",
    "runnerRouteMeters": "AED保障路线距离米",
    "qualityLevel": "质量等级",
    "qualityScore": "质量分",
    "qualityIssueCount": "质量提示总数",
    "qualityCriticalCount": "严重问题数",
    "qualityWarningCount": "警告问题数",
    "qualityInfoCount": "提示项数",
}

VALUE_REPLACEMENTS = {
    "round_01": "第一轮",
    "round_02": "第二轮",
    "round_03": "第三轮",
    "round_04": "第四轮",
    "round_05": "第五轮",
    "campus_standard_handover": "校园标准交接流程",
    "fast_aed_route": "AED取送较快流程",
    "ambulance_early_arrival": "救护车较早接近现场流程",
    "coordination_delay": "现场协同稍慢流程",
    "aed_analysis_complete": "含AED分析与除颤确认流程",
    "round_01_evidence.zip": "第一轮证据包.zip",
    "round_02_evidence.zip": "第二轮证据包.zip",
    "round_03_evidence.zip": "第三轮证据包.zip",
    "round_04_evidence.zip": "第四轮证据包.zip",
    "round_05_evidence.zip": "第五轮证据包.zip",
    "ARCHIVED": "已归档",
    "fallback": "规则备用分派",
    "ready_for_low_cost_pre_experiment_summary": "可用于低成本预实验汇总",
}


def _copy_text_with_replacements(source: Path, target: Path) -> None:
    text = source.read_text(encoding="utf-8-sig")
    text = _translate_text(text)
    target.write_text(text, encoding="utf-8")


def _translate_text(text: str) -> str:
    for old, new in sorted(TEXT_REPLACEMENTS.items(), key=lambda item: len(item[0]), reverse=True):
        text = text.replace(old, new)
    return text


def _translated_zip_member_name(name: str) -> str:
    parts = name.replace("\\", "/").split("/")
    translated_parts = [FILE_NAMES.get(part, TEXT_REPLACEMENTS.get(part, part)) for part in parts]
    return "/".join(translated_parts)


def _zip_text(raw: bytes) -> str | None:
    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return None


def _line_count(raw: bytes) -> int:
    text = _zip_text(raw)
    if text is None:
        return 0
    return text.count("\n") + (1 if text else 0)


def _refresh_chinese_manifest(files: dict[str, bytes]) -> None:
    manifest_name = "证据包清单.json"
    if manifest_name not in files:
        return
    text = _zip_text(files[manifest_name])
    if text is None:
        return
    try:
        manifest = json.loads(text)
    except json.JSONDecodeError:
        return

    entries = []
    for name, raw in sorted(files.items()):
        if name == manifest_name:
            continue
        entries.append(
            {
                "文件名": name,
                "字节数": len(raw),
                "SHA256哈希": hashlib.sha256(raw).hexdigest(),
                "行数": _line_count(raw),
            }
        )
    manifest["文件列表"] = entries
    manifest["清单外文件数量"] = len(entries)
    manifest["完整性校验"] = {"算法": "SHA-256", "覆盖范围": "除证据包清单.json 以外的全部文件"}
    files[manifest_name] = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")


def _write_chinese_zip(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    translated_files: dict[str, bytes] = {}
    with zipfile.ZipFile(source, "r") as source_zip:
        for info in source_zip.infolist():
            if info.is_dir():
                continue
            raw = source_zip.read(info.filename)
            translated_name = _translated_zip_member_name(info.filename)
            suffix = Path(info.filename).suffix.lower()
            text = _zip_text(raw)
            if text is not None and suffix in {".md", ".txt", ".csv", ".json"}:
                raw = _translate_text(text).encode("utf-8")
            translated_files[translated_name] = raw

    _refresh_chinese_manifest(translated_files)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as target_zip:
        for name, raw in sorted(translated_files.items()):
            target_zip.writestr(name, raw, compress_type=zipfile.ZIP_DEFLATED)


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() in {".md", ".txt", ".csv", ".json"}:
        _copy_text_with_replacements(source, target)
    else:
        shutil.copy2(source, target)


def _write_chinese_index(source: Path, target: Path) -> None:
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        original_headers = handle.readline
    if not rows:
        return
    headers = list(INDEX_HEADERS)
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[INDEX_HEADERS[key] for key in headers])
        writer.writeheader()
        for row in rows:
            translated = {}
            for key in headers:
                value = row.get(key, "")
                translated[INDEX_HEADERS[key]] = VALUE_REPLACEMENTS.get(value, value)
            writer.writerow(translated)


def _write_top_readme(target: Path) -> None:
    text = """# 生命反射弧五轮预实验数据

这个目录是给指导老师、队友和答辩材料整理使用的中文阅读版。目录名、文件夹名和主要材料文件名均已改为中文。

## 推荐阅读顺序

1. 打开 `多轮分析/多轮分析报告.md`，先看五轮总体结论。
2. 打开 `轮次索引.csv`，快速查看每轮场景、事件编号、关键耗时和证据质量。
3. 打开 `图表数据底表.csv`，交给 PPT 同学做图。
4. 需要逐轮复核时，进入 `第一轮 校园标准交接流程` 到 `第五轮 含AED分析与除颤确认流程`。
5. `证据包` 文件夹中保存每轮原始 ZIP，可作为可校验的系统证据包留档。

## 使用边界

本批材料来自电脑端系统级预实验流程，不是真实患者数据，也不是临床试验数据。可用于说明平台具备流程闭环、日志追踪、角色分派、AED取送协同和证据导出能力；不可用于声称真实抢救成功率提升或替代120/专业医护判断。
"""
    target.write_text(text, encoding="utf-8")


def build_copy(source: Path, target: Path, *, force: bool) -> None:
    source = source.resolve()
    target = target.resolve()
    if not source.is_dir():
        raise FileNotFoundError(source)
    if target.exists():
        if not force:
            raise FileExistsError(f"{target} already exists; pass --force to replace it")
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)

    evidence_target = target / "证据包"
    evidence_target.mkdir()
    for old_name, new_name in ROUND_ZIP_NAMES.items():
        _write_chinese_zip(source / "evidence_zips" / old_name, evidence_target / new_name)

    analysis_target = target / "多轮分析"
    analysis_target.mkdir()
    for old_name, new_name in ANALYSIS_NAMES.items():
        _copy_file(source / "analysis_output" / old_name, analysis_target / new_name)

    for old_dir, new_dir in ROUND_DIR_NAMES.items():
        round_source = source / old_dir
        round_target = target / new_dir
        round_target.mkdir()
        for old_name, new_name in FILE_NAMES.items():
            candidate = round_source / old_name
            if candidate.is_file():
                _copy_file(candidate, round_target / new_name)

    for old_name, new_name in TOP_LEVEL_NAMES.items():
        source_file = source / old_name
        if not source_file.is_file():
            continue
        if old_name == "round-index.csv":
            _write_chinese_index(source_file, target / new_name)
        else:
            _copy_file(source_file, target / new_name)

    _write_top_readme(target / "先看这里.md")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a Chinese-named reader copy of pre-experiment evidence.")
    parser.add_argument(
        "--source",
        type=Path,
        default=BASE / "pre_experiment_20260526",
        help="Source pre-experiment directory.",
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=BASE / "医创赛预实验数据",
        help="Chinese-named target directory.",
    )
    parser.add_argument("--force", action="store_true", help="Replace target directory if it already exists.")
    args = parser.parse_args()
    build_copy(args.source, args.target, force=args.force)
    print(f"OK: Chinese reader copy written to {args.target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
