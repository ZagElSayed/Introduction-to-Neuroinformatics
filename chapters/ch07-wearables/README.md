# Chapter 7 — Peripheral, Behavioral, and Wearable Signals

A complete, reproducible laboratory integrating **synthetic ECG**, **three-axis accelerometry**, **activity events**, **clock synchronization**, **missing-data quality flags**, and **1-Hz derived features**. No participant data or download is required.

- [Student assignment, procedure and 100-point rubric](ASSIGNMENT.md)
- [Python analysis script](exercise_7_1_multimodal_timeline.py)
- [Automated validation tests](../../tests/test_chapter7_lab.py)

## Quick start

From the repository root:

```bash
python -m pip install -r requirements.txt
python chapters/ch07-wearables/exercise_7_1_multimodal_timeline.py --output-dir outputs/ch07
```

Inspect `outputs/ch07/multimodal_timeline.png`, `outputs/ch07/analysis_table.csv`, and `outputs/ch07/metadata.json`. Native-rate ECG, IMU, and event files are exported separately to preserve sampling and provenance.

## Instructor verification

```bash
python -m pytest -q tests/test_chapter7_lab.py
```

The [Chapter 7 lab workflow](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics/actions/workflows/chapter7-lab.yml) runs the student-facing CLI and validates output files, sampling, clock offset, and the missing-data window. The generated signals are intentionally simplified: synthetic R-peak times are supplied by the generator, and results cannot be used for medical decisions.

See [the chapter laboratory standard](../../docs/CHAPTER_LAB_STANDARD.md).
