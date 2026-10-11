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
