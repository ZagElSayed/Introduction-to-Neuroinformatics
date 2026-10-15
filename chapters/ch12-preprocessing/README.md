# Chapter 12 — Neural Signal Preprocessing and Artifact Modeling

This standard-library teaching lab compares **unchanged and smoothed synthetic mixtures against their known sources**. The central question is whether a preprocessing choice changes the intended signal, not whether the trace looks cleaner. It implements no ICA, physiological artifact removal, real EEG analysis, or clinical validation.

## Run locally from the repository root

Use a different, new or empty directory for each run. Nonempty directories are refused so previous evidence is retained.

```bash
python chapters/ch12-preprocessing/exercise_12_1_artifact_qc.py --output-dir outputs/ch12/w01 --window 1
python chapters/ch12-preprocessing/exercise_12_1_artifact_qc.py --output-dir outputs/ch12/w11 --window 11
python -m pytest -q tests/test_chapter12_lab.py
```

Run these checks locally before interpreting results. Choose new paths for later comparisons; passing software checks does not establish validity for real neural data.

## What the generator defines

- 500 samples at 250 Hz: a 2-second sample interval, with last sample at 1.996 s.
- Neural source: a 10-Hz sinusoid with peak amplitude 12 microvolts at Fz and 9.6 microvolts at Pz.
- Ocular transient: a triangular pulse centered at 0.8 s, peak 85 microvolts; Pz receives one quarter of the Fz contribution. Drift: a 0.5-Hz sinusoid with peak amplitude 7 microvolts at both channels.
- A synthetic EOG-like channel contains the pulse alone. This ideal source separation is a simulation convenience, not a claim about real EOG.
- An event marker at sample 250 (1.0 s) is preserved. There is no evoked response, repeated trial set, or condition comparison.
- Signals use microvolts throughout. The channel labels do not imply a physical montage or electrode reference.

## Artifacts per run

| File | Evidence |
|---|---|
| `synthetic_raw.csv` | Fixed mixture, sample indices, time, two signals and EOG-like channel |
| `synthetic_truth.csv` | Neural, pulse, and drift sources known by construction |
| `events.csv` | Original sample and time coordinates |
| `synthetic_smoothed.csv` | Derivative and explicit boundary-window flags |
| `qc_comparison.svg` | Both channels: raw, smoothed, and known neural traces on a fixed amplitude scale |
| `qc_provenance.json` | Configuration, code/runtime identity, run/time identifiers, hashes, QC, and review state |

The transform is an odd-width **centered moving average**. Away from the boundaries it uses equal weights over the full window. At the first and last half-window, it truncates and renormalizes the available weights; these samples are flagged. It uses future samples and therefore cannot be directly deployed as a zero-latency online filter. Width 1 is the identity control; width 11 spans 44 ms and uses five future samples (20 ms look-ahead).

## Read QC without equating smoothness with validity

Peak and RMS describe the full recorded mixture and derivative. The known-source comparisons use only the full-window interior, avoiding a claim that the boundary operator has the same response:

- `raw_vs_neural_rmse_uV`: error of the mixture relative to the neural source.
- `derivative_vs_neural_rmse_uV`: total error after smoothing, combining residual nuisance and neural distortion.
- `neural_only_filter_rmse_uV`: distortion caused by applying the same transform to the neural source alone.
- `remaining_filtered_nuisance_rms_uV`: nuisance that remains when pulse plus drift is filtered separately. Neural and nuisance errors can correlate; their RMS values should not simply be added.

For an odd, centered boxcar of width L, its interior signed response at frequency f is `sin(pi*f*L/fs)/(L*sin(pi*f/fs))`; the report evaluates this at 10 Hz. Magnitude is the absolute value. For some widths, the signed response can be negative; this is more than simple amplitude attenuation. This formula does not describe truncated boundary windows. Detailed PSD/time-frequency estimation follows in Chapter 13.

The report remains `review_required` and `accepted_as_neurally_valid: false`. A lower total RMSE in this particular simulation does not establish general validity for human recordings. Content hashes verify bytes, not scientific correctness; run IDs/timestamps differ between otherwise deterministic runs.

## Assignment — 100 points

1. **Measurement contract (15):** State units, timing, neural source, nuisance sources, scientific endpoint, and what is known only because this is synthetic.
2. **Controlled comparison (20):** Compare width 1 and 11 using identical raw/truth/event hashes. Inspect both channels and explain peak/RMS changes using known-source error metrics.
3. **Filter reasoning (20):** Calculate width, look-ahead, and the 10-Hz response; compare full-window and boundary behavior. Explain why this is neither a validated band-pass nor an artifact classifier.
4. **Preservation and QC (15):** Explain how lower nuisance amplitude can coexist with neural distortion. Identify another artifact model and independent evidence needed before adopting it.
5. **Reproducibility and review (15):** Submit both run directories, configuration/code hashes, annotated QC plots, and a one-page decision rationale. State what the reviewer cannot conclude.
6. **Transfer to real data (15):** Use `REAL_EEG_PROTOCOL.md` to propose reference, rank, filter, annotation, ICA review, retention and endpoint checks. Distinguish the proposal from an executed analysis.

Optional graduate extension: carry out the real-data protocol on an appropriately licensed dataset, keeping participant/site separation and preserving all decisions. No data are downloaded by the baseline lab.

## Figure-to-lab mapping

| Figure | Connection to this exercise |
|---|---|
| 12.1 Mixture | Raw and known sources; ideal additive assumptions |
| 12.2 Decision pipeline | Validate parameters, preserve run artifacts, review the derivative |
| 12.3 Filtering | Width sensitivity, boundary weights, 10-Hz attenuation, noncausal look-ahead |
| 12.4 Reference | Explain why synthetic labels provide no real reference; apply the real-data protocol |
| 12.5 Artifacts | Pulse and drift are simulated; real signatures require converging evidence |
| 12.6 ICA | Design/review only; ICA is not implemented here |
| 12.7 Human + AI | Explicit review state; no component classifier or automatic acceptance |
| 12.8 NeuroBridge | Code/configuration/artifact identities and review handoff; no production service |
