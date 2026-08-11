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
    AiTaskState,
    AuditEvent,
    AutoJoinResponse,
    ClientInfo,
    CreateIncidentResponse,
    demoBootstrapResponse,
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
from app.services.ai_tasks import AiTaskPlanner
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
        sos_duration_sec: int = 5,
        dispatch_delay_sec: int = 3,
        siliconflow_api_key: str | None = None,
        siliconflow_model: str = "Qwen/Qwen2-7B-Instruct",
        siliconflow_base_url: str = "https://api.siliconflow.cn/v1",
        siliconflow_timeout_sec: int = 8,
        dispatch_llm_budget_sec: float = 1.0,
        local_model_base_url: str | None = None,
        local_model_name: str = "Qwen/Qwen2.5-7B-Instruct",
        local_model_timeout_sec: int = 30,
        prefer_local_model: bool = True,
        map_provider: str = "demo",
        amap_service_key: str | None = None,
        baidu_service_ak: str | None = None,
        map_distance_timeout_sec: int = 3,
        push_provider: str = "websocket",
        notification_provider: NotificationProvider | None = None,
        deepseek_api_key: str | None = None,
        deepseek_model: str = "deepseek-v4-flash",
        deepseek_base_url: str = "https://api.deepseek.com",
        deepseek_timeout_sec: int = 15,
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
            baidu_service_ak=baidu_service_ak,
            timeout_sec=map_distance_timeout_sec,
        )
        self.notification_provider = notification_provider or WebSocketFallbackNotificationProvider(
            provider=push_provider,
            send_state=self._send_websocket_state,
        )
        self.ai_task_planner = AiTaskPlanner(
            api_key=deepseek_api_key,
            model=deepseek_model,
            base_url=deepseek_base_url,
            timeout_sec=deepseek_timeout_sec,
            spatial_provider=self.spatial_provider,
        )
        self.dispatch_planner = DispatchPlanner(
            api_key=siliconflow_api_key,
            model=siliconflow_model,
            base_url=siliconflow_base_url,
            timeout_sec=siliconflow_timeout_sec,
            llm_budget_sec=dispatch_llm_budget_sec,
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

    # ---------- AI 临时任务（DeepSeek 解析 + 硬算法匹配） ----------
    def _mainline_busy_user_ids(self, state: IncidentState) -> set[str]:
        busy: set[str] = set()
        for role_name in ("PRIME", "RUNNER", "GUIDE"):
            role_state = getattr(state.roles, role_name)
            if role_state.userId and role_state.status and role_state.status not in ("", "PENDING"):
                busy.add(role_state.userId)
        return busy

    def _ai_task_busy_user_ids(self, state: IncidentState) -> set[str]:
        busy = self._mainline_busy_user_ids(state)
        for task in state.aiTasks.values():
            if task.status in ("PENDING", "ACTIVE") and task.runnerUserId:
                busy.add(task.runnerUserId)
        return busy

    def _task_target_location(self, state: IncidentState, task: AiTaskState) -> GeoPoint | None:
        if task.locationLabel:
            for site in state.aedSites:
                if task.locationLabel in (site.name, site.siteId) or (site.name or "") in (task.locationLabel or ""):
                    return site.location
        patient = self.clients.get(state.patientUserId or "")
        if patient and patient.location:
            return patient.location
        creator = self.clients.get(task.createdBy)
        return creator.location if creator and creator.location else None

    def _refresh_task_scores(self, state: IncidentState, task: AiTaskState) -> bool:
        busy = self._ai_task_busy_user_ids(state)
        target = self._task_target_location(state, task)
        changed = False
        for client in self.clients.values():
            if client.userId not in task.assignableUserIds:
                continue
            is_busy = client.userId in busy and not (
                task.status == "ACTIVE" and task.runnerUserId == client.userId
            )
            result = self.ai_task_planner.match_score(
                client,
                task.requiredSkill,
                target,
                is_busy=is_busy,
                cooperation_bonus=0,
            )
            old = task.matchScores.get(client.userId)
            if old != result.score:
                changed = True
                task.matchScores[client.userId] = result.score
                task.matchReasons[client.userId] = result.reasons
        if changed:
            task.scoreRev += 1
            task.updatedAt = self._now_ms()
        return changed

    def _refresh_all_task_scores(self, incident_id: str) -> bool:
        state = self.incidents.get(incident_id)
        if state is None or not state.aiTasks:
            return False
        changed = False
        for task in state.aiTasks.values():
            if task.status in ("PENDING", "ACTIVE"):
                changed = self._refresh_task_scores(state, task) or changed
        if changed:
            self._persist()
        return changed

    async def refresh_ai_task_scores_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(3)
                for incident_id in list(self.incidents.keys()):
                    if self._refresh_all_task_scores(incident_id):
                        await self._broadcast_state_async(incident_id)
            except asyncio.CancelledError:
                break
            except Exception:
                pass

    async def create_ai_task(self, incident_id: str, requester_user_id: str, message: str) -> list[AiTaskState]:
        state = self.incidents.get(incident_id)
        if state is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        requester = self.clients.get(requester_user_id)
        if requester is None:
            raise HTTPException(status_code=404, detail="Requester client not registered")
        patient = self.clients.get(state.patientUserId or "")
        patient_note = patient.profileBio if patient else None
        specs = await asyncio.to_thread(self.ai_task_planner.parse_tasks, message, requester, patient_note)
        now = self._now_ms()
        busy = self._ai_task_busy_user_ids(state)
        candidates = [
            client
            for client in self.clients.values()
            if client.userId != requester_user_id
            and client.online
            and not client.isPatient
            and client.userId not in busy
            and not self.ai_task_planner.health_risk(client)
        ]
        tasks: list[AiTaskState] = []
        for spec in specs:
            task = AiTaskState(
                taskId=f"ai-{uuid.uuid4().hex[:8]}",
                title=spec.title,
                description=spec.description,
                requiredSkill=spec.required_skill,
                priority=spec.priority,
                locationLabel=spec.location_label,
                createdBy=requester_user_id,
                createdRole=requester.assignedRole or "",
                createdAt=now,
                updatedAt=now,
                requires=spec.requires or [],
                statusLogs=[{"ts": now, "type": "CREATED", "userId": requester_user_id, "note": spec.description}],
            )
            task.assignableUserIds = [client.userId for client in candidates]
            self._refresh_task_scores(state, task)
            task.assignableUserIds = sorted(
                task.assignableUserIds,
                key=lambda uid: task.matchScores.get(uid, -1000),
                reverse=True,
            )
            task.targetLocation = self._task_target_location(state, task)
            state.aiTasks[task.taskId] = task
            tasks.append(task)
        for task in tasks:
            state.logs.append(IncidentLogEntry(ts=now, msg=f"AI 任务创建：{task.title}（发起 {requester.displayName}）"))
        self._persist()
        await self._broadcast_state_async(incident_id)
        return tasks

    async def accept_ai_task(self, incident_id: str, task_id: str, user_id: str) -> AiTaskState:
        state = self.incidents.get(incident_id)
        if state is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        task = state.aiTasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status != "PENDING":
            raise HTTPException(status_code=409, detail=f"任务当前状态 {task.status}，不可接单")
        if user_id not in task.assignableUserIds:
            raise HTTPException(status_code=409, detail="该终端不在任务候选名单中")
        if user_id in self._ai_task_busy_user_ids(state):
            raise HTTPException(status_code=409, detail="该终端当前繁忙，无法接单")
        now = self._now_ms()
        client = self.clients.get(user_id)
        display = client.displayName if client else user_id
        task.status = "ACTIVE"
        task.runnerUserId = user_id
        task.supportUserIds = [uid for uid in task.assignableUserIds if uid != user_id]
        task.acceptedAt = now
        task.updatedAt = now
        task.statusLogs.append({"ts": now, "type": "ACCEPTED", "userId": user_id, "note": f"{display} 接单成为 runner"})
        state.logs.append(IncidentLogEntry(ts=now, msg=f"AI 任务接单：{task.title} → {display}"))
        self._refresh_task_scores(state, task)
        self._persist()
        await self._broadcast_state_async(incident_id)
        return task

    async def release_ai_task(self, incident_id: str, task_id: str, user_id: str) -> AiTaskState:
        state = self.incidents.get(incident_id)
        if state is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        task = state.aiTasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status != "ACTIVE":
            raise HTTPException(status_code=409, detail=f"任务当前状态 {task.status}，不可放单")
        if task.runnerUserId != user_id:
            raise HTTPException(status_code=409, detail="仅当前 runner 可放单")
        now = self._now_ms()
        task.status = "PENDING"
        task.releasedAt = now
        task.assignableUserIds = list(dict.fromkeys(task.assignableUserIds + task.supportUserIds + [user_id]))
        task.supportUserIds = []
        task.runnerUserId = None
        task.acceptedAt = None
        task.updatedAt = now
        task.statusLogs.append({"ts": now, "type": "RELEASED", "userId": user_id, "note": "runner 放单，任务重新开放"})
        state.logs.append(IncidentLogEntry(ts=now, msg=f"AI 任务放单：{task.title} 重新开放接单"))
        self._refresh_task_scores(state, task)
        self._persist()
        await self._broadcast_state_async(incident_id)
        return task

    async def complete_ai_task(self, incident_id: str, task_id: str, user_id: str) -> AiTaskState:
        state = self.incidents.get(incident_id)
        if state is None:
            raise HTTPException(status_code=404, detail="Incident not found")
        task = state.aiTasks.get(task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        if task.status != "ACTIVE":
            raise HTTPException(status_code=409, detail=f"任务当前状态 {task.status}，不可完成")
        if task.runnerUserId != user_id:
            raise HTTPException(status_code=409, detail="仅当前 runner 可完成")
        now = self._now_ms()
        task.status = "COMPLETED"
        task.completedAt = now
        task.updatedAt = now
        task.statusLogs.append({"ts": now, "type": "COMPLETED", "userId": user_id, "note": "任务完成"})
        state.logs.append(IncidentLogEntry(ts=now, msg=f"AI 任务完成：{task.title}"))
        self._persist()
        await self._broadcast_state_async(incident_id)
        return task

    def list_demo_terminals(self) -> list[dict]:
        terminals: list[dict] = []
        for client in self.list_clients():
            terminals.append(
                {
                    "userId": client.userId,
                    "displayName": client.displayName,
                    "organization": client.organization,
                    "online": client.online,
                    "isPatient": client.isPatient,
                    "assignedRole": client.assignedRole,
                    "location": client.location.model_dump(mode="json") if client.location else None,
                    "deviceType": client.deviceType,
                }
            )
        return terminals

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
        return await self._designate_patient_for_state(state, patient_user_id, source_label, cancel_sos_timer)

    async def _designate_patient_for_state(
        self,
        state: IncidentState,
        patient_user_id: str,
        source_label: str,
        cancel_sos_timer: bool,
    ) -> DispatchResponse:
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

        clients = self.list_clients()
        aed_sites = self.list_aed_sites()
        dispatch_task = asyncio.create_task(
            asyncio.to_thread(self.dispatch_planner.assign_roles, patient_user_id, clients, aed_sites)
        )
        try:
            assignments, source, rationale = await asyncio.wait_for(
                asyncio.shield(dispatch_task),
                timeout=max(0.05, self.dispatch_planner.llm_budget_sec),
            )
        except asyncio.TimeoutError:
            assignments, source, rationale = self.dispatch_planner.fallback_assign_roles(
                patient_user_id,
                clients,
                aed_sites,
            )
            state.logs.append(
                IncidentLogEntry(ts=self._now_ms(), msg="AI dispatch timed out; static fallback assigned")
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
        if current.phase in {"CREATED", "DISPATCHING"}:
            raise HTTPException(status_code=409, detail="请先由患者端启动 SOS，系统分派任务后再接单")
        self._touch_client(user_id)

        for role_name in ("PRIME", "RUNNER", "GUIDE"):
            role_state = getattr(current.roles, role_name)
            if role_state.userId == user_id:
                if role_state.status == "ASSIGNED":
                    role_state.status = "JOINED"
                    current.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"{role_name} auto-joined ({user_id})"))
                    self._persist()
                    await self._broadcast_state_async(incident_id)
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
        if state.phase in {"CREATED", "DISPATCHING"}:
            raise HTTPException(status_code=409, detail="请先由患者端启动 SOS，系统分派任务后再接单")

        normalized_role = role.upper()
        if normalized_role not in {"PRIME", "RUNNER", "GUIDE"}:
            raise HTTPException(status_code=400, detail="Invalid role")
        self._touch_client(user_id)

        role_state = getattr(state.roles, normalized_role)
        if role_state.userId == user_id and role_state.status != "ASSIGNED":
            return MutationResponse(incidentId=incident_id, phase=state.phase)
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
            if self._is_role_action_already_recorded(state, "PRIME", normalized_action):
                return MutationResponse(incidentId=incident_id, phase=state.phase)
            self._ensure_role_status(state.roles.PRIME.status, {"ASSIGNED", "JOINED", "CPR_STARTED"}, "PRIME")
            self._advance_phase(state, "CPR")
            state.roles.PRIME.status = "CPR_STARTED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"CPR started by {user_id}"))
        elif normalized_action == "AED_ANALYSIS_STARTED":
            self._ensure_role_actor(state, "PRIME", user_id)
            if self._is_role_action_already_recorded(state, "PRIME", normalized_action):
                return MutationResponse(incidentId=incident_id, phase=state.phase)
            self._ensure_role_status(
                state.roles.PRIME.status,
                {"CPR_STARTED", "AED_ANALYZING", "AED_SHOCK_DELIVERED"},
                "PRIME",
            )
            self._ensure_role_status(state.roles.RUNNER.status, {"AED_DELIVERED"}, "RUNNER")
            self._advance_phase(state, "AED_ANALYZING")
            state.roles.PRIME.status = "AED_ANALYZING"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED analysis started by {user_id}"))
        elif normalized_action == "AED_SHOCK_DELIVERED":
            self._ensure_role_actor(state, "PRIME", user_id)
            if self._is_role_action_already_recorded(state, "PRIME", normalized_action):
                return MutationResponse(incidentId=incident_id, phase=state.phase)
            self._ensure_role_status(state.roles.PRIME.status, {"AED_ANALYZING", "AED_SHOCK_DELIVERED"}, "PRIME")
            self._ensure_role_status(state.roles.RUNNER.status, {"AED_DELIVERED"}, "RUNNER")
            self._advance_phase(state, "SHOCK_DELIVERED")
            state.roles.PRIME.status = "AED_SHOCK_DELIVERED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED shock delivered by {user_id}"))
        elif normalized_action == "AED_PICKED":
            self._ensure_role_actor(state, "RUNNER", user_id)
            if self._is_role_action_already_recorded(state, "RUNNER", normalized_action):
                return MutationResponse(incidentId=incident_id, phase=state.phase)
            self._ensure_role_status(state.roles.RUNNER.status, {"ASSIGNED", "JOINED", "AED_PICKED"}, "RUNNER")
            self._advance_phase(state, "AED_PICKED")
            state.roles.RUNNER.status = "AED_PICKED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED picked by {user_id}"))
        elif normalized_action == "AED_DELIVERED":
            self._ensure_role_actor(state, "RUNNER", user_id)
            if self._is_role_action_already_recorded(state, "RUNNER", normalized_action):
                return MutationResponse(incidentId=incident_id, phase=state.phase)
            self._ensure_role_status(state.roles.RUNNER.status, {"AED_PICKED", "AED_DELIVERED"}, "RUNNER")
            self._advance_phase(state, "AED_DELIVERED")
            state.roles.RUNNER.status = "AED_DELIVERED"
            state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg=f"AED delivered by {user_id}"))
        elif normalized_action == "AMBULANCE_ARRIVED":
            self._ensure_role_actor(state, "GUIDE", user_id)
            if self._is_role_action_already_recorded(state, "GUIDE", normalized_action):
                if state.phase not in {"HANDOVER", "ARCHIVED"}:
                    state.phase = "HANDOVER"
                    state.logs.append(
                        IncidentLogEntry(ts=self._now_ms(), msg=f"Ambulance handover state repaired by {user_id}")
                    )
                    self._persist()
                    await self._broadcast_state_async(incident_id)
                return MutationResponse(incidentId=incident_id, phase=state.phase)
            self._ensure_role_status(
                state.roles.GUIDE.status,
                {"ASSIGNED", "JOINED", "AMBULANCE_ARRIVED"},
                "GUIDE",
            )
            self._advance_phase(state, "HANDOVER")
            state.roles.GUIDE.status = "AMBULANCE_ARRIVED"
            state.logs.append(
                IncidentLogEntry(ts=self._now_ms(), msg=f"Ambulance arrived (reported by {user_id})")
            )
        elif normalized_action == "HANDOVER_COMPLETED":
            participants = {
                state.patientUserId,
                state.roles.PRIME.userId,
                state.roles.RUNNER.userId,
                state.roles.GUIDE.userId,
            }
            if user_id not in participants:
                raise HTTPException(status_code=403, detail="Only active participants can complete handover")
            if state.phase not in {"HANDOVER", "ARCHIVED"}:
                if state.roles.GUIDE.status != "AMBULANCE_ARRIVED":
                    raise HTTPException(status_code=409, detail="Handover not ready")
                state.phase = "HANDOVER"
                state.logs.append(
                    IncidentLogEntry(ts=self._now_ms(), msg=f"Ambulance handover state repaired before archive by {user_id}")
                )
            if state.phase == "ARCHIVED" and state.roles.GUIDE.status == "HANDOVER_COMPLETED":
                return MutationResponse(incidentId=incident_id, phase=state.phase)
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

    async def bootstrap_demo(self) -> demoBootstrapResponse:
        self.clients = {}
        self.aed_sites = {}
        incident_id = self._new_incident()
        self.current_incident_id = incident_id

        demo_locations = {
            "patient": GeoPoint(latitude=39.916156, longitude=116.465571, label="交通和苑 8 号楼前广场（患者现场）", floor="1F", source="demo"),
            "doctor": GeoPoint(latitude=39.916030, longitude=116.466039, label="交通和苑中心花园", floor="1F", source="demo"),
            "runner": GeoPoint(latitude=39.915868, longitude=116.466566, label="交通和苑物业用房（AED 保障）", floor="1F", source="demo"),
            "guide": GeoPoint(latitude=39.915509, longitude=116.464892, label="交通和苑北门出入口", floor="1F", source="demo"),
            "runner2": GeoPoint(latitude=39.916320, longitude=116.465900, label="交通和苑 8 号楼西侧广场", floor="1F", source="demo"),
            "runner3": GeoPoint(latitude=39.914900, longitude=116.466800, label="交通和苑东门外", floor="1F", source="demo"),
            "aed1": GeoPoint(latitude=39.915122, longitude=116.465922, label="交通和苑南门岗亭 AED 箱", floor="1F", source="demo"),
            "aed2": GeoPoint(latitude=39.916533, longitude=116.466741, label="交通和苑车库入口 AED 箱", floor="B1", source="demo"),
        }

        demo_health = {
            "patient": HealthSignalSummary(
                source="mock",
                authorizationStatus="sample",
                heartRateBpm=118,
                bloodOxygenPercent=92,
                pressureScore=82,
                activityLevel="low",
                sleepQuality="poor",
                riskTags=["tachycardia", "low_spo2", "high_pressure"],
                note="健康摘要样例：高风险患者端",
            ),
            "doctor": HealthSignalSummary(
                source="mock",
                authorizationStatus="sample",
                heartRateBpm=76,
                bloodOxygenPercent=98,
                pressureScore=35,
                activityLevel="normal",
                sleepQuality="good",
                riskTags=[],
                note="健康摘要样例：稳定专业施救者",
            ),
            "runner": HealthSignalSummary(
                source="mock",
                authorizationStatus="sample",
                heartRateBpm=84,
                bloodOxygenPercent=99,
                pressureScore=28,
                activityLevel="high",
                sleepQuality="good",
                riskTags=[],
                note="健康摘要样例：高机动响应者",
            ),
            "runner2": HealthSignalSummary(
                source="mock",
                authorizationStatus="sample",
                heartRateBpm=72,
                bloodOxygenPercent=99,
                pressureScore=22,
                activityLevel="high",
                sleepQuality="good",
                riskTags=[],
                note="健康摘要样例：高机动志愿者",
            ),
            "runner3": HealthSignalSummary(
                source="mock",
                authorizationStatus="sample",
                heartRateBpm=86,
                bloodOxygenPercent=96,
                pressureScore=58,
                activityLevel="normal",
                sleepQuality="fair",
                riskTags=[],
                note="健康摘要样例：一般协助者",
            ),
            "guide": HealthSignalSummary(
                source="mock",
                authorizationStatus="sample",
                heartRateBpm=80,
                bloodOxygenPercent=97,
                pressureScore=44,
                activityLevel="normal",
                sleepQuality="fair",
                riskTags=[],
                note="健康摘要样例：稳定清障接驳者",
            ),
        }

        self.register_client("demo-patient", "冠心病患者", "示范社区", "存在心脏骤停风险", "患者侧", "多年冠心病病史，需要重点监护", "ANDROID", demo_locations["patient"], demo_health["patient"])
        self.register_client("demo-prime", "张医生", "市医院急救科", "身体状态一般", "医生 / 专业急救人员", "急救科医生，熟悉 CPR 和 AED 处置", "ANDROID", demo_locations["doctor"], demo_health["doctor"])
        self.register_client("demo-runner", "小区物业小周", "交通和苑物业", "身体素质良好", "有一定急救常识", "小区物业员工，熟悉各楼栋和单元动线，负责日常巡检", "ANDROID", demo_locations["runner"], demo_health["runner"])
        self.register_client("demo-guide", "安保老刘", "交通和苑安保部", "身体状态一般", "安保 / 物业 / 场地协调人员", "熟悉小区出入口、单元门和救护车通道", "ANDROID", demo_locations["guide"], demo_health["guide"])
        self.register_client("demo-runner2", "志愿者小王", "小区志愿者服务队", "身体素质优秀", "退伍军人 / 志愿者", "退伍军人，体能出色，跑得快，熟悉小区各栋楼位置，可快速取送物资", "ANDROID", demo_locations["runner2"], demo_health["runner2"])
        self.register_client("demo-runner3", "业主老李", "小区业主", "身体状态一般", "退休人员", "对楼栋位置不熟，体力一般，可协助简单取送", "ANDROID", demo_locations["runner3"], demo_health["runner3"])
        self.upsert_aed_site("南门岗亭 AED", demo_locations["aed1"], access_notes="南门岗亭内红色 AED 箱，24 小时可取用", site_id="demo-aed-1")
        self.upsert_aed_site("车库入口 AED", demo_locations["aed2"], access_notes="车库入口岗亭处，24 小时可取用", site_id="demo-aed-2")

        state = self.incidents[incident_id]
        state.aedSites = self.list_aed_sites()
        state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg="demo scenario bootstrapped"))
        self._persist()
        await self._broadcast_state_async(incident_id)
        return demoBootstrapResponse(
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
            "review_index.md": self._review_index(export, participant_map),
            "expert_summary.md": self._expert_summary(export, participant_map),
            "expert_review_checklist.md": self._expert_review_checklist(export, participant_map),
            "expert_feedback_form.md": self._expert_feedback_form(export, participant_map),
            "facilitator_run_sheet.md": self._facilitator_run_sheet(export, participant_map),
            "analysis_guide.md": self._analysis_guide(export),
            "data_dictionary.md": self._data_dictionary(export),
            "participant_consent_safety_brief.md": self._participant_consent_safety_brief(export, participant_map),
            "evidence_quality_report.json": json.dumps(
                self._evidence_quality_report(export, participant_map),
                ensure_ascii=False,
                indent=2,
            ),
            "experiment.json": json.dumps(payload, ensure_ascii=False, indent=2),
            "experiment_anonymized.json": json.dumps(anonymized_payload, ensure_ascii=False, indent=2),
            "metrics.csv": self._csv_text(
                [{"metric": key, "value": value} for key, value in export.metrics.items()],
                ["metric", "value"],
            ),
            "timeline.csv": self._csv_text(
                self._timeline_export_rows(export.timeline, participant_map),
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
            "participant_questionnaire.csv": self._csv_text(
                self._participant_questionnaire_rows(export, participant_map),
                self._participant_questionnaire_fields(),
            ),
            "baseline_vs_system_comparison.csv": self._csv_text(
                self._baseline_vs_system_comparison_rows(export),
                self._baseline_vs_system_comparison_fields(),
            ),
            "pre_experiment_round_summary.csv": self._csv_text(
                self._pre_experiment_round_summary_rows(export),
                self._pre_experiment_round_summary_fields(),
            ),
            "expert_feedback_summary.csv": self._csv_text(
                self._expert_feedback_summary_rows(export),
                self._expert_feedback_summary_fields(),
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
                    await self._designate_patient_for_state(
                        state,
                        state.patientUserId,
                        "patient SOS after restart",
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
            "LRA_DISPATCH_LLM_BUDGET_SEC",
            "LRA_MAP_PROVIDER",
            "LRA_AMAP_SERVICE_KEY",
            "LRA_BAIDU_WEB_AK",
            "LRA_BAIDU_SERVICE_AK",
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
                try:
                    await asyncio.wait_for(websocket.receive_text(), timeout=25)
                except asyncio.TimeoutError:
                    await websocket.send_json({"type": "HEARTBEAT", "ts": self._now_ms()})
        except WebSocketDisconnect:
            pass
        except Exception:
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
        await self._designate_patient_for_state(state, patient_user_id, "patient SOS", cancel_sos_timer=False)

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
    def _first_log_ts_any(state: IncidentState, keywords: list[str]) -> int | None:
        lowered = [keyword.lower() for keyword in keywords]
        for entry in state.logs:
            message = entry.msg.lower()
            if any(keyword in message for keyword in lowered):
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
        first_responder_ts = self._first_log_ts_any(
            state,
            [
                "PRIME joined",
                "PRIME auto-joined",
                "CPR started",
            ],
        )
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
            "firstResponderResponseSeconds": delta_seconds(designated_ts, first_responder_ts),
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
        return ["ts", "tsIso", "elapsedSec", "eventType", "participantCode", "role", "msg"]

    @staticmethod
    def _observer_record_fields() -> list[str]:
        return ["roundId", "incidentId", "item", "systemValue", "observerValue", "score1to5", "notes"]

    @staticmethod
    def _participant_questionnaire_fields() -> list[str]:
        return [
            "roundId",
            "incidentId",
            "participantCode",
            "assignedTask",
            "questionId",
            "question",
            "score1to5",
            "notes",
        ]

    @staticmethod
    def _baseline_vs_system_comparison_fields() -> list[str]:
        metrics = [
            "dispatchSeconds",
            "firstResponderResponseSeconds",
            "cprStartSeconds",
            "aedPickupSeconds",
            "aedDeliverySeconds",
            "ambulanceArriveSeconds",
        ]
        scores = [
            "roleAssignmentClarityScore",
            "taskInstructionClarityScore",
            "stressOperabilityScore",
            "dispatchReasonablenessScore",
            "aedPromptUsefulnessScore",
        ]
        fields = [
            "comparisonId",
            "scenarioId",
            "scenarioLocation",
            "participantGroup",
            "baselineRoundId",
            "systemRoundId",
            "baselineIncidentId",
            "systemIncidentId",
        ]
        for metric in metrics:
            fields.extend([f"baseline{metric[0].upper()}{metric[1:]}", f"system{metric[0].upper()}{metric[1:]}", f"{metric}Delta", f"{metric}ChangePercent"])
        for score in scores:
            fields.extend([f"baseline{score[0].upper()}{score[1:]}", f"system{score[0].upper()}{score[1:]}", f"{score}Delta"])
        fields.append("analysisNotes")
        return fields

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
            "firstResponderResponseSeconds",
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
                "firstResponderResponseSeconds": metrics.get("firstResponderResponseSeconds"),
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

    def _evidence_quality_report(
        self,
        export: ExperimentExportResponse,
        participant_map: dict[str, str],
    ) -> dict:
        metrics = export.metrics
        timeline_rows = self._timeline_export_rows(export.timeline, participant_map)
        event_types = {str(row.get("eventType", "")) for row in timeline_rows}

        required_events = [
            {
                "key": "patientTrigger",
                "label": "患者触发或指定",
                "eventTypes": ["PATIENT_SOS", "PATIENT_DESIGNATED"],
            },
            {
                "key": "roleAssignment",
                "label": "角色分派或接单",
                "eventTypes": ["ROLE_ASSIGNED", "ROLE_JOINED", "ROLE_AUTO_JOINED"],
            },
            {"key": "cprStarted", "label": "CPR 开始记录", "eventTypes": ["CPR_STARTED"]},
            {"key": "aedPicked", "label": "AED 取到记录", "eventTypes": ["AED_PICKED"]},
            {"key": "aedDelivered", "label": "AED 送达记录", "eventTypes": ["AED_DELIVERED"]},
            {"key": "ambulanceArrived", "label": "救护接管记录", "eventTypes": ["AMBULANCE_ARRIVED"]},
            {"key": "handoverCompleted", "label": "交接归档记录", "eventTypes": ["HANDOVER_COMPLETED"]},
        ]
        event_coverage = [
            {
                "key": item["key"],
                "label": item["label"],
                "covered": any(event_type in event_types for event_type in item["eventTypes"]),
            }
            for item in required_events
        ]
        missing_key_events = [
            {"key": item["key"], "label": item["label"]}
            for item in event_coverage
            if not item["covered"]
        ]

        warnings: list[dict[str, str]] = []

        def add_warning(code: str, severity: str, message: str, suggested_action: str) -> None:
            warnings.append(
                {
                    "code": code,
                    "severity": severity,
                    "message": message,
                    "suggestedAction": suggested_action,
                }
            )

        if export.phase != "ARCHIVED":
            add_warning(
                "incident_not_archived",
                "warning",
                "事件尚未归档，本轮材料可能缺少最终交接或复盘节点。",
                "完成救护接管、交接归档后重新下载证据包。",
            )
        if metrics.get("roleAssignmentCompleteness") != 1.0:
            add_warning(
                "role_assignment_incomplete",
                "critical",
                "PRIME/RUNNER/GUIDE 三类角色未完整覆盖。",
                "重新初始化或手动补齐三类终端后再开始预实验轮次。",
            )
        if metrics.get("availableAedSiteCount", 0) < 1:
            add_warning(
                "no_available_aed",
                "critical",
                "本轮没有可用 AED 点位记录。",
                "在总控台或后台补充至少一个可用 AED 点位。",
            )
        if metrics.get("locationCoveragePercent", 0) < 100:
            add_warning(
                "location_coverage_partial",
                "warning",
                "部分终端缺少位置摘要，距离或取送链路解释可能不完整。",
                "让每个移动端上报位置，或在预实验记录中注明手动点位来源。",
            )
        if metrics.get("healthCoveragePercent", 0) < 100:
            add_warning(
                "health_coverage_partial",
                "info",
                "部分终端缺少健康摘要，健康数据增强展示不完整。",
                "补齐样例健康摘要或在记录中说明该轮未启用健康增强。",
            )
        if metrics.get("dispatchSourceIsFallback") == 1:
            add_warning(
                "dispatch_fallback_used",
                "info",
                "本轮使用规则或备用分派路径，适合演示闭环但不代表第三方 AI/地图能力已接入。",
                "在 PPT 和专家材料中注明当前 provider 状态。",
            )
        for missing in missing_key_events:
            if missing["key"] in {"patientTrigger", "roleAssignment"}:
                severity = "critical"
            elif missing["key"] in {"cprStarted", "aedPicked", "aedDelivered"}:
                severity = "warning"
            else:
                severity = "info"
            add_warning(
                f"missing_{missing['key']}",
                severity,
                f"缺少“{missing['label']}”时间线节点。",
                "按主持人跑场单完成本节点，或由观察员在记录表中补充说明。",
            )

        penalty = sum(25 if item["severity"] == "critical" else 10 if item["severity"] == "warning" else 3 for item in warnings)
        quality_score = max(0, 100 - penalty)
        if quality_score >= 85 and export.phase == "ARCHIVED":
            quality_level = "ready_for_low_cost_pre_experiment_summary"
        elif quality_score >= 65:
            quality_level = "usable_with_notes"
        else:
            quality_level = "needs_rerun_or_manual_review"

        role_codes = {
            role: participant_map.get(user_id or "", None)
            for role, user_id in export.assignments.items()
        }
        role_codes["PATIENT"] = participant_map.get(export.patientUserId or "", None)

        return {
            "schemaVersion": 1,
            "incidentId": export.incidentId,
            "generatedAtIso": self._iso_timestamp(export.generatedAt),
            "phase": export.phase,
            "qualityLevel": quality_level,
            "qualityScore": quality_score,
            "scope": "simulation_training_pre_experiment_only",
            "participantSummary": {
                "participantCount": len(export.clients),
                "patientCode": role_codes.get("PATIENT"),
                "roleCodes": role_codes,
            },
            "metricCoverage": {
                "dispatchSeconds": metrics.get("dispatchSeconds") is not None,
                "firstResponderResponseSeconds": metrics.get("firstResponderResponseSeconds") is not None,
                "cprStartSeconds": metrics.get("cprStartSeconds") is not None,
                "aedPickupSeconds": metrics.get("aedPickupSeconds") is not None,
                "aedDeliverySeconds": metrics.get("aedDeliverySeconds") is not None,
                "ambulanceArriveSeconds": metrics.get("ambulanceArriveSeconds") is not None,
                "roleAssignmentCompleteness": metrics.get("roleAssignmentCompleteness"),
                "locationCoveragePercent": metrics.get("locationCoveragePercent"),
                "healthCoveragePercent": metrics.get("healthCoveragePercent"),
                "availableAedSiteCount": metrics.get("availableAedSiteCount"),
                "runnerRouteMetersAvailable": metrics.get("runnerRouteMeters") is not None,
            },
            "eventCoverage": event_coverage,
            "missingKeyEvents": missing_key_events,
            "warnings": warnings,
            "recommendedUse": [
                "用于低成本预实验流程可行性、协同清晰度和专家反馈材料整理。",
                "如存在 warning 或 critical 项，应在观察员记录或 PPT 备注中说明。",
                "不得作为真实临床疗效、抢救成功率或患者预后改善证据。",
            ],
        }

    @staticmethod
    def _expert_feedback_summary_fields() -> list[str]:
        return [
            "feedbackId",
            "incidentId",
            "roundId",
            "expertCode",
            "expertSpecialty",
            "reviewDate",
            "scenarioFitScore",
            "medicalFlowSafetyScore",
            "roleDivisionScore",
            "dispatchExplainabilityScore",
            "mobileUsabilityScore",
            "evidencePackageScore",
            "safetyBoundaryScore",
            "overallRecommendation",
            "keyPositiveFeedback",
            "keyRiskOrConcern",
            "requiredImprovement",
            "owner",
            "priority",
            "status",
            "targetFollowUpDate",
            "followUpEvidence",
            "secondReviewComment",
        ]

    def _expert_feedback_summary_rows(self, export: ExperimentExportResponse) -> list[dict]:
        return [
            {
                "feedbackId": "EF001",
                "incidentId": export.incidentId,
                "roundId": "R001",
                "expertCode": "E01",
                "expertSpecialty": "",
                "reviewDate": "",
                "scenarioFitScore": "",
                "medicalFlowSafetyScore": "",
                "roleDivisionScore": "",
                "dispatchExplainabilityScore": "",
                "mobileUsabilityScore": "",
                "evidencePackageScore": "",
                "safetyBoundaryScore": "",
                "overallRecommendation": "",
                "keyPositiveFeedback": "",
                "keyRiskOrConcern": "",
                "requiredImprovement": "",
                "owner": "",
                "priority": "",
                "status": "pending_review",
                "targetFollowUpDate": "",
                "followUpEvidence": "",
                "secondReviewComment": "",
            }
        ]

    def _baseline_vs_system_comparison_rows(self, export: ExperimentExportResponse) -> list[dict]:
        metrics = export.metrics
        return [
            {
                "comparisonId": "C001",
                "scenarioId": "S001",
                "scenarioLocation": "",
                "participantGroup": "",
                "baselineRoundId": "",
                "systemRoundId": "R001",
                "baselineIncidentId": "",
                "systemIncidentId": export.incidentId,
                "baselineDispatchSeconds": "",
                "systemDispatchSeconds": metrics.get("dispatchSeconds"),
                "dispatchSecondsDelta": "",
                "dispatchSecondsChangePercent": "",
                "baselineFirstResponderResponseSeconds": "",
                "systemFirstResponderResponseSeconds": metrics.get("firstResponderResponseSeconds"),
                "firstResponderResponseSecondsDelta": "",
                "firstResponderResponseSecondsChangePercent": "",
                "baselineCprStartSeconds": "",
                "systemCprStartSeconds": metrics.get("cprStartSeconds"),
                "cprStartSecondsDelta": "",
                "cprStartSecondsChangePercent": "",
                "baselineAedPickupSeconds": "",
                "systemAedPickupSeconds": metrics.get("aedPickupSeconds"),
                "aedPickupSecondsDelta": "",
                "aedPickupSecondsChangePercent": "",
                "baselineAedDeliverySeconds": "",
                "systemAedDeliverySeconds": metrics.get("aedDeliverySeconds"),
                "aedDeliverySecondsDelta": "",
                "aedDeliverySecondsChangePercent": "",
                "baselineAmbulanceArriveSeconds": "",
                "systemAmbulanceArriveSeconds": metrics.get("ambulanceArriveSeconds"),
                "ambulanceArriveSecondsDelta": "",
                "ambulanceArriveSecondsChangePercent": "",
                "baselineRoleAssignmentClarityScore": "",
                "systemRoleAssignmentClarityScore": "",
                "roleAssignmentClarityScoreDelta": "",
                "baselineTaskInstructionClarityScore": "",
                "systemTaskInstructionClarityScore": "",
                "taskInstructionClarityScoreDelta": "",
                "baselineStressOperabilityScore": "",
                "systemStressOperabilityScore": "",
                "stressOperabilityScoreDelta": "",
                "baselineDispatchReasonablenessScore": "",
                "systemDispatchReasonablenessScore": "",
                "dispatchReasonablenessScoreDelta": "",
                "baselineAedPromptUsefulnessScore": "",
                "systemAedPromptUsefulnessScore": "",
                "aedPromptUsefulnessScoreDelta": "",
                "analysisNotes": "填写无系统基线轮数据后在 Excel 中计算差值；时间差值为负数表示系统轮更快。主观评分需结合参与者问卷和观察员记录补填。",
            }
        ]

    def _observer_record_rows(self, export: ExperimentExportResponse) -> list[dict]:
        metrics = export.metrics
        rows = [
            ("round_id", "", "R001"),
            ("scenario_location", "", ""),
            ("observer_name", "", ""),
            ("trigger_to_dispatch_seconds", metrics.get("dispatchSeconds"), ""),
            ("trigger_to_first_responder_response_seconds", metrics.get("firstResponderResponseSeconds"), ""),
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

    def _participant_questionnaire_rows(
        self,
        export: ExperimentExportResponse,
        participant_map: dict[str, str],
    ) -> list[dict]:
        assigned_tasks = self._participant_assigned_tasks(export)
        questions = [
            ("Q01", "我能快速理解自己在本轮预实验中的任务。"),
            ("Q02", "系统降低了多人协同和现场沟通的混乱感。"),
            ("Q03", "移动端或 App 的当前动作提示足够清楚。"),
            ("Q04", "AED 点位、取送或 CPR/AED 下一步提示对预实验有帮助。"),
            ("Q05", "系统的安全边界提示清楚，没有让我误以为它能替代真实急救。"),
            ("Q06", "我愿意在后续急救协同训练或系统级预实验中继续使用该系统。"),
        ]
        rows: list[dict] = []
        for client in sorted(export.clients, key=lambda item: participant_map.get(item.userId, item.userId)):
            participant_code = participant_map.get(client.userId, client.userId)
            assigned_task = assigned_tasks.get(client.userId, "待命/观察")
            for question_id, question in questions:
                rows.append(
                    {
                        "roundId": "R001",
                        "incidentId": export.incidentId,
                        "participantCode": participant_code,
                        "assignedTask": assigned_task,
                        "questionId": question_id,
                        "question": question,
                        "score1to5": "",
                        "notes": "",
                    }
                )
        return rows

    def _timeline_export_rows(
        self,
        timeline: list[IncidentLogEntry],
        participant_map: dict[str, str],
    ) -> list[dict]:
        start_ts = timeline[0].ts if timeline else None
        rows: list[dict] = []
        for item in timeline:
            parsed = self._parse_timeline_message(item.msg)
            actor_user_id = parsed["actorUserId"]
            rows.append(
                {
                    "ts": item.ts,
                    "tsIso": self._iso_timestamp(item.ts),
                    "elapsedSec": round((item.ts - start_ts) / 1000, 3) if start_ts else 0,
                    "eventType": parsed["eventType"],
                    "participantCode": participant_map.get(actor_user_id, actor_user_id),
                    "role": parsed["role"],
                    "msg": self._replace_participant_ids(item.msg, participant_map),
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
        if "demo scenario bootstrapped" in message:
            return {"eventType": "demo_BOOTSTRAPPED", "role": "", "actorUserId": ""}
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
                    "review_index.md",
                    "expert_summary.md",
                    "expert_review_checklist.md",
                    "expert_feedback_form.md",
                    "facilitator_run_sheet.md",
                    "analysis_guide.md",
                    "data_dictionary.md",
                    "participant_consent_safety_brief.md",
                    "evidence_quality_report.json",
                    "observer_record_form.csv",
                    "participant_questionnaire.csv",
                    "baseline_vs_system_comparison.csv",
                    "pre_experiment_round_summary.csv",
                    "expert_feedback_summary.csv",
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

- `review_index.md`：专家/评委快速审阅索引，建议先打开，用于理解每份材料的用途和公开边界。
- `experiment.json`：完整结构化导出，保留事件、终端、AED、调度依据和健康摘要。
- `experiment_anonymized.json`：匿名化结构化导出，用于专家反馈、PPT 和对外材料。
- `expert_summary.md`：专家/指导教师可快速阅读的预实验摘要。
- `expert_review_checklist.md`：专家现场复核清单，覆盖医学场景、流程安全、AI 分派和数据边界。
- `expert_feedback_form.md`：事件级专家反馈与签字表，便于专家对本轮预实验给出评分、意见和签字确认。
- `facilitator_run_sheet.md`：主持人/观察员跑场单，用于按步骤完成预实验流程、记录关键时间点和导出材料。
- `analysis_guide.md`：预实验数据分析说明，解释 T1-T6、问卷、基线对照和谨慎结论写法。
- `data_dictionary.md`：证据包数据字典，解释关键指标、CSV 字段、角色代码和对外表述边界。
- `participant_consent_safety_brief.md`：参与者知情与安全边界简表，用于预实验前说明和签署记录。
- `evidence_quality_report.json`：本轮证据质量报告，标记关键节点覆盖、缺失项、质量分和可否进入低成本预实验汇总。
- `timeline.csv`：事件时间线，适合直接导入 Excel。
- `clients.csv`：参与终端画像、位置、角色和健康摘要，仅建议内部复核使用。
- `clients_anonymized.csv`：匿名化参与者表，隐藏 userId、姓名、组织和个人简介。
- `aed_sites.csv`：AED 点位与访问备注。
- `dispatch_rationale.csv`：AI/规则分派评分、理由、距离和风险提示。
- `metrics.csv`：响应耗时、AED 取送、交接等预实验指标。
- `observer_record_form.csv`：观察员补充记录表，用于填写系统无法自动采集的现场行为、评分和开放反馈。
- `participant_questionnaire.csv`：参与者主观问卷表，用于记录可理解性、协同减负、移动端提示和安全边界评分。
- `baseline_vs_system_comparison.csv`：无系统基线轮与系统轮对照分析模板，用于计算 T1-T6 差值、百分比变化和主观评分差异。
- `pre_experiment_round_summary.csv`：单轮预实验汇总行，便于把多轮 ZIP 的核心指标合并到 Excel 做描述性统计。
- `expert_feedback_summary.csv`：多名专家意见汇总和整改闭环表，用于记录评分、风险点、负责人、处理状态和二次复核意见。
- `manifest.json`：文件清单、SHA256 校验、生成时间、匿名化使用建议和内部复核文件说明。

## 使用建议

该包用于医创赛低成本预实验记录、PPT 截图依据和专家反馈前的材料整理。对外材料优先使用 `review_index.md`、`experiment_anonymized.json`、`clients_anonymized.csv`、`expert_summary.md`、`expert_review_checklist.md`、`expert_feedback_form.md`、`expert_feedback_summary.csv`、`facilitator_run_sheet.md`、`analysis_guide.md`、`data_dictionary.md`、`participant_consent_safety_brief.md`、`evidence_quality_report.json`、`observer_record_form.csv`、`participant_questionnaire.csv`、`baseline_vs_system_comparison.csv` 和 `pre_experiment_round_summary.csv`；完整 `experiment.json` 与 `clients.csv` 仅建议内部复核使用。

多轮系统级预实验结束后，把每轮 ZIP 放到同一目录，在项目根目录运行：

```powershell
python scripts\\build_pre_experiment_report.py "D:\\path\\to\\evidence-zips" --output-dir "D:\\path\\to\\analysis-output"
```

脚本会先校验证据包 manifest/SHA-256，再生成 `round-summary.csv`、`round-analysis.md`、`round-chart-data.csv` 与 `round-review-actions.csv`。健康摘要如标记为样例接入或演示来源，只能作为预实验模拟数据说明，不应被表述为真实临床诊断或疗效依据；进入 PPT 图表前请先按复核行动清单筛掉需要重跑或人工补充说明的轮次。
"""

    def _review_index(self, export: ExperimentExportResponse, participant_map: dict[str, str]) -> str:
        metrics = export.metrics
        generated_at = self._iso_timestamp(export.generatedAt)
        role_summary = "；".join(
            f"{role}={participant_map.get(user_id or '', user_id or '未分派')}"
            for role, user_id in export.assignments.items()
        )
        return f"""# 生命反射弧证据包审阅索引

事件编号：{export.incidentId}
导出时间：{generated_at}
事件阶段：{export.phase}
患者代号：{participant_map.get(export.patientUserId or "", export.patientUserId or "未指定")}
角色分派：{role_summary}

## 一、建议 3 分钟打开顺序

1. `expert_summary.md`：先看项目场景、分派结果、T1-T6 指标和安全边界。
2. `facilitator_run_sheet.md`：确认这轮预实验是否按预实验流程执行，特别是 T0-T6 记录点。
3. `timeline.csv` 与 `metrics.csv`：核对自动记录的事件时间线和核心耗时。
4. `dispatch_rationale.csv`：查看核心施救、AED 保障、环境清障的分派依据。
5. `expert_feedback_form.md`：填写专家评分、意见和签字。

## 二、材料用途速查

| 材料 | 建议读者 | 主要证明什么 | 公开边界 |
| --- | --- | --- | --- |
| `expert_summary.md` | 专家、指导教师、PPT 制作者 | 这轮预实验的医学场景、协同流程、指标和谨慎结论 | 可外部展示 |
| `expert_review_checklist.md` | 专家、指导教师 | 医学安全边界、AI 分派、数据记录是否可接受 | 可外部展示 |
| `expert_feedback_form.md` | 专家 | 事件级评分、改进意见和签字材料 | 可外部展示 |
| `expert_feedback_summary.csv` | 项目负责人、指导教师 | 汇总专家意见、风险点和整改闭环 | 可外部展示，需去除专家联系方式 |
| `facilitator_run_sheet.md` | 主持人、观察员 | 现场跑场流程、T0-T6 记录提示、预实验后整理步骤 | 可外部展示 |
| `analysis_guide.md` | 数据整理同学、PPT 制作者 | 如何解释 T1-T6、问卷、基线对照和不可夸大结论 | 可外部展示 |
| `data_dictionary.md` | 数据整理同学、专家、PPT 制作者 | 指标、CSV 字段、角色代码和数据边界说明 | 可外部展示 |
| `observer_record_form.csv` | 观察员 | 系统无法自动采集的现场行为、错误、理解度 | 可外部展示 |
| `participant_questionnaire.csv` | 参与者、数据整理同学 | 参与者主观评分和反馈 | 可外部展示，需匿名 |
| `baseline_vs_system_comparison.csv` | 数据整理同学 | 无系统基线轮与系统轮的描述性对照 | 可外部展示 |
| `pre_experiment_round_summary.csv` | 数据整理同学 | 多轮预实验合并统计的一行摘要 | 可外部展示 |
| `manifest.json` | 复核者 | 文件清单、SHA-256 校验和隐私边界 | 可外部展示 |

## 三、自动指标快照

| 指标 | 本轮记录 |
| --- | --- |
| T1 触发到分派完成 | {self._format_metric(metrics.get("dispatchSeconds"))} |
| T2 触发到核心施救响应 | {self._format_metric(metrics.get("firstResponderResponseSeconds"))} |
| T3 触发到 CPR 开始 | {self._format_metric(metrics.get("cprStartSeconds"))} |
| T4 触发到 AED 取到 | {self._format_metric(metrics.get("aedPickupSeconds"))} |
| T5 触发到 AED 送达 | {self._format_metric(metrics.get("aedDeliverySeconds"))} |
| T6 触发到救护接管 | {self._format_metric(metrics.get("ambulanceArriveSeconds"))} |
| 角色完整度 | {metrics.get("roleAssignmentCompleteness", "--")} |
| 定位覆盖率 | {metrics.get("locationCoveragePercent", "--")}% |
| 健康摘要覆盖率 | {metrics.get("healthCoveragePercent", "--")}% |

## 四、对外材料优先使用

- `review_index.md`
- `experiment_anonymized.json`
- `clients_anonymized.csv`
- `expert_summary.md`
- `expert_review_checklist.md`
- `expert_feedback_form.md`
- `facilitator_run_sheet.md`
- `analysis_guide.md`
- `data_dictionary.md`
- `participant_consent_safety_brief.md`
- `observer_record_form.csv`
- `participant_questionnaire.csv`
- `baseline_vs_system_comparison.csv`
- `pre_experiment_round_summary.csv`
- `expert_feedback_summary.csv`

## 五、内部复核材料

- `experiment.json` 与 `clients.csv` 保留原始 userId、终端画像和完整事件内容，只建议团队内部排查或复核使用。
- `aed_sites.csv` 可用于核对 AED 点位和访问备注；若点位来自真实场地，外部展示前应检查是否涉及不宜公开的位置细节。

## 六、必须避免的结论

- 不宣称提高抢救成功率或改善患者预后。
- 不宣称系统可替代 120、AED 语音提示或专业医护判断。
- 不把样例健康摘要或演示健康摘要描述成真实临床监测、诊断或疗效依据。
- 小样本预实验只写流程可行性、可用性、协同清晰度和专家接受度，不写统计显著性临床结论。
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

    def _participant_assigned_tasks(self, export: ExperimentExportResponse) -> dict[str, str]:
        tasks: dict[str, str] = {}
        if export.patientUserId:
            tasks[export.patientUserId] = "患者模拟/触发端"
        role_tasks = {
            "PRIME": "核心施救",
            "RUNNER": "AED 保障",
            "GUIDE": "环境清障/救护接应",
        }
        for role, user_id in export.assignments.items():
            if user_id:
                tasks[user_id] = role_tasks.get(role, role)
        return tasks

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
- 核心施救响应耗时：{self._format_metric(metrics.get("firstResponderResponseSeconds"))}
- CPR 开始耗时：{self._format_metric(metrics.get("cprStartSeconds"))}
- AED 取出耗时：{self._format_metric(metrics.get("aedPickupSeconds"))}
- AED 送达耗时：{self._format_metric(metrics.get("aedDeliverySeconds"))}
- 救护接管耗时：{self._format_metric(metrics.get("ambulanceArriveSeconds"))}
- 事件日志数：{metrics.get("logCount", 0)}

## 数据使用边界

本摘要用于医创赛低成本预实验、专家反馈和产品可行性讨论。健康摘要若为样例接入或演示来源，仅代表预实验闭环中的模拟健康摘要，不可用于真实医疗诊断或疗效结论。
"""

    def _analysis_guide(self, export: ExperimentExportResponse) -> str:
        metrics = export.metrics
        return f"""# 生命反射弧预实验数据分析说明

事件编号：{export.incidentId}
生成时间：{self._iso_timestamp(export.generatedAt)}

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
python scripts\\build_pre_experiment_report.py "D:\\path\\to\\evidence-zips" --output-dir "D:\\path\\to\\analysis-output"
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
| T1 触发到分派完成 | {self._format_metric(metrics.get("dispatchSeconds"))} | 越短表示系统越快完成并行任务组织 |
| T2 触发到核心施救响应 | {self._format_metric(metrics.get("firstResponderResponseSeconds"))} | 用于观察核心施救者是否能及时接单或启动处置 |
| T3 触发到 CPR 开始 | {self._format_metric(metrics.get("cprStartSeconds"))} | 反映核心施救动作启动速度 |
| T4 触发到 AED 取到 | {self._format_metric(metrics.get("aedPickupSeconds"))} | 反映 AED 保障者找到并取出 AED 的速度 |
| T5 触发到 AED 送达 | {self._format_metric(metrics.get("aedDeliverySeconds"))} | 反映 AED 取送链路总效率 |
| T6 触发到救护接管 | {self._format_metric(metrics.get("ambulanceArriveSeconds"))} | 反映环境清障、接应和交接流程 |

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
"""

    def _data_dictionary(self, export: ExperimentExportResponse) -> str:
        metrics = export.metrics
        return f"""# 生命反射弧证据包数据字典

事件编号：{export.incidentId}
生成时间：{self._iso_timestamp(export.generatedAt)}

## 一、核心文件

| 文件 | 内容 | 建议用途 |
| --- | --- | --- |
| `review_index.md` | 3 分钟审阅顺序、材料用途和公开边界 | 专家或评委先打开 |
| `experiment_anonymized.json` | 匿名化后的事件、角色、指标和健康摘要 | PPT、专家审阅、内部复盘 |
| `clients_anonymized.csv` | 匿名化参与者列表，含角色、位置、健康摘要字段 | Excel 汇总、问卷匹配 |
| `timeline.csv` | 事件日志的结构化时间线，使用匿名参与者代号和脱敏日志文本 | 复核 T0-T6 节点 |
| `metrics.csv` | 系统自动计算的核心指标 | 低成本预实验结果表 |
| `dispatch_rationale.csv` | 角色分派评分、距离、理由和警示，使用匿名参与者代号 | 展示智能协同解释性 |
| `observer_record_form.csv` | 观察员补充记录模板 | 记录系统无法自动采集的现场行为 |
| `participant_questionnaire.csv` | 参与者主观问卷模板 | 计算可理解性、压力、可用性评分 |
| `baseline_vs_system_comparison.csv` | 无系统基线轮与系统轮对照模板 | 描述性对照分析 |
| `pre_experiment_round_summary.csv` | 单轮汇总行 | 多轮合并统计 |
| `round-summary.csv` / `round-analysis.md` / `round-chart-data.csv` / `round-review-actions.csv` | 由一键分析脚本在 ZIP 外生成 | 多轮描述性统计、PPT 谨慎摘要、图表数据和复核行动清单 |
| `manifest.json` | 文件 hash、生成时间、隐私边界 | 复核证据包完整性 |

## 二、自动指标

| 字段 | 当前值 | 含义 | 解释边界 |
| --- | --- | --- | --- |
| `dispatchSeconds` | {self._format_metric(metrics.get("dispatchSeconds"))} | T1，患者触发到三类任务分派完成的秒数 | 仅表示系统流程耗时 |
| `firstResponderResponseSeconds` | {self._format_metric(metrics.get("firstResponderResponseSeconds"))} | T2，患者触发到核心施救端接单或启动处置的秒数 | 不等同真实到达患者身边 |
| `cprStartSeconds` | {self._format_metric(metrics.get("cprStartSeconds"))} | T3，患者触发到核心施救端记录 CPR 开始的秒数 | 不等同真实高质量 CPR |
| `aedPickupSeconds` | {self._format_metric(metrics.get("aedPickupSeconds"))} | T4，患者触发到 AED 保障端记录取到 AED 的秒数 | 取决于预实验路径和道具点位 |
| `aedDeliverySeconds` | {self._format_metric(metrics.get("aedDeliverySeconds"))} | T5，患者触发到 AED 送达患者位置的秒数 | 不代表真实除颤完成 |
| `ambulanceArriveSeconds` | {self._format_metric(metrics.get("ambulanceArriveSeconds"))} | T6，患者触发到清障接驳端记录救护接管的秒数 | 可由观察员补充真实口令时间 |
| `roleAssignmentCompleteness` | {metrics.get("roleAssignmentCompleteness", "--")} | PRIME/RUNNER/GUIDE 三类角色是否完整分派，1.0 表示三类均有终端 | 仅表示任务分派完整性 |
| `locationCoveragePercent` | {metrics.get("locationCoveragePercent", "--")}% | 有位置摘要的终端占比 | 演示坐标不等同真实定位精度 |
| `healthCoveragePercent` | {metrics.get("healthCoveragePercent", "--")}% | 有健康摘要的终端占比 | 演示健康摘要不等同真实诊断 |
| `runnerRouteMeters` | {metrics.get("runnerRouteMeters", "--")} | AED 保障端到 AED 点位再回患者位置的估算总距离 | 地图 Key 未接入时可能为 demo/Haversine 估算 |

## 三、角色代码

| 代码 | 对外中文 | 说明 |
| --- | --- | --- |
| `PATIENT` | 患者端 | 触发 SOS、保持位置、等待协同成员到场 |
| `PRIME` | 核心施救 | 前往患者位置并执行 CPR/AED 操作提示 |
| `RUNNER` | AED 保障 | 就近取用 AED 并回送患者位置 |
| `GUIDE` | 环境清障 | 疏通通道、接引救护车、协助交接 |

## 四、关键 CSV 字段

| 字段 | 常见文件 | 含义 |
| --- | --- | --- |
| `participantCode` | `clients_anonymized.csv`、`timeline.csv`、`dispatch_rationale.csv`、问卷、汇总表 | 匿名参与者代号，如 P001/R001 |
| `eventType` | `timeline.csv` | 系统从日志归类出的事件类型 |
| `elapsedSec` | `timeline.csv` | 相对本轮第一条日志的秒数 |
| `msg` | `timeline.csv` | 脱敏后的日志文本，内部 userId 已替换为参与者代号 |
| `score` | `dispatch_rationale.csv` | 角色候选综合评分 |
| `reasons` | `dispatch_rationale.csv` | 分派理由，通常包含能力、距离、AED 可达性或健康风险 |
| `warnings` | `dispatch_rationale.csv` | 候选终端风险或降权提示 |
| `observerValue` | `observer_record_form.csv` | 观察员人工补充值 |
| `score1to5` | 问卷、观察员表 | 1-5 分主观评分 |
| `baseline...` / `system...` | `baseline_vs_system_comparison.csv` | 基线轮与系统轮配对数据 |

## 五、匿名化与禁止表述

- 对外材料优先使用 `review_index.md`、`experiment_anonymized.json`、`clients_anonymized.csv`、`timeline.csv`、`dispatch_rationale.csv` 和本数据字典。
- `review_index.md`、`timeline.csv` 与 `dispatch_rationale.csv` 已使用 `participantCode` 做公开审阅匿名化，不应再手工补回原始 userId。
- `experiment.json`、`clients.csv` 可能包含原始 userId、显示名、组织等内部复核信息，不建议直接放入 PPT。
- 可以写“用于模拟急救协同、训练复盘、预实验记录和专家反馈准备”。
- 不要写“提高抢救成功率”“改善患者预后”“替代 120/AED/医护判断”。
- 样例健康摘要、演示位置或演示健康摘要只能作为演示/预实验数据来源说明，不能写成真实临床监测结论。
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
| 核心施救响应耗时 | {self._format_metric(metrics.get("firstResponderResponseSeconds"))} |
| CPR 开始耗时 | {self._format_metric(metrics.get("cprStartSeconds"))} |
| AED 取出耗时 | {self._format_metric(metrics.get("aedPickupSeconds"))} |
| AED 送达耗时 | {self._format_metric(metrics.get("aedDeliverySeconds"))} |
| 救护接管耗时 | {self._format_metric(metrics.get("ambulanceArriveSeconds"))} |
| 角色完整度 | {metrics.get("roleAssignmentCompleteness", "--")} |
| 定位覆盖率 | {metrics.get("locationCoveragePercent", "--")}% |
| 健康摘要覆盖率 | {metrics.get("healthCoveragePercent", "--")}% |

## 三、专家重点判断

- [ ] 医学场景是否聚焦公共场所疑似心脏骤停的真实协同问题。
- [ ] CPR/AED/救护接应提示是否适合预实验和培训语境，是否存在不安全或过度医疗化表述。
- [ ] PRIME/RUNNER/GUIDE 三类角色分工是否能降低现场混乱。
- [ ] AI/规则分派是否合理体现人员能力、距离、AED 可达性和健康风险。
- [ ] 调度解释是否足够清晰，能否被非技术评委和医学专家理解。
- [ ] 证据包是否支持低成本预实验归档、匿名化审阅和后续 PPT 论证。

## 四、现场补充记录

请结合 `observer_record_form.csv` 填写系统无法自动采集的信息，例如参与者迟疑点、现场沟通问题、误触发、界面阅读困难、专家认为应修改的医学措辞。

## 五、安全边界

本系统为模拟急救协同、训练复盘和预实验验证工具。它不替代拨打 120、AED 语音提示、专业医护判断，也不用于真实医疗诊断或疗效证明。
"""

    def _expert_feedback_form(
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
        return f"""# 生命反射弧事件级专家反馈与签字表

事件编号：{export.incidentId}
导出时间：{generated_at}
事件阶段：{export.phase}
患者代号：{participant_map.get(export.patientUserId or "", export.patientUserId or "未指定")}
角色分派：核心施救={assignments.get("PRIME", "未分派")}，AED 保障={assignments.get("RUNNER", "未分派")}，环境清障={assignments.get("GUIDE", "未分派")}

## 一、专家基本信息

| 项目 | 填写 |
| --- | --- |
| 姓名 |  |
| 单位 / 科室 |  |
| 职称 / 职务 |  |
| 专业方向 |  |
| 联系方式（可选） |  |
| 审阅日期 |  |

## 二、本轮预实验关键记录

| 指标 | 系统记录 | 专家备注 |
| --- | --- | --- |
| T1 触发到分派完成 | {self._format_metric(metrics.get("dispatchSeconds"))} |  |
| T2 触发到核心施救响应 | {self._format_metric(metrics.get("firstResponderResponseSeconds"))} |  |
| T3 触发到 CPR 开始 | {self._format_metric(metrics.get("cprStartSeconds"))} |  |
| T4 触发到 AED 取到 | {self._format_metric(metrics.get("aedPickupSeconds"))} |  |
| T5 触发到 AED 送达 | {self._format_metric(metrics.get("aedDeliverySeconds"))} |  |
| T6 触发到救护接管 | {self._format_metric(metrics.get("ambulanceArriveSeconds"))} |  |
| 角色完整度 | {metrics.get("roleAssignmentCompleteness", "--")} |  |
| 定位覆盖率 | {metrics.get("locationCoveragePercent", "--")}% |  |
| 健康摘要覆盖率 | {metrics.get("healthCoveragePercent", "--")}% |  |

## 三、审阅材料确认

- [ ] Web 调度台或录屏。
- [ ] 移动 Web / Android 任务页演示。
- [ ] `experiment_anonymized.json` 与 `clients_anonymized.csv`。
- [ ] `timeline.csv`、`metrics.csv`、`dispatch_rationale.csv`。
- [ ] `expert_summary.md` 与 `expert_review_checklist.md`。
- [ ] `analysis_guide.md`、`observer_record_form.csv`、`participant_questionnaire.csv`。
- [ ] `baseline_vs_system_comparison.csv` 与 `pre_experiment_round_summary.csv`。
- [ ] `manifest.json` 文件清单、SHA-256 校验与匿名化使用建议。

## 四、专家评分

评分：1 分为很不认可，5 分为非常认可。

| 评价项 | 1 | 2 | 3 | 4 | 5 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| 医学应用场景明确，聚焦公共场所疑似心脏骤停协同问题 |  |  |  |  |  |  |
| CPR/AED/救护接应提示适合训练或预实验场景 |  |  |  |  |  |  |
| 核心施救、AED 保障、环境清障的角色分工合理 |  |  |  |  |  |  |
| AI/规则分派解释能体现能力、距离、AED 和风险因素 |  |  |  |  |  |  |
| 移动端任务提示在紧张情境下可读、可执行 |  |  |  |  |  |  |
| 证据包可支持低成本预实验记录、匿名化审阅和后续统计 |  |  |  |  |  |  |
| 安全边界、免责说明和数据使用边界清楚 |  |  |  |  |  |  |
| 具备进一步用于校园/社区急救协同训练试点的潜力 |  |  |  |  |  |  |

## 五、开放反馈

### 5.1 医学流程合理性

请指出本轮流程在 CPR、AED 取送、AED 分析/除颤提示、救护接应或交接环节中需要修正的地方。

反馈：


### 5.2 AI 分派与协同价值

请评价系统分派是否有助于降低多人现场混乱，并指出人员选择、距离判断、AED 点位选择或健康风险处理上的不足。

反馈：


### 5.3 界面与预实验可用性

请评价 Web 总控台、移动 Web、Android App 在模拟急救情境中的可理解性、信息负载和误触风险。

反馈：


### 5.4 数据与预实验设计

请评价本轮导出的时间线、指标、问卷、观察员记录和基线对照表是否足以支撑医创赛预实验材料。

反馈：


## 六、100-300 字专家意见摘要

可用于项目申报材料或 PPT 中的专家意见摘录。建议围绕医学场景价值、流程可行性、AI 协同创新点、安全边界和后续改进方向书写。

专家意见：


## 七、安全与合规声明

本人知悉本反馈基于模拟心脏骤停预实验、系统演示和预实验材料审阅，仅用于学生创新竞赛、训练复盘和产品迭代参考。本表不构成真实临床疗效证明、医疗器械注册证明、急救培训资质证明，也不替代拨打 120、AED 语音提示或专业医护判断。

专家签字：

日期：

单位盖章（如适用）：
"""

    def _facilitator_run_sheet(
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
        patient_code = participant_map.get(export.patientUserId or "", export.patientUserId or "未指定")
        return f"""# 生命反射弧预实验主持人跑场单

事件编号：{export.incidentId}
导出时间：{generated_at}
事件阶段：{export.phase}
患者代号：{patient_code}
角色分派：核心施救={assignments.get("PRIME", "未分派")}，AED 保障={assignments.get("RUNNER", "未分派")}，环境清障={assignments.get("GUIDE", "未分派")}

## 一、适用场景

本跑场单给主持人、观察员或指导教师使用，用于 3-5 分钟课堂/答辩演示，或 8-16 人低成本预实验。它只服务模拟急救协同和训练复盘，不用于真实患者处置。

## 二、预实验前 5 分钟检查

- [ ] Web 总控台可访问，演示口令或管理员账号可用。
- [ ] 点击“初始化医创赛演示场景”，确认 4 类终端和 AED 点位出现。
- [ ] 在“演示入口”面板复制或打开患者端、核心施救端、AED 保障端、清障接驳端和 4 端导播台链接。
- [ ] 参与者已阅读 `participant_consent_safety_brief.md`，不做真实胸外按压、不做真实电击。
- [ ] 观察员准备填写 `observer_record_form.csv`，参与者预实验后填写 `participant_questionnaire.csv`。
- [ ] 如专家在场，提前发放 `expert_review_checklist.md` 和 `expert_feedback_form.md`。

## 三、现场口令与动作顺序

| 顺序 | 主持人口令 | 系统/参与者动作 | 记录重点 |
| --- | --- | --- | --- |
| 1 | “预实验开始，患者端进入走廊场景。” | 患者端保持当前位置，其他端待命 | 记录场景、人数和 AED 道具状态 |
| 2 | “患者出现异常，启动 SOS。” | 患者端点击 SOS 并完成二次确认 | 记 T0：患者触发时间 |
| 3 | “等待系统分派。” | Web 展示 AI/规则分派，三类角色收到任务 | 记 T1：分派完成时间 |
| 4 | “核心施救者响应并前往患者。” | 核心施救端接单，到达后开始 CPR | 记 T2/T3：响应与 CPR 开始 |
| 5 | “AED 保障者取 AED。” | AED 保障端前往点位、取到 AED、回送患者 | 记 T4/T5：AED 取到与送达 |
| 6 | “清障接驳者疏通通道。” | 清障接驳端完成通道清理、救护车接应 | 记 T6：救护接管/交接 |
| 7 | “完成交接，归档事件。” | Web 或移动端完成交接归档，下载证据包 | 记录包名、manifest 生成时间 |

## 四、本轮系统自动指标快照

| 指标 | 当前系统记录 | 观察员补充 |
| --- | --- | --- |
| T1 触发到分派完成 | {self._format_metric(metrics.get("dispatchSeconds"))} |  |
| T2 触发到核心施救响应 | {self._format_metric(metrics.get("firstResponderResponseSeconds"))} |  |
| T3 触发到 CPR 开始 | {self._format_metric(metrics.get("cprStartSeconds"))} |  |
| T4 触发到 AED 取到 | {self._format_metric(metrics.get("aedPickupSeconds"))} |  |
| T5 触发到 AED 送达 | {self._format_metric(metrics.get("aedDeliverySeconds"))} |  |
| T6 触发到救护接管 | {self._format_metric(metrics.get("ambulanceArriveSeconds"))} |  |
| 角色完整度 | {metrics.get("roleAssignmentCompleteness", "--")} |  |
| 定位覆盖率 | {metrics.get("locationCoveragePercent", "--")}% |  |
| 健康摘要覆盖率 | {metrics.get("healthCoveragePercent", "--")}% |  |

## 五、观察员必须补记

- 是否有人看不懂任务说明或误触按钮。
- 患者端、核心施救端、AED 保障端、清障接驳端是否能独立完成当前动作。
- AED 点位提示是否足够明确，是否存在绕路、找不到点位或楼层信息不足。
- 系统分派理由是否能被非技术参与者理解。
- 安全边界提示是否清楚，是否有人误以为可替代真实 120 或 AED 语音提示。

## 六、预实验后 10 分钟整理

1. 下载 ZIP 证据包，优先对外使用匿名化文件。
2. 核对 `manifest.json` 生成时间和 SHA-256 文件清单。
3. 把观察员补充内容填入 `observer_record_form.csv`。
4. 让参与者填写 `participant_questionnaire.csv` 对应代号行。
5. 如进行了无系统基线轮，把基线数据填入 `baseline_vs_system_comparison.csv`。
6. 专家审阅后，在 `expert_feedback_form.md` 中填写 100-300 字意见并签字。

## 七、必须避免的表述

- 不写“提高抢救成功率”“改善患者预后”。
- 不写“系统可替代 120、AED 语音提示或专业医护判断”。
- 不把样例健康摘要或演示健康摘要描述成真实临床监测或诊断。
- 不把小样本预实验描述成具有统计显著性的临床研究。
"""

    def _participant_consent_safety_brief(
        self,
        export: ExperimentExportResponse,
        participant_map: dict[str, str],
    ) -> str:
        generated_at = self._iso_timestamp(export.generatedAt)
        assigned_tasks = self._participant_assigned_tasks(export)
        participant_rows = []
        for client in sorted(export.clients, key=lambda item: participant_map.get(item.userId, item.userId)):
            participant_code = participant_map.get(client.userId, client.userId)
            participant_rows.append(
                f"| {participant_code} | {assigned_tasks.get(client.userId, '待命/观察')} |  |  |"
            )
        participant_table = "\n".join(participant_rows) if participant_rows else "|  |  |  |  |"
        return f"""# 生命反射弧参与者知情与安全边界简表

事件编号：{export.incidentId}
导出时间：{generated_at}

## 一、预实验目的

本轮预实验用于医创赛低成本预实验，目标是观察“生命反射弧”在模拟心脏骤停场景下对多人协同分工、AED 取送、CPR/AED 流程提示和数据留痕的支持效果。预实验结果仅用于学生创新竞赛、产品迭代和专家反馈准备。

## 二、安全边界

- 本预实验不纳入真实患者，不用于真实医疗诊断、治疗或疗效评价。
- 不在真人身上进行真实胸外按压，不进行真实电击；如使用 AED，仅使用训练机、模型或空盒道具。
- 系统提示不能替代拨打 120、AED 语音提示、专业医护判断或正式急救培训。
- 参与者可随时暂停或退出，不影响后续学习、评价或团队关系。
- 如出现身体不适、焦虑、眩晕、跌倒风险或现场安全问题，应立即停止预实验。

## 三、数据与隐私

- 对外和专家材料优先使用匿名化文件，参与者以 P001、R001、S001 等代号出现。
- 不把手机号、真实姓名、学校/单位身份、精确个人轨迹或未经授权的照片放入公开 PPT。
- 健康摘要若为样例接入或演示来源，只能表述为模拟数据，不得表述为真实健康监测或临床诊断。

## 四、参与者确认记录

| 参与者代号 | 本轮任务 | 已阅读安全边界 | 签名/确认 |
| --- | --- | --- | --- |
{participant_table}

## 五、预实验后反馈

预实验结束后，请配合填写 `participant_questionnaire.csv` 中对应自己代号的问卷行；观察员另行填写 `observer_record_form.csv`，专家可对照 `expert_review_checklist.md` 复核。
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
    def _ensure_handover_prerequisites(state: IncidentState) -> None:
        prime_ready = state.roles.PRIME.status in {"CPR_STARTED", "AED_ANALYZING", "AED_SHOCK_DELIVERED"}
        aed_ready = state.roles.RUNNER.status == "AED_DELIVERED"
        if not prime_ready or not aed_ready:
            raise HTTPException(
                status_code=409,
                detail="Handover requires CPR started and AED delivered",
            )

    @staticmethod
    def _is_role_action_already_recorded(state: IncidentState, role_name: str, action: str) -> bool:
        completed_status_by_action = {
            "AED_ANALYSIS_STARTED": "AED_ANALYZING",
        }
        completed_status = completed_status_by_action.get(action, action)
        return getattr(state.roles, role_name).status == completed_status

    @staticmethod
    def _phase_rank(phase: str | None) -> int:
        order = {
            "CREATED": 0,
            "DISPATCHING": 1,
            "DISPATCHED": 2,
            "CPR": 3,
            "AED_PICKED": 4,
            "AED_DELIVERED": 5,
            "AED_ANALYZING": 6,
            "SHOCK_DELIVERED": 7,
            "HANDOVER": 8,
            "ARCHIVED": 9,
        }
        return order.get(phase or "", -1)

    def _advance_phase(self, state: IncidentState, next_phase: str) -> None:
        if state.phase in {"HANDOVER", "ARCHIVED"} and self._phase_rank(next_phase) < self._phase_rank(state.phase):
            return
        state.phase = next_phase

    @staticmethod
    def _is_patient_candidate(health_condition: str, profile_bio: str) -> bool:
        text = f"{health_condition} {profile_bio}".lower()
        markers = ("心脏", "冠心病", "骤停风险", "重点监测", "患者侧")
        return any(marker in text for marker in markers)
