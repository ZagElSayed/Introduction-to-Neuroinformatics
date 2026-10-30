# Chapter 24 assignment — 100 points

Submit the executed notebook, the new exported bundle directory, and a 1,200–1,800-word translational report. Report the helper version, Python environment, generator seed, cohort size, mapping, thresholds, failures, and limitations. All numerical results must come from your own run.

## 1. Study boundaries — 20 points

Explain participant/site/cohort separation and the simulated prediction/outcome calendar. Inspect subject uniqueness and label availability. Identify what the fixed score represents and why it is not an EEG biomarker. Explain the synthetic groups and the difference between known unsupported inputs and an OOD detector.

## 2. Mapping and policy control — 20 points

Fit the mapping only on eligible calibration records and freeze both supplied thresholds. Compare original, mapped, and development-derived constant outputs. Inspect sparse and empty mapping bins. Explain why changes based on external results require another independent evaluation.

## 3. Metrics and coverage — 20 points

Report counts, coverage, technical rejection reasons, threshold metrics, ROC-AUC, average precision, Brier score, and calibration counts. Compare G1/G2 coverage and conditional performance. Explain undefined values, conditional denominators, and why site-B mapped results are not independent evidence. Show the consequences of both supplied thresholds without labeling one clinically optimal.

## 4. Assumptions and uncertainty — 20 points

Report the scoped bootstrap Brier interval and what it excludes. Show PPV/NPV at prevalences 0.02, 0.10, and 0.30 under fixed test characteristics, plus one likelihood-ratio update. Draw decision curves with the same eligible population under all comparators. Explain the difference between these modeled tradeoffs and measured clinical impact.

## 5. Evidence and clinical interpretation — 20 points

Inspect eligible and insufficient-evidence cards and verify that later outcomes are not in prediction-time exports. Save a unique bundle and receipt, reconstruct one result, and state what the digest does and does not prove. Describe the additional measurement, reference, transportability, human-factors, and impact evidence needed for real use. Propose a feasible next study rather than declaring clinical readiness from the synthetic exercise.

Optional extensions can assess a justified real dataset, fuller calibration uncertainty, censoring, independent external sites, a prospective protocol, or an abstention-aware pathway. They must identify assumptions, lawful/approved access where relevant, and what has actually been implemented. No human intervention or live clinical use is part of this assignment.
