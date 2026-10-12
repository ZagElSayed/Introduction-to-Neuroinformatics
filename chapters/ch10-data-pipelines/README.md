# Chapter 10 — Neuroinformatics Pipelines and Infrastructure

**Status: runnable student lab.** Build an auditable synthetic EEG-like pipeline with a protected source directory, metadata validation, channel-wise centering, SHA-256 provenance, scientific QC, and a deliberate failure/recovery exercise. Uses only Python's standard library.

## Run from repository root

```bash
python chapters/ch10-data-pipelines/exercise_10_1_reproducible_pipeline.py --work-dir outputs/ch10
python chapters/ch10-data-pipelines/exercise_10_1_reproducible_pipeline.py --work-dir outputs/ch10 --run-only
python -m pytest -q tests/test_chapter10_lab.py
```

Outputs include `raw/synthetic_eeg.csv`, `config/metadata.json`, `config/pipeline.json`, `derivatives/centered_eeg.csv`, and `manifests/provenance.json`.

## Assignment (100 points)

1. **Architecture (15):** Draw the raw → validate → transform → QC → provenance workflow. Identify immutable inputs, derived outputs, and audit artifacts.
2. **Input integrity (15):** Record the source SHA-256 and explain how it distinguishes dataset state from a filename alone.
3. **Metadata and scientific units (20):** Remove `units` from `config/metadata.json`, rerun with `--run-only`, capture the failure and provenance record, restore the field, and recover.
4. **Determinism (20):** Rerun unchanged inputs and compare output SHA-256 values. Explain why matching bytes are evidence of repeatability in this environment, not universal cross-platform bitwise reproducibility.
5. **Quality and operations (15):** Report sample count, centered channel means, runtime, and the QC threshold. Explain the difference between a scientific QC metric and a system metric.
6. **Infrastructure design (15):** Propose an HPC or cloud execution design with a storage tier, scheduler, logs, backup/recovery plan, and least-privilege service identity. Do not claim the small script implements these production controls.

**Deliverables:** output files, one failure/recovery log, a one-page architecture diagram, and a short technical report.

**Graduate extension:** Add dependency-aware caching keyed by input/config hashes, a DAG workflow engine, atomic derivative writes, and a failure-injection test. These are *extensions*, not capabilities already implemented by the baseline exercise.

**Safety and interpretation:** The data are synthetic and EEG-like, not clinical EEG; channel-wise centering is an engineering demonstration rather than a recommended complete EEG preprocessing method. Chapter 9 teaches formal standards; Chapter 11 covers governance.
