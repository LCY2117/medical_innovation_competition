from __future__ import annotations

import hashlib
import hmac
import secrets
import time
import uuid

from fastapi import HTTPException

from app.models.schemas import AuthMeResponse, AuthResponse, AuthUser, SimpleOkResponse
from app.storage.sqlite_auth_store import SqliteAuthStore, UserRecord


class AuthService:
    DEMO_PERSONAS = {
        "patient": {
            "display_name": "冠心病患者",
            "phone": "13900001001",
            "organization": "模拟社区",
            "health_condition": "存在心脏骤停风险",
            "profession_identity": "患者侧",
            "profile_bio": "多年冠心病病史，需要重点监护，可用于预实验患者端。",
        },
        "prime": {
            "display_name": "张医生",
            "phone": "13900001002",
            "organization": "市医院急救科",
            "health_condition": "身体状态一般",
            "profession_identity": "医生 / 专业急救人员",
            "profile_bio": "急救科医生，熟悉 CPR 和 AED 处置，可承担核心施救任务。",
        },
        "runner": {
            "display_name": "体育生小李",
            "phone": "13900001003",
            "organization": "大学校园",
            "health_condition": "身体素质良好",
            "profession_identity": "有一定急救常识",
            "profile_bio": "体育生，跑得快，熟悉校园路线，可快速取送 AED。",
        },
        "guide": {
            "display_name": "安保老王",
            "phone": "13900001004",
            "organization": "校园安保",
            "health_condition": "身体状态一般",
            "profession_identity": "安保 / 物业 / 场地协调人员",
            "profile_bio": "熟悉楼栋出入口、电梯和救护车通道，可承担环境协调与接驳。",
        },
    }

    def __init__(self, store: SqliteAuthStore, token_ttl_sec: int = 604800) -> None:
        self.store = store
        self.token_ttl_sec = token_ttl_sec

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
        token, expires_at = self._issue_token(record.user_id)
        return AuthResponse(token=token, user=self._to_auth_user(record), tokenExpiresAt=expires_at)

    def login(self, phone: str, password: str) -> AuthResponse:
        normalized_phone = self._normalize_phone(phone)
        user = self.store.get_user_by_phone(normalized_phone)
        if user is None or not self._verify_password(password, user.password_hash):
            raise HTTPException(status_code=401, detail="手机号或密码错误")

        token, expires_at = self._issue_token(user.user_id)
        return AuthResponse(token=token, user=self._to_auth_user(user), tokenExpiresAt=expires_at)

    def demo_login(self, persona: str) -> AuthResponse:
        normalized_persona = persona.strip().lower()
        profile = self.DEMO_PERSONAS.get(normalized_persona)
        if profile is None:
            raise HTTPException(status_code=400, detail="未知演示身份")

        user = self.store.get_user_by_phone(profile["phone"])
        if user is None:
            user = UserRecord(
                user_id=f"demo-{normalized_persona}",
                display_name=profile["display_name"],
                phone=profile["phone"],
                password_hash=self._hash_password("LCY"),
                organization=profile["organization"],
                health_condition=profile["health_condition"],
                profession_identity=profile["profession_identity"],
                profile_bio=profile["profile_bio"],
                credential_status=self._credential_status(profile["health_condition"], profile["profession_identity"]),
                created_at=self._now_ms(),
            )
            self.store.create_user(user)

        token, expires_at = self._issue_token(user.user_id)
        return AuthResponse(token=token, user=self._to_auth_user(user), tokenExpiresAt=expires_at)

    def me(self, authorization: str | None) -> AuthMeResponse:
        token = self._extract_token(authorization)
        user = self._require_user_by_token(token)
        return AuthMeResponse(user=self._to_auth_user(user), tokenExpiresAt=self.store.get_token_expires_at(token))

    def logout(self, authorization: str | None) -> SimpleOkResponse:
        token = self._extract_token(authorization)
        self.store.delete_token(token)
        return SimpleOkResponse()

    def require_user(self, authorization: str | None) -> UserRecord:
        token = self._extract_token(authorization)
        return self._require_user_by_token(token)

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

    def _issue_token(self, user_id: str) -> tuple[str, int | None]:
        token = secrets.token_urlsafe(32)
        issued_at = self._now_ms()
        expires_at = self._token_expires_at(issued_at)
        self.store.save_token(token, user_id, issued_at, expires_at)
        return token, expires_at

    def _require_user_by_token(self, token: str) -> UserRecord:
        user = self.store.get_user_by_token(token, self._now_ms())
        if user is None:
            raise HTTPException(status_code=401, detail="登录态已失效，请重新登录")
        return user

    def _token_expires_at(self, issued_at: int) -> int | None:
        if self.token_ttl_sec > 0:
            return issued_at + self.token_ttl_sec * 1000
        if self.token_ttl_sec < 0:
            return issued_at - 1
        return None

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
