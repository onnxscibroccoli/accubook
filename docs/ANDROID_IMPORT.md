# Android application import

The standalone repository now contains the Android application at `android/` alongside
its existing Python workspace foundation and feature-signal research tooling.

Source: `onnxscibroccoli/broccoli-core`, PR #96, commit
`4dfe34b1ba200d3ef0d71c2400ab8a81fca8ecf8`, directory `experiments/accubook/android/`.
This captures the stacked implementation through private annotations and touch-first
jiggle photo reordering, including onboarding, CSV import and inventory ledger work.

All 75 Android files were copied byte-for-byte. `ANDROID_IMPORT.json` records source paths,
destination paths, Git blob IDs and SHA-256 hashes. The two Android Actions workflows were
copied with paths adjusted to `android/` and push triggers set to `main`; PR and manual
triggers are retained. The original Broccoli Core files and PR history remain intact.
The existing standalone Python code, schemas, tests and research pipeline are preserved.
This is a snapshot import, not a transfer of GitHub issues or PR objects.

The Android Java implementation and Python foundation are separate implementations:
no automatic cross-runtime CSV compatibility or synchronization is claimed. Existing
Android documents retain their historical repository-relative paths; when running their
commands here, replace `experiments/accubook/android` with `android`.

## Validation

Run existing standalone tests from the root:

```sh
python3 tests/test_core.py
python3 -m unittest discover -s tests -p 'test_feature_signals.py' -v
```

GitHub Actions runs all imported standalone Java smoke tests, compiles the debug APK,
verifies its APK signature and uploads the APK plus checksum. A separate workflow runs
the imported Android API 35 emulator smoke. Physical Android 15, TalkBack, large fonts,
backup/restore and production release acceptance remain independent of these CI checks.
No production signing key is imported. A fresh runner's debug certificate may differ from
an installed development APK; preserve/export device data before any reinstall.

Future Android work should target this standalone repository. If the historical Broccoli
Core PR stack advances, compare against the pinned source commit before importing again.
