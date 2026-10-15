"""Scientific controls and artifact-preservation checks; run locally with pytest."""
import csv
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch12-preprocessing/exercise_12_1_artifact_qc.py"


def load():
    spec = importlib.util.spec_from_file_location("ch12", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cli_and_artifact_hashes(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
                            capture_output=True, text=True, check=True)
    report = json.loads(result.stdout)
    module = load()
    assert report["n_samples"] == 500
    assert report["window_duration_ms"] == 44
    assert report["lookahead_samples"] == 5
    assert report["causal"] is False
    assert report["review_status"] == "review_required"
    assert report["accepted_as_neurally_valid"] is False
    for name, digest in report["artifacts_sha256"].items():
        assert module.sha256(tmp_path / name) == digest
    with (tmp_path / "synthetic_smoothed.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 500
    assert sum(row["edge_window_truncated"] == "True" for row in rows) == 10
    assert rows[250]["time_s"] == "1.0"


def test_known_mixture_and_sensitivity(tmp_path):
    module = load()
    raw, truth = module.source_rows()
    for observed, source in zip(raw, truth):
        assert math.isclose(observed["Fz_uV"], source["Fz_neural_uV"] + source["blink_uV"] + source["drift_uV"], abs_tol=1e-12)
        assert math.isclose(observed["Pz_uV"], source["Pz_neural_uV"] + .25*source["blink_uV"] + source["drift_uV"], abs_tol=1e-12)
    identity = module.run(tmp_path / "identity", 1)
    smoothed = module.run(tmp_path / "smoothed", 11)
    for name in ("synthetic_raw.csv", "synthetic_truth.csv", "events.csv"):
        assert identity["artifacts_sha256"][name] == smoothed["artifacts_sha256"][name]
    assert identity["output_sha256"] != smoothed["output_sha256"]
    assert identity["configuration_sha256"] != smoothed["configuration_sha256"]
    assert identity["run_id"] != smoothed["run_id"]
    assert identity["interior_magnitude_gain_at_10_hz"] == 1
    assert 0 < smoothed["interior_magnitude_gain_at_10_hz"] < 1
    for channel in module.CHANNELS:
        assert identity["known_source_comparison_interior"][channel]["neural_only_filter_rmse_uV"] == 0
        assert smoothed["known_source_comparison_interior"][channel]["neural_only_filter_rmse_uV"] > 0


def test_refuses_overwrite_and_invalid_input(tmp_path):
    module = load()
    for window in (0, 2, 501, True, 1.5):
        destination = tmp_path / str(window)
        with pytest.raises(ValueError):
            module.run(destination, window)
        assert not destination.exists()
    module.run(tmp_path / "preserved", 1)
    before = (tmp_path / "preserved" / "qc_provenance.json").read_bytes()
    with pytest.raises(FileExistsError):
        module.run(tmp_path / "preserved", 11)
    assert (tmp_path / "preserved" / "qc_provenance.json").read_bytes() == before
    with pytest.raises(ValueError):
        module.moving_average([1, float("nan"), 2], 1)
