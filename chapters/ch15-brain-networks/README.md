# Chapter 15 — Neural Networks and Graph-Theoretic Models

**Status: runnable synthetic graph-sensitivity laboratory.** The exercise builds a six-node, symmetric weighted matrix; creates binary graphs at 20%, 40%, and 60% requested density; and compares degree, **unthresholded weighted node strength**, clustering, connected components, and global efficiency. It reports binary graph metrics after thresholding but computes strength on the original weighted matrix; students must not interpret the latter as threshold-specific strength. A synthetic shared-signal surrogate changes three edge weights to demonstrate sensitivity to confounds.

**Important:** The weights are invented; they are **not measured EEG/MEG connectivity**. Increasing weights is a toy surrogate, not a physically validated simulation of volume conduction.

## Run from the public repository root

```bash
python chapters/ch15-brain-networks/exercise_15_1_graph_sensitivity.py --output-dir outputs/ch15
python -m pytest -q tests/test_chapter15_lab.py
```

Outputs: `graph_sensitivity.csv` and `graph_report.json`.

## Assignment (100 points)

1. **Graph contract (15):** Explain node definitions, weight meaning, symmetry, diagonal, and the distinction between structural, functional, and effective connectivity.
2. **Threshold sensitivity (20):** Compare requested versus realized densities, components, degree, clustering, and global efficiency across thresholds. Explain finite-edge rounding and the deterministic lexicographic tie-breaking rule.
3. **Hub stability (15):** Compare the highest-degree node across thresholds and confound conditions; identify any ties before interpreting the reported first-listed hub. Explain why a threshold-dependent hub is not a validated biomarker.
4. **Confound reasoning (20):** Compare the baseline and altered matrices. Explain common-source mixing, reference effects, source leakage, and why imaginary coherency or leakage corrections cannot guarantee physiological truth.
5. **Statistics and null models (15):** Propose a degree-preserving or spatially constrained null model, identify the correct unit of independence, and outline multiplicity control for a real cohort.
6. **Reproducibility (15):** Submit CSV, JSON, analysis plots, a parameter manifest, and a short limitations section.

**Advanced extension:** Use a properly licensed EEG/MEG dataset to estimate connectivity with documented preprocessing, reference, estimator, frequency band, and leakage strategy. Compare multiple thresholds and at least two defensible estimators, with subject-level statistics and suitable null models.

**Limits:** The baseline does not estimate coherence, imaginary coherency, Granger causality, tractography, directed graphs, weighted shortest paths, community detection, or clinical biomarkers.

## Scientific reproducibility checklist

Record the node ordering, matrix symmetry and diagonal, invented weight scale, graph density rounding, edge tie-breaking, disconnected-pair convention (zero reciprocal distance), and the distinction between full-matrix strength and thresholded degree. The shared-signal surrogate modifies weights but is **not** a biophysical forward model or evidence of true neural communication. The script is intentionally not a full EEG/MEG connectivity estimator.
