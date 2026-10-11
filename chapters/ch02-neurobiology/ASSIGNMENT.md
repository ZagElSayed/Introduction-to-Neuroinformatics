# Lab 2 — Simulating Neural Oscillations and Transients

**Textbook:** Chapter 2 of *Introduction to Neuroinformatics: Data, Computational Models, and Neuroscience*  
**Estimated time:** 50–65 minutes  
**Levels:** undergraduate core + graduate extension  
**Notebook:** [02_neural_signals.ipynb](02_neural_signals.ipynb)  
**Data:** Synthetic data generated in notebook with NumPy random seed 42; no external dataset.

## Learning outcomes

1. Explain oscillatory and transient components in a conceptual signal model.
2. Differentiate simulated mixtures from physiological forward models.
3. Evaluate how added noise alters visibility of transient events.

## Preparation and ethical use

From the companion repository root, run `python -m pip install -r requirements.txt` and `jupyter lab`, then open the chapter notebook. No dataset download is needed; the notebook uses explicitly synthetic data. Preserve original data. These exercises are not diagnostic software; do not upload identifiable or restricted recordings to public services.

## Student procedure

1. Run the notebook and identify the 10-Hz, 2-Hz, and transient components.
2. Estimate the time of the synthetic transient from the plot.
3. Increase noise standard deviation from 5 to 12 and compare interpretability.
4. Explain why a synthetic oscillation cannot be labeled a specific cortical generator.

## Expected observations (not an answer key for clinical interpretation)

A two-panel plot showing the illustrative components and their noisy mixture; the transient is centered near 2 seconds.

## Interpretation questions

1. What exactly is observed or computed, in which units, and from which source?
2. Which choices (sampling, reference, window, noise model, preprocessing, or data structure) can change the result?
3. What conclusion would be scientifically unjustified from this experiment alone?
4. How would another student reproduce the output? Record versions, source, and parameter settings.

## Graduate extension

Run repeated noise realizations, quantify transient peak detectability, and explain how detection depends on noise assumptions.

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
