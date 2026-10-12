"""End-to-end checks for Chapter 7 public wearable laboratory."""
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch07-wearables/exercise_7_1_multimodal_timeline.py"


def test_lab_functions(tmp_path):
    spec = importlib.util.spec_from_file_location("chapter7", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    data = module.generate(seed=42)
    assert len(data["ecg_mv"]) == 30000
    assert len(data["imu_t_reference"]) == 6000
    assert np.isclose(data["ecg_t_device"][0] - data["ecg_t_reference"][0], 0.25)
    assert np.count_nonzero(~data["imu_valid"]) == 150
    summary = module.analyze(data, tmp_path)
    assert np.isclose(summary["imu_coverage_fraction"], 0.975)
    assert summary["ecg_beat_source"].startswith("synthetic")
    with (tmp_path / "analysis_table.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) > 100
    # All of the one-second interval 55-56 is missing; no invented acceleration.
    row = next(r for r in rows if float(r["reference_time_s"]) == 55)
    assert row["accel_magnitude_mean_mps2"].lower() == "nan"
    assert float(row["imu_coverage_fraction"]) == 0
    assert (tmp_path / "multimodal_timeline.png").stat().st_size > 1000


def test_student_cli(tmp_path):
    out = tmp_path / "ch07"
    result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(out)],
                            cwd=ROOT, capture_output=True, text=True, timeout=120, check=True)
    assert json.loads(result.stdout)["source"] == "synthetic, not clinical"
    expected = ["ecg_native.csv", "imu_native.csv", "events.csv",
                "analysis_table.csv", "metadata.json", "multimodal_timeline.png"]
    for filename in expected:
        assert (out / filename).is_file()
