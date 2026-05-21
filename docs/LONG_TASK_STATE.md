# Long Task State

## Current Status

- Status: running
- Task: OPPO Health data enhancement phase 1
- Branch: codex/competition-hardening
- HEAD: 5a18fc5
- Last update: 2026-05-22 03:03:00 +08:00
- Workspace: D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧

## Goal

Complete OPPO Health data enhancement phase 1: application/material verification, SDK integration preparation, mock/fallback health-data flow, three-end display/export integration, and if official conditions allow, attempt real SDK compilation and authorization-page launch.

## Safety Rules

- Do not expose or commit credentials, API keys, client secrets, `.env`, keystores, or OPPO account details.
- Do not accept legal agreements, submit OPPO health permission applications, publish apps, delete apps, or perform irreversible OPPO-console actions unattended.
- Do not revert unrelated dirty work.
- If OPPO login, verification, legal agreement, health-data permission approval, or secret-copying is required, record it in `docs/LONG_TASK_BLOCKERS.md` and continue independent work.
- Do not commit unless a coherent checkpoint is ready and secrets/unrelated files are excluded.

## Current Milestone

1. Establish task anchors and inspect OPPO/app state. (done)
2. Build OPPO Health mock/fallback data path. (done)
3. Integrate Android/Web/backend display and experiment export. (done, validating)
4. Try real SDK dependency/authorization only if non-blocked. (blocked by approval/secrets/user authorization; documented prep only)
5. Validate and create a Git backup/checkpoint if safe. (in progress)
6. Continue competition hardening after checkpoint: improve pre-experiment export/evidence package. (done, checkpointing)
7. Improve deployment/operations observability through richer health detail. (done, checkpointing)
8. Feed OPPO/mock health summaries into dispatch scoring and rationale. (done, checkpointing)
9. Smoke-check Web UI after evidence package and health-summary additions. (done)
10. Strengthen pre-experiment evidence integrity: anonymized package, manifest hashes, structured timeline, richer metrics, historical export correctness, and demo readiness. (done, validating)
11. Wire Android app auto-join entry into the current AppRoot flow. (done, checkpointing)
12. Add Web command-center flow stepper and 4-terminal demo-stage runbook. (done, checkpointing)
13. Add mobile Web SOS two-step confirmation to reduce accidental emergency triggering. (done, checkpointing)
14. Add input boundary validation for location, health summaries, and AED status. (done, validating)
15. Update morning handoff with OPPO phase 1, evidence package, demo guidance, validation, and latest checkpoints. (done, checkpointing)
16. Localize health-risk tags and remove mock/fallback wording from user-facing health cards. (done, checkpointing)
17. Align pre-experiment, deployment, expert feedback, product plan, and whitepaper docs to the ZIP evidence package. (done, validating)
18. Add manifest privacy guidance and verification metadata for evidence packages. (done, validating)
19. Fold mobile Web manual role takeover under a demo backup control. (done, validating)
20. Add recent on-site timeline cards to Android task and incident screens. (done, validating)
21. Commit evidence/mobile/Android polish checkpoint. (done)
22. Push current checkpoints to GitHub. (done)
23. Add Android Runner full-screen AED target card. (done, validating)
24. Push Android AED target checkpoint. (done)
25. Add mobile Web PRIME next-step CPR/AED guidance card. (done, validating)
26. Push mobile Web PRIME next-step checkpoint. (done)

## Sub-Agent Ledger

- Web/mobile explorer (`019e4b97-e5bd-7200-a64b-fb9c42167d8e`): completed read-only; identified `ClientInfo.healthSignals`, Web console, `/mobile`, and export insertion points.
- Android explorer (`019e4b98-1336-70d0-b06d-72d187a79a14`): completed read-only; identified Kotlin provider, register, DTO, and UI insertion points.
- OPPO docs explorer (`019e4b98-45d3-7fb3-96c0-c6831d5d5701`): completed read-only; produced checklist-ready OPPO materials and blockers.
- Web/mobile UI explorer (`019e4bb7-9d4e-7372-9536-5ab5537730b1`): completed read-only; recommended demo stepper, mobile demo script, SOS confirm, task fallback folding, and next-action cards.
- Backend evidence explorer (`019e4bb7-b138-7263-abf1-99c38ba0bfa5`): completed read-only; recommended target-incident export roles, ZIP manifest, richer metrics, structured timeline, demo readiness, and input constraints.
- Android APK explorer (`019e4bb7-c511-78f2-af54-44692d632c16`): completed read-only; recommended wiring auto-join, adding timeline visibility, Chinese health presentation, demo location switching, and AED/CPR status cards.

## Git Baseline

Current working tree was already dirty before OPPO phase 1. Treat existing changes as user/Codex prior work and avoid broad cleanup.

