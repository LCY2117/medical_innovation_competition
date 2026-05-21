# Long Task Blockers

This file records user-only actions that should not stop independent engineering work.

## Active Blockers

- OPPO Health service cooperation and data permission approval may require legal agreement acceptance, manual submission, real-name/company/school verification, or OPPO-side review. Do not complete those unattended.
- If OPPO login expires and asks for SMS/email/QR/slider verification, record the exact page/action and continue local mock/fallback work.
- If OPPO console displays clientId/clientSecret or asks to create/copy secrets, do not expose or commit them.
- Current Android package remains com.example.lifereflexarc; changing to a formal package name would require re-binding third-party keys and is out of scope unless explicitly requested.
- True OPPO Health data validation requires compatible phone/HeyTap Health app/account and wearable/history data. If unavailable, keep demo on mock/fallback provider.
- Real SDK dependency activation remains blocked until OPPO cooperation approval, SDK repository access, privacy disclosure, and user-triggered authorization flow are confirmed.

## Resolved Blockers

- Chrome extension browser control is available and OPPO console login state was valid during readiness check.
