# Long Task State

## Current Session - 2026-05-26 Medical Innovation National Web Delivery

- Status: done
- Task: Build the Web command center + `/mobile` four-terminal flow + evidence/material chain into a national-round medical innovation competition deliverable.
- Branch: codex/competition-hardening
- HEAD at start: b8e8c6d
- Workspace: D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧
- User instruction: start the long task; sub-agents are allowed; acceptance is the detailed national-round Web delivery standard below.

### Active Work Plan

1. Establish this session's plan, blocker queue, Git baseline, and sub-agent ledger. (done)
2. Audit Web command center, `/mobile` four-terminal flow, and evidence/material chain. (done)
3. Implement P0 national-round betanstration and evidence-chain improvements. (done)
4. Validate locally with build/tests/browser checks appropriate to changed areas. (done)
5. Deploy through Git/SSH/deploy workflow and verify public readiness. (done)
6. Record final handoff, validation evidence, blockers, and resume instructions. (done)

### Sub-Agent Ledger For This Session

- 019e6045-2e4a-7261-b763-02de2d8edc52 / Bacon: Web command-center read-only audit.
  Permission: read-only
  Owned scope: `server(web)/web/src/app/**`, shared API/types as needed
  Expected output: P0/P1/P2 findings, suggested files, validation ideas
  Status: closed
  Result: P0 findings: command center needs a 5-minute defense path; `/mobile-beta` needs dynamic incident/role/AED/evidence status. P1 findings: score evidence matrix, AED point edit/import, clearer dispatch explanation, friendlier errors, evidence-package boundary prompt.
- 019e6045-6300-75d3-9d36-cc4b891a5b90 / Cicero: `/mobile` four-terminal read-only audit.
  Permission: read-only
  Owned scope: `server(web)/web/src/mobile/**`, shared API/types as needed
  Expected output: P0/P1/P2 findings, suggested files, validation ideas
  Status: closed
  Result: P0 finding: GUIDE can advance to ambulance handover before CPR/AED flow is ready; fix backend and mobile action guard. P1 findings: old-incident auto-join uses current incident, manual role override can break persona roles, guide stage needs dynamic status, projection readability risks.
- 019e6045-9a01-7583-b0e7-8f7ea36bdcf2 / Kierkegaard: evidence package and competition-material read-only audit.
  Permission: read-only
  Owned scope: `server(web)/app/services/incidents.py`, `scripts/*evidence*`, `competition_materials/medical_innovation_competition/**`
  Expected output: P0/P1/P2 findings, suggested files, validation ideas
  Status: closed
  Result: P0 findings: formal multi-round evidence data is missing; T2 first-responder response is not in automatic metrics/summary; official abstract/PPT/experiment/expert materials remain mostly templates. P1 findings: route metrics can be misleading if coordinates are mismatched; add blind-review checklist and AI evidence page support.
- 019e604b-3d0c-7251-b670-e2c3a7a1ab37 / Popper: `/mobile-beta` dynamic stage implementation.
  Permission: write
  Owned scope: `server(web)/web/src/mobile/MobilebetaStage.tsx`, `server(web)/web/src/mobile/mobile-beta-stage.css`
  Expected output: Dynamic incident/role/AED/evidence stage status and projection-friendly runbook.
  Status: closed
  Result: Implemented a polling incident dashboard, dynamic runbook status, role/AED/evidence summaries, recent logs, and projection-friendly stage CSS; parent refined status mappings and validated with Web typecheck/build.
- 019e604b-7756-76a2-80ca-d41be453998f / Dirac: national beta runbook and blind-review/evidence checklist.
  Permission: write
  Owned scope: `competition_materials/medical_innovation_competition/NATIONAL_beta_RUNBOOK.md`, `competition_materials/medical_innovation_competition/BLIND_REVIEW_AND_EVIDENCE_CHECKLIST.md`
  Expected output: Chinese competition-facing runbook/checklist, no fabricated results.
  Status: closed
  Result: Added a 5-minute Web beta runbook and blind-review/evidence checklist; content preserves simulation-only and no-clinical-efficacy boundaries.
- 019e6069-af47-7112-ba38-feb900f52405 / Galileo: public deployment read-only verification.
  Permission: read-only
  Owned scope: `https://lifereflex.mddcommunity.top/`, `/mobile-beta`, `/api/health/detail`, deployed JS bundles
  Expected output: Public smoke conclusion and risk notes only; no file edits or service changes.
  Status: closed
  Result: Verified public HTML, `/mobile-beta`, and `/api/health/detail` are reachable; noted readiness is named `betaReadiness`; parent confirmed `App-CqevobQC.js` contains the national 5-minute copy.

### Current Safety Notes

- Current scope is Web national-round delivery. OPPO SDK and Android APK are not current blockers.
- Preserve unrelated dirty files and runtime DBs. Do not revert user work.
- Real AED points, expert signatures, and final PPT decisions remain external/team tasks.
- Do not commit secrets, `.env`, tokens, keystores, DB runtime artifacts, screenshots, or bulky generated output.

### Current Progress

- Created `competition_materials/medical_innovation_competition/NATIONAL_WEB_DELIVERY_TASK_PLAN.md`.
- Updated `docs/LONG_TASK_BLOCKERS.md` so this round's active blockers are real AED data, expert feedback/signature, and final PPT/team decisions.
- Spawned three read-only audit agents for command center, `/mobile`, and evidence/material chain.
- Integrated and closed three read-only audit agents. First implementation priorities: fix GUIDE premature handover, add T2 response metric, make `/mobile-beta` dynamic, and add command-center competition evidence path.
- Implemented backend handover guard: GUIDE cannot report ambulance arrival until CPR has started and AED has been delivered. Added regression coverage.
- Added `firstResponderResponseSeconds` as T2 to metrics, evidence package CSVs, quality coverage, analysis chart output, and competition-facing evidence text.
- Merged `/mobile-beta` dynamic stage and created national beta runbook / blind-review checklist through closed sub-agents.
- Validation so far: Web `npm run typecheck` passed; Web `npm run build` passed; backend `.venv` unittest discovery passed, 57 tests OK; evidence scripts `py_compile` passed.
- Git checkpoint created and pushed: `5786280 checkpoint: harden national web delivery` on `codex/competition-hardening`.
- Server deploy completed through `deploy@104.248.151.6` at `/opt/lifereflex/medical_innovation_competition`, HEAD `5786280`.
- Server-side source was fast-forwarded from `b8e8c6d` to `5786280`; existing remote dirty `server(web)/web/package-lock.json` was preserved.
- Server Node is `v18.19.1`, while current Vite requires Node `20.19+` or `22.12+`; local Node `v24.15.0` was used to build Web `dist`, then the build artifact was uploaded. Do not treat this as a user blocker; future server builds should either use a project-local Node 20/22 or continue artifact upload.
- Server Web `dist` backup preserved at `/opt/lifereflex/medical_innovation_competition/server(web)/web/dist.backup.20260525183120`.
- Uvicorn on port `8029` was restarted; active process after restart: `/opt/lifereflex/medical_innovation_competition/server(web)/venv/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8029`.
- Public health verified: `https://lifereflex.mddcommunity.top/api/health` returned `{"ok":true}`; `/api/health/detail` returned `frontend.ok=true`, `version=competition-hardening`, `mapProvider.mode=amap`, `betaReadiness.ready=true`, `healthProvider.mode=mock`, `betaAdminAuthEnabled=true`.
- Public bundle verified: `/` references `assets/index-Du7C57ZQ.js`; lazy chunks include `App-CqevobQC.js`, `MobileApp-BFiYGBIX.js`, and `MobilebetaStage-CWuZ-INL.js`; deployed `App-CqevobQC.js` contains national 5-minute beta copy.
- Public beta flow verified with token `LCY`: `/api/beta/bootstrap` -> `/api/incidents/current/designate_patient` -> role joins -> premature GUIDE handover returns `409 Handover requires CPR started and AED delivered` -> CPR/AED pickup/AED delivery/AED analysis/shock/handover/archive all completed.
- Public export metrics verified on archived incident `af2e1835-fe85-4a96-83ad-c62cb14e1fea`: `dispatchSeconds=1`, `firstResponderResponseSeconds=2`, `cprStartSeconds=5`, `aedPickupSeconds=6`, `aedDeliverySeconds=6`, `ambulanceArriveSeconds=8`, `roleAssignmentCompleteness=1.0`.
- Public evidence ZIP verified: `/api/experiments/current/package` returned `application/zip`, ZIP magic `PK`, 32982 bytes, and SHA-256 header `bdd610c63f11eebb6872fc5f0144c6b80a12376007350ae02a21dd226cca5390`.
- Public screenshots generated under `output/browser-check/`: `public-dashboard-after-deploy.png`, `public-mobile-beta-after-deploy.png`, and `public-mobile-prime-after-deploy.png`. These are validation artifacts and should remain untracked.
- Remote residual state after deploy: `server(web)/web/package-lock.json` remains dirty on server from a pre-existing npm optional `libc` diff; `server(web)/web/dist.backup.20260525183120/` is an intentional remote rollback backup. Do not commit either without a separate decision.
- Local residual dirty state after deploy remains unrelated/user or runtime work: Android app files, `server(web)/data/lifereflexarc.db`, `OPPO健康SDK文档.md`, and `output/`.

### Final Handoff - 2026-05-26 Public National Web Milestone

- Public command center: `https://lifereflex.mddcommunity.top/` is deployed and loading the current national-round bundle.
- Public four-terminal stage: `https://lifereflex.mddcommunity.top/mobile-beta?incidentId=af2e1835-fe85-4a96-83ad-c62cb14e1fea` is reachable and shows the archived four-terminal betanstration stage.
- Public mobile terminal example: `https://lifereflex.mddcommunity.top/mobile?beta=prime&slot=prime&incidentId=af2e1835-fe85-4a96-83ad-c62cb14e1fea` is reachable and shows the app-like mobile Web terminal.
- beta admin token remains `LCY`.
- Current Git branch is `codex/competition-hardening`; latest committed/pushed task checkpoint is `5786280`.
- Remaining true blockers are only the team/external items in `docs/LONG_TASK_BLOCKERS.md`: real AED location confirmation, expert feedback/signature, and final PPT/team wording decisions.

## Current Session Acceptance Standard - Medical Innovation National Web Delivery

The current long task is ready to start once the user confirms. Its acceptance standard is:

Build "生命反射弧" into a competition-ready Web product for the 12th National Undergraduate Medical Innovation Competition national round. The declared direction is undergraduate group, experimental design type, interdisciplinary track, subgroup 4 "AI Innovation Design". The product must be publicly accessible, support desktop-based four-terminal simulation, complete a simulated emergency collaboration flow, export evidence materials, and support the national-round defense narrative.

Competition-specific framing:

- Official deliverables include abstract, PPT, and experiment records.
- Experimental-design abstracts should cover: rationale, design idea, experiment content, materials, preliminary experiment result, feasibility, and innovation.
- The track requires a clear medical application scenario, a medical real-world problem, medical-related validation data or clinical/expert feedback, and AI integration into the research process. Avoid presenting the work as a pure software/AI technical project.
- The current safe claim is "low-cost simulation pre-experiment + expert feedback", not clinical efficacy or real patient validation.
- Blind-review materials and experiment records must avoid school names, student names, advisor names, photos, logos, and other identifying information.
- Defense PPT should support a 5-minute Chinese presentation, match submitted abstract/PPT content, use 16:9 layout, and avoid school/team-identifying content except the allowed team number/title format.

Scoring-aligned acceptance goals:

- Feasibility 15 points: show medical rationale, technical route, preliminary simulation result, and low-cost budget.
- Innovation 20 points: make the AI innovation explicit, original, and critical; AI should be role dispatch/explanation/fallback integration, not only generic chat or a UI label.
- Application 10 points: show value for campus, community, public venue, training, drills, and reviewable emergency coordination.
- Experiment record 5 points: produce traceable system/experiment records and post-competition-progress style materials.
- Defense 30 points: support clear PPT logic, attractive screenshots, accurate Q&A, and basic medical/AI reasoning.
- Teamwork 20 points: make system, PPT, pre-experiment, expert feedback, compliance, and data-analysis contributions easy to map to team roles.

Detailed acceptance criteria:

1. Public Web entry is usable for presentation:
   - `https://lifereflex.mddcommunity.top/` loads as the command-center entry.
   - The command center can initialize or reset a beta scenario with the beta admin token `LCY`.
   - The command center clearly shows scenario status, terminal readiness, role dispatch, AED sites, event logs, evidence/export actions, and beta links.
   - The page is suitable for projection: no cramped first screen, no unexplained technical noise, no status flicker that distracts judges.
   - The visible copy should support a Chinese 5-minute defense: concise, judge-facing, and aligned with "AI-assisted emergency coordination" rather than developer/debug wording.

2. Desktop four-terminal beta works without real phones:
   - One computer can open four `/mobile` terminals for patient, prime responder, AED runner, and guide/clearance roles.
   - Each terminal can bind to the same incident while keeping its own session identity through `slot` or equivalent isolation.
   - The four terminals do not cross-login, overwrite each other's state, or trigger the wrong role action.
   - The command center provides a practical way to open or share the four terminal links.
   - The four-terminal route should support screenshots or video capture for PPT page 6 "system implementation display".

3. Simulated emergency collaboration flow is complete:
   - The beta can represent patient alert, dispatch, role acceptance, CPR start, AED pickup, AED delivery, AED analysis, shock/handover, and archive/completion.
   - AI dispatch may use cloud reasoning when available, but the beta must have a fast deterministic/static fallback so presentation does not depend on a third-party model.
   - Actions should be idempotent or guarded against duplicate clicks where practical.
   - Errors must be understandable to presenters instead of producing blank screens or unexplained failures.
   - The flow should expose enough timestamps or state transitions to support T1-T6 style pre-experiment metrics.

4. Evidence materials are exportable and competition-safe:
   - The system can export a ZIP evidence package for a completed or current incident.
   - The evidence package should include structured event data, timeline/logs, participant/role summary, AED/site information, experiment-ready records, and review-friendly materials.
   - Exported public/review-facing materials should avoid leaking secrets, raw tokens, API keys, private certificates, or unnecessary personal data.
   - SHA-256 or manifest verification should remain available where implemented.
   - Evidence should support official experiment-record requirements: experiment date, content, materials/methods, results with tables/figures, discussion/analysis, project name, and design idea.
   - Materials should support blind-review safety by excluding school/student/advisor identifiers from public/review-facing files.

5. Low-cost desktop simulation experiment is supported:
   - The workflow should support running multiple simulated rounds from one computer.
   - Materials under `competition_materials/medical_innovation_competition` should explain how to run the simulation, record observations, summarize rounds, and prepare PPT-safe data.
   - The system should not require real OPPO SDK, Android APK, SMS, push notification, or real multi-device hardware for this phase.
   - At minimum, the workflow should make 2-3 simulation rounds feasible; the ideal plan still supports 3-5 rounds if the team has time.
   - The output should support T1-T6 time indicators, participant subjective scores, observer notes, and a cautious preliminary-result paragraph.

6. National-round defense narrative is supported:
   - The Web product and materials should make the AI innovation design value visible: role dispatch logic, location/AED consideration, health-summary concept, collaboration timeline, evidence loop, and fallback safety.
   - The deliverable should help presenters explain "what problem it solves", "how AI participates", "how a low-cost experiment can verify the workflow", and "what remains as future clinical/field validation".
   - Avoid claiming clinical efficacy from simulated data. Keep language framed as workflow simulation, training, coordination, and pre-experiment evidence.
   - The narrative must answer why the work belongs to "AI Innovation Design": clear medical scenario, real emergency coordination problem, AI/algorithm contribution, medical-related validation or expert feedback, and AI integrated into the research workflow.
   - The narrative should explicitly distinguish the product from 120 calling, AED maps, chatbots, and generic notification groups.
   - Materials should include or support Q&A for likely questions: AI failure fallback, AED/location accuracy, safety boundary, privacy, small sample size, and future real-world validation.

7. Abstract, PPT, and official-material compatibility:
   - Abstract content should map to experimental-design fields: rationale, design idea, experiment content, materials, preliminary result, feasibility, and innovation.
   - PPT mainline should fit a 5-minute Chinese defense and roughly follow: medical problem -> AI design -> system implementation -> pre-experiment -> innovation/application/safety.
   - PPT/screenshots should avoid school names, logos, student/advisor names, student photos, chat notifications, and other blind-review risks.
   - Suggested PPT evidence should include: system architecture, AI dispatch logic, command center, four `/mobile` terminals, dispatch explanation, evidence package export, pre-experiment charts, and safety/future-work slide.

