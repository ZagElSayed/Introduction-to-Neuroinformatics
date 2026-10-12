# Chapter 14 — Neural Source Localization and Inverse Modeling

**Status: runnable synthetic inverse-problem laboratory.** This small example uses a 2-sensor by 3-source lead-field matrix, ridge/Tikhonov regularization, and an intentionally perturbed gain matrix to illustrate nonuniqueness, parameter sensitivity, and the distinction between sensor residuals and source accuracy.

The matrix is a **mathematical teaching model**. It is not an anatomically valid EEG/MEG head model, and the perturbation is **not** equivalent to a measured sensor displacement in millimeters.

## Run from the student repository root

```bash
python chapters/ch14-source-localization/exercise_14_1_inverse_sensitivity.py --output-dir outputs/ch14
python -m pytest -q tests/test_chapter14_lab.py
```

Outputs: `inverse_sensitivity.csv` and `source_inverse_report.json`.

## Student assignment (100 points)

1. **Forward model (15):** Explain the meaning and dimensions of the lead field, source vector, and sensor observation. Identify why three source amplitudes cannot generally be uniquely recovered from two sensor measurements.
2. **Inverse and regularization (20):** Compare estimated source amplitudes and residuals for three positive regularization strengths. Explain the tradeoff between fit and shrinkage.
3. **Model uncertainty (20):** Compare nominal and perturbed lead fields. Explain why a low sensor residual does not prove a correct anatomical location.
4. **Quality assurance (15):** Propose geometry, MRI segmentation, noise-covariance, whitening, and forward-model checks needed before interpreting real EEG/MEG source maps.
5. **Reproducibility (15):** Record output checksum, assumptions, input matrices, solver, parameter settings, and evidence needed to reproduce the estimate.
6. **Scientific interpretation (15):** Write a short report separating synthetic mathematical demonstration, physiological inference, and clinical claims.

**Deliverables:** CSV and JSON outputs, one comparison plot, a forward/inverse diagram, and a 1–2-page interpretation.

**Advanced MNE-Python extension:** With a licensed sample EEG/MEG dataset and compatible anatomical information, inspect coregistration, source space, BEM/FEM model, noise covariance, forward solution, inverse operator, residuals, and sensitivity to a documented geometry perturbation. Do not claim the toy matrix quantifies realistic millimeter localization error.

**Limitations:** No anatomical segmentation, realistic volume conduction, physical coordinate transforms, MEG forward physics, uncertainty intervals, or clinical validation is implemented in the baseline script.
