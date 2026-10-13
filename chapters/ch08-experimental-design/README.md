# Chapter 8 — Experimental Design and Paradigms

**Status: runnable companion laboratory.** The baseline exercise uses reproducible **synthetic** Go/No-Go event logs, with 48 trials with balanced condition counts and randomized trial order, event IDs, response correctness, reaction times, a deliberate +100-ms software timestamp error, and a reference-stream validator. No participants, clinical records, PsychoPy installation, or hardware timing claims are required.

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
4. **Quality control (20):** Inspect `qc_report.json`; explain the duplicate-ID, missing-trial, reaction-time, event-code, numeric/schema, response-consistency, and recomputed accuracy checks. Deliberately introduce one duplicate ID and one 0.05-s response latency in a copy and verify the validator flags them.
5. **Reproducibility (15):** Rerun with the same seed, compare exports, then change the seed and document what changes. Record commands and Python version.
6. **Ethics and scientific limits (10):** Explain why coded identifiers are not equivalent to anonymization, and why a synthetic task cannot establish experimental validity in humans.

**Submission in your student GitHub repository:** Commit your four generated files, a 1–2-page report, a runnable modified-data QC demonstration, and a protocol diagram under `chapter08/`. Include a `README.md` with commands, Python version, task definitions, seed, and interpretation limits. Keep original exports separate from corrupted copies. Submit the repository URL and commit SHA; verify the result from a fresh checkout. Do not upload identifiable human data.

## Optional real experiment extension

Implement the same event schema in PsychoPy or PsychoJS, with consent and appropriate supervision. Measure physical visual onset with a photodiode where timing validity matters. Add hardware-based reference timestamps, device configuration, and an auditable protocol-deviation log. **Do not** assume the synthetic timing validation demonstrates hardware accuracy.

## Relationship to textbook

This laboratory implements Chapter 8's experimental protocol, timing, event schema, quality assurance, and reproducibility learning objectives. Chapter 9 will introduce formal neurodata standardization; this chapter's TSV is **BIDS-inspired**, not a claim of BIDS compliance.

## Additional design and validation tasks

- **Experimental units:** explain why 48 simulated trials are not 48 independent participants. Record participant/session/trial relationships in your protocol.
- **Validator challenge:** inject an unknown event code, an inconsistent `correct` value, a NaN onset, a response without RT, and an unexpected trial ID. Demonstrate flags without overwriting original data.
- **BIDS-inspired export:** create a separate `events_bids_inspired.tsv` with `onset`, `duration`, and `trial_type`; declare the time origin and a synthetic stimulus duration in the report. Identify further requirements before claiming BIDS compliance. This is an extension of the events/metadata task, not a formal BIDS validator.
- **Read the thresholds:** the 50-ms discrepancy threshold and 0.15–1.5-s RT range are teaching parameters. Explain why these do not certify EEG stimulus timing or define universal physiological limits.
- **Go/No-Go limits:** equal Go/No-Go counts demonstrate event-log handling. They do not necessarily create the response prepotency of a conventional inhibition experiment. A human protocol must justify its Go probability, instructions, and behavioral contrast.
- **Reproducibility:** compare all four output files from two same-seed runs byte-for-byte. If outputs differ, explain and resolve the difference.

The six marked assignment categories still total 100 points; incorporate these tasks into protocol, events/metadata, timing, QC, and reproducibility deliverables.
