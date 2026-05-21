# OPPO Health Integration Checklist

## Phase 1 Goal

- Keep the LifeReflexArc demo usable before OPPO review is complete.
- Add a mock/fallback health-data path for Android, mobile web, backend export, and Web console display.
- Prepare the real OPPO Health SDK/API integration points without storing secrets in Git.

## Application Materials

- App name: LifeReflexArc / 生命反射弧.
- Current Android package: `com.example.lifereflexarc`.
- Prepare a 520 x 520 px logo under 3 MB.
- Prepare a fixed HTTPS host and redirect URI for future OAuth/cloud callbacks.
- Prepare a short cooperation purpose, cooperation plan, and minimal health-data permission request.
- Only request phase-1 read permissions that support the demo: profile identifier, daily activity, heart rate, sleep, blood oxygen, and sport metadata summary.

## Compliance

- Disclose OPPO Health SDK in the privacy policy before real SDK initialization.
- Initialize the real SDK only after the user has accepted the app privacy policy.
- Real health-data reads must be triggered by a visible user action.
- Do not log or commit OPPO `clientId`, `clientSecret`, access tokens, refresh tokens, signing material, SDK repository credentials, or decryption keys.
- Treat mock/fallback values as demo evidence, not clinical diagnosis.

## Android SDK Preparation

- Keep Android package visibility entries for:
  - `com.heytap.health`
  - `com.heytap.market`
  - `com.oppo.market`
- Use a `HealthSignalProvider` abstraction.
- Keep `MockOppoHealthSignalProvider` as the default provider until OPPO approval, SDK dependency access, compatible phone, HeyTap Health app, and user authorization are all ready.
- Real SDK provider should later implement:
  - health app installation check
  - `HeytapHealthApi.init(context)`
  - `authorityApi().request(...)`
  - `authorityApi().valid(...)`
  - `authorityApi().revoke(...)`
  - `dataApi().read(...)`

## Backend And Export

- `ClientInfo.healthSignals` is the internal phase-1 summary model.
- `/api/clients/health` updates the authenticated terminal's health summary.
- Experiment export includes `clients[].healthSignals`, giving the team a low-cost pre-experiment data trail.
- `.env.example` contains OPPO placeholders only; real values belong in `.env` or server secret storage.

## User-Only Blockers

- OPPO cooperation application and legal agreement acceptance.
- Real-name, school, company, email, SMS, QR, slider, or face verification.
- Receiving or copying OPPO `clientId`, `clientSecret`, access tokens, SDK credentials, or encryption material.
- Publishing the OPPO app, changing package names, or binding production callback domains.
- Real wearable validation, which requires a compatible phone, HeyTap Health account/app, and health history or wearable data.

## Phase 2 Candidates

- Real OPPO Android SDK authorization-page launch.
- Server-side OAuth callback and encrypted token storage.
- Heart-rate anomaly and fall-detection callbacks after compliance approval.
- Raw sample ingestion into a privacy-minimized `WearableSample` table.
- Expert-facing export with anonymized health summary columns.
