"""Chapter 12 synthetic artifact QC regression checks."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch12-preprocessing/exercise_12_1_artifact_qc.py"

def load():
    spec = importlib.util.spec_from_file_location("ch12", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_cli(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
                            capture_output=True, text=True, check=True)
    report = json.loads(result.stdout)
    assert report["n_samples"] == 500
    assert report["synthetic"] is True
    assert report["window_duration_ms"] == 44
    assert report["input_sha256"] and report["output_sha256"]
    assert (tmp_path / "synthetic_raw.csv").exists()
    assert (tmp_path / "synthetic_smoothed.csv").exists()

def test_smoothing_and_invalid_window(tmp_path):
    m = load()
    assert m.moving_average([1, 2, 3, 4, 5], 1) == [1, 2, 3, 4, 5]
    assert m.moving_average([1, 2, 3, 4, 5], 3)[2] == 3
    try:
        m.moving_average([1, 2, 3], 2)
        assert False, "Even window should fail"
    except ValueError:
        pass
    a = m.run(tmp_path, window=1)
    b = m.run(tmp_path, window=11)
    assert a["input_sha256"] == b["input_sha256"]
    assert a["output_sha256"] != b["output_sha256"]
