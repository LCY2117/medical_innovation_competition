from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from app.models.schemas import AedSite, AuditEvent, ClientInfo, IncidentState


@dataclass(frozen=True)
class IncidentSnapshot:
    incidents: dict[str, IncidentState]
    current_incident_id: str | None
    clients: dict[str, ClientInfo]
    aed_sites: dict[str, AedSite]


class SqliteIncidentStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._initialize()

    def load_snapshot(self) -> IncidentSnapshot:
        with closing(self._connect()) as conn, self._lock:
            current_row = conn.execute(
                "SELECT incident_id FROM incidents WHERE is_current = 1 LIMIT 1"
            ).fetchone()
            incident_rows = conn.execute(
                "SELECT incident_id, state_json FROM incidents ORDER BY updated_at DESC"
            ).fetchall()
            runtime_rows = conn.execute("SELECT key, value_json FROM runtime_state").fetchall()

        incidents = {
            row["incident_id"]: IncidentState.model_validate_json(row["state_json"])
            for row in incident_rows
        }
        runtime = {row["key"]: row["value_json"] for row in runtime_rows}
        clients = {
            client.userId: client
            for client in (
                ClientInfo.model_validate(item)
                for item in self._load_runtime_list(runtime.get("clients"))
            )
        }
        aed_sites = {
            site.siteId: site
            for site in (
                AedSite.model_validate(item)
                for item in self._load_runtime_list(runtime.get("aed_sites"))
            )
        }
        current_id = current_row["incident_id"] if current_row else None
        return IncidentSnapshot(
            incidents=incidents,
            current_incident_id=current_id,
            clients=clients,
            aed_sites=aed_sites,
        )

    def save_snapshot(
        self,
        incidents: dict[str, IncidentState],
        current_incident_id: str | None,
        clients: dict[str, ClientInfo] | None = None,
        aed_sites: dict[str, AedSite] | None = None,
    ) -> None:
        serialized = [
            (
                incident_id,
                incident.model_dump_json(),
                1 if incident_id == current_incident_id else 0,
                self._incident_updated_at(incident),
            )
            for incident_id, incident in incidents.items()
        ]

        with closing(self._connect()) as conn, self._lock:
            conn.execute("DELETE FROM incidents")
            conn.executemany(
                """
                INSERT INTO incidents (incident_id, state_json, is_current, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                serialized,
            )
            if clients is not None:
                conn.execute(
                    """
                    INSERT INTO runtime_state (key, value_json)
                    VALUES ('clients', ?)
                    ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json
                    """,
                    (json.dumps([client.model_dump(mode="json") for client in clients.values()], ensure_ascii=False),),
                )
            if aed_sites is not None:
                conn.execute(
                    """
                    INSERT INTO runtime_state (key, value_json)
                    VALUES ('aed_sites', ?)
                    ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json
                    """,
                    (json.dumps([site.model_dump(mode="json") for site in aed_sites.values()], ensure_ascii=False),),
                )
            conn.commit()

    def health(self) -> dict:
        with closing(self._connect()) as conn, self._lock:
            incident_count = conn.execute("SELECT COUNT(*) AS count FROM incidents").fetchone()["count"]
            audit_event_count = conn.execute("SELECT COUNT(*) AS count FROM audit_events").fetchone()["count"]

        return {
            "ok": True,
            "dbPath": str(self.db_path),
            "incidentCount": incident_count,
            "auditEventCount": audit_event_count,
        }

    def append_audit_event(self, event: AuditEvent) -> None:
        with closing(self._connect()) as conn, self._lock:
            conn.execute(
                """
                INSERT INTO audit_events (
                    event_id, ts, event_type, actor_type, actor_id,
                    target_type, target_id, outcome, request_hash, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.eventId,
                    event.ts,
                    event.eventType,
                    event.actorType,
                    event.actorId,
                    event.targetType,
                    event.targetId,
                    event.outcome,
                    event.requestHash,
                    json.dumps(event.metadata, ensure_ascii=False),
                ),
            )
            conn.commit()

    def list_audit_events(self, limit: int = 100) -> list[AuditEvent]:
        safe_limit = max(1, min(limit, 500))
        with closing(self._connect()) as conn, self._lock:
            rows = conn.execute(
                """
                SELECT event_id, ts, event_type, actor_type, actor_id,
                       target_type, target_id, outcome, request_hash, metadata_json
                FROM audit_events
                ORDER BY ts DESC, event_id DESC
                LIMIT ?
                """,
                (safe_limit,),
            ).fetchall()
        return [self._row_to_audit_event(row) for row in rows]

    def _initialize(self) -> None:
        with closing(self._connect()) as conn, self._lock:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    incident_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    is_current INTEGER NOT NULL DEFAULT 0,
                    updated_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS runtime_state (
                    key TEXT PRIMARY KEY,
                    value_json TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    ts INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    actor_type TEXT NOT NULL,
                    actor_id TEXT,
                    target_type TEXT,
                    target_id TEXT,
                    outcome TEXT NOT NULL,
                    request_hash TEXT,
                    metadata_json TEXT NOT NULL DEFAULT '{}'
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_audit_events_ts
                ON audit_events(ts DESC)
                """
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _incident_updated_at(incident: IncidentState) -> int:
        if not incident.logs:
            return 0
        return max(log.ts for log in incident.logs)

    @staticmethod
    def _load_runtime_list(value_json: str | None) -> list[dict]:
        if not value_json:
            return []
        try:
            value = json.loads(value_json)
        except json.JSONDecodeError:
            return []
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    @staticmethod
    def _row_to_audit_event(row: sqlite3.Row) -> AuditEvent:
        try:
            metadata = json.loads(row["metadata_json"])
        except json.JSONDecodeError:
            metadata = {}
        if not isinstance(metadata, dict):
            metadata = {}
        return AuditEvent(
            eventId=row["event_id"],
            ts=row["ts"],
            eventType=row["event_type"],
            actorType=row["actor_type"],
            actorId=row["actor_id"],
            targetType=row["target_type"],
            targetId=row["target_id"],
            outcome=row["outcome"],
            requestHash=row["request_hash"],
            metadata=metadata,
        )
