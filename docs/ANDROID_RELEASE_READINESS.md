# Android Release Readiness

This checklist is for turning the current installable debug APK into a more formal competition/expert-demo APK without committing secrets.

## Current State

- Debug APK path: `lifereflex(app)/app/build/outputs/apk/debug/app-debug.apk`
- Package name: `com.example.lifereflexarc`
- Public backend: `https://lifereflex.mddcommunity.top/`
- Public WebSocket: `wss://lifereflex.mddcommunity.top/ws`
- Debug builds may use local HTTP for LAN testing.
- Release builds should use HTTPS/WSS only.

## Secret Boundary

Do not commit these files or values:

- `*.jks`, `*.keystore`, APK/AAB artifacts, `local.properties`
- keystore passwords, key passwords, API keys, `.env`
- OPPO client secrets, access tokens, SDK repository credentials

The repository `.gitignore` already excludes common APK, keystore, local properties, and env files.

## Release Signing Inputs

The Gradle build can sign `release` automatically when all four values are provided through `local.properties` or environment variables:

```properties
LRA_RELEASE_STORE_FILE=C:\\Users\\LCY\\secrets\\lifereflex-release.jks
LRA_RELEASE_STORE_PASSWORD=
LRA_RELEASE_KEY_ALIAS=lifereflex
LRA_RELEASE_KEY_PASSWORD=
```

If any value is missing, Gradle leaves the release variant unsigned; debug APK builds are unaffected.

Generate a competition keystore once and keep it outside the repository:

```powershell
keytool -genkeypair -v `
  -keystore "$env:USERPROFILE\secrets\lifereflex-release.jks" `
  -alias lifereflex `
  -keyalg RSA `
  -keysize 2048 `
  -validity 10000
```

Check the release SHA1:

```powershell
keytool -list -v `
  -keystore "$env:USERPROFILE\secrets\lifereflex-release.jks" `
  -alias lifereflex
```

Use this release SHA1 with Android-platform map keys. If testing with `app-debug.apk`, use the debug SHA1 or a separate debug Android key.

## Build Commands

Debug APK:

```powershell
cd "D:\WARE_HOUSE\desktop_file\LSM\软著\生命反射弧\lifereflex(app)"
gradle :app:assembleDebug --no-daemon
```

Release APK readiness check:

```powershell
gradle :app:assembleRelease --no-daemon
```

Install on a connected device:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" install -r "app\build\outputs\apk\debug\app-debug.apk"
```

## Before Expert Demo

- Confirm `/api/health/detail` is healthy on the public domain.
- Confirm Android `LRA_API_BASE` and `LRA_WS_BASE` are public HTTPS/WSS values.
- Install the APK on 3-4 phones and log in with separate users.
- Use the Web command center to initialize the scenario and open the four mobile links.
- Run one full flow: patient SOS, automatic dispatch, CPR/AED/guide actions, handover, evidence package download.
- Keep the mobile browser fallback `/mobile` ready for participants who cannot install the APK.