8. Engineering and deployment readiness:
   - Local code should build/typecheck/test according to the risk of changed areas during the long task.
   - Public deployment should be updated through the Git/SSH/deploy workflow when changes are ready.
   - Server-side changes should preserve the `deploy` user workflow, `/opt` project layout, SSH Git remote, and existing 1Panel/OpenResty setup.
   - Dirty or unrelated files must not be reverted or accidentally committed.
   - beta should have network/presentation fallback options: static/fast dispatch fallback, understandable degraded-state messages, and enough screenshot/video/evidence backup for defense if live network is unstable.

9. Teamwork and contribution evidence:
   - The final materials should make it easy for the team to claim real contributions: system development, AI dispatch design, pre-experiment organization, data analysis, PPT narrative, expert feedback, and compliance/anonymous-material checking.
   - Do not invent team contributions, signatures, expert opinions, or real-world experiment results. Provide templates and reminders where external work is required.

10. Final handoff must be concrete:
   - Report changed files, deployed URL/status, validation commands and results, screenshots or exported evidence when useful, remaining agent-owned tasks, and true user/external blockers.
   - Update `docs/LONG_TASK_STATE.md` and `docs/LONG_TASK_BLOCKERS.md` or the competition-material equivalents so a future resumed thread can continue without relying on chat memory.

## Standing Rule - Pre-Long-Task Test Scope

- Before a long task starts, only validate resource, permission, environment, and tooling availability.
- Website business-flow tests, UI tests, and feature acceptance tests belong inside the long-task development/validation phase.
- Do not expand preflight into a full product smoke test unless the user explicitly asks for that specific test.

## Current Session Override - 2026-05-24 National Final `/mobile` Redesign

- Status: done
- Task: Complete the Web `/mobile` national-final UI redesign.
- Branch: codex/competition-hardening
- HEAD at start: 14d74f7
- Workspace: D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧
- User instruction: treat as a long task; sub-agents are allowed; acceptance is completing the Web `/mobile` experience.

### Acceptance Criteria

- `/mobile` is redesigned as a focused emergency collaboration terminal rather than a compressed dashboard.
- Patient, responder, scene/AED, logs, and profile/health states have clear hierarchy and large touch-friendly controls.
- The visual language is closer to the Android app while avoiding its current heavy/ugly parts.
- Web `typecheck` and `build` pass.
- Browser verification covers common mobile width and confirms no horizontal overflow.

### Active Work Plan

1. Establish plan/state/git baseline. (done)
2. Run parallel read-only audits for current `/mobile` and Android app visual tokens. (done)
3. Refactor `/mobile` TypeScript structure and CSS. (done)
4. Validate with Web build/typecheck and browser layout checks. (done)
5. Record final state, blockers, and handoff. (done)

### Sub-Agent Ledger For This Session

- Leibniz: read-only `/mobile` structure/UI audit. Status: completed.
- Helmholtz: read-only Android visual-token extraction. Status: completed.

### Safety Notes

- Preserve existing dirty/user files: `server(web)/data/lifereflexarc.db`, `OPPO健康SDK文档.md`, and `output/`.
- Do not commit secrets, local properties, APK/AAB artifacts, keystores, runtime DBs, or generated screenshots.
- Do not deploy to production unless the user explicitly asks for this session.
- Keep edits scoped to `/mobile`, directly shared mobile styles, task docs/state, and validation artifacts that are intentionally untracked.

### Progress Update

- Created `docs/MOBILE_WEB_UI_REDESIGN_PLAN.md` as the local source of truth for this UI task.
- Checked git baseline: branch `codex/competition-hardening`, start HEAD `14d74f7`, existing dirty runtime/user files recorded above.
- Sub-agent audits completed:
  - `/mobile` audit recommended a stronger cross-tab emergency header, lower first-screen cognitive load, clearer offline/reconnecting status, weaker beta-only controls, and fixing `.mobile-manual-toggle` layout.
  - Android visual-token audit recommended keeping the calm dark command-terminal base, role colors, large primary buttons, status chips, and metric cards while avoiding heavy red-black gradients, fake phone chrome, emoji-like cues, and overlarge numbers.
- First implementation slice completed in `server(web)/web/src/mobile/MobileApp.tsx` and `server(web)/web/src/mobile/mobile.css`: added a command header, clearer sync/phase labels, event/AED/online facts, terminal identity card, compact health metrics, role-tinted action panels, and larger touch controls.
- Validation so far: Web `npm run typecheck` passed after the first JSX/CSS slice.
- Final implementation slice completed:
  - patient beta terminals are treated as patient terminals even when connected to an already-dispatched event;
  - long-running beta incident durations are formatted as days/hours instead of huge minute counts;
  - responder home state directly shows the assigned role action;
  - manual-role fallback toggle now has explicit flex layout.
- Final validation:
  - `npm run typecheck` passed.
  - `npm run build` passed with mobile bundle `MobileApp-C5X2RwQM.js` and CSS `MobileApp-AjNmK5FG.css`.
  - Local Vite on `127.0.0.1:5174` plus local FastAPI on `127.0.0.1:8080` were used for DOM checks, then stopped.
  - Browser DOM checks at 390 x 844 confirmed no horizontal overflow for patient and runner beta flows.
- Git status at finish still includes expected runtime/user files outside commit scope: `server(web)/data/lifereflexarc.db`, `OPPO健康SDK文档.md`, and `output/`.

## Current Session Override - 2026-05-23 National Final UI/App Polish

- Status: done
- Task: Polish public `/mobile-beta` and Android app completeness for national final preparation
- Branch: codex/competition-hardening
- HEAD at start: 8499857
- Workspace: D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧
- User instruction: continue unattended, use sub-agents/parallel agents if useful, improve `/mobile-beta` visible UI and Android app functionality; deploy/verify where feasible.

### Acceptance Criteria

- `/mobile-beta` is visually cleaner, lower load, closer to Android app style, and browser-verified at desktop and narrower widths.
- Android app gains practical complete-app affordances around login/home/settings/user/profile/status without touching secrets or real OPPO SDK approval paths.
- Relevant validation commands pass or blockers are recorded.
- Public deployment is updated if the Web build is stable.

### Active Work Plan

1. Inspect current `/mobile-beta`, Android app structure, git state, and long-task blockers. (done)
2. Improve `/mobile-beta` layout, hierarchy, labels, responsive behavior, and iframe presentation. (done, validating)
3. Improve Android app completeness with low-risk settings/profile/status surfaces. (done, validating)
4. Validate Web typecheck/build, Android debug build, and targeted backend tests if touched. (done with one Android unit-test environment note)
5. Deploy to public server using the existing Git/PM2 flow after successful Web build. (next)
6. Capture screenshots and update this state file with validation/deployment results. (done)

### Sub-Agent Ledger For This Session

- `/mobile-beta` explorer: started read-only to identify low-risk UI polish opportunities.
- Android completeness explorer: started read-only to identify missing app functions and safe implementation paths.

### Safety Notes

- Preserve existing dirty files: `server(web)/data/lifereflexarc.db`, `OPPO健康SDK文档.md`, and `output/`.
- Do not commit secrets, local properties, APK/AAB artifacts, keystores, runtime DBs, or generated screenshots.
- Do not attempt real OPPO Health approval, secret copying, legal acceptance, or account actions unattended.
- Keep edits scoped to Web `/mobile-beta`, Android UI/functionality, docs/state, and directly required supporting code.

### Progress Update

- `/mobile-beta` redesigned as a lighter app-style four-device stage: shallow background, compact app bar, status strip, six-step guide, and phone-like panels.
- Browser screenshot validation with Edge succeeded at `1440x900` and `390x844`; screenshots saved under `output/playwright/` and intentionally left untracked.
- Android app now has a `设置` tab with service status, endpoint diagnostics, device capability status, local preferences, beta boundary copy, version/build info, and logout.
- Added local app settings (`语音指引`, `震动提醒`, `演示安全确认`) with SharedPreferences persistence; PRIME voice prompts now respect the voice-guidance setting.
- Android patient SOS now uses authenticated user endpoints `/patient_sos_start` and `/patient_sos_cancel` instead of admin-only SOS endpoints.
- Validation passed: Web `npm run typecheck`; Web `npm run build`; Android `gradle :app:assembleDebug --no-daemon`; backend `python -m unittest discover -s tests -v` with 54 tests OK.
- Validation note: Android `gradle :app:testDebugUnitTest --no-daemon` currently fails on the pre-existing template `ExampleUnitTest` with `ClassNotFoundException`; debug APK build is healthy, and no app logic failure was observed.
- Second app-completeness slice: backend now supports authenticated `PATCH /auth/me`; Android profile page can edit display name, organization, health condition, profession identity, and bio, then persists the refreshed session locally.
- Profile update validation passed: targeted backend profile tests; full backend unittest discovery with 55 tests OK; Android `gradle :app:assembleDebug --no-daemon`; Web `npm run typecheck`; Web `npm run build`.
- Git checkpoints pushed: `1d8d541` (`Polish mobile beta stage and Android settings`) and `0f6a5fd` (`Add editable Android profile flow`).
- Public deployment completed on `https://lifereflex.mddcommunity.top/`; server HEAD is `0f6a5fd`, PM2 process `mspc-backend` restarted and online.
- Public API smoke passed: `PATCH /api/auth/me` updated a test account profile; `/api/health/detail` reports `ok: true` and frontend assets ready.
- Remaining untracked/dirty items intentionally excluded: local runtime DB, OPPO SDK document, `output/` screenshots/artifacts, and server-side unrelated `server(web)/web/package-lock.json`.

## Current Status

- Status: running
- Task: OPPO Health data enhancement phase 1
- Branch: codex/competition-hardening
- HEAD: 7ea7537
- Last update: 2026-05-22 17:14:26 +08:00
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
10. Strengthen pre-experiment evidence integrity: anonymized package, manifest hashes, structured timeline, richer metrics, historical export correctness, and beta readiness. (done, validating)
11. Wire Android app auto-join entry into the current AppRoot flow. (done, checkpointing)
12. Add Web command-center flow stepper and 4-terminal beta-stage runbook. (done, checkpointing)
13. Add mobile Web SOS two-step confirmation to reduce accidental emergency triggering. (done, checkpointing)
14. Add input boundary validation for location, health summaries, and AED status. (done, validating)
15. Update morning handoff with OPPO phase 1, evidence package, beta guidance, validation, and latest checkpoints. (done, checkpointing)
16. Localize health-risk tags and remove mock/fallback wording from user-facing health cards. (done, checkpointing)
17. Align pre-experiment, deployment, expert feedback, product plan, and whitepaper docs to the ZIP evidence package. (done, validating)
18. Add manifest privacy guidance and verification metadata for evidence packages. (done, validating)
19. Fold mobile Web manual role takeover under a beta backup control. (done, validating)
20. Add recent on-site timeline cards to Android task and incident screens. (done, validating)
21. Commit evidence/mobile/Android polish checkpoint. (done)
22. Push current checkpoints to GitHub. (done)
23. Add Android Runner full-screen AED target card. (done, validating)
24. Push Android AED target checkpoint. (done)
25. Add mobile Web PRIME next-step CPR/AED guidance card. (done, validating)
26. Push mobile Web PRIME next-step checkpoint. (done)
27. Add Android profile beta-location selector. (done, validating)
28. Push Android beta-location checkpoint. (done)
29. Run post-beta-polish validation sweep. (done)
30. Add expert-review screenshot checklist and 3-5 minute beta script. (done, validating)
31. Push expert-material checklist checkpoint. (done)
32. Expand `/api/health/detail` frontend build diagnostics. (done, validating)
33. Push frontend health diagnostics checkpoint. (done)
34. Add Web/mobile medical disclaimer and data-use boundary copy. (done, validating)
35. Push Web/mobile safety-boundary checkpoint. (done)
36. Add Android local archive participant-perspective task summary. (done, validating)
37. Push Android archive-summary checkpoint. (done)
38. Complete deployment backup/rollback/1Panel/OpenResty runbook details. (done, validating)
39. Push deployment runbook hardening checkpoint. (done)
40. Reorder Android home event actions to prioritize current event and auto-join. (done, validating)
41. Push Android current-event CTA checkpoint. (done)
42. Run final P0/P1 validation sweep. (done)
43. Document third-party provider contract and mark AI/SMS fallback readiness. (done, validating)
44. Push provider fallback documentation checkpoint. (done)
45. Add backend audit log, rate limits, and Web audit panel. (done, validating)
46. Migrate Android token/session storage to encrypted preferences with legacy migration. (done, validating)
47. Increase Android Gradle heap for reliable APK builds after security dependency. (done, validating)
48. Update docs and create security-hardening checkpoint. (done)
49. Push security-hardening checkpoint to GitHub. (done)
50. Record pushed security checkpoint in handoff/state. (done)
51. Add backend map/spatial provider abstraction with AMap WebService fallback. (done, pushed)
52. Add Android native location provider with system-location and beta fallback. (done, pushed)
53. Add backend notification provider with WebSocket fallback. (done, pushed)
54. Add backend formal admin account minimal RBAC. (done, pushed)
55. Align frontend admin user type. (done, pushed)
56. Fix mobile patient SOS delayed auto-dispatch and wire Web command center admin login. (done, pushed)
57. Localize visible Web command-center and `/mobile-beta` beta labels. (done, pushed)
58. Run final post-polish validation sweep. (done, pushed)
59. Run Android debug APK validation sweep. (done, pushed)
60. Reduce Web command-center first-screen technical overload and preserve mobile incident deep links. (done, pushed)
61. Simplify mobile scene/cooperation page technical details. (done, pushed)
62. Surface beta readiness checklist in Web command center. (done, pushed)
63. Add expert review checklist and observer record form into ZIP evidence package. (done, pushed)
64. Remove visible PRIME/RUNNER/GUIDE auxiliary labels from mobile beta entry and 4-terminal stage captions. (done, pushed)
65. Add mobile Web archived-flow evidence package download entry. (done, pushed)
66. Localize remaining Android emergency-screen role-code wording. (done, pushed)
67. Localize Android CPR metronome visible English labels. (done, pushed)
68. Run post-label/evidence-package validation sweep. (done, pushed)
69. Align whitepaper/pre-experiment/handoff wording with latest evidence package and Chinese role labels. (done, pushed)
70. Add pre-experiment round-summary CSV into ZIP evidence package. (done, pushed)
71. Refresh README with current beta entries, validation commands, evidence package, admin auth, and provider fallback. (done, pushed)
72. Record README checkpoint and resume state after context handoff. (done, pushed)
73. Add participant consent/safety brief and questionnaire into ZIP evidence package. (done, pushed)
74. Add baseline-vs-system comparison CSV template into ZIP evidence package. (done, pushed)
75. Add pre-experiment analysis guide into ZIP evidence package. (done, pushed)
76. Add event-specific expert feedback and signature form into ZIP evidence package. (done, pushed)
77. Add Web command-center beta entrance share links. (done, pushed)
78. Add facilitator run sheet into ZIP evidence package. (done, pushed)
79. Add reliable Web command-center opener for four mobile terminal tabs. (done, pushed)
80. Polish Android PRIME navigation visible language and placeholder distance. (done, pushed)
81. Add ZIP evidence-package review index for expert/judge review. (done, pushed)
82. Improve mobile Web archived-flow evidence package permission UX. (done, pushed)
83. Run latest backend/Web/Android validation sweep and record handoff. (done, pushed)
84. Polish Android visible location floor/source and AED status labels. (done, pushed)
85. Harden archive/evidence summary copy and remove visible fake metrics. (done, pushed)
86. Polish mobile visible beta/evidence/health copy. (done, pushed)
87. Add mobile archived-flow next actions. (done, pushed)
88. Polish Web phone-preview inert actions and Android visible task wording. (done, pushed)
89. Normalize dispatch-source labels across Web and Android. (done, pushed)
90. Add mobile PWA offline fallback and event context strip. (done, pushed)
91. Add ZIP evidence-package data dictionary and sync public review docs. (done, pushed)
92. Polish visible evidence-package, health-summary, and location wording across Web/mobile/Android. (done, pushed)
93. Soften medical-compliance wording and sample health authorization across Web/mobile/Android. (done, pushed)
94. Anonymize public evidence-package review files and sync docs. (done, pushed)
95. Tighten health-summary sample authorization and backend input boundaries. (done, pushed)
96. Make evidence-package downloads incident-specific and tighten Web AED archive summary. (done, pushed)
97. Surface health authorization status across Web/mobile summaries. (done, pushed)
98. Sync public documentation wording with safer beta/evidence language. (done, pushed)
99. Add Android HeyTap Health readiness display without invoking real SDK authorization. (done, pushed)
100. Run post-health-readiness validation sweep. (done, checkpointing)
101. Add Android friendly error mapping for HTTP/network/WebSocket failures. (done, pushed)
102. Add debug-only Android cleartext network support for LAN/local backend testing. (done, pushed)
103. Strengthen mobile PWA shell/resource caching and update activation. (done, pushed)
104. Polish Android visible safety/archive wording for presentation readiness. (done, pushed)
105. Add Android release APK readiness and optional signing configuration. (done, pushed)
106. Refresh morning handoff with latest checkpoints, APK artifacts, PWA, and release readiness. (done, checkpointing)
107. Sync overnight plan, product plan, and technical whitepaper with Android release readiness, PWA cache resilience, and latest validation facts. (done, checkpointing)
108. Add Web command-center preflight Markdown report for beta readiness, provider fallback, terminal/AED state, and safe handoff notes. (done, checkpointing)
109. Add independent evidence-package verification script for manifest SHA-256, file-list, ZIP path safety, and privacy-boundary checks. (done, pushed)
110. Refresh morning handoff with Web preflight report, evidence-package verifier, and latest 38-test backend validation. (done, pushed)
111. Add expert feedback summary and remediation-loop CSV into the evidence package. (done, pushed)
112. Sync long-task state, handoff, and competition docs with the expert-feedback remediation loop. (done, pushed)
113. Add multi-round evidence-package summary CLI for pre-experiment ZIP aggregation. (done, pushed)
114. Add PPT-safe Markdown analysis report generator for round-summary CSV. (done, pushed)
115. Sync expert feedback template, whitepaper, and product plan with evidence analysis toolchain and 40-test validation. (done, pushed)
116. Correct analysis-report percentage scaling for role assignment completeness. (done, pushed)
117. Add one-command pre-experiment report builder for CSV plus Markdown generation. (done, pushed)
118. Sync product plan, whitepaper, and expert template with the one-command evidence-analysis flow. (done, pushed)
119. Add one-command analysis guidance inside exported evidence-package materials. (done, pushed)
120. Add PPT/Excel chart-data CSV output for multi-round pre-experiment analysis. (done, pushed)
121. Refresh morning handoff with latest evidence-analysis checkpoints. (done, checkpointing)
122. Add post-beta evidence-processing checklist to the Web preflight Markdown report. (done, pushed)
123. Identify next low-risk competition hardening slice after checkpoint. (done)
124. Polish Web/mobile competition beta visibility: remove hardcoded phone-preview values, anchor mobile CPR timing to event logs, and keep mobile next action visible. (done, pushed)
125. Add evidence-package SHA-256 response header and audit metadata. (done, pushed)
126. Guard Android release builds against local HTTP/WS endpoints. (done, pushed)
127. Strengthen evidence-package verifier with public-file raw participant ID leak detection. (done, pushed)
128. Add ZIP evidence quality report with key-event coverage, warnings, and low-cost pre-experiment readiness level. (done, pushed)
129. Seed Android incident state from REST before waiting for WebSocket updates. (done, pushed)
130. Make Android WebSocket reconnect scheduling single-flight under network flaps. (done, pushed)
131. Add Android emergency action duplicate-submit guard for full-screen flow. (done, pushed)
132. Extend Android pending-action feedback to regular task/incident mission cards. (done, pushed)
133. Add evidence verifier negative tests for tampered hash, unlisted files, privacy overlap, and public raw-ID leaks. (done, pushed)
134. Harden Web and mobile WebSocket reconnect against stale socket close/error callbacks. (done, pushed)
135. Sync public product, deployment, README, and whitepaper docs with latest reliability and validation facts. (done, pushed)
136. Make backend role action endpoints idempotent for repeated completed actions. (done, pushed)
137. Prevent repeated manual join from resetting completed role progress. (done, pushed)
138. Mark already assigned users as JOINED when they auto-join current incident. (done, pushed)
139. Add mobile Web ref-level single-flight guard for emergency actions. (done, pushed)
140. Refresh Android incident state immediately after auto-joining. (done, checkpointing)
141. Merge evidence quality fields into multi-round CSV/report analysis and reviewer docs. (done, checkpointing)
142. Add round-analysis quality review table for rerun/manual-review triage. (done, checkpointing)
143. Sync Web preflight report post-beta evidence steps with quality review table. (done, pushed)
144. Add multi-round review-action CSV for PPT/expert evidence triage. (done, pushed)
145. Prevent non-patient beta mobile terminals from starting patient SOS. (done, pushed)
146. Surface evidence-package SHA-256 after Web/mobile downloads. (done, pushed)
147. Align Web command-center readiness warning count with visible/admin warnings. (done, pushed)
148. Add bound-event status strip to the 4-terminal mobile beta stage. (done, pushed)
149. Add Web command-center copy affordance for evidence-package SHA-256. (done, pushed)

