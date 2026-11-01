# Assignment: build and defend a point-in-time cohort (100 points)

Run the guided notebook yourself. Submit the executed notebook, new export bundle, and a concise scientific report. Report actual results and errors; authoring inspection did not execute the helper or notebook. Do not invent expected performance.

## A. Clinical question and normalized record — 20 points

Explain the study contract and its synthetic scope. Diagram or describe the entity relationships. Distinguish observation, availability, index, and outcome times. Explain why the 90-day toy event does not establish a neurological endpoint or treatment-response model. Describe one real clinical question that would require a different reference and study plan.

## B. Cohort and leakage audit — 20 points

Verify one index/person and selected input availability. Inspect a future neural derivative, a late MRI result, and a late-documented medication. Explain why an acquisition date alone is insufficient. Report eligibility and missingness by site and artificial group. Compare a naive latest-record query with the permitted as-of view; do not use the leakage trap to claim clinical predictive performance.

## C. Transparent fitting and partition boundaries — 20 points

Show disjoint people and the development/calibration/external calendar. Document which data determine preprocessing and weights. Fit the basic and multimodal candidates using eligible development records only. Inspect the calibration cohort without revising either model. Explain the limits of fixed optimization choices, site/device/period confounding, and uncalibrated candidate probabilities.

## D. Evaluation and robustness — 20 points

Report counts, coverage, ROC-AUC, Brier, calibration-bin counts, and fixed-threshold errors. Keep undefined values explicit. Compare complete-case descriptions and an MRI-removal stress test using appropriate denominators. Explain why the stress test does not reproduce every clinical missingness mechanism and why no displayed metric establishes treatment benefit. State that uncertainty intervals are not implemented.

## E. Evidence and reproducibility — 20 points

Inspect eligible and insufficient-evidence research cards. Verify that future outcomes are absent from cards but present in the separate reference export. Export SQL, cohort, models, summaries, cards, and receipts. Explain what the hashes can and cannot establish. Propose the measurement, reference, population, interface, and impact evidence that a real NeuroBridge Phase XVII application would still require.

## Optional extensions

Implement candidate calibration on the reserved cohort and evaluate it on new independent synthetic data; add multiple index encounters with a justified split; or evaluate event-level detection in a separate synthetic stream. Label revised questions, data boundaries, and limitations explicitly. Do not connect real clinical records or fabricate validated clinical claims from this exercise.
