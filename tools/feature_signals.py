#!/usr/bin/env python3
"""Deterministic, privacy-preserving feature-signal research (stdlib only).

This is a build-time research tool. It does not collect Accubook device data.
An O(total input characters) bounded-vocabulary classifier is not an LLM,
semantic embedding model, proof of market demand, or causal experiment.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re

MAX_LINE = 16384
MAX_TEXT = 4096
MAX_EVENTS = 5000
SOURCES = {"github_issue", "app_review", "forum", "curated_public", "synthetic"}
COHORTS = {"field", "office", "solo", "team", "general"}
PHRASES = {
    "contact_import": ("import contacts", "contact import", "phone contacts", "address book", "bulk import"),
    "color_picker": ("color picker", "colour picker", "rainbow picker", "rgb slider", "choose colors"),
    "drag_reorder": ("drag reorder", "drag to reorder", "reorder photos", "reorder images", "long press reorder", "jiggle mode"),
    "local_export": ("local export", "export data", "export csv", "export pdf", "data portability", "vendor lock in"),
    "invoice_lookup": ("find invoice", "invoice lookup", "search invoice", "unpaid invoice", "mark paid"),
    "job_customization": ("custom job", "job template", "custom fields", "edit job fields", "workflow template"),
    "offline_use": ("work offline", "offline mode", "no internet", "local first", "no subscription"),
    "photo_management": ("upload photos", "upload pictures", "bulk photos", "job photos", "photo upload"),
    "reminders": ("dumpster reminder", "service reminder", "due date reminder", "calendar sync"),
}
assert len(PHRASES) == len(set(PHRASES))


def normalize(value):
    # A fixed vocabulary and maximum record length bound classification cost.
    return " ".join(re.findall(r"\w+", value.casefold(), flags=re.UNICODE))


def classify(text):
    padded = " " + normalize(text) + " "
    return [key for key, phrases in PHRASES.items()
            if any(" " + phrase + " " in padded for phrase in phrases)]


def load_jsonl(paths):
    for path in paths:
        with open(path, "r", encoding="utf-8") as stream:
            line_number = 0
            while True:
                line = stream.readline(MAX_LINE + 1)
                if not line:
                    break
                line_number += 1
                if len(line) > MAX_LINE or (line and not line.endswith("\n") and
                                              len(line) == MAX_LINE + 1):
                    raise ValueError(f"{path}:{line_number}: record too long")
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{line_number}: invalid JSON") from exc
                if not isinstance(data, dict):
                    raise ValueError(f"{path}:{line_number}: expected JSON object")
                yield data


def validate(record):
    source = record.get("source")
    origin = record.get("origin")
    cohort = record.get("cohort")
    ident = record.get("id")
    text = record.get("text")
    if source not in SOURCES or origin not in {"public", "synthetic"}:
        raise ValueError("source/origin must be approved public or synthetic categories")
    if (source == "synthetic") != (origin == "synthetic"):
        raise ValueError("synthetic data must be explicitly marked and isolated")
    if cohort not in COHORTS:
        raise ValueError("unknown cohort")
    if not isinstance(ident, str) or not re.fullmatch(r"[\w:./-]{1,128}", ident):
        raise ValueError("invalid source id")
    if not isinstance(text, str) or len(text) > MAX_TEXT:
        raise ValueError("invalid or overlong feedback")
    if origin == "public" and not isinstance(record.get("evidence_url"), str):
        raise ValueError("public evidence requires a source URL for manual audit")
    return source, origin, cohort, ident, text


def experiment_signal(trial, tested_hypotheses=1):
    """One-sided two-proportion z indicator, NOT a causal or universal-utility proof.

    Requires separately collected, pre-registered, randomized observed outcomes.
    Input declarations still require external/human verification.
    """
    if trial is None:
        return {"status": "not_measured"}
    if not isinstance(trial, dict):
        raise ValueError("experiment must be an object")
    if trial.get("kind") != "observed" or not all(
        trial.get(k) is True for k in ("preregistered", "randomized", "independent")
    ):
        return {"status": "unverified_design"}
    try:
        n0, n1 = trial["control_trials"], trial["treatment_trials"]
        x0, x1 = trial["control_success"], trial["treatment_success"]
    except KeyError as exc:
        raise ValueError("missing experiment count") from exc
    if any(type(v) is not int for v in (n0, n1, x0, x1)):
        raise ValueError("experiment counts must be integers")
    if n0 < 100 or n1 < 100 or not (0 <= x0 <= n0 and 0 <= x1 <= n1):
        return {"status": "inadequate_counts"}
    pooled = (x0 + x1) / (n0 + n1)
    if min(pooled * n0, pooled * n1, (1 - pooled) * n0, (1 - pooled) * n1) < 5:
        return {"status": "inadequate_expected_cells"}
    standard_error = math.sqrt(pooled * (1 - pooled) * (1 / n0 + 1 / n1))
    z = (x1 / n1 - x0 / n0) / standard_error
    p_one_sided = 0.5 * math.erfc(z / math.sqrt(2))
    adjusted = min(1.0, p_one_sided * max(1, tested_hypotheses))
    return {
        "status": "five_sigma_indicator_requires_audit"
                  if z >= 5 and adjusted < 0.5 * math.erfc(5 / math.sqrt(2))
                  else "no_five_sigma_indicator",
        "z": round(z, 5),
        "adjusted_p_one_sided": adjusted,
        "control_rate": round(x0 / n0, 5),
        "treatment_rate": round(x1 / n1, 5),
    }


def analyze(records, experiments=None):
    experiments = experiments or {}
    if not isinstance(experiments, dict) or set(experiments) - set(PHRASES):
        raise ValueError("experiment file has unknown feature keys")
    counters = {feature: {"public": 0, "synthetic": 0, "sources": set(),
                          "cohorts": set()} for feature in PHRASES}
    seen_ids, seen_text = set(), set()
    summary = Counter()
    for record in records:
        summary["rows"] += 1
        if summary["rows"] > MAX_EVENTS:
            raise ValueError("too many feedback rows")
        source, origin, cohort, ident, text = validate(record)
        fingerprint = hashlib.sha256(normalize(text).encode("utf-8")).digest()
        source_id = (source, ident)
        # Duplicate public/reposted content must not manufacture diversity.
        if source_id in seen_ids or fingerprint in seen_text:
            summary["duplicates"] += 1
            continue
        seen_ids.add(source_id)
        seen_text.add(fingerprint)
        summary["unique_rows"] += 1
        features = classify(text)
        if not features:
            summary["unclassified"] += 1
            continue
        for feature in features:
            item = counters[feature]
            item[origin] += 1
            if origin == "public":
                item["sources"].add(source)
                item["cohorts"].add(cohort)
    output = []
    for feature in sorted(PHRASES):
        item = counters[feature]
        # This selects candidates for experiments, NEVER an automatic build.
        eligible = (item["public"] >= 5 and len(item["sources"]) >= 2
                    and len(item["cohorts"]) >= 2)
        output.append({
            "feature": feature,
            "public_mentions": item["public"],
            "synthetic_mentions": item["synthetic"],
            "source_types": len(item["sources"]),
            "cohorts": len(item["cohorts"]),
            "research_status": "candidate_for_controlled_test" if eligible
                               else "insufficient_diverse_evidence",
            "experiment": experiment_signal(experiments.get(feature), max(1, len(experiments))),
        })
    return {
        "schema_version": 1,
        "provenance": "public_opt_in_research_only; no in_app_collection",
        "privacy": "aggregates_only; no raw text, author IDs, URLs, or device data",
        "summary": dict(sorted(summary.items())),
        "features": output,
        "automatic_build_authorized": False,
    }


def markdown(report):
    lines = [
        "# Accubook feature-signal research",
        "",
        "Research indicators only. **Not proof of universal utility or permission to build.**",
        "No private in-app annotations are ingested. Raw issue text is never exported.",
        "",
        "| Feature | Public mentions | Sources | Cohorts | Research | Experiment |",
        "| --- | ---: | ---: | ---: | --- | --- |",
    ]
    for f in report["features"]:
        lines.append("| {} | {} | {} | {} | {} | {} |".format(
            f["feature"], f["public_mentions"], f["source_types"], f["cohorts"],
            f["research_status"], f["experiment"]["status"]))
    lines.append("")
    lines.append("Synthetic examples do not contribute to promotion. Human audit required.")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", action="append", required=True, type=Path)
    parser.add_argument("--experiments", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--markdown-out", type=Path)
    args = parser.parse_args()
    trials = json.loads(args.experiments.read_text(encoding="utf-8")) if args.experiments else None
    report = analyze(load_jsonl(args.input), trials)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_out:
        args.markdown_out.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_out.write_text(markdown(report), encoding="utf-8")
    print("Research complete: {} unique public/synthetic records; {} duplicates".format(
        report["summary"].get("unique_rows", 0), report["summary"].get("duplicates", 0)))


if __name__ == "__main__":
    main()
