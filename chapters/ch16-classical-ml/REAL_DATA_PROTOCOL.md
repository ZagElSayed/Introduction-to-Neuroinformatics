# Chapter 16 — protocol for extending the synthetic lab to measured data

This is proposed additional work, not functionality supplied by the baseline. Agree the target and information boundary before extracting features.

## Choose an honest target

The optional source is [PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), [DOI 10.13026/C28G6P](https://doi.org/10.13026/C28G6P). Follow its release license, attribution, event definitions and acquisition notes. The release describes motor tasks, not diagnoses.

Choose a clearly documented task comparison and compatible runs across multiple participants. Define how each event annotation becomes a label, which intervals are included, what happens at boundaries and which observations are excluded. Preserve participant IDs, run IDs, release version and source-file hashes. A baseline eyes-open recording alone does not supply a motor-task comparison.

Task targets vary within a participant. **Replace the baseline's one-target-per-person splitter and aggregation rule.** Group participants at both levels, while defining a task-appropriate evaluation unit and class balance. Averaging all probabilities for a person with multiple task labels would erase the target distinction. Do not relabel the task as disease or reuse the synthetic identity columns.

## Freeze feature and split contracts

1. Record recording state, channels, reference, sampling, preprocessing, event timing, epoch construction and feature definitions.
2. Decide the target population: unseen people, new visits of known people, or new sites require different validation boundaries.
3. Keep all related epochs and repeated sessions from a participant together for unseen-person evaluation; add family/site constraints where relevant.
4. Distinguish prespecified processing applied independently to a recording from transformations learned across recordings. Fit all cross-participant imputation, scaling, selection, PCA, tuning, calibration and threshold choice inside the appropriate training boundary.
5. Check labels and feature availability at the intended prediction time. Do not use future measurements to support a prospective claim.

The original lab has finite data and no missing values; imputation, feature selection, calibration fitting and real EEG extraction are **not** implemented there. Adding them requires explicit training-only pipelines and local verification.

## Evaluate a procedure, not a selected score

Begin with dummy and simple feature baselines. If choosing model family or representations, include that selection in the inner procedure or use a separate untouched evaluation cohort. Assess operating-point errors, ranking, calibration where probabilities are used, relevant subgroups and acquisition shortcuts. ROC-AUC requires both classes in the evaluated set. Report undefined quantities rather than inventing values.

Use participant-respecting uncertainty and permutation designs. Fold standard deviations are not independent confidence intervals. A site-only baseline can reveal confounding, but if target and site are perfectly confounded, no algorithm or site split can recover absent site-by-target combinations; redesign recruitment.

## Save the evidence chain

Keep cohort and feature contracts, row/label/group manifests, both split levels, fitted transformations, model-selection details, predictions, metric definitions, QC, software identity, hashes and a model card. Preserve earlier runs. State what was actually computed and what remains unvalidated. Computational reproducibility, external generalization, biological explanation and decision benefit are separate claims.

Read the primary method sources linked in the README and the book's TRIPOD+AI / PROBAST+AI references. Reporting and appraisal tools help others assess evidence; they do not substitute for it.
