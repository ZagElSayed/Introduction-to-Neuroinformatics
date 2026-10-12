# Chapter 8 — Experimental Design and Paradigms

**Status: runnable companion laboratory.** The baseline exercise uses reproducible **synthetic** Go/No-Go event logs, with 48 counterbalanced-in-count trials, event IDs, response correctness, reaction times, a deliberate +100-ms software timestamp error, and a reference-stream validator. No participants, clinical records, PsychoPy installation, or hardware timing claims are required.

## Run the lab

From the public repository root:

```bash
python chapters/ch08-experimental-design/exercise_8_1_protocol_qc.py --output-dir outputs/ch08
python -m pytest -q tests/test_chapter8_lab.py
```

Outputs: `events.tsv`, `events_offset_100ms.tsv`, `task_metadata.json`, and `qc_report.json`.

## Student assignment (100 points)

1. **Protocol and hypothesis (15):** State a Go/No-Go hypothesis, independent variable, dependent measure, and two confounds. Explain why simulated task accuracy is not neural evidence.
2. **Events and metadata (20):** Inspect `events.tsv` and `task_metadata.json`. Identify event codes, units, coded participant/session identifiers, and software version. Explain why display refresh is unknown in a synthetic task.
3. **Timing validation (20):** Compare the original and injected-offset event files against the reference timestamps. Report detected mismatch counts and the +100-ms injected error. Distinguish a software event timestamp from measured physical stimulus onset.
4. **Quality control (20):** Inspect `qc_report.json`; explain the duplicate-ID, missing-trial, reaction-time, and accuracy checks. Deliberately introduce one duplicate ID and one 0.05-s response latency in a copy and verify the validator flags them.
5. **Reproducibility (15):** Rerun with the same seed, compare exports, then change the seed and document what changes. Record commands and Python version.
6. **Ethics and scientific limits (10):** Explain why coded identifiers are not equivalent to anonymization, and why a synthetic task cannot establish experimental validity in humans.

**Submission:** Four generated files, a 1–2-page report, a short modified-data QC demonstration, and a brief protocol diagram. Do not upload identifiable human data.

## Optional real experiment extension

Implement the same event schema in PsychoPy or PsychoJS, with consent and appropriate supervision. Measure physical visual onset with a photodiode where timing validity matters. Add hardware-based reference timestamps, device configuration, and an auditable protocol-deviation log. **Do not** assume the synthetic timing validation demonstrates hardware accuracy.

## Relationship to textbook

This laboratory implements Chapter 8's experimental protocol, timing, event schema, quality assurance, and reproducibility learning objectives. Chapter 9 will introduce formal neurodata standardization; this chapter's TSV is **BIDS-inspired**, not a claim of BIDS compliance.
