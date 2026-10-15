# Chapter 13 — Time–Frequency and Spectral Analysis

Use a known synthetic signal to separate **changes in physiology from changes in the estimator**. This standard-library lab computes density-scaled one-sided periodograms by direct DFT, averages them for Welch PSDs, and keeps individual frames for spectrograms. It uses no FFT package and downloads no human data.

## Run locally from the repository root

```bash
python chapters/ch13-time-frequency/exercise_13_1_welch_sensitivity.py --output-dir outputs/ch13/run01
python -m pytest -q tests/test_chapter13_lab.py
```

Choose a new or empty directory for each run; nonempty paths are refused. Tests and numerical results require local execution. Passing software checks is not scientific validation of human EEG.

## Controlled experiments

| Experiment | Fixed information | Changed choice | What to inspect |
|---|---|---|---|
| Welch, 1 versus 2 seconds | Same 4-s signal, symmetric Hann, 50% overlap, density scaling | Segment length 128 versus 256 | Bin spacing 1 versus 0.5 Hz, 7 versus 3 averaged segments, peak height and band integral |
| Zero-padding control | Same 128 observed samples per segment | DFT length 128 versus 512 | Grid spacing 1 versus 0.25 Hz; the observation duration and resolving information stay the same |
| Transient burst | Same 8-s recording, same 16-sample hop | 1-s versus 2-s windows | Temporal spreading, frequency smoothing, unavailable boundary estimates |

The stationary signal is `12*sin(10 Hz) + 4*sin(22 Hz) + 1.5*sin(3 Hz)`, in microvolts, at 128 Hz. Over its four seconds the components complete integer cycles. Its exact analytic mean square is `(12² + 4² + 1.5²)/2 = 81.125 microvolts²`; the 10-Hz term alone contributes 72 microvolts². A finite-window band integral is an estimate and includes taper/leakage effects.

The separate burst recording has 3- and 22-Hz backgrounds plus a 10-Hz oscillation with a smooth Hann amplitude envelope supported from 3 through just before 5 s. The envelope peaks at 4 s with amplitude 10 microvolts. This is one constructed event with no trial population, significance test, neural source inference, or event-related baseline normalization.

## Explicit conventions

- **Taper:** symmetric Hann, `0.5 - 0.5*cos(2*pi*j/(L-1))`. This differs from a periodic Hann and should be supplied as an explicit array when comparing with SciPy.
- **Detrending:** subtract each segment's arithmetic mean before applying its taper.
- **Density:** divide squared DFT magnitude by `fs * sum(window²)`; double positive-frequency bins except DC and Nyquist. Units are `microvolts²/Hz`.
- **Welch:** mean average of full frames; overlap samples are `floor(L*overlap)`; unused tail is reported. The number of overlapping segments is not an independent sample size.
- **Padding:** `nfft` sets DFT grid spacing; observed length sets available temporal information. Zero-padding changes neither segment weights nor its duration.
- **Band integration:** rectangular uniform-bin sum times `df`, with low inclusive and high exclusive boundaries. Alpha is `[8,13)` and its relative denominator is `[1,40)`. Full-grid Parseval checks include both endpoints and are different from these band summaries.
- **ENBW:** `fs * sum(window²) / sum(window)²`. This describes the taper's equivalent noise bandwidth, not another participant count or a universal two-peak resolution threshold.
- **STFT:** no boundary padding; frames use the same detrending/taper/density convention. Time is the mean of the first and last sample times. Hop 16 samples gives a 0.125-s display grid; it does not provide 0.125-s independent temporal resolution.

## Saved evidence

| Artifact | Content |
|---|---|
| `stationary_signal.csv` | Sample index, time, unchanged synthetic mixture |
| `burst_signal.csv` | Mixture, known burst, and known envelope |
| `welch_128_nfft_128.csv` | 1-s Welch estimate |
| `welch_256_nfft_256.csv` | 2-s Welch estimate |
| `welch_128_nfft_512.csv` | Zero-padded 1-s control |
| `stft_128.csv`, `stft_256.csv` | Full-window start/stop, center time, frequency and linear PSD |
| `psd_comparison.svg` | Common logarithmic PSD axes; display-only floor |
| `tfr_comparison.svg` | Common color scale for both windows; unavailable edges are gray |
| `spectral_report.json` | Config/code/runtime identities, hashes, timing, QC, features and review state |

The TFR image uses **dB relative to the common plot maximum**, floored at -60 dB for display. That plotting reference is not a pre-event baseline and does not alter the linear CSV values. The PSD plot has a display floor of `1e-8`; do not integrate either plotted log quantity to obtain band power.

For each Welch configuration the report compares the full PSD integral with the average taper-weighted, mean-detrended time-domain energy. This is the matching Parseval check; neither quantity must equal the untapered recording's mean square exactly. `alpha_peak_hz` is only the maximum bin in `[8,13)`, not a fitted or statistically established oscillatory peak. The status stays `review_required` and acceptance remains false.

## Assignment — 100 points

1. **Measurement and units (15):** Explain sample rate, duration, Nyquist, amplitudes, and the known mean square. Distinguish a signal unit, density unit, integrated power, and relative power.
2. **Estimator mechanics (20):** Explain taper, detrending, one-sided factors, overlap, unused samples and the matching energy check. Do not equate seven frames with seven people.
3. **Resolution sensitivity (20):** Compare all three Welch configurations, including ENBW. Separate denser frequency sampling from information needed to distinguish close peaks.
4. **Time–frequency reasoning (20):** Compare both burst maps against the known support. Explain smearing, absent boundary estimates, center timestamps, and why the dense time grid does not establish onset precision.
5. **Interpretation (15):** Compare absolute and relative alpha estimates. Explain why this example establishes neither an aperiodic exponent nor a clinical mechanism. Use `REAL_EEG_PROTOCOL.md` to plan the real-data checks.
6. **Reproducibility (10):** Submit the full run directory, annotated plots, configuration/code hashes and a short sensitivity report; state what was executed and what remains unverified.

## Chapter figure mapping

| Figure | Companion connection |
|---|---|
| 13.1 Waveform/spectrum | Known mixture and PSD; phase is discarded by power |
| 13.2 Fourier intuition | Direct DFT implementation and analytic component powers |
| 13.3 Window tradeoff | One-/two-second Welch and burst STFT comparisons |
| 13.4 PSD reading | Density, integral, ENBW, and maximum-bin limitations |
| 13.5 Periodic/aperiodic | Interpretation/design only; no aperiodic model is fitted |
| 13.6 Time–frequency map | Known burst, full-frame support, common display scale |
| 13.7 ERD/ERS | Real-data protocol; no ERD/ERS or baseline inference in this simulation |
| 13.8 NeuroBridge | Preserved inputs, named configurations, review state and evidence |

Extensions: cross-check the direct DFT against a library with the **same explicit window and conventions**; compare multitaper or Morlet estimates using versioned software. The baseline does not implement wavelets, periodic/aperiodic fitting, connectivity, repeated-trial inference, or clinical analysis.
