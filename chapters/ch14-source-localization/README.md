# Chapter 14 — Source Localization and Spatial Modeling

Explain **why a good sensor fit can coexist with a wrong or nonunique source estimate**. This standard-library lab uses two synthetic sensors and three signed candidate-source amplitudes. Every number is dimensionless; source indices are labels, not anatomical coordinates.

## Run locally from the student repository root

```bash
python chapters/ch14-source-localization/exercise_14_1_inverse_sensitivity.py --output-dir outputs/ch14/run01
python -m pytest -q tests/test_chapter14_lab.py
```

Choose a new or empty directory for each run. Existing nonempty directories are refused. Runtime and numerical results must be confirmed by local execution. The source checks performed during editing do not establish that these tests pass.

## CS/IT reading guide — Section 14.1 and Figure 14.1

The chapter distinguishes observed channel arrays from model-dependent source arrays. Use the toy lab to make that distinction concrete:

- `y` contains two sensor measurements; `j` contains three signed candidate amplitudes. A source index is an identifier in a model, not a brain-region label or a distance.
- Rows of `G` correspond to sensor channels and columns to candidate source amplitudes. Its links represent sensitivities/weights, not neural pathways. Array ordering must agree with those identities.
- The forward operation predicts sensors from a specified source vector. The inverse uses measurements and an explicit penalty to select an estimate; it is not an ordinary reversal of `G`.
- The two vectors in `nonunique_sources.csv` show that extra source-array entries do not add measured information. Read the chapter's worked null-space example before interpreting a good residual.
- The lab is dimensionless. Real EEG/MEG workflows additionally require measurement units, reference, coordinate frames, anatomy and orientation/normalization metadata; use `REAL_SOURCE_PROTOCOL.md` for that extension.
- ICA components, inferred anatomical sources and connectivity edges are different objects. This exercise implements only the declared toy forward/inverse problem.

## Experiment 1 — Two source vectors, one measurement

The nominal gain matrix is `G = [[1, .4, .1], [.2, .8, .4]]`; the known source is `[1, 0, 0]`, giving sensors `[1, .2]`. The nonzero vector `n = [.08, -.38, .72]` satisfies `G n = 0`. Consequently `[1, 0, 0]` and `[1.08, -.38, .72]` produce the same measurement, within floating-point rounding. In fact, `j + a*n` does so for any real scalar `a`.

This is a direct demonstration of nonuniqueness. Negative source coefficients represent signed amplitude, not negative power. No sensor noise is required for ambiguity, and no numerical optimizer can discover which null-space component is true from these observations alone.

## Experiment 2 — Regularization, model error and a fixed sensor perturbation

The script minimizes `||y-Gj||² + lambda*||j||²` using the dual expression `Gᵀ (G Gᵀ + lambda I)⁻¹ y`, implemented by solving the small sensor-space system. Noise and source weights are identity matrices. The coefficient multiplies the squared source norm directly; it is not automatically equivalent to another package's `lambda2`, SNR or covariance-loading setting.

Compare three coefficients (`.01`, `.1`, `1`) across two assumed gains (nominal and altered) and two observations (noiseless and with fixed additive vector `[.02, -.01]`). This gives **12 rows**. The altered gain is `[[.85, .50, .15], [.28, .72, .45]]`; it is an illustrative model mismatch, not a simulated 5-mm electrode displacement. The one fixed sensor perturbation does not estimate stochastic variance or a confidence interval.

Keep three diagnostics separate:

| Diagnostic | Definition and interpretation |
|---|---|
| Sensor residual | `||G_assumed*j_est-y_observed||`; agreement under the assumed model |
| Source error | `||j_est-j_true||`; available here only because simulation truth is known |
| Source norm | `||j_est||`; measures shrinkage favored by the penalty |

The reported peak is the largest **absolute** source coefficient, indexed from 1. It is neither a cortical coordinate nor proof of correct source recovery. Study the complete vector, not only its peak label.

## Experiment 3 — Resolution and cross-talk

The inverse operator `K` maps sensors to estimated sources. With a matched model, `R = K G` describes how a true source vector is mixed into its estimate, ignoring additive noise. Columns are point-spread functions; rows are cross-talk functions. Identity resolution would recover each basis source without attenuation or mixing, which this rank-limited model cannot achieve for all three sources.

For each model/coefficient, the script stores both `K*G_assumed` and `K*G_true`. The second is the effective mapping under this controlled model mismatch. With real EEG/MEG, the exact true gain is unknown; an assumed-model resolution matrix does not automatically quantify errors in anatomy, geometry or conductivity. Matrix coefficients are signed gains, not probabilities or anatomical error distances.

## Saved evidence

| Artifact | Contents |
|---|---|
| `inverse_sensitivity.csv` | 12 estimates, sensor residuals, source errors, norms and peak indices |
| `nonunique_sources.csv` | Two different source vectors and their common sensor measurements |
| `resolution_matrices.json` | Inverse operators, assumed-model resolution and true-gain effective resolution for six settings |
| `inverse_diagnostics.svg` | Nominal/noiseless source curves and signed resolution coefficients at lambda `.1` |
| `source_inverse_report.json` | Run/config/code identities, truth, assumptions, output hashes and review state |

The status remains `review_required` and acceptance remains false. The SVG source axis is categorical; its connecting lines do not describe anatomical adjacency. The heatmap prints coefficients explicitly; teal denotes positive and coral negative values, with intensity proportional to absolute value and capped at 1. Source indices on rows denote estimates; columns denote generating sources.

## Assignment — 100 points

1. **Forward model and ambiguity (20):** State all dimensions, verify the two sensor observations and null vector by hand, and explain the infinitely many equivalent source vectors.
2. **Regularization (20):** Compare residual and source norm across coefficients. Relate the chosen solution to the penalty; explain why reducing residual cannot recover the missing null-space information.
3. **Model and data sensitivity (20):** Separate gain mismatch from sensor perturbation. Compare source error with sensor fit and avoid translating a matrix change into millimeters.
4. **Resolution (15):** Interpret one column and one row, distinguish assumed from effective resolution, and identify why three-source identity recovery is impossible with rank two.
5. **Scientific transfer (15):** Follow `REAL_SOURCE_PROTOCOL.md` to plan coordinate, anatomy, reference/rank, covariance, inverse and QC checks for real EEG/MEG. Define defensible output units and claims.
6. **Reproducibility (10):** Submit the complete run directory, annotated diagnostics and a short interpretation. Preserve configuration/code hashes, versioned decisions and the status of local verification.

## Connection to the eight chapter figures

| Figure | Lab connection |
|---|---|
| 14.1 Sensor/source | G maps candidate-source amplitudes into sensor mixtures |
| 14.2 Inverse ambiguity | Explicit null-space pair |
| 14.3 Coregistration | Advanced protocol only; no coordinates in the toy model |
| 14.4 Forward model | Gain dependencies and assumed-versus-true gain distinction |
| 14.5 Inverse solution | Declared objective and three coefficients |
| 14.6 Methods | Ridge/minimum-norm-like mechanics only; no dipole fitting or beamformer |
| 14.7 Uncertainty | Sensor residual, truth-based error, fixed perturbation and resolution limits |
| 14.8 NeuroBridge | Run/config/code/output identities and review-required handoff |

The tests supplied for local execution check nonuniqueness, first-order optimality, null-space orthogonality, regularization behavior, resolution columns, model mismatch, invalid inputs, hashes and refusal to overwrite earlier runs. This is not a realistic head model, a physical uncertainty calibration, an implementation of whitening/depth weighting, or clinical source imaging.
