"""Tests for Chapter 10 pipeline integrity, recovery, and reproducibility."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch10-data-pipelines/exercise_10_1_reproducible_pipeline.py"

def test_cli_reproducibility(tmp_path):
    command = [sys.executable, str(SCRIPT), "--work-dir", str(tmp_path)]
    first = json.loads(subprocess.run(command, capture_output=True, text=True, check=True).stdout)
    assert first["status"] == "success"
    assert first["qc"]["sample_count"] == 40
    second = json.loads(subprocess.run(command, capture_output=True, text=True, check=True).stdout)
    assert second["output_sha256"] == first["output_sha256"]
    assert second["input_sha256"] == first["input_sha256"]
    assert (tmp_path / "raw/synthetic_eeg.csv").is_file()

def test_missing_metadata_fails_then_recovers(tmp_path):
    spec = importlib.util.spec_from_file_location("chapter10", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.setup(tmp_path)
    metadata = tmp_path / "config/metadata.json"
    saved = json.loads(metadata.read_text())
    del saved["units"]
    metadata.write_text(json.dumps(saved))
    failure = mod.run(tmp_path)
    assert failure["status"] == "failed"
    assert not (tmp_path / "derivatives/centered_eeg.csv").exists()
    saved["units"] = "uV"
    metadata.write_text(json.dumps(saved))
    assert mod.run(tmp_path)["status"] == "success"