## Sub-Agent Ledger

- Web/mobile explorer (`019e4b97-e5bd-7200-a64b-fb9c42167d8e`): completed read-only; identified `ClientInfo.healthSignals`, Web console, `/mobile`, and export insertion points.
- Android explorer (`019e4b98-1336-70d0-b06d-72d187a79a14`): completed read-only; identified Kotlin provider, register, DTO, and UI insertion points.
- OPPO docs explorer (`019e4b98-45d3-7fb3-96c0-c6831d5d5701`): completed read-only; produced checklist-ready OPPO materials and blockers.
- Web/mobile UI explorer (`019e4bb7-9d4e-7372-9536-5ab5537730b1`): completed read-only; recommended beta stepper, mobile beta script, SOS confirm, task fallback folding, and next-action cards.
- Backend evidence explorer (`019e4bb7-b138-7263-abf1-99c38ba0bfa5`): completed read-only; recommended target-incident export roles, ZIP manifest, richer metrics, structured timeline, beta readiness, and input constraints.
- Android APK explorer (`019e4bb7-c511-78f2-af54-44692d632c16`): completed read-only; recommended wiring auto-join, adding timeline visibility, Chinese health presentation, beta location switching, and AED/CPR status cards.
- P2 location/push explorer (`019e4c10-ef42-7dc1-b9ce-76e6d76fa2fc`): completed read-only; recommended Android native location provider prewiring first, then backend notification provider with WebSocket fallback.
- Admin/RBAC explorer (`019e4c27-d940-7411-bcad-12f6103a3b4d`): completed read-only; confirmed config-based `LRA_ADMIN_PHONES` minimal RBAC is the safest slice and noted frontend `AuthUser.privileges` type drift.
- Web/mobile polish explorer (`019e4c27-ed2f-71e2-b975-4d47eaeac985`): completed read-only; identified a P0 mobile patient SOS delayed auto-dispatch stall, raw English/status labels in the command center, overloaded AI diagnostics, English role labels in `/mobile-beta`, and evidence wording polish.
- Expert feedback evidence explorer (`019e4c90-6c28-7110-bbd1-05db34c07ada`): completed read-only; confirmed `expert_feedback_form.md` belongs in export generation, manifest public-review guidance, package tests, README, deployment runbook, expert template, pre-experiment protocol, product plan, whitepaper, and morning handoff.
- Next-slice explorer (`019e4ca9-a516-7362-8b0f-57a17315eaf3`): completed read-only; recommended Android visible-language polish, mobile Web evidence-package permission UX, and ZIP review index as the next low-risk slices.
- Web/mobile polish explorer (`019e4cfa-e2ad-7552-80b9-ad63f2facc8b`): completed read-only; recommended softening SOS/SCA/auto-call claims, PWA offline read-only state, evidence-package entry consistency, neutral beta-token placeholders, less mobile noise, removing hardcoded beta values, and role-name consistency.
- Android polish explorer (`019e4cfa-f682-7d40-adc5-ce798a58db98`): completed read-only; recommended lower-friction current-event entry, hiding raw device IDs, filtering local archives, using sample health authorization instead of real authorization, stricter AED archive inference, and friendlier error mapping.
- Backend evidence explorer (`019e4cfb-0a63-7343-9401-e225d1189f27`): completed read-only; recommended anonymization checks for public files, manifest/file-list consistency, external hash verification guide, full-field data dictionary, multi-round summary, expert feedback remediation loop, and medical-compliance wording scans.
- Web/mobile next-slice explorer (`019e4d0a-d1d2-7f33-a973-bcebba0be928`): completed read-only; recommended incident-specific evidence downloads, Web archive AED-summary tightening, backend beta-health wording, public-doc wording sync, and optional PWA asset caching.
- Android/OPPO next-slice explorer (`019e4d0a-e5ae-70a0-8aa6-3fc9275cb531`): completed read-only; recommended backend beta health `sample` status, health input enum boundaries, Android HeyTap readiness states, local HTTP clarity, Android error mapping, and Web/mobile health authorization display.
- New sidecar review attempts after resume: requested by user but blocked by current agent thread limit; main thread continued locally with read-only review and scoped documentation updates.
- Resume after interruption: user again authorized sub-agents/parallel agents; main thread will keep ownership of edits and may use read-only/sidecar agents for non-overlapping recommendations if capacity allows.
- Web/mobile UI sidecar (`019e4dba-bb11-7032-ae34-363e6ab4bb99`): completed read-only; recommended event-anchored mobile CPR timing, actionable readiness cues, milestone ribbon, persistent mobile next action, and residual terminal/SOS wording cleanup.
- Backend evidence sidecar (`019e4dba-cf57-79e0-9ad1-a081f9f0f1f0`): completed read-only; recommended package SHA-256 response headers/audit metadata, ZIP-internal evidence quality report, stronger verifier privacy scans, clearer multi-round identifiers, and negative verifier tests.
- Android reliability sidecar (`019e4dba-e576-7461-999a-70bb9904450c`): completed read-only; recommended REST state seeding before WebSocket, terminal registration readiness/retry, emergency CTA debouncing, single-flight WebSocket reconnect, and release endpoint HTTPS/WSS guard.
- Android REST-state sidecar (`019e4ddd-fa5d-7d52-89ca-d5550cb8b20b`): completed read-only after resume; recommended the smallest safe Android reliability patch as seeding repository state from REST `getCurrentIncident`/`getIncident` before waiting for the first WebSocket frame.
- Evidence-quality summary sidecar (`019e4e96-350a-7763-834a-c0a70925f9cd`): completed read-only after resume; recommended adding quality fields to `summarize_evidence_rounds.py`, asserting one-command report-builder propagation, optionally surfacing quality in `analyze_round_summary.py`, and syncing README/deployment/pre-experiment/handoff/reviewer docs.

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
- `docs/ANDROID_RELEASE_READINESS.md`
- `docs/MORNING_HANDOFF.md`
- `README.md`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/AppModels.kt`
- `lifereflex(app)/local.properties.example`
- `lifereflex(app)/app/build.gradle.kts`
- `lifereflex(app)/app/src/debug/AndroidManifest.xml`
- `lifereflex(app)/app/src/debug/res/xml/debug_network_security_config.xml`
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
- `server(web)/web/public/mobile-sw.js`
- `server(web)/web/public/offline.html`
- `server(web)/web/src/main.tsx`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/ErrorMessages.kt`
- `lifereflex(app)/app/src/main/AndroidManifest.xml`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/IncidentModels.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/HealthSignalProvider.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/ApiService.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/data/IncidentRepository.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/viewmodel/IncidentViewModel.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/AppRoot.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/ActiveEmergencyScreen.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/GuideTaskScreen.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/LoginScreen.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/MissionPanels.kt`
- `lifereflex(app)/app/src/main/java/com/example/lifereflexarc/ui/screens/ShellScreens.kt`

## Last Completed Step

- Backend `HealthSignalSummary` model, `/clients/health`, persistence, beta data, and export integration are implemented.
- Web console and `/mobile` show mock/OPPO health summaries; mobile web also syncs a mock health summary after login/beta entry.
- Android app has `HealthSignalProvider`, `MockOppoHealthSignalProvider`, OPPO package visibility, server sync, and Compose health summary cards.
- OPPO checklist doc added.
- Evidence package now includes anonymized JSON/CSV, `expert_summary.md`, structured `timeline.csv`, richer experiment metrics, and `manifest.json` with SHA256 hashes.
- Historical event export now derives participant roles/patient flags from the target incident instead of the current incident.
- `/api/health/detail` now reports `betaReadiness` with readiness warnings, location coverage, health coverage, AED availability, and export readiness.
- Android Home and Incident tabs now expose the existing auto-join flow, passing the logged-in token and routing the user to Tasks after auto-join.
- Web dashboard now shows a five-step competition beta flow: scenario bootstrap, patient SOS, AI dispatch, field response, and handover/export.
- `/mobile-beta` now shows a compact runbook above the four terminal frames so a presenter can follow the correct sequence without separate notes.
- Mobile Web patient SOS now requires a second confirmation click before calling the backend start endpoint.
- Backend schemas now reject invalid latitude/longitude, negative accuracy, out-of-range health values, and unsupported AED status while normalizing valid AED status values.
- `docs/MORNING_HANDOFF.md` is updated with latest checkpoints, validation status, beta script, and evidence-package guidance.
- Web, mobile Web, and Android now present health-risk tags in Chinese, such as 心率偏快、血氧偏低、压力偏高, and Android frames OPPO health data as a beta health-data integration instead of raw mock/fallback text.
- Pre-experiment protocol, deployment runbook, expert feedback template, product optimization plan, and technical landing whitepaper now consistently describe the ZIP evidence package rather than a JSON-only export.
- Evidence package `manifest.json` now includes package type, anonymized-file guidance, internal-review-only file guidance, and SHA-256 verification metadata.
- Mobile Web keeps manual PRIME/RUNNER/GUIDE role takeover available only under a collapsed “演示备用” control, so the default task path supports the AI dispatch story.
- Android task and incident screens now show the latest six on-site timeline logs with Chinese summaries for patient SOS, dispatch, CPR, AED, ambulance, handover, and archive events.
- Android Runner full-screen task now shows target AED name, location/floor/status, access notes, distance to AED, and AED return distance to patient using existing dispatch rationale and AED-site data.
- Mobile Web PRIME task card now shows the next CPR/AED step: start CPR, wait for AED, AED returning, attach pads, stop touching during analysis, or resume CPR after shock.
- Android Profile screen now includes four beta-location buttons (patient corridor, first-floor lobby, gate post, sports-field entrance) that call the existing authenticated location update path for dispatch-distance betanstrations.
- Pre-experiment protocol now includes an S01-S08 screenshot checklist and a timed 3-5 minute expert/PPT beta script.
- Expert feedback template now explicitly asks experts to review mobile Web, screenshot checklist, and beta script materials.
- `/api/health/detail` frontend diagnostics now report index readiness, index mtime, asset count, latest asset mtime, mobile chunk readiness, and desktop chunk readiness.
- Web dashboard and mobile Web now show concise safety-boundary copy: simulation/training/pre-experiment only, not a substitute for 120, AED voice prompts, professional medical judgment, or real diagnosis. Mobile archive copy now points users to anonymized evidence package materials.
- Android local archive entries now persist and display participant-perspective task summaries for patient, PRIME, RUNNER, GUIDE, and standby roles.
- Deployment runbook now includes production backup commands, SQLite online backup, 1Panel/OpenResty check commands, config path cautions, database rollback, and DB Git hygiene notes. P1 deployment checklist now marks env examples, `/opt` layout, health checks, and debug DB hygiene as complete.
- Android Home now emphasizes entering the current event and auto-joining first; creating a new event is labeled as beta backup to reduce accidental public-beta incident creation.
- Third-party resources doc now defines provider/fallback contracts for map, AI, health, push, and SMS. Product plan marks AI provider abstraction and SMS non-blocking login strategy complete.
- Backend now persists audit events in SQLite and exposes admin-protected `/api/audit/events`; `/api/health/detail` reports `storage.auditEventCount` and `security` settings.
- Lightweight per-process sliding-window rate limits now protect auth, admin, and actor mutation buckets through configurable `.env` values.
- Web dashboard now includes an “审计” control that loads recent login/beta/export/role/action audit events with actor, target, outcome, and request hash.
- Android session/token storage now uses AndroidX Security encrypted preferences with migration from legacy `lra_session`; if secure storage is unavailable, token persistence is disabled rather than falling back to plaintext.
- Android Gradle JVM args now use a larger heap/metaspace to avoid GC thrashing after adding AndroidX Security.
- Backend map distances now flow through `SpatialProvider`: default beta/Haversine distance, AMap WebService distance when `LRA_MAP_PROVIDER=amap` and `LRA_AMAP_SERVICE_KEY` is configured, and structured fallback metadata in health/detail and dispatch/meta.
- Android location now flows through a `LocationProvider`: app startup/terminal registration and the Profile location card can use system last-known location when runtime permission is granted; missing permission, disabled provider, or no recent location falls back to beta coordinates.
- Backend notifications now flow through `NotificationProvider`: default WebSocket state sync, future `jpush`/`vendor` placeholder values report adapter-pending fallback in `/api/health/detail.pushProvider`.
- Git checkpoint `5855cf4` (`checkpoint: add notification provider fallback`) was pushed to `origin/codex/competition-hardening`.
- Backend minimal RBAC now supports `LRA_ADMIN_PHONES`: matching registered users receive `privileges=["admin"]` from `/auth/me`, and admin APIs accept either formal admin Bearer tokens or legacy beta admin tokens. If only admin phones are configured, anonymous admin APIs stay closed.
- Git checkpoint `a635129` (`checkpoint: add admin account rbac`) was pushed to `origin/codex/competition-hardening`.
- Git checkpoint `337496d` (`checkpoint: align admin user type`) was pushed to `origin/codex/competition-hardening`.
- Mobile patient SOS delayed auto-dispatch no longer self-cancels the task that calls `designate_patient`; a positive-delay regression test now covers the exact `/mobile?beta=patient` failure mode.
- Web command center now exposes optional formal admin login when `LRA_ADMIN_PHONES` is configured, uses the admin Bearer token for management APIs and dashboard-simulated role actions, and keeps the old beta admin token as a fallback.
- Git checkpoint `9b373f4` (`checkpoint: fix patient sos and admin console login`) was pushed to `origin/codex/competition-hardening`.
- `/mobile-beta` now uses Chinese primary role labels; Web command-center audit labels, scenario phase, AED status, and visible timeline logs are localized for presentation while preserving raw backend logs for exports.
- Git checkpoint `a648ad8` (`checkpoint: polish beta visible labels`) was pushed to `origin/codex/competition-hardening`.
- Git checkpoint `c15d60f` (`checkpoint: record post-polish validation`) was pushed to `origin/codex/competition-hardening`.
- Git checkpoint `36b818b` (`checkpoint: record android validation`) was pushed to `origin/codex/competition-hardening`.
- Web command center now has a default-visible dispatch summary and collapses AI engine config, streaming decision details, scoring/rationale, online-terminal debug list, and logs under a 技术详情 toggle.
- `/mobile` no longer strips `incidentId` from deep links; `/mobile-beta?incidentId=...` passes the same target incident into all four beta iframes, and the mobile service worker cache was bumped to avoid the old redirect behavior.
- Mobile Web home now prioritizes SOS/current action before the user profile card, reducing emergency-state first-screen load.
- Mobile beta-stage and mobile login entry visible labels are now fully Chinese-first: “生命反射弧”, “演示模式”, “患者端”, with PRIME/RUNNER/GUIDE only kept as auxiliary role codes.
- Mobile archived-flow next actions checkpoint `e1fe48e` is pushed; archived mobile summary now has evidence package download, link copy, and console return actions.
- Web phone-preview inert buttons are now visibly disabled with explanatory tooltips, and archived command-center phone actions are disabled instead of remaining actionable.
- Android visible wording now avoids raw `HANDOVER`, hardcoded guide task IDs, and raw role status codes in summary rows; AI-facing user copy is framed as 云端智能协同 where visible to participants.
- Dispatch source labels are now normalized in Android active, overview, and archive screens, so provider values such as `fallback`, `ai`, `local_model`, and `siliconflow` do not appear directly to participants.
- Web command-center dispatch copy now says 智能调度/本地规则引擎 instead of exposed AI/debug phrasing in visible loading and technical-detail panels.
- Mobile Web now shows a compact event context strip with the current event short ID and sync state, making phone-browser terminals easier to verify during a multi-device beta.
- Mobile PWA service worker now caches an offline fallback page and serves it for `/mobile` when the network is unavailable instead of returning a blank/error response.

## Validation Log

- Backend targeted tests: `.\.venv\Scripts\python.exe -m unittest tests.test_server -v` passed, 22 tests OK.
- Backend full tests: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 26 tests OK.
- Web typecheck: `npm run typecheck` passed.
- Web production build: `npm run build` passed.
- Android debug APK: `gradle :app:assembleDebug --no-daemon` passed after removing the new Kotlin warning.
- Git checkpoint: `9fb32ed` (`checkpoint: add OPPO health beta loop`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package backend/Web validation: backend full tests passed, Web typecheck passed, Web build passed.
- Git checkpoint: `64dc256` (`checkpoint: add experiment evidence package`) created and pushed to `origin/codex/competition-hardening`.
- Health detail validation: backend full tests passed after adding version/auth/features/healthProvider diagnostics.
- Git checkpoint: `c27a34f` (`checkpoint: expand health diagnostics`) created and pushed to `origin/codex/competition-hardening`.
- Dispatch health-scoring validation: backend full tests passed, 27 tests OK.
- Git checkpoint: `6b531af` (`checkpoint: use health signals in dispatch`) created and pushed to `origin/codex/competition-hardening`.
- Local smoke check: temporary backend on `127.0.0.1:18080` with temp DB opened dashboard, initialized beta scenario, confirmed evidence-package UI, AED sites, health summaries, `healthSignals` dispatch field, and ZIP package contents. Smoke service stopped and temp DB removed.
- Evidence integrity targeted tests: `.\.venv\Scripts\python.exe -m unittest tests.test_server.ServerTestCase.test_health_detail_reports_storage_and_frontend_state tests.test_server.ServerTestCase.test_health_detail_reports_beta_readiness_after_bootstrap tests.test_server.ServerTestCase.test_beta_bootstrap_aed_dispatch_and_export tests.test_server.ServerTestCase.test_historical_export_uses_target_incident_roles -v` passed, 4 tests OK.
- Backend full tests after evidence integrity: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 29 tests OK.
- Android auto-join validation: `gradle :app:assembleDebug --no-daemon` passed.
- Web beta guidance validation: `npm run typecheck` passed; `npm run build` passed.
- Browser smoke: temporary backend on `127.0.0.1:18082` opened dashboard and `/mobile-beta`; confirmed dashboard flow labels, evidence-package entry, runbook labels, and 4 iframe panels. Temporary service stopped.
- Mobile SOS confirmation validation: `npm run typecheck` passed; `npm run build` passed; browser smoke on `127.0.0.1:18083/mobile?beta=patient` confirmed first click only shows confirmation while backend remains `CREATED`/`MONITORING`. Temporary service stopped.
- Input validation targeted tests: `.\.venv\Scripts\python.exe -m unittest tests.test_server.ServerTestCase.test_input_validation_rejects_invalid_location_health_and_aed_status tests.test_server.ServerTestCase.test_beta_bootstrap_aed_dispatch_and_export tests.test_server.ServerTestCase.test_client_location_and_aed_site_can_be_updated -v` passed, 3 tests OK.
- Backend full tests after input validation: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 30 tests OK.
- Health presentation validation: Web `npm run typecheck` passed, Web `npm run build` passed, Android `gradle :app:assembleDebug --no-daemon` passed.
- Evidence manifest targeted validation: `.\.venv\Scripts\python.exe -m unittest tests.test_server.ServerTestCase.test_beta_bootstrap_aed_dispatch_and_export -v` passed.
- Current full backend validation: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v` passed, 30 tests OK.
- Current Web validation: `npm run typecheck` passed; `npm run build` passed.
- Current Android validation: `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `69d7cc8` (`checkpoint: polish evidence and mobile beta`) created locally.
- Git checkpoint: `f11f607` (`checkpoint: update long task handoff`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `6342bb7` (`checkpoint: record pushed state`) created and pushed to `origin/codex/competition-hardening`.
- Android AED target validation: `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `5cc9534` (`checkpoint: show android AED target`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `b2c0370` (`checkpoint: record AED target push`) created and pushed to `origin/codex/competition-hardening`.
- Mobile Web next-step validation: `npm run typecheck` passed; `npm run build` passed.
- Git checkpoint: `5a18fc5` (`checkpoint: guide mobile CPR next steps`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `449815f` (`checkpoint: record mobile guidance push`) created and pushed to `origin/codex/competition-hardening`.
- Android beta-location validation: `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `261b05d` (`checkpoint: add android beta locations`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `e8e23b8` (`checkpoint: record beta locations push`) created and pushed to `origin/codex/competition-hardening`.
- Post-polish validation sweep: backend targeted evidence/export test passed; Web `npm run typecheck` passed; Web `npm run build` passed; Android `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `71b9834` (`checkpoint: record validation sweep`) created and pushed to `origin/codex/competition-hardening`.
- Expert materials doc validation: `rg` confirmed screenshot checklist, beta script, ZIP evidence package, and manifest wording are present; no JSON-only export wording reintroduced in touched docs.
- Git checkpoint: `fb8d3e2` (`checkpoint: add expert beta checklist`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `4aa7317` (`checkpoint: record expert checklist push`) created and pushed to `origin/codex/competition-hardening`.
- Health detail frontend diagnostics validation: targeted health-detail test passed; backend full unittest discovery passed, 30 tests OK.
- Git checkpoint: `af96cae` (`checkpoint: expand frontend health diagnostics`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `3526ca0` (`checkpoint: record health diagnostics push`) created and pushed to `origin/codex/competition-hardening`.
- Web disclaimer validation: `npm run typecheck` passed; `npm run build` passed.
- Git checkpoint: `95b4e88` (`checkpoint: add safety boundary copy`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `7e39ee3` (`checkpoint: record safety copy push`) created and pushed to `origin/codex/competition-hardening`.
- Android archive-summary validation: `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `b2b650f` (`checkpoint: summarize android archives`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `9e48785` (`checkpoint: record archive summary push`) created and pushed to `origin/codex/competition-hardening`.
- Deployment runbook doc validation: `rg` confirmed backup, rollback, 1Panel/OpenResty checks, `/opt/lifereflex`, `.env.example`, and DB hygiene notes are present.
- Git checkpoint: `aa0160b` (`checkpoint: harden deployment runbook`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `7e9c65e` (`checkpoint: record deployment runbook push`) created and pushed to `origin/codex/competition-hardening`.
- Android home action validation: `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `4600663` (`checkpoint: prioritize android current event`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `6b832e7` (`checkpoint: record android current event push`) created and pushed to `origin/codex/competition-hardening`.
- Final P0/P1 validation sweep: backend full unittest discovery passed, 30 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed; Android `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `f0ce716` (`checkpoint: record final validation sweep`) created and pushed to `origin/codex/competition-hardening`.
- Provider-contract doc validation: `rg` confirmed provider env vars, fallback behavior, AI provider, SMS provider, and no-secret rules are present.
- Git checkpoint: `615566d` (`checkpoint: document provider fallbacks`) created and pushed to `origin/codex/competition-hardening`.
- Security hardening targeted backend tests passed: audit events, health security fields, beta-admin protection, and auth rate limiting.
- Security hardening full validation: backend full unittest discovery passed, 32 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed; Android `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `4b0f11f` (`checkpoint: harden beta security`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `b07bb63` (`checkpoint: record security hardening push`) created and pushed to `origin/codex/competition-hardening`.
- Map provider targeted validation: `& '..\.venv\Scripts\python.exe' -m unittest tests.test_server.ServerTestCase.test_health_detail_reports_storage_and_frontend_state tests.test_server.ServerTestCase.test_dispatch_meta_is_serializable tests.test_server.ServerTestCase.test_amap_distance_provider_falls_back_without_service_key tests.test_server.ServerTestCase.test_beta_bootstrap_aed_dispatch_and_export -v` passed, 4 tests OK.
- Map provider full backend validation: `& '..\.venv\Scripts\python.exe' -m unittest discover -s tests -v` passed, 33 tests OK.
- Git checkpoint: `1259394` (`checkpoint: add map distance provider`) created and pushed to `origin/codex/competition-hardening`.
- Android location validation: `gradle :app:assembleDebug --no-daemon` passed; existing `PhoneAppRoot.kt` non-blocking Kotlin warning remains.
- Git checkpoint: `f30be6d` (`checkpoint: add android location provider`) created and pushed to `origin/codex/competition-hardening`.
- Notification provider targeted validation: `& '..\.venv\Scripts\python.exe' -m unittest tests.test_server.ServerTestCase.test_health_detail_reports_storage_and_frontend_state tests.test_server.ServerTestCase.test_push_provider_placeholder_falls_back_to_websocket tests.test_server.ServerTestCase.test_beta_bootstrap_aed_dispatch_and_export -v` passed, 3 tests OK.
- Notification provider full backend validation: `& '..\.venv\Scripts\python.exe' -m unittest discover -s tests -v` passed, 34 tests OK.
- Git checkpoint: `5855cf4` (`checkpoint: add notification provider fallback`) created and pushed to `origin/codex/competition-hardening`.
- RBAC targeted validation: `& '..\.venv\Scripts\python.exe' -m unittest tests.test_server.ServerTestCase.test_beta_admin_token_protects_public_beta_mutations tests.test_server.ServerTestCase.test_configured_admin_account_can_manage_beta tests.test_server.ServerTestCase.test_admin_phones_without_beta_token_keep_admin_apis_closed tests.test_server.ServerTestCase.test_health_detail_reports_storage_and_frontend_state -v` passed, 4 tests OK.
- RBAC full backend validation: first run exposed an audit event naming regression; after preserving `beta_admin_denied`, `& '..\.venv\Scripts\python.exe' -m unittest discover -s tests -v` passed, 36 tests OK.
- RBAC Web validation: `npm run typecheck` passed; `npm run build` passed.
- Git checkpoint: `a635129` (`checkpoint: add admin account rbac`) created and pushed to `origin/codex/competition-hardening`.
- Frontend RBAC type alignment validation: `npm run typecheck` passed after adding `AuthUser.privileges` to shared Web types.
- Git checkpoint: `337496d` (`checkpoint: align admin user type`) created and pushed to `origin/codex/competition-hardening`.
- Patient SOS delayed-dispatch targeted validation: `& '..\.venv\Scripts\python.exe' -m unittest tests.test_server.ServerTestCase.test_patient_sos_with_dispatch_delay_completes_auto_dispatch -v` passed, 1 test OK.
- Admin UI/backend targeted validation: `& '..\.venv\Scripts\python.exe' -m unittest tests.test_server.ServerTestCase.test_patient_sos_with_dispatch_delay_completes_auto_dispatch tests.test_server.ServerTestCase.test_configured_admin_account_can_manage_beta -v` passed, 2 tests OK.
- Current full backend validation: `& '..\.venv\Scripts\python.exe' -m unittest discover -s tests -v` passed, 37 tests OK.
- Current Web validation: `npm run typecheck` passed; first `npm run build` attempt used an invalid path and did not run; rerun from `server(web)\web` passed with dashboard chunk `214.23 kB` raw / `65.60 kB` gzip.
- Git checkpoint: `9b373f4` (`checkpoint: fix patient sos and admin console login`) created and pushed to `origin/codex/competition-hardening`.
- Web localization validation: `npm run typecheck` passed; `npm run build` passed with dashboard chunk `217.60 kB` raw / `66.63 kB` gzip.
- Browser smoke: temporary local backend on `127.0.0.1:18084` verified command-center Chinese scenario label and `/mobile-beta` Chinese role labels; temporary local backend on `127.0.0.1:18085` with `LRA_ADMIN_PHONES` verified admin-permission state shows “需要权限” and no longer reports “本地免口令”. Both services were stopped and temporary smoke DBs removed.
- Final post-polish validation sweep: backend unittest discovery passed, 37 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed with dashboard chunk `217.60 kB` raw / `66.63 kB` gzip.
- Git checkpoint: `c15d60f` (`checkpoint: record post-polish validation`) created and pushed to `origin/codex/competition-hardening`.
- Android validation sweep: `gradle :app:assembleDebug --no-daemon` passed; only the existing `android.overridePathCheck=true` experimental warning appeared.
- Git checkpoint: `36b818b` (`checkpoint: record android validation`) created and pushed to `origin/codex/competition-hardening`.
- Web presentation polish validation: `npm run typecheck` passed; `npm run build` passed with desktop `App-M71lbyYK.js` at `220.37 kB` raw / `67.15 kB` gzip and mobile `MobileApp-DDAEQ_T7.js` at `34.30 kB` raw / `11.09 kB` gzip.
- Browser smoke on temporary local backend `127.0.0.1:18086` passed using temp DB and beta token `LCY`: dashboard defaults to collapsed technical details, technical details expand to AI/log diagnostics, `/mobile-beta?incidentId=...` propagated the same incident into all four iframes, and `/mobile?beta=patient&slot=smoke2&incidentId=...` retained the incident link with the SOS action panel above the profile card. Temporary backend and temp DB were stopped/removed.
- Git checkpoint: `203b4e8` (`checkpoint: polish beta presentation links`) created and pushed to `origin/codex/competition-hardening`.
- Mobile Web scene/cooperation page now keeps AED location, teammate role, online state, and task status visible by default; dispatch score, rationale, health summaries, and risk tags are under “分派依据与健康摘要”.
- Mobile scene detail validation: Web `npm run typecheck` passed; Web `npm run build` passed with mobile `MobileApp-CJY-P70v.js` at `35.08 kB` raw / `11.20 kB` gzip. Browser smoke on temporary local backend `127.0.0.1:18087` confirmed collapsed scene hides “智能评分/风险标记” and expanded details reveal health/risk information. Temporary backend and temp DB were stopped/removed.
- Git checkpoint: `77a6a99` (`checkpoint: simplify mobile scene details`) created and pushed to `origin/codex/competition-hardening`.
- Web command center now surfaces `/api/health/detail.betaReadiness` as an “演示准备度” checklist covering terminal count, AED availability, location coverage, health-summary coverage, and evidence-export readiness.
- beta readiness validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-WEFAl1C8.js` at `222.46 kB` raw / `67.65 kB` gzip. Browser smoke on temporary local backend `127.0.0.1:18088` confirmed the readiness card and five checklist labels render, with initialized beta status “准备就绪”. Temporary backend and temp DB were stopped/removed.
- Git checkpoint: `548ed8f` (`checkpoint: show beta readiness`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `a648ad8` (`checkpoint: polish beta visible labels`) created and pushed to `origin/codex/competition-hardening`.
- Web command center/mobile deep-link checkpoint `7719d7b` (`checkpoint: record beta readiness`) is the current pushed HEAD.
- ZIP evidence package work in progress: added `expert_review_checklist.md` and `observer_record_form.csv` generation, manifest public-review guidance, backend package assertions, and synchronized pre-experiment/deployment/expert/product docs.
- Evidence package targeted validation: `& '..\.venv\Scripts\python.exe' -m unittest tests.test_server.ServerTestCase.test_beta_bootstrap_aed_dispatch_and_export -v` passed, 1 test OK.
- Evidence package full backend validation: `& '..\.venv\Scripts\python.exe' -m unittest discover -s tests -v` passed, 37 tests OK.
- Git checkpoint: `169a615` (`checkpoint: add expert evidence forms`) created and pushed to `origin/codex/competition-hardening`.
- Mobile beta visible-label polish: `/mobile` beta persona titles now use Chinese terminal names, and `/mobile-beta` four-frame captions describe duties rather than PRIME/RUNNER/GUIDE auxiliary codes.
- Mobile label validation: `npm run typecheck` passed; `npm run build` passed with mobile `MobileApp-DMzu6r2C.js` at `35.11 kB` raw / `11.20 kB` gzip and `MobilebetaStage-DmDdV0Yl.js` at `2.59 kB` raw / `1.20 kB` gzip.
- Git checkpoint: `de3107e` (`checkpoint: polish mobile role labels`) created and pushed to `origin/codex/competition-hardening`.
- Mobile Web archive summary now includes a protected “下载预实验证据包” action using the existing admin token/Bearer auth path, plus guidance to enter the beta token or admin account if permissions are missing.
- Mobile archive package validation: `npm run typecheck` passed; `npm run build` passed with mobile `MobileApp-DTIoJNCQ.js` at `36.43 kB` raw / `11.71 kB` gzip.
- Git checkpoint: `b885b96` (`checkpoint: add mobile evidence package download`) created and pushed to `origin/codex/competition-hardening`.
- Android emergency full-screen wording now describes “核心施救、AED 保障、环境清障” instead of visible PRIME/RUNNER/GUIDE codes during dispatching and AED return/delivery guidance.
- Android wording validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `4e08911` (`checkpoint: polish android emergency wording`) created and pushed to `origin/codex/competition-hardening`.
- Android CPR metronome visible English labels changed to Chinese: “CPR 节律辅助” and “语音辅助已启用”.
- Android CPR label validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `7b8392b` (`checkpoint: localize android cpr labels`) created and pushed to `origin/codex/competition-hardening`.
- Post-label/evidence-package validation sweep: backend `& '..\.venv\Scripts\python.exe' -m unittest discover -s tests -v` passed, 37 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-OIunfMkh.js` at `222.46 kB` raw / `67.65 kB` gzip and mobile `MobileApp-DTIoJNCQ.js` at `36.43 kB` raw / `11.71 kB` gzip; Android `gradle :app:assembleDebug --no-daemon` passed.
- Git checkpoint: `b02c634` (`checkpoint: record validation sweep`) created and pushed to `origin/codex/competition-hardening`.
- Whitepaper, pre-experiment protocol, and morning handoff are being aligned so the exported evidence package consistently mentions expert review checklist and observer record form, and presenter-facing role wording uses Chinese task names.
- Git checkpoint: `3362496` (`checkpoint: align evidence docs`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package now includes `pre_experiment_round_summary.csv`, a single-row per-round summary with anonymized participant codes, core timing metrics, coverage metrics, route distance, and blank observer/scoring columns for Excel aggregation across multiple simulated rounds. Documentation and tests are being updated to include the new file.
- Round-summary evidence validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed, 1 test OK; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `a852318` (`checkpoint: add pre-experiment round summary`) created and pushed to `origin/codex/competition-hardening`.
- README now documents `/mobile`, `/mobile-beta`, explicit validation commands, beta/admin auth settings, ZIP evidence package contents including `pre_experiment_round_summary.csv`, Chinese role presentation, and AI/map/health/push provider fallback behavior.
- README validation: `rg` confirmed mobile entries, evidence package, beta admin token, provider fallback, round summary, and Chinese role wording are present.
- Git checkpoint: `3e8b2ca` (`checkpoint: refresh project README`) created and pushed to `origin/codex/competition-hardening`.
- Context handoff resumed at `3e8b2ca`; state and morning handoff are being corrected so future work starts from the actual pushed README checkpoint.
- Git checkpoint: `3432d11` (`checkpoint: record README handoff`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package now includes `participant_consent_safety_brief.md` for pre-round safety/consent briefing and `participant_questionnaire.csv` for post-round participant scores. README, pre-experiment protocol, deployment runbook, expert feedback template, product plan, whitepaper, and morning handoff are updated to list these materials.
- Evidence participant-material validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `e4fca63` (`checkpoint: add participant evidence forms`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `92a5a77` (`checkpoint: record participant evidence push`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package now includes `baseline_vs_system_comparison.csv`, a no-system baseline vs LifeReflexArc system-round comparison template with system-round T1-T6 values prefilled and baseline/delta/score fields left for observer or Excel completion. Documentation and tests are updated to include the new public review file.
- Baseline comparison validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `be93e14` (`checkpoint: add baseline comparison evidence`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package now includes `analysis_guide.md`, a concise guide for reading T1-T6, questionnaire scores, baseline-vs-system deltas, PPT-safe conclusions, and prohibited clinical-effectiveness claims. Documentation and tests are updated to include the new public review file.
- Analysis guide validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `1f99b31` (`checkpoint: add experiment analysis guide`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `6b3c123` (`checkpoint: record analysis guide push`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package now includes `expert_feedback_form.md`, an event-specific expert feedback and signature form with incident metadata, anonymized role assignment, T1-T6 metric snapshot, review-material checklist, 1-5 rating table, open feedback sections, 100-300 word expert opinion area, and safety/legal wording. Tests and docs are updated to list it as a public/expert-review file.
- Expert feedback form validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `0674344` (`checkpoint: add expert feedback form`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `03f0360` (`checkpoint: record expert feedback push`) created and pushed to `origin/codex/competition-hardening`.
- Web command center now includes an “演示入口” panel with copy/open controls for the 4-terminal beta stage, patient terminal, core-rescuer terminal, AED-runner terminal, and guide terminal. After beta bootstrap, every link carries the current `incidentId`.
- beta entrance validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-DRfENPpz.js` at `226.67 kB` raw / `68.78 kB` gzip and mobile `MobileApp-BoXW44GW.js` at `36.43 kB` raw / `11.71 kB` gzip. Local Edge smoke on temporary backend `127.0.0.1:18089` passed; the smoke DB/process were removed after validation.
- Git checkpoint: `5dc86eb` (`checkpoint: add beta entrance links`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `1fe3190` (`checkpoint: record beta entrance push`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `19b14d1` (`checkpoint: record beta entrance state`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package now includes `facilitator_run_sheet.md`, a facilitator/observer run sheet for pre-checks, beta entrance links, T1-T6 cueing, observer notes, post-run package verification, questionnaire collection, and prohibited clinical-effectiveness wording.
- Facilitator run sheet validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `0a97fda` (`checkpoint: add facilitator run sheet`) created and pushed to `origin/codex/competition-hardening`.
- Git checkpoint: `637e9f6` (`checkpoint: record facilitator run sheet push`) created and pushed to `origin/codex/competition-hardening`.
- Web command-center beta entrance work in progress: added an “打开4个手机端” action that synchronously preopens the patient, core-rescuer, AED-runner, and guide mobile terminal tabs, then navigates each to the current incident-linked URL; if a browser blocks some tabs, it copies the four terminal links as fallback.
- Web 4-mobile opener validation: `npm run typecheck` passed; `npm run build` passed with desktop `App-S9VqVZaB.js`, mobile `MobileApp-DQI2rm0L.js`, and stage `MobilebetaStage-D4SVbmOo.js`.
- Browser smoke on temporary local backend `127.0.0.1:18090` with temp DB and beta token `LCY`: command center rendered “打开4个手机端” and incident-linked mobile URLs. The in-app browser blocked all four popups, and the new fallback message appeared with copied four-terminal links. Temporary process and smoke DB/logs were removed.
- Git checkpoint: `f775954` (`checkpoint: improve mobile beta opener`) created and pushed to `origin/codex/competition-hardening`.
- Android PRIME navigation polish in progress: removed visible `AHEAD`, `Start CPR`, and hardcoded `15 m`; the screen now shows Chinese labels and uses dispatch distance when available, otherwise shows a cautious no-precise-distance instruction.
- Android PRIME navigation validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning and a non-blocking `SosState` safe-call warning remain.
- Git checkpoint: `56ea748` (`checkpoint: polish android prime navigation`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package now includes `review_index.md`, a judge/expert-facing quick index that lists the recommended 3-minute file opening order, explains each public review artifact, summarizes T1-T6 metrics, separates external materials from internal-only files, and repeats prohibited clinical-effectiveness claims.
- Review-index validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `4116432` (`checkpoint: add evidence review index`) created and pushed to `origin/codex/competition-hardening`.
- Mobile Web archived-flow permission UX in progress: the archive card now has an inline beta-token field that saves to the same `lra_beta_admin_token` used by the Web command center and passes it to protected evidence-package download.
- Mobile Web archive permission validation: `npm run typecheck` passed; `npm run build` passed with mobile `MobileApp-BiCFGvZL.js`. Browser smoke on temporary local backend `127.0.0.1:18091` with temp DB and beta token `LCY` created an archived incident and confirmed `/mobile?beta=guide&incidentId=...` shows “演示口令” plus “下载预实验证据包”. Temporary process and smoke DB/logs were removed.
- Git checkpoint: `35768d6` (`checkpoint: improve mobile evidence download auth`) created and pushed to `origin/codex/competition-hardening`.
- Latest validation sweep: backend `& '..\.venv\Scripts\python.exe' -m unittest discover -s tests -v` passed, 37 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-DAHq5Wl1.js`, mobile `MobileApp-BiCFGvZL.js`, and stage `MobilebetaStage-DKdt3ZAL.js`; Android `gradle :app:assembleDebug --no-daemon` passed. Existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `2605c33` (`checkpoint: record latest validation sweep`) created and pushed to `origin/codex/competition-hardening`.
- Android visible label polish in progress: added shared UI formatters for floor labels, AED status, and location source, replacing visible `1F/2F`, `AVAILABLE`, and `app-beta-fallback` style strings with Chinese labels in Android incident/AED/profile screens.
- Android visible label validation: `gradle :app:assembleDebug --no-daemon` passed in `lifereflex(app)`; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `0d0e02d` (`checkpoint: polish android location labels`) created and pushed to `origin/codex/competition-hardening`.
- Archive/evidence summary copy hardening: Web phone-preview archive summary now derives total duration, task count, and AED record from the incident logs/roles instead of fixed `04:35`, `3人`, and `成功`; removed empty clickable handover-summary affordance; Android `HandoverArchiveScreen` now receives `IncidentState`, computes the same summary from logs/roles, and replaces the unsupported NFC-transfer promise with a reviewable handover-summary message; phone routing now sends `HANDOVER`/`ARCHIVED` to the archive screen for all roles.
- Visible wording cleanup: changed remaining judge-facing `AI 分派/AI 分配`, `硅基流动`, `医创赛演示`, `评委浏览器`, simulated AED/health wording, and raw map fallback labels to more cautious Chinese product language. `/mobile-beta` now includes “归档并下载证据包” as the final guided step.
- Archive copy validation: `rg` found no remaining high-risk visible strings among `04:35`, `3人`, `成功 (1次)`, `NFC 触碰`, `等待 AI`, `AI 分派`, `AI 分配`, `调用 AI`, `硅基流动`, `server（云端服务）/.env`, `医创赛演示`, `评委浏览器`, `自动生成模拟点位`, and `模拟健康` in the checked Web/Android UI files.
- Archive copy validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App--36xguvV.js`, mobile `MobileApp-C2UVJLdb.js`, and stage `MobilebetaStage-BlmPj_Gp.js`; Android `gradle :app:assembleDebug --no-daemon` passed with existing non-blocking `android.overridePathCheck=true`, `SosState` safe-call, and AndroidX Security deprecation warnings; backend full unittest discovery passed, 37 tests OK.
- Git checkpoint: `1493e5c` (`checkpoint: harden archive summary copy`) created and pushed to `origin/codex/competition-hardening`.
- Mobile visible copy polish: changed mobile/default location, organization, safety copy, archive package messages, Web title/tooltip labels, and Android health-card explanation from more internal “模拟/预实验/OPPO” wording to `协同演示现场`, `事件证据包`, and `健康摘要` style language while retaining safety boundaries.
- Mobile visible copy validation: `rg` found no remaining target visible strings among `医创赛模拟现场`, `模拟社区`, `本次模拟流程`, `手动/模拟点位`, `预实验证据包`, `OPPO 健康摘要`, `模拟接入`, `模拟点位`, `模拟健康`, `mock fallback`, and `AI 调度引擎` in the checked Web/mobile/Android UI files.
- Mobile visible copy validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-B4okz-ZB.js`, mobile `MobileApp-CQYLGBPK.js`, stage `MobilebetaStage-B2oMgsLu.js`, and shared domain `domain-0m1nEXxg.js`; Android `gradle :app:assembleDebug --no-daemon` passed with existing non-blocking `android.overridePathCheck=true` warning.
- Git checkpoint: `fdaf060` (`checkpoint: polish visible beta copy`) created and pushed to `origin/codex/competition-hardening`.
- Mobile archived-flow next actions: archived mobile summary now offers `下载事件证据包`, `复制本轮链接`, and `返回总控台`; archived role action state now shows `已完成归档` instead of prompting the guide/responder to respond again after the event is archived.
- Mobile archived-flow validation: Web `npm run typecheck` passed; Web `npm run build` passed with mobile `MobileApp-YRz2tLyc.js` and CSS `MobileApp-MGToxcyi.css`. Browser smoke on temporary local backend `127.0.0.1:18092` with temp DB and beta token `LCY` created an archived incident, confirmed the mobile archive page renders `下载事件证据包`, `复制本轮链接`, `返回总控台`, and no longer shows the old `响应清障接驳` action in archived state. Temporary backend/frontend processes and smoke DB files were stopped/removed.
- Visible action/wording validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-vYbqPRcR.js` at `229.50 kB` raw / `69.59 kB` gzip and mobile `MobileApp-BhrtJOWA.js` at `38.10 kB` raw / `12.22 kB` gzip; Android `gradle :app:assembleDebug --no-daemon` passed with the existing non-blocking `android.overridePathCheck=true` warning. Targeted visible-string scan found no remaining `onClick={() => {}}`, `Golden Rescue Time`, `Analyze`, `Detecting`, `现场任务已转入 HANDOVER`, hardcoded guide task ID, or raw role-status summary rows in checked UI files.
- Dispatch-source label validation: Android `gradle :app:assembleDebug --no-daemon` passed; Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-CBug2GXj.js` at `229.51 kB` raw / `69.58 kB` gzip and mobile `MobileApp-OoG1rKgg.js` at `38.10 kB` raw / `12.22 kB` gzip. Targeted visible-string scan found no remaining `加载 AI 调度说明失败`, `AI 流式分派过程`, `AI 正在生成角色选择理由`, `规则/AI 处理中`, `规则调度`, raw archive `entry.dispatchSource`, or raw active `incidentState.dispatchSource` display in checked UI files.
- Mobile PWA validation: Web `npm run typecheck` passed; Web `npm run build` passed with mobile `MobileApp-D6grxFFA.js` at `38.76 kB` raw / `12.42 kB` gzip and CSS `MobileApp-BtgHt77P.css` at `15.83 kB` raw / `3.57 kB` gzip. Local Vite preview on `127.0.0.1:18093` returned 200 for `/mobile` and `/offline.html`; browser smoke confirmed `/offline.html` shows `移动端暂时离线` and `重新连接`, and `/mobile` shows `浏览器应急端`, `演示模式直达`, and `进入移动端`. Temporary preview process and logs were stopped/removed.
- Git checkpoint: `17e999f` (`checkpoint: add mobile pwa fallback`) created and pushed to `origin/codex/competition-hardening`.
- Evidence package data dictionary slice ready to checkpoint: ZIP generation now includes `data_dictionary.md`, manifest public/expert-review guidance lists it, and backend package tests assert presence, content, manifest privacy guidance, and hash manifest membership.
- Documentation sync ready to checkpoint: README, deployment runbook, expert feedback template, pre-experiment protocol, product optimization plan, technical whitepaper, and morning handoff now list `data_dictionary.md` alongside analysis guide and public review artifacts.
- Evidence data dictionary validation: targeted `test_beta_bootstrap_aed_dispatch_and_export` passed, 1 test OK; backend full unittest discovery passed, 37 tests OK after documentation sync.
- Git checkpoint: `7640379` (`checkpoint: add evidence data dictionary`) created and pushed to `origin/codex/competition-hardening`.
- Visible wording polish in progress: Web/mobile download and AED copy now says `事件证据包` instead of visible `预实验证据包`; Android archive summary says `匿名化协同记录`; Android location beta labels now present as `协同点位`; Android health card presents `健康数据增强` and `健康摘要样例` instead of visible OPPO/mock/fallback wording.
- Visible wording validation: targeted `rg` found no remaining `下载预实验证据包`, `预实验患者端`, `匿名化预实验记录`, `已切换到演示位置`, `OPPO Health mock fallback`, `演示健康数据`, `OPPO 健康增强`, or `可用于调度评分与预实验记录` in checked Web/Android UI files.
- Web visible wording validation: `npm run typecheck` passed; `npm run build` passed with desktop `App-hfqjqD1K.js` at `229.51 kB` raw / `69.57 kB` gzip and mobile `MobileApp-BZNCyjRt.js` at `38.76 kB` raw / `12.41 kB` gzip.
- Android visible wording validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning and AndroidX Security deprecation warnings remain non-blocking.
- Git checkpoint: `2b75ae1` (`checkpoint: polish visible evidence wording`) created and pushed to `origin/codex/competition-hardening`.
- Medical-compliance wording slice in progress: Web beta-phone and Android alert/countdown screens now use `协同 SOS`、`一级危急`、`疑似心脏骤停`、`启动协同响应` instead of `SOS Alert`、`SCA`、`自动呼叫急救` or diagnosis-like trigger text; intro wording now says `现场协同空窗风险`.
- Health authorization slice in progress: mobile Web and Android health samples now send/display `authorizationStatus=sample` and show `样例接入`, avoiding the appearance of completed real OPPO Health authorization.
- Android archive slice in progress: Android archive AED summary no longer treats `HANDOVER`/`ARCHIVED` alone as `AED 已送达`; it now requires AED delivery, analysis, shock, or pickup status.
- Medical-compliance validation: targeted `rg` found no remaining `SOS Alert`, `SCA`, `自动呼叫急救`, `触发心脏骤停`, `死亡真空`, `150 米`, `购物中心`, `LCY 移动端`, `如 LCY`, Android health-provider `authorizationStatus = "authorized"`, or mobile health sample `authorizationStatus: 'authorized'` in checked Web/Android UI files.
- Medical-compliance validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-BG832lIu.js` at `229.52 kB` raw / `69.58 kB` gzip and mobile `MobileApp-DCIArHZJ.js` at `38.76 kB` raw / `12.41 kB` gzip; Android `gradle :app:assembleDebug --no-daemon` passed with existing `android.overridePathCheck=true` warning.
- Git checkpoint: `f5fefa7` (`checkpoint: soften medical beta wording`) was already created and pushed to `origin/codex/competition-hardening`.
- Public evidence anonymization slice: `review_index.md`, `timeline.csv`, and `dispatch_rationale.csv` now use `participantCode` for external review instead of raw beta/user IDs; timeline log text replaces participant IDs before export, and dispatch rationale no longer exposes a raw `userId` column.
- Public evidence anonymization docs: generated `data_dictionary.md`, README, and deployment runbook now describe `participantCode`, anonymized timeline/rationale fields, and the public/internal file boundary consistently.
- Public evidence anonymization validation: backend full unittest discovery passed, 37 tests OK; targeted `rg` confirms `docs/DEPLOYMENT_RUNBOOK.md`, README, and generated dictionary copy no longer describe public timeline/rationale exports with raw `actorUserId`/`userId` fields. Remaining `actorUserId` matches are internal parser keys only.
- Git checkpoint: `7b3b3af` (`checkpoint: anonymize public evidence files`) created and pushed to `origin/codex/competition-hardening`.
- Health-summary boundary slice: backend beta bootstrap health summaries now use `authorizationStatus="sample"` and neutral Chinese notes instead of implying real OPPO authorization; `HealthSignalSummary` validates source, authorization status, activity level, sleep quality, risk tags, and non-negative update timestamps with normalization.
- Health-summary boundary validation: targeted backend tests for beta evidence export, invalid health inputs, and health export passed; full backend unittest discovery passed, 37 tests OK; targeted `rg` found no `OPPO Health mock` or hardcoded sample `authorizationStatus="authorized"` patterns in checked server/Web/Android source.
- Git checkpoint: `18dec36` (`checkpoint: tighten health summary boundaries`) created and pushed to `origin/codex/competition-hardening`.
- Incident-specific evidence download slice: shared Web download helper now accepts an optional incident id, mobile archived-flow downloads the currently opened incident package, and Web command-center package export uses the loaded incident id instead of always `/current/package`.
- Web archive AED summary slice: desktop phone-preview archive summary no longer infers `AED 已送达` from `HANDOVER` or `ARCHIVED` alone; it requires AED pickup, delivery, analysis, or shock status/log evidence.
- Incident package validation: targeted historical export/package test passed; full backend unittest discovery passed, 37 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-DRTpuSLA.js` at `229.74 kB` raw / `69.67 kB` gzip and mobile `MobileApp-i_i6eOca.js` at `38.94 kB` raw / `12.46 kB` gzip.
- Git checkpoint: `32affef` (`checkpoint: fix incident evidence downloads`) created and pushed to `origin/codex/competition-hardening`.
- Web/mobile health authorization display slice: shared domain formatting now translates `sample`/`authorized`/`denied`/`not_connected`; Web phone-preview health cards and mobile health summaries surface `样例接入` or the relevant authorization state instead of only showing data source and vitals.
- Health authorization display validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-B_LHHgCt.js` at `229.98 kB` raw / `69.71 kB` gzip and mobile `MobileApp-Bjui0p8t.js` at `38.89 kB` raw / `12.45 kB` gzip.
- Git checkpoint: `40cdc98` (`checkpoint: show health authorization status`) created and pushed to `origin/codex/competition-hardening`.
- Public-doc wording sync: README, third-party resources, deployment runbook, pre-experiment protocol, product plan, technical whitepaper, and morning handoff now use safer public-facing terms such as `协同演示场景`, `疑似心脏骤停协同流程`, `事件证据包`, and `现场审阅端` while preserving legitimate `预实验` protocol wording.
- Public-doc wording validation: targeted `rg` found no remaining `医创赛演示`, `评委浏览器`, `触发心脏骤停模拟`, `下载预实验证据包`, `导出预实验证据包`, `触发心脏骤停`, `自动呼叫急救`, `死亡真空`, `SOS Alert`, or `SCA` in README/docs excluding `LONG_TASK_STATE.md`.
- Git checkpoint: `226186a` (`checkpoint: sync public beta wording`) created and pushed to `origin/codex/competition-hardening`.
- Android HeyTap readiness slice: app now passes application context into the mock OPPO health provider, checks whether `com.heytap.health` or OPPO/HeyTap market packages are installed via `PackageManager`, and surfaces a readiness row/detail in Android health cards while keeping real SDK authorization blocked and sample summaries active.
- Android HeyTap readiness validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `fe8fcc1` (`checkpoint: add android health readiness`) created and pushed to `origin/codex/competition-hardening`.
- Latest validation sweep: backend full unittest discovery passed, 37 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-B_LHHgCt.js` at `229.98 kB` raw / `69.71 kB` gzip and mobile `MobileApp-Bjui0p8t.js` at `38.89 kB` raw / `12.45 kB` gzip; Android `gradle :app:assembleDebug --no-daemon` passed with existing non-blocking `android.overridePathCheck=true` warning.
- Git checkpoint: `fa7abc1` (`checkpoint: record validation sweep`) created and pushed to `origin/codex/competition-hardening`.
- Android error-state hardening slice: added a shared Android `ErrorMessages` mapper for HTTP status codes, server detail payloads, timeout/DNS/connectivity/TLS/cleartext failures, and WebSocket payload/failure states; `IncidentViewModel`, `SessionViewModel`, and `WsClient` now surface actionable Chinese messages instead of raw exception text.
- Android session validation hardening: stored sessions are only cleared when `/auth/me` explicitly returns unauthorized; transient network or certificate failures now keep the saved session and show a diagnostic message.
- Android error-state validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning and AndroidX Security deprecation warnings remain non-blocking.
- Git checkpoint: `65260e1` (`checkpoint: harden android error states`) created and pushed to `origin/codex/competition-hardening`.
- Android local HTTP/debug network slice: added debug-only `networkSecurityConfig` and `usesCleartextTraffic=true` so debug APKs can connect to `http://LAN-IP:PORT` or emulator/local backends during development while release manifest remains without cleartext flags; README and Android local config template now explain HTTP/WS debug versus HTTPS/WSS public beta usage.
- Android debug-network validation: `gradle :app:assembleDebug --no-daemon` passed; `gradle :app:processReleaseMainManifest --no-daemon` passed; `rg` confirmed cleartext/networkSecurityConfig only appears in the debug merged manifest, not release.
- Git checkpoint: `451bbd8` (`checkpoint: allow android debug local http`) created and pushed to `origin/codex/competition-hardening`.
- Mobile PWA cache-resilience slice: `mobile-sw.js` now caches `/mobile` in the app shell, uses network-first navigation for the mobile shell, stale-while-revalidate for mobile static assets/manifest/offline/icon, keeps API and WebSocket requests uncached, enables navigation preload when available, and accepts `SKIP_WAITING` update messages; `main.tsx` now asks waiting/installing mobile service workers to activate so new mobile shells do not linger behind an old cache during betanstrations.
- Mobile PWA validation: Web `npm run typecheck` passed; Web `npm run build` passed with mobile `MobileApp-DSEHznZU.js` at `38.89 kB` raw / `12.45 kB` gzip; local Vite preview on `127.0.0.1:18094` returned 200 for `/mobile`, `/offline.html`, and `/mobile-sw.js`; Browser DOM smoke confirmed `/mobile` renders `浏览器应急端`/beta entries and `/offline.html` renders `移动端暂时离线`/`重新连接`. The Node REPL browser sandbox could not inspect `navigator.serviceWorker`, so SW registration/cache internals were verified by build, served script content, and visible-page smoke; temporary preview processes were stopped.
- Git checkpoint: `a179220` (`checkpoint: strengthen mobile pwa cache`) created and pushed to `origin/codex/competition-hardening`.
- Android visible wording polish: removed remaining presentation-rough wording such as `本地假会话`, `救援记录`, `被救援记录`, `黄金救援时间`, and `心脏骤停事件已完成院前协同救援` from key Android login, emergency, archive, and phase screens; replaced with service-account/encrypted-session, cooperative record, response window, and suspected-cardiac-arrest cooperative-flow wording.
- Android wording validation: targeted `rg` found no remaining `本地假会话|心脏骤停事件已完成|救援记录|被救援记录|黄金救援时间|急救接力|协同救援` in Android source; remaining `急救车` hits are normal 120 ambulance context. `gradle :app:assembleDebug --no-daemon` passed with existing non-blocking `android.overridePathCheck=true` and AndroidX Security deprecation warnings.
- Git checkpoint: `8e683f5` (`checkpoint: polish android presentation wording`) created and pushed to `origin/codex/competition-hardening`.
- Android release-readiness slice: Gradle release signing now reads `LRA_RELEASE_STORE_FILE`, `LRA_RELEASE_STORE_PASSWORD`, `LRA_RELEASE_KEY_ALIAS`, and `LRA_RELEASE_KEY_PASSWORD` from Gradle properties, untracked `local.properties`, or environment variables; if all four are present, `release` is signed, otherwise the release variant remains unsigned for readiness checks. `local.properties.example`, README, deployment runbook, and new `docs/ANDROID_RELEASE_READINESS.md` document debug APK, release keystore/SHA1, secret boundaries, build commands, and expert-beta preflight steps.
- Android release-readiness validation: `gradle :app:assembleDebug --no-daemon` passed and produced `app-debug.apk` (~14.18 MB); `gradle :app:assembleRelease --no-daemon` passed and produced `app-release-unsigned.apk` (~9.65 MB) because release signing secrets are not configured. The previous `PhoneAppRoot.kt` safe-call warning was removed; remaining warnings are the existing `android.overridePathCheck=true` experimental notice and AndroidX Security deprecations.
- Git checkpoint: `cb45832` (`checkpoint: add android release readiness`) created and pushed to `origin/codex/competition-hardening`.
- Morning handoff refresh: `docs/MORNING_HANDOFF.md` now lists the latest Android error-state, debug HTTP, PWA cache, Android presentation wording, and release-readiness checkpoints; it also records debug/release APK artifact paths and sizes, PWA smoke validation, and the release keystore/SHA1 next step.
- Git checkpoint: `83a368c` (`checkpoint: refresh morning handoff`) created and pushed to `origin/codex/competition-hardening`.
- Documentation sync slice: `docs/OVERNIGHT_IMPLEMENTATION_PLAN.md`, `docs/PRODUCT_OPTIMIZATION_PLAN.md`, and `docs/TECHNICAL_LANDING_WHITEPAPER.md` now reflect Android release readiness, debug-only HTTP/LAN support, user-friendly Android error states, mobile PWA cache/update resilience, and current validation counts.
- Documentation sync validation: manual diff review found no secrets and kept the medical framing at simulation/training/pre-experiment scope; targeted wording scan found no unsafe clinical efficacy claims or exposed credential values in the changed docs.
- Git checkpoint: `fbfd9a8` (`checkpoint: sync release readiness docs`) created and pushed to `origin/codex/competition-hardening`.
- Web preflight report slice: Web command center now exports a Markdown self-check report covering beta readiness, warnings, auth status, frontend/backend health, audit/rate-limit state, map/push/health provider fallback, terminal tasks, AED sites, beta links, and safe usage boundaries without writing beta tokens, admin tokens, API keys, or personal phone numbers.
- Web preflight validation: `npm run typecheck` passed; `npm run build` passed with desktop `App-DHwe7OoC.js`; local integrated backend smoke on `127.0.0.1:18096` with temp DB and beta token `LCY` initialized a scenario and confirmed `自检报告`/`导出自检` buttons render with incident binding. The in-app Browser backend does not support download events, so downloaded Markdown content could not be captured through that tool; report generation was validated by code review, typecheck/build, and DOM smoke. Temporary preview/backend ports `18095`/`18096` were stopped.
- Git checkpoint: `aa1c634` (`checkpoint: add beta preflight report`) created and pushed to `origin/codex/competition-hardening`.
- Evidence-package verification script slice: added `scripts/verify_evidence_package.py`, a standard-library CLI that validates `manifest.json`, SHA-256 hashes, byte counts, duplicate/missing files, unsafe ZIP paths, manifest file-list consistency, and public/internal privacy guidance. README and deployment runbook now document how to run it after downloading a ZIP package.
- Evidence-package verification validation: targeted `test_evidence_package_verification_script_accepts_current_package` passed; `python scripts\verify_evidence_package.py --help` worked; backend full unittest discovery passed, 38 tests OK. Temporary `output/preflight-smoke` artifacts were removed after smoke testing.
- Git checkpoint: `8c44d97` (`checkpoint: add evidence package verifier`) created and pushed to `origin/codex/competition-hardening`.
- Morning handoff refresh: `docs/MORNING_HANDOFF.md` now records the Web self-check report, evidence-package verifier, latest checkpoints `aa1c634`/`8c44d97`, backend 38-test validation, and updated wake-up/beta instructions.
- Git checkpoint: `7dfebfd` (`checkpoint: refresh handoff with verifier`) created and pushed to `origin/codex/competition-hardening`.
- Expert feedback remediation slice: evidence packages now include `expert_feedback_summary.csv`, a public-review-friendly CSV for aggregating multiple experts' scores, positive feedback, risk concerns, required improvements, owner, priority, remediation status, follow-up evidence, and second-review comments. README, deployment runbook, package README, review index, manifest privacy guidance, and backend package tests now include the new file.
- Expert feedback remediation validation: targeted package/export and verifier tests passed; backend full unittest discovery passed, 38 tests OK.
- Git checkpoint: `2443136` (`checkpoint: add expert feedback summary`) created and pushed to `origin/codex/competition-hardening`.
- Resume/status sync slice: updated `docs/LONG_TASK_STATE.md`, `docs/MORNING_HANDOFF.md`, `docs/PRE_EXPERIMENT_PROTOCOL.md`, `docs/PRODUCT_OPTIMIZATION_PLAN.md`, and `docs/TECHNICAL_LANDING_WHITEPAPER.md` so the new expert-feedback remediation loop is visible in the morning handoff, pre-experiment flow, product plan, and whitepaper.
- Documentation sync validation: targeted `rg` confirmed `expert_feedback_summary.csv` and expert-remediation wording now appear in README, deployment runbook, morning handoff, pre-experiment protocol, product plan, and technical whitepaper; targeted safety scan found risky clinical-claim terms only inside cautionary/negative contexts; `git diff --check` passed with only Windows CRLF normalization warnings.
- Git checkpoint: `709b7e9` (`checkpoint: sync expert feedback docs`) created and pushed to `origin/codex/competition-hardening`.
- Multi-round evidence summary slice: added `scripts/summarize_evidence_rounds.py`, a standard-library CLI that verifies one or more evidence-package ZIPs, merges each package's `pre_experiment_round_summary.csv`, and writes a single CSV with package path, package SHA-256, verification status, manifest incident id, generated time, phase, and round metrics. README, deployment runbook, and pre-experiment protocol now document the command for multi-round simulated experiments.
- Multi-round evidence summary validation: project `.venv` already existed and was used. `python scripts\summarize_evidence_rounds.py --help` passed; `python -m py_compile scripts\verify_evidence_package.py scripts\summarize_evidence_rounds.py` passed; targeted backend test `test_evidence_round_summary_script_merges_packages` passed.
- Full backend validation after multi-round summary slice: `python -m unittest discover -s tests -v` passed, 39 tests OK.
- Git checkpoint: `87e1941` (`checkpoint: add evidence round summary tool`) created and pushed to `origin/codex/competition-hardening`.
- Round-summary analysis slice: added `scripts/analyze_round_summary.py`, a standard-library CLI that reads the merged round-summary CSV and writes a Markdown report with sample count, verification status, phase distribution, mean/median/min/max for timing, coverage, and scenario context metrics, plus PPT-safe conclusion boundaries. README, deployment runbook, and pre-experiment protocol now document the command after `summarize_evidence_rounds.py`.
- Round-summary analysis validation: project `.venv` already existed and was used. `python scripts\analyze_round_summary.py --help` passed; `python -m py_compile scripts\verify_evidence_package.py scripts\summarize_evidence_rounds.py scripts\analyze_round_summary.py` passed; targeted backend test `test_round_summary_analysis_script_writes_ppt_safe_report` passed after adding event-id traceability to the report; full backend unittest discovery passed, 40 tests OK.
- Git checkpoint: `9ed144d` (`checkpoint: add round analysis report`) created and pushed to `origin/codex/competition-hardening`.
- Expert-material sync slice: `docs/EXPERT_FEEDBACK_TEMPLATE.md` now includes `expert_feedback_summary.csv`, `round-summary.csv`, and `round-analysis.md` in the review-material checklist and adds a dedicated evidence-chain/analysis-material feedback section. `docs/TECHNICAL_LANDING_WHITEPAPER.md` now mentions the multi-round CSV/Markdown analysis flow and 40 passing backend tests. `docs/PRODUCT_OPTIMIZATION_PLAN.md` now documents the same evidence-analysis toolchain and current 40-test validation.
- Expert-material sync validation: targeted `rg` confirmed `round-summary.csv`, `round-analysis.md`, `summarize_evidence_rounds.py`, `analyze_round_summary.py`, `expert_feedback_summary.csv`, and current 40-test wording appear in the relevant docs; safety wording scan found only cautionary `不替代/不要写成真实临床疗效证明/不应表述为` contexts.
- Git checkpoint: `d999a0d` (`checkpoint: sync expert evidence materials`) created and pushed to `origin/codex/competition-hardening`.
- Analysis-report percentage fix: `scripts/analyze_round_summary.py` now scales `roleAssignmentCompleteness` from the stored 0-1 ratio to a 0-100 percentage in the report table, while leaving existing percent fields unchanged. Backend test now asserts the generated report shows role assignment completeness as 100 instead of 1.
- Analysis-report percentage validation: targeted backend test `test_round_summary_analysis_script_writes_ppt_safe_report` passed; full backend unittest discovery passed, 40 tests OK.
- Git checkpoint: `af1bec5` (`checkpoint: fix evidence analysis percentages`) created and pushed to `origin/codex/competition-hardening`.
- Pre-experiment report-builder slice: added `scripts/build_pre_experiment_report.py`, a standard-library CLI that accepts evidence ZIP files, directories, or glob patterns and writes both `round-summary.csv` and `round-analysis.md` into a chosen output directory. README, deployment runbook, pre-experiment protocol, and morning handoff now recommend this one-command workflow before the older two-step flow.
- Pre-experiment report-builder validation: project `.venv` was used. `python scripts\build_pre_experiment_report.py --help` passed; `python -m py_compile scripts\verify_evidence_package.py scripts\summarize_evidence_rounds.py scripts\analyze_round_summary.py scripts\build_pre_experiment_report.py` passed; targeted backend test `test_pre_experiment_report_builder_creates_summary_and_analysis` passed; full backend unittest discovery passed, 41 tests OK.
- Resume safety check after interruption: `git status --short --branch` shows branch `codex/competition-hardening` aligned with `origin/codex/competition-hardening`; pending checkpoint files are README, deployment runbook, morning handoff, pre-experiment protocol, long-task state, the new report-builder script, and backend tests. Runtime/user files remain excluded: `server(web)/data/lifereflexarc.db`, `OPPO健康SDK文档.md`, and `output/`.
- Diff hygiene validation: `git diff --check` passed with only Windows CRLF normalization warnings.
- Git checkpoint: `ed7a17d` (`checkpoint: add pre-experiment report builder`) created and pushed to `origin/codex/competition-hardening`.
- Evidence-analysis documentation sync slice: `docs/PRODUCT_OPTIMIZATION_PLAN.md`, `docs/TECHNICAL_LANDING_WHITEPAPER.md`, and `docs/EXPERT_FEEDBACK_TEMPLATE.md` now point reviewers and teammates to `scripts/build_pre_experiment_report.py` as the preferred one-command multi-round ZIP analysis flow, while keeping the two-step scripts available for troubleshooting.
- Evidence-analysis documentation validation: targeted `rg` confirmed the one-command flow, `round-summary.csv`, `round-analysis.md`, and current 41-test wording appear in public planning/review materials; safety wording scan found clinical-effectiveness terms only in cautionary or negative contexts; `git diff --check` passed with only Windows CRLF normalization warnings.
- Git checkpoint: `f758a1e` (`checkpoint: sync evidence analysis docs`) created and pushed to `origin/codex/competition-hardening`.
- Evidence-package internal guidance slice: generated ZIP materials now include the one-command multi-round analysis workflow inside `README.md` and `analysis_guide.md`; `review_index.md` includes `expert_feedback_summary.csv` in public materials; expert-facing health-summary wording now uses sample/beta-health wording instead of raw engineering `mock` labels.
- Evidence-package internal guidance validation: targeted package/export test passed; `python -m py_compile` passed for all four evidence scripts; full backend unittest discovery passed, 41 tests OK; targeted wording scan found no exposed `OPPO Health mock` or `mock/演示` wording in generated evidence-package templates outside negative test assertions.
- Git checkpoint: `ae4bc9c` (`checkpoint: add evidence package analysis guidance`) created and pushed to `origin/codex/competition-hardening`.
- Chart-data analysis slice: `scripts/analyze_round_summary.py` can now write `round-chart-data.csv` with metric group, key, label, unit, valid round count, mean, median, min, max, chart hint, and PPT-safe-use boundary. `scripts/build_pre_experiment_report.py` now generates `round-summary.csv`, `round-analysis.md`, and `round-chart-data.csv` in one command. README, deployment runbook, pre-experiment protocol, morning handoff, product plan, whitepaper, expert template, and generated ZIP guidance now document the chart data.
- Chart-data validation: `analyze_round_summary.py --help` and `build_pre_experiment_report.py --help` passed; `python -m py_compile` passed for all four evidence scripts; targeted backend tests for round-summary analysis and one-command report builder passed; full backend unittest discovery passed, 41 tests OK; `git diff --check` passed with only Windows CRLF normalization warnings.
- Git checkpoint: `1c1eab2` (`checkpoint: add pre-experiment chart data`) created and pushed to `origin/codex/competition-hardening`.
- Morning handoff refresh slice: `docs/MORNING_HANDOFF.md` now records the recent evidence-analysis checkpoints from `87e1941` through `1c1eab2`, including the one-command report builder and `round-chart-data.csv` output, so the wake-up report reflects the actual latest pushed branch.
- Morning handoff refresh validation: `git status --short --branch` confirms branch `codex/competition-hardening` aligned with `origin/codex/competition-hardening`; only runtime/user files remain untracked or modified outside the checkpoint scope (`server(web)/data/lifereflexarc.db`, `OPPO健康SDK文档.md`, `output/`).
- Git checkpoint: `8e482be` (`checkpoint: refresh evidence handoff`) created and pushed to `origin/codex/competition-hardening`.
- Web preflight evidence-processing slice: `server(web)/web/src/app/App.tsx` now includes a post-beta evidence-processing section in the exported Markdown self-check report, telling operators how to verify a downloaded evidence ZIP and how to generate `round-summary.csv`, `round-analysis.md`, and `round-chart-data.csv` from multiple rounds.
- Web preflight evidence-processing validation: Web `npm run typecheck` passed before this resume; Web `npm run build` passed after the report update with desktop bundle `App-BZWfXHVx.js` and mobile bundle `MobileApp-CMWWhsBf.js`.
- Git checkpoint: `a7aa77c` (`checkpoint: add preflight evidence processing steps`) created and pushed to `origin/codex/competition-hardening`.
- Resume continuation after checkpoint: `git status --short --branch` shows only runtime/user files outside checkpoint scope (`server(web)/data/lifereflexarc.db`, `OPPO健康SDK文档.md`, `output/`). Started scanning for the next low-risk competition-hardening slice.
- Web/mobile visible-beta polish slice: Web command-center phone preview now avoids fixed personal names, fake status-bar values, fixed AED location, fixed ambulance plate/distance, fixed prime/runner distances, and raw `km/m` labels; it derives AED target/distance from incident/AED state when available and uses neutral role/device wording otherwise. Mobile Web CPR guidance now starts its CPR/AED cycle from the current incident's CPR or AED-shock log timestamp instead of wall-clock Unix time, and the event context strip keeps a one-line “my next action” visible across tabs.
- Web/mobile visible-beta validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop bundle `App-Czvvf4Pu.js` and mobile bundle `MobileApp-C9dwup_s.js`; targeted `rg` scan found no remaining `在线安卓终端|自动智能分派|粤B|120QA|3km|50m|小李|二楼服务台|商场场景|心脏骤停事件|14:00|5G|100%|03:30|黄金急救时间|15<span` in Web/mobile source, with only a non-visible animation coordinate match remaining.
- Git checkpoint: `07881be` (`checkpoint: polish web mobile beta cues`) created and pushed to `origin/codex/competition-hardening`.
- Evidence-package SHA-256 slice: both current and incident-specific ZIP package endpoints now compute the package body SHA-256 once, expose it as `X-LifeReflexArc-Package-Sha256`, and record `filename`, `bytes`, and `packageSha256` in the audit event metadata for `experiment_package_exported`.
- Evidence-package SHA-256 validation: targeted audit/package test passed; full backend unittest discovery passed, 41 tests OK; `git diff --check` passed with only Windows CRLF normalization warnings.
- Git checkpoint: `6303c76` (`checkpoint: add evidence package hash header`) created and pushed to `origin/codex/competition-hardening`.
- Android release endpoint guard slice: `lifereflex(app)/app/build.gradle.kts` now fails release build tasks if `LRA_API_BASE` does not start with `https://` or `LRA_WS_BASE` does not start with `wss://`; debug builds remain able to use local HTTP/WS for LAN testing. `lifereflex(app)/local.properties.example` and `docs/ANDROID_RELEASE_READINESS.md` document the guard and expected failure test.
- Android release endpoint guard validation: `gradle :app:assembleDebug --no-daemon` passed; `gradle :app:assembleRelease --no-daemon` passed; intentionally running `gradle :app:assembleRelease -PLRA_API_BASE=http://127.0.0.1:8080/ -PLRA_WS_BASE=ws://127.0.0.1:8080/ws --no-daemon` failed as expected with `LRA_API_BASE must start with https:// for release builds...`.
- Git checkpoint: `4a4a48b` (`checkpoint: guard android release endpoints`) created and pushed to `origin/codex/competition-hardening`.
- Evidence verifier privacy-leak slice: `scripts/verify_evidence_package.py` now derives raw participant IDs from internal `experiment.json` and `clients.csv`, then scans manifest-declared public/expert-review files for those IDs. A public file containing `beta-patient`/raw user IDs now fails verification instead of silently passing.
- Evidence verifier privacy-leak validation: targeted positive/negative verifier tests passed; `verify_evidence_package.py --help` passed; `python -m py_compile` passed for the evidence scripts; full backend unittest discovery passed, 42 tests OK; `git diff --check` passed with only Windows CRLF normalization warnings.
- Git checkpoint: `b6792f0` (`checkpoint: strengthen evidence verifier privacy scan`) created and pushed to `origin/codex/competition-hardening`.
- Evidence quality report slice: ZIP packages now include `evidence_quality_report.json`, a public/expert-review-safe JSON report with anonymized participant codes, key event coverage, missing nodes, metric availability, quality score, readiness level, provider/fallback warnings, and simulation-only usage boundaries.
- Evidence quality report validation: targeted package/export, completed-flow quality-report, and verifier tests passed; full backend unittest discovery passed, 43 tests OK; `git diff --check` passed with only Windows CRLF normalization warnings.
- Git checkpoint: `b89f55b` (`checkpoint: add evidence quality report`) created and pushed to `origin/codex/competition-hardening`.
- Android REST state-seeding slice: `IncidentRepository.getCurrentIncident()` and `getIncident()` now update the local `StateFlow` immediately from REST responses, so Android screens can render the incident snapshot before the first WebSocket `STATE` frame arrives.
- Android REST state-seeding validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `b52e5b6` (`checkpoint: seed android state from rest`) created and pushed to `origin/codex/competition-hardening`.
- Android WebSocket reconnect slice: `WsClient` now keeps a single reconnect `Job`, cancels stale reconnects on incident switch, manual close, and successful open, and avoids scheduling duplicate delayed reconnects when `onClosed`/`onFailure` fire close together.
- Android WebSocket reconnect validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `6751516` (`checkpoint: make android websocket reconnect single flight`) created and pushed to `origin/codex/competition-hardening`.
- Android emergency action debounce slice: full-screen emergency action buttons now expose a shared pending-action state, ignore duplicate submissions while an action is in flight, disable all action CTAs until the request returns, and show `提交中...` on the active action. Covered actions include CPR started, AED analysis, AED shock, AED pickup/delivery, ambulance arrival, and handover completion.
- Android emergency action debounce validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `c1ff709` (`checkpoint: debounce android emergency actions`) created and pushed to `origin/codex/competition-hardening`.
- Android regular mission-card pending-action slice: Tasks and Incident tabs now pass the shared pending-action state into `MissionPanel`; CPR, AED pickup/delivery, and ambulance-arrival CTAs show `提交中...` and disable while any emergency action is in flight, matching the full-screen emergency flow and reducing repeat taps in betas.
- Android regular mission-card pending-action validation: `gradle :app:assembleDebug --no-daemon` passed; existing `android.overridePathCheck=true` experimental warning remains non-blocking.
- Git checkpoint: `da1655d` (`checkpoint: show android mission action pending state`) created and pushed to `origin/codex/competition-hardening`.
- Evidence verifier negative-test slice: backend tests now use a reusable evidence-package helper and assert the independent verifier rejects tampered manifest SHA-256 values, unlisted ZIP payload files, public/internal privacy-guidance overlap, and raw participant ID leaks in public review files.
- Evidence verifier negative-test validation: targeted verifier tests passed; full backend unittest discovery passed, 46 tests OK.
- Git checkpoint: `9ced23d` (`checkpoint: add evidence verifier negative tests`) created and pushed to `origin/codex/competition-hardening`.
- Web/mobile WebSocket stale-callback guard slice: desktop command-center and mobile Web now clear refs before closing old sockets, ignore stale `onopen`/`onmessage`/`onerror`/`onclose` callbacks, bind reconnects to the connection's incident id, and cancel pending mobile reconnects on logout/unmount. This reduces ghost reconnect/status flips during event switching, logout, or network flaps.
- Web/mobile WebSocket stale-callback validation: `npm run typecheck` passed; `npm run build` passed with desktop bundle `App-CCmke60w.js` and mobile bundle `MobileApp-CEP25Ntl.js`.
- Git checkpoint: `6b967cb` (`checkpoint: guard web websocket stale callbacks`) created and pushed to `origin/codex/competition-hardening`.
- Public documentation sync slice: README, deployment runbook, product plan, and technical whitepaper now mention Web/mobile WebSocket stale-callback protection, Android pending-action guards, evidence verifier bad-package negative tests, 46 passing backend tests, and the latest Web build artifacts. This keeps teammate/PPT-facing materials aligned with the current branch.
- Public documentation sync validation: `git diff --check` passed; targeted scan found remaining clinical-effectiveness wording only in cautionary contexts and no newly exposed credential values.
- Git checkpoint: `594a410` (`checkpoint: sync reliability validation docs`) created and pushed to `origin/codex/competition-hardening`.
- Backend action idempotency slice: repeated completed role actions now return the current incident phase without appending duplicate logs. Covered completed states include CPR started, AED analysis, AED shock, AED picked/delivered, ambulance arrived, and archived handover completion. This keeps evidence timelines clean if a client retries after weak network or rapid taps.
- Backend action idempotency validation: targeted role-action tests passed; full backend unittest discovery passed, 47 tests OK.
- Git checkpoint: `7b015d3` (`checkpoint: make backend actions idempotent`) created and pushed to `origin/codex/competition-hardening`.
- Backend join idempotency slice: repeated manual join by the same role user now returns the current incident phase without resetting already advanced role status such as CPR started or AED analysis back to JOINED. This protects mobile refresh/retry paths after the participant has already started task execution.
- Backend join idempotency validation: targeted repeated-join/action tests passed; full backend unittest discovery passed, 48 tests OK.
- Git checkpoint: `fba6303` (`checkpoint: keep repeated joins idempotent`) created and pushed to `origin/codex/competition-hardening`.
- Backend auto-join evidence slice: when an AI-assigned terminal taps auto-join, an ASSIGNED role is now advanced to JOINED and a single auto-joined timeline entry is recorded. Repeated auto-join taps for the same user remain idempotent and do not duplicate logs.
- Backend auto-join validation: targeted auto-join, patient SOS, and evidence export tests passed; full backend unittest discovery passed, 49 tests OK.
- Git checkpoint: `c191d41` (`checkpoint: record assigned auto joins`) created and pushed to `origin/codex/competition-hardening`.
- Mobile Web single-flight slice: mobile `runAction` now uses a ref-level in-flight guard in addition to visible button disabled states. This closes the same-frame double-tap window for SOS, auto-join, role actions, location sync, and evidence package download before React state has re-rendered.
- Mobile Web single-flight validation: `npm run typecheck` passed; `npm run build` passed with desktop bundle `App-WniwvbhZ.js`, mobile bundle `MobileApp-VrPZVJ6u.js`, and stage bundle `MobilebetaStage-BqdjEtRj.js`.
- Git checkpoint: `187f0e3` (`checkpoint: guard mobile actions single flight`) created and pushed to `origin/codex/competition-hardening`.
- Android auto-join refresh slice: after `connectCurrent(autoJoin=true)` calls the backend auto-join endpoint, the app now immediately fetches the joined incident snapshot before opening the WebSocket. This lets the APK show the JOINED role/task state without waiting for the first realtime frame.
- Android auto-join refresh validation: `gradle :app:assembleDebug --no-daemon` passed; only the existing `android.overridePathCheck=true` experimental warning appeared.
- Evidence-quality multi-round summary slice: `scripts/summarize_evidence_rounds.py` now reads each ZIP's `evidence_quality_report.json` and adds fixed `round-summary.csv` columns for quality level, quality score, total issue count, critical/warning/info counts, missing key-event count/list, and warning codes. Older ZIPs without the report keep blank quality fields instead of failing.
- Evidence-quality analysis slice: `scripts/analyze_round_summary.py` now adds a `证据质量` Markdown section with quality-level distribution, total critical/warning/info counts, missing-key-event total, and quality-score statistics; `round-chart-data.csv` now includes quality score, critical count, warning count, and missing-key-event count rows for Excel/PPT charts.
- Evidence-quality documentation sync: README, deployment runbook, pre-experiment protocol, morning handoff, product plan, technical whitepaper, and expert feedback template now describe that multi-round summaries include evidence quality fields for deciding which simulation rounds need rerun or manual review, while keeping clinical-effectiveness wording cautious.
- Evidence-quality validation: `python -m py_compile scripts\verify_evidence_package.py scripts\summarize_evidence_rounds.py scripts\analyze_round_summary.py scripts\build_pre_experiment_report.py` passed; targeted evidence-summary/report-builder tests passed; full backend unittest discovery passed, 49 tests OK.
- Quality review triage slice: `scripts/analyze_round_summary.py` now adds a `需复核轮次` table that lists non-ready rounds, rounds with critical/warning/missing-key-event counts, and legacy CSV rows without quality fields as `missing_quality_report`. README, deployment runbook, pre-experiment protocol, and morning handoff now explain the table as a rerun/manual-supplement triage aid.
- Quality review triage validation: `python -m py_compile scripts\summarize_evidence_rounds.py scripts\analyze_round_summary.py scripts\build_pre_experiment_report.py` passed; targeted report/report-builder tests passed; full backend unittest discovery passed, 49 tests OK.
- Web preflight quality-review sync slice: `server(web)/web/src/app/App.tsx` self-check Markdown now tells operators to open `round-analysis.md` and review the `证据质量` / `需复核轮次` sections before handing chart data to PPT, and includes `round-analysis.md` among recommended external materials.
- Web preflight quality-review validation: `npm run typecheck` passed; `npm run build` passed with desktop `App-BJA77-CK.js`, mobile `MobileApp-C_SM1_pZ.js`, and stage `MobilebetaStage-DKrKuX3T.js`.
- Git checkpoint: `b7e5a96` (`checkpoint: sync preflight evidence quality guidance`) created and pushed to `origin/codex/competition-hardening`.
- Review-action CSV slice: `scripts/analyze_round_summary.py` can now write `round-review-actions.csv` via `--review-output`, and `scripts/build_pre_experiment_report.py` now generates it by default alongside `round-summary.csv`, `round-analysis.md`, and `round-chart-data.csv`. The CSV labels each round as usable, usable with notes, requiring rerun/manual supplement, or excluded/manual review, so PPT and expert materials can be filtered before charting.
- Review-action CSV documentation sync: README, deployment runbook, pre-experiment protocol, product plan, technical whitepaper, expert feedback template, evidence-package internal guidance, Web self-check report, and morning handoff now mention `round-review-actions.csv` and explain that it is a pre-PPT triage aid, not clinical evidence.
- Review-action CSV validation: `python -m py_compile scripts\verify_evidence_package.py scripts\summarize_evidence_rounds.py scripts\analyze_round_summary.py scripts\build_pre_experiment_report.py` passed; targeted evidence analysis/report-builder tests passed; full backend unittest discovery passed, 49 tests OK; Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-JkgAD_yM.js`, mobile `MobileApp-7Q1VHnBQ.js`, and stage `MobilebetaStage-DyZIJVu5.js`.
- Git checkpoint: `da9fdf2` (`checkpoint: add review action analysis output`) created and pushed to `origin/codex/competition-hardening`.
- Mobile beta SOS gate slice: `/mobile?beta=prime|runner|guide` now renders a read-only waiting panel instead of a patient SOS trigger, while `/mobile?beta=patient` keeps the two-step SOS confirmation. `handlePatientSos` also guards against non-patient beta personas so accidental responder-tab clicks cannot start a patient alert.
- Mobile beta SOS gate validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-y6G93YAO.js`, mobile `MobileApp-xJvHSufN.js`, and stage `MobilebetaStage-CoUTmnw3.js`. Browser smoke on a temporary local stack `127.0.0.1:18092` confirmed patient beta has an enabled `启动 SOS` button, first click only changes it to `再次点击确认 SOS` without starting a countdown, and core-rescuer beta has no enabled SOS button plus a disabled `等待患者端启动 SOS` control. Temporary backend/frontend processes, DB, log, and pid files were stopped/removed.
- Git checkpoint: `0b127b5` (`checkpoint: gate mobile beta sos trigger`) created and pushed to `origin/codex/competition-hardening`.
- Evidence-package SHA display slice: Web command-center package downloads and mobile archived-flow package downloads now read `X-LifeReflexArc-Package-Sha256` and show the downloaded filename plus SHA-256 in a success message. The shared mobile download helper returns filename/hash metadata; the Web command center shows successful downloads in a green status bar rather than the red request-error area.
- Evidence-package SHA display validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-C1o_GuN-.js`, mobile `MobileApp-D6sQFbqf.js`, and stage `MobilebetaStage-DylKZH_L.js`. Browser smoke on temporary local backend `127.0.0.1:18093` with beta token `LCY` confirmed Web header package download displays `证据包已下载` and a 64-character SHA-256 without `请求异常`; mobile `/mobile?beta=guide&incidentId=...` archived package download displays `事件证据包已下载` and a 64-character SHA-256 without error. Temporary process, DB, log, and pid files were stopped/removed.
- Git checkpoint: `8ee452a` (`checkpoint: show package hash after download`) created and pushed to `origin/codex/competition-hardening`.
- Web readiness warning alignment slice: the command-center readiness card now derives its color, title, count, visible warning text, and exported Markdown self-check status from one combined readiness state. Admin-auth gaps are counted and displayed alongside backend readiness warnings, so the card no longer says ready while the self-check report still lists management permission as unresolved.
- Web readiness warning alignment validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-DKGpinBD.js`, mobile `MobileApp-CWxAHAbu.js`, and stage `MobilebetaStage-cNrZP1Tv.js`.
- Git checkpoint: `4df1382` (`checkpoint: align readiness warnings`) created and pushed to `origin/codex/competition-hardening`.
- Mobile beta stage binding-status slice: `/mobile-beta` now shows whether the stage is bound to an incident, displays a shortened incident id, explains that all four terminals share the same event, and marks each terminal panel with the shared event id or an unbound warning. This reduces onsite confusion when four browser tabs/frames are opened for judging.
- Mobile beta stage binding-status validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-C8-rsJ4D.js`, mobile `MobileApp-9a_Fy8WK.js`, and stage `MobilebetaStage-7g9iM-bl.js`; targeted source scan confirmed the visible bound/unbound/shared-event labels are present.
- Git checkpoint: `e8283d3` (`checkpoint: show beta stage incident binding`) created and pushed to `origin/codex/competition-hardening`.
- Web evidence-package SHA copy slice: after a Web command-center ZIP download with `X-LifeReflexArc-Package-Sha256`, the success banner now keeps the downloaded filename/hash metadata and shows a `复制 SHA` button. The button uses the existing clipboard fallback and replaces the success text with a copied confirmation, making it easier to paste the package hash into reviewer notes or pre-experiment records.
- Web evidence-package SHA copy validation: Web `npm run typecheck` passed; Web `npm run build` passed with desktop `App-DVQkGLsA.js`, mobile `MobileApp-Dhqmeawv.js`, and stage `MobilebetaStage-bWe17Ylh.js`.
- Git checkpoint: `7ea7537` (`checkpoint: add package hash copy action`) created and pushed to `origin/codex/competition-hardening`.
- Competition terminology cleanup slice: source UI, mobile Web copy, backend evidence-package templates, analysis scripts, national-competition materials, public docs, and the local round-01 evidence folder now use safer wording such as `系统级预实验`, `急救协同训练`, and `流程复盘`; the old risk-prone wording has been removed from normal repository text and the regenerated evidence ZIP.
- Competition terminology cleanup validation: `rg` scan for the old wording family returned no matches outside ignored cache output; Web `npm run typecheck` passed; targeted backend evidence/export tests passed using `server(web)/.venv`; regenerated the local round-01 evidence ZIP and verified its extracted contents also contain no old wording.

## Blockers Summary

- Real OPPO Health approval, legal/application submission, secrets, and compatible device validation remain user-only blockers.
- Implemented mock/fallback closed loop instead of unattended real SDK submission or secret handling.

## Next Unblocked Action

Continue with another low-risk Web/mobile beta quality slice or run a broader validation sweep. Good next candidates from sidecar review: add a small Web smoke for the readiness card, continue polishing judge-visible beta affordances, or refresh morning handoff with the newest three checkpoints. Keep excluding SQLite runtime DB, OPPO SDK doc, `output/`, APK/AAB build outputs, keystores, local.properties, and temp Playwright/browser artifacts.

## Resume Instructions

Read `docs/LONG_TASK_STATE.md`, `docs/LONG_TASK_BLOCKERS.md`, `docs/PRODUCT_OPTIMIZATION_PLAN.md`, and run `git status --short --branch`; then continue the current milestone without relying on chat memory.