```text
## codex/competition-hardening...origin/codex/competition-hardening
 M lifereflex(app)/app/build.gradle.kts
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/ApiService.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/AuthModels.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/AuthRepository.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/IncidentModels.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/IncidentRepository.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/UserSession.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/WsClient.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/AppRoot.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/components/FormFields.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/LoginScreen.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/ShellScreens.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/viewmodel/IncidentViewModel.kt
 M lifereflex(app)/app/src/main/java/com/example/lifereflexarc/viewmodel/SessionViewModel.kt
 M lifereflex(app)/build.gradle.kts
 M lifereflex(app)/gradle.properties
 M server(web)/data/lifereflexarc.db
?? OPPO健康SDK文档.md
?? docs/
?? lifereflex(app)/app/proguard-rules.pro
?? lifereflex(app)/app/src/main/AndroidManifest.xml
?? lifereflex(app)/app/src/main/res/
?? lifereflex(app)/gradle/
?? output/
```

## Files Changed Or Being Edited This Task

- `docs/LONG_TASK_STATE.md`
- `docs/LONG_TASK_BLOCKERS.md`
- `docs/OPPO_HEALTH_INTEGRATION_CHECKLIST.md`
- `server(web)/.env.example`
- `server(web)/app/models/schemas.py`
- `server(web)/app/api/rest.py`
- `server(web)/app/services/incidents.py`
- `server(web)/tests/test_server.py`
- `server(web)/web/src/shared/types.ts`
- `server(web)/web/src/shared/domain.ts`
- `server(web)/web/src/shared/api.ts`
- `server(web)/web/src/app/App.tsx`
- `server(web)/web/src/mobile/MobileApp.tsx`
- `server(web)/web/src/mobile/mobile.css`
- `lifereflex(app)/app/src/main/AndroidManifest.xml`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/IncidentModels.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/HealthSignalProvider.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/ApiService.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/IncidentRepository.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/viewmodel/IncidentViewModel.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/AppRoot.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/ShellScreens.kt`

## Last Completed Step

- Backend `HealthSignalSummary` model, `/clients/health`, persistence, demo data, and export integration are implemented.
- Web console and `/mobile` show mock/OPPO health summaries; mobile web also syncs a mock health summary after login/demo entry.
- Android app has `HealthSignalProvider`, `MockOppoHealthSignalProvider`, OPPO package visibility, server sync, and Compose health summary cards.
- OPPO checklist doc added.
- Evidence package now includes anonymized JSON/CSV, `expert_summary.md`, structured `timeline.csv`, richer experiment metrics, and `manifest.json` with SHA256 hashes.
- Historical event export now derives participant roles/patient flags from the target incident instead of the current incident.
- `/api/health/detail` now reports `demoReadiness` with readiness warnings, location coverage, health coverage, AED availability, and export readiness.
- Android Home and Incident tabs now expose the existing auto-join flow, passing the logged-in token and routing the user to Tasks after auto-join.
- Web dashboard now shows a five-step competition demo flow: scenario bootstrap, patient SOS, AI dispatch, field response, and handover/export.
- `/mobile-demo` now shows a compact runbook above the four terminal frames so a presenter can follow the correct sequence without separate notes.
- Mobile Web patient SOS now requires a second confirmation click before calling the backend start endpoint.
- Backend schemas now reject invalid latitude/longitude, negative accuracy, out-of-range health values, and unsupported AED status while normalizing valid AED status values.
- `docs/MORNING_HANDOFF.md` is updated with latest checkpoints, validation status, demo script, and evidence-package guidance.
- Web, mobile Web, and Android now present health-risk tags in Chinese, such as 心率偏快、血氧偏低、压力偏高, and Android frames OPPO health data as a demo health-data integration instead of raw mock/fallback text.
- Pre-experiment protocol, deployment runbook, expert feedback template, product optimization plan, and technical landing whitepaper now consistently describe the ZIP evidence package rather than a JSON-only export.
- Evidence package `manifest.json` now includes package type, anonymized-file guidance, internal-review-only file guidance, and SHA-256 verification metadata.
- Mobile Web keeps manual PRIME/RUNNER/GUIDE role takeover available only under a collapsed “演示备用” control, so the default task path supports the AI dispatch story.
- Android task and incident screens now show the latest six on-site timeline logs with Chinese summaries for patient SOS, dispatch, CPR, AED, ambulance, handover, and archive events.
- Android Runner full-screen task now shows target AED name, location/floor/status, access notes, distance to AED, and AED return distance to patient using existing dispatch rationale and AED-site data.
- Mobile Web PRIME task card now shows the next CPR/AED step: start CPR, wait for AED, AED returning, attach pads, stop touching during analysis, or resume CPR after shock.

## Validation Log

- Backend targeted tests: `.\.venv\Scripts\python.exe -m unittest tests.test_server -v` passed, 22 tests OK.
- Backend full tests: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 26 tests OK.
- Web typecheck: `npm run typecheck` passed.
- Web production build: `npm run build` passed.
- Android debug APK: `gradle :app:assembleDebug --no-daemon` passed after removing the new Kotlin warning.
- Git checkpoint: `9fb32ed` (`checkpoint: add OPPO health demo loop`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package backend/Web validation: backend full tests passed, Web typecheck passed, Web build passed.
- Git checkpoint: `64dc256` (`checkpoint: add experiment evidence package`) created and pushed to `origin/codex/competition-hardening`.
- Health detail validation: backend full tests passed after adding version/auth/features/healthProvider diagnostics.
- Git checkpoint: `c27a34f` (`checkpoint: expand health diagnostics`) created and pushed to `origin/codex/competition-hardening`.
- Dispatch health-scoring validation: backend full tests passed, 27 tests OK.
- Git checkpoint: `6b531af` (`checkpoint: use health signals in dispatch`) created and pushed to `origin/codex/competition-hardening`.
- Local smoke check: temporary backend on `127.0.0.1:18080` with temp DB opened dashboard, initialized demo scenario, confirmed evidence-package UI, AED sites, health summaries, `healthSignals` dispatch field, and ZIP package contents. Smoke service stopped and temp DB removed.
- Evidence integrity targeted tests: `.\.venv\Scripts\python.exe -m unittest tests.test_server.ServerTestCase.test_health_detail_reports_storage_and_frontend_state tests.test_server.ServerTestCase.test_health_detail_reports_demo_readiness_after_bootstrap tests.test_server.ServerTestCase.test_demo_bootstrap_aed_dispatch_and_export tests.test_server.ServerTestCase.test_historical_export_uses_target_incident_roles -v` passed, 4 tests OK.
- Backend full tests after evidence integrity: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 29 tests OK.
- Android auto-join validation: `gradle :app:assembleDebug --no-daemon` passed.
- Web demo guidance validation: `npm run typecheck` passed; `npm run build` passed.
- Browser smoke: temporary backend on `127.0.0.1:18082` opened dashboard and `/mobile-demo`; confirmed dashboard flow labels, evidence-package entry, runbook labels, and 4 iframe panels. Temporary service stopped.
- Mobile SOS confirmation validation: `npm run typecheck` passed; `npm run build` passed; browser smoke on `127.0.0.1:18083/mobile?demo=patient` confirmed first click only shows confirmation while backend remains `CREATED`/`MONITORING`. Temporary service stopped.
- Input validation targeted tests: `.\.venv\Scripts\python.exe -m unittest tests.test_server.ServerTestCase.test_input_validation_rejects_invalid_location_health_and_aed_status tests.test_server.ServerTestCase.test_demo_bootstrap_aed_dispatch_and_export tests.test_server.ServerTestCase.test_client_location_and_aed_site_can_be_updated -v` passed, 3 tests OK.
- Backend full tests after input validation: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 30 tests OK.
- Health presentation validation: Web `npm run typecheck` passed, Web `npm run build` passed, Android `gradle :app:assembleDebug --no-daemon` passed.
- Evidence manifest targeted validation: `.\.venv\Scripts\python.exe -m unittest tests.test_server.ServerTestCase.test_demo_bootstrap_aed_dispatch_and_export -v` passed.
- Current full backend validation: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 30 tests OK.
- Current Web validation: `npm run typecheck` passed; `npm run build` passed.
- Current Android validation: `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `69d7cc8` (`checkpoint: polish evidence and mobile demo`) created locally.
- Git checkpoint: `f11f607` (`checkpoint: update long task handoff`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `6342bb7` (`checkpoint: record pushed state`) created and pushed to `origin/codex/competition-hardening`.
- Android AED target validation: `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `5cc9534` (`checkpoint: show android AED target`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `b2c0370` (`checkpoint: record AED target push`) created and pushed to `origin/codex/competition-hardening`.
- Mobile Web next-step validation: `npm run typecheck` passed; `npm run build` passed.
- Git checkpoint: `5a18fc5` (`checkpoint: guide mobile CPR next steps`) created and pushed to `origin/codex/competition-hardening`.

## Blockers Summary

- Real OPPO Health approval, legal/application submission, secrets, and compatible device validation remain user-only blockers.
- Implemented mock/fallback closed loop instead of unattended real SDK submission or secret handling.

## Next Unblocked Action

Continue from remote checkpoint `5a18fc5` to the next unblocked polish or validation pass while leaving local DB/output/OPPO doc copy uncommitted.

## Resume Instructions

Read `docs/LONG_TASK_STATE.md`, `docs/LONG_TASK_BLOCKERS.md`, `docs/PRODUCT_OPTIMIZATION_PLAN.md`, and run `git status --short --branch`; then continue the current milestone without relying on chat memory.
