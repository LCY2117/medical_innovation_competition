"""容器健康检查脚本。

流程：演示登录（/api/v1/auth/demo）获取 JWT →
     请求 /api/v1/auth/me，返回 200 即健康。
     同时验证了 DB 可读写与 JWT 签发链路。
"""
from __future__ import annotations

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8000"


def _post(path: str, payload: dict):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def main() -> int:
    try:
        data = _post("/api/v1/auth/demo", {"role": "PATIENT"})
        token = data.get("access_token", "")
        if not token:
            return 1
        req = urllib.request.Request(
            BASE + "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return 0 if resp.status == 200 else 1
    except Exception:  # noqa: BLE001
        return 1


if __name__ == "__main__":
    sys.exit(main())
