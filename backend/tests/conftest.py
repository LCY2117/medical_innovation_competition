"""pytest 共享夹具：独立临时库 + 测试应用 + 登录工具。"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


@pytest.fixture()
def app(tmp_path):
    """每个测试独立的临时 SQLite 库 + 测试应用。

    关闭自动分派/确认计时器（DISPATCH_TIMEOUT=0, CONFIRM_TIMEOUT=0），
    保证测试确定性；超时逻辑通过显式调用引擎方法验证。
    """
    db_path = tmp_path / "test.db"
    settings = Settings(
        database_url=f"sqlite:///{db_path}",
        seed_on_startup=True,
        dispatch_timeout=0.0,
        confirm_timeout=0.0,
    )
    application = create_app(settings)
    # 直接使用 app（不经 TestClient 生命周期）时也要有种子数据
    from app.seed import seed_if_empty

    with application.state.session_factory() as session:
        seed_if_empty(session, settings)
    return application


@pytest.fixture()
def client(app):
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def session(app):
    s = app.state.session_factory()
    yield s
    s.close()


def demo_login(client, role: str) -> str:
    r = client.post("/api/v1/auth/demo", json={"role": role})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def admin_login(client, username: str = "admin", password: str = "admin1234") -> str:
    r = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture()
def headers(client):
    """返回 角色 -> Authorization 头。"""
    return {
        role: {"Authorization": f"Bearer {demo_login(client, role)}"}
        for role in ("PATIENT", "PRIME", "RUNNER", "GUIDE")
    } | {
        "SYSTEM": {"Authorization": f"Bearer {admin_login(client, 'system')}"},
        "ADMIN": {"Authorization": f"Bearer {admin_login(client, 'admin')}"},
    }


@pytest.fixture()
def make_event(client, headers):
    """创建 SOS 事件并返回 event_id。"""

    def _make():
        r = client.post(
            "/api/v1/events/sos",
            json={"location": "测试场地", "latitude": 30.1, "longitude": 120.2},
            headers=headers["PATIENT"],
        )
        assert r.status_code == 201, r.text
        return r.json()["id"]

    return _make
