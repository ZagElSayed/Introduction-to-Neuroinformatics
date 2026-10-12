# Chapter 13 — Time–Frequency and Spectral Analysis

**Status: runnable synthetic spectral-estimation lab.** The baseline uses a transparent Python standard-library implementation of one-sided Welch PSD with a Hann taper, segment-wise mean detrending, and 50% overlap. It compares 1-s and 2-s segments for a synthetic signal containing 3, 10, and 22 Hz components. No human EEG or clinical interpretation is involved.

## Run from the student repository root

```bash
python chapters/ch13-time-frequency/exercise_13_1_welch_sensitivity.py --output-dir outputs/ch13
python -m pytest -q tests/test_chapter13_lab.py
```

Outputs: `welch_128.csv`, `welch_256.csv`, `spectral_report.json`.

## Assignment (100 points)

1. **Frequency fundamentals (15):** Explain sampling rate, Nyquist frequency, signal duration, and the three known simulated oscillations.
2. **Welch estimator (20):** Identify the taper, overlap, mean detrending, PSD units, and one-sided scaling. Explain why Welch averages reduce variance without creating new independent data.
3. **Resolution sensitivity (20):** Compare 128- and 256-sample windows. Calculate bin spacing, segment count, and changes in alpha peak and band power. Explain why zero-padding does not improve true resolving power.
4. **Band power interpretation (15):** Compare integrated 8–13 Hz alpha power with total 1–40 Hz power. Explain the difference between absolute, relative, and peak-centered measurements.
5. **Aperiodic and artifacts (15):** Describe how a broadband background change or line-noise contamination could alter a band-power result. State why this synthetic example does not perform periodic/aperiodic decomposition.
6. **Reproducibility (15):** Submit outputs, commands, estimator settings, a PSD plot for both windows, and a short sensitivity report.

**Graduate extension:** Analyze an approved public EEG dataset with MNE-Python. Compare Welch and multitaper estimates; generate event-related time–frequency power with explicit baseline choices; fit periodic/aperiodic models only when assumptions and fit diagnostics are satisfied. Validate at participant level and avoid treating time-frequency pixels as independent participants.

**Limits:** The baseline exercise computes stationary PSDs only. It does not implement STFT, wavelets, FOOOF/specparam, ICA, or infer neural mechanisms.
