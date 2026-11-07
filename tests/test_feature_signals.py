"""Offline tests for feature research; no network, AI APIs, or external packages."""
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from feature_signals import analyze, classify, experiment_signal, load_jsonl, markdown
from import_public_issues import fetch_public_issues


def public_record(ident, text, cohort="general", source="github_issue"):
    return {
        "id": str(ident), "source": source, "origin": "public",
        "cohort": cohort, "text": text,
        "evidence_url": "https://github.com/example/repo/issues/" + str(ident),
    }


class SignalTests(unittest.TestCase):
    def test_one_pass_intents_and_deduplication(self):
        rows = [
            public_record(1, "Drag to reorder photos should jiggle without another long press", "field"),
            public_record(2, "Drag to reorder photos should jiggle without another long press", "office"),
            public_record(3, "We need a rainbow color picker instead of RGB sliders", "solo", "forum"),
            public_record(4, "Bulk import contacts without creating customers", "office", "app_review"),
            {"id": "fixture", "source": "synthetic", "origin": "synthetic",
             "cohort": "general", "text": "Need job templates and custom fields"},
        ]
        output = analyze(rows)
        by_name = {row["feature"]: row for row in output["features"]}
        self.assertEqual(output["summary"]["duplicates"], 1)
        self.assertEqual(by_name["drag_reorder"]["public_mentions"], 1)
        self.assertEqual(by_name["color_picker"]["public_mentions"], 1)
        self.assertEqual(by_name["job_customization"]["synthetic_mentions"], 1)
        self.assertEqual(by_name["job_customization"]["public_mentions"], 0)
        self.assertFalse(output["automatic_build_authorized"])

    def test_synthetic_cannot_mask_public_evidence(self):
        note = "Bulk import contacts should be a single step"
        rows = [
            {"id": "fake", "source": "synthetic", "origin": "synthetic",
             "cohort": "general", "text": note},
            public_record("real", note, "field"),
        ]
        report = analyze(rows)
        item = next(x for x in report["features"] if x["feature"] == "contact_import")
        self.assertEqual(item["public_mentions"], 1)
        self.assertEqual(item["synthetic_mentions"], 1)

    def test_diversity_gate_not_auto_build(self):
        rows = [
            public_record(i, f"Need bulk import contacts without selecting each section {i}",
                          "field" if i % 2 else "office",
                          "forum" if i % 2 else "github_issue")
            for i in range(1, 7)
        ]
        result = analyze(rows)
        item = next(x for x in result["features"] if x["feature"] == "contact_import")
        self.assertEqual(item["research_status"], "candidate_for_controlled_test")
        self.assertEqual(item["experiment"]["status"], "not_measured")
        self.assertFalse(result["automatic_build_authorized"])

    def test_privacy_does_not_output_quotes_or_user_identifiers(self):
        sensitive = "Drag to reorder images, name test@example.com, mobile 555-777-1234"
        result = analyze([public_record("secret-identifier", sensitive)])
        exported = json.dumps(result) + markdown(result)
        for forbidden in ("test@example.com", "555-777-1234", "secret-identifier", sensitive):
            self.assertNotIn(forbidden, exported)

    def test_experiment_is_independent_of_demand_count(self):
        trial = {"kind": "observed", "preregistered": True, "randomized": True,
                 "independent": True, "control_trials": 1000, "control_success": 400,
                 "treatment_trials": 1000, "treatment_success": 700}
        signal = experiment_signal(trial, tested_hypotheses=4)
        self.assertEqual(signal["status"], "five_sigma_indicator_requires_audit")
        self.assertGreater(signal["z"], 5)
        trial["randomized"] = False
        self.assertEqual(experiment_signal(trial)["status"], "unverified_design")
        trial["randomized"] = True
        trial["control_trials"] = 20
        self.assertEqual(experiment_signal(trial)["status"], "inadequate_counts")

    def test_reject_private_and_malformed_rows(self):
        with self.assertRaises(ValueError):
            analyze([{"id": "1", "source": "device_telemetry", "origin": "private",
                      "cohort": "general", "text": "Drag reorder"}])
        with self.assertRaises(ValueError):
            analyze([public_record(1, "too long " * 600)])
        with self.assertRaises(ValueError):
            analyze([public_record(1, "reorder")], {"made_up_feature": {}})
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "feedback.jsonl"
            path.write_text("x" * 17000 + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                list(load_jsonl([path]))

    def test_importer_filters_issues_and_skips_pull_requests(self):
        issues = [
            {"number": 12, "title": "Color picker",
             "body": "A graphical rainbow color picker is essential.",
             "labels": [{"name": "ux-feedback"}, {"name": "cohort:field"}]},
            {"number": 13, "title": "Not feedback", "pull_request": {"url": "fake"},
             "labels": [{"name": "ux-feedback"}]},
        ]
        class Response(io.BytesIO):
            def __enter__(self):
                return self
            def __exit__(self, *args):
                self.close()
        def fake_opener(request, timeout):
            self.assertEqual(request.full_url.split("?")[0],
                             "https://api.github.com/repos/owner/accubook/issues")
            return Response(json.dumps(issues).encode("utf-8"))
        result = list(fetch_public_issues("owner/accubook", opener=fake_opener))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["cohort"], "field")
        self.assertEqual(result[0]["source"], "github_issue")
        with self.assertRaises(ValueError):
            list(fetch_public_issues("attacker/../repo", opener=fake_opener))


if __name__ == "__main__":
    unittest.main()
