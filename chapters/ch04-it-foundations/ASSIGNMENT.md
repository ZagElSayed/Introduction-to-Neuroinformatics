# Lab 4 — Building an Auditable Data Pipeline

**Textbook:** Chapter 4 of *Introduction to Neuroinformatics: Data, Computational Models, and Neuroscience*  
**Estimated time:** 60–75 minutes  
**Levels:** undergraduate core + graduate extension  
**Notebook:** [04_provenance_pipeline.ipynb](04_provenance_pipeline.ipynb)  
**Data:** Deterministic synthetic array (seed 17), locally saved as .npy; no clinical data.

## Learning outcomes

1. Generate a reproducible numerical dataset and derived summary.
2. Verify data integrity using SHA-256.
3. Explain provenance fields needed for reproducible neuroscience.

## Preparation and ethical use

From the companion repository root, run `python -m pip install -r requirements.txt` and `jupyter lab`, then open the chapter notebook. No dataset download is needed; the notebook uses explicitly synthetic data. Preserve original data. These exercises are not diagnostic software; do not upload identifiable or restricted recordings to public services.

## Student procedure

1. Run the notebook and inspect synthetic_signal.npy and provenance.json.
2. Verify that the checksum of the reloaded array matches the recorded checksum.
3. Change the random seed and explain which provenance fields and outputs change.
4. Propose metadata fields required for a real multimodal EEG acquisition.

## Expected observations (not an answer key for clinical interpretation)

A local outputs/ch04 folder containing synthetic_signal.npy and provenance.json; the checksum assertion succeeds for unchanged data.

## Interpretation questions

1. What exactly is observed or computed, in which units, and from which source?
2. Which choices (sampling, reference, window, noise model, preprocessing, or data structure) can change the result?
3. What conclusion would be scientifically unjustified from this experiment alone?
4. How would another student reproduce the output? Record versions, source, and parameter settings.

## Graduate extension

Write a second integrity check that detects a deliberate one-sample alteration and logs the failed validation without silently overwriting source data.

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
