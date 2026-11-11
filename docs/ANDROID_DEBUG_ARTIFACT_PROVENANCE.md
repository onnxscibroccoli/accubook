# Android debug artifact provenance

This implementation packages and verifies the standalone Accubook Android debug APK from the `android/` application source, which currently lives on the [Android import PR #2](https://github.com/onnxscibroccoli/accubook/pull/2). It does **not** publish a production app.

## Build/verification contract

The [Accubook Android Debug APK](../.github/workflows/accubook-debug-apk.yml) GitHub Actions workflow runs the Java CSV/backup/ledger smoke tests, an offline manifest-generator regression suite, Gradle `assembleDebug`, `apksigner verify`, and a SHA-256 checksum. The Python verifier checks ZIP integrity, presence of `AndroidManifest.xml` and DEX bytecode, the independent checksum, Gradle package ID, full source SHA and exact Actions run URL.

Only after these checks pass does the workflow upload one artifact named `accubook-debug-universal` containing:

- `android/app/build/outputs/apk/debug/app-debug.apk`
- `android/app/build/outputs/apk/debug/SHA256SUMS.txt`
- `android/app/build/outputs/apk/debug/DEBUG_BUILD_MANIFEST.json`

The manifest status is always `DEBUG_APK_TEST_ARTIFACT_NOT_RELEASE`. It contains a content digest, source checkout SHA, Actions URL, package identifier, version, and explicit unverified activities.

On PR events, `github.sha` identifies the tested PR merge checkout. It does not necessarily equal the feature branch's head SHA; inspect the run's event and head SHA to understand provenance.

## Offline unit tests

From the `android/` directory:

```sh
python3 -m unittest discover -s scripts/tests -p 'test_verify_debug_artifact.py' -v
```

These tests deliberately exercise checksum mismatch, invalid source SHA, unexpected application ID, non-APK archive, and mismatched checksum filename. No Android SDK or network access is required to test the manifest logic.

## Installing a verified test build

1. Open the exact successful Actions run for the source/merge commit under test.
2. Download `accubook-debug-universal` from that run's **Artifacts** section.
3. Independently verify the extracted APK SHA-256 against `SHA256SUMS.txt` and `DEBUG_BUILD_MANIFEST.json`.
4. Inspect Android permissions and install on a device you control, acknowledging the debug/development label.
5. Record Android version, tested workflow, install result, and a basic customer/job workflow smoke test before declaring `DEVICE_TESTED`.

A green emulator smoke-test run is not evidence of successful installation on a physical handset.

## Publication boundary

The artifact expires according to Actions retention settings. It is not a GitHub Release or stable direct APK URL. A Release requires a separately reviewed publication gate, durable artifact link, signature/provenance controls, user-facing version notes, current tests, and approval of what is actually shipped.

**No cloud telemetry, contacts, customer data, or private in-app annotations are transmitted by this workflow.**

## Related issues

- [#5 — Debug artifact provenance](https://github.com/onnxscibroccoli/accubook/issues/5)
- [#3 — Portfolio readiness](https://github.com/onnxscibroccoli/accubook/issues/3)
- [#2 — Android import PR](https://github.com/onnxscibroccoli/accubook/pull/2)
- [Master portfolio program](https://github.com/onnxscibroccoli/broccoli-core/issues/102)

### Current verification status

The source and workflow modifications are reviewable, but no successful Actions run for this exact change should be claimed until the stacked PR's CI executes.
