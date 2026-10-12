# Lab 7 — ECG, Accelerometry, Clock Synchronization, and Missing Data

**Chapter:** 7, *Peripheral, Behavioral, and Wearable Signals*  
**Time:** 90–120 minutes; optional graduate extension 30–45 minutes  
**Data:** Locally generated synthetic signals only (no patients or download).  
**Tools:** Python 3.11, NumPy, Matplotlib, standard-library CSV/JSON.

## Learning objectives

1. Distinguish ECG voltage, acceleration, heart rate, and task events by units and sampling frequency.
2. Explain device timestamps versus reference timestamps and correct a known 250-ms offset.
3. Preserve native-rate measurements while creating a documented 1-Hz derived-feature table.
4. Compute acceleration magnitude and instantaneous heart rate from known synthetic beat times.
5. Detect a simulated three-second IMU packet-loss interval and avoid replacing missing data with zeros.
6. Explain why synthetic physiological correlations are not clinical biomarkers.

## Setup (from the public repository root)

```bash
python -m pip install -r requirements.txt
python chapters/ch07-wearables/exercise_7_1_multimodal_timeline.py --output-dir outputs/ch07
```

The command creates six files in `outputs/ch07/`: `ecg_native.csv`, `imu_native.csv`, `events.csv`, `analysis_table.csv`, `multimodal_timeline.png`, and `metadata.json`. No network access or external dataset is needed after dependency installation.

## Student procedure

1. Open `metadata.json`. Identify the data source, seed, ECG/IMU sample rates, measurement units, and clock offset.
2. Plot or inspect `multimodal_timeline.png`. Explain the two event lines at 40 and 80 seconds and the shaded IMU data gap from 55 to 58 seconds.
3. Open `ecg_native.csv`. Compare `device_time_s` and `reference_time_s` and verify the 0.250-second offset. Explain how to correct timestamps without modifying voltage samples.
4. Open `imu_native.csv`. Compute acceleration magnitude as `sqrt(ax² + ay² + az²)` for valid samples. Explain why magnitude includes gravitational acceleration and does not directly measure activity intensity.
5. Open `analysis_table.csv`. Explain the difference between native ECG (250 Hz), native IMU (50 Hz), and the 1-Hz derived-feature grid. The heart rate is computed from **known synthetic beat times**, not an ECG peak detector.
6. Verify that acceleration features are missing (NaN) during packet loss and that `imu_coverage_fraction` reports zero for affected complete windows. Explain why imputing zero would be misleading.
7. Compare the two event-centered ECG means reported in `metadata.json` (corrected versus uncorrected clock). Explain how a timestamp error can change an event-centered analysis; do not claim that one window captures a meaningful physiological event response.
8. Write a 1–2-page reproducibility and interpretation report with the run command, version information, two screenshots or figures, and your answers to steps 1–7.

## Expected results

- ECG: 250 samples/s; IMU: 50 samples/s; approximately 120 seconds.
- ECG device clock has a **+0.250 s** offset.
- Events: activity starts at 40 s and ends at 80 s.
- IMU samples from 55 s (inclusive) to 58 s (exclusive) are marked missing.
- The 1-Hz table contains heart-rate estimates, acceleration summaries, and quality coverage. Edge bins may have missing heart-rate values because interpolation is intentionally restricted to the supported beat interval.
- All signals are synthetic. The ECG is not physiologically realistic, and the activity labels are prescribed by the generator.

## Graduate extension

Implement an alternative timestamp-alignment approach with two known synchronization markers and an added linear clock drift. Compare estimated drift and offset with the generator's known parameters. Compare a complete-case activity summary against a documented imputation approach, and quantify how much each changes the result. Keep original and corrected timestamps in separate fields. Explain why these simulated demonstrations do not validate clinical monitoring.

## Submission and grading (100 points)

| Criterion | Points |
|---|---:|
| Reproducible setup, seed, and provenance | 15 |
| Correct interpretation of native sampling, units, and derived features | 20 |
| Timestamp offset and event-alignment explanation | 20 |
| Missingness, quality flags, and analysis limitations | 20 |
| Figures, exported files, and clear scientific report | 15 |
| Privacy, ethical limitations, and responsible interpretation | 10 |
| **Total** | **100** |

## Troubleshooting

- `ModuleNotFoundError`: install root `requirements.txt` into the same interpreter used to run the script.
- No files visible: check the `--output-dir` path relative to your working directory.
- NaN in acceleration summary: expected for the simulated packet-loss window; do not silently replace it.
- Want real patient or wearable data: **do not** pass raw real-world recordings to this synthetic teaching script. A real-data workflow needs consent/permissions, device calibration, signal quality, clock validation, and a documented preprocessing plan.

**Instructor preflight:** `python -m pytest -q tests/test_chapter7_lab.py`.

## Exercise 7.2 — Integrated systems and biomarker audit (30–45 minutes)

This extension connects **Section 7.9 (candidate digital biomarkers)** and **Section 7.10 (remote neuroinformatics systems)** to the synthetic lab. First run Exercise 7.1, then:

```bash
python chapters/ch07-wearables/exercise_7_2_remote_monitoring.py --input-dir outputs/ch07 --output-dir outputs/ch07/audit
```

Inspect `quality_windows.csv` and `engineering_audit.json` and answer:

1. Which one-second windows fail the 80% IMU coverage criterion? Why must a failed window be excluded rather than treated as zero movement?
2. Distinguish a 12-minute **network outage with successful edge buffering** from **sensor detachment**. Which produces late packets, and which produces invalid physiological observations?
3. Recalculate the nominal 1,050 bytes/s and 756,000-byte buffer from the Section 7.10 channel assumptions. What additional capacity is needed for timestamps, security, and operational overhead?
4. Explain why the hypothetical PPG and EDA channels in the storage estimate do not appear in Exercise 7.1's generated CSV files.
5. Choose ECG-derived heart rate or IMU-derived activity as a **candidate** feature. Write a context-of-use statement, identify two confounders, propose a reference measurement, and distinguish analytical validity from clinical validity.
6. Sketch a minimal schema with participant pseudonym, acquisition timestamp, corrected timestamp, device/firmware version, quality mask, processing version, and consent state. Describe a participant-level train/test split for any future predictive analysis.

**Deliverables:** both exported audit files and a one-page engineering and biomarker-interpretation note. These are exploratory teaching outputs and must not be described as validated clinical biomarkers.

**Assessment:** The existing 100-point Exercise 7.1 rubric remains unchanged. Instructors may assign this extension separately (suggested 25 points: coverage and missingness 5; storage calculations 5; biomarker evidence 5; provenance/security schema 5; scientific interpretation 5).
