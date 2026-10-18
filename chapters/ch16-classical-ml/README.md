# Chapter 16 — Classical Machine Learning for Neuroinformatics

Build it wrong, then build it right: compare a deliberately contaminated row split with nested participant-level evaluation. Learn how classical models consume the feature representations from Chapters 12–15, and complete NeuroBridge Phase VIII with a traceable prediction pipeline.

Start with **[FIRST_STEPS.md](FIRST_STEPS.md)** for the shared CS/IT and medical/neurology walkthrough, worked predictions, fold arithmetic and output-reading order. The advanced measured-data extension is separated in **[REAL_DATA_PROTOCOL.md](REAL_DATA_PROTOCOL.md)**.

**New to ML or programming?** Follow **[MED_NEURO_WALKTHROUGH.md](MED_NEURO_WALKTHROUGH.md)** for Windows/macOS/Linux setup, output reading, model comparison and a medical/neurology interpretation worksheet. `requirements-lab.txt` provides just this lab's runtime dependencies; the full-course requirements below are also supported.

## Start with an easy coding lesson

For a first implementation, use **[FIRST_MODEL.md](FIRST_MODEL.md)** and run `exercise_16_0_first_model.py`. It uses one row per artificial person and prints predictions, error counts and a dummy-baseline comparison. Its six commented blocks teach table → split → pipeline → fit → predict → inspect. Then proceed to the full repeated-measures lab below. The introductory script writes no artifacts and does not tune hyperparameters.

## Data and intended use

The baseline generates **synthetic educational feature vectors**, not EEG or clinical data: 60 artificial participants, six rows each, four physiology-like variables, and artificial identity coordinates. The target is a balanced invented participant label. A weak target-associated feature and stable fingerprints illustrate generalization versus memorization. The row-split comparison is intentionally invalid evidence for unseen participants; the scaler itself is still fit only on training rows. The artificial identity construction is deliberately exaggerated, not a physical model of EEG fingerprints. No download, patient data, or clinical claim is involved.

## Install and run

From the repository root, with Python 3.11 or newer:

```bash
python -m pip install -r chapters/ch16-classical-ml/requirements-lab.txt
python -m pip install pytest
python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config chapters/ch16-classical-ml/config.json --output-dir outputs/ch16/run01
python -m pytest -q tests/test_chapter16_lab.py
python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config outputs/ch16/run01/config.json --output-dir outputs/ch16/run02
```

Use a **new or empty output directory**. A populated directory is rejected before fitting, preserving earlier evidence. Tests are provided for local execution; no executed outcome is asserted here.

All config keys are required: seed, participants (even, at least 24), repeats (at least two), outer_folds, inner_folds, signal, fingerprint_scale. Fold counts must leave enough participants per class in each training partition. Signal and fingerprint scale are finite nonnegative numbers. Keep the same config, source and dependency versions when reproducing. Record an exact environment lock for long-term reproduction; the repository requirements specify compatible ranges rather than an exact lock. The report records installed versions. Predictions and splits should match in the same environment; serialized model bytes and rendered plots may differ across versions.

## Models, splits and scoring

Compare logistic regression, k-nearest neighbors and a random forest with a prevalence-only dummy baseline. All scaling is in fitted training pipelines. Nested folds stratify **unique participant labels**, then expand participant assignments into row indices; inner folds use only outer-training participants. This explicit splitter assumes one target per participant. A time-varying task target needs a different contract.

Inner tuning and final evaluation both use **participant-level predictions**. For every candidate, fit on inner-training rows, average held-out probabilities within each validation participant, calculate ROC-AUC in each inner fold, and maximize the mean of those fold scores. The explicit `select_parameters` loop records each candidate's scores and chosen parameters. Exact score ties retain the first candidate in deterministic `ParameterGrid` order. This is not pooled row AUC or pooled participant AUC. Final decisions use one mean probability per held-out participant and a prespecified 0.5 threshold.

The default outer test has 20 participants / 120 rows and its training set has 40 participants / 240 rows. Inner validation sets contain 14, 13 and 13 participants. Equal repeat counts give equal training row weight to participants but do not make rows independent. Four prespecified model families yield 240 participant prediction rows across the complete outer evaluation. Model-family selection is not part of the baseline.

