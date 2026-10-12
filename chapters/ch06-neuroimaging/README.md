# Chapter 6 — Neuroimaging and Multimodal Data

This chapter's **classroom-ready laboratory** introduces NIfTI image metadata, anatomical slices, affine transformations, and region-of-interest functional connectivity.

- [Student assignment and 100-point rubric](ASSIGNMENT.md)
- [Jupyter notebook](06_neuroimaging_connectivity.ipynb)
- [Reusable Python analysis script](exercise_6_1_neuroimaging.py)

## Install and run

From the companion repository root:

```bash
python -m pip install -r requirements.txt
python chapters/ch06-neuroimaging/exercise_6_1_neuroimaging.py --output-dir outputs/ch06
```

For Jupyter, change into `chapters/ch06-neuroimaging`, start `jupyter lab`, and open `06_neuroimaging_connectivity.ipynb`. The notebook imports the local Python script; keep both files together. Run all notebook cells to inspect the affine, dimensions, images, connectivity matrix, and optional graduate detrending comparison. Notebook outputs are written relative to the notebook working directory (`chapters/ch06-neuroimaging/outputs/ch06/`), whereas the root-level script command above writes to `outputs/ch06/`.

**Data:** A reproducible synthetic 32 × 32 × 24 anatomical NIfTI image, four-region atlas, and 180-volume synthetic fMRI time series (TR = 2 s). The script generates data locally; no dataset download or redistribution is required. The simulated correlations are deliberately constructed and do not model neurovascular coupling or authentic brain networks.

## Expected outputs

`synthetic_T1w.nii.gz`, `synthetic_atlas.nii.gz`, `synthetic_bold.nii.gz`, `metadata.json`, `anatomical_slices.png`, `roi_timeseries.csv`, `connectivity.csv`, `connectivity.png`, and `analysis_summary.json`.

## Public-data extension

Students may use an appropriate public BIDS-compatible **preprocessed** fMRI dataset obtained directly from its provider, subject to its access and reuse terms. Recommended discovery portals include [OpenNeuro](https://openneuro.org/) and [NITRC](https://www.nitrc.org/). Dataset suitability, preprocessing derivatives, atlas compatibility, and download permissions must be verified before use. This starter script assumes synthetic volumes share a voxel grid; real data require registration and appropriate confound handling. Do not present the synthetic atlas as an anatomical atlas or inferred correlation as a causal connection.

See [the 28-chapter laboratory standard](../../docs/CHAPTER_LAB_STANDARD.md).
## Instructor preflight check

From the repository root, run `python -m pytest -q tests/test_chapter6_lab.py`. The CI workflow also tests the student CLI, synthetic NIfTI geometry, generated outputs, and all notebook code cells. Check the latest [Chapter 6 lab CI run](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics/actions/workflows/chapter6-lab.yml) before assigning. The exercise is designed for Python 3.11 and the root `requirements.txt` environment.
