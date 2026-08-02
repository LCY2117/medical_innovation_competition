"""种子数据：4 个预置演示用户 + 候选施救者 + AED 点位 + 管理账号。

预置演示用户：
    patient / prime / runner / guide   （密码 demo1234）
管理账号：
    admin / system                     （密码 admin1234）
"""
from __future__ import annotations

import logging

from passlib.hash import pbkdf2_sha256
from sqlmodel import Session, select

from app.models.aed import AedDevice
from app.models.responder import ResponderProfile
from app.models.user import User
from app.config import Settings

logger = logging.getLogger("lifereflex.seed")

DEMO_USERS = [
    # (username, 全名, 角色, 电话)
    ("patient", "患者 演示用户", "PATIENT", "13800000001"),
    ("prime", "核心施救 演示用户", "PRIME", "13800000002"),
    ("runner", "AED保障 演示用户", "RUNNER", "13800000003"),
    ("guide", "环境清障 演示用户", "GUIDE", "13800000004"),
]

# 候选施救者画像：(username, 角色, 状态, skill, fitness, health_active,
#                   venue_familiarity, distance_km, aed_distance_km)
CANDIDATES = [
    # --- PRIME 候选 ---
    ("c_prime_1", "PRIME", "AVAILABLE", 0.90, 0.85, True, 0.80, 1.0, 1.2),
    ("c_prime_2", "PRIME", "AVAILABLE", 0.70, 0.75, True, 0.60, 3.0, 2.5),
    ("c_prime_3", "PRIME", "TIRED", 0.95, 0.90, True, 0.90, 0.5, 0.8),  # 疲劳→过滤
    ("c_prime_4", "PRIME", "AVAILABLE", 0.50, 0.60, False, 0.40, 4.5, 4.0),
    # --- RUNNER 候选 ---
    ("c_runner_1", "RUNNER", "AVAILABLE", 0.50, 0.50, True, 0.50, 0.8, 0.5),
    ("c_runner_2", "RUNNER", "AVAILABLE", 0.50, 0.50, True, 0.50, 2.5, 1.5),
    ("c_runner_3", "RUNNER", "OFFLINE", 0.50, 0.50, True, 0.50, 0.5, 0.3),  # 离线→过滤
    # --- GUIDE 候选 ---
    ("c_guide_1", "GUIDE", "AVAILABLE", 0.50, 0.50, True, 0.95, 1.2, 1.0),
    ("c_guide_2", "GUIDE", "AVAILABLE", 0.50, 0.50, True, 0.70, 2.0, 1.5),
]

# 演示用户的画像（确保总是被选中）
DEMO_PROFILES = {
    "prime": ("PRIME", "AVAILABLE", 0.98, 0.95, True, 0.90, 0.4, 0.6),
    "runner": ("RUNNER", "AVAILABLE", 0.50, 0.50, True, 0.50, 0.4, 0.3),
    "guide": ("GUIDE", "AVAILABLE", 0.50, 0.50, True, 0.99, 0.6, 0.8),
}

AED_DEVICES = [
    ("AED-01 大厅前台", "1号楼一层大厅", 30.100, 120.200),
    ("AED-02 健身房", "体育馆二楼", 30.110, 120.210),
    ("AED-03 停车场", "东侧地下车库入口", 30.095, 120.195),
    ("AED-04 食堂", "食堂一楼西侧", 30.105, 120.205),
]


def _hash(pw: str) -> str:
    return pbkdf2_sha256.hash(pw)


def seed_if_empty(session: Session, settings: Settings) -> bool:
    """库空时写入全部种子数据。返回是否执行了种子写入。"""
    existing = session.exec(select(User)).first()
    if existing is not None:
        return False

    # 管理/系统账号
    admin = User(
        username="admin",
        full_name="系统管理员",
        role="ADMIN",
        email="admin@lifereflex.local",
        hashed_password=_hash(settings.admin_password),
    )
    system = User(
        username="system",
        full_name="自动调度系统",
        role="SYSTEM",
        email="system@lifereflex.local",
        hashed_password=_hash(settings.admin_password),
    )
    session.add(admin)
    session.add(system)

    # 演示用户
    demo_user_ids: dict[str, int] = {}
    for username, full_name, role, phone in DEMO_USERS:
        u = User(
            username=username,
            full_name=full_name,
            role=role,
            phone=phone,
            hashed_password=_hash(settings.demo_password),
        )
        session.add(u)
        session.flush()
        demo_user_ids[username] = u.id

    # 候选施救者
    for (username, role, status, skill, fitness, health, venue, dist, aed_dist) in CANDIDATES:
        u = User(
            username=username,
            full_name=f"候选{role} {username}",
            role=role,
            hashed_password=_hash(settings.demo_password),
        )
        session.add(u)
        session.flush()
        session.add(
            ResponderProfile(
                user_id=u.id,
                role=role,
                responder_status=status,
                skill_level=skill,
                fitness=fitness,
                health_active=health,
                venue_familiarity=venue,
                distance_km=dist,
                aed_distance_km=aed_dist,
            )
        )

    # 演示用户画像
    for username, (role, status, skill, fitness, health, venue, dist, aed_dist) in DEMO_PROFILES.items():
        session.add(
            ResponderProfile(
                user_id=demo_user_ids[username],
                role=role,
                responder_status=status,
                skill_level=skill,
                fitness=fitness,
                health_active=health,
                venue_familiarity=venue,
                distance_km=dist,
                aed_distance_km=aed_dist,
            )
        )

    # AED 点位
    for name, loc, lat, lng in AED_DEVICES:
        session.add(
            AedDevice(name=name, location=loc, latitude=lat, longitude=lng)
        )

    session.commit()
    logger.info("种子数据写入完成")
    return True
