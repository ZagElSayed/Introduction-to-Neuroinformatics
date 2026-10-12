# Chapter 9 — Neurodata Formats, Standards, and Metadata

**Status: runnable synthetic lab.** Build a small BIDS-inspired event dataset, inspect a source-to-target checksum manifest, and validate basic JSON/TSV schema constraints. This is **not** a formal BIDS certification and does not contain genuine EEG, MRI, or patient records.

## Run from the repository root

```bash
python chapters/ch09-data-standards/exercise_9_1_neurodata_contract.py --output-dir outputs/ch09
python chapters/ch09-data-standards/exercise_9_1_neurodata_contract.py --output-dir outputs/ch09 --validate-only
python -m pytest -q tests/test_chapter9_lab.py
```

Inspect `outputs/ch09/source/`, `outputs/ch09/export/`, `outputs/ch09/manifest.json`, and `outputs/ch09/validation_report.json`.

## Student assignment (100 points)

1. **Inventory and representation (20):** Identify the source event file, coded participant/session ID, target event TSV, and modality represented. Explain why a synthetic event table is not an EEG or MRI conversion.
2. **Metadata contract (20):** Inspect `dataset_description.json`, event sidecar JSON, and `participants.tsv`. Describe units, event labels, and how metadata preserves meaning. Identify further requirements for actual BIDS compliance.
3. **Provenance and checksums (20):** Explain the SHA-256 mapping in `manifest.json`. Modify the source file and run `--validate-only`; show that the checksum check fails, then regenerate to restore the original synthetic dataset.
4. **Validation layers (20):** Introduce an invalid onset (e.g. `bad`) in a copy of the event TSV and verify that the validator flags it. Explain why syntactic checks do not establish scientific validity or full BIDS compliance.
5. **Governance and interoperability (10):** Identify which fields would require restricted access in a real multisite EEG--MRI study; do not include direct identifiers in this exercise.
6. **Reproducibility (10):** Submit the commands, output manifest, validation report, and a short reflection distinguishing file format, dataset standard, and data dictionary.

**Deliverables:** exported files, one modified-file failure demonstration, and a 1–2-page report.

**Graduate extension:** Propose a genuine BIDS EEG dataset layout and an official BIDS-validator step, including modality-specific requirements and a human scientific audit. Do not claim the teaching export is a fully validated BIDS dataset.

## Book alignment

Implements Chapter 9's formats, BIDS-inspired organization, metadata, provenance, and layered validation. Chapter 8 owns experimental event generation; Chapter 10 owns scalable pipelines and infrastructure; Chapter 11 owns governance and access control.
