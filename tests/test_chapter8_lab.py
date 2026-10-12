"""Chapter 8 synthetic event protocol checks."""
import csv
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch08-experimental-design/exercise_8_1_protocol_qc.py"


def test_chapter8_cli(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
                            cwd=ROOT, capture_output=True, text=True, check=True, timeout=30)
    qc = json.loads(result.stdout)
    assert qc["baseline"]["n_trials"] == 48
    assert qc["baseline"]["onset_mismatch_trial_ids"] == []
    assert len(qc["injected_offset"]["onset_mismatch_trial_ids"]) == 48
    for name in ("events.tsv", "events_offset_100ms.tsv", "task_metadata.json", "qc_report.json"):
        assert (tmp_path / name).is_file()
    with (tmp_path / "events.tsv").open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    assert len(rows) == 48
    assert {r["condition"] for r in rows} == {"go", "nogo"}
    assert json.loads((tmp_path / "task_metadata.json").read_text())["source"].startswith("synthetic")


def test_chapter8_qc_detects_corruptions():
    spec = importlib.util.spec_from_file_location("chapter8", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    events = mod.generate()
    reference = {row["trial_id"]: float(row["reference_onset_s"]) for row in events}
    damaged = [dict(row) for row in events]
    damaged[1]["trial_id"] = damaged[0]["trial_id"]
    damaged[2]["reaction_time_s"] = 0.05
    report = mod.validate(damaged, reference)
    assert report["duplicate_trial_ids"] == 1
    assert report["missing_reference_trials"] == 1
    assert damaged[2]["trial_id"] in report["implausible_reaction_time_trial_ids"]
