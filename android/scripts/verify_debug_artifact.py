#!/usr/bin/env python3
"""Validate Accubook debug APK integrity and emit a build-bound, non-release manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
from zipfile import BadZipFile, ZipFile

SHA256 = re.compile(r"^[0-9a-f]{64}$", re.I)
COMMIT_SHA = re.compile(r"^[0-9a-f]{40}$", re.I)


def gradle_property(text: str, key: str) -> str:
    match = re.search(r"^\s*" + re.escape(key) + r"\s+['\"]([^'\"]+)['\"]", text, re.M)
    if not match:
        raise ValueError(f"missing Gradle property: {key}")
    return match.group(1)


def verify(apk: Path, checksum_file: Path, gradle: Path, source_sha: str,
           run_url: str) -> dict:
    if not COMMIT_SHA.fullmatch(source_sha):
        raise ValueError("source SHA must be a complete commit SHA")
    if not re.fullmatch(r"https://github\.com/[\w.-]+/[\w.-]+/actions/runs/\d+", run_url):
        raise ValueError("workflow URL must be an exact Actions run")
    if apk.name != "app-debug.apk" or not apk.is_file() or apk.stat().st_size == 0:
        raise ValueError("debug APK missing or unexpected filename")
    with ZipFile(apk, "r") as package:
        names = set(package.namelist())
        if "AndroidManifest.xml" not in names or not any(n.startswith("classes") and n.endswith(".dex") for n in names):
            raise ValueError("not an installable-looking Android APK archive")
        bad_member = package.testzip()
        if bad_member is not None:
            raise ValueError(f"APK archive CRC mismatch: {bad_member}")
    with apk.open("rb") as apk_stream:
        digest = hashlib.file_digest(apk_stream, "sha256").hexdigest()
    lines = checksum_file.read_text(encoding="utf-8").splitlines()
    if len(lines) != 1:
        raise ValueError("checksum file must contain exactly one entry")
    parts = lines[0].split(maxsplit=1)
    if len(parts) != 2 or not SHA256.fullmatch(parts[0]) or Path(parts[1].lstrip("*")).name != apk.name:
        raise ValueError("malformed or unrelated checksum entry")
    if digest.lower() != parts[0].lower():
        raise ValueError("APK SHA-256 mismatch")
    text = gradle.read_text(encoding="utf-8")
    package_name = gradle_property(text, "applicationId")
    version_name = gradle_property(text, "versionName")
    if package_name != "com.accubook.crm":
        raise ValueError("unexpected Android application ID")
    return {
        "schema_version": 1,
        "status": "DEBUG_APK_TEST_ARTIFACT_NOT_RELEASE",
        "package": package_name,
        "version_name": version_name,
        "file": apk.name,
        "bytes": apk.stat().st_size,
        "sha256": digest,
        "tested_checkout_sha": source_sha,
        "workflow_run": run_url,
        "checks_required_in_workflow": ["Java CSV unit/smoke tests", "Gradle assembleDebug", "apksigner verify"],
        "not_verified": ["physical device installation", "production signing", "publication release", "user data or private annotations"],
    }


def main() -> int:
    a = argparse.ArgumentParser(description=__doc__)
    a.add_argument("--apk", type=Path, required=True)
    a.add_argument("--checksum-file", type=Path, required=True)
    a.add_argument("--gradle", type=Path, default=Path("app/build.gradle"))
    a.add_argument("--source-sha", required=True)
    a.add_argument("--run-url", required=True)
    a.add_argument("--out", type=Path, required=True)
    args = a.parse_args()
    manifest = verify(args.apk, args.checksum_file, args.gradle,
                      args.source_sha, args.run_url)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Verified debug APK checksum and archive: {manifest['sha256']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, BadZipFile) as exc:
        print(f"DEBUG ARTIFACT FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
