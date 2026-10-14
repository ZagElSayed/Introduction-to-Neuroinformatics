# NeuroBridge Phase II — Student Runbook

Complete this for the supplied synthetic lab. Mark proposed production capabilities as **design only**. Do not put clinical data, secrets, passwords, or access tokens here.

## Scope and responsibility

| Item | Your entry |
|---|---|
| Scientific/teaching purpose | |
| Authorized operator / scientific reviewer | |
| Infrastructure/recovery owner | |
| Code commit and Python version | |
| Work directory / audit directory | |
| Source baseline and configuration state | |
| Input and output units | |
| Known limitations | |

## Start and inspect a run

From the repository root, move into `chapters/ch10-data-pipelines`. Use an empty/new work directory for initialization. Reuse an existing workspace with `--run-only`; do not expect edited inputs to be silently repaired.

```bash
python exercise_10_1_reproducible_pipeline.py --work-dir ../../outputs/ch10
python exercise_10_1_reproducible_pipeline.py --work-dir ../../outputs/ch10 --run-only
```

Record the actual run ID, command exit status, and per-run `provenance.json` path. Follow `output_path` only for a successful record and verify the reported digest. Locate `events.jsonl` and inspect which stages completed. The latest-run summary is a convenience copy, not the full history.

## Failure response

| Finding | Actual local response / evidence | Proposed owner |
|---|---|---|
| Required units missing | Retain failure; restore the saved metadata; run again | |
| Source digest mismatch | Identify the intentional/accidental source change; do not silently rebaseline | |
| Non-finite samples or duplicate index | Retain invalid input evidence; correct only in a traceable synthetic experiment | |
| Candidate fails centering QC | Retain failure; investigate configuration and numeric behavior | |
| Old run has corrupt derivative | Audit must identify an integrity problem; retain original evidence | |
| Missing/orphaned manifest | Mark incomplete; investigate before accepting outputs | |
| Output directory already contains results | Use a new directory; preserve prior audit evidence | |

Distinguish an auditable failed attempt from an evidence failure: the former may be expected in this assignment; the latter makes the operability audit fail.

## Catalog and operational review

```bash
python exercise_10_2_operability_audit.py \
  --work-dir ../../outputs/ch10 \
  --output-dir ../../outputs/ch10-audit
```

Record the summary observation time and denominator. Reconcile all observed run directories with declared successes, declared failures, incomplete/invalid evidence, and numerically eligible outputs. Inspect the `runs` and `artifacts` tables and the selection query. This is a local numerical eligibility check, not production authorization or clinical acceptance.

## Recovery evidence

Inspect `backup_package/`, `restored_workspace/`, and `recovery_verification.json`. Record the selected reference run, restored run, both derivative digests, and whether they match. Confirm original history was not altered. If the drill failed or was interrupted, describe its partial evidence rather than reporting success.

| Verification | Observed evidence / result |
|---|---|
| Reference source/configuration snapshots recovered | |
| New reference execution completed | |
| Saved-output numerical QC passed | |
| Reference and restored derivative digests match | |
| Original run history preserved | |
| Remaining gaps or unresolved findings | |

## Production design handoff

Specify the storage/catalog locations, access boundary, workflow and software versions, resource requests, alert owners, and escalation rules. Describe how an independent backup failure domain would differ from this same-file-system demonstration. State hypothetical RPO/RTO targets with rationale, identify the service scope and verification needed, and explain how an outage drill would measure the relevant intervals.

The local drill's elapsed duration is **not** an achieved RTO, and its copies do not establish independent backup or RPO performance. Clinical validation, cloud/HPC deployment, live resource telemetry, and real permissions are outside the baseline code.

## Verification record

Record only commands you actually ran and the outcome you observed:

```bash
python -m pytest -q tests/test_chapter10_lab.py tests/test_chapter10_operability.py
```

Run that test command from the repository root. Mark unexecuted checks **not run**. Link your implementation commit, report, diagram, and small synthetic evidence folder.
