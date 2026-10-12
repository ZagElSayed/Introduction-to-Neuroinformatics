# Chapter 12 — Neural Signal Preprocessing and Artifact Modeling

**Status: runnable synthetic companion laboratory.** The baseline Python exercise demonstrates why preprocessing choices change scientific measurements, without pretending that smoothing is a clinically validated artifact-removal pipeline. It uses Python's standard library and creates **synthetic EEG-like signals** containing a 10-Hz oscillation, slow drift, and a simulated blink.

## Run from the repository root

```bash
python chapters/ch12-preprocessing/exercise_12_1_artifact_qc.py --output-dir outputs/ch12 --window 11
python chapters/ch12-preprocessing/exercise_12_1_artifact_qc.py --output-dir outputs/ch12 --window 1
python -m pytest -q tests/test_chapter12_lab.py
```

Outputs: `synthetic_raw.csv`, `synthetic_smoothed.csv`, `qc_provenance.json`.

## Student assignment (100 points)

1. **Signal provenance (15):** Identify sampling rate, simulated oscillation, blink timing, and drift. Explain what is known by construction versus what a researcher would need to infer from real EEG.
2. **Before/after QC (20):** Compare peak amplitude and RMS of both channels before and after smoothing. Explain why lower amplitude is not proof of improved neural fidelity.
3. **Filter reasoning (20):** Compare 1-sample (identity) and 11-sample moving-average windows. Calculate window duration and explain edge behavior, waveform distortion, and why this is not a band-pass filter.
4. **Artifact decisions (15):** Propose a separate annotation, regression, or ICA strategy for a real dataset, including independent evidence required before removing a component.
5. **Scientific preservation (15):** Explain which real neural phenomena might be attenuated by smoothing, and how you would validate downstream ERP or spectral endpoints.
6. **Reproducibility (15):** Report SHA-256 digests, parameter values, output differences, and limitations. Submit a short report and QC plots.

**Graduate extension:** Use MNE-Python on a properly licensed public EEG dataset to compare justified filter settings, bad-channel annotation, ICA with reviewed component decisions, epoch retention, and a preregistered downstream metric. Maintain subject-level separation if a classifier is used.

**Limits:** The synthetic example is not human EEG; it does not implement ICA, EOG regression, MNE, formal BIDS compliance, or clinical signal processing. No result should be interpreted diagnostically.
