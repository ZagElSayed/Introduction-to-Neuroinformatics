# Chapter 16 — Classical Machine Learning for Neuroinformatics

Build it wrong, then build it right: compare a deliberately contaminated row split with nested participant-level evaluation. Learn how classical models consume the feature representations from Chapters 12–15, and complete NeuroBridge Phase VIII with a traceable prediction pipeline.

## Data and intended use

The baseline generates **synthetic educational feature vectors**, not EEG or clinical data: 60 artificial participants, six rows each, four physiology-like variables, and artificial identity coordinates. The target is a balanced invented participant label. A weak target-associated feature and stable fingerprints illustrate generalization versus memorization. The row-split comparison is intentionally invalid evidence for unseen participants; the scaler itself is still fit only on training rows. The artificial identity construction is deliberately exaggerated, not a physical model of EEG fingerprints. No download, patient data, or clinical claim is involved.

## Install and run

From the repository root, with Python 3.11 or newer:

```bash
python -m pip install -r requirements.txt
python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config chapters/ch16-classical-ml/config.json --output-dir outputs/ch16
python -m pytest -q tests/test_chapter16_lab.py
python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config outputs/ch16/config.json --output-dir outputs/ch16-reproduced
```

All config keys are required: seed, participants (even, at least 24), repeats (at least two), outer_folds, inner_folds, signal, fingerprint_scale. Fold counts must leave enough participants per class in each training partition. Signal and fingerprint scale are finite nonnegative numbers. Keep the same config, source and dependency versions when reproducing. Record an exact environment lock for long-term reproduction; the repository requirements specify compatible ranges rather than an exact lock. The report records installed versions. Predictions and splits should match in the same environment; serialized model bytes and rendered plots may differ across versions.

## Models, splits and scoring

Compare logistic regression, k-nearest neighbors and a random forest with a prevalence-only dummy baseline. All scaling is in fitted training pipelines. Nested folds stratify **unique participant labels**, then expand participant assignments into row indices; inner folds use only outer-training participants. This explicit splitter assumes one target per participant. A time-varying task target needs a different contract.

Inner grid search optimizes row ROC-AUC, while final evaluation uses **one mean probability per held-out participant** at a fixed 0.5 threshold. Equal repeats give equal row weight to each participant; this does not make rows independent or make row and participant objectives equivalent. Extend inner tuning to participant-level scoring when that matches the scientific objective.

Report accuracy, sensitivity, specificity, precision, F1, ROC-AUC, **average precision** (not trapezoidal PR-AUC) and Brier score. Fold summaries are descriptive, not independent confidence intervals. Pooled out-of-fold predictions come from separate fitted models. Reliability is assessed without fitting a probability calibrator. The naive score uses rows and a different holdout design; compare the information boundaries before directly comparing numerical scores. Removing leakage does not guarantee a decrease for every model, sample or seed.

## Generated derivatives

| Artifact | Meaning |
| --- | --- |
| `config.json` | Complete experiment parameters |
| `split_manifest.json` | Naive row partition and nested row/participant partitions |
| `predictions.csv` | Participant-level out-of-fold probabilities by model |
| `ml_report.json` | Metrics, chosen hyperparameters, versions, source/data/artifact hashes |
| `evaluation.png` | Reliability diagrams and participant ROC-AUC comparison |
| `development_logistic.joblib` | Fixed logistic family tuned and refit on all development observations |
| `model_card.md` | Intended use, feature contract, evaluation and limitations |

The refitted logistic artifact is **not** any individual fold model and has no prospective or external validation. Load only trusted joblib files. Output hashes detect changes, not scientific validity. Keep generated outputs untracked.

## Assignment — 100 points

1. **Target and feature contract (15):** Explain the independent unit, invented target and fingerprint construction. Identify what a clinical or task-based target would require.
2. **Split audit (20):** Inspect inner and outer manifests, verify zero participant overlap, and contrast the naive row split. Explain why a pipeline alone cannot fix an inappropriate split.
3. **Model comparison (20):** Compare three classical families and the dummy baseline, chosen parameters, participant discrimination and threshold errors. Do not choose a winning family from outer results and call its score an unbiased estimate of the selected system.
4. **Probability evidence (15):** Interpret reliability, Brier score and average precision. Explain the sampling prevalence, aggregation rule and why 0.5 is only a teaching threshold.
5. **Sensitivity (15):** Copy the configuration, set `fingerprint_scale` to 0, run to a separate output directory, and compare predictions/metrics. Also vary `signal` or seed. Explain which conclusions are stable and why differences are not clinical effect sizes.
6. **Reproduction and GitHub reflection (15):** Reproduce predictions and splits from saved config. Submit code/config commit, derivative hashes, plots, model card and a short reflection linking upstream NeuroBridge feature provenance. Document software versions and limitations; keep restricted recordings out of Git.

## Graduate extension and public data

Implement participant-level inner scoring; choose model family inside the inner loop; quantify training-procedure uncertainty with a justified design; add participant-blocked permutation or calibration fitted only within training data. For calibration, preserve group boundaries in every calibration partition. Hold the final outer fold untouched by calibration and threshold selection.

Optional real-data source: [PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI [10.13026/C28G6P](https://doi.org/10.13026/C28G6P), distributed under the Open Data Commons Attribution License v1.0 as stated on its release page. Follow release attribution, task/event definitions and acquisition notes. It contains motor tasks, not diagnostic labels. Define run/event selection, epoch boundaries and features before fitting. Use multiple participants and group them at both split levels. Adapt the baseline's one-label-per-person splitter for within-person task labels. Save release version and file hashes. This is an optional extension, not implemented or tested by the baseline.

Method references: [scikit-learn preprocessing pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), [nested CV](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html), and [probability calibration](https://scikit-learn.org/stable/modules/calibration.html). Scientific claims require actual validation beyond this synthetic exercise.
