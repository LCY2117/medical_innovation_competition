from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Iterable
from urllib import error, request

from app.models.schemas import AedSite, ClientInfo, DispatchRoleDecision, GeoPoint
from app.services.spatial import SpatialProvider


ROLE_ORDER = ("PRIME", "RUNNER", "GUIDE")
SELECTION_RULES = {
    "PRIME": "专业急救人员优先，其次距离患者近、受过系统急救训练者优先",
    "RUNNER": "距离 AED 近、身体素质好、熟悉路线的人优先",
    "GUIDE": "安保、物业、熟悉场地和交通组织的人优先",
}
CANDIDATE_FIELDS = [
    "userId",
    "displayName",
    "organization",
    "healthCondition",
    "professionIdentity",
    "profileBio",
    "deviceType",
    "online",
    "patientCandidate",
    "isPatient",
    "location",
    "healthSignals",
    "distanceToPatientMeters",
    "nearestAedDistanceMeters",
]
RESPONSE_FORMAT = {
    "PRIME": "userId or null",
    "RUNNER": "userId or null",
    "GUIDE": "userId or null",
}
SYSTEM_PROMPT = (
    "你是院前急救协同系统的调度大脑。"
    "请根据患者画像、候选协助者画像、候选者位置和 AED 点位，在 PRIME、RUNNER、GUIDE 三类任务中各选择一个最合适的人。"
    "PRIME 优先专业急救能力、临场施救能力、距离患者较近和健康摘要稳定；"
    "RUNNER 优先靠近 AED、体能速度、行动半径、执行力和健康摘要稳定；"
    "GUIDE 优先物业、安保、组织协调和现场通道能力。"
    "不要把高风险患者、低血氧、高心率、高压力或明显身体受限的人分配到高强度任务。"
    "只返回紧凑 JSON，格式必须是 "
    "{\"PRIME\":\"userId或null\",\"RUNNER\":\"userId或null\",\"GUIDE\":\"userId或null\"}。"
)


