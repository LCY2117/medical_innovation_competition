from __future__ import annotations

import hashlib
import hmac
import secrets
import time
import uuid

from fastapi import HTTPException

from app.models.schemas import AuthResponse, AuthUser
from app.storage.sqlite_auth_store import SqliteAuthStore, UserRecord


class AuthService:
    def __init__(self, store: SqliteAuthStore) -> None:
        self.store = store

    def register(
        self,
        display_name: str,
        phone: str,
        password: str,
        organization: str,
        health_condition: str,
        profession_identity: str,
        profile_bio: str,
    ) -> AuthResponse:
        normalized_phone = self._normalize_phone(phone)
        self._validate_registration(display_name, normalized_phone, password, profile_bio)
        if self.store.get_user_by_phone(normalized_phone) is not None:
            raise HTTPException(status_code=409, detail="手机号已注册")

        record = UserRecord(
            user_id=str(uuid.uuid4()),
            display_name=display_name.strip(),
            phone=normalized_phone,
            password_hash=self._hash_password(password),
            organization=organization.strip() or "Life Reflex Arc 网络",
            health_condition=health_condition.strip(),
            profession_identity=profession_identity.strip(),
            profile_bio=profile_bio.strip(),
            credential_status=self._credential_status(health_condition, profession_identity),
            created_at=self._now_ms(),
        )
        self.store.create_user(record)
        token = self._issue_token(record.user_id)
        return AuthResponse(token=token, user=self._to_auth_user(record))

    def login(self, phone: str, password: str) -> AuthResponse:
        normalized_phone = self._normalize_phone(phone)
        user = self.store.get_user_by_phone(normalized_phone)
        if user is None or not self._verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="手机号或密码错误")

        token = self._issue_token(user.user_id)
        return AuthResponse(token=token, user=self._to_auth_user(user))

    def require_user(self, authorization: str | None) -> UserRecord:
        token = self._extract_token(authorization)
        user = self.store.get_user_by_token(token)
        if user is None:
            raise HTTPException(status_code=401, detail="登录态已失效，请重新登录")
        return user

    @staticmethod
    def _normalize_phone(phone: str) -> str:
        return "".join(ch for ch in phone if ch.isdigit())

    @staticmethod
    def _validate_registration(display_name: str, phone: str, password: str, profile_bio: str) -> None:
        if not display_name.strip():
            raise HTTPException(status_code=400, detail="请输入姓名")
        if len(phone) < 11:
            raise HTTPException(status_code=400, detail="请输入有效手机号")
        if len(password) < 4:
            raise HTTPException(status_code=400, detail="密码至少 4 位")
        if len(profile_bio.strip()) < 8:
            raise HTTPException(status_code=400, detail="个人介绍至少 8 个字")

    def _issue_token(self, user_id: str) -> str:
        token = secrets.token_urlsafe(32)
        self.store.save_token(token, user_id, self._now_ms())
        return token

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return f"{salt.hex()}:{digest.hex()}"

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        try:
            salt_hex, digest_hex = stored_hash.split(":", 1)
        except ValueError:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000)
        return hmac.compare_digest(actual, expected)

    @staticmethod
    def _credential_status(health_condition: str, profession_identity: str) -> str:
        if "风险" in health_condition or "心脏" in health_condition:
            return "重点监护对象"
        if "医生" in profession_identity or "专业" in profession_identity:
            return "高可信急救资质"
        if "安保" in profession_identity or "物业" in profession_identity:
            return "适合环境协调与接驳"
        return "已完成基础画像认证"

    @staticmethod
    def _extract_token(authorization: str | None) -> str:
        if authorization is None or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="缺少有效登录凭证")
        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            raise HTTPException(status_code=401, detail="缺少有效登录凭证")
        return token

    @staticmethod
    def _to_auth_user(user: UserRecord) -> AuthUser:
        return AuthUser(
            userId=user.user_id,
            displayName=user.display_name,
            phone=user.phone,
            organization=user.organization,
            healthCondition=user.health_condition,
            professionIdentity=user.profession_identity,
            profileBio=user.profile_bio,
            credentialStatus=user.credential_status,
        )

    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)
