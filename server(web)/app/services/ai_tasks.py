from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from app.models.schemas import ClientInfo
from app.services.spatial import SpatialProvider

SKILL_FETCH = "fetch"
SKILL_SAVE = "save"
SKILL_GUIDE = "guide"
SKILL_COORDINATE = "coordinate"
SKILLS = (SKILL_FETCH, SKILL_SAVE, SKILL_GUIDE, SKILL_COORDINATE)

SKILL_LABELS = {
    SKILL_FETCH: "物资取送",
    SKILL_SAVE: "现场施救",
    SKILL_GUIDE: "通道疏导",
    SKILL_COORDINATE: "协调对接",
}

SYSTEM_PROMPT = (
    "你是院前急救协同系统的任务解析器。"
    "把现场的临时求助需求解析为结构化任务，只做语义拆解，不参与人选分配。"
    "requester 是发起求助的现场终端（如正在施救的医生），不是患者，description 中不要把它描述为患者。"
    "title 是 ≤16 字的动作型标题（如「取送止血绷带」）；"
    "description 用一句话说明做什么、给谁用；"
    "requiredSkill 取值：取送物资=fetch，现场施救=save，通道疏导=guide，协调对接=coordinate；"
    "priority 取 1-5（涉及出血、窒息等紧急情况给高值）；"
    "locationLabel 在需求未指明地点时返回 null；"
    "requires 是完成任务所需的物资或技能清单（数组）。"
    "一条求助可能包含多个并列需求（例如同时要止血绷带和速效救心丸），必须拆分为多个独立任务；"
    "只有单一需求时也返回只含一个任务的数组。"
    '只返回紧凑 JSON，不要 markdown 围栏，格式为 '
    '{"tasks":[{"task":{"title":"…","description":"…","requiredSkill":"fetch|save|guide|coordinate",'
    '"priority":3,"locationLabel":null},"requires":["…"]}]}'
)

# 资质分规则：requiredSkill -> (关键词, 加分)
_CAPABILITY_RULES: dict[str, list[tuple[tuple[str, ...], int]]] = {
    SKILL_FETCH: [
        (("体能", "体育", "跑得快", "奔跑", "运动", "快速", "行动能力"), 12),
        (("熟悉", "路线", "楼栋", "单元", "点位", "社区"), 8),
        (("急救常识", "急救", "培训", "常识"), 4),
    ],
    SKILL_SAVE: [
        (("医生", "医护", "专业急救", "急救人员", "护士"), 20),
        (("cpr", "aed", "急救", "培训", "训练"), 12),
    ],
    SKILL_GUIDE: [
        (("安保", "物业", "保安", "场地", "通道"), 14),
        (("协调", "组织", "熟悉", "路线"), 6),
    ],
    SKILL_COORDINATE: [
        (("组织", "协调", "对接"), 10),
        (("熟悉", "小区", "物业", "路线"), 6),
    ],
}

_HIGH_RISK_MARKERS = ("心脏", "冠心病", "骤停风险", "体能受限", "受限", "高风险", "高血压", "糖尿病")


@dataclass
class TaskSpec:
    title: str
    description: str
    required_skill: str = SKILL_FETCH
    priority: int = 3
    location_label: str | None = None
    requires: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.requires is None:
            self.requires = []
        if self.required_skill not in SKILLS:
            self.required_skill = SKILL_FETCH
        self.priority = max(1, min(5, int(self.priority or 3)))
        self.title = (self.title or "临时任务").strip()[:16]
        self.description = (self.description or "").strip()


@dataclass
class MatchResult:
    score: float
    capability: int
    distance: float | None
    reasons: list[str]