@dataclass
class DispatchPlanner:
    api_key: str | None
    model: str
    base_url: str
    timeout_sec: int
    local_base_url: str | None = None
    local_model: str = "default"
    local_timeout_sec: int = 30
    prefer_local: bool = True
    llm_budget_sec: float = 1.0
    spatial_provider: SpatialProvider | None = None

    def __post_init__(self) -> None:
        if self.spatial_provider is None:
            self.spatial_provider = SpatialProvider()

    def assign_roles(
        self,
        patient_user_id: str,
        clients: Iterable[ClientInfo],
        aed_sites: Iterable[AedSite] | None = None,
    ) -> tuple[dict[str, str | None], str, dict[str, DispatchRoleDecision]]:
        all_clients = [client for client in clients if client.online]
        patient = next((client for client in all_clients if client.userId == patient_user_id), None)
        candidates = [client for client in all_clients if client.userId != patient_user_id]
        sites = list(aed_sites or [])
        if not candidates:
            assignments = {role: None for role in ROLE_ORDER}
            return assignments, "fallback", self.explain_assignments(assignments, patient, candidates, sites)

        endpoints: list[tuple[str, str, str | None, str, int]] = []
        if self.prefer_local:
            if self.local_base_url:
                endpoints.append(("local", self.local_base_url, None, self.local_model, self.local_timeout_sec))
            if self.api_key:
                endpoints.append(("siliconflow", self.base_url, self.api_key, self.model, self.timeout_sec))
        else:
            if self.api_key:
                endpoints.append(("siliconflow", self.base_url, self.api_key, self.model, self.timeout_sec))
            if self.local_base_url:
                endpoints.append(("local", self.local_base_url, None, self.local_model, self.local_timeout_sec))

        deadline = time.monotonic() + max(0.0, self.llm_budget_sec)
        for name, url, key, model, timeout in endpoints:
            remaining_budget = deadline - time.monotonic()
            if remaining_budget <= 0:
                break
            endpoint_timeout = max(0.05, min(float(timeout), remaining_budget))
            assignments = self._assign_with_llm(patient, candidates, sites, url, key, model, endpoint_timeout)
            if assignments is not None:
                return (
                    assignments,
                    "local_model" if name == "local" else "siliconflow",
                    self.explain_assignments(assignments, patient, candidates, sites),
                )

        assignments = self._fallback_assignments(candidates, patient, sites, local_only=True)
        return assignments, "fallback", self.explain_assignments(assignments, patient, candidates, sites, local_only=True)

    def fallback_assign_roles(
        self,
        patient_user_id: str,
        clients: Iterable[ClientInfo],
        aed_sites: Iterable[AedSite] | None = None,
    ) -> tuple[dict[str, str | None], str, dict[str, DispatchRoleDecision]]:
        all_clients = [client for client in clients if client.online]
        patient = next((client for client in all_clients if client.userId == patient_user_id), None)
        candidates = [client for client in all_clients if client.userId != patient_user_id]
        sites = list(aed_sites or [])
        assignments = self._fallback_assignments(candidates, patient, sites, local_only=True)
        return assignments, "fallback", self.explain_assignments(assignments, patient, candidates, sites, local_only=True)

    def explain(self) -> dict:
        provider = "fallback"
        if self.prefer_local:
            if self.local_base_url:
                provider = "local_model"
            elif self.api_key:
                provider = "siliconflow"
        else:
            if self.api_key:
                provider = "siliconflow"
            elif self.local_base_url:
                provider = "local_model"

        info = {
            "configured": bool(self.local_base_url or self.api_key),
            "localModelConfigured": bool(self.local_base_url),
            "localModelUrl": self.local_base_url,
            "siliconFlowConfigured": bool(self.api_key),
            "provider": provider,
            "model": self.model,
            "baseUrl": self.base_url,
            "timeoutSec": self.timeout_sec,
            "llmBudgetSec": self.llm_budget_sec,
            "candidateFields": list(CANDIDATE_FIELDS),
            "selectionRules": dict(SELECTION_RULES),
            "responseFormat": dict(RESPONSE_FORMAT),
            "systemPrompt": SYSTEM_PROMPT,
            "mapProvider": self.spatial_provider.explain() if self.spatial_provider else {},
        }

        try:
            info["localModelAlive"] = bool(
                self.local_base_url
                and self._is_endpoint_alive(
                    self.local_base_url,
                    None,
                    self.local_model,
                    min(2, self.local_timeout_sec),
                )
            )
        except Exception:
            info["localModelAlive"] = False

        return info

    def _assign_with_llm(
        self,
        patient: ClientInfo | None,
        candidates: list[ClientInfo],
        aed_sites: list[AedSite],
        base_url: str,
        api_key: str | None,
        model: str,
        timeout_sec: float,
    ) -> dict[str, str | None] | None:
        payload = {
            "model": model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "patient": self._client_payload(patient) if patient else None,
                            "candidates": [
                                self._client_payload(
                                    client,
                                    patient_location=patient.location if patient else None,
                                    aed_sites=aed_sites,
                                )
                                for client in candidates
                            ],
                            "aedSites": [site.model_dump(mode="json") for site in aed_sites],
                            "selectionRules": SELECTION_RULES,
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }

        headers = {"Content-Type": "application/json"}
        if api_key:
            ak = api_key.strip()
            if ak and ak.upper() not in {"EMPTY", "ANY"}:
                headers["Authorization"] = f"Bearer {api_key}"

        req = request.Request(
            url=f"{base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=timeout_sec) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
            return None

        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        return self._extract_assignments(content, candidates)

    def _extract_assignments(
        self,
        content: str,
        clients: list[ClientInfo],
    ) -> dict[str, str | None] | None:
        if not content:
            return None

        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        raw_json = match.group(0) if match else content

        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError:
            return None

        valid_ids = {client.userId for client in clients}
        assignments: dict[str, str | None] = {}
        used: set[str] = set()
        for role in ROLE_ORDER:
            value = data.get(role)
            if isinstance(value, str) and value in valid_ids and value not in used:
                assignments[role] = value
                used.add(value)
            else:
                assignments[role] = None

        if any(assignments.values()):
            return assignments
        return None

    def _is_endpoint_alive(self, base_url: str, api_key: str | None, model: str, timeout_sec: int) -> bool:
        try:
            health_url = f"{base_url}/health"
            headers = {"Content-Type": "application/json"}
            if api_key:
                ak = api_key.strip()
                if ak and ak.upper() not in {"EMPTY", "ANY"}:
                    headers["Authorization"] = f"Bearer {api_key}"
            req = request.Request(url=health_url, headers=headers)
            with request.urlopen(req, timeout=timeout_sec) as resp:
                if getattr(resp, "status", 200) == 200:
                    return True
        except Exception:
            pass

        payload = {
            "model": model,
            "temperature": 0.0,
            "messages": [{"role": "system", "content": "ping"}],
        }
        headers = {"Content-Type": "application/json"}
        if api_key:
            ak = api_key.strip()
            if ak and ak.upper() not in {"EMPTY", "ANY"}:
                headers["Authorization"] = f"Bearer {api_key}"

        try:
            req = request.Request(
                url=f"{base_url}/chat/completions",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with request.urlopen(req, timeout=timeout_sec) as response:
                body = json.loads(response.read().decode("utf-8"))
                return isinstance(body, dict)
        except Exception:
            return False

    def _fallback_assignments(
        self,
        clients: list[ClientInfo],
        patient: ClientInfo | None,
        aed_sites: list[AedSite],
        local_only: bool = False,
    ) -> dict[str, str | None]:
        assignments: dict[str, str | None] = {role: None for role in ROLE_ORDER}
        remaining = list(clients)

        for role in ROLE_ORDER:
            scored = sorted(
                ((self._score_client(client, role, patient, aed_sites, local_only=local_only), client) for client in remaining),
                key=lambda item: item[0],
                reverse=True,
            )
            if not scored or scored[0][0] <= -100:
                continue
            picked = scored[0][1]
            assignments[role] = picked.userId
            remaining = [client for client in remaining if client.userId != picked.userId]

        for role in ROLE_ORDER:
            if assignments[role] is None and remaining:
                picked = remaining.pop(0)
                assignments[role] = picked.userId

        return assignments

    def explain_assignments(
        self,
        assignments: dict[str, str | None],
        patient: ClientInfo | None,
        candidates: list[ClientInfo],
        aed_sites: list[AedSite],
        local_only: bool = False,
    ) -> dict[str, DispatchRoleDecision]:
        candidate_map = {client.userId: client for client in candidates}
        rationale: dict[str, DispatchRoleDecision] = {}
        for role in ROLE_ORDER:
            user_id = assignments.get(role)
            client = candidate_map.get(user_id or "")
            if client is None:
                rationale[role] = DispatchRoleDecision(
                    userId=None,
                    score=0,
                    reasons=["当前没有合适在线终端可分配"],
                    warnings=["需要人工补位"],
                )
                continue

            reasons, warnings = self._decision_notes(client, role, patient, aed_sites, local_only=local_only)
            nearest = self._nearest_aed(client.location, aed_sites, local_only=local_only)
            rationale[role] = DispatchRoleDecision(
                userId=client.userId,
                score=self._score_client(client, role, patient, aed_sites, local_only=local_only),
                reasons=reasons,
                warnings=warnings,
                distanceToPatientMeters=self._distance_meters_for_mode(
                    client.location,
                    patient.location if patient else None,
                    local_only,
                ),
                nearestAedSiteId=nearest[0].siteId if nearest else None,
                distanceToAedMeters=nearest[1] if nearest else None,
                aedToPatientMeters=self._distance_meters_for_mode(
                    nearest[0].location if nearest else None,
                    patient.location if patient else None,
                    local_only,
                ),
            )
        return rationale

    def _score_client(
        self,
        client: ClientInfo,
        role: str,
        patient: ClientInfo | None = None,
        aed_sites: list[AedSite] | None = None,
        local_only: bool = False,
    ) -> int:
        profession = client.professionIdentity.lower()
        bio = client.profileBio.lower()
        organization = client.organization.lower()
        health = client.healthCondition.lower()
        name = client.displayName.lower()
        text = " ".join([health, profession, organization, bio, name])
        score = 0

        high_risk_markers = ("心脏", "冠心病", "骤停风险", "体能受限", "受限", "高风险")
        mobility_markers = ("体育", "跑得快", "体能", "行动能力", "奔跑", "运动", "快速")
        medical_identity_markers = ("医生", "医护", "专业急救", "急救人员")
        medical_skill_markers = ("急救", "cpr", "aed", "培训", "训练")
        guide_markers = ("安保", "物业", "保安", "协调", "交通", "电梯", "场地", "通道")
        route_markers = ("熟悉", "校园", "社区", "路线", "楼栋", "点位")
        trained_markers = ("培训", "系统培训", "常识", "救护")
        health_risk_score = self._health_risk_score(client)

        if any(marker in text for marker in high_risk_markers):
            score -= 12 if role in {"PRIME", "RUNNER"} else 3
        if health_risk_score:
            score -= health_risk_score if role in {"PRIME", "RUNNER"} else max(1, health_risk_score // 3)

        distance_to_patient = self._distance_meters_for_mode(
            client.location,
            patient.location if patient else None,
            local_only,
        )
        nearest_aed = self._nearest_aed(client.location, list(aed_sites or []), local_only=local_only)

        if distance_to_patient is not None:
            if distance_to_patient <= 80:
                score += 8 if role == "PRIME" else 2
            elif distance_to_patient <= 250:
                score += 4 if role in {"PRIME", "GUIDE"} else 2
            elif distance_to_patient > 800:
                score -= 6

        if role == "PRIME":
            if any(marker in profession for marker in medical_identity_markers):
                score += 20
            if any(marker in bio for marker in medical_skill_markers):
                score += 6
            if "培训" in text or "训练" in text:
                score += 6
            if "常识" in text:
                score += 2
        elif role == "RUNNER":
            if any(marker in text for marker in mobility_markers):
                score += 12
            if any(marker in text for marker in route_markers):
                score += 4
            if any(marker in text for marker in trained_markers):
                score += 2
            if nearest_aed is not None:
                aed_distance = nearest_aed[1]
                if aed_distance <= 120:
                    score += 10
                elif aed_distance <= 350:
                    score += 6
                elif aed_distance > 900:
                    score -= 4
        elif role == "GUIDE":
            if any(marker in text for marker in guide_markers):
                score += 14
            if any(marker in text for marker in route_markers):
                score += 5
            if "组织" in text or "协调" in text:
                score += 4

        if client.isPatient:
            return -1000

        return score

    def _decision_notes(
        self,
        client: ClientInfo,
        role: str,
        patient: ClientInfo | None,
        aed_sites: list[AedSite],
        local_only: bool = False,
    ) -> tuple[list[str], list[str]]:
        profession = client.professionIdentity.lower()
        bio = client.profileBio.lower()
        text = " ".join([client.healthCondition.lower(), profession, bio, client.organization.lower()])
        reasons: list[str] = []
        warnings: list[str] = []

        distance_to_patient = self._distance_meters_for_mode(
            client.location,
            patient.location if patient else None,
            local_only,
        )
        if distance_to_patient is not None:
            reasons.append(f"距离患者约 {round(distance_to_patient)} 米")
        else:
            warnings.append("缺少实时位置，使用画像和文本规则补偿")

        if role == "PRIME":
            if any(marker in profession for marker in ("医生", "医护", "专业急救", "急救人员")):
                reasons.append("具备医护或专业急救身份")
            if any(marker in bio for marker in ("急救", "cpr", "aed", "培训", "训练")):
                reasons.append("画像显示掌握 CPR/AED 急救技能")
        elif role == "RUNNER":
            nearest = self._nearest_aed(client.location, aed_sites, local_only=local_only)
            if nearest:
                reasons.append(f"距离最近 AED 点约 {round(nearest[1])} 米")
            if any(marker in text for marker in ("体育", "跑得快", "体能", "运动", "快速")):
                reasons.append("体能和移动能力适合 AED 取送")
        elif role == "GUIDE":
            if any(marker in text for marker in ("安保", "物业", "保安", "协调", "交通", "电梯", "场地", "通道")):
                reasons.append("适合现场通道协调和救护车接驳")
            if any(marker in text for marker in ("熟悉", "校园", "社区", "路线", "楼栋", "点位")):
                reasons.append("熟悉场地路线")

        if any(marker in text for marker in ("心脏", "冠心病", "骤停风险", "体能受限", "高风险")):
            warnings.append("健康画像提示风险，避免承担高强度任务")
        health_summary = self._health_summary_note(client)
        if health_summary:
            warnings.append(health_summary)
        if client.isPatient:
            warnings.append("当前为患者端，不应被分配救援任务")

        if not reasons:
            reasons.append("综合在线状态和基础画像完成兜底分配")
        return reasons, warnings

    def _distance_meters(self, a: GeoPoint | None, b: GeoPoint | None) -> float | None:
        return self.spatial_provider.distance_meters(a, b).meters if self.spatial_provider else None

    def _local_distance_meters(self, a: GeoPoint | None, b: GeoPoint | None) -> float | None:
        if self.spatial_provider is None:
            return None
        return self.spatial_provider.local_distance_meters(a, b)

    def _distance_meters_for_mode(self, a: GeoPoint | None, b: GeoPoint | None, local_only: bool) -> float | None:
        if local_only:
            return self._local_distance_meters(a, b)
        return self._distance_meters(a, b)

    def _nearest_aed(
        self,
        origin: GeoPoint | None,
        aed_sites: list[AedSite],
        local_only: bool = False,
    ) -> tuple[AedSite, float] | None:
        if origin is None:
            return None
        available_sites = [site for site in aed_sites if site.status.upper() == "AVAILABLE"]
        distances = [
            (site, distance)
            for site in available_sites
            if (distance := self._distance_meters_for_mode(origin, site.location, local_only)) is not None
        ]
        if not distances:
            return None
        return min(distances, key=lambda item: item[1])

    def _client_payload(
        self,
        client: ClientInfo | None,
        patient_location: GeoPoint | None = None,
        aed_sites: list[AedSite] | None = None,
    ) -> dict | None:
        if client is None:
            return None
        nearest = self._nearest_aed(client.location, list(aed_sites or []))
        return {
            "userId": client.userId,
            "displayName": client.displayName,
            "organization": client.organization,
            "healthCondition": client.healthCondition,
            "professionIdentity": client.professionIdentity,
            "profileBio": client.profileBio,
            "deviceType": client.deviceType,
            "online": client.online,
            "patientCandidate": client.patientCandidate,
            "isPatient": client.isPatient,
            "location": client.location.model_dump(mode="json") if client.location else None,
            "healthSignals": client.healthSignals.model_dump(mode="json") if client.healthSignals else None,
            "distanceToPatientMeters": self._distance_meters(client.location, patient_location),
            "nearestAedDistanceMeters": nearest[1] if nearest else None,
        }

    @staticmethod
    def _health_risk_score(client: ClientInfo) -> int:
        summary = client.healthSignals
        if summary is None:
            return 0
        score = 0
        tags = {tag.lower() for tag in summary.riskTags}
        if tags.intersection({"tachycardia", "bradycardia", "low_spo2", "high_pressure", "limited_mobility"}):
            score += 8
        if summary.heartRateBpm is not None and (summary.heartRateBpm >= 120 or summary.heartRateBpm <= 45):
            score += 6
        if summary.bloodOxygenPercent is not None and summary.bloodOxygenPercent < 94:
            score += 8
        if summary.pressureScore is not None and summary.pressureScore >= 75:
            score += 5
        if (summary.activityLevel or "").lower() == "low":
            score += 2
        return score

    @staticmethod
    def _health_summary_note(client: ClientInfo) -> str | None:
        summary = client.healthSignals
        if summary is None:
            return None
        warnings: list[str] = []
        if summary.heartRateBpm is not None and (summary.heartRateBpm >= 120 or summary.heartRateBpm <= 45):
            warnings.append(f"心率 {summary.heartRateBpm} bpm")
        if summary.bloodOxygenPercent is not None and summary.bloodOxygenPercent < 94:
            warnings.append(f"血氧 {summary.bloodOxygenPercent}%")
        if summary.pressureScore is not None and summary.pressureScore >= 75:
            warnings.append(f"压力 {summary.pressureScore}")
        if summary.riskTags:
            warnings.append(f"健康标记 {'、'.join(summary.riskTags)}")
        if not warnings:
            return None
        return f"健康摘要提示风险（{summary.source}）：{'；'.join(warnings)}，不宜承担高强度任务"
