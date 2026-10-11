"""Chapter 6: synthetic NIfTI anatomy and ROI connectivity (not clinical data)."""
from pathlib import Path
import argparse
import json
import numpy as np
import nibabel as nib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def generate_demo(folder, seed=42):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    shape = (32, 32, 24)
    grid = np.indices(shape)
    radius = ((grid[0] - 15.5) / 12)**2 + ((grid[1] - 15.5) / 11)**2 + ((grid[2] - 11.5) / 9)**2
    anatomy = np.clip(np.where(radius < 1, 700 + 100 * (1 - radius), 0) + rng.normal(0, 8, shape), 0, None).astype("float32")
    labels = np.zeros(shape, dtype="int16")
    inside = radius < 0.8
    labels[inside & (grid[0] < 16) & (grid[1] < 16)] = 1
    labels[inside & (grid[0] >= 16) & (grid[1] < 16)] = 2
    labels[inside & (grid[0] < 16) & (grid[1] >= 16)] = 3
    labels[inside & (grid[0] >= 16) & (grid[1] >= 16)] = 4
    affine = np.diag([2., 2., 2.5, 1.])
    affine[:3, 3] = [-31., -31., -28.75]
    latent = rng.normal(size=(180, 3))
    timecourses = np.column_stack([latent[:, 0], .8*latent[:, 0] + .6*latent[:, 1], latent[:, 2], -.5*latent[:, 2] + .866*latent[:, 1]])
    bold = rng.normal(0, .7, (*shape, 180)).astype("float32")
    for index in range(1, 5):
        bold[labels == index, :] += timecourses[:, index - 1].astype("float32")
    nib.save(nib.Nifti1Image(anatomy, affine), folder / "synthetic_T1w.nii.gz")
    nib.save(nib.Nifti1Image(labels, affine), folder / "synthetic_atlas.nii.gz")
    image = nib.Nifti1Image(bold, affine)
    image.header.set_zooms((2., 2., 2.5, 2.))
    nib.save(image, folder / "synthetic_bold.nii.gz")
    (folder / "metadata.json").write_text(json.dumps({"source": "synthetic, not clinical", "seed": seed, "tr_seconds": 2., "atlas_labels": ["ROI-A", "ROI-B", "ROI-C", "ROI-D"], "warning": "No hemodynamic response or physiological forward model"}, indent=2))
    return folder


def analyze(folder, output):
    folder, output = Path(folder), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    t1 = nib.load(folder / "synthetic_T1w.nii.gz")
    fmri = nib.load(folder / "synthetic_bold.nii.gz")
    atlas = nib.load(folder / "synthetic_atlas.nii.gz")
    if not (t1.shape == atlas.shape == fmri.shape[:3] and np.allclose(t1.affine, fmri.affine) and np.allclose(t1.affine, atlas.affine)):
        raise ValueError("Spatial grids or affine transforms differ: registration is required")
    anatomy = np.asarray(t1.dataobj)
    labels = np.asarray(atlas.dataobj).astype(int)
    bold = np.asarray(fmri.dataobj)
    fig, axes = plt.subplots(1, 3, figsize=(11, 4))
    for ax, slc, name in zip(axes, [anatomy[16, :, :], anatomy[:, 16, :], anatomy[:, :, 12]], ["Sagittal", "Coronal", "Axial"]):
        ax.imshow(np.rot90(slc), cmap="gray")
        ax.set_title(name)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(output / "anatomical_slices.png", dpi=150)
    plt.close(fig)
    roi = np.stack([bold[labels == i, :].mean(axis=0) for i in range(1, 5)], axis=1)
    corr = np.corrcoef(roi, rowvar=False)
    if not np.isfinite(corr).all():
        raise ValueError("Nonfinite correlations; inspect ROI time series")
    np.savetxt(output / "roi_timeseries.csv", roi, delimiter=",", header="ROI-A,ROI-B,ROI-C,ROI-D", comments="")
    np.savetxt(output / "connectivity.csv", corr, delimiter=",", header="ROI-A,ROI-B,ROI-C,ROI-D", comments="")
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(4), ["ROI-A", "ROI-B", "ROI-C", "ROI-D"])
    ax.set_yticks(range(4), ["ROI-A", "ROI-B", "ROI-C", "ROI-D"])
    fig.colorbar(im, ax=ax, label="Pearson correlation (not causation)")
    fig.tight_layout()
    fig.savefig(output / "connectivity.png", dpi=150)
    plt.close(fig)
    summary = {"source": "synthetic, not clinical", "voxel_sizes_mm": [float(v) for v in t1.header.get_zooms()[:3]], "t1_shape": t1.shape, "bold_shape": fmri.shape, "tr_seconds": float(fmri.header.get_zooms()[3]), "atlas_regions": [1, 2, 3, 4], "method": "mean ROI time courses and Pearson correlation, without temporal filtering or nuisance regression", "nibabel_version": nib.__version__, "numpy_version": np.__version__}
    (output / "analysis_summary.json").write_text(json.dumps(summary, indent=2))
    return corr


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/ch06"))
    args = parser.parse_args()
    folder = generate_demo(args.output_dir / "synthetic_data")
    print(np.round(analyze(folder, args.output_dir), 3))
