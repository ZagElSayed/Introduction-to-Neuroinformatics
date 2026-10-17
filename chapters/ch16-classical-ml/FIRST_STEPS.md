# Chapter 16 — first steps from features to a trustworthy prediction

This guide accompanies the chapter's calculations. All numbers in the script are synthetic. Medical, neurology, CS and IT students complete the same computations and split audit.

## 1. Describe the experiment before fitting

A target is what you want to predict; a feature is an input available at prediction time. A label is the recorded target value. In this lab, labels are invented binary participant labels. They are not diagnoses. Real clinical labels need assignment criteria, timing, eligibility and uncertainty; motor-task labels need event definitions.

The default table has 60 participants × 6 repeats = **360 rows** and 4 + 60 = **64 features**. Four columns are invented physiology-like variables. Sixty columns form an exaggerated one-hot identity basis. These identifiers are a deliberate memorization trap, not a deployable feature schema. The participant group vector is separately retained for splitting and aggregation.

## 2. Check a prediction by hand

For standardized features `(0.5, -1)`, weights `(0.8, -0.4)` and intercept `-0.2`, the score is `0.6`. Logistic probability is `1 / (1 + exp(-0.6)) ≈ 0.646`.

- A fixed threshold of 0.5 assigns class 1; a threshold of 0.7 assigns class 0.
- The probability does not change when the threshold changes.
- Training means and standard deviations must be reused for held-out inputs. Training mean 10 and SD 2 turn held-out value 14 into `(14 - 10) / 2 = 2`.
- Interpreting a coefficient requires its scaling and other predictors. It is not automatically a causal effect.

## 3. Follow one outer fold

Three outer folds each hold out 20 participants (120 rows). Development uses the other 40 participants (240 rows). Inner validation partitions those 40 into groups of 14, 13 and 13 people. All six repeats from a person stay together at both levels.

For each parameter candidate:

1. Fit the pipeline on inner-training rows only.
2. Predict inner-validation rows, then average probabilities within each participant.
3. Compute participant ROC-AUC for the inner fold; average these fold scores.
4. Pick the highest mean score; exact ties retain the first `ParameterGrid` setting.
5. Refit that setting on all outer-training rows and predict the untouched outer-test participants.

The explicit `select_parameters` helper implements this order. The report preserves candidate-level inner scores. Neither tuning nor scaling uses the outer-test people. The dummy prevalence baseline passes through the same participant scoring, but has no parameter choices.

After all outer folds, each model has one out-of-fold prediction per participant. Four prespecified families × 60 people = **240 prediction rows**. The naive row-split score is saved separately; it has a different evaluation unit and cannot be compared as if the only difference were model quality. High scores are not guaranteed to decrease for every seed after correcting leakage.

## 4. Read the outputs in order

| Open | Ask |
| --- | --- |
| `input_contract.json` | What do the feature columns, shape, target and participant IDs mean? |
| `row_manifest.csv` | Which participant and target belong to each row ID? |
| `split_manifest.json` | Does any person cross a training/validation or training/test boundary? Inner indices are saved as global row IDs. |
| `predictions.csv` | Is each model's probability one participant-level mean from held-out data? |
| `ml_report.json` | What was tuned, which metric selected it, and what are the resulting errors and limitations? |
| `evaluation.png` | Are rankings and probabilities telling different stories? How sparse are the calibration bins? Their counts and plotted coordinates are also saved under `reliability` in the report. |
| `model_card.md` | What was implemented and what remains unvalidated? |

`config.json` records the parameters. `development_logistic.joblib` is the logistic family retuned and refitted on **all** development participants. It is not an outer-fold model and has no separate external performance estimate. Load only trusted model files.

## 5. Work through the metric examples

For TP = 18, FN = 2, FP = 8 and TN = 72:

- Accuracy = 90/100 = 0.90.
- Sensitivity = 18/20 = 0.90; specificity = 72/80 = 0.90.
- Precision = 18/26 ≈ 0.692; F1 = 36/46 ≈ 0.783.

For targets `(0, 0, 1, 1)` and probabilities `(0.1, 0.2, 0.8, 0.9)`, Brier score is 0.025. These examples are arithmetic, not clinical evidence. Average precision is reported separately from trapezoidal PR-AUC. Single-class ROC-AUC is `null`; sensitivity/specificity with no relevant class are `null`. Precision and F1 explicitly use zero for undefined ratios in the teaching report.

## 6. Reproduce without overwriting

Use the README commands and a new directory for each run. Preserve the saved configuration and match the source and dependency versions. Compare splits and participant predictions; UUIDs and timestamps are expected to differ. Identical numerical outputs can have identical artifact hashes. The report excludes itself from its artifact hash list.

Every completed run remains `review_required` with `accepted: false`. A manifest documents the computation; it does not make a synthetic model a clinical system.

## Explain it in both languages

**CS/IT:** Explain the matrix dimensions, schema, grouping, training-only transformations, deterministic tie rule and saved fitted objects.

**Medical/neurology:** Explain the invented label, independence unit, measurement context, error consequences and why a well-ranked prediction is not automatically calibrated or clinically useful.

Then exchange explanations. A complete handoff needs both.
