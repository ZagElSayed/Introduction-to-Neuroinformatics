"""Chapter 6 synthetic imaging lab verification (no patient data)."""
import importlib.util
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch06-neuroimaging/exercise_6_1_neuroimaging.py"


def test_synthetic_neuroimaging_lab(tmp_path):
    spec = importlib.util.spec_from_file_location("ch06lab", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    folder = module.generate_demo(tmp_path / "source", seed=42)
    matrix = module.analyze(folder, tmp_path / "results")
    assert matrix.shape == (4, 4)
    assert np.allclose(matrix, matrix.T)
    assert np.allclose(np.diag(matrix), 1)
    assert matrix[0, 1] > 0.3
    for name in ["anatomical_slices.png", "connectivity.png", "connectivity.csv", "roi_timeseries.csv", "analysis_summary.json"]:
        assert (tmp_path / "results" / name).is_file()
    meta = json.loads((tmp_path / "results" / "analysis_summary.json").read_text())
    assert meta["source"] == "synthetic, not clinical"
    assert meta["t1_shape"] == [32, 32, 24] or tuple(meta["t1_shape"]) == (32, 32, 24)
    assert meta["bold_shape"] == [32, 32, 24, 180] or tuple(meta["bold_shape"]) == (32, 32, 24, 180)
    assert meta["tr_seconds"] == 2.0


def test_notebook_structure():
    path = ROOT / "chapters/ch06-neuroimaging/06_neuroimaging_connectivity.ipynb"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["nbformat"] == 4
    assert any(cell["cell_type"] == "code" for cell in data["cells"])

def test_student_cli_end_to_end(tmp_path):
    import subprocess
    import sys
    import nibabel as nib
    out = tmp_path / "cli"
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", str(out)],
        cwd=ROOT, capture_output=True, text=True, timeout=120, check=True
    )
    assert "1." in result.stdout or "[" in result.stdout
    t1 = nib.load(out / "synthetic_data" / "synthetic_T1w.nii.gz")
    fmri = nib.load(out / "synthetic_data" / "synthetic_bold.nii.gz")
    atlas = nib.load(out / "synthetic_data" / "synthetic_atlas.nii.gz")
    assert t1.shape == (32, 32, 24)
    assert fmri.shape == (32, 32, 24, 180)
    assert np.allclose(t1.affine, fmri.affine)
    assert np.allclose(t1.affine, atlas.affine)
    assert np.allclose(t1.header.get_zooms()[:3], (2, 2, 2.5))
    assert fmri.header.get_zooms()[3] == 2.0
    for name in ("synthetic_T1w.nii.gz", "synthetic_atlas.nii.gz", "synthetic_bold.nii.gz", "metadata.json"):
        assert (out / "synthetic_data" / name).is_file()


def test_notebook_cells_execute(tmp_path, monkeypatch):
    """Run the actual student notebook code cells in order, not just JSON syntax."""
    import sys
    from IPython.display import Image, display
    nb = json.loads((ROOT / "chapters/ch06-neuroimaging/06_neuroimaging_connectivity.ipynb").read_text())
    lab = ROOT / "chapters/ch06-neuroimaging"
    monkeypatch.chdir(tmp_path)
    sys.path.insert(0, str(lab))
    globals_dict = {"__name__": "__main__", "display": display, "Image": Image}
    for cell in nb["cells"]:
        if cell["cell_type"] == "code":
            code = "".join(cell["source"])
            exec(compile(code, "<Chapter 6 notebook cell>", "exec"), globals_dict)
    assert (lab / "outputs/ch06/analysis_summary.json").is_file()
    assert np.isfinite(globals_dict["corr_detrended"]).all()
    assert globals_dict["corr_detrended"].shape == (4, 4)
