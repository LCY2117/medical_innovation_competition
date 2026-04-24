from __future__ import annotations

import sqlite3
import threading
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class UserRecord:
    user_id: str
    display_name: str
    phone: str
    password_hash: str
    organization: str
    health_condition: str
    profession_identity: str
    profile_bio: str
    credential_status: str
    created_at: int


class SqliteAuthStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._initialize()

    def create_user(self, record: UserRecord) -> None:
        with closing(self._connect()) as conn, self._lock:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, display_name, phone, password_hash, organization,
                    health_condition, profession_identity, profile_bio, credential_status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.user_id,
                    record.display_name,
                    record.phone,
                    record.password_hash,
                    record.organization,
                    record.health_condition,
                    record.profession_identity,
                    record.profile_bio,
                    record.credential_status,
                    record.created_at,
                ),
            )
            conn.commit()

    def get_user_by_phone(self, phone: str) -> UserRecord | None:
        with closing(self._connect()) as conn, self._lock:
            row = conn.execute(
                """
                SELECT user_id, display_name, phone, password_hash, organization,
                       health_condition, profession_identity, profile_bio, credential_status, created_at
                FROM users
                WHERE phone = ?
                LIMIT 1
                """,
                (phone,),
            ).fetchone()
        return self._row_to_user(row)

    def get_user_by_id(self, user_id: str) -> UserRecord | None:
        with closing(self._connect()) as conn, self._lock:
            row = conn.execute(
                """
                SELECT user_id, display_name, phone, password_hash, organization,
                       health_condition, profession_identity, profile_bio, credential_status, created_at
                FROM users
                WHERE user_id = ?
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        return self._row_to_user(row)

    def save_token(self, token: str, user_id: str, issued_at: int) -> None:
        with closing(self._connect()) as conn, self._lock:
            conn.execute(
                """
                INSERT OR REPLACE INTO auth_tokens (token, user_id, issued_at)
                VALUES (?, ?, ?)
                """,
                (token, user_id, issued_at),
            )
            conn.commit()

    def get_user_by_token(self, token: str) -> UserRecord | None:
        with closing(self._connect()) as conn, self._lock:
            row = conn.execute(
                """
                SELECT u.user_id, u.display_name, u.phone, u.password_hash, u.organization,
                       u.health_condition, u.profession_identity, u.profile_bio, u.credential_status, u.created_at
                FROM auth_tokens t
                JOIN users u ON u.user_id = t.user_id
                WHERE t.token = ?
                LIMIT 1
                """,
                (token,),
            ).fetchone()
        return self._row_to_user(row)

    def health(self) -> dict:
        with closing(self._connect()) as conn, self._lock:
            user_count = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
            token_count = conn.execute("SELECT COUNT(*) AS count FROM auth_tokens").fetchone()["count"]
        return {"ok": True, "userCount": user_count, "tokenCount": token_count}

    def _initialize(self) -> None:
        with closing(self._connect()) as conn, self._lock:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    phone TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    health_condition TEXT NOT NULL,
                    profession_identity TEXT NOT NULL,
                    profile_bio TEXT NOT NULL,
                    credential_status TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS auth_tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    issued_at INTEGER NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """
            )
            conn.commit()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _row_to_user(row: sqlite3.Row | None) -> UserRecord | None:
        if row is None:
            return None
        return UserRecord(
            user_id=row["user_id"],
            display_name=row["display_name"],
            phone=row["phone"],
            password_hash=row["password_hash"],
            organization=row["organization"],
            health_condition=row["health_condition"],
            profession_identity=row["profession_identity"],
            profile_bio=row["profile_bio"],
            credential_status=row["credential_status"],
            created_at=row["created_at"],
        )
