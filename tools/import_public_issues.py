#!/usr/bin/env python3
"""Import *public, explicitly labeled* Accubook GitHub issues into ephemeral JSONL.

No private app feedback, contacts, workspace files, or device data are accessed.
The intermediate JSONL may contain public user-authored text: keep it runner-local.
"""
import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API = "https://api.github.com"
LABEL = "ux-feedback"
COHORTS = {"field", "office", "solo", "team", "general"}


def fetch_public_issues(repository, token="", opener=urlopen):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("invalid GitHub repository identifier")
    for page in range(1, 6):  # fixed upper bound: max 500 records per run
        qs = urlencode({"state": "all", "labels": LABEL, "per_page": 100, "page": page})
        url = f"{API}/repos/{repository}/issues?{qs}"
        headers = {"Accept": "application/vnd.github+json",
                   "X-GitHub-Api-Version": "2022-11-28",
                   "User-Agent": "accubook-feature-research"}
        if token:
            headers["Authorization"] = "Bearer " + token
        with opener(Request(url, headers=headers), timeout=15) as response:
            issues = json.load(response)
        if not isinstance(issues, list):
            raise ValueError("GitHub API did not return an issue list")
        for issue in issues:
            if "pull_request" in issue:
                continue
            labels = [item.get("name", "") for item in issue.get("labels", [])
                      if isinstance(item, dict)]
            cohort = next((label.split(":", 1)[1] for label in labels
                           if label.startswith("cohort:")
                           and label.split(":", 1)[1] in COHORTS), "general")
            # Never log or upload the issue text. This is strictly transient input.
            text = str(issue.get("title") or "") + "\n" + str(issue.get("body") or "")
            yield {
                "id": str(issue["number"]),
                "source": "github_issue",
                "origin": "public",
                "cohort": cohort,
                "evidence_url": f"https://github.com/{repository}/issues/{int(issue['number'])}",
                "text": text[:4096],
            }
        if len(issues) < 100:
            return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    os.umask(0o077)
    count = 0
    with args.out.open("w", encoding="utf-8") as stream:
        for record in fetch_public_issues(args.repo, os.getenv("GITHUB_TOKEN", "")):
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    print(f"Imported {count} explicitly labeled public GitHub issues into ephemeral runner storage.")


if __name__ == "__main__":
    main()