class AiTaskPlanner:
    """AI 临时任务：DeepSeek 只负责自然语言 → 结构化任务；匹配度走硬算法。"""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "deepseek-v4-flash",
        base_url: str = "https://api.deepseek.com",
        timeout_sec: int = 15,
        spatial_provider: SpatialProvider | None = None,
    ) -> None:
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout_sec = timeout_sec
        self.spatial_provider = spatial_provider or SpatialProvider()

    # ------------------------------------------------------------------
    # 1. AI 解析：自然语言 -> TaskSpec（失败走关键词兜底，永不阻塞）
    # ------------------------------------------------------------------
    def parse_tasks(self, demand: str, requester: ClientInfo | None = None, patient_note: str | None = None) -> list[TaskSpec]:
        specs = self._parse_with_llm(demand, requester, patient_note)
        if not specs:
            specs = [self._parse_with_rules(demand)]
        cleaned = [spec for spec in specs if spec and spec.title.strip()]
        if not cleaned:
            cleaned = [TaskSpec(title="临时任务", description=demand.strip())]
        for spec in cleaned:
            if not spec.description:
                spec.description = demand.strip()
        return cleaned

    def _parse_with_llm(self, demand: str, requester: ClientInfo | None, patient_note: str | None) -> TaskSpec | None:
        if not self.api_key:
            return None
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": json.dumps(
                        {
                            "requester": {
                                "role": requester.assignedRole if requester else None,
                                "displayName": requester.displayName if requester else None,
                            },
                            "demand": demand,
                            "patient": {"situation": patient_note or ""},
                        },
                        ensure_ascii=False,
                    ),
                },
            ],
        }
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        req = request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_sec) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except (error.URLError, error.HTTPError, TimeoutError, json.JSONDecodeError):
            return None
        content = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        return self._extract_tasks(content)

    def _extract_tasks(self, content: str) -> list[TaskSpec]:
        if not content:
            return []
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.MULTILINE)
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        raw = match.group(0) if match else cleaned
        # 清理常见 JSON 错误（尾逗号）
        raw = re.sub(r",\s*([}\]])", r"\1", raw)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if not isinstance(data, dict):
            return []
        # 优先解析 tasks 数组；兼容旧的单任务对象
        raw_tasks = data.get("tasks")
        if not isinstance(raw_tasks, list):
            if isinstance(data.get("task"), dict):
                raw_tasks = [data]
            else:
                return []
        specs: list[TaskSpec] = []
        for item in raw_tasks:
            if not isinstance(item, dict):
                continue
            task = item.get("task") if isinstance(item.get("task"), dict) else item
            if not isinstance(task, dict):
                continue
            specs.append(
                TaskSpec(
                    title=str(task.get("title") or ""),
                    description=str(task.get("description") or ""),
                    required_skill=str(task.get("requiredSkill") or SKILL_FETCH),
                    priority=int(task.get("priority") or 3),
                    location_label=task.get("locationLabel"),
                    requires=item.get("requires") if isinstance(item.get("requires"), list) else [],
                )
            )
        return specs

    def _parse_with_rules(self, demand: str) -> TaskSpec:
        text = demand.strip()
        skill = SKILL_COORDINATE
        if any(k in text for k in ("取", "送", "搬运", "拿", "领", "递", "补充", "物资")):
            skill = SKILL_FETCH
        elif any(k in text for k in ("止血", "包扎", "施救", "抢救", "心肺", "按压", "除颤")):
            skill = SKILL_SAVE
        elif any(k in text for k in ("疏导", "清障", "通道", "接应", "引导", "疏散")):
            skill = SKILL_GUIDE
        title = text[:12] or "临时任务"
        return TaskSpec(
            title=title,
            description=text,
            required_skill=skill,
            priority=3,
            location_label=None,
            requires=[],
        )

    # ------------------------------------------------------------------
    # 2. 硬算法匹配度
    # ------------------------------------------------------------------
    def capability_score(self, client: ClientInfo, skill: str) -> int:
        text = " ".join(
            [
                (client.healthCondition or "").lower(),
                (client.professionIdentity or "").lower(),
                (client.organization or "").lower(),
                (client.profileBio or "").lower(),
                (client.displayName or "").lower(),
            ]
        )
        score = 0
        for keywords, weight in _CAPABILITY_RULES.get(skill, []):
            if any(k in text for k in keywords):
                score += weight
        return max(0, min(100, score))

    def health_risk(self, client: ClientInfo) -> bool:
        text = " ".join(
            [
                (client.healthCondition or "").lower(),
                (client.profileBio or "").lower(),
            ]
        )
        if any(k in text for k in _HIGH_RISK_MARKERS):
            return True
        summary = client.healthSignals
        if summary is not None:
            tags = {t.lower() for t in summary.riskTags or []}
            if tags.intersection({"tachycardia", "bradycardia", "low_spo2", "high_pressure", "limited_mobility"}):
                return True
            if summary.heartRateBpm is not None and (summary.heartRateBpm >= 120 or summary.heartRateBpm <= 45):
                return True
            if summary.bloodOxygenPercent is not None and summary.bloodOxygenPercent < 94:
                return True
        return False

    def distance_meters(self, a: Any, b: Any) -> float | None:
        try:
            return self.spatial_provider.local_distance_meters(a, b)
        except Exception:
            return None

    def match_score(
        self,
        client: ClientInfo,
        skill: str,
        target_location: Any | None,
        is_busy: bool,
        cooperation_bonus: int = 0,
    ) -> MatchResult:
        """matchScore = 距离35% + 资质40% + 状态15% + 协作10%。"""
        dist = self.distance_meters(client.location, target_location) if target_location is not None else None
        if dist is None:
            distance_score = 50.0  # 未知距离给中值
        elif dist <= 50:
            distance_score = 100.0
        elif dist >= 500:
            distance_score = 0.0
        else:
            distance_score = 100.0 * (1.0 - (dist - 50) / 450)

        capability = self.capability_score(client, skill)
        if is_busy:
            state_score = -200.0  # 繁忙直接淘汰
        elif self.health_risk(client):
            state_score = 20.0
        else:
            state_score = 100.0

        cooperation = min(100, 80 + cooperation_bonus)

        score = 0.35 * distance_score + 0.40 * capability + 0.15 * state_score + 0.10 * cooperation

        reasons: list[str] = []
        if dist is not None:
            reasons.append(f"距离现场约 {round(dist)} 米")
        else:
            reasons.append("暂无实时距离，按资质评估")
        reasons.append(f"资质匹配 {capability} 分")
        if is_busy:
            reasons.append("当前繁忙，不宜分配")
        elif state_score >= 100:
            reasons.append("在线空闲")
        return MatchResult(score=round(max(-200, score), 1), capability=capability, distance=dist, reasons=reasons)

    def explain(self) -> dict:
        return {
            "configured": bool(self.api_key),
            "model": self.model,
            "baseUrl": self.base_url,
            "timeoutSec": self.timeout_sec,
            "capabilityRules": {k: [[list(kw), w] for kw, w in v] for k, v in _CAPABILITY_RULES.items()},
            "systemPrompt": SYSTEM_PROMPT,
        }
