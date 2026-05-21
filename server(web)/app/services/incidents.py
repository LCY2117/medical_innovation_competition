from __future__ import annotations

import asyncio
import csv
import hashlib
import io
import json
import random
import re
import time
import uuid
import zipfile
from datetime import datetime, timezone
from typing import Dict

from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from app.models.schemas import (
    AedSite,
    AuditEvent,
    AutoJoinResponse,
    ClientInfo,
    CreateIncidentResponse,
    DemoBootstrapResponse,
    DispatchResponse,
    ExperimentExportResponse,
    GeoPoint,
    HealthSignalSummary,
    IncidentLogEntry,
    IncidentState,
    MutationResponse,
    RoleState,
    RoleStates,
    SosState,
)
from app.services.dispatch_ai import DispatchPlanner
from app.services.notifications import NotificationIntent, NotificationProvider, WebSocketFallbackNotificationProvider
from app.services.spatial import SpatialProvider
from app.storage.sqlite_store import SqliteIncidentStore


class NearestAedResult:
    def __init__(self, site: AedSite, distance_meters: float) -> None:
        self.site = site
        self.distanceMeters = distance_meters


class IncidentService:
    def __init__(
        self,
        store: SqliteIncidentStore,
        sos_duration_sec: int = 10,
        dispatch_delay_sec: int = 3,
        siliconflow_api_key: str | None = None,
        siliconflow_model: str = "Qwen/Qwen2-7B-Instruct",
        siliconflow_base_url: str = "https://api.siliconflow.cn/v1",
        siliconflow_timeout_sec: int = 8,
        local_model_base_url: str | None = None,
        local_model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        local_model_timeout_sec: int = 30,
        prefer_local_model: bool = True,
        map_provider: str = "demo",
        amap_service_key: str | None = None,
        map_distance_timeout_sec: int = 3,
        push_provider: str = "websocket",
        notification_provider: NotificationProvider | None = None,
    ) -> None:
        self.store = store
        self.sos_duration_sec = sos_duration_sec
        self.dispatch_delay_sec = dispatch_delay_sec
        snapshot = self.store.load_snapshot()
        self.incidents: Dict[str, IncidentState] = snapshot.incidents
        self.ws_connections: Dict[str, list[WebSocket]] = {}
        self.sos_tasks: Dict[str, asyncio.Task[None]] = {}
        self.current_incident_id: str | None = snapshot.current_incident_id
        self.clients: Dict[str, ClientInfo] = snapshot.clients
        self.aed_sites: Dict[str, AedSite] = snapshot.aed_sites
        self.spatial_provider = SpatialProvider(
            provider=map_provider,
            amap_service_key=amap_service_key,
            timeout_sec=map_distance_timeout_sec,
        )
        self.notification_provider = notification_provider or WebSocketFallbackNotificationProvider(
            provider=push_provider,
            send_state=self._send_websocket_state,
        )
        self.dispatch_planner = DispatchPlanner(
            api_key=siliconflow_api_key,
            model=siliconflow_model,
            base_url=siliconflow_base_url,
            timeout_sec=siliconflow_timeout_sec,
            local_base_url=local_model_base_url,
            local_model=local_model_name,
            local_timeout_sec=local_model_timeout_sec,
            prefer_local=prefer_local_model,
            spatial_provider=self.spatial_provider,
        )

    def create_incident(self) -> CreateIncidentResponse:
        incident_id = self._new_incident()
        self.current_incident_id = incident_id
        self._persist()
        return CreateIncidentResponse(incidentId=incident_id)

    def get_current_incident(self) -> IncidentState:
        if not self.current_incident_id or self.current_incident_id not in self.incidents:
            self.current_incident_id = self._new_incident()
            self._persist()
        return self.incidents[self.current_incident_id]

    def register_client(
        self,
        user_id: str,
        display_name: str,
        organization: str,
        health_condition: str,
        profession_identity: str,
        profile_bio: str,
        device_type: str = "ANDROID",
        location: GeoPoint | None = None,
        health_signals: HealthSignalSummary | None = None,
    ) -> ClientInfo:
        previous = self.clients.get(user_id)
        client = ClientInfo(
            userId=user_id,
            displayName=display_name,
            organization=organization,
            healthCondition=health_condition,
            professionIdentity=profession_identity,
            profileBio=profile_bio,
            deviceType=device_type,
            online=True,
            lastSeenTs=self._now_ms(),
            assignedRole=self._assigned_role_for(user_id),
            patientCandidate=self._is_patient_candidate(health_condition, profile_bio),
            isPatient=self._is_patient(user_id),
            location=location,
            healthSignals=health_signals or (previous.healthSignals if previous else None),
        )
        self.clients[user_id] = client
        self._persist()
        return client

    def update_client_location(self, user_id: str, location: GeoPoint) -> ClientInfo:
        client = self.clients.get(user_id)
        if client is None:
            raise HTTPException(status_code=404, detail="Client not registered")
        updated_location = location.model_copy(update={"updatedTs": location.updatedTs or self._now_ms()})
        updated = client.model_copy(
            update={"location": updated_location, "lastSeenTs": self._now_ms(), "online": True}
        )
        self.clients[user_id] = updated
        self._persist()
        return updated

    def update_client_health(self, user_id: str, health_signals: HealthSignalSummary) -> ClientInfo:
        client = self.clients.get(user_id)
        if client is None:
            raise HTTPException(status_code=404, detail="Client not registered")
        updated_signals = health_signals.model_copy(update={"updatedTs": health_signals.updatedTs or self._now_ms()})
        updated = client.model_copy(
            update={"healthSignals": updated_signals, "lastSeenTs": self._now_ms(), "online": True}
        )
        self.clients[user_id] = updated
        self._persist()
        return updated

    def list_clients(self) -> list[ClientInfo]:
        clients: list[ClientInfo] = []
        for user_id, client in self.clients.items():
            clients.append(
                client.model_copy(
                    update={
                        "lastSeenTs": client.lastSeenTs,
                        "assignedRole": self._assigned_role_for(user_id),
                        "patientCandidate": self._is_patient_candidate(client.healthCondition, client.profileBio),
                        "isPatient": self._is_patient(user_id),
                        "location": client.location,
                        "healthSignals": client.healthSignals,
                    }
                )
            )
        return sorted(
            clients,
            key=lambda item: (
                0 if item.isPatient else 1,
                0 if item.patientCandidate else 1,
                -item.lastSeenTs,
            ),
        )

    def list_aed_sites(self) -> list[AedSite]:
        return sorted(self.aed_sites.values(), key=lambda site: site.name)

    def record_audit_event(self, event: AuditEvent) -> None:
        self.store.append_audit_event(event)

    def list_audit_events(self, limit: int = 100) -> list[AuditEvent]:
        return self.store.list_audit_events(limit)

    def upsert_aed_site(
        self,
        name: str,
        location: GeoPoint,
        status: str = "AVAILABLE",
        access_notes: str = "",
        site_id: str | None = None,
    ) -> AedSite:
        now = self._now_ms()
        normalized_id = site_id or f"aed-{uuid.uuid4()}"
        site = AedSite(
            siteId=normalized_id,
            name=name,
            location=location.model_copy(update={"updatedTs": location.updatedTs or now}),
            status=status,
            accessNotes=access_notes,
            lastCheckedTs=now,
        )
        self.aed_sites[normalized_id] = site
        state = self.get_current_incident()
        state.aedSites = self.list_aed_sites()
        state.logs.append(IncidentLogEntry(ts=now, msg=f"AED site updated ({site.name})"))
        self._persist()
        return site

    async def designate_patient(
        self,
        patient_user_id: str,
        source_label: str = "dashboard",
        cancel_sos_timer: bool = True,
    ) -> DispatchResponse:
        state = self.get_current_incident()
        now = self._now_ms()
        if patient_user_id not in self.clients:
            raise HTTPException(status_code=404, detail="Patient client not registered")
        if state.phase != "CREATED":
            if state.patientUserId == patient_user_id:
                return self._dispatch_response_from_state(state)
            raise HTTPException(status_code=409, detail="Incident already has an active patient; reset before selecting another patient")

        state.phase = "DISPATCHING"
        state.sos = self._new_sos(status="ALERTING", start_ts=now)
        state.roles = self._new_roles()
        state.patientUserId = patient_user_id
        state.dispatchSource = None
        state.logs.append(IncidentLogEntry(ts=now, msg=f"Patient designated by {source_label} ({patient_user_id})"))
        state.logs.append(IncidentLogEntry(ts=now, msg="AI dispatching started"))
        self._touch_client(patient_user_id)

        if cancel_sos_timer:
            task = self.sos_tasks.get(state.incidentId)
            if task and not task.done():
                task.cancel()

        self._persist()
        await self._broadcast_state_async(state.incidentId)

        if self.dispatch_delay_sec > 0:
            await asyncio.sleep(self.dispatch_delay_sec)

        assignments, source, rationale = await asyncio.to_thread(
            self.dispatch_planner.assign_roles,
            patient_user_id,
            self.list_clients(),
            self.list_aed_sites(),
        )
        state.phase = "DISPATCHED"
        state.dispatchSource = source
        state.dispatchRationale = rationale
        state.aedSites = self.list_aed_sites()
        for role_name, assigned_user_id in assignments.items():
            if assigned_user_id is None:
                continue
            role_state = getattr(state.roles, role_name)
            role_state.status = "ASSIGNED"
            role_state.userId = assigned_user_id
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"{role_name} assigned ({assigned_user_id}) via {source}"))
            self._touch_client(assigned_user_id)

        self._persist()
        await self._broadcast_state_async(state.incidentId)
        return DispatchResponse(
            incidentId=state.incidentId,
            patientUserId=patient_user_id,
            assignments=assignments,
            source=source,
            rationale=rationale,
        )

    async def reset_current_incident(self) -> MutationResponse:
        if not self.current_incident_id or self.current_incident_id not in self.incidents:
            self.current_incident_id = self._new_incident()
            self._persist()
            await self._broadcast_state_async(self.current_incident_id)
            return MutationResponse(
                incidentId=self.current_incident_id,
                phase=self.incidents[self.current_incident_id].phase,
            )

        state = self.incidents[self.current_incident_id]
        state.phase = "CREATED"
        state.sos = self._new_sos(status="MONITORING", start_ts=None)
        state.roles = self._new_roles()
        state.patientUserId = None
        state.dispatchSource = None
        state.dispatchRationale = {}
        state.aedSites = self.list_aed_sites()
        state.logs = [IncidentLogEntry(ts=self._now_ms(), msg="Incident reset")]

        task = self.sos_tasks.get(self.current_incident_id)
        if task and not task.done():
            task.cancel()

        self._persist()
        await self._broadcast_state_async(self.current_incident_id)
        return MutationResponse(incidentId=self.current_incident_id, phase=state.phase)

    async def sos_start(self, incident_id: str) -> MutationResponse:
        state = self._require_incident(incident_id)
        if state.phase != "CREATED":
            raise HTTPException(status_code=400, detail="Incident already dispatched")

        start_ts = self._now_ms()
        state.sos = self._new_sos(status="ALERTING", start_ts=start_ts)
        state.logs.append(IncidentLogEntry(ts=start_ts, msg="SOS alerting started"))
        self._persist()
        await self._broadcast_state_async(incident_id)

        task = self.sos_tasks.get(incident_id)
        if task and not task.done():
            task.cancel()
        self.sos_tasks[incident_id] = asyncio.create_task(self._auto_trigger_after(incident_id, start_ts))

        return MutationResponse(incidentId=incident_id, phase=state.phase)

    async def sos_cancel(self, incident_id: str) -> MutationResponse:
        state = self._require_incident(incident_id)
        if state.phase != "CREATED":
            return MutationResponse(incidentId=incident_id, phase=state.phase)

        state.sos = self._new_sos(status="MONITORING", start_ts=None)
        state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg="SOS alerting canceled"))
        self._persist()
        await self._broadcast_state_async(incident_id)

        task = self.sos_tasks.get(incident_id)
        if task and not task.done():
            task.cancel()

        return MutationResponse(incidentId=incident_id, phase=state.phase)

    async def patient_sos_start(self, incident_id: str, patient_user_id: str) -> MutationResponse:
        state = self._require_incident(incident_id)
        if state.phase != "CREATED":
            if state.patientUserId == patient_user_id:
                return MutationResponse(incidentId=incident_id, phase=state.phase)
            raise HTTPException(status_code=400, detail="Incident already dispatched")
        if patient_user_id not in self.clients:
            raise HTTPException(status_code=404, detail="Patient client not registered")
        if state.sos.status == "ALERTING" and state.patientUserId == patient_user_id:
            return MutationResponse(incidentId=incident_id, phase=state.phase)

        start_ts = self._now_ms()
        state.sos = self._new_sos(status="ALERTING", start_ts=start_ts)
        state.patientUserId = patient_user_id
        state.roles = self._new_roles()
        state.dispatchSource = None
        state.dispatchRationale = {}
        state.aedSites = self.list_aed_sites()
        state.logs.append(IncidentLogEntry(ts=start_ts, msg=f"Patient SOS alerting started ({patient_user_id})"))
        self._touch_client(patient_user_id)
        self._persist()
        await self._broadcast_state_async(incident_id)

        task = self.sos_tasks.get(incident_id)
        if task and not task.done():
            task.cancel()
        if self.sos_duration_sec <= 0:
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"Patient SOS confirmed ({patient_user_id})"))
            self._persist()
            dispatch = await self.designate_patient(patient_user_id, source_label="patient SOS", cancel_sos_timer=False)
            return MutationResponse(incidentId=dispatch.incidentId, phase=self.incidents[dispatch.incidentId].phase)
        self.sos_tasks[incident_id] = asyncio.create_task(
            self._auto_designate_after(incident_id, patient_user_id, start_ts)
        )

        return MutationResponse(incidentId=incident_id, phase=state.phase)

    async def patient_sos_cancel(self, incident_id: str, patient_user_id: str) -> MutationResponse:
        state = self._require_incident(incident_id)
        if state.phase != "CREATED":
            return MutationResponse(incidentId=incident_id, phase=state.phase)
        if state.patientUserId not in (None, patient_user_id):
            raise HTTPException(status_code=403, detail="Only the active patient can cancel SOS")

        state.sos = self._new_sos(status="MONITORING", start_ts=None)
        state.patientUserId = None
        state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"Patient SOS alerting canceled ({patient_user_id})"))
        self._persist()
        await self._broadcast_state_async(incident_id)

        task = self.sos_tasks.get(incident_id)
        if task and not task.done():
            task.cancel()

        return MutationResponse(incidentId=incident_id, phase=state.phase)

    async def join_current_auto(self, user_id: str) -> AutoJoinResponse:
        current = self.get_current_incident()
        incident_id = current.incidentId
        self._touch_client(user_id)

        for role_name in ("PRIME", "RUNNER", "GUIDE"):
            if getattr(current.roles, role_name).userId == user_id:
                return AutoJoinResponse(incidentId=incident_id, role=role_name)

        available = [
            role_name
            for role_name in ("PRIME", "RUNNER", "GUIDE")
            if getattr(current.roles, role_name).userId is None
        ]
        if not available:
            raise HTTPException(status_code=409, detail="No available roles")

        assigned = random.choice(available)
        role_state = getattr(current.roles, assigned)
        role_state.status = "JOINED"
        role_state.userId = user_id
        if current.phase == "CREATED":
            current.phase = "DISPATCHED"

        current.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"{assigned} auto-joined ({user_id})"))
        self._persist()
        await self._broadcast_state_async(incident_id)
        return AutoJoinResponse(incidentId=incident_id, role=assigned)

    def get_incident(self, incident_id: str) -> IncidentState:
        return self._require_incident(incident_id)

    async def join_incident(self, incident_id: str, role: str, user_id: str) -> MutationResponse:
        state = self._require_incident(incident_id)

        normalized_role = role.upper()
        if normalized_role not in {"PRIME", "RUNNER", "GUIDE"}:
            raise HTTPException(status_code=400, detail="Invalid role")
        self._touch_client(user_id)

        role_state = getattr(state.roles, normalized_role)
        role_state.status = "JOINED"
        role_state.userId = user_id

        if state.phase == "CREATED":
            state.phase = "DISPATCHED"

        state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"{normalized_role} joined ({user_id})"))
        self._persist()
        await self._broadcast_state_async(incident_id)
        return MutationResponse(incidentId=incident_id, phase=state.phase)

    async def post_action(self, incident_id: str, action: str, user_id: str) -> MutationResponse:
        state = self._require_incident(incident_id)
        normalized_action = action.upper()
        self._touch_client(user_id)

        if normalized_action == "CPR_STARTED":
            self._ensure_role_actor(state, "PRIME", user_id)
            self._ensure_role_status(state.roles.PRIME.status, {"ASSIGNED", "JOINED", "CPR_STARTED"}, "PRIME")
            state.phase = "CPR"
            state.roles.PRIME.status = "CPR_STARTED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"CPR started by {user_id}"))
        elif normalized_action == "AED_ANALYSIS_STARTED":
            self._ensure_role_actor(state, "PRIME", user_id)
            self._ensure_role_status(
                state.roles.PRIME.status,
                {"CPR_STARTED", "AED_ANALYZING", "AED_SHOCK_DELIVERED"},
                "PRIME",
            )
            self._ensure_role_status(state.roles.RUNNER.status, {"AED_DELIVERED"}, "RUNNER")
            state.phase = "AED_ANALYZING"
            state.roles.PRIME.status = "AED_ANALYZING"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED analysis started by {user_id}"))
        elif normalized_action == "AED_SHOCK_DELIVERED":
            self._ensure_role_actor(state, "PRIME", user_id)
            self._ensure_role_status(state.roles.PRIME.status, {"AED_ANALYZING", "AED_SHOCK_DELIVERED"}, "PRIME")
            self._ensure_role_status(state.roles.RUNNER.status, {"AED_DELIVERED"}, "RUNNER")
            state.phase = "SHOCK_DELIVERED"
            state.roles.PRIME.status = "AED_SHOCK_DELIVERED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED shock delivered by {user_id}"))
        elif normalized_action == "AED_PICKED":
            self._ensure_role_actor(state, "RUNNER", user_id)
            self._ensure_role_status(state.roles.RUNNER.status, {"ASSIGNED", "JOINED", "AED_PICKED"}, "RUNNER")
            state.phase = "AED_PICKED"
            state.roles.RUNNER.status = "AED_PICKED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED picked by {user_id}"))
        elif normalized_action == "AED_DELIVERED":
            self._ensure_role_actor(state, "RUNNER", user_id)
            self._ensure_role_status(state.roles.RUNNER.status, {"AED_PICKED", "AED_DELIVERED"}, "RUNNER")
            state.phase = "AED_DELIVERED"
            state.roles.RUNNER.status = "AED_DELIVERED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED delivered by {user_id}"))
        elif normalized_action == "AMBULANCE_ARRIVED":
            self._ensure_role_actor(state, "GUIDE", user_id)
            self._ensure_role_status(
                state.roles.GUIDE.status,
                {"ASSIGNED", "JOINED", "AMBULANCE_ARRIVED"},
                "GUIDE",
            )
            state.phase = "HANDOVER"
            state.roles.GUIDE.status = "AMBULANCE_ARRIVED"
            state.logs.append(
                IncidentLogEntry(ts=self._now_ms(), msg=f"Ambulance arrived (reported by {user_id})")
            )
        elif normalized_action == "HANDOVER_COMPLETED":
            if state.phase not in {"HANDOVER", "ARCHIVED"}:
                raise HTTPException(status_code=409, detail="Handover not ready")
            participants = {
                state.patientUserId,
                state.roles.PRIME.userId,
                state.roles.RUNNER.userId,
                state.roles.GUIDE.userId,
            }
            if user_id not in participants:
                raise HTTPException(status_code=403, detail="Only active participants can complete handover")
            state.phase = "ARCHIVED"
            state.roles.GUIDE.status = "HANDOVER_COMPLETED"
            state.logs.append(
                IncidentLogEntry(ts=self._now_ms(), msg=f"Handover completed by {user_id}")
            )
        else:
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"Unknown action: {normalized_action} by {user_id}"))

        self._persist()
        await self._broadcast_state_async(incident_id)
        return MutationResponse(incidentId=incident_id, phase=state.phase)

    async def trigger_incident(self, incident_id: str) -> MutationResponse:
        state = self._require_incident(incident_id)
        if state.phase == "CREATED":
            state.phase = "DISPATCHED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg="Incident triggered"))

        self._persist()
        await self._broadcast_state_async(incident_id)
        return MutationResponse(incidentId=incident_id, phase=state.phase)

    async def bootstrap_demo(self) -> DemoBootstrapResponse:
        self.clients = {}
        self.aed_sites = {}
        incident_id = self._new_incident()
        self.current_incident_id = incident_id

        demo_locations = {
            "patient": GeoPoint(latitude=39.904120, longitude=116.407210, label="教学楼 A 座 2 层走廊", floor="2F", source="demo"),
            "doctor": GeoPoint(latitude=39.904210, longitude=116.407260, label="教学楼 A 座 1 层大厅", floor="1F", source="demo"),
            "runner": GeoPoint(latitude=39.903920, longitude=116.407020, label="操场入口", floor="1F", source="demo"),
            "guide": GeoPoint(latitude=39.904500, longitude=116.407620, label="校门岗亭", floor="1F", source="demo"),
            "aed1": GeoPoint(latitude=39.904030, longitude=116.406920, label="二楼服务台 AED 箱", floor="2F", source="demo"),
            "aed2": GeoPoint(latitude=39.904560, longitude=116.407700, label="校门值班室 AED 箱", floor="1F", source="demo"),
        }

        demo_health = {
            "patient": HealthSignalSummary(
                source="mock",
                authorizationStatus="authorized",
                heartRateBpm=118,
                bloodOxygenPercent=92,
                pressureScore=82,
                activityLevel="low",
                sleepQuality="poor",
                riskTags=["tachycardia", "low_spo2", "high_pressure"],
                note="OPPO Health mock: simulated high-risk patient baseline",
            ),
            "doctor": HealthSignalSummary(
                source="mock",
                authorizationStatus="authorized",
                heartRateBpm=76,
                bloodOxygenPercent=98,
                pressureScore=35,
                activityLevel="normal",
                sleepQuality="good",
                riskTags=[],
                note="OPPO Health mock: stable professional rescuer",
            ),
            "runner": HealthSignalSummary(
                source="mock",
                authorizationStatus="authorized",
                heartRateBpm=84,
                bloodOxygenPercent=99,
                pressureScore=28,
                activityLevel="high",
                sleepQuality="good",
                riskTags=[],
                note="OPPO Health mock: high mobility responder",
            ),
            "guide": HealthSignalSummary(
                source="mock",
                authorizationStatus="authorized",
                heartRateBpm=80,
                bloodOxygenPercent=97,
                pressureScore=44,
                activityLevel="normal",
                sleepQuality="fair",
                riskTags=[],
                note="OPPO Health mock: steady guide responder",
            ),
        }

        self.register_client("demo-patient", "冠心病患者", "模拟社区", "存在心脏骤停风险", "患者侧", "多年冠心病病史，需要重点监护", "ANDROID", demo_locations["patient"], demo_health["patient"])
        self.register_client("demo-prime", "张医生", "市医院急救科", "身体状态一般", "医生 / 专业急救人员", "急救科医生，熟悉 CPR 和 AED 处置", "ANDROID", demo_locations["doctor"], demo_health["doctor"])
        self.register_client("demo-runner", "体育生小李", "大学校园", "身体素质良好", "有一定急救常识", "体育生，跑得快，熟悉校园路线，可快速取送 AED", "ANDROID", demo_locations["runner"], demo_health["runner"])
        self.register_client("demo-guide", "安保老王", "校园安保", "身体状态一般", "安保 / 物业 / 场地协调人员", "熟悉楼栋出入口、电梯和救护车通道", "ANDROID", demo_locations["guide"], demo_health["guide"])
        self.upsert_aed_site("二楼服务台 AED", demo_locations["aed1"], access_notes="教学楼 A 座服务台左侧红色 AED 箱", site_id="demo-aed-1")
        self.upsert_aed_site("校门值班室 AED", demo_locations["aed2"], access_notes="校门岗亭内，安保可协助取用", site_id="demo-aed-2")

        state = self.incidents[incident_id]
        state.aedSites = self.list_aed_sites()
        state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg="Demo scenario bootstrapped"))
        self._persist()
        await self._broadcast_state_async(incident_id)
        return DemoBootstrapResponse(
            incidentId=incident_id,
            clients=self.list_clients(),
            aedSites=self.list_aed_sites(),
        )

    def export_experiment(self, incident_id: str | None = None) -> ExperimentExportResponse:
        state = self._require_incident(incident_id) if incident_id else self.get_current_incident()
        assignments = {
            "PRIME": state.roles.PRIME.userId,
            "RUNNER": state.roles.RUNNER.userId,
            "GUIDE": state.roles.GUIDE.userId,
        }
        aed_sites = state.aedSites or self.list_aed_sites()
        clients = self._clients_for_export(state)
        return ExperimentExportResponse(
            incidentId=state.incidentId,
            generatedAt=self._now_ms(),
            phase=state.phase,
            patientUserId=state.patientUserId,
            dispatchSource=state.dispatchSource,
            assignments=assignments,
            metrics=self._experiment_metrics(state, clients, aed_sites),
            timeline=state.logs,
            clients=clients,
            aedSites=aed_sites,
            dispatchRationale=state.dispatchRationale,
        )

    def export_experiment_package(self, incident_id: str | None = None) -> tuple[str, bytes]:
        export = self.export_experiment(incident_id)
        payload = export.model_dump(mode="json")
        anonymized_payload, participant_map = self._anonymized_experiment_payload(export)
        files: dict[str, str] = {
            "README.md": self._experiment_readme(export),
            "expert_summary.md": self._expert_summary(export, participant_map),
            "expert_review_checklist.md": self._expert_review_checklist(export, participant_map),
            "experiment.json": json.dumps(payload, ensure_ascii=False, indent=2),
            "experiment_anonymized.json": json.dumps(anonymized_payload, ensure_ascii=False, indent=2),
            "metrics.csv": self._csv_text(
                [{"metric": key, "value": value} for key, value in export.metrics.items()],
                ["metric", "value"],
            ),
            "timeline.csv": self._csv_text(
                self._timeline_export_rows(export.timeline),
                self._timeline_export_fields(),
            ),
            "clients.csv": self._csv_text(self._client_export_rows(export.clients), self._client_export_fields()),
            "clients_anonymized.csv": self._csv_text(
                self._client_export_rows(export.clients, participant_map=participant_map, anonymized=True),
                self._client_export_fields(anonymized=True),
            ),
            "aed_sites.csv": self._csv_text(self._aed_site_export_rows(export.aedSites), self._aed_site_export_fields()),
            "dispatch_rationale.csv": self._csv_text(
                self._dispatch_rationale_export_rows(export, participant_map),
                self._dispatch_rationale_export_fields(),
            ),
            "observer_record_form.csv": self._csv_text(
                self._observer_record_rows(export),
                self._observer_record_fields(),
            ),
            "pre_experiment_round_summary.csv": self._csv_text(
                self._pre_experiment_round_summary_rows(export),
                self._pre_experiment_round_summary_fields(),
            ),
        }
        files["manifest.json"] = self._package_manifest(export, files)
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, mode="w", compression=zipfile.ZIP_DEFLATED) as package:
            for name, content in files.items():
                package.writestr(name, content, compress_type=zipfile.ZIP_DEFLATED)
        filename = f"lifereflex-experiment-{export.incidentId}.zip"
        return filename, archive.getvalue()

    def _dispatch_response_from_state(self, state: IncidentState) -> DispatchResponse:
        assignments = {
            "PRIME": state.roles.PRIME.userId,
            "RUNNER": state.roles.RUNNER.userId,
            "GUIDE": state.roles.GUIDE.userId,
        }
        return DispatchResponse(
            incidentId=state.incidentId,
            patientUserId=state.patientUserId,
            assignments=assignments,
            source=state.dispatchSource or "existing",
            rationale=state.dispatchRationale,
        )

    async def bootstrap(self) -> None:
        for incident_id, state in list(self.incidents.items()):
            if state.phase != "CREATED":
                continue
            if state.sos.status != "ALERTING" or state.sos.startTs is None:
                continue

            remaining = self.sos_duration_sec - max(0, int((self._now_ms() - state.sos.startTs) / 1000))
            task = self.sos_tasks.get(incident_id)
            if task and not task.done():
                task.cancel()

            if remaining <= 0:
                if state.patientUserId:
                    state.logs.append(
                        IncidentLogEntry(ts=self._now_ms(), msg="Patient SOS confirmed after restart")
                    )
                    self._persist()
                    await self.designate_patient(
                        state.patientUserId,
                        source_label="patient SOS after restart",
                        cancel_sos_timer=False,
                    )
                else:
                    state.phase = "DISPATCHED"
                    state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg="Incident auto-triggered after restart"))
                    self._persist()
            else:
                if state.patientUserId:
                    self.sos_tasks[incident_id] = asyncio.create_task(
                        self._auto_designate_after(
                            incident_id,
                            state.patientUserId,
                            state.sos.startTs,
                            delay_override=remaining,
                        )
                    )
                else:
                    self.sos_tasks[incident_id] = asyncio.create_task(
                        self._auto_trigger_after(incident_id, state.sos.startTs, delay_override=remaining)
                    )

    def health(self) -> dict:
        store_health = self.store.health()
        dispatch_info = {}
        try:
            dispatch_info = self.dispatch_planner.explain()
        except Exception:
            dispatch_info = {"error": "dispatch_explain_failed"}

        return {
            "ok": True,
            "storage": store_health,
            "currentIncidentId": self.current_incident_id,
            "loadedIncidents": len(self.incidents),
            "registeredClients": len(self.clients),
            "registeredAedSites": len(self.aed_sites),
            "activeWebSockets": sum(len(connections) for connections in self.ws_connections.values()),
            "activeSosTimers": sum(1 for task in self.sos_tasks.values() if not task.done()),
            "dispatch": dispatch_info,
            "mapProvider": self.spatial_provider.explain(),
            "pushProvider": self.notification_provider.explain(),
            "demoReadiness": self._demo_readiness(),
        }

    def dispatch_explain(self) -> dict:
        explanation = self.dispatch_planner.explain()
        explanation["dispatchDelaySec"] = self.dispatch_delay_sec
        explanation["configFile"] = "server（云端服务）/.env"
        explanation["envKeys"] = [
            "LRA_DISPATCH_DELAY_SEC",
            "LRA_SILICONFLOW_API_KEY",
            "LRA_SILICONFLOW_MODEL",
            "LRA_SILICONFLOW_BASE_URL",
            "LRA_SILICONFLOW_TIMEOUT_SEC",
            "LRA_MAP_PROVIDER",
            "LRA_AMAP_SERVICE_KEY",
            "LRA_MAP_DISTANCE_TIMEOUT_SEC",
        ]
        explanation["mapProvider"] = self.spatial_provider.explain()
        return explanation

    def _demo_readiness(self) -> dict:
        state = self.incidents.get(self.current_incident_id or "") if self.current_incident_id else None
        clients = self._clients_for_export(state) if state else self.list_clients()
        aed_sites = state.aedSites if state and state.aedSites else self.list_aed_sites()
        clients_with_location = sum(1 for client in clients if client.location is not None)
        clients_with_health = sum(1 for client in clients if client.healthSignals is not None)
        available_aed_count = sum(1 for site in aed_sites if site.status.upper() == "AVAILABLE")
        assigned_count = (
            sum(1 for role_name in ("PRIME", "RUNNER", "GUIDE") if getattr(state.roles, role_name).userId)
            if state
            else 0
        )
        warnings: list[str] = []
        if state is None:
            warnings.append("尚未创建当前事件")
        if len(clients) < 4:
            warnings.append("建议至少准备 4 台终端：患者、PRIME、RUNNER、GUIDE")
        if available_aed_count < 1:
            warnings.append("缺少可用 AED 点位")
        if clients_with_location < len(clients):
            warnings.append("部分终端未上报位置")
        if clients_with_health < len(clients):
            warnings.append("部分终端缺少健康摘要")
        if state and state.phase in {"DISPATCHED", "CPR", "AED_PICKED", "AED_DELIVERED", "AED_ANALYZING", "SHOCK_DELIVERED", "HANDOVER", "ARCHIVED"} and assigned_count < 3:
            warnings.append("角色分派未完整覆盖 PRIME/RUNNER/GUIDE")

        return {
            "ready": state is not None and len(clients) >= 4 and available_aed_count >= 1 and not warnings,
            "incidentId": state.incidentId if state else None,
            "phase": state.phase if state else None,
            "patientSelected": bool(state and state.patientUserId),
            "clientCount": len(clients),
            "assignedRoleCount": assigned_count,
            "availableAedSiteCount": available_aed_count,
            "clientsWithLocation": clients_with_location,
            "locationCoveragePercent": round((clients_with_location / len(clients)) * 100, 1) if clients else 0,
            "clientsWithHealthSignals": clients_with_health,
            "healthCoveragePercent": round((clients_with_health / len(clients)) * 100, 1) if clients else 0,
            "exportReady": state is not None and bool(state.logs),
            "warnings": warnings,
        }

    async def handle_websocket(self, websocket: WebSocket, incident_id: str) -> None:
        await websocket.accept()

        if incident_id not in self.incidents:
            await websocket.send_json({"type": "ERROR", "payload": "Incident not found"})
            await websocket.close()
            return

        self.ws_connections.setdefault(incident_id, []).append(websocket)
        await websocket.send_json({"type": "STATE", "payload": self._incident_payload(self.incidents[incident_id])})

        try:
            while True:
                await asyncio.sleep(30)
        except WebSocketDisconnect:
            pass
        finally:
            self.ws_connections[incident_id] = [
                ws for ws in self.ws_connections.get(incident_id, []) if ws is not websocket
            ]

    def _new_incident(self) -> str:
        incident_id = str(uuid.uuid4())
        self.incidents[incident_id] = IncidentState(
            incidentId=incident_id,
            phase="CREATED",
            sos=self._new_sos(status="MONITORING", start_ts=None),
            roles=self._new_roles(),
            logs=[IncidentLogEntry(ts=self._now_ms(), msg="Incident created")],
            patientUserId=None,
            dispatchSource=None,
            aedSites=self.list_aed_sites(),
            dispatchRationale={},
        )
        self.ws_connections.setdefault(incident_id, [])
        return incident_id

    def _new_roles(self) -> RoleStates:
        return RoleStates(
            PRIME=RoleState(status="", userId=None),
            RUNNER=RoleState(status="", userId=None),
            GUIDE=RoleState(status="", userId=None),
        )

    def _new_sos(self, status: str, start_ts: int | None) -> SosState:
        return SosState(status=status, startTs=start_ts, durationSec=self.sos_duration_sec)

    def _require_incident(self, incident_id: str) -> IncidentState:
        state = self.incidents.get(incident_id)
        if state is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        return state

    async def _broadcast_state_async(self, incident_id: str) -> None:
        await self.notification_provider.notify(
            NotificationIntent(
                incident_id=incident_id,
                event_type="state_updated",
                title="Incident state updated",
                body="Incident state has changed and should be synchronized.",
            )
        )

    async def _send_websocket_state(self, incident_id: str) -> int:
        state = self.incidents.get(incident_id)
        if state is None:
            return 0

        payload = {"type": "STATE", "payload": self._incident_payload(state)}
        alive: list[WebSocket] = []
        for ws in self.ws_connections.get(incident_id, []):
            try:
                await ws.send_json(payload)
                alive.append(ws)
            except Exception:
                pass
        self.ws_connections[incident_id] = alive
        return len(alive)

    async def _auto_trigger_after(self, incident_id: str, start_ts: int, delay_override: int | None = None) -> None:
        await asyncio.sleep(delay_override if delay_override is not None else self.sos_duration_sec)
        state = self.incidents.get(incident_id)
        if state is None:
            return
        if state.phase != "CREATED":
            return
        if state.sos.status != "ALERTING" or state.sos.startTs != start_ts:
            return

        state.phase = "DISPATCHED"
        state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg="Incident auto-triggered"))
        self._persist()
        await self._broadcast_state_async(incident_id)

    async def _auto_designate_after(
        self,
        incident_id: str,
        patient_user_id: str,
        start_ts: int,
        delay_override: int | None = None,
    ) -> None:
        await asyncio.sleep(delay_override if delay_override is not None else self.sos_duration_sec)
        state = self.incidents.get(incident_id)
        if state is None:
            return
        if state.phase != "CREATED":
            return
        if state.sos.status != "ALERTING" or state.sos.startTs != start_ts:
            return
        if state.patientUserId != patient_user_id:
            return

        state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"Patient SOS confirmed ({patient_user_id})"))
        self._persist()
        await self.designate_patient(patient_user_id, source_label="patient SOS", cancel_sos_timer=False)

    @staticmethod
    def _incident_payload(state: IncidentState) -> dict:
        return state.model_dump(mode="json")

    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)

    def _persist(self) -> None:
        self.store.save_snapshot(self.incidents, self.current_incident_id, self.clients, self.aed_sites)

    def _touch_client(self, user_id: str) -> None:
        client = self.clients.get(user_id)
        if client is None:
            return
        self.clients[user_id] = client.model_copy(update={"lastSeenTs": self._now_ms(), "online": True})
        self._persist()

    @staticmethod
    def _latest_log_ts(state: IncidentState, keyword: str) -> int | None:
        lowered = keyword.lower()
        for entry in reversed(state.logs):
            if lowered in entry.msg.lower():
                return entry.ts
        return None

    @staticmethod
    def _iso_timestamp(ts: int | None) -> str | None:
        if ts is None:
            return None
        return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat()

    def _distance_meters(self, a: GeoPoint | None, b: GeoPoint | None) -> float | None:
        return self.spatial_provider.distance_meters(a, b).meters

    def _nearest_aed(self, origin: GeoPoint | None, aed_sites: list[AedSite]) -> NearestAedResult | None:
        if origin is None:
            return None
        candidates: list[NearestAedResult] = []
        for site in aed_sites:
            if site.status.upper() != "AVAILABLE":
                continue
            distance = self._distance_meters(origin, site.location)
            if distance is not None:
                candidates.append(NearestAedResult(site=site, distance_meters=distance))
        if not candidates:
            return None
        return min(candidates, key=lambda item: item.distanceMeters)

    def _clients_for_export(self, state: IncidentState) -> list[ClientInfo]:
        clients: list[ClientInfo] = []
        for client in self.clients.values():
            assigned_role = None
            for role_name in ("PRIME", "RUNNER", "GUIDE"):
                if getattr(state.roles, role_name).userId == client.userId:
                    assigned_role = role_name
                    break
            clients.append(
                client.model_copy(
                    update={
                        "assignedRole": assigned_role,
                        "patientCandidate": self._is_patient_candidate(client.healthCondition, client.profileBio),
                        "isPatient": state.patientUserId == client.userId,
                        "location": client.location,
                        "healthSignals": client.healthSignals,
                    }
                )
            )
        return sorted(
            clients,
            key=lambda item: (
                0 if item.isPatient else 1,
                0 if item.patientCandidate else 1,
                -item.lastSeenTs,
            ),
        )

    def _experiment_metrics(
        self,
        state: IncidentState,
        clients: list[ClientInfo],
        aed_sites: list[AedSite],
    ) -> dict[str, int | float | None]:
        designated_ts = self._latest_log_ts(state, "Patient designated") or self._latest_log_ts(state, "SOS alerting started")
        dispatch_done_ts = self._latest_log_ts(state, "assigned")
        cpr_ts = self._latest_log_ts(state, "CPR started")
        aed_picked_ts = self._latest_log_ts(state, "AED picked")
        aed_delivered_ts = self._latest_log_ts(state, "AED delivered")
        ambulance_ts = self._latest_log_ts(state, "Ambulance arrived")
        patient = next((client for client in clients if client.userId == state.patientUserId), None)
        runner = next((client for client in clients if client.userId == state.roles.RUNNER.userId), None)
        nearest_aed = self._nearest_aed(runner.location if runner else None, aed_sites)
        runner_route_meters = None
        if runner and patient and nearest_aed and patient.location:
            aed_to_patient = self._distance_meters(nearest_aed.site.location, patient.location)
            if aed_to_patient is not None:
                runner_route_meters = round(nearest_aed.distanceMeters + aed_to_patient, 1)
        assigned_count = sum(1 for role_name in ("PRIME", "RUNNER", "GUIDE") if getattr(state.roles, role_name).userId)
        available_aed_count = sum(1 for site in aed_sites if site.status.upper() == "AVAILABLE")
        clients_with_location = sum(1 for client in clients if client.location is not None)
        clients_with_health = sum(1 for client in clients if client.healthSignals is not None)

        def delta_seconds(start: int | None, end: int | None) -> int | None:
            if start is None or end is None:
                return None
            return max(0, round((end - start) / 1000))

        return {
            "dispatchSeconds": delta_seconds(designated_ts, dispatch_done_ts),
            "cprStartSeconds": delta_seconds(designated_ts, cpr_ts),
            "aedPickupSeconds": delta_seconds(designated_ts, aed_picked_ts),
            "aedDeliverySeconds": delta_seconds(designated_ts, aed_delivered_ts),
            "ambulanceArriveSeconds": delta_seconds(designated_ts, ambulance_ts),
            "logCount": len(state.logs),
            "participantCount": len(clients),
            "aedSiteCount": len(aed_sites),
            "availableAedSiteCount": available_aed_count,
            "roleAssignmentCompleteness": round(assigned_count / 3, 3),
            "clientsWithLocation": clients_with_location,
            "locationCoveragePercent": round((clients_with_location / len(clients)) * 100, 1) if clients else 0,
            "clientsWithHealthSignals": clients_with_health,
            "healthCoveragePercent": round((clients_with_health / len(clients)) * 100, 1) if clients else 0,
            "runnerRouteMeters": runner_route_meters,
            "dispatchSourceIsFallback": 1 if state.dispatchSource == "fallback" else 0,
        }

    @staticmethod
    def _csv_text(rows: list[dict], fieldnames: list[str]) -> str:
        buffer = io.StringIO()
        buffer.write("\ufeff")
        writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()

    @staticmethod
    def _timeline_export_fields() -> list[str]:
        return ["ts", "tsIso", "elapsedSec", "eventType", "actorUserId", "role", "msg"]

    @staticmethod
    def _observer_record_fields() -> list[str]:
        return ["roundId", "incidentId", "item", "systemValue", "observerValue", "score1to5", "notes"]

    @staticmethod
    def _pre_experiment_round_summary_fields() -> list[str]:
        return [
            "roundId",
            "incidentId",
            "generatedAtIso",
            "phase",
            "patientCode",
            "primeCode",
            "runnerCode",
            "guideCode",
            "dispatchSource",
            "dispatchSeconds",
            "cprStartSeconds",
            "aedPickupSeconds",
            "aedDeliverySeconds",
            "ambulanceArriveSeconds",
            "participantCount",
            "aedSiteCount",
            "availableAedSiteCount",
            "roleAssignmentCompleteness",
            "locationCoveragePercent",
            "healthCoveragePercent",
            "runnerRouteMeters",
            "observerName",
            "scenarioLocation",
            "roleAssignmentClarityScore",
            "taskInstructionClarityScore",
            "stressOperabilityScore",
            "dispatchReasonablenessScore",
            "aedPromptUsefulnessScore",
            "notes",
        ]

    def _pre_experiment_round_summary_rows(self, export: ExperimentExportResponse) -> list[dict]:
        participant_map = self._participant_aliases(export)
        metrics = export.metrics
        return [
            {
                "roundId": "R001",
                "incidentId": export.incidentId,
                "generatedAtIso": self._iso_timestamp(export.generatedAt),
                "phase": export.phase,
                "patientCode": participant_map.get(export.patientUserId or "", export.patientUserId or ""),
                "primeCode": participant_map.get(export.assignments.get("PRIME") or "", export.assignments.get("PRIME") or ""),
                "runnerCode": participant_map.get(export.assignments.get("RUNNER") or "", export.assignments.get("RUNNER") or ""),
                "guideCode": participant_map.get(export.assignments.get("GUIDE") or "", export.assignments.get("GUIDE") or ""),
                "dispatchSource": export.dispatchSource or "",
                "dispatchSeconds": metrics.get("dispatchSeconds"),
                "cprStartSeconds": metrics.get("cprStartSeconds"),
                "aedPickupSeconds": metrics.get("aedPickupSeconds"),
                "aedDeliverySeconds": metrics.get("aedDeliverySeconds"),
                "ambulanceArriveSeconds": metrics.get("ambulanceArriveSeconds"),
                "participantCount": metrics.get("participantCount"),
                "aedSiteCount": metrics.get("aedSiteCount"),
                "availableAedSiteCount": metrics.get("availableAedSiteCount"),
                "roleAssignmentCompleteness": metrics.get("roleAssignmentCompleteness"),
                "locationCoveragePercent": metrics.get("locationCoveragePercent"),
                "healthCoveragePercent": metrics.get("healthCoveragePercent"),
                "runnerRouteMeters": metrics.get("runnerRouteMeters"),
                "observerName": "",
                "scenarioLocation": "",
                "roleAssignmentClarityScore": "",
                "taskInstructionClarityScore": "",
                "stressOperabilityScore": "",
                "dispatchReasonablenessScore": "",
                "aedPromptUsefulnessScore": "",
                "notes": "",
            }
        ]

    def _observer_record_rows(self, export: ExperimentExportResponse) -> list[dict]:
        metrics = export.metrics
        rows = [
            ("round_id", "", "R001"),
            ("scenario_location", "", ""),
            ("observer_name", "", ""),
            ("trigger_to_dispatch_seconds", metrics.get("dispatchSeconds"), ""),
            ("trigger_to_cpr_seconds", metrics.get("cprStartSeconds"), ""),
            ("trigger_to_aed_pickup_seconds", metrics.get("aedPickupSeconds"), ""),
            ("trigger_to_aed_delivery_seconds", metrics.get("aedDeliverySeconds"), ""),
            ("trigger_to_ambulance_handover_seconds", metrics.get("ambulanceArriveSeconds"), ""),
            ("role_assignment_clarity", "", ""),
            ("task_instruction_clarity", "", ""),
            ("stress_scenario_operability", "", ""),
            ("dispatch_reasonableness", "", ""),
            ("aed_location_prompt_usefulness", "", ""),
            ("data_record_completeness", "", ""),
            ("observed_blocking_step", "", ""),
            ("unsafe_or_misleading_copy", "", ""),
            ("participant_open_feedback", "", ""),
        ]
        return [
            {
                "roundId": "R001",
                "incidentId": export.incidentId,
                "item": item,
                "systemValue": "" if system_value is None else system_value,
                "observerValue": observer_value,
                "score1to5": "",
                "notes": "",
            }
            for item, system_value, observer_value in rows
        ]

    def _timeline_export_rows(self, timeline: list[IncidentLogEntry]) -> list[dict]:
        start_ts = timeline[0].ts if timeline else None
        rows: list[dict] = []
        for item in timeline:
            parsed = self._parse_timeline_message(item.msg)
            rows.append(
                {
                    "ts": item.ts,
                    "tsIso": self._iso_timestamp(item.ts),
                    "elapsedSec": round((item.ts - start_ts) / 1000, 3) if start_ts else 0,
                    "eventType": parsed["eventType"],
                    "actorUserId": parsed["actorUserId"],
                    "role": parsed["role"],
                    "msg": item.msg,
                }
            )
        return rows

    @staticmethod
    def _parse_timeline_message(message: str) -> dict[str, str]:
        patterns = [
            (r"^(PRIME|RUNNER|GUIDE) assigned \(([^)]+)\)", "ROLE_ASSIGNED"),
            (r"^(PRIME|RUNNER|GUIDE) joined \(([^)]+)\)", "ROLE_JOINED"),
            (r"^(PRIME|RUNNER|GUIDE) auto-joined \(([^)]+)\)", "ROLE_AUTO_JOINED"),
        ]
        for pattern, event_type in patterns:
            match = re.search(pattern, message)
            if match:
                return {"eventType": event_type, "role": match.group(1), "actorUserId": match.group(2)}

        by_action = [
            (r"CPR started by (.+)$", "CPR_STARTED", "PRIME"),
            (r"AED picked by (.+)$", "AED_PICKED", "RUNNER"),
            (r"AED delivered by (.+)$", "AED_DELIVERED", "RUNNER"),
            (r"AED analysis started by (.+)$", "AED_ANALYSIS_STARTED", "PRIME"),
            (r"AED shock delivered by (.+)$", "AED_SHOCK_DELIVERED", "PRIME"),
            (r"Ambulance arrived \(reported by (.+)\)$", "AMBULANCE_ARRIVED", "GUIDE"),
            (r"Handover completed by (.+)$", "HANDOVER_COMPLETED", "GUIDE"),
        ]
        for pattern, event_type, role in by_action:
            match = re.search(pattern, message)
            if match:
                return {"eventType": event_type, "role": role, "actorUserId": match.group(1)}

        patient_match = re.search(r"Patient (?:SOS alerting started|SOS confirmed|designated).*?\(([^)]+)\)", message)
        if patient_match:
            event_type = "PATIENT_SOS" if "SOS" in message else "PATIENT_DESIGNATED"
            return {"eventType": event_type, "role": "PATIENT", "actorUserId": patient_match.group(1)}

        if "AI dispatching started" in message:
            return {"eventType": "DISPATCH_STARTED", "role": "", "actorUserId": ""}
        if "Demo scenario bootstrapped" in message:
            return {"eventType": "DEMO_BOOTSTRAPPED", "role": "", "actorUserId": ""}
        if "AED site updated" in message:
            return {"eventType": "AED_SITE_UPDATED", "role": "", "actorUserId": ""}
        if "Incident reset" in message:
            return {"eventType": "INCIDENT_RESET", "role": "", "actorUserId": ""}
        if "Incident created" in message:
            return {"eventType": "INCIDENT_CREATED", "role": "", "actorUserId": ""}
        return {"eventType": "LOG", "role": "", "actorUserId": ""}

    @staticmethod
    def _dispatch_rationale_export_fields() -> list[str]:
        return [
            "role",
            "userId",
            "participantCode",
            "score",
            "reasons",
            "warnings",
            "distanceToPatientMeters",
            "nearestAedSiteId",
            "distanceToAedMeters",
            "aedToPatientMeters",
        ]

    @staticmethod
    def _dispatch_rationale_export_rows(
        export: ExperimentExportResponse,
        participant_map: dict[str, str],
    ) -> list[dict]:
        return [
            {
                "role": role,
                "userId": decision.userId,
                "participantCode": participant_map.get(decision.userId or "", ""),
                "score": decision.score,
                "reasons": "；".join(decision.reasons),
                "warnings": "；".join(decision.warnings),
                "distanceToPatientMeters": decision.distanceToPatientMeters,
                "nearestAedSiteId": decision.nearestAedSiteId,
                "distanceToAedMeters": decision.distanceToAedMeters,
                "aedToPatientMeters": decision.aedToPatientMeters,
            }
            for role, decision in sorted(export.dispatchRationale.items())
        ]

    def _package_manifest(self, export: ExperimentExportResponse, files: dict[str, str]) -> str:
        entries = []
        for name, content in sorted(files.items()):
            raw = content.encode("utf-8")
            entries.append(
                {
                    "fileName": name,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "lineCount": content.count("\n") + (1 if content else 0),
                }
            )
        manifest = {
            "schemaVersion": 1,
            "packageType": "LifeReflexArc pre-experiment evidence package",
            "incidentId": export.incidentId,
            "generatedAt": export.generatedAt,
            "generatedAtIso": self._iso_timestamp(export.generatedAt),
            "phase": export.phase,
            "privacyGuidance": {
                "publicOrExpertReview": [
                    "experiment_anonymized.json",
                    "clients_anonymized.csv",
                    "timeline.csv",
                    "metrics.csv",
                    "dispatch_rationale.csv",
                    "expert_summary.md",
                    "expert_review_checklist.md",
                    "observer_record_form.csv",
                    "pre_experiment_round_summary.csv",
                ],
                "internalReviewOnly": ["experiment.json", "clients.csv"],
                "note": "Use anonymized files for PPT, expert feedback, and externally shared materials.",
            },
            "verification": {
                "algorithm": "SHA-256",
                "covers": "all package files except manifest.json",
            },
            "fileCountExcludingManifest": len(files),
            "files": entries,
        }
        return json.dumps(manifest, ensure_ascii=False, indent=2)

    @staticmethod
    def _client_export_fields(anonymized: bool = False) -> list[str]:
        base = [
            "userId",
            "displayName",
            "organization",
            "healthCondition",
            "professionIdentity",
            "deviceType",
            "online",
            "assignedRole",
            "patientCandidate",
            "isPatient",
            "locationLabel",
            "locationFloor",
            "locationSource",
            "latitude",
            "longitude",
            "healthSource",
            "healthAuthorizationStatus",
            "heartRateBpm",
            "bloodOxygenPercent",
            "pressureScore",
            "activityLevel",
            "sleepQuality",
            "riskTags",
            "healthNote",
        ]
        if not anonymized:
            return base
        return ["participantCode", *[field for field in base if field not in {"userId", "displayName", "organization", "profileBio", "healthNote"}]]

    @staticmethod
    def _client_export_rows(
        clients: list[ClientInfo],
        participant_map: dict[str, str] | None = None,
        anonymized: bool = False,
    ) -> list[dict]:
        rows: list[dict] = []
        for client in clients:
            health = client.healthSignals
            location = client.location
            participant_code = (participant_map or {}).get(client.userId, client.userId)
            row = {
                "userId": client.userId,
                "displayName": client.displayName,
                "organization": client.organization,
                "healthCondition": client.healthCondition,
                "professionIdentity": client.professionIdentity,
                "profileBio": client.profileBio,
                "deviceType": client.deviceType,
                "online": client.online,
                "assignedRole": client.assignedRole,
                "patientCandidate": client.patientCandidate,
                "isPatient": client.isPatient,
                "locationLabel": location.label if location else None,
                "locationFloor": location.floor if location else None,
                "locationSource": location.source if location else None,
                "latitude": location.latitude if location else None,
                "longitude": location.longitude if location else None,
                "healthSource": health.source if health else None,
                "healthAuthorizationStatus": health.authorizationStatus if health else None,
                "heartRateBpm": health.heartRateBpm if health else None,
                "bloodOxygenPercent": health.bloodOxygenPercent if health else None,
                "pressureScore": health.pressureScore if health else None,
                "activityLevel": health.activityLevel if health else None,
                "sleepQuality": health.sleepQuality if health else None,
                "riskTags": "；".join(health.riskTags) if health else "",
                "healthNote": health.note if health else None,
            }
            if anonymized:
                row = {
                    **row,
                    "participantCode": participant_code,
                    "userId": participant_code,
                    "displayName": participant_code,
                    "organization": "REDACTED",
                    "profileBio": "REDACTED",
                    "healthNote": None,
                }
            rows.append(
                row
            )
        return rows

    @staticmethod
    def _aed_site_export_fields() -> list[str]:
        return [
            "siteId",
            "name",
            "status",
            "accessNotes",
            "lastCheckedTs",
            "locationLabel",
            "locationFloor",
            "locationSource",
            "latitude",
            "longitude",
        ]

    @staticmethod
    def _aed_site_export_rows(aed_sites: list[AedSite]) -> list[dict]:
        return [
            {
                "siteId": site.siteId,
                "name": site.name,
                "status": site.status,
                "accessNotes": site.accessNotes,
                "lastCheckedTs": site.lastCheckedTs,
                "locationLabel": site.location.label,
                "locationFloor": site.location.floor,
                "locationSource": site.location.source,
                "latitude": site.location.latitude,
                "longitude": site.location.longitude,
            }
            for site in aed_sites
        ]

    @staticmethod
    def _experiment_readme(export: ExperimentExportResponse) -> str:
        return f"""# 生命反射弧预实验证据包

事件编号：{export.incidentId}
导出时间戳：{export.generatedAt}
事件阶段：{export.phase}
患者终端：{export.patientUserId or "未指定"}
调度来源：{export.dispatchSource or "未记录"}

## 文件说明

- `experiment.json`：完整结构化导出，保留事件、终端、AED、调度依据和健康摘要。
- `experiment_anonymized.json`：匿名化结构化导出，用于专家反馈、PPT 和对外材料。
- `expert_summary.md`：专家/指导教师可快速阅读的预实验摘要。
- `expert_review_checklist.md`：专家现场复核清单，覆盖医学场景、流程安全、AI 分派和数据边界。
- `timeline.csv`：事件时间线，适合直接导入 Excel。
- `clients.csv`：参与终端画像、位置、角色和 OPPO/mock 健康摘要。
- `clients_anonymized.csv`：匿名化参与者表，隐藏 userId、姓名、组织和个人简介。
- `aed_sites.csv`：AED 点位与访问备注。
- `dispatch_rationale.csv`：AI/规则分派评分、理由、距离和风险提示。
- `metrics.csv`：响应耗时、AED 取送、交接等预实验指标。
- `observer_record_form.csv`：观察员补充记录表，用于填写系统无法自动采集的现场行为、评分和开放反馈。
- `pre_experiment_round_summary.csv`：单轮预实验汇总行，便于把多轮 ZIP 的核心指标合并到 Excel 做描述性统计。
- `manifest.json`：文件清单、SHA256 校验、生成时间、匿名化使用建议和内部复核文件说明。

## 使用建议

该包用于医创赛低成本预实验记录、PPT 截图依据和专家反馈前的材料整理。对外材料优先使用 `experiment_anonymized.json`、`clients_anonymized.csv`、`expert_summary.md`、`expert_review_checklist.md`、`observer_record_form.csv` 和 `pre_experiment_round_summary.csv`；完整 `experiment.json` 与 `clients.csv` 仅建议内部复核使用。健康摘要中 `mock` 来源表示演示/预实验模拟数据，不应被表述为真实临床诊断结论。
"""

    def _participant_aliases(self, export: ExperimentExportResponse) -> dict[str, str]:
        aliases: dict[str, str] = {}
        if export.patientUserId:
            aliases[export.patientUserId] = "P001"

        for role in ("PRIME", "RUNNER", "GUIDE"):
            user_id = export.assignments.get(role)
            if user_id and user_id not in aliases:
                aliases[user_id] = f"R{len([value for value in aliases.values() if value.startswith('R')]) + 1:03d}-{role}"

        for client in export.clients:
            if client.userId not in aliases:
                aliases[client.userId] = f"C{len(aliases) + 1:03d}"
        return aliases

    @staticmethod
    def _replace_participant_ids(value: object, participant_map: dict[str, str]) -> object:
        if isinstance(value, str):
            updated = value
            for raw, alias in sorted(participant_map.items(), key=lambda item: len(item[0]), reverse=True):
                updated = updated.replace(raw, alias)
            return updated
        if isinstance(value, list):
            return [IncidentService._replace_participant_ids(item, participant_map) for item in value]
        if isinstance(value, dict):
            return {
                key: IncidentService._replace_participant_ids(item, participant_map)
                for key, item in value.items()
            }
        return value

    def _anonymized_experiment_payload(self, export: ExperimentExportResponse) -> tuple[dict, dict[str, str]]:
        participant_map = self._participant_aliases(export)
        payload = export.model_dump(mode="json")
        anonymized = self._replace_participant_ids(payload, participant_map)
        if not isinstance(anonymized, dict):
            return payload, participant_map

        anonymized["patientUserId"] = participant_map.get(export.patientUserId or "", export.patientUserId)
        anonymized["assignments"] = {
            role: participant_map.get(user_id or "", user_id)
            for role, user_id in export.assignments.items()
        }
        anonymized["participantMap"] = [
            {
                "participantCode": participant_map[client.userId],
                "role": "PATIENT" if client.userId == export.patientUserId else client.assignedRole,
                "deviceType": client.deviceType,
                "professionIdentity": client.professionIdentity,
                "healthCondition": client.healthCondition,
                "healthSource": client.healthSignals.source if client.healthSignals else None,
                "riskTags": client.healthSignals.riskTags if client.healthSignals else [],
            }
            for client in export.clients
        ]
        for client in anonymized.get("clients", []):
            if not isinstance(client, dict):
                continue
            participant_code = participant_map.get(str(client.get("userId")), str(client.get("userId")))
            client["participantCode"] = participant_code
            client["userId"] = participant_code
            client["displayName"] = participant_code
            client["organization"] = "REDACTED"
            client["profileBio"] = "REDACTED"
            if isinstance(client.get("healthSignals"), dict):
                client["healthSignals"]["note"] = None
        return anonymized, participant_map

    @staticmethod
    def _format_metric(value: int | float | None) -> str:
        return "--" if value is None else f"{value}s"

    def _expert_summary(self, export: ExperimentExportResponse, participant_map: dict[str, str]) -> str:
        assignments = {
            role: participant_map.get(user_id or "", user_id or "未分派")
            for role, user_id in export.assignments.items()
        }
        metrics = export.metrics
        return f"""# 生命反射弧预实验专家摘要

## 事件概况

- 事件编号：{export.incidentId}
- 事件阶段：{export.phase}
- 患者代号：{participant_map.get(export.patientUserId or "", export.patientUserId or "未指定")}
- 调度来源：{export.dispatchSource or "未记录"}
- 参与终端数：{len(export.clients)}
- AED 点位数：{len(export.aedSites)}

## 角色分派

- PRIME 核心施救：{assignments.get("PRIME", "未分派")}
- RUNNER AED 保障：{assignments.get("RUNNER", "未分派")}
- GUIDE 环境清障/接车：{assignments.get("GUIDE", "未分派")}

## 关键耗时

- 调度耗时：{self._format_metric(metrics.get("dispatchSeconds"))}
- CPR 开始耗时：{self._format_metric(metrics.get("cprStartSeconds"))}
- AED 取出耗时：{self._format_metric(metrics.get("aedPickupSeconds"))}
- AED 送达耗时：{self._format_metric(metrics.get("aedDeliverySeconds"))}
- 救护接管耗时：{self._format_metric(metrics.get("ambulanceArriveSeconds"))}
- 事件日志数：{metrics.get("logCount", 0)}

## 数据使用边界

本摘要用于医创赛低成本预实验、专家反馈和产品可行性讨论。OPPO 健康数据若来源为 `mock`，仅代表演示闭环中的模拟健康摘要，不可用于真实医疗诊断或疗效结论。
"""

    def _expert_review_checklist(
        self,
        export: ExperimentExportResponse,
        participant_map: dict[str, str],
    ) -> str:
        assignments = {
            role: participant_map.get(user_id or "", user_id or "未分派")
            for role, user_id in export.assignments.items()
        }
        metrics = export.metrics
        generated_at = self._iso_timestamp(export.generatedAt)
        return f"""# 生命反射弧专家现场复核清单

事件编号：{export.incidentId}
导出时间：{generated_at}
患者代号：{participant_map.get(export.patientUserId or "", export.patientUserId or "未指定")}
角色分派：PRIME={assignments.get("PRIME", "未分派")}，RUNNER={assignments.get("RUNNER", "未分派")}，GUIDE={assignments.get("GUIDE", "未分派")}

## 一、建议审阅材料

- [ ] Web 调度台首页、演示准备度、四端在线状态。
- [ ] 患者 SOS 触发与二次确认流程。
- [ ] PRIME/RUNNER/GUIDE 分派结果和解释。
- [ ] 移动 Web 或 Android 任务页的当前动作、AED 位置、现场时间线。
- [ ] 证据包中的 `experiment_anonymized.json`、`clients_anonymized.csv`、`timeline.csv`、`metrics.csv`。
- [ ] `manifest.json` 的生成时间、SHA-256 校验和匿名化文件建议。

## 二、关键指标快照

| 指标 | 系统记录 |
| --- | --- |
| 调度耗时 | {self._format_metric(metrics.get("dispatchSeconds"))} |
| CPR 开始耗时 | {self._format_metric(metrics.get("cprStartSeconds"))} |
| AED 取出耗时 | {self._format_metric(metrics.get("aedPickupSeconds"))} |
| AED 送达耗时 | {self._format_metric(metrics.get("aedDeliverySeconds"))} |
| 救护接管耗时 | {self._format_metric(metrics.get("ambulanceArriveSeconds"))} |
| 角色完整度 | {metrics.get("roleAssignmentCompleteness", "--")} |
| 定位覆盖率 | {metrics.get("locationCoveragePercent", "--")}% |
| 健康摘要覆盖率 | {metrics.get("healthCoveragePercent", "--")}% |

## 三、专家重点判断

- [ ] 医学场景是否聚焦公共场所疑似心脏骤停的真实协同问题。
- [ ] CPR/AED/救护接应提示是否适合演练和培训语境，是否存在不安全或过度医疗化表述。
- [ ] PRIME/RUNNER/GUIDE 三类角色分工是否能降低现场混乱。
- [ ] AI/规则分派是否合理体现人员能力、距离、AED 可达性和健康风险。
- [ ] 调度解释是否足够清晰，能否被非技术评委和医学专家理解。
- [ ] 证据包是否支持低成本预实验归档、匿名化审阅和后续 PPT 论证。

## 四、现场补充记录

请结合 `observer_record_form.csv` 填写系统无法自动采集的信息，例如参与者迟疑点、现场沟通问题、误触发、界面阅读困难、专家认为应修改的医学措辞。

## 五、安全边界

本系统为模拟急救协同、训练复盘和预实验验证工具。它不替代拨打 120、AED 语音提示、专业医护判断，也不用于真实医疗诊断或疗效证明。
"""

    def _assigned_role_for(self, user_id: str) -> str | None:
        if not self.current_incident_id or self.current_incident_id not in self.incidents:
            return None
        state = self.incidents[self.current_incident_id]
        for role_name in ("PRIME", "RUNNER", "GUIDE"):
            if getattr(state.roles, role_name).userId == user_id:
                return role_name
        return None

    def _is_patient(self, user_id: str) -> bool:
        if not self.current_incident_id or self.current_incident_id not in self.incidents:
            return False
        return self.incidents[self.current_incident_id].patientUserId == user_id

    @staticmethod
    def _ensure_role_actor(state: IncidentState, role_name: str, user_id: str) -> None:
        role_state = getattr(state.roles, role_name)
        if role_state.userId != user_id:
            raise HTTPException(status_code=403, detail=f"User is not assigned to {role_name}")

    @staticmethod
    def _ensure_role_status(current_status: str | None, allowed: set[str], role_name: str) -> None:
        normalized_status = current_status or ""
        if normalized_status not in allowed:
            raise HTTPException(
                status_code=409,
                detail=f"{role_name} cannot perform this action from status {normalized_status}",
            )

    @staticmethod
    def _is_patient_candidate(health_condition: str, profile_bio: str) -> bool:
        text = f"{health_condition} {profile_bio}".lower()
        markers = ("心脏", "冠心病", "骤停风险", "重点监测", "患者侧")
        return any(marker in text for marker in markers)
