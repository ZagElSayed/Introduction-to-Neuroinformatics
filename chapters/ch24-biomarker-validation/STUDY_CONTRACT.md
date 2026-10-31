# Chapter 24 study contract

Version: `ch24-validation-v1`. This contract describes a synthetic evaluation exercise, not a study of EEG, disease, demographic biology, or clinical benefit.

## Data and time

- Python 3.11+; standard-library helper; default seed 2401.
- One row per synthetic person; 240 rows each in development/site A, calibration/site B, and external/site C (720 total).
- Cohort-specific IDs; no person appears across cohorts. Artificial group labels G1/G2 alternate within each cohort.
- `prediction_day` is an arbitrary simulation calendar: 0+i, 365+i, or 730+i; `outcome_available_day` is prediction day+30. These are not real dates or actual clinical endpoints.
- The helper allows 10–300 people per cohort to retain nonoverlapping cohort calendars with all preceding outcomes available before the next cohort begins.
- Every generated binary outcome is known in the retrospective evaluation table. No censoring or missing reference labels are modeled. Such cases in real data require a separately justified analysis.
- `source_id` refers to synthetic evidence, not a physiological recording.

## Generator

For a generated latent number z, generating risk is `logistic(-0.6 + site_offset + 1.2*z)`, with offsets 0, -0.35, -0.70. A binary outcome is sampled from that risk. The fixed candidate score is `sqrt(risk)`, clipped to [0.01,0.99]. This is a deliberately distorted teaching score, not an EEG predictor or an already validated probability.

The random stream and draw order are part of the helper. Record seed, helper bytes/version, Python version, and cohort size for reproduction. The site change alters the conditional outcome relationship as well as baseline event frequency; it is not pure label shift. The separate prevalence scenario holds sensitivity/specificity fixed by definition.

The quality-acceptance probability is 0.92 in G1 and 0.80 in G2. Supported-input and score-presence probabilities are 0.94 and 0.96. These arbitrary settings create coverage questions; G1/G2 have no demographic interpretation. The support flag is supplied by the fixture, not inferred by an OOD detector.

## Eligibility and calibration

Eligibility priority is missing score, then poor quality, then unsupported input, then eligible. One reason is recorded per person; multiple underlying failed flags can still be inspected in the row. An ineligible result is not a negative classification.

Fit the calibration mapping only on eligible site-B records. Use five equal-width original-score bins, with bin index `min(int(score*5),4)`. A populated bin maps to `(events+1)/(n+2)`; an empty bin uses its midpoint. This smoothed histogram may be nonmonotone and may worsen external performance. Store the mapping and counts. A fixed method version alone is insufficient to identify fitted values; the result card includes a digest of the complete mapping object.

Threshold policies are fixed at 0.25 (`sensitive`) and 0.60 (`selective`), with equality positive. Names describe teaching intentions, not guaranteed comparative sensitivity in every dataset or validated clinical actions. Do not revise the mapping or thresholds using external outcomes and retain a claim that site C is untouched.

## Metrics and uncertainty

- Confusion counts and prediction metrics concern eligible people only; report total count, eligible count, status counts, and coverage beside them.
- Undefined ratios are `None`, serialized as JSON `null`. ROC-AUC is undefined without both outcome classes. Average precision is undefined without positives.
- ROC-AUC uses positive/negative pairs with half credit for ties.
- Average precision groups equal scores and sums precision weighted by recall increments. It is not trapezoidal PR-AUC.
- Brier score is mean squared probability error, not a pure calibration metric. Calibration tables use five equal-width probability bins with counts; empty-bin means are missing.
- Bootstrap Brier intervals resample eligible people at one synthetic site, condition on a fixed fitted mapping, and use nearest-rank 2.5%/97.5% percentiles. They exclude mapping-estimation and between-site uncertainty and do not describe individual risk.
- Net benefit uses `TP/n - FP/n * pt/(1-pt)` among eligible people. All-positive/all-negative comparators use that same population. This does not evaluate the full pathway for ineligible people or measure treatment effects.
- Site-B mapped performance is in-sample for calibration; do not present it as independent validation. Site-C is one external fixture, not proof of transport to real hospitals or an estimate of between-site variation.

## Exports and claims

Prediction cards exclude later outcomes. Evaluation rows retain outcomes separately, and the saved bundle contains both for synthetic assessment. The card supplies a research-only category, technical eligibility, source identity, prediction time, model/preprocessing/mapping/policy identities, and explicit lack of a validated individual interval. It contains no patient-care recommendation.

`save_bundle` creates a new timestamped directory containing JSON and its SHA-256 receipt. The digest supports byte comparison, not authentication, immutability, or clinical validation. The helper performs no network access, clinical integration, model training, or physical action.

The authoring process statically inspected the code and notebook; it did not run the generator, calibration, evaluation, bootstrap, or export. Run and inspect all results yourself. Report environment and failures as well as favorable observations.
