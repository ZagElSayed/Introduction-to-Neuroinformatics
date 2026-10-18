# Chapter 16 assignment: a traceable prediction experiment

This is the required synthetic assignment for the book's Chapter 16 hands-on section and NeuroBridge Phase VIII. Medical, neurology, CS, and IT students complete the same work. Use [FIRST_MODEL.md](FIRST_MODEL.md) before [FIRST_STEPS.md](FIRST_STEPS.md); [MED_NEURO_WALKTHROUGH.md](MED_NEURO_WALKTHROUGH.md) supplies environment setup. Run the code locally. These instructions do not assert executed results.

## What is required

Use the supplied generator and the four prespecified families. No EEG download, PCA, missing-value imputation, probability calibrator, family selection, external validation, or clinical-impact study is required. [REAL_DATA_PROTOCOL.md](REAL_DATA_PROTOCOL.md) and the graduate challenge describe additional work.

The default contract is 60 artificial people, six rows per person, and 64 predictors: four invented physiology-like features plus 60 artificial identity coordinates. The target is an invented balanced participant label. The data are not EEG. The 240 prediction rows are 60 people evaluated by four families, not 240 independent people.

## Local run sequence

From the repository root, use your activated environment's Python:

```text
python -m pip install -r chapters/ch16-classical-ml/requirements-lab.txt
python chapters/ch16-classical-ml/exercise_16_0_first_model.py
python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config chapters/ch16-classical-ml/config.json --output-dir outputs/ch16/run01
```

Make a copy of `config.json`, changing **only** `fingerprint_scale` to `0`. Save the copy as `submissions/ch16/student-id/config-no-identity.json` after creating that directory; replace `student-id` with your course identifier. Keep the original seed and other settings fixed.

```text
python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config submissions/ch16/student-id/config-no-identity.json --output-dir outputs/ch16/no-identity
python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config outputs/ch16/run01/config.json --output-dir outputs/ch16/reproduced
```

Replace `student-id` before running a command. Every output directory must be new or empty. The sensitivity run zeros identity columns; it does not delete them or reduce the 64-column schema. It removes no measured EEG artifacts. Compare the saved split manifests as well as predictions and scores. Additional seed or signal changes are optional experiments and should be declared separately.

Optional local verification uses pytest, which is not in the runtime-only requirements:

```text
python -m pip install pytest
python -m pytest -q tests/test_chapter16_lab.py
```

## Rubric: 100 points

| Category | Points | Required evidence |
| --- | ---: | --- |
| Target and feature contract | 15 | Explain `X`, targets, group IDs, independent unit, repeated rows, artificial identity, and requirements for a measured target. Trace one first-model prediction and error category. |
| Split audit | 20 | Show zero participant overlap for each outer and inner partition, and report naive overlap. Explain the information boundary and why a pipeline alone cannot repair it. |
| Model comparison | 20 | Compare dummy, logistic, kNN, and forest participant results and selected settings. Include confusion counts and threshold metrics. Distinguish prespecified comparison from selecting a winning family. |
| Probability evidence | 15 | Interpret Brier, average precision, reliability bin counts, prevalence, aggregation, threshold, and uncertainty limits. Complete the metric checkpoint below. |
| Sensitivity | 15 | Submit the zero-identity configuration and compare its splits, predictions, and metrics with the baseline. Explain changes or their absence without requiring a particular score decrease. |
| Reproduction and handoff | 15 | Compare baseline/reproduced splits and participant predictions; document source, configuration, environment, hashes, model card, and limits. Distinguish fold models from the all-data refit. |

For model comparison, make a table with rows for the four families and columns for accuracy, sensitivity, specificity, precision, F1, ROC-AUC, average precision, and Brier. The threshold is 0.5. Read the metrics from `nested` → family → `pooled_participant_metrics`; outer settings and candidate scores are under that family's `folds`. The separate `naive_row_knn` result scores rows and uses a different holdout design, so its score is not a matched participant-level comparison.

