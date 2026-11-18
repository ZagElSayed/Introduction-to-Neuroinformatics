# Chapter 24 execution review

Reviewed 17 November 2026. This record concerns the default synthetic teaching fixture, not real physiology or clinical validity.

## What ran

- Python 3.12.14, Matplotlib 3.10.8, scikit-learn 1.8.0 on Linux.
- All eight unmodified notebook code cells were executed in order in one isolated Python process, with Matplotlib's noninteractive Agg backend. The helper was copied beside the notebook code before import. No patient data, network service, or GPU was used.
- This exercised generation, split/calendar assertions, calibration, both fixed policies, the development-derived constant baseline, diagrams, subgroup coverage, prevalence calculations, all 19 decision-curve thresholds, the 400-repeat bootstrap, research cards, and bundle export.
- The source notebook retains empty outputs and execution counts. This run does not establish browser rendering, Jupyter-kernel behavior, or Colab compatibility.
- Seven regression tests in `tests/test_chapter24_lab.py` passed. They cover known confusion counts and denominator handling, abstentions, tied/undefined metrics, a prevalence example, disjoint people/calendar boundaries, calibration-only fitting, prediction-time exclusion of future outcomes, deterministic fixed-mapping bootstrap, and nonoverwriting bundle/digest checks.
- The complete companion suite passed: 121 tests and 8 subtests. Its pre-existing EDF notebook fixtures remain synthetic.

## Observed default-fixture results

Seed 2401; 240 generated people in each of development, calibration, and external evaluation. Calibration-bin eligible counts: [4, 50, 65, 45, 19].

External cohort: 240 people, 183 eligible, coverage 0.7625. Gate reasons: 36 poor quality, 8 unsupported input, and 13 missing score. These are mutually exclusive recorded reasons under the stated priority, not independent prevalence estimates of all underlying failures.

| Frozen mapped-score policy | TP | FP | FN | TN |
| --- | ---: | ---: | ---: | ---: |
| 0.25, equality positive | 53 | 67 | 4 | 59 |
| 0.60, equality positive | 10 | 2 | 47 | 124 |

For the mapped external score: ROC-AUC 0.806112503, grouped-tie average precision 0.603875467, and Brier score 0.158675235. All three agree with independent scikit-learn implementations to absolute difference below 1e-12. At threshold 0.25, eligible-record net benefit is 0.167577413; the all-positive comparator is 0.081967213. These are decision-model quantities under the stated weighting, not patient-benefit percentages or observed treatment effects.

The fixed-mapping eligible-subject Brier bootstrap returned [0.132386797, 0.185588534] using 400 resamples. This interval excludes calibration-fit and between-site uncertainty and is not an individual risk interval.

## Scientific clarification

The site offset changes conditional risk given the latent z, score distributions, and event frequency. Away from clipping, the generating event probability remains score squared at every site. The exercise therefore does not inject site-specific drift in the original score-to-risk relationship. Finite-sample histogram mappings may still behave differently across sites. Distinguish this from both pure label shift and a genuinely changing conditional outcome relationship at the same score.

## Source identities

- Helper SHA-256: `8551d43ac505199103da681fb451f3420e90b3f3bef0c81aa71d06adeedb1353`.
- Notebook SHA-256: `2cc3e61ca82bfecd95f159324a7e77a18e190ad56cc43a2f43cb93f814877c62`.

These hashes identify the bytes exercised; they do not authenticate clinical data or establish scientific validity. The helper's only change in this pass is its documentation of execution coverage. No scoring, calibration, metric, or export algorithm was changed.
