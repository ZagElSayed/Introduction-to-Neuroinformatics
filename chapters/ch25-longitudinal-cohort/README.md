# Chapter 25: a disorder-aware longitudinal cohort

Build an inspectable research cohort before trusting a predictor. This studio links normalized records, time-aware feature selection, participant/site/time boundaries, missing MRI, transparent models, and research evidence cards.

Start with [STUDY_CONTRACT.md](STUDY_CONTRACT.md), open [01_longitudinal_cohort_studio.ipynb](01_longitudinal_cohort_studio.ipynb), and follow [ASSIGNMENT.md](ASSIGNMENT.md). The helper is `cohort_studio.py`, version `ch25-cohort-v1`.

## Setup

Use Python 3.11 or newer with its standard-library `sqlite3` module. The core requires no external packages, patient data, EEG files, API key, cloud account, or EHR connection. For the notebook and optional plots:

```bash
python -m venv .venv
# Activate the environment for your operating system.
python -m pip install -r requirements-notebooks.txt
python -m jupyterlab
```

Run the notebook from this folder so it can import the adjacent helper. Cells are saved without outputs. Materials were inspected statically; no helper functions or notebook cells were executed during authoring. Students must run them and report their own results or errors. No performance outcome is promised.

## What you build

The default fixture has 240 invented participants: 80 development/site A, 80 calibration/site B, and 80 external/site C. Every participant has history, recent, and index encounters. SQLite separates people, encounters, acquisitions, derivatives, medications, and outcomes. Observation time and availability time differ deliberately.

The cohort uses one index per person and a 45-day lookback. It selects the latest eligible EEG-derived toy value and an optional MRI-derived toy value using both clocks. It excludes a future EEG value that was deliberately made highly predictive of the label, and it rejects an MRI interpretation that was acquired before index but available afterward. These are fabricated numbers, not signal processing.

Eligible records have a usable required neural feature. Missing MRI is retained with a reason. All generated medication entries are recorded after index and are therefore unavailable in the as-of context, even though their nominal start is earlier. Site and device are perfectly linked fixture properties; device differences cannot be identified separately from site with these records.

Two ridge logistic teaching models use development records only. The basic model uses age and the latest neural feature. The multimodal model adds MRI and a missingness indicator. Imputation means and feature scaling are fitted only on development data. Model outputs are candidate probabilities whose calibration and clinical validity are not guaranteed. These are prediction models, not causal or treatment-selection models.

The calibration cohort is used for descriptive inspection without changing the models or cutoff. No recalibration is fitted in this studio. The external fixture evaluates the prespecified models and a declared missing-MRI stress test. Reusing those outcomes to redesign a model would require further evaluation; the original fixture would no longer be untouched confirmation.

## Outputs to interpret

- Eligible and excluded counts, with MRI missingness by site and artificial group.
- ROC-AUC with half credit for ties; undefined AUC is `None` when one outcome class is absent.
- Brier score, fixed-0.50 confusion counts, sensitivity, specificity, PPV/NPV, and five-bin calibration counts. Undefined ratios and empty-bin values are `None`.
- Complete-case descriptive comparisons and a deliberate imaging-removal stress test. Keep denominators explicit.
- Research cards with source times, device and recipe identities, model identity, missingness, and uncertainty limitations. Cards contain no future outcome label.
- A new timestamped bundle with SQL fixture, cohort, references, model configurations, summaries, research cards, and SHA-256 receipts. Receipts support byte comparison; they are not authentication or immutable storage.

The experiment demonstrates cohort and evaluation mechanics. It does not validate a disease biomarker, process EEG, perform clinical harmonization, connect to an EHR, handle censoring, estimate treatment effects, or evaluate clinical impact. Continue to Chapter 26 only with those boundaries clear.
