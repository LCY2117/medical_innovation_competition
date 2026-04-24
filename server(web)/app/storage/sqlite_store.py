from __future__ import annotations

import sqlite3
import threading
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from app.models.schemas import IncidentState


@dataclass(frozen=True)
class IncidentSnapshot:
    incidents: dict[str, IncidentState]
    current_incident_id: str | None


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

        incidents = {
            row["incident_id"]: IncidentState.model_validate_json(row["state_json"])
            for row in incident_rows
        }
        current_id = current_row["incident_id"] if current_row else None
        return IncidentSnapshot(incidents=incidents, current_incident_id=current_id)

    def save_snapshot(self, incidents: dict[str, IncidentState], current_incident_id: str | None) -> None:
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