## Audit indices before scores: book subsection 16.18.2

Use `row_manifest.csv` to map each global row ID to its participant. In `split_manifest.json`:

1. For each `outer` record, inspect `train_participants` and `test_participants`; their intersection must be empty.
2. For every `inner` record, map its `train_rows` and `validation_rows` through the original row manifest. These are **global row IDs**, not indices into a locally renumbered development array. Check participant disjointness and exclusion of all outer-test participants.
3. Confirm that outer-test participants together cover all 60 people once. The same split records apply to every prespecified family.
4. Contrast `naive` row membership and `naive_row_knn.overlapping_participants` in the report. An epoch-level split can have different row IDs but shared participants.

Record your audit as a table: outer fold, development people, test people, overlap; then outer fold/inner fold, training people, validation people, inner overlap, overlap with outer test. The default outer counts are 40/20; inner training/validation counts are 26/14, 27/13, and 27/13. Use your saved IDs as evidence rather than merely copying these expected totals.

## Metric checkpoint and evidence limits

For the **separate invented Figure 16.8 example**, compute precision and F1 from TP=18, FN=2, FP=8, TN=72. Expected arithmetic: precision `18/26 ≈ 0.692`, F1 `36/46 ≈ 0.783`.

Assign probability 0.8 to 18 positives and eight negatives, and 0.2 to two positives and 72 negatives. Explain why ROC-AUC is 0.900 while reliability points `(0.2, 2/74)` and `(0.8, 18/26)` are below the equality line. Compute Brier error 0.100 and the constant-0.20 reference error 0.160. These are teaching arithmetic, not outputs expected from the 60-person lab. The four-observation checkpoint has a different Brier value, 0.025. Wilson intervals shown in the book are not calculated by the baseline code.

Describe what each of the four evidence branches in Figure 16.9 asks. The lab demonstrates internal grouped validation only. Silent prospective predictions do not establish benefit from changing care. For Figure 16.10, link the contract, splits, selection, held-out predictions, and evidence package; explain why `development_logistic.joblib` is a separate all-data fit rather than an independently tested final model.

## Submit a readable handoff

Copy [SUBMISSION_TEMPLATE.md](SUBMISSION_TEMPLATE.md) into `submissions/ch16/student-id/report.md`. Commit the authored report, comparison/audit tables, original and sensitivity configurations, source commit ID, and any code you intentionally changed. Record `source_sha256`, software versions, run IDs, configuration hashes, and artifact hashes from the report. For this synthetic baseline, the upstream source is the generator and seed, **not** EEG recordings.

Keep `outputs/` untracked. Submit requested plots, model card, and report/manifests as learning-platform attachments rather than committing generated run directories. Retain all nine generated artifacts locally. Do not upload the joblib model or recordings. `ml_report.json` hashes its eight companion artifacts and excludes itself; document the serialized-model hash without uploading that model. Run UUIDs and timestamps should change across reproductions; compare splits and participant predictions in a matching environment. Do not require whole-report byte equality or promise identical model bytes across dependency versions.

Every run remains `review_required` with `accepted: false`. Do not change these fields to imply clinical authorization.

## Figures mapped to the assignment

| Book figure | Apply it here |
| --- | --- |
| 16.1 | Question → cohort → features → split → model → evidence |
| 16.2 | Explain shortcuts and site–target confounding |
| 16.3 | Separate predictors, targets, and grouping metadata |
| 16.4 | Trace score, probability, threshold, and class |
| 16.5 | Explain candidate hyperparameters and protected selection |
| 16.6 | Audit participant separation |
| 16.7 | Trace inner tuning, outer refit, and held-out scoring |
| 16.8 | Interpret errors, ranking, probabilities, and uncertainty |
| 16.9 | Bound the evidence claim to internal validation |
| 16.10 | Package the procedure with provenance and review limits |
