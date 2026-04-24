from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


class ServerTestCase(unittest.TestCase):
    def setUp(self) -> None:
        workspace_tmp = Path(__file__).resolve().parent / ".tmp"
        workspace_tmp.mkdir(parents=True, exist_ok=True)
        self.temp_dir = tempfile.TemporaryDirectory(dir=workspace_tmp)
        self.root = Path(self.temp_dir.name)
        self.settings = Settings(
            app_name="Life Reflex Arc Test",
            api_prefix="/api",
            host="127.0.0.1",
            port=8080,
            reload=False,
            sos_duration_sec=10,
            dispatch_delay_sec=0,
            cors_origins=["http://localhost:5173"],
            db_path=self.root / "data" / "test.db",
            web_dist_dir=self.root / "web-dist",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _client(self) -> TestClient:
        return TestClient(create_app(self.settings))

    @staticmethod
    def _register_payload(
        display_name: str,
        phone: str,
        organization: str,
        health_condition: str,
        profession_identity: str,
        profile_bio: str,
    ) -> dict:
        return {
            "displayName": display_name,
            "phone": phone,
            "password": "123456",
            "organization": organization,
            "healthCondition": health_condition,
            "professionIdentity": profession_identity,
            "profileBio": profile_bio,
        }

    def test_dual_api_prefixes_work(self) -> None:
        with self._client() as client:
            old_health = client.get("/health")
            api_health = client.get("/api/health")

        self.assertEqual(old_health.status_code, 200)
        self.assertEqual(api_health.status_code, 200)
        self.assertEqual(old_health.json(), {"ok": True})
        self.assertEqual(api_health.json(), {"ok": True})

    def test_incident_persists_across_app_recreation(self) -> None:
        with self._client() as client:
            created = client.post("/api/incidents")
            incident_id = created.json()["incidentId"]

            joined = client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "PRIME", "userId": "tester-prime"},
            )

        self.assertEqual(created.status_code, 200)
        self.assertEqual(joined.status_code, 200)

        with self._client() as second_client:
            current = second_client.get("/api/incidents/current")

        self.assertEqual(current.status_code, 200)
        payload = current.json()
        self.assertEqual(payload["incidentId"], incident_id)
        self.assertEqual(payload["roles"]["PRIME"]["userId"], "tester-prime")
        self.assertEqual(payload["phase"], "DISPATCHED")

    def test_health_detail_reports_storage_and_frontend_state(self) -> None:
        with self._client() as client:
            response = client.get("/api/health/detail")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["storage"]["dbPath"], str(self.settings.db_path))
        self.assertFalse(payload["frontend"]["ok"])
        self.assertEqual(payload["loadedIncidents"], 0)

    def test_auth_register_and_login(self) -> None:
        with self._client() as client:
            register = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    display_name="张医生",
                    phone="13800138000",
                    organization="市医院急救科",
                    health_condition="身体状态一般",
                    profession_identity="医生 / 专业急救人员",
                    profile_bio="急救科医生，熟悉 CPR 和 AED 处置",
                ),
            )
            login = client.post(
                "/api/auth/login",
                json={"phone": "13800138000", "password": "123456"},
            )

        self.assertEqual(register.status_code, 200)
        self.assertEqual(login.status_code, 200)
        register_payload = register.json()
        login_payload = login.json()
        self.assertTrue(register_payload["token"])
        self.assertTrue(login_payload["token"])
        self.assertEqual(register_payload["user"]["phone"], "13800138000")
        self.assertEqual(login_payload["user"]["phone"], "13800138000")

    def test_patient_designation_assigns_roles_from_registered_profiles(self) -> None:
        with self._client() as client:
            incident = client.get("/api/incidents/current").json()
            incident_id = incident["incidentId"]

            registrations = [
                self._register_payload(
                    display_name="冠心病患者",
                    phone="13800138001",
                    organization="社区",
                    health_condition="存在心脏骤停风险",
                    profession_identity="对急救不太熟悉",
                    profile_bio="多年冠心病病史，需要重点监护",
                ),
                self._register_payload(
                    display_name="张医生",
                    phone="13800138002",
                    organization="市医院急救科",
                    health_condition="身体状态一般",
                    profession_identity="医生 / 专业急救人员",
                    profile_bio="急救科医生，熟悉 CPR 和 AED 处置",
                ),
                self._register_payload(
                    display_name="体育生小李",
                    phone="13800138003",
                    organization="大学校园",
                    health_condition="身体素质良好",
                    profession_identity="有一定急救常识",
                    profile_bio="体育生，跑得快，熟悉校园路线，可快速取送 AED",
                ),
                self._register_payload(
                    display_name="社区安保老王",
                    phone="13800138004",
                    organization="小区物业",
                    health_condition="身体状态一般",
                    profession_identity="安保 / 物业 / 场地协调人员",
                    profile_bio="安保人员，熟悉楼栋出入口和车辆通道",
                ),
            ]

            user_ids: dict[str, str] = {}
            for payload in registrations:
                auth = client.post("/api/auth/register", json=payload)
                self.assertEqual(auth.status_code, 200)
                auth_payload = auth.json()
                user_id = auth_payload["user"]["userId"]
                user_ids[payload["displayName"]] = user_id
                register_terminal = client.post(
                    "/api/clients/register",
                    headers={"Authorization": f"Bearer {auth_payload['token']}"},
                    json={
                        "userId": user_id,
                        "displayName": payload["displayName"],
                        "organization": payload["organization"],
                        "healthCondition": payload["healthCondition"],
                        "professionIdentity": payload["professionIdentity"],
                        "profileBio": payload["profileBio"],
                        "deviceType": "ANDROID",
                    },
                )
                self.assertEqual(register_terminal.status_code, 200)

            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": user_ids["冠心病患者"]},
            )

            self.assertEqual(dispatch.status_code, 200)
            data = dispatch.json()
            self.assertEqual(data["incidentId"], incident_id)
            self.assertEqual(data["assignments"]["PRIME"], user_ids["张医生"])
            self.assertEqual(data["assignments"]["RUNNER"], user_ids["体育生小李"])
            self.assertEqual(data["assignments"]["GUIDE"], user_ids["社区安保老王"])

            current = client.get("/api/incidents/current")
            self.assertEqual(current.status_code, 200)
            current_payload = current.json()
            self.assertEqual(current_payload["phase"], "DISPATCHED")
            self.assertEqual(current_payload["patientUserId"], user_ids["冠心病患者"])

    def test_role_progress_does_not_reset_prime_after_runner_update(self) -> None:
        with self._client() as client:
            incident_id = client.post("/api/incidents").json()["incidentId"]

            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "PRIME", "userId": "prime-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "RUNNER", "userId": "runner-user"},
            )

            cpr_started = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "CPR_STARTED", "userId": "prime-user"},
            )
            aed_picked = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_PICKED", "userId": "runner-user"},
            )
            current = client.get(f"/api/incidents/{incident_id}")

        self.assertEqual(cpr_started.status_code, 200)
        self.assertEqual(aed_picked.status_code, 200)
        self.assertEqual(current.status_code, 200)
        payload = current.json()
        self.assertEqual(payload["phase"], "AED_PICKED")
        self.assertEqual(payload["roles"]["PRIME"]["status"], "CPR_STARTED")
        self.assertEqual(payload["roles"]["RUNNER"]["status"], "AED_PICKED")

    def test_runner_cannot_deliver_before_pickup(self) -> None:
        with self._client() as client:
            incident_id = client.post("/api/incidents").json()["incidentId"]
            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "RUNNER", "userId": "runner-user"},
            )
            response = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_DELIVERED", "userId": "runner-user"},
            )

        self.assertEqual(response.status_code, 409)

    def test_prime_can_complete_aed_analysis_and_shock_after_delivery(self) -> None:
        with self._client() as client:
            incident_id = client.post("/api/incidents").json()["incidentId"]
            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "PRIME", "userId": "prime-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "RUNNER", "userId": "runner-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "CPR_STARTED", "userId": "prime-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_PICKED", "userId": "runner-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_DELIVERED", "userId": "runner-user"},
            )

            analysis = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_ANALYSIS_STARTED", "userId": "prime-user"},
            )
            shock = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_SHOCK_DELIVERED", "userId": "prime-user"},
            )
            current = client.get(f"/api/incidents/{incident_id}")

        self.assertEqual(analysis.status_code, 200)
        self.assertEqual(shock.status_code, 200)
        payload = current.json()
        self.assertEqual(payload["phase"], "SHOCK_DELIVERED")
        self.assertEqual(payload["roles"]["PRIME"]["status"], "AED_SHOCK_DELIVERED")
        self.assertEqual(payload["roles"]["RUNNER"]["status"], "AED_DELIVERED")

    def test_prime_can_start_second_aed_analysis_after_shock(self) -> None:
        with self._client() as client:
            incident_id = client.post("/api/incidents").json()["incidentId"]
            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "PRIME", "userId": "prime-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "RUNNER", "userId": "runner-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "CPR_STARTED", "userId": "prime-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_PICKED", "userId": "runner-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_DELIVERED", "userId": "runner-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_ANALYSIS_STARTED", "userId": "prime-user"},
            )
            client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_SHOCK_DELIVERED", "userId": "prime-user"},
            )

            second_analysis = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AED_ANALYSIS_STARTED", "userId": "prime-user"},
            )
            current = client.get(f"/api/incidents/{incident_id}")

        self.assertEqual(second_analysis.status_code, 200)
        payload = current.json()
        self.assertEqual(payload["phase"], "AED_ANALYZING")
        self.assertEqual(payload["roles"]["PRIME"]["status"], "AED_ANALYZING")

    def test_handover_can_be_completed_and_archived(self) -> None:
        with self._client() as client:
            incident_id = client.post("/api/incidents").json()["incidentId"]
            client.post(
                f"/api/incidents/{incident_id}/join",
                json={"role": "GUIDE", "userId": "guide-user"},
            )

            arrived = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "AMBULANCE_ARRIVED", "userId": "guide-user"},
            )
            completed = client.post(
                f"/api/incidents/{incident_id}/actions",
                json={"action": "HANDOVER_COMPLETED", "userId": "guide-user"},
            )
            current = client.get(f"/api/incidents/{incident_id}")

        self.assertEqual(arrived.status_code, 200)
        self.assertEqual(completed.status_code, 200)
        payload = current.json()
        self.assertEqual(payload["phase"], "ARCHIVED")
        self.assertEqual(payload["roles"]["GUIDE"]["status"], "HANDOVER_COMPLETED")


if __name__ == "__main__":
    unittest.main()
