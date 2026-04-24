from __future__ import annotations

import asyncio
import random
import time
import uuid
from typing import Dict

from fastapi import HTTPException, WebSocket, WebSocketDisconnect

from app.models.schemas import (
    AutoJoinResponse,
    ClientInfo,
    CreateIncidentResponse,
    DispatchResponse,
    IncidentLogEntry,
    IncidentState,
    MutationResponse,
    RoleState,
    RoleStates,
    SosState,
)
from app.services.dispatch_ai import DispatchPlanner
from app.storage.sqlite_store import SqliteIncidentStore


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
    ) -> None:
        self.store = store
        self.sos_duration_sec = sos_duration_sec
        self.dispatch_delay_sec = dispatch_delay_sec
        snapshot = self.store.load_snapshot()
        self.incidents: Dict[str, IncidentState] = snapshot.incidents
        self.ws_connections: Dict[str, list[WebSocket]] = {}
        self.sos_tasks: Dict[str, asyncio.Task[None]] = {}
        self.current_incident_id: str | None = snapshot.current_incident_id
        self.clients: Dict[str, ClientInfo] = {}
        self.dispatch_planner = DispatchPlanner(
            api_key=siliconflow_api_key,
            model=siliconflow_model,
            base_url=siliconflow_base_url,
            timeout_sec=siliconflow_timeout_sec,
            local_base_url=local_model_base_url,
            local_model=local_model_name,
            local_timeout_sec=local_model_timeout_sec,
            prefer_local=prefer_local_model,
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
    ) -> ClientInfo:
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
        )
        self.clients[user_id] = client
        return client

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

    async def designate_patient(self, patient_user_id: str) -> DispatchResponse:
        state = self.get_current_incident()
        now = self._now_ms()

        state.phase = "DISPATCHING"
        state.sos = self._new_sos(status="ALERTING", start_ts=now)
        state.roles = self._new_roles()
        state.patientUserId = patient_user_id
        state.dispatchSource = None
        state.logs.append(IncidentLogEntry(ts=now, msg=f"Patient designated by dashboard ({patient_user_id})"))
        state.logs.append(IncidentLogEntry(ts=now, msg="AI dispatching started"))
        self._touch_client(patient_user_id)
        self._persist()
        await self._broadcast_state_async(state.incidentId)

        if self.dispatch_delay_sec > 0:
            await asyncio.sleep(self.dispatch_delay_sec)

        assignments, source = self.dispatch_planner.assign_roles(patient_user_id, self.list_clients())
        state.phase = "DISPATCHED"
        state.dispatchSource = source
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
                state.phase = "DISPATCHED"
                state.logs.append(IncidentLogEntry(ts=self._now_ms(), msg="Incident auto-triggered after restart"))
                self._persist()
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
            "activeWebSockets": sum(len(connections) for connections in self.ws_connections.values()),
            "activeSosTimers": sum(1 for task in self.sos_tasks.values() if not task.done()),
            "dispatch": dispatch_info,
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
        ]
        return explanation

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
        state = self.incidents.get(incident_id)
        if state is None:
            return

        payload = {"type": "STATE", "payload": self._incident_payload(state)}
        alive: list[WebSocket] = []
        for ws in self.ws_connections.get(incident_id, []):
            try:
                await ws.send_json(payload)
                alive.append(ws)
            except Exception:
                pass
        self.ws_connections[incident_id] = alive

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

    @staticmethod
    def _incident_payload(state: IncidentState) -> dict:
        return state.model_dump(mode="json")

    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)

    def _persist(self) -> None:
        self.store.save_snapshot(self.incidents, self.current_incident_id)

    def _touch_client(self, user_id: str) -> None:
        client = self.clients.get(user_id)
        if client is None:
            return
        self.clients[user_id] = client.model_copy(update={"lastSeenTs": self._now_ms(), "online": True})

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
