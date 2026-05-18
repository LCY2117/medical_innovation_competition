from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def _client_with_demo_admin_token(self, token: str = "test-demo-admin") -> TestClient:
        settings = Settings(
            app_name=self.settings.app_name,
            api_prefix=self.settings.api_prefix,
            host=self.settings.host,
            port=self.settings.port,
            reload=self.settings.reload,
            sos_duration_sec=self.settings.sos_duration_sec,
            dispatch_delay_sec=self.settings.dispatch_delay_sec,
            cors_origins=self.settings.cors_origins,
            db_path=self.settings.db_path,
            web_dist_dir=self.settings.web_dist_dir,
            demo_admin_token=token,
        )
        return TestClient(create_app(settings))

    def _client_with_expired_auth_tokens(self) -> TestClient:
        settings = Settings(
            app_name=self.settings.app_name,
            api_prefix=self.settings.api_prefix,
            host=self.settings.host,
            port=self.settings.port,
            reload=self.settings.reload,
            sos_duration_sec=self.settings.sos_duration_sec,
            dispatch_delay_sec=self.settings.dispatch_delay_sec,
            cors_origins=self.settings.cors_origins,
            db_path=self.settings.db_path,
            web_dist_dir=self.settings.web_dist_dir,
            auth_token_ttl_sec=-1,
        )
        return TestClient(create_app(settings))

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
        self.assertEqual(payload["registeredClients"], 0)
        self.assertEqual(payload["registeredAedSites"], 0)
        self.assertIn("dispatch", payload)
        self.assertFalse(payload["demoAdminAuthEnabled"])

    def test_dispatch_meta_is_serializable(self) -> None:
        with self._client() as client:
            response = client.get("/api/dispatch/meta")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("configured", payload)
        self.assertIn("provider", payload)
        self.assertIn("dispatchDelaySec", payload)
        self.assertIn("systemPrompt", payload)

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
            me = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {register.json()['token']}"},
            )
            logout = client.post(
                "/api/auth/logout",
                headers={"Authorization": f"Bearer {register.json()['token']}"},
            )
            after_logout = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {register.json()['token']}"},
            )

        self.assertEqual(register.status_code, 200)
        self.assertEqual(login.status_code, 200)
        self.assertEqual(me.status_code, 200)
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(after_logout.status_code, 401)
        register_payload = register.json()
        login_payload = login.json()
        self.assertTrue(register_payload["token"])
        self.assertTrue(login_payload["token"])
        self.assertIsInstance(register_payload["tokenExpiresAt"], int)
        self.assertEqual(register_payload["user"]["phone"], "13800138000")
        self.assertEqual(login_payload["user"]["phone"], "13800138000")
        self.assertEqual(me.json()["user"]["phone"], "13800138000")

    def test_expired_auth_token_is_rejected(self) -> None:
        with self._client_with_expired_auth_tokens() as client:
            register = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    display_name="过期测试",
                    phone="13800138999",
                    organization="测试组织",
                    health_condition="身体状态一般",
                    profession_identity="有一定急救常识",
                    profile_bio="用于测试登录态过期处理",
                ),
            )
            self.assertEqual(register.status_code, 200)
            token = register.json()["token"]
            me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

        self.assertEqual(me.status_code, 401)

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
            self.assertIn("dispatchRationale", current_payload)
            self.assertEqual(current_payload["dispatchRationale"]["PRIME"]["userId"], user_ids["张医生"])

    def test_demo_bootstrap_aed_dispatch_and_export(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            self.assertEqual(bootstrapped.status_code, 200)
            demo = bootstrapped.json()
            self.assertEqual(len(demo["clients"]), 4)
            self.assertEqual(len(demo["aedSites"]), 2)

            aed_sites = client.get("/api/aed-sites")
            self.assertEqual(aed_sites.status_code, 200)
            self.assertEqual(len(aed_sites.json()["aedSites"]), 2)

            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )
            self.assertEqual(dispatch.status_code, 200)
            payload = dispatch.json()
            self.assertEqual(payload["assignments"]["PRIME"], "demo-doctor")
            self.assertEqual(payload["assignments"]["RUNNER"], "demo-runner")
            self.assertEqual(payload["assignments"]["GUIDE"], "demo-guide")
            self.assertGreater(payload["rationale"]["RUNNER"]["distanceToAedMeters"], 0)

            export = client.get("/api/experiments/current/export")
            self.assertEqual(export.status_code, 200)
            exported = export.json()
            self.assertEqual(exported["patientUserId"], "demo-patient")
            self.assertEqual(exported["assignments"]["RUNNER"], "demo-runner")
            self.assertIn("dispatchSeconds", exported["metrics"])
            self.assertTrue(exported["timeline"])

    def test_demo_clients_and_aed_sites_persist_across_app_recreation(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            self.assertEqual(bootstrapped.status_code, 200)

        with self._client() as restarted_client:
            clients = restarted_client.get("/api/clients")
            aed_sites = restarted_client.get("/api/aed-sites")
            dispatch = restarted_client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )

        self.assertEqual(clients.status_code, 200)
        self.assertEqual(aed_sites.status_code, 200)
        self.assertEqual(dispatch.status_code, 200)
        self.assertEqual(len(clients.json()["clients"]), 4)
        self.assertEqual(len(aed_sites.json()["aedSites"]), 2)
        self.assertEqual(dispatch.json()["assignments"]["PRIME"], "demo-doctor")

    def test_patient_designation_rejects_unregistered_patient(self) -> None:
        with self._client() as client:
            response = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "missing-patient"},
            )

        self.assertEqual(response.status_code, 404)
        self.assertIn("Patient client not registered", response.text)

    def test_patient_sos_uses_logged_in_user_and_dispatches_roles(self) -> None:
        settings = Settings(
            app_name=self.settings.app_name,
            api_prefix=self.settings.api_prefix,
            host=self.settings.host,
            port=self.settings.port,
            reload=self.settings.reload,
            sos_duration_sec=0,
            dispatch_delay_sec=0,
            cors_origins=self.settings.cors_origins,
            db_path=self.settings.db_path,
            web_dist_dir=self.settings.web_dist_dir,
        )
        with TestClient(create_app(settings)) as client:
            incident = client.get("/api/incidents/current").json()
            incident_id = incident["incidentId"]

            registrations = [
                self._register_payload(
                    display_name="冠心病患者",
                    phone="13800138101",
                    organization="社区",
                    health_condition="存在心脏骤停风险",
                    profession_identity="患者侧",
                    profile_bio="多年冠心病病史，需要重点监护",
                ),
                self._register_payload(
                    display_name="张医生",
                    phone="13800138102",
                    organization="市医院急救科",
                    health_condition="身体状态一般",
                    profession_identity="医生 / 专业急救人员",
                    profile_bio="急救科医生，熟悉 CPR 和 AED 处置",
                ),
                self._register_payload(
                    display_name="体育生小李",
                    phone="13800138103",
                    organization="大学校园",
                    health_condition="身体素质良好",
                    profession_identity="有一定急救常识",
                    profile_bio="体育生，跑得快，熟悉校园路线，可快速取送 AED",
                ),
                self._register_payload(
                    display_name="社区安保老王",
                    phone="13800138104",
                    organization="小区物业",
                    health_condition="身体状态一般",
                    profession_identity="安保 / 物业 / 场地协调人员",
                    profile_bio="安保人员，熟悉楼栋出入口和车辆通道",
                ),
            ]

            patient_token = ""
            patient_user_id = ""
            for payload in registrations:
                auth = client.post("/api/auth/register", json=payload)
                self.assertEqual(auth.status_code, 200)
                auth_payload = auth.json()
                user_id = auth_payload["user"]["userId"]
                token = auth_payload["token"]
                if payload["displayName"] == "冠心病患者":
                    patient_token = token
                    patient_user_id = user_id
                register_terminal = client.post(
                    "/api/clients/register",
                    headers={"Authorization": f"Bearer {token}"},
                    json={
                        "userId": user_id,
                        "displayName": payload["displayName"],
                        "organization": payload["organization"],
                        "healthCondition": payload["healthCondition"],
                        "professionIdentity": payload["professionIdentity"],
                        "profileBio": payload["profileBio"],
                        "deviceType": "MOBILE_WEB",
                    },
                )
                self.assertEqual(register_terminal.status_code, 200)

            no_auth = client.post(f"/api/incidents/{incident_id}/patient_sos_start")
            started = client.post(
                f"/api/incidents/{incident_id}/patient_sos_start",
                headers={"Authorization": f"Bearer {patient_token}"},
            )
            current = client.get("/api/incidents/current")

        self.assertEqual(no_auth.status_code, 401)
        self.assertEqual(started.status_code, 200)
        payload = current.json()
        self.assertEqual(payload["phase"], "DISPATCHED")
        self.assertEqual(payload["patientUserId"], patient_user_id)
        self.assertEqual(payload["roles"]["PRIME"]["status"], "ASSIGNED")
        self.assertEqual(payload["roles"]["RUNNER"]["status"], "ASSIGNED")
        self.assertEqual(payload["roles"]["GUIDE"]["status"], "ASSIGNED")

    def test_patient_designation_runs_dispatch_in_worker_thread(self) -> None:
        with self._client() as client:
            client.post("/api/demo/bootstrap")

            with patch(
                "app.services.incidents.asyncio.to_thread",
                wraps=__import__("asyncio").to_thread,
            ) as to_thread:
                response = client.post(
                    "/api/incidents/current/designate_patient",
                    json={"patientUserId": "demo-patient"},
                )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(to_thread.called)

    def test_client_location_and_aed_site_can_be_updated(self) -> None:
        with self._client() as client:
            auth = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    display_name="测试终端",
                    phone="13800138009",
                    organization="测试组织",
                    health_condition="身体状态良好",
                    profession_identity="急救志愿者",
                    profile_bio="完成 CPR AED 培训并熟悉路线",
                ),
            )
            self.assertEqual(auth.status_code, 200)
            auth_payload = auth.json()
            user_id = auth_payload["user"]["userId"]
            registered = client.post(
                "/api/clients/register",
                headers={"Authorization": f"Bearer {auth_payload['token']}"},
                json={
                    "userId": user_id,
                    "displayName": "测试终端",
                    "organization": "测试组织",
                    "healthCondition": "身体状态良好",
                    "professionIdentity": "急救志愿者",
                    "profileBio": "完成 CPR AED 培训并熟悉路线",
                    "deviceType": "ANDROID",
                },
            )
            self.assertEqual(registered.status_code, 200)

            location = {
                "latitude": 39.9042,
                "longitude": 116.4074,
                "label": "测试点位",
                "source": "manual",
            }
            moved = client.post(
                "/api/clients/location",
                headers={"Authorization": f"Bearer {auth_payload['token']}"},
                json={"userId": user_id, "location": location},
            )
            self.assertEqual(moved.status_code, 200)

            aed = client.post(
                "/api/aed-sites",
                json={
                    "siteId": "test-aed",
                    "name": "测试 AED",
                    "location": location,
                    "status": "AVAILABLE",
                    "accessNotes": "测试备注",
                },
            )
            self.assertEqual(aed.status_code, 200)
            self.assertEqual(aed.json()["aedSites"][0]["siteId"], "test-aed")

            clients = client.get("/api/clients").json()["clients"]
            self.assertEqual(clients[0]["location"]["label"], "测试点位")

    def test_client_location_requires_matching_auth_token(self) -> None:
        with self._client() as client:
            auth = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    display_name="定位终端",
                    phone="13800138010",
                    organization="测试组织",
                    health_condition="身体状态良好",
                    profession_identity="急救志愿者",
                    profile_bio="完成 CPR AED 培训并熟悉路线",
                ),
            )
            self.assertEqual(auth.status_code, 200)
            auth_payload = auth.json()
            user_id = auth_payload["user"]["userId"]
            client.post(
                "/api/clients/register",
                headers={"Authorization": f"Bearer {auth_payload['token']}"},
                json={
                    "userId": user_id,
                    "displayName": "定位终端",
                    "organization": "测试组织",
                    "healthCondition": "身体状态良好",
                    "professionIdentity": "急救志愿者",
                    "profileBio": "完成 CPR AED 培训并熟悉路线",
                    "deviceType": "ANDROID",
                },
            )

            location = {"latitude": 39.9042, "longitude": 116.4074, "label": "伪造点位"}
            no_auth = client.post(
                "/api/clients/location",
                json={"userId": user_id, "location": location},
            )
            wrong_user = client.post(
                "/api/clients/location",
                headers={"Authorization": f"Bearer {auth_payload['token']}"},
                json={"userId": "other-user", "location": location},
            )

        self.assertEqual(no_auth.status_code, 401)
        self.assertEqual(wrong_user.status_code, 403)

    def test_demo_admin_token_protects_public_demo_mutations(self) -> None:
        token = "test-demo-admin"
        with self._client_with_demo_admin_token(token) as client:
            health = client.get("/api/health/detail")
            denied_create = client.post("/api/incidents")
            denied_bootstrap = client.post("/api/demo/bootstrap")
            denied_export = client.get("/api/experiments/current/export")
            denied_designate = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )
            allowed_create = client.post(
                "/api/incidents",
                headers={"X-Demo-Admin-Token": token},
            )
            allowed_bootstrap = client.post(
                "/api/demo/bootstrap",
                headers={"X-Demo-Admin-Token": token},
            )
            allowed_designate = client.post(
                "/api/incidents/current/designate_patient",
                headers={"X-Demo-Admin-Token": token},
                json={"patientUserId": "demo-patient"},
            )
            denied_join = client.post(
                f"/api/incidents/{allowed_create.json()['incidentId']}/join",
                json={"role": "PRIME", "userId": "demo-web-prime"},
            )
            allowed_join = client.post(
                f"/api/incidents/{allowed_create.json()['incidentId']}/join",
                headers={"X-Demo-Admin-Token": token},
                json={"role": "PRIME", "userId": "demo-web-prime"},
            )
            allowed_action = client.post(
                f"/api/incidents/{allowed_create.json()['incidentId']}/actions",
                headers={"X-Demo-Admin-Token": token},
                json={"action": "CPR_STARTED", "userId": "demo-web-prime"},
            )
            allowed_export = client.get(
                "/api/experiments/current/export",
                headers={"X-Demo-Admin-Token": token},
            )

        self.assertEqual(health.status_code, 200)
        self.assertTrue(health.json()["demoAdminAuthEnabled"])
        self.assertEqual(denied_create.status_code, 403)
        self.assertEqual(denied_bootstrap.status_code, 403)
        self.assertEqual(denied_export.status_code, 403)
        self.assertEqual(denied_designate.status_code, 403)
        self.assertEqual(allowed_create.status_code, 200)
        self.assertEqual(allowed_bootstrap.status_code, 200)
        self.assertEqual(allowed_designate.status_code, 200)
        self.assertEqual(denied_join.status_code, 401)
        self.assertEqual(allowed_join.status_code, 200)
        self.assertEqual(allowed_action.status_code, 200)
        self.assertEqual(allowed_export.status_code, 200)

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
