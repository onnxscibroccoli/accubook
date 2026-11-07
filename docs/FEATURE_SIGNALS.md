# Feature-signal research and GitHub Actions

## Current state

**CI verified:** The Python analyzer uses only the standard library, and the first pull-request Actions run completed successfully (run 42427568724 at commit e5a3f1b; later commits must pass their own checks). **Termux/device validation:** Not run. **Production-market validation:** Not established. This is a research pipeline, not a product analytics SDK or an app feature.

Accubook operates completely offline at runtime. GitHub Actions is an **optional development-time control plane**; GitHub service interruptions do not affect device data or app functionality. No local Accubook annotation, contact, customer, job, photo, signature, or workspace file is transmitted to GitHub.

## Why it exists

Borrow the useful engineering discipline of high-throughput research pipelines: separate ingestion, cheap deterministic filtering, deeper investigation, experimental verification, and controlled release. This is an analogy; the pipeline does **not** reproduce CERN detectors, guarantee linear-time embeddings, or prove user utility.

### Stages and controls

| Stage | Mechanism now | Evidence produced | Limitation |
| --- | --- | --- | --- |
| Input | Explicitly labeled public GitHub issues; CLI accepts deliberately supplied public/fictional JSONL | Ephemeral input only | No app-store/forum scraping or private in-app export |
| Low-cost trigger | Fixed feature vocabulary, bounded text, normalized-content and source-ID deduplication | Aggregate feature counts | A rule-based classifier, not semantic clustering; can miss paraphrases |
| Reconstruction | Feature taxonomy, aggregate source-type and cohort diversity | JSON and Markdown report | No latent-space model or verified demographic representativeness |
| Hypothesis test | Optional pre-registered two-proportion z indicator on separately recorded outcomes | Z value, adjusted one-sided P value | Requires audited design and real trials; does not prove causality from observational feedback |
| Controlled experiment | **Planned:** instrumented representative task benchmarks + accessible device usability checks | None yet | Synthetic workflows cannot establish real-world retention |
| Build | **Not authorized by this workflow** | Human/owner-directed PRs | Research data cannot approve code, security exceptions, or releases |

### Complexity

Each row is processed once. The taxonomy is a **fixed-size** list; text is limited to 4,096 characters, lines to 16,384 characters, and runs to 5,000 rows. This makes the current processor O(total accepted text characters) time with O(distinct record hashes) memory. This is not a claim that arbitrary vector clustering or full-text embeddings are O(N).

### Evidence thresholds

- A **research candidate** requires at least five unique *public* observations, at least two source types, and two declared cohorts. These are operational heuristics, not confidence intervals. One commenter can still bias several records; reviewer must inspect provenance.
- Synthetic examples are counted **separately** and NEVER raise priority.
- The optional **five-sigma indicator** is a one-sided two-proportion z test, with Bonferroni adjustment over the provided, pre-specified hypotheses. A declared observed, pre-registered, randomized, independent comparison and minimum of 100 trials per arm are required; expected contingency-cell counts must be adequate. Passing this numerical check requires **external design/data audit** and does not prove permanent universal demand.
- An unmet threshold is a **request for better evidence**, not a reason to ignore accessibility defects, safety, privacy, owner-reported pain, or demonstrated usability regressions. Your reported photo-reordering and contact-import friction remain engineering requirements without a five-sigma claim.
- No action opens a PR, edits an issue, runs an LLM, contacts app stores, or merges anything. Gate output is **advisory only**.

## Run locally

From the repository root:

    python3 tests/test_core.py
    python3 -m unittest discover -s tests -p "test_feature_signals.py" -v
    python3 tools/feature_signals.py --input research/synthetic_feedback.jsonl --out /tmp/accubook-research.json --markdown-out /tmp/accubook-research.md

The sample file is entirely fabricated and exists only to validate the pipeline. It is not real market evidence. Run these same commands in Termux; Python 3.8+ and the standard library suffice.

To analyze a **deliberately reviewed public** dataset, create a JSONL file outside the app workspace, with one object per line:

    {"id":"issue-10","source":"github_issue","origin":"public","cohort":"field","text":"Drag to reorder photos should work after selecting reorder","evidence_url":"https://github.com/owner/repo/issues/10"}

For other public evidence, approved source categories are `app_review`, `forum`, and `curated_public`. Include the public evidence URL in each record. Respect each source's terms, licenses, privacy, consent, and copyright; do not mechanically harvest review sites. Do not include personal information or private support tickets. The example URL above is illustrative, not a claim of a real issue.

For an experiment, provide an independently audited JSON mapping feature keys to trial outcomes (never reuse anecdotal mention counts as experiment trials):

    {
      "drag_reorder": {
        "kind": "observed",
        "preregistered": true,
        "randomized": true,
        "independent": true,
        "control_trials": 1000,
        "control_success": 400,
        "treatment_trials": 1000,
        "treatment_success": 700
      }
    }

The numbers above are **fictional for illustrating the schema**. To include real, authorized measurements:

    python3 tools/feature_signals.py --input /path/to/approved-public.jsonl --experiments /path/to/audited-trials.json --out /tmp/report.json

A `five_sigma_indicator_requires_audit` result is **not** an authorization for an autonomous build.

## GitHub Actions

Workflow: `.github/workflows/feature-signals.yml`.

- On pull requests that modify pipeline files, run tests and a **synthetic-only** smoke report.
- On the weekly Monday 08:17 UTC schedule or manual **Run workflow**, query only public issues in **this repository** carrying the `ux-feedback` label. An optional `cohort:field`, `cohort:office`, `cohort:solo`, or `cohort:team` label sets the declared role; default is `general`.
- The raw issue title/body live only in an ephemeral runner file under `$RUNNER_TEMP`, never in repository commits, printed logs, the job summary, or uploaded artifacts.
- Only aggregate JSON/Markdown files are preserved as 7-day artifacts. The job has `contents: read` and `issues: read`, no write privileges, secrets for remote models, or publication rights.
- Trigger a new manual workflow run after introducing explicitly labeled public research; scheduled Actions can be delayed or disabled by repository settings. No public issues were present during initial implementation, so **zero real observations is expected**.
- GitHub-hosted runners are not offline; **only the shipped application remains offline**. No expense-generating API or cloud infrastructure is required for this pipeline beyond GitHub's ordinary Actions quotas.

## Next engineering increments

1. Attach a privacy-safe **separate** connector for independently sourced public reviews, with permission checks, rate limits, provenance review, and data quality tests. Do not pipe private app annotations into Actions.
2. Define accessible task benchmarks for photo reordering, contact import, invoice search, job-field editing, and color selection. Capture step count, completion rate, task duration, and failure classes on real supported devices with informed consent and local-only raw recording.
3. Add cohort-aware analysis and independent pre-registered experiments; address correlated observations, selection bias, nonresponse bias, multiple comparisons, and practical effect sizes.
4. Let the engineering governor consume **reviewed issue/PR specifications** only. Block automated merge on security, data migration, UI accessibility regression, or unreviewed assumptions. Human governance remains independent of mechanical CI.
5. When the actual Android UI repository is connected, integrate its existing automated accessibility/UI tests; this Python repository currently contains a core workspace, not the Android UI implementation.

**Trust boundary:** User-created feedback inside Accubook stays exclusively local unless the user separately chooses to publish a sanitized issue. Public external research is opt-in and does not imply application telemetry. Reports must not claim product-market fit without real, independent user evidence.
