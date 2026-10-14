# Chapter 10 — Pipelines, Infrastructure, and Workflows

A miniature, local pipeline for **synthetic EEG-like values**, using Python 3.10+ and the standard library. Channel-wise centering demonstrates a transformation; it is not rereferencing, artifact removal, biomarker extraction, or clinical validation. No cloud account, GPU, container runtime, or human recording is needed.

The revised lab adds strict finite-value/schema checks, a recorded source baseline, independent execution histories, input snapshots, serialized-candidate QC, and local publication after checks. This revision has been reviewed as source; **the code and tests have not been executed for this revision**. Run locally and report any failures.

## Run locally

From the repository root:

```bash
cd chapters/ch10-data-pipelines
python exercise_10_1_reproducible_pipeline.py --work-dir ../../outputs/ch10
python exercise_10_1_reproducible_pipeline.py --work-dir ../../outputs/ch10 --run-only
```

Use a **fresh work directory** when upgrading from version 1.0. Initial setup refuses an unrelated nonempty directory. Once a baseline exists, setup leaves source and configuration alone; it does not silently replace missing or edited inputs. `--run-only` attempts processing without initialization. A failed attempt returns command exit status 1.

From the repository root, optional local tests require pytest:

```bash
python -m pip install pytest
python -m pytest -q tests/test_chapter10_lab.py
```

No GitHub build or execution is required. Do not interpret the presence of a test file as a claim that checks have passed.

## Follow the outputs

| Path inside the work directory | Purpose |
|---|---|
| `raw/synthetic_eeg.csv` | Forty synthetic sample rows, two channels, microvolt values |
| `config/metadata.json` | Sampling rate, channels, units, synthetic-source label |
| `config/pipeline.json` | Supported pipeline version and numerical QC tolerance |
| `manifests/source_baseline.json` | Locally recorded source digest for subsequent comparisons |
| `runs/<run-id>/inputs/` | Exact bytes read for the source, metadata, configuration, and baseline |
| `runs/<run-id>/derivatives/centered_eeg.csv` | Published only when this attempt succeeds |
| `runs/<run-id>/provenance.json` | Run identity, digests, environment, status, stages, QC, and error |
| `runs/<run-id>/events.jsonl` | One JSON stage event per line |
| `manifests/provenance.json` | Convenience copy describing the latest attempt, including failures |

The workflow is **snapshot → validation → transform → saved-candidate QC → publication**. Follow `output_path` and `manifest_path` relative to the work directory. A failed rerun keeps previous runs intact and publishes no derivative for the failed attempt. Candidate files are temporary. If the process is killed or storage becomes unwritable, evidence may be incomplete: only use artifacts with a successful per-run record and verified digest. Inspect orphaned run directories before trusting a recovered workspace.

Source digest comparison detects a change relative to the local baseline. It does not authenticate the baseline, prove the values are meaningful, prevent editing, or implement access control. Metadata and configuration are intentionally editable and are recorded for each run. The script hashes its source, records Python/platform context, and uses the exact in-memory input snapshots for processing. Concurrent editing during snapshot collection is outside this single-process teaching model; production systems need immutable dataset versions and consistent configuration snapshots.

## Assignment — 100 points

1. **Architecture and dependencies (15).** Draw the five stages; identify the input, configuration, candidate, released derivative, and records. Explain why a DAG needs a dependency on QC before release, even if feature computation can run in parallel with QC.
2. **Integrity and provenance (15).** Inspect source/baseline comparison and all digests. Follow snapshots and output paths. Explain why a digest is insufficient to establish correct participant identity or scientific validity.
3. **Failure and recovery (20).** Save metadata bytes, remove `units`, rerun with `--run-only`, capture command status and failed stage, restore the exact bytes, and rerun. Preserve baseline, failure, and recovery records. Demonstrate that the earlier successful derivative remains available.
4. **Adversarial inputs (15).** Use isolated work directories for a non-finite sampling rate, non-finite amplitude, wrong channel order, and duplicate sample index. Record the stage that fails. For amplitude/index experiments, first observe baseline integrity failure; then deliberately update **only the synthetic local baseline** to the edited source digest to test semantic checks independently. Explain why trusted-baseline modification is a governed operation in real systems. Valid JSON uses `250`, not `NaN` or `Infinity`; intentionally invalid values are failure examples.
5. **Repeatability and QC (20).** Rerun unchanged inputs; compare derivative digests and run identities. Report sample count, saved-output channel means, numerical tolerance, and elapsed runtime. Verify the output bytes against the reported digest. Explain why matching derivatives need not mean matching manifests, and why a centered mean is a narrow arithmetic check rather than physiological QC.
6. **Operating the platform (15).** Propose HPC/cloud resource requests, bounded retry versus quarantine decisions, ownership of alerts, storage/catalog separation, and a recovery drill with RPO/RTO. Calculate ideal transfer time for 500 GB at 0.6 Gb/s, speedup for an 80%-parallel job on eight workers, and capacity for 12 TB primary plus one backup with 20% free headroom.

## Submit to your student GitHub repository

Submit your implementation commit and a link to a folder containing:

- `report.md`: assumptions, calculations, digest comparisons, and limitations;
- an architecture diagram with stage dependencies and storage locations;
- baseline, failed, and recovered per-run records, logs, and input snapshots;
- at least one successful derivative and the failed command's exit status;
- your local verification command, Python version, and actual test outcome.

Preserve relative directory structure so artifact links remain meaningful. Use small synthetic evidence only. Exclude environments, caches, secrets, clinical files, and large recordings. The report should distinguish **what you observed locally** from capabilities merely proposed for deployment.

## Interpretation and extensions

The centering formula is `y[i,j] = x[i,j] - mean(x[:,j])`. The default threshold is a numerical tolerance of `1e-9 uV`, not a patient or signal-quality cutoff. QC reads the serialized candidate rather than trusting pre-write arrays. Output bytes are compared across runs; timestamps, UUIDs, and runtimes are expected to differ.

The baseline is a sequential demonstration, not a workflow engine: no scheduling, caching, bounded automatic retries, checkpoint resume, production permissions, real monitoring service, backup service, or container isolation is implemented. Per-file replacement is not a multi-file transaction or a power-loss durability guarantee. Runtime is elapsed time for the recorded processing attempt, not queue time or full CLI overhead.

**Graduate extension:** encode the stages in Snakemake/Nextflow; document the real engine's cache behavior; add validated reuse, an interruption experiment, and a bounded retry for a transient operational fault. Never modify scientific parameters automatically just to make QC pass.

See [RESOURCES.md](RESOURCES.md) for primary documentation and study prompts.
