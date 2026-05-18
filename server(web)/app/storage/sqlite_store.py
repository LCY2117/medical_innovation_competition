from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from app.models.schemas import AedSite, ClientInfo, IncidentState


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

        return {
            "ok": True,
            "dbPath": str(self.db_path),
            "incidentCount": incident_count,
        }

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