Report accuracy, sensitivity, specificity, precision, F1, confusion counts, ROC-AUC, **average precision** (not trapezoidal PR-AUC) and Brier score. Fold summaries are descriptive, not independent confidence intervals. Pooled out-of-fold predictions come from separate fitted models. Reliability is assessed without fitting a probability calibrator. The report saves each nonempty calibration bin’s count, mean probability and observed positive fraction; requested bins are uniform and empty bins are omitted. The naive score uses rows and a different holdout design; compare the information boundaries before directly comparing numerical scores. Removing leakage does not guarantee a decrease for every model, sample or seed.

Undefined single-class ROC-AUC is `null`; sensitivity/specificity without the corresponding class are `null`. Average precision is `null` with no positives. Precision and F1 explicitly use `zero_division=0`. The generated folds themselves contain both classes by design.

## Generated derivatives

| Artifact | Meaning |
| --- | --- |
| `config.json` | Complete experiment parameters |
| `input_contract.json` | Feature names, dimensions, dtype, target/group semantics and artificial identity warning |
| `row_manifest.csv` | Row IDs linked to participant IDs and targets |
| `split_manifest.json` | Naive row partition and nested row/participant partitions |
| `predictions.csv` | Participant-level out-of-fold probabilities by model |
| `ml_report.json` | Metrics, inner candidate scores, chosen parameters, versions, run UUID/time, source/config/data/artifact hashes and pending-review status |
| `evaluation.png` | Reliability diagrams and participant ROC-AUC comparison |
| `development_logistic.joblib` | Fixed logistic family tuned and refit on all development observations |
| `model_card.md` | Intended use, feature contract, evaluation and limitations |

The refitted logistic artifact is **not** any individual fold model and has no prospective or external validation. Load only trusted joblib files. Output hashes detect changes, not scientific validity. Keep generated outputs untracked. Each completed run records `review_required` and `accepted: false`. The report hashes the other eight files, excluding itself. Compare predictions/splits in a matching environment; UUIDs and timestamps intentionally change.

## Assignment — 100 points

Use **[ASSIGNMENT.md](ASSIGNMENT.md)** as the shared book/repository submission contract and copy **[SUBMISSION_TEMPLATE.md](SUBMISSION_TEMPLATE.md)** for your report. It specifies the six rubric categories, three required runs (baseline, zero-identity sensitivity, reproduction), global-index split audit, figure checkpoints, evidence attachments, and what to commit. Additional seed/signal experiments and measured-data work are optional.

The baseline zeros identity columns when `fingerprint_scale=0`; its 64-column default schema is retained. No empirical performance decrease is guaranteed.

## Graduate extension and public data

Audit the implemented participant-level inner scoring; extend the search to choose model family inside the inner loop; quantify training-procedure uncertainty with a justified design; add participant-blocked permutation or calibration fitted only within training data. For calibration, preserve group boundaries in every calibration partition. Hold the final outer fold untouched by calibration and threshold selection.

Optional real-data source: [PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI [10.13026/C28G6P](https://doi.org/10.13026/C28G6P), distributed under the Open Data Commons Attribution License v1.0 as stated on its release page. Follow release attribution, task/event definitions and acquisition notes. It contains motor tasks, not diagnostic labels. Define run/event selection, epoch boundaries and features before fitting. Use multiple participants and group them at both split levels. Adapt the baseline's one-label-per-person splitter for within-person task labels. Save release version and file hashes. This is an optional extension, not implemented or tested by the baseline.

Updated reporting/appraisal sources: [TRIPOD+AI (2024)](https://doi.org/10.1136/bmj-2023-078378) and [PROBAST+AI (2025)](https://doi.org/10.1136/bmj-2024-082505). They help describe and assess evidence, not certify clinical readiness.

Method references: [scikit-learn preprocessing pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), [nested CV](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html), and [probability calibration](https://scikit-learn.org/stable/modules/calibration.html). Scientific claims require actual validation beyond this synthetic exercise.



## Source verification and execution

The Chapter 16 GitHub workflow performs static Python syntax/JSON and required-file checks only. It does not import the lab, fit models, run pytest, or execute assignments. Run the optional runtime tests locally using the commands above; no runtime result is asserted by a static check.
