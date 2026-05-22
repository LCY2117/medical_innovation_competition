from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from io import BytesIO
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

    def _client_with_admin_phones(self, *phones: str) -> TestClient:
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
            demo_admin_token="test-demo-admin",
            admin_phones=tuple(phones),
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

    def _client_with_auth_rate_limit(self, limit: int = 1) -> TestClient:
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
            rate_limit_auth_per_minute=limit,
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
        self.assertEqual(payload["auth"]["tokenTtlSec"], self.settings.auth_token_ttl_sec)
        self.assertTrue(payload["features"]["experimentZipPackage"])
        self.assertEqual(payload["healthProvider"]["mode"], "mock")
        self.assertEqual(payload["mapProvider"]["mode"], "demo")
        self.assertEqual(payload["mapProvider"]["distanceSource"], "haversine_demo")
        self.assertEqual(payload["pushProvider"]["mode"], "websocket")
        self.assertEqual(payload["pushProvider"]["channel"], "websocket_state")
        self.assertEqual(payload["storage"]["auditEventCount"], 0)
        self.assertTrue(payload["security"]["auditLogEnabled"])
        self.assertTrue(payload["security"]["rateLimitEnabled"])
        self.assertEqual(payload["security"]["rateLimitAuthPerMinute"], self.settings.rate_limit_auth_per_minute)
        self.assertFalse(payload["frontend"]["indexReady"])
        self.assertFalse(payload["frontend"]["assetsReady"])
        self.assertEqual(payload["frontend"]["assetCount"], 0)
        self.assertFalse(payload["frontend"]["mobileChunkReady"])
        self.assertFalse(payload["frontend"]["desktopChunkReady"])
        self.assertFalse(payload["demoAdminAuthEnabled"])
        self.assertFalse(payload["demoReadiness"]["ready"])
        self.assertIn("尚未创建当前事件", payload["demoReadiness"]["warnings"])

        self.settings.web_dist_dir.mkdir(parents=True, exist_ok=True)
        (self.settings.web_dist_dir / "index.html").write_text("<html></html>", encoding="utf-8")
        assets_dir = self.settings.web_dist_dir / "assets"
        assets_dir.mkdir()
        (assets_dir / "MobileApp-test.js").write_text("console.log('mobile')", encoding="utf-8")
        (assets_dir / "App-test.js").write_text("console.log('app')", encoding="utf-8")
        with self._client() as client:
            ready_response = client.get("/api/health/detail")
        ready_payload = ready_response.json()
        self.assertTrue(ready_payload["frontend"]["ok"])
        self.assertTrue(ready_payload["frontend"]["indexReady"])
        self.assertTrue(ready_payload["frontend"]["assetsReady"])
        self.assertEqual(ready_payload["frontend"]["assetCount"], 2)
        self.assertTrue(ready_payload["frontend"]["mobileChunkReady"])
        self.assertTrue(ready_payload["frontend"]["desktopChunkReady"])

    def test_health_detail_reports_demo_readiness_after_bootstrap(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            response = client.get("/api/health/detail")

        self.assertEqual(bootstrapped.status_code, 200)
        self.assertEqual(response.status_code, 200)
        readiness = response.json()["demoReadiness"]
        self.assertTrue(readiness["ready"])
        self.assertEqual(readiness["clientCount"], 4)
        self.assertEqual(readiness["availableAedSiteCount"], 2)
        self.assertEqual(readiness["clientsWithLocation"], 4)
        self.assertEqual(readiness["clientsWithHealthSignals"], 4)
        self.assertEqual(readiness["healthCoveragePercent"], 100.0)
        self.assertTrue(readiness["exportReady"])
        self.assertEqual(readiness["warnings"], [])

    def test_dispatch_meta_is_serializable(self) -> None:
        with self._client() as client:
            response = client.get("/api/dispatch/meta")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("configured", payload)
        self.assertIn("provider", payload)
        self.assertIn("dispatchDelaySec", payload)
        self.assertIn("systemPrompt", payload)
        self.assertEqual(payload["mapProvider"]["mode"], "demo")
        self.assertIn("LRA_MAP_PROVIDER", payload["envKeys"])

    def test_amap_distance_provider_falls_back_without_service_key(self) -> None:
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
            map_provider="amap",
            amap_service_key=None,
        )
        with TestClient(create_app(settings)) as client:
            health = client.get("/api/health/detail")
            meta = client.get("/api/dispatch/meta")

        self.assertEqual(health.status_code, 200)
        provider = health.json()["mapProvider"]
        self.assertEqual(provider["requestedProvider"], "amap")
        self.assertEqual(provider["mode"], "amap")
        self.assertFalse(provider["configured"])
        self.assertEqual(provider["fallbackReason"], "amap_service_key_missing")
        self.assertEqual(provider["distanceSource"], "haversine_demo")
        self.assertEqual(meta.status_code, 200)
        self.assertEqual(meta.json()["mapProvider"]["fallbackReason"], "amap_service_key_missing")

    def test_push_provider_placeholder_falls_back_to_websocket(self) -> None:
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
            push_provider="jpush",
        )
        with TestClient(create_app(settings)) as client:
            health = client.get("/api/health/detail")
            bootstrapped = client.post("/api/demo/bootstrap")

        self.assertEqual(health.status_code, 200)
        provider = health.json()["pushProvider"]
        self.assertEqual(provider["requestedProvider"], "jpush")
        self.assertEqual(provider["mode"], "jpush")
        self.assertEqual(provider["activeProvider"], "websocket")
        self.assertEqual(provider["fallbackReason"], "jpush_adapter_pending")
        self.assertEqual(bootstrapped.status_code, 200)

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

    def test_demo_auth_personas_issue_reusable_sessions(self) -> None:
        with self._client() as client:
            patient = client.post("/api/auth/demo", json={"persona": "patient"})
            repeat_patient = client.post("/api/auth/demo", json={"persona": "patient"})
            prime = client.post("/api/auth/demo", json={"persona": "prime"})
            unknown = client.post("/api/auth/demo", json={"persona": "pilot"})
            me = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {patient.json()['token']}"},
            )

        self.assertEqual(patient.status_code, 200)
        self.assertEqual(repeat_patient.status_code, 200)
        self.assertEqual(prime.status_code, 200)
        self.assertEqual(unknown.status_code, 400)
        self.assertEqual(patient.json()["user"]["userId"], "demo-patient")
        self.assertEqual(repeat_patient.json()["user"]["userId"], "demo-patient")
        self.assertEqual(prime.json()["user"]["userId"], "demo-prime")
        self.assertNotEqual(patient.json()["token"], repeat_patient.json()["token"])
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["user"]["userId"], "demo-patient")

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

            repeated = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": user_ids["冠心病患者"]},
            )
            self.assertEqual(repeated.status_code, 200)
            repeated_payload = repeated.json()
            self.assertEqual(repeated_payload["assignments"]["PRIME"], user_ids["张医生"])

            current_after_repeat = client.get("/api/incidents/current")
            self.assertEqual(current_after_repeat.status_code, 200)
            current_after_repeat_payload = current_after_repeat.json()
            self.assertEqual(current_after_repeat_payload["phase"], "DISPATCHED")
            self.assertEqual(current_after_repeat_payload["dispatchRationale"]["PRIME"]["userId"], user_ids["张医生"])

    def test_health_risk_summary_deprioritizes_high_intensity_roles(self) -> None:
        with self._client() as client:
            registrations = [
                self._register_payload(
                    display_name="模拟患者",
                    phone="13800138201",
                    organization="社区",
                    health_condition="存在心脏骤停风险",
                    profession_identity="患者侧",
                    profile_bio="心血管病史，需要重点监护",
                ),
                self._register_payload(
                    display_name="风险跑者",
                    phone="13800138202",
                    organization="大学校园",
                    health_condition="身体素质良好",
                    profession_identity="有一定急救常识",
                    profile_bio="体育生，跑得快，熟悉校园路线，可快速取送 AED",
                ),
                self._register_payload(
                    display_name="稳健跑者",
                    phone="13800138203",
                    organization="大学校园",
                    health_condition="身体素质良好",
                    profession_identity="有一定急救常识",
                    profile_bio="熟悉校园路线，可快速取送 AED",
                ),
                self._register_payload(
                    display_name="张医生",
                    phone="13800138204",
                    organization="市医院急救科",
                    health_condition="身体状态一般",
                    profession_identity="医生 / 专业急救人员",
                    profile_bio="急救科医生，熟悉 CPR 和 AED 处置",
                ),
                self._register_payload(
                    display_name="安保老王",
                    phone="13800138205",
                    organization="校园安保",
                    health_condition="身体状态一般",
                    profession_identity="安保 / 物业 / 场地协调人员",
                    profile_bio="熟悉通道和救护车接驳",
                ),
            ]
            sessions = {}
            for payload in registrations:
                auth = client.post("/api/auth/register", json=payload)
                self.assertEqual(auth.status_code, 200)
                auth_payload = auth.json()
                user_id = auth_payload["user"]["userId"]
                token = auth_payload["token"]
                sessions[payload["displayName"]] = (user_id, token)
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

            risky_user_id, risky_token = sessions["风险跑者"]
            health_update = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {risky_token}"},
                json={
                    "userId": risky_user_id,
                    "healthSignals": {
                        "source": "mock",
                        "authorizationStatus": "authorized",
                        "heartRateBpm": 132,
                        "bloodOxygenPercent": 91,
                        "pressureScore": 85,
                        "riskTags": ["tachycardia", "low_spo2", "high_pressure"],
                    },
                },
            )
            self.assertEqual(health_update.status_code, 200)

            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": sessions["模拟患者"][0]},
            )
            self.assertEqual(dispatch.status_code, 200)
            payload = dispatch.json()
            meta = client.get("/api/dispatch/meta").json()

        self.assertEqual(payload["assignments"]["RUNNER"], sessions["稳健跑者"][0])
        self.assertNotEqual(payload["assignments"]["RUNNER"], risky_user_id)
        self.assertIn("healthSignals", meta["candidateFields"])

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
            self.assertEqual(payload["assignments"]["PRIME"], "demo-prime")
            self.assertEqual(payload["assignments"]["RUNNER"], "demo-runner")
            self.assertEqual(payload["assignments"]["GUIDE"], "demo-guide")
            self.assertGreater(payload["rationale"]["RUNNER"]["distanceToAedMeters"], 0)

            export = client.get("/api/experiments/current/export")
            self.assertEqual(export.status_code, 200)
            exported = export.json()
            self.assertEqual(exported["patientUserId"], "demo-patient")
            self.assertEqual(exported["assignments"]["RUNNER"], "demo-runner")
            self.assertIn("dispatchSeconds", exported["metrics"])
            self.assertEqual(exported["metrics"]["participantCount"], 4)
            self.assertEqual(exported["metrics"]["aedSiteCount"], 2)
            self.assertEqual(exported["metrics"]["clientsWithHealthSignals"], 4)
            self.assertEqual(exported["metrics"]["healthCoveragePercent"], 100.0)
            self.assertEqual(exported["metrics"]["roleAssignmentCompleteness"], 1.0)
            self.assertGreater(exported["metrics"]["runnerRouteMeters"], 0)
            self.assertTrue(exported["timeline"])
            patient = next(item for item in exported["clients"] if item["userId"] == "demo-patient")
            self.assertEqual(patient["healthSignals"]["source"], "mock")
            self.assertEqual(patient["healthSignals"]["authorizationStatus"], "sample")
            self.assertIn("low_spo2", patient["healthSignals"]["riskTags"])

            package = client.get("/api/experiments/current/package")
            self.assertEqual(package.status_code, 200)
            self.assertEqual(package.headers["content-type"], "application/zip")
            with zipfile.ZipFile(BytesIO(package.content)) as archive:
                names = set(archive.namelist())
                self.assertIn("experiment.json", names)
                self.assertIn("experiment_anonymized.json", names)
                self.assertIn("review_index.md", names)
                self.assertIn("expert_summary.md", names)
                self.assertIn("expert_review_checklist.md", names)
                self.assertIn("expert_feedback_form.md", names)
                self.assertIn("facilitator_run_sheet.md", names)
                self.assertIn("analysis_guide.md", names)
                self.assertIn("data_dictionary.md", names)
                self.assertIn("participant_consent_safety_brief.md", names)
                self.assertIn("clients.csv", names)
                self.assertIn("clients_anonymized.csv", names)
                self.assertIn("timeline.csv", names)
                self.assertIn("dispatch_rationale.csv", names)
                self.assertIn("observer_record_form.csv", names)
                self.assertIn("participant_questionnaire.csv", names)
                self.assertIn("baseline_vs_system_comparison.csv", names)
                self.assertIn("pre_experiment_round_summary.csv", names)
                self.assertIn("expert_feedback_summary.csv", names)
                self.assertIn("manifest.json", names)
                clients_csv = archive.read("clients.csv").decode("utf-8-sig")
                self.assertIn("heartRateBpm", clients_csv)
                self.assertIn("demo-patient", clients_csv)
                self.assertIn("sample", clients_csv)
                self.assertNotIn("OPPO Health mock", clients_csv)
                experiment_json = archive.read("experiment.json").decode("utf-8")
                self.assertIn('"authorizationStatus": "sample"', experiment_json)
                self.assertNotIn("OPPO Health mock", experiment_json)
                metrics_csv = archive.read("metrics.csv").decode("utf-8-sig")
                self.assertIn("healthCoveragePercent", metrics_csv)
                self.assertIn("runnerRouteMeters", metrics_csv)
                timeline_csv = archive.read("timeline.csv").decode("utf-8-sig")
                self.assertIn("tsIso", timeline_csv)
                self.assertIn("eventType", timeline_csv)
                self.assertIn("participantCode", timeline_csv)
                self.assertIn("ROLE_ASSIGNED", timeline_csv)
                self.assertIn("P001", timeline_csv)
                self.assertNotIn("actorUserId", timeline_csv)
                self.assertNotIn("demo-patient", timeline_csv)
                self.assertNotIn("demo-prime", timeline_csv)
                self.assertNotIn("demo-runner", timeline_csv)
                dispatch_rationale_csv = archive.read("dispatch_rationale.csv").decode("utf-8-sig")
                self.assertIn("participantCode", dispatch_rationale_csv)
                self.assertNotIn("userId", dispatch_rationale_csv.splitlines()[0])
                self.assertNotIn("demo-prime", dispatch_rationale_csv)
                self.assertNotIn("demo-runner", dispatch_rationale_csv)
                self.assertNotIn("demo-guide", dispatch_rationale_csv)
                anonymized_clients_csv = archive.read("clients_anonymized.csv").decode("utf-8-sig")
                self.assertIn("participantCode", anonymized_clients_csv)
                self.assertIn("P001", anonymized_clients_csv)
                self.assertNotIn("demo-patient", anonymized_clients_csv)
                anonymized_json = archive.read("experiment_anonymized.json").decode("utf-8")
                self.assertIn("participantMap", anonymized_json)
                self.assertIn("P001", anonymized_json)
                self.assertNotIn("demo-patient", anonymized_json)
                package_readme = archive.read("README.md").decode("utf-8")
                self.assertIn("build_pre_experiment_report.py", package_readme)
                self.assertIn("round-summary.csv", package_readme)
                self.assertIn("round-analysis.md", package_readme)
                self.assertIn("样例接入或演示来源", package_readme)
                review_index = archive.read("review_index.md").decode("utf-8")
                self.assertIn("生命反射弧证据包审阅索引", review_index)
                self.assertIn("建议 3 分钟打开顺序", review_index)
                self.assertIn("对外材料优先使用", review_index)
                self.assertIn("不宣称提高抢救成功率", review_index)
                self.assertIn("expert_feedback_summary.csv", review_index)
                self.assertIn("样例健康摘要或演示健康摘要", review_index)
                self.assertIn("患者代号：P001", review_index)
                self.assertNotIn("demo-patient", review_index)
                self.assertNotIn("demo-prime", review_index)
                expert_summary = archive.read("expert_summary.md").decode("utf-8")
                self.assertIn("生命反射弧预实验专家摘要", expert_summary)
                self.assertIn("数据使用边界", expert_summary)
                self.assertIn("样例接入或演示来源", expert_summary)
                review_checklist = archive.read("expert_review_checklist.md").decode("utf-8")
                self.assertIn("生命反射弧专家现场复核清单", review_checklist)
                self.assertIn("安全边界", review_checklist)
                expert_feedback = archive.read("expert_feedback_form.md").decode("utf-8")
                self.assertIn("生命反射弧事件级专家反馈与签字表", expert_feedback)
                self.assertIn("专家签字", expert_feedback)
                self.assertIn("不构成真实临床疗效证明", expert_feedback)
                run_sheet = archive.read("facilitator_run_sheet.md").decode("utf-8")
                self.assertIn("生命反射弧预实验主持人跑场单", run_sheet)
                self.assertIn("演练前 5 分钟检查", run_sheet)
                self.assertIn("不用于真实患者处置", run_sheet)
                analysis_guide = archive.read("analysis_guide.md").decode("utf-8")
                self.assertIn("预实验数据分析说明", analysis_guide)
                self.assertIn("多轮 ZIP 一键汇总", analysis_guide)
                self.assertIn("build_pre_experiment_report.py", analysis_guide)
                self.assertIn("T1-T6", analysis_guide)
                self.assertIn("避免写法", analysis_guide)
                data_dictionary = archive.read("data_dictionary.md").decode("utf-8")
                self.assertIn("证据包数据字典", data_dictionary)
                self.assertIn("runnerRouteMeters", data_dictionary)
                self.assertIn("round-summary.csv", data_dictionary)
                self.assertIn("角色代码", data_dictionary)
                self.assertIn("禁止表述", data_dictionary)
                safety_brief = archive.read("participant_consent_safety_brief.md").decode("utf-8")
                self.assertIn("参与者知情与安全边界简表", safety_brief)
                self.assertIn("参与者可随时暂停或退出", safety_brief)
                self.assertIn("样例接入或演示来源", safety_brief)
                observer_form = archive.read("observer_record_form.csv").decode("utf-8-sig")
                self.assertIn("observerValue", observer_form)
                self.assertIn("role_assignment_clarity", observer_form)
                participant_questionnaire = archive.read("participant_questionnaire.csv").decode("utf-8-sig")
                self.assertIn("participantCode", participant_questionnaire)
                self.assertIn("Q05", participant_questionnaire)
                self.assertIn("安全边界提示清楚", participant_questionnaire)
                comparison = archive.read("baseline_vs_system_comparison.csv").decode("utf-8-sig")
                self.assertIn("baselineRoundId", comparison)
                self.assertIn("systemRoundId", comparison)
                self.assertIn("cprStartSecondsDelta", comparison)
                self.assertIn("aedDeliverySecondsChangePercent", comparison)
                round_summary = archive.read("pre_experiment_round_summary.csv").decode("utf-8-sig")
                self.assertIn("roundId", round_summary)
                self.assertIn("roleAssignmentCompleteness", round_summary)
                self.assertIn("healthCoveragePercent", round_summary)
                feedback_summary = archive.read("expert_feedback_summary.csv").decode("utf-8-sig")
                self.assertIn("feedbackId", feedback_summary)
                self.assertIn("requiredImprovement", feedback_summary)
                self.assertIn("secondReviewComment", feedback_summary)
                manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
                self.assertEqual(manifest["incidentId"], exported["incidentId"])
                self.assertIn("generatedAtIso", manifest)
                self.assertEqual(manifest["packageType"], "LifeReflexArc pre-experiment evidence package")
                self.assertEqual(manifest["verification"]["algorithm"], "SHA-256")
                self.assertIn("review_index.md", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("experiment_anonymized.json", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("expert_review_checklist.md", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("expert_feedback_form.md", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("facilitator_run_sheet.md", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("analysis_guide.md", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("data_dictionary.md", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("participant_consent_safety_brief.md", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("observer_record_form.csv", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("participant_questionnaire.csv", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("baseline_vs_system_comparison.csv", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("pre_experiment_round_summary.csv", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("expert_feedback_summary.csv", manifest["privacyGuidance"]["publicOrExpertReview"])
                self.assertIn("experiment.json", manifest["privacyGuidance"]["internalReviewOnly"])
                manifest_files = {item["fileName"]: item for item in manifest["files"]}
                self.assertIn("review_index.md", manifest_files)
                self.assertIn("expert_summary.md", manifest_files)
                self.assertIn("expert_review_checklist.md", manifest_files)
                self.assertIn("expert_feedback_form.md", manifest_files)
                self.assertIn("facilitator_run_sheet.md", manifest_files)
                self.assertIn("analysis_guide.md", manifest_files)
                self.assertIn("data_dictionary.md", manifest_files)
                self.assertIn("participant_consent_safety_brief.md", manifest_files)
                self.assertIn("observer_record_form.csv", manifest_files)
                self.assertIn("participant_questionnaire.csv", manifest_files)
                self.assertIn("baseline_vs_system_comparison.csv", manifest_files)
                self.assertIn("pre_experiment_round_summary.csv", manifest_files)
                self.assertIn("expert_feedback_summary.csv", manifest_files)
                for name, entry in manifest_files.items():
                    content = archive.read(name)
                    self.assertEqual(hashlib.sha256(content).hexdigest(), entry["sha256"])

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
        self.assertEqual(dispatch.json()["assignments"]["PRIME"], "demo-prime")

    def test_historical_export_uses_target_incident_roles(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            self.assertEqual(bootstrapped.status_code, 200)
            old_incident_id = bootstrapped.json()["incidentId"]
            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )
            self.assertEqual(dispatch.status_code, 200)

            created = client.post("/api/incidents")
            self.assertEqual(created.status_code, 200)
            self.assertNotEqual(created.json()["incidentId"], old_incident_id)
            current_export = client.get("/api/experiments/current/export")
            self.assertEqual(current_export.status_code, 200)
            current_clients = current_export.json()["clients"]
            current_prime = next(item for item in current_clients if item["userId"] == "demo-prime")
            self.assertIsNone(current_prime["assignedRole"])

            old_export = client.get(f"/api/experiments/{old_incident_id}/export")
            self.assertEqual(old_export.status_code, 200)
            old_payload = old_export.json()
            old_prime = next(item for item in old_payload["clients"] if item["userId"] == "demo-prime")
            old_patient = next(item for item in old_payload["clients"] if item["userId"] == "demo-patient")
            old_package = client.get(f"/api/experiments/{old_incident_id}/package")
            self.assertEqual(old_package.status_code, 200)
            current_package = client.get("/api/experiments/current/package")
            self.assertEqual(current_package.status_code, 200)

        self.assertEqual(old_payload["assignments"]["PRIME"], "demo-prime")
        self.assertEqual(old_prime["assignedRole"], "PRIME")
        self.assertTrue(old_patient["isPatient"])
        with zipfile.ZipFile(BytesIO(old_package.content)) as archive:
            old_manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        with zipfile.ZipFile(BytesIO(current_package.content)) as archive:
            current_manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        self.assertEqual(old_manifest["incidentId"], old_incident_id)
        self.assertNotEqual(current_manifest["incidentId"], old_incident_id)

    def test_evidence_package_verification_script_accepts_current_package(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            self.assertEqual(bootstrapped.status_code, 200)
            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )
            self.assertEqual(dispatch.status_code, 200)
            package = client.get("/api/experiments/current/package")
            self.assertEqual(package.status_code, 200)

        package_path = self.root / "lifereflex-evidence.zip"
        package_path.write_bytes(package.content)
        script_path = Path(__file__).resolve().parents[2] / "scripts" / "verify_evidence_package.py"
        result = subprocess.run(
            [sys.executable, str(script_path), str(package_path)],
            cwd=script_path.parent.parent,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: evidence package manifest", result.stdout)

    def test_evidence_round_summary_script_merges_packages(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            self.assertEqual(bootstrapped.status_code, 200)
            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )
            self.assertEqual(dispatch.status_code, 200)
            package = client.get("/api/experiments/current/package")
            self.assertEqual(package.status_code, 200)

        package_path = self.root / "lifereflex-evidence.zip"
        output_path = self.root / "round-summary.csv"
        package_path.write_bytes(package.content)
        script_path = Path(__file__).resolve().parents[2] / "scripts" / "summarize_evidence_rounds.py"
        result = subprocess.run(
            [sys.executable, str(script_path), str(package_path), "--output", str(output_path)],
            cwd=script_path.parent,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: summarized 1 evidence round", result.stdout)
        summary = output_path.read_text(encoding="utf-8-sig")
        self.assertIn("packageSha256", summary)
        self.assertIn("verificationStatus", summary)
        self.assertIn("manifestIncidentId", summary)
        self.assertIn("roleAssignmentCompleteness", summary)
        self.assertIn("OK", summary)
        self.assertIn(bootstrapped.json()["incidentId"], summary)

    def test_round_summary_analysis_script_writes_ppt_safe_report(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            self.assertEqual(bootstrapped.status_code, 200)
            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )
            self.assertEqual(dispatch.status_code, 200)
            package = client.get("/api/experiments/current/package")
            self.assertEqual(package.status_code, 200)

        package_path = self.root / "lifereflex-evidence.zip"
        summary_path = self.root / "round-summary.csv"
        report_path = self.root / "round-analysis.md"
        package_path.write_bytes(package.content)
        scripts_dir = Path(__file__).resolve().parents[2] / "scripts"

        summary_result = subprocess.run(
            [
                sys.executable,
                str(scripts_dir / "summarize_evidence_rounds.py"),
                str(package_path),
                "--output",
                str(summary_path),
            ],
            cwd=scripts_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        report_result = subprocess.run(
            [
                sys.executable,
                str(scripts_dir / "analyze_round_summary.py"),
                str(summary_path),
                "--output",
                str(report_path),
            ],
            cwd=scripts_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(summary_result.returncode, 0, summary_result.stderr)
        self.assertEqual(report_result.returncode, 0, report_result.stderr)
        report = report_path.read_text(encoding="utf-8")
        self.assertIn("生命反射弧预实验多轮分析摘要", report)
        self.assertIn("T1 触发到分派完成", report)
        self.assertIn("校验通过轮次：1", report)
        self.assertIn("| 角色分派完整度 `roleAssignmentCompleteness` | 1 | 100 | 100 | 100 | 100 |", report)
        self.assertIn("不应表述为：提高真实抢救成功率", report)
        self.assertIn(bootstrapped.json()["incidentId"], report)

    def test_pre_experiment_report_builder_creates_summary_and_analysis(self) -> None:
        with self._client() as client:
            bootstrapped = client.post("/api/demo/bootstrap")
            self.assertEqual(bootstrapped.status_code, 200)
            dispatch = client.post(
                "/api/incidents/current/designate_patient",
                json={"patientUserId": "demo-patient"},
            )
            self.assertEqual(dispatch.status_code, 200)
            package = client.get("/api/experiments/current/package")
            self.assertEqual(package.status_code, 200)

        package_path = self.root / "lifereflex-evidence.zip"
        output_dir = self.root / "analysis-output"
        package_path.write_bytes(package.content)
        scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
        result = subprocess.run(
            [
                sys.executable,
                str(scripts_dir / "build_pre_experiment_report.py"),
                str(package_path),
                "--output-dir",
                str(output_dir),
            ],
            cwd=scripts_dir,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: summarized 1 evidence round", result.stdout)
        summary = (output_dir / "round-summary.csv").read_text(encoding="utf-8-sig")
        report = (output_dir / "round-analysis.md").read_text(encoding="utf-8")
        self.assertIn("verificationStatus", summary)
        self.assertIn(bootstrapped.json()["incidentId"], summary)
        self.assertIn("生命反射弧预实验多轮分析摘要", report)
        self.assertIn("角色分派完整度", report)

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

    def test_patient_sos_with_dispatch_delay_completes_auto_dispatch(self) -> None:
        settings = Settings(
            app_name=self.settings.app_name,
            api_prefix=self.settings.api_prefix,
            host=self.settings.host,
            port=self.settings.port,
            reload=self.settings.reload,
            sos_duration_sec=1,
            dispatch_delay_sec=1,
            cors_origins=self.settings.cors_origins,
            db_path=self.settings.db_path,
            web_dist_dir=self.settings.web_dist_dir,
        )
        with TestClient(create_app(settings)) as client:
            incident_id = client.get("/api/incidents/current").json()["incidentId"]
            patient_token = ""

            for payload in [
                self._register_payload("延迟患者", "13800138201", "社区", "存在心脏骤停风险", "患者侧", "用于正延迟自动分派测试"),
                self._register_payload("延迟医生", "13800138202", "医院", "身体状态一般", "医生 / 专业急救人员", "用于正延迟自动分派测试"),
                self._register_payload("延迟跑者", "13800138203", "校园", "身体素质良好", "有一定急救常识", "用于正延迟自动分派测试"),
                self._register_payload("延迟引导员", "13800138204", "物业", "身体状态一般", "安保 / 物业", "用于正延迟自动分派测试"),
            ]:
                auth = client.post("/api/auth/register", json=payload)
                self.assertEqual(auth.status_code, 200)
                auth_payload = auth.json()
                token = auth_payload["token"]
                user_id = auth_payload["user"]["userId"]
                if payload["displayName"] == "延迟患者":
                    patient_token = token
                registered = client.post(
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
                self.assertEqual(registered.status_code, 200)

            started = client.post(
                f"/api/incidents/{incident_id}/patient_sos_start",
                headers={"Authorization": f"Bearer {patient_token}"},
            )

            current = {}
            for _ in range(20):
                current = client.get("/api/incidents/current").json()
                if current["phase"] == "DISPATCHED":
                    break
                import time

                time.sleep(0.2)

        self.assertEqual(started.status_code, 200)
        self.assertEqual(current["phase"], "DISPATCHED")
        self.assertEqual(current["roles"]["PRIME"]["status"], "ASSIGNED")
        self.assertEqual(current["roles"]["RUNNER"]["status"], "ASSIGNED")
        self.assertEqual(current["roles"]["GUIDE"]["status"], "ASSIGNED")

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

    def test_input_validation_rejects_invalid_location_health_and_aed_status(self) -> None:
        with self._client() as client:
            auth = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    display_name="边界测试",
                    phone="13800138666",
                    organization="测试组织",
                    health_condition="身体状态一般",
                    profession_identity="急救志愿者",
                    profile_bio="用于输入边界校验",
                ),
            )
            self.assertEqual(auth.status_code, 200)
            auth_payload = auth.json()
            user_id = auth_payload["user"]["userId"]
            token = auth_payload["token"]
            registered = client.post(
                "/api/clients/register",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "displayName": "边界测试",
                    "organization": "测试组织",
                    "healthCondition": "身体状态一般",
                    "professionIdentity": "急救志愿者",
                    "profileBio": "用于输入边界校验",
                    "deviceType": "MOBILE_WEB",
                },
            )
            bad_location = client.post(
                "/api/clients/location",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "location": {
                        "latitude": 120,
                        "longitude": 116.4,
                        "accuracyMeters": -1,
                    },
                },
            )
            bad_health = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "healthSignals": {
                        "source": "mock",
                        "authorizationStatus": "authorized",
                        "heartRateBpm": 300,
                        "bloodOxygenPercent": 101,
                        "pressureScore": -2,
                    },
                },
            )
            bad_health_source = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "healthSignals": {
                        "source": "clinical-monitor",
                        "authorizationStatus": "sample",
                    },
                },
            )
            bad_health_auth = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "healthSignals": {
                        "source": "mock",
                        "authorizationStatus": "real_clinical_authorized",
                    },
                },
            )
            bad_health_activity = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "healthSignals": {
                        "source": "mock",
                        "authorizationStatus": "sample",
                        "activityLevel": "sprint",
                        "sleepQuality": "diagnosed",
                    },
                },
            )
            bad_health_risk_tag = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "healthSignals": {
                        "source": "mock",
                        "authorizationStatus": "sample",
                        "riskTags": ["diagnosis_confirmed"],
                    },
                },
            )
            bad_aed = client.post(
                "/api/aed-sites",
                json={
                    "siteId": "bad-aed",
                    "name": "异常 AED",
                    "location": {"latitude": 39.9, "longitude": 116.4},
                    "status": "BROKEN",
                },
            )
            normalized_aed = client.post(
                "/api/aed-sites",
                json={
                    "siteId": "maint-aed",
                    "name": "维护中 AED",
                    "location": {"latitude": 39.9, "longitude": 116.4},
                    "status": "maintenance",
                },
            )

        self.assertEqual(registered.status_code, 200)
        self.assertEqual(bad_location.status_code, 422)
        self.assertEqual(bad_health.status_code, 422)
        self.assertEqual(bad_health_source.status_code, 422)
        self.assertEqual(bad_health_auth.status_code, 422)
        self.assertEqual(bad_health_activity.status_code, 422)
        self.assertEqual(bad_health_risk_tag.status_code, 422)
        self.assertEqual(bad_aed.status_code, 422)
        self.assertEqual(normalized_aed.status_code, 200)
        self.assertEqual(normalized_aed.json()["aedSites"][0]["status"], "MAINTENANCE")

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

    def test_client_health_signals_can_be_updated_and_exported(self) -> None:
        with self._client() as client:
            auth = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    display_name="健康终端",
                    phone="13800138011",
                    organization="测试组织",
                    health_condition="身体状态一般",
                    profession_identity="急救志愿者",
                    profile_bio="用于 OPPO 健康 mock/fallback 测试",
                ),
            )
            self.assertEqual(auth.status_code, 200)
            auth_payload = auth.json()
            user_id = auth_payload["user"]["userId"]
            token = auth_payload["token"]
            registered = client.post(
                "/api/clients/register",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "displayName": "健康终端",
                    "organization": "测试组织",
                    "healthCondition": "身体状态一般",
                    "professionIdentity": "急救志愿者",
                    "profileBio": "用于 OPPO 健康 mock/fallback 测试",
                    "deviceType": "ANDROID",
                    "healthSignals": {
                        "source": "MOCK",
                        "authorizationStatus": "SAMPLE",
                        "heartRateBpm": 82,
                        "bloodOxygenPercent": 98,
                        "pressureScore": 30,
                        "riskTags": [],
                        "note": "initial mock snapshot",
                    },
                },
            )
            self.assertEqual(registered.status_code, 200)

            updated = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": user_id,
                    "healthSignals": {
                        "source": "manual",
                        "authorizationStatus": "sample",
                        "heartRateBpm": 126,
                        "bloodOxygenPercent": 91,
                        "pressureScore": 78,
                        "activityLevel": "LOW",
                        "sleepQuality": "POOR",
                        "riskTags": ["tachycardia", "low-spo2", "tachycardia"],
                        "note": "manual fallback snapshot",
                    },
                },
            )
            self.assertEqual(updated.status_code, 200)

            no_auth = client.post(
                "/api/clients/health",
                json={
                    "userId": user_id,
                    "healthSignals": {"source": "mock", "authorizationStatus": "authorized"},
                },
            )
            wrong_user = client.post(
                "/api/clients/health",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "userId": "other-user",
                    "healthSignals": {"source": "mock", "authorizationStatus": "authorized"},
                },
            )
            clients = client.get("/api/clients").json()["clients"]
            export = client.get("/api/experiments/current/export").json()

        self.assertEqual(no_auth.status_code, 401)
        self.assertEqual(wrong_user.status_code, 403)
        health = next(item for item in clients if item["userId"] == user_id)["healthSignals"]
        self.assertEqual(health["source"], "manual")
        self.assertEqual(health["authorizationStatus"], "sample")
        self.assertEqual(health["heartRateBpm"], 126)
        self.assertEqual(health["activityLevel"], "low")
        self.assertEqual(health["sleepQuality"], "poor")
        self.assertIsInstance(health["updatedTs"], int)
        exported_health = next(item for item in export["clients"] if item["userId"] == user_id)["healthSignals"]
        self.assertEqual(exported_health["riskTags"], ["tachycardia", "low_spo2"])

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

    def test_configured_admin_account_can_manage_demo(self) -> None:
        admin_phone = "13800130001"
        user_phone = "13800130002"
        with self._client_with_admin_phones(admin_phone) as client:
            admin_register = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    "管理员",
                    admin_phone,
                    "医创赛团队",
                    "身体状态良好",
                    "项目负责人",
                    "负责演示管理和数据导出",
                ),
            )
            user_register = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    "普通成员",
                    user_phone,
                    "医创赛团队",
                    "身体状态良好",
                    "志愿者",
                    "只参与手机端现场演示",
                ),
            )

            admin_token = admin_register.json()["token"]
            user_token = user_register.json()["token"]
            admin_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
            denied = client.post("/api/demo/bootstrap", headers={"Authorization": f"Bearer {user_token}"})
            bootstrapped = client.post("/api/demo/bootstrap", headers={"Authorization": f"Bearer {admin_token}"})
            role_join = client.post(
                f"/api/incidents/{bootstrapped.json()['incidentId']}/join",
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"role": "PRIME", "userId": "dashboard-prime"},
            )
            audit_log = client.get("/api/audit/events?limit=20", headers={"Authorization": f"Bearer {admin_token}"})
            health = client.get("/api/health/detail")

        self.assertEqual(admin_register.status_code, 200)
        self.assertEqual(user_register.status_code, 200)
        self.assertIn("admin", admin_me.json()["user"]["privileges"])
        self.assertEqual(denied.status_code, 403)
        self.assertEqual(bootstrapped.status_code, 200)
        self.assertEqual(role_join.status_code, 200)
        self.assertEqual(audit_log.status_code, 200)
        event_types = {event["eventType"] for event in audit_log.json()["events"]}
        self.assertIn("admin_user_denied", event_types)
        self.assertIn("demo_bootstrapped", event_types)
        self.assertTrue(health.json()["auth"]["adminAccountAuthEnabled"])
        self.assertEqual(health.json()["auth"]["adminPhoneCount"], 1)

    def test_admin_phones_without_demo_token_keep_admin_apis_closed(self) -> None:
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
            admin_phones=("13800130003",),
        )
        with TestClient(create_app(settings)) as client:
            open_bootstrap = client.post("/api/demo/bootstrap")
            register = client.post(
                "/api/auth/register",
                json=self._register_payload(
                    "正式管理员",
                    "13800130003",
                    "医创赛团队",
                    "身体状态良好",
                    "项目负责人",
                    "负责系统管理和预实验导出",
                ),
            )
            token = register.json()["token"]
            admin_bootstrap = client.post("/api/demo/bootstrap", headers={"Authorization": f"Bearer {token}"})

        self.assertEqual(open_bootstrap.status_code, 403)
        self.assertEqual(register.status_code, 200)
        self.assertEqual(admin_bootstrap.status_code, 200)

    def test_audit_events_capture_sensitive_demo_and_actor_actions(self) -> None:
        token = "test-demo-admin"
        with self._client_with_demo_admin_token(token) as client:
            denied_bootstrap = client.post("/api/demo/bootstrap")
            bootstrapped = client.post(
                "/api/demo/bootstrap",
                headers={"X-Demo-Admin-Token": token},
            )
            designated = client.post(
                "/api/incidents/current/designate_patient",
                headers={"X-Demo-Admin-Token": token},
                json={"patientUserId": "demo-patient"},
            )
            joined = client.post(
                f"/api/incidents/{bootstrapped.json()['incidentId']}/join",
                headers={"X-Demo-Admin-Token": token},
                json={"role": "PRIME", "userId": "demo-prime"},
            )
            package = client.get(
                "/api/experiments/current/package",
                headers={"X-Demo-Admin-Token": token},
            )
            audit_log = client.get(
                "/api/audit/events?limit=20",
                headers={"X-Demo-Admin-Token": token},
            )
            health = client.get("/api/health/detail")

        self.assertEqual(denied_bootstrap.status_code, 403)
        self.assertEqual(bootstrapped.status_code, 200)
        self.assertEqual(designated.status_code, 200)
        self.assertEqual(joined.status_code, 200)
        self.assertEqual(package.status_code, 200)
        self.assertEqual(audit_log.status_code, 200)
        events = audit_log.json()["events"]
        event_types = {event["eventType"] for event in events}
        self.assertIn("demo_admin_denied", event_types)
        self.assertIn("demo_bootstrapped", event_types)
        self.assertIn("patient_designated", event_types)
        self.assertIn("role_joined", event_types)
        self.assertIn("experiment_package_exported", event_types)
        self.assertTrue(all("requestHash" in event for event in events))
        self.assertGreater(health.json()["storage"]["auditEventCount"], 0)

    def test_auth_rate_limit_returns_429(self) -> None:
        with self._client_with_auth_rate_limit(limit=1) as client:
            first = client.post("/api/auth/login", json={"phone": "13800139999", "password": "bad"})
            second = client.post("/api/auth/login", json={"phone": "13800139999", "password": "bad"})

        self.assertEqual(first.status_code, 401)
        self.assertEqual(second.status_code, 429)

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
