# A practical introduction to ML for medical and neurology students

Use this alongside Chapter 16 and [FIRST_STEPS.md](FIRST_STEPS.md). You do not need prior machine-learning programming experience. You will run an existing experiment, inspect its evidence, change one assumption and write an interpretation. The inputs and targets are invented, so the exercise has no diagnostic or treatment meaning.

**First time coding an ML model?** Start with [FIRST_MODEL.md](FIRST_MODEL.md). Use the environment setup below, run the short `exercise_16_0_first_model.py` instead of the full lab, and return here when its split/fit/predict operations are clear. This guide then introduces the repeated-measures experiment.

## 1. Know what you are building

The script learns to predict an invented binary participant label from synthetic feature rows. Its default data have **60 people, six rows per person and 64 feature columns**. Four features are physiology-like numbers; the other 60 deliberately encode artificial participant identity. This exaggerated construction exposes how recognizing a person can inflate a contaminated test score.

A feature is an available input. A target is what you want to predict. Training learns a rule; validation compares choices during development; test evaluation assesses the frozen procedure on held-out people. Inference applies that fitted procedure to a compatible new input.

The workflow is **Question → Cohort → Features → Split → Model → Evidence**, supported throughout by provenance, leakage control, uncertainty, governance and human oversight.

## 2. Prepare a local environment

Download or clone the student repository, then open a terminal **in its root directory**, the folder containing `chapters/` and `tests/`. Install a compatible Python version if necessary; the course instructions use Python 3.11 or newer. Commands go in the terminal, not inside a Python prompt marked `>>>`.

Choose **one** of the two command sets. These use the virtual environment's interpreter explicitly, so shell activation is not required.

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r chapters/ch16-classical-ml/requirements-lab.txt
.\.venv\Scripts\python.exe chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config chapters/ch16-classical-ml/config.json --output-dir outputs/ch16/med01
```

**macOS or Linux:**

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r chapters/ch16-classical-ml/requirements-lab.txt
.venv/bin/python chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py --config chapters/ch16-classical-ml/config.json --output-dir outputs/ch16/med01
```

The environment command creates an isolated location for packages. The install command supplies this lab's four dependencies. The final command reads the experiment settings and writes results to `outputs/ch16/med01`. It does not download EEG. The repository-wide `requirements.txt` is still available for the whole course.

Use a new output directory. If `med01` already contains files, choose another name instead of deleting earlier evidence. A completed script may return to the terminal without displaying a long score table; inspect the output directory. Runtime success is for you to verify locally. If an error appears, preserve its text and check the repository-root location, interpreter path and dependency installation first.

## 3. Open the evidence, in this order

1. **`model_card.md`:** read intended use and limitations before looking for a high score. It opens in a text editor.
2. **`input_contract.json`:** confirm the row count, feature names, target meaning and artificial identity warning. JSON is structured text; read it in a text editor.
3. **`row_manifest.csv`:** open a copy in a spreadsheet for reading. Count people separately from repeated rows. A row ID is not a new person.
4. **`split_manifest.json`:** check that a participant never appears on both sides of an inner or outer boundary. The default outer test contains 20 people, not 120 independent people.
5. **`predictions.csv`:** read one participant's probability from each model. Each row is a participant-level held-out mean for one family. There are 240 prediction rows because four families evaluate the same 60 participants.
6. **`ml_report.json`:** inspect the model's errors and probability evidence as described below.
7. **`evaluation.png`:** compare the participant ranking summary and reliability plot. Small calibration bins are unstable; their counts appear in the report.

Keep generated originals unchanged; spreadsheet software may rewrite numbers or formatting when saving. The other two files are the saved `config.json` and `development_logistic.joblib`. The latter is a separately refitted development model. You do **not** need to load it to complete this walkthrough, and it is not the model used in any single outer test fold.

## 4. Read a probability before interpreting a class

The chapter's worked logistic rule returns about **0.646** for an invented input. At threshold 0.5 it gives class 1; at threshold 0.7 it gives class 0. Changing the threshold changes the class, not the probability.

Six example held-out window probabilities `(0.4, 0.5, 0.6, 0.6, 0.7, 0.8)` average to `0.6`, the lab's participant-level summary. They are six related observations of one person, not six independent confirmations.

In this exercise, a probability refers to the **invented label**. Do not rewrite it as a person's probability of disease. Such an interpretation would require a real clinical target, relevant sampling and validation, calibration and evidence for the intended use.

## 5. Find the right report fields

Under `nested`, choose `dummy`, `logistic`, `knn` or `forest`, then open `pooled_participant_metrics`.

