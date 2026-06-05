# Mobile Web UI Redesign Plan

## Goal

Make `/mobile` feel like a national-final-ready emergency collaboration terminal:

- closer to the native Android app's product tone
- clearer in urgent states
- lower cognitive load for patient, PRIME, RUNNER, GUIDE, and observer roles
- reliable on phone-sized browser viewports
- still fully compatible with the existing beta and cloud workflow

## Non-Goals

- Do not change backend data contracts unless a UI bug truly requires it.
- Do not alter production secrets, runtime databases, certificates, or third-party keys.
- Do not implement real OPPO Health SDK approval or real map vendor account actions.
- Do not deploy to the public server unless explicitly approved for this session.

## Design Direction

- Tone: calm emergency command terminal, not marketing page and not cyberpunk.
- Palette: quiet dark base, restrained blue-gray surfaces, role colors used deliberately.
- Red: reserved for patient SOS and critical emergency actions.
- Layout: one primary task per screen; details move below, into tabs, or into compact panels.
- Controls: large touch targets, fixed bottom navigation, clear disabled/loading states.
- Evidence: logs and dispatch explanations remain available but never compete with the main action.

## Work Items

1. Audit current `/mobile` structure, CSS, and screenshots.
2. Extract reusable app-like visual tokens into mobile CSS.
3. Refactor the mobile shell hierarchy:
   - calmer top bar
   - stronger incident/role status band
   - single primary action area
   - cleaner bottom tabs
4. Polish key cards:
   - patient SOS
   - role mission
   - scene/AED
   - timeline/logs
   - profile/health/location
5. Validate:
   - `npm run typecheck`
   - `npm run build`
   - browser screenshots for patient, responder, logs, and narrow width
   - no horizontal overflow on common mobile widths

## Acceptance Criteria

- `/mobile` no longer looks like compressed dashboard content.
- Patient flow emphasizes SOS and current incident state.
- Responder flow emphasizes assigned role and next action.
- Details are readable without overwhelming the first viewport.
- The UI works at about 390px wide with no horizontal overflow.
- Build/typecheck pass.
- Screenshots show dark and light mode surfaces are coherent.
