from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Iterable
from urllib import error, request

from app.models.schemas import ClientInfo


ROLE_ORDER = ("PRIME", "RUNNER", "GUIDE")
SELECTION_RULES = {
    "PRIME": "专业急救人员优先，其次是受过系统急救训练者",
    "RUNNER": "身体素质好、跑得快、熟悉路线的人优先",
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
]
RESPONSE_FORMAT = {
    "PRIME": "userId or null",
    "RUNNER": "userId or null",
    "GUIDE": "userId or null",
}
SYSTEM_PROMPT = (
    "你是院前急救协同系统的调度大脑。"
    "请根据患者画像和候选协助者画像，在 PRIME、RUNNER、GUIDE 三类任务中各选择一个最合适的人。"
    "PRIME 优先专业急救能力和临场施救能力；"
    "RUNNER 优先体能、速度、行动半径和执行力；"
    "GUIDE 优先物业、安保、组织协调和现场通道能力。"
    "不要把高风险患者或明显身体受限的人分配到高强度任务。"
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

    def assign_roles(self, patient_user_id: str, clients: Iterable[ClientInfo]) -> tuple[dict[str, str | None], str]:
        all_clients = [client for client in clients if client.online]
        patient = next((client for client in all_clients if client.userId == patient_user_id), None)
        candidates = [client for client in all_clients if client.userId != patient_user_id]
        if not candidates:
            return {role: None for role in ROLE_ORDER}, "fallback"

        # Build ordered endpoints according to preference
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

        for name, url, key, model, timeout in endpoints:
            assignments = self._assign_with_llm(patient, candidates, url, key, model, timeout)
            if assignments is not None:
                return assignments, ("local_model" if name == "local" else "siliconflow")

        return self._fallback_assignments(candidates), "fallback"

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
            "candidateFields": list(CANDIDATE_FIELDS),
            "selectionRules": dict(SELECTION_RULES),
            "responseFormat": dict(RESPONSE_FORMAT),
            "systemPrompt": SYSTEM_PROMPT,
        }

        # probe local model liveness (fast probe)
        try:
            info["localModelAlive"] = bool(self.local_base_url and self._is_endpoint_alive(self.local_base_url, None, self.local_model, min(2, self.local_timeout_sec)))
        except Exception:
            info["localModelAlive"] = False

        return info

    def _assign_with_llm(
        self,
        patient: ClientInfo | None,
        candidates: list[ClientInfo],
        base_url: str,
        api_key: str | None,
        model: str,
        timeout_sec: int,
    ) -> dict[str, str | None] | None:
        payload = {
            "model": model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "patient": self._client_payload(patient) if patient else None,
                            "candidates": [self._client_payload(client) for client in candidates],
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
        # Try a simple /health GET first
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

        # Fallback: small POST to chat/completions
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
            req = request.Request(url=f"{base_url}/chat/completions", data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            with request.urlopen(req, timeout=timeout_sec) as response:
                body = json.loads(response.read().decode("utf-8"))
                return isinstance(body, dict)
        except Exception:
            return False

    def _fallback_assignments(self, clients: list[ClientInfo]) -> dict[str, str | None]:
        assignments: dict[str, str | None] = {role: None for role in ROLE_ORDER}
        remaining = list(clients)

        for role in ROLE_ORDER:
            scored = sorted(
                ((self._score_client(client, role), client) for client in remaining),
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

    def _score_client(self, client: ClientInfo, role: str) -> int:
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

        if any(marker in text for marker in high_risk_markers):
            score -= 12 if role in {"PRIME", "RUNNER"} else 3

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

    @staticmethod
    def _client_payload(client: ClientInfo | None) -> dict | None:
        if client is None:
            return None
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
        }