| Field | Read it as | Ask next |
| --- | --- | --- |
| `confusion` | Counts of true/false positive/negative calls | What kind of mistake was made at the fixed threshold? |
| `sensitivity` | Fraction of positive targets detected | How many positive cases were missed? |
| `specificity` | Fraction of negative targets called negative | How many negative cases received a positive call? |
| `precision` | Fraction of positive calls that were correct | What would prevalence and setting change? |
| `roc_auc` | Ranking of positive versus negative targets | Does this say anything about probability calibration? |
| `average_precision` | A precision–recall ranking summary | Is it being confused with trapezoidal PR-AUC? |
| `brier` | Mean squared probability error | How does it compare with the dummy baseline? |

The threshold is prespecified as 0.5. Smaller Brier error means smaller average probability error on the evaluated examples; it is not a pure calibration score. ROC-AUC does not mean “probability of disease.” `null` means an undefined quantity under the documented convention, not a zero score. The synthetic folds are designed to contain both classes.

Under `reliability`, each model has nonempty-bin counts, mean probabilities and observed positive fractions. Under each model's `folds`, inspect `inner_selection` to see candidate settings and participant-level tuning scores. Inner selection averages fold participant ROC-AUC after averaging rows per person.

`naive_row_knn` is a deliberately contaminated **row-level** experiment with overlapping participants. Its holdout design and evaluation unit differ from the participant-level nested experiment. Compare why the information boundary differs before comparing the numbers directly. Leakage correction does not guarantee that every score decreases for every seed.

## 6. Compare models without choosing an unsupported winner

Make a worksheet with four rows: dummy, logistic, knn and forest. Copy sensitivity, specificity, precision, ROC-AUC, average precision and Brier error. Include false-positive/negative counts and note the fixed threshold. Do not declare a clinically superior model from this toy table.

The dummy model predicts from training prevalence. The logistic model learns a weighted combination. K-nearest neighbors compares the new row with stored training rows. The forest combines many decision trees. All three can use the wrong information if the experiment permits it.

Choosing a winning family using outer test scores is a new selection step. The baseline compares prespecified families; it does not provide an unbiased test of a family selected after seeing those scores.

## 7. Change one assumption deliberately

Copy `chapters/ch16-classical-ml/config.json` to `config_no_identity.json` in the same folder. In a plain text editor, change only:

```json
"fingerprint_scale": 0
```

Keep all other keys and JSON punctuation valid. This zeros the artificial identity coordinates, without removing columns or simulating EEG artifact removal. Run the same command set with `--config chapters/ch16-classical-ml/config_no_identity.json` and `--output-dir outputs/ch16/med02`.

Compare participant predictions, split assignments and the worksheet. State which conclusion about memorization and generalization remains supported. There is no required direction or magnitude of a score change. Do not repeatedly alter settings until the preferred result appears.

## 8. Write six sentences

1. Our target was an invented participant category; the independent evaluation unit was the participant.
2. The default table contained ___ people and ___ repeated rows, with ___ features.
3. Inner and outer partitions protected people from influencing their own evaluation by ___ .
4. At the prespecified threshold, the model made ___ false-positive and ___ false-negative calls; compared with the dummy baseline, ___ .
5. Ranking and probability evidence showed ___, with limitations including ___ .
6. The exercise demonstrates ___ on synthetic data; it does not establish diagnosis, mechanism or patient benefit.

The report remains `review_required` with `accepted: false`. A successful computation documents an experiment; it is not clinical approval.

## Before moving to measured neurodata

Read [REAL_DATA_PROTOCOL.md](REAL_DATA_PROTOCOL.md). Agree the target, timing, eligibility and measurement context with the study team. Preserve participant and session IDs, input permissions and upstream feature provenance. Replace the synthetic generator with a documented extraction process and redesign splitting/aggregation if labels vary within a participant. This baseline accepts synthetic configuration parameters; it does **not** accept an arbitrary patient CSV or automatically process EEG.

CS/IT collaborators help make the schema, code and fitted transformations reproducible. Medical and neurology collaborators help make the target, measurements and interpretation defensible. Both should be able to explain the complete experiment.

## Submit the shared Chapter 16 assignment

Use [ASSIGNMENT.md](ASSIGNMENT.md) for the 100-point rubric and [SUBMISSION_TEMPLATE.md](SUBMISSION_TEMPLATE.md) for the assessed handoff. The six-sentence worksheet above prepares your interpretation; the assignment also requires a split audit, four-family comparison, zero-identity sensitivity run, and reproduction. Inner manifest row IDs map into the original `row_manifest.csv`, not a renumbered outer-training subset. Keep generated outputs local and submit requested evidence through the learning platform.
