# LifeReflexArc Overnight Implementation Plan

## Goal

Build LifeReflexArc into a competition-ready medical innovation system:

- installable Android APK
- release APK readiness path without committing signing secrets
- public cloud web console
- complete simulated cardiac-arrest rescue workflow
- location/AED/AI dispatch support with safe fallback
- exportable experiment data
- preparation materials for low-cost pre-experiment and expert feedback

## Non-Goals For This Overnight Run

- Do not submit real-name applications, payment forms, or legal attestations on third-party websites without the user present.
- Do not store API keys, passwords, certificates, or private tokens in source files.
- Do not claim clinical effectiveness. The project is a simulated emergency collaboration and decision-support prototype.
- Do not perform destructive server operations or database migrations without backups.

## Safety Rules

- Preserve all user changes.
- Work on branch `codex/competition-hardening`.
- Prefer `/opt/lifereflex` for server deployment preparation.
- Third-party accounts that need QR login, email/SMS verification, real-name verification, paid quota, or final legal agreement are recorded as blockers and skipped.
- Build features so the system still works in beta mode without map/vendor API keys.

## Priority 1: Planning And Resource Prep

Deliverables:

- `docs/OVERNIGHT_IMPLEMENTATION_PLAN.md`
- `docs/THIRD_PARTY_RESOURCES.md`
- third-party account blocker list
- map/API key application checklist

Validation:

- Files exist and are readable.
- No secrets are written.

## Priority 2: Engineering Baseline

Deliverables:

- backend dependency files for runtime and tests
- frontend package metadata and build script
- Android reproducible build metadata where possible
- Android release signing inputs documented as local/env-only secrets
- environment examples for cloud URL, AI provider, and map provider

Validation:

- backend tests pass
- frontend build starts from `npm install && npm run build`
- Android build path is documented or wrapper generated if possible
- Android debug and release readiness builds pass

## Priority 3: Core Competition Product Features

Deliverables:

- location model fields for users/clients
- AED site inventory model
- dispatch scoring uses qualification + health risk + distance + AED access
- dispatch explanation exposed to web/app
- event timeline and export endpoint
- beta scenario bootstrap endpoint

Validation:

- existing backend tests pass
- new tests cover beta data, AED inventory, export, and dispatch rationale

## Priority 4: App And Web Usability

Deliverables:

- app defaults point to production-friendly domain config
- app can submit simulated/manual location
- web console shows AED, location, dispatch rationale, export controls
- frontend builds cleanly

Validation:

- TypeScript build passes
- manual smoke test can complete the workflow locally

## Priority 5: Cloud Deployment Preparation

Deliverables:

- deployment guide/script updates
- production `.env.example` values
- 1Panel/OpenResty compatible checklist

Validation:

- server deployment steps are documented
- no production secrets committed

## Priority 6: Pre-Experiment And Expert Feedback Materials

Deliverables:

- low-cost pre-experiment protocol
- data recording tables
- expert feedback template
- PPT asset checklist

Validation:

- materials align with competition notice: experimental design, feasibility, innovation, application, experiment record

## Stop Conditions

Stop only for:

- destructive operation risk
- account/verification/legal action requiring user identity
- production secret exposure risk
- server operation that could interrupt existing services without a rollback path

Otherwise, continue to the next unblocked priority.

## Final Report Format

- completed work
- changed files
- validation commands and results
- third-party account blockers
- remaining risks
- next recommended action
