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

def load_lab():
    spec = importlib.util.spec_from_file_location("chapter8", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_schema_and_behavior_corruptions():
    mod = load_lab()
    rows = mod.generate()
    ref = {r["trial_id"]: float(r["reference_onset_s"]) for r in rows}
    damaged = [dict(r) for r in rows]
    damaged[0]["stimulus_code"] = "UNKNOWN"
    damaged[1]["software_onset_s"] = float("nan")
    damaged[2]["correct"] = 1 - damaged[2]["correct"]
    damaged[3]["response"] = "key"
    damaged[3]["reaction_time_s"] = ""
    damaged[4]["trial_id"] = "unexpected"
    report = mod.validate(damaged, ref)
    assert any(e["field"] == "stimulus_code" for e in report["schema_errors"])
    assert any(e["field"] == "software_onset_s" for e in report["schema_errors"])
    assert any(e["field"] == "reaction_time_s" for e in report["schema_errors"])
    assert rows[2]["trial_id"] in report["inconsistent_correctness_trial_ids"]
    assert report["unexpected_trial_ids"] == ["unexpected"]
    assert report["missing_reference_trials"] == 1
    assert rows[1]["software_onset_s"] != damaged[1]["software_onset_s"]


def test_accuracy_is_recomputed():
    mod = load_lab()
    rows = mod.generate()
    ref = {r["trial_id"]: float(r["reference_onset_s"]) for r in rows}
    baseline = mod.validate(rows, ref)
    flipped = [dict(r, correct=1-r["correct"]) for r in rows]
    report = mod.validate(flipped, ref)
    assert report["task_accuracy"] == baseline["task_accuracy"]
    assert len(report["inconsistent_correctness_trial_ids"]) == 48


def test_same_seed_files_are_identical(tmp_path):
    mod = load_lab()
    first, second = tmp_path / "first", tmp_path / "second"
    mod.run(first, seed=8)
    mod.run(second, seed=8)
    for name in ("events.tsv", "events_offset_100ms.tsv", "task_metadata.json", "qc_report.json"):
        assert (first / name).read_bytes() == (second / name).read_bytes()
    assert not mod.validate([], {})["schema_errors"]
    assert mod.validate([], {})["task_accuracy"] is None
