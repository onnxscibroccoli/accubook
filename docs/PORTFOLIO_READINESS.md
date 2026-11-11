# Portfolio reviewer readiness — accubook

> **Status:** Reviewable documentation plan, not a production certification. **As of:** 2026-11-11. **Tracking:** [local issue](https://github.com/onnxscibroccoli/accubook/issues/3) · [cross-repository ledger](https://github.com/onnxscibroccoli/broccoli-core/issues/102).  
> Do not interpret AI-assisted source development, successful offline tests or simulations as independently verified industry employment, compliance, or live operations.

## One-minute technical orientation

**Focus:** Offline-first configurable field service software. A Python CSV/JSON local-first workspace with configurable modules, pricebook and change-order foundations; an Android application import lives on a separate draft PR.

**What is demonstrable:** The listed source files and explicitly scoped CI runs can be inspected. A reviewer can evaluate the code, rerun supported unit tests, and challenge the architecture decisions. Any claimed practical capability requires the corresponding test, environment, and source revision; not all systems are integrated or generally available.

## Source and reviewer starting points

| Evidence | Path |
| --- | --- |
| Standalone Python workspace | [Inspect](https://github.com/onnxscibroccoli/accubook/blob/main/core/accubook.py) |
| Core tests | [Inspect](https://github.com/onnxscibroccoli/accubook/blob/main/tests/test_core.py) |
| Android import PR (not main) | [Inspect](https://github.com/onnxscibroccoli/accubook/pull/2) |
| Feature-signal CI | [Inspect](https://github.com/onnxscibroccoli/accubook/blob/main/.github/workflows/feature-signals.yml) |

## Executed CI references (historical, scoped)

| Check | Exact run |
| --- | --- |
| Android debug APK, import PR branch | [Run 42430101238](https://github.com/onnxscibroccoli/accubook/actions/runs/42430101238) |
| Android emulator smoke, import PR branch | [Run 42430101223](https://github.com/onnxscibroccoli/accubook/actions/runs/42430101223) |
| Feature signal scheduled test on main | [Run 42677322785](https://github.com/onnxscibroccoli/accubook/actions/runs/42677322785) |

These run links refer to the specific branch/commit shown on GitHub. They must not be silently attributed to a different current HEAD, production environment, device or approval state.

## Reproduce the relevant local checks

After cloning the repository and reviewing dependencies and safe environment requirements:

```sh
python3 tests/test_core.py && python3 -m unittest discover -s tests -p 'test_feature_signals.py' -v
```

This is a **documented command**, not a claim that this portfolio PR executed it. Some modules require dependencies or privileges, and a missing dependency must be reported rather than converted into a false PASS.

## Ordered actionable changes

1. [ ] Present core Python implementation on main truthfully; don't imply Android UI is already merged.
2. [ ] Review and reconcile Android import draft PR #2 against the current core model and all user-facing field service requirements.
3. [ ] After tested source inclusion, publish independently installable APK with version, checksum and source SHA.
4. [ ] Demonstrate the customer vs contact distinction, estimate/job workflow, and offline data export under a separate feature test.
5. [ ] Keep private annotations, customer data and contacts entirely off public CI/research pathways.

## Maturity and verification boundary

Main does not yet include the Android UI; feature-branch build and emulator smoke are not a merged release or verified physical-device installation.

## Release and artifact strategy

Prepare an Android debug or prerelease GitHub Release **only after** import acceptance, artifact inspection, checksum, emulator/physical device results and explicit known limits.

## Safe continuation after interruption

1. Follow the local issue and the [master execution ledger](https://github.com/onnxscibroccoli/broccoli-core/issues/102); inspect existing PRs before creating new ones.
2. Check `git rev-parse HEAD`, repo default branch, current feature branches and fresh Actions conclusions.
3. For each checklist item, implement the smallest change on a reviewable PR; record exact SHA, test scope, successes, failed/untested checks and outstanding decisions.
4. Keep a previously failing independent-approval requirement or live-device gate unresolved until a legitimately authorized actor/environment supplies evidence.
5. Re-read this document against source after changing implementation. Do **not** mark a checklist item complete merely because it is documented.

**Human-only / outside repository assertions:** employment history, professional tenure, team-management responsibilities, third-party audit and approvals.