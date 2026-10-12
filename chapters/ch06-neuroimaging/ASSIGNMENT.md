# Lab 6 — Structural MRI, NIfTI Geometry, and Functional Connectivity

**Textbook:** Chapter 6, *Neuroimaging and Multimodal Data*  
**Duration:** 90–110 minutes  
**Level:** undergraduate core; graduate quantitative extension  
**Notebook:** [06_neuroimaging_connectivity.ipynb](06_neuroimaging_connectivity.ipynb)  
**Data:** Locally generated synthetic NIfTI images; seed 42; no human participant data.

## Learning outcomes

1. Explain the distinction between voxel indices, voxel sizes, and real-world coordinates specified by the NIfTI affine.
2. Inspect anatomical image dimensions and orthogonal slices without mislabeling the orientation.
3. Extract mean regional time series from a synthetic 4D fMRI image using a matching atlas.
4. Compute Pearson correlations and explain why these are neither causal nor structural connections.
5. Document synthetic data provenance, assumptions, and preprocessing limitations.

## Procedure

1. Install repository dependencies with `python -m pip install -r requirements.txt`.
2. **Notebook route:** from the repository root run `cd chapters/ch06-neuroimaging`, then `jupyter lab`, open `06_neuroimaging_connectivity.ipynb`, and choose **Run All Cells** using the environment in which dependencies were installed. **Script route:** from the repository root run `python chapters/ch06-neuroimaging/exercise_6_1_neuroimaging.py --output-dir outputs/ch06`. The two routes use different output locations relative to their working directories.
3. Identify the NIfTI anatomical and fMRI array dimensions, voxel spacing in millimeters, and the fMRI repetition time (TR). Use the notebook's geometry cell or inspect `analysis_summary.json` and the printed affine.
4. Examine the affine and describe how it maps voxel indices to physical coordinates.
5. Inspect three anatomical slices. Do not infer left/right orientation solely from array axis labels.
6. Examine the four regional mean time series and the 4 × 4 correlation matrix.
7. Record two limitations of the synthetic signal generator and explain why a strong correlation is not evidence of a direct neural connection.
8. Submit outputs and a brief reproducibility report (suggested length: 1–2 pages). Include the run command or notebook kernel, Python/package versions, synthetic seed, a screenshot or saved copy of each figure, the matrix CSV, the affine-to-coordinate example, and answers to the interpretation questions. If using the script route, the files are in `outputs/ch06/` at the repository root; if using the notebook route, they are under `chapters/ch06-neuroimaging/outputs/ch06/`.

## Expected observations

The script generates an anatomical volume of shape **32 × 32 × 24**, a synthetic fMRI volume of **32 × 32 × 24 × 180**, voxel spacing **2 × 2 × 2.5 mm**, and TR **2 seconds**. Four atlas regions produce a **4 × 4** symmetric correlation matrix with unit diagonal. The constructed ROI-A and ROI-B time series should show positive association. Exact correlations vary with synthetic noise and must not be interpreted clinically.

## Graduate extension

Execute the notebook's graduate sensitivity cell to compare raw Pearson correlations with correlations after linear detrending, or implement another justified time-series analysis choice. Quantify differences and discuss temporal autocorrelation, confounds, atlas selection, and sensitivity to preprocessing. Explain why this exercise cannot establish biomarkers or treatment effects.

## Submission checklist

- [ ] Reproducible code execution, outputs, and source/seed.
- [ ] Anatomical slices and functional-connectivity heatmap.
- [ ] Matrix file and analysis summary with voxel dimensions and TR.
- [ ] Explanation of affine coordinates and two interpretation limitations.
- [ ] Graduate: quantitative sensitivity analysis and parameter documentation.
- [ ] No patient data or unlicensed dataset copies uploaded.

## Grading rubric

| Criterion | Undergraduate expectation | Graduate expectation | Points |
|---|---|---|---:|
| Reproducible environment and provenance | Seed, packages, data source | Also compares parameters | 20 |
| Implementation and outputs | Valid NIfTI inspection and ROI matrix | Quantitative extension | 25 |
| Scientific interpretation | Units, BOLD caveats, noncausality | Confounds and analytic sensitivity | 25 |
| Quality control and critical reasoning | Checks dimensions and affine | Explains alignment and nuisance effects | 20 |
| Reporting and ethical data handling | Clear documented submission | Clear comparative report | 10 |
| **Total** | | | **100** |

## Troubleshooting

| Issue | Solution |
|---|---|
| `No module named nibabel` | Install root `requirements.txt` in the same Python environment used by Jupyter |
| Notebook cannot import `exercise_6_1_neuroimaging` | Start Jupyter in this chapter folder or add this folder to the Python path |
| Affine or spatial dimensions mismatch | Do not resample blindly; confirm transforms and register real images before atlas extraction |
| Unexpected correlation pattern | Check synthetic seed, ROI masks, region labels, and whether preprocessing was changed |
| Outputs appear in Git | Keep `outputs/` untracked; do not commit real scans |
| Trying real fMRI with the script | This is a synthetic demonstration, not a complete BIDS/fMRIPrep or Nilearn real-data pipeline |

## Instructor verification

From the repository root run `python -m pytest -q tests/test_chapter6_lab.py`. Automated tests validate synthetic geometry, output shapes, correlation symmetry, the student-facing command-line route, and execution of the notebook's code cells. A separate real-data workflow would require acquisition-specific preprocessing, alignment, confound handling, and verified source permissions.