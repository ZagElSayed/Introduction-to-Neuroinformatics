# Chapter 9 — Neurodata Formats, Standards, and Metadata

**Lab contract v1.1. Python 3.11+; standard library only.** Convert a fictional CSV event log from milliseconds to seconds and map event codes to a TSV plus JSON metadata. Inspect object links and SHA-256 digests; distinguish byte integrity from preserved meaning. No human data, EEG/MRI signal processing, or clinical de-identification is performed.

The export uses a `beh/` folder because this exercise contains behavioral events without a neural recording. It is **BIDS-inspired, not a complete BIDS dataset**: no corresponding task data file is supplied. Declaring `BIDSVersion` does not establish compliance. The local validator checks this explicit teaching contract, not the entire BIDS specification.

## Run from the repository root

```bash
python chapters/ch09-data-standards/exercise_9_1_neurodata_contract.py --output-dir outputs/ch09
python chapters/ch09-data-standards/exercise_9_1_neurodata_contract.py --output-dir outputs/ch09 --validate-only
python chapters/ch09-data-standards/exercise_9_2_validation_layers.py --output-dir outputs/ch09-failures
python -m unittest discover -s tests -p test_chapter9_lab.py -v
```

If pytest is already installed, `python -m pytest -q tests/test_chapter9_lab.py` runs the same tests. It is not needed for this lab.

Use a fresh output directory for each run. Generation refuses to overwrite a nonempty directory; `--force` explicitly regenerates the known synthetic demo files. It is only for this demo and does not delete unrelated files. Validation leaves data and the manifest unchanged and writes its findings to `validation_report.json`; copy that report if you need to preserve successive review records. Exit status is **0 for passing local checks, 1 for failure**. The failure-demonstration script returns 0 only when all deliberately introduced failures are detected.

## Understand the outputs

| Object | Role |
| --- | --- |
| `source/Study_P01_task.csv` | Fictional source log: `time_ms,code`; `500,G` means an event at 500 ms. |
| `source/source_contract.json` | Declares milliseconds, time origin, and `G → go`, `N → nogo`. |
| `export/sub-001/ses-01/beh/*_events.tsv` | Actual converted values: onsets `0.5, 2.0, 3.5` seconds, zero durations, defined trial types. |
| `*_events.json` | Column definitions, seconds, event-time origin, and trial vocabulary. |
| `participants.tsv` and `participants.json` | Fictional participant linkage and group dictionary. |
| `dataset_description.json` and `README` | Dataset context and explicit teaching limitations. |
| `manifest.json` | Eight source/target/metadata objects, their full SHA-256 digests, and conversion/identity links. |
| `validation_report.json` | Per-check layer/results, errors, and limitations; no clinical or governance certification. |

The validator checks finite event times, nonnegative duration, permitted labels, expected columns, metadata units/time origin, participant linkage, source-to-target values, and file digests. Negative onsets are allowed when they describe events before the first stored task data point; negative durations are rejected. These are different meanings. The synthetic zero durations represent impulse-like events, not missing durations.

## Student assignment (100 points)

1. **Inventory and representation (15):** Describe all source/export objects and the roles of format, dataset convention, and metadata. Explain why this is not EEG or MRI conversion.
2. **Metadata and conversion (25):** Trace `500,G → 0.5 seconds, go`. Explain the time origin, zero duration, units, and allowed codes. Inspect the participant and event dictionaries. Name the missing evidence for full BIDS compliance.
3. **Integrity and provenance (20):** Explain the source/target digest distinction. Inspect the unchanged baseline alongside `source_change`. Why should a copy retain its digest while a converted TSV normally differs from its CSV source?
4. **Validation layers (25):** Inspect all five isolated failure directories and `failure_summary.json`. Identify integrity versus structural/semantic findings. In `meaning_with_rehashed_target`, the complete target hash reference was deliberately updated **only to demonstrate the limitation**; the original manifest is retained as `manifest_before_rehash.json`. Explain why this case fails meaning checks despite a matching target hash. Never repair a real mismatch by rebaselining a suspect object.
5. **Clinical and governance review (10):** Identify identity, timing, acquisition, unit, and permission questions that remain for a genuine multisite study. Submit no patient identifiers or clinical data.
6. **Reproducibility (5):** Record Python version, commands, test outcome, and paths of evidence used.

**Submit:** baseline export and manifest, five failure reports and summary, commands/test result, and a 1–2-page interpretation. Preserve the baseline; perform further manual experiments on copies. Automated success does not establish scientific correctness, participant identity, privacy protection, or permission for use.

**Graduate extension:** Propose a genuine BIDS EEG dataset with actual recording and modality-specific sidecars, official validator integration, reviewed acquisition/identity/units, and protected mapping boundaries. Explain how a negative onset can be valid. Do not claim the teaching export is fully compliant.

## Resources and book alignment

Use [RESOURCES.md](RESOURCES.md) for primary standards and tools. This lab implements Chapter 9's data contract, dictionaries, object links, integrity, and layered validation. Chapter 8 owns experimental event generation; Chapter 10 owns infrastructure; Chapter 11 develops governance. The dedicated GitHub Actions workflow runs the same tests and baseline/failure demonstrations.
