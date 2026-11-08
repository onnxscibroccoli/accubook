# Accubook

Open-source, local-first CRM for trades and sole proprietorships.

Designed so the person on the truck and the person in the office can do their work without friction, admin gates, or subscription lock-in.

## Core Principles

- Simple default that already works, then extend. AccuLube flyer-style invoice + due-date reminder + paid flag is the baseline.
- Field notes populate money. Free-text type-ahead from local pricebook inserts cost and sell price.
- Lookup by anything. One search box across name, phone, address, PO, work order, VIN, notes, color.
- No role walls for the owner. Solo operator sees and edits everything. Crews/permissions only when toggled on.
- Local-first, printable, exportable. PDFs, share intents, unpaid invoice folder. No hosted lock-in.
- Change orders and acknowledgment are first-class. Linked child of the job, not a second quote.
- Feature flags. Turn modules on/off. Core stays lean.
- Editable modules. Owner can reorder fields, add custom fields from the interface.
- Privacy by default. Optional P2P encrypted sync later via key exchange (no central server).

## Architecture

- Workspace is a directory of CSVs + JSON config + media folders.
- Core entities: customers, properties/sites, jobs, job_lines (billing, materials, notes), photos, signatures.
- Optional modules add CSVs or columns (vehicles, measurements, inventory layers, recurring services).
- All operations offline. Export anytime.
- Python core for data layer (Termux/Android friendly). UI can be any client that reads the workspace.
- Development-time GitHub Actions research never uploads local customer data, annotations, contacts, or device telemetry.

## Getting Started

1. Clone or copy the workspace template.
2. Run onboarding questionnaire (checkboxes) to set feature flags in `config.json`.
3. Start using: create customers/jobs, type notes that auto-fill from pricebook, print slips, mark paid.

See `docs/DESIGN.md` for full design from AccuLube, Atlantic Mechanical, Associate Roofing, and trade experience.

## Priorities (current implementation pass)

1. Reorderable collections (fields, photos, lines) with long-press actions.
2. Change-order + signature capture on the job.
3. Local pricebook with type-ahead into invoice lines.
4. Feature-flagged inventory and recurring due dates.

## Feature-Signal Research (GitHub Actions)

This repository includes an **advisory, read-only** feature-discovery pipeline. A weekly/manual GitHub Actions run analyzes explicitly labeled **public** GitHub issues and publishes only aggregate counts; pull requests run synthetic regression tests. No private in-app feedback is transferred. This workflow never automatically writes code, opens issues, merges PRs, or claims that feedback frequency proves utility.

See [the feature-signal engineering specification](docs/FEATURE_SIGNALS.md) for the source schema, reproducible commands, research gates, statistics, and required human audit.

For an immediate local test:

    python3 tests/test_core.py
    python3 -m unittest discover -s tests -p "test_feature_signals.py" -v
    python3 tools/feature_signals.py --input research/synthetic_feedback.jsonl --out /tmp/accubook-research.json

## Android application

The native Android implementation is now in [`android/`](android/README.md), imported
from Broccoli Core PR #96 with private annotations, touch-first photo reordering,
onboarding, inventory and the existing CRM workflows. See the
[import provenance and validation guide](docs/ANDROID_IMPORT.md).

The Android debug APK and emulator workflows build/test this repository directly.
The Python foundation and research tooling remain separate components; shared data
compatibility and production release acceptance are not implied by the import.

## License

MIT. Donations accepted. Ads optional and fully disableable.
