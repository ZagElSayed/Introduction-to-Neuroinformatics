# Lab 3 — Sampling, Nyquist Limits, and Aliasing

**Textbook:** Chapter 3 of *Introduction to Neuroinformatics: Data, Computational Models, and Neuroscience*  
**Estimated time:** 55–70 minutes  
**Levels:** undergraduate core + graduate extension  
**Notebook:** [03_sampling_spectrum.ipynb](03_sampling_spectrum.ipynb)  
**Data:** Synthetic 35-Hz sine wave generated in the notebook; no external dataset.

## Learning outcomes

1. Compute the Nyquist frequency for a selected sampling rate.
2. Identify alias frequencies from a discrete Fourier spectrum.
3. Explain the role of analog anti-alias filters before digitization or downsampling.

## Preparation and ethical use

From the companion repository root, run `python -m pip install -r requirements.txt` and `jupyter lab`, then open the chapter notebook. No dataset download is needed; the notebook uses explicitly synthetic data. Preserve original data. These exercises are not diagnostic software; do not upload identifiable or restricted recordings to public services.

## Student procedure

1. Run both FFT examples and identify the dominant observed frequencies.
2. Calculate Nyquist frequencies at 200 Hz and 50 Hz sampling.
3. Derive the alias of a 35-Hz input sampled at 50 Hz.
4. Change sampling to 80 Hz and explain why the 35-Hz component is now representable.

## Expected observations (not an answer key for clinical interpretation)

At 200 Hz, the spectrum peaks at 35 Hz; at 50 Hz it peaks at 15 Hz. These are simulated ideal samples, not real electrode measurements.

## Interpretation questions

1. What exactly is observed or computed, in which units, and from which source?
2. Which choices (sampling, reference, window, noise model, preprocessing, or data structure) can change the result?
3. What conclusion would be scientifically unjustified from this experiment alone?
4. How would another student reproduce the output? Record versions, source, and parameter settings.

## Graduate extension

Explore 45-Hz and 65-Hz inputs and compare analytical alias predictions with FFT output; distinguish sampling from anti-alias filtering.

## Submission checklist

- [ ] Executed notebook or exported figures/output, with errors resolved or documented.
- [ ] Brief report (about 1–2 pages undergraduate; 2–3 pages graduate) addressing the questions.
- [ ] Input dataset/source or synthetic seed, versions, and parameter values recorded.
- [ ] One scientific limitation and a quality-control note.
- [ ] Graduate students: reproducible extension and quantitative comparison.
- [ ] No participant-level data or identifiable clinical information included in submission unless explicitly approved by course policy.

## Grading rubric

| Criterion | Undergraduate | Graduate | Points |
|---|---|---|---:|
| Reproducible setup and source/provenance | Runs notebook; records inputs and software | Also documents parameter/environment changes and rerun method | 20 |
| Correct implementation and outputs | Executes core cells and produces expected plots/files | Also implements a justified quantitative extension | 25 |
| Scientific interpretation | Correct units, physiology, and limitations | Also evaluates assumptions, confounders, and alternatives | 25 |
| Quality control and critical reasoning | Notes artifacts, uncertainty, or simulation limits | Quantifies or systematically tests a relevant limitation | 20 |
| Clear submission and ethical data handling | Clear report; no raw recordings committed | Same, with reproducible comparison | 10 |
| **Total** | | | **100** |

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| `ModuleNotFoundError` | Notebook kernel differs from installed environment | Install `pip install -r requirements.txt` in the intended environment; restart kernel |
| `FileNotFoundError: S001R01.edf` | EDF is not in notebook's working directory | Download from the original PhysioNet dataset; check `Path.cwd()` and edit `edf` path |
| No plots appear | Backend/kernel problem | Run cells in order; restart Jupyter kernel and rerun |
| Channel types or montage are unexpected | Metadata or device naming differences | Inspect `raw.info` and channel types; do not invent sensor coordinates |
| Spectrum differs from a peer's | Channel, segment length, reference, or preprocessing differ | Compare exact analysis parameters and units |
| `outputs/` appears in Git changes | Local derivatives were created | Keep generated outputs and raw EDF files untracked; never commit participant-level recordings |
| Very high model accuracy in an extension | Leakage, confounding, or participant overlap | Split by participant first and verify training-only preprocessing |

## Instructor verification

The notebook must parse as notebook format 4 and run in the documented environment. Synthetic labs can be tested without external data. For real-EDF labs, run with the original PhysioNet recording and verify channel metadata, plots, and units before assigning. Automated synthetic smoke tests are **not** a substitute for checking results on the source dataset.
