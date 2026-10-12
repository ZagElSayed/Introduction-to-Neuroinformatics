"""Chapter 9 source-to-target provenance and validation tests."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch09-data-standards/exercise_9_1_neurodata_contract.py"

def test_chapter9_cli(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
                            capture_output=True, text=True, check=True, cwd=ROOT)
    report = json.loads(result.stdout)
    assert report["passed_local_checks"] is True
    assert report["bids_compliant"].startswith("not established")
    assert (tmp_path / "manifest.json").is_file()
    assert (tmp_path / "export/participants.tsv").is_file()

def test_detect_corruption(tmp_path):
    spec = importlib.util.spec_from_file_location("chapter9", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build(tmp_path)
    source = tmp_path / "source/Study_P01_task.csv"
    source.write_text(source.read_text() + "4.0,N\n", encoding="utf-8")
    assert "source checksum mismatch or missing" in mod.validate(tmp_path)["errors"]
    mod.build(tmp_path)
    events = tmp_path / "export/sub-001/ses-01/func/sub-001_ses-01_task-gonogo_events.tsv"
    events.write_text(events.read_text().replace("0.5\t0\tgo", "bad\t0\tgo"), encoding="utf-8")
    assert "invalid event time" in mod.validate(tmp_path)["errors"]
