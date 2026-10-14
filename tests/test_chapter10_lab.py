"""Behavioral checks for local execution; no human data or external services."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch10-data-pipelines/exercise_10_1_reproducible_pipeline.py"


@pytest.fixture
def lab():
    spec = importlib.util.spec_from_file_location("chapter10", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def edit_json(path, key, value):
    data = json.loads(path.read_text())
    data[key] = value
    path.write_text(json.dumps(data), encoding="utf-8")


def rebaseline(lab, root):
    """Controlled test only: bypass byte integrity to challenge semantic checks."""
    edit_json(root / "manifests/source_baseline.json", "source_sha256",
              lab.digest(root / "raw/synthetic_eeg.csv"))


def test_cli_repeatability_and_history(tmp_path):
    command = [sys.executable, str(SCRIPT), "--work-dir", str(tmp_path)]
    first = json.loads(subprocess.run(command, capture_output=True, text=True, check=True).stdout)
    second = json.loads(subprocess.run(command + ["--run-only"], capture_output=True,
                                      text=True, check=True).stdout)
    assert first["status"] == second["status"] == "success"
    assert first["output_sha256"] == second["output_sha256"]
    assert first["run_id"] != second["run_id"]
    for record in (first, second):
        assert (tmp_path / record["output_path"]).is_file()
        assert json.loads((tmp_path / record["manifest_path"]).read_text()) == record
        assert record["qc"]["sample_count"] == 40
        assert record["qc"]["evaluated_on"] == "serialized_candidate"
    assert json.loads((tmp_path / "manifests/provenance.json").read_text()) == second


def test_failure_then_recovery_preserves_previous_success(lab, tmp_path):
    lab.setup(tmp_path)
    first = lab.run(tmp_path)
    meta = tmp_path / "config/metadata.json"
    saved = meta.read_bytes()
    data = json.loads(saved)
    del data["units"]
    meta.write_text(json.dumps(data))
    lab.setup(tmp_path)  # Must not silently repair this intentionally broken metadata.
    failure = lab.run(tmp_path)
    assert failure["status"] == "failed"
    assert failure["failed_stage"] == "validation"
    assert failure["output_path"] is None
    assert (tmp_path / first["output_path"]).is_file()
    assert not list((tmp_path / "runs" / failure["run_id"]).rglob("centered_eeg.csv"))
    assert (tmp_path / "runs" / failure["run_id"] / "events.jsonl").is_file()
    meta.write_bytes(saved)
    recovered = lab.run(tmp_path)
    assert recovered["status"] == "success"
    assert recovered["output_sha256"] == first["output_sha256"]
    assert len(list((tmp_path / "runs").glob("*/provenance.json"))) == 3


@pytest.mark.parametrize("key,value", [
    ("sampling_rate_hz", float("nan")), ("sampling_rate_hz", float("inf")),
    ("sampling_rate_hz", True), ("sampling_rate_hz", 0),
    ("sampling_rate_hz", "250"), ("channels", ["Pz", "Cz"]),
    ("units", "mV"), ("source", "clinical"),
])
def test_invalid_metadata_fails(lab, tmp_path, key, value):
    lab.setup(tmp_path)
    edit_json(tmp_path / "config/metadata.json", key, value)
    result = lab.run(tmp_path)
    assert result["status"] == "failed"
    assert result["failed_stage"] == "validation"


@pytest.mark.parametrize("key,value", [
    ("qc_max_abs_mean_uV", -1), ("qc_max_abs_mean_uV", float("inf")),
    ("qc_max_abs_mean_uV", True), ("pipeline_version", "unknown"),
])
def test_invalid_configuration_fails(lab, tmp_path, key, value):
    lab.setup(tmp_path)
    edit_json(tmp_path / "config/pipeline.json", key, value)
    assert lab.run(tmp_path)["status"] == "failed"


@pytest.mark.parametrize("replacement", ["0,nan,-3", "0,inf,-3", "1,-4,-3", "0,-4,-3,extra"])
def test_corrupt_samples_fail_even_with_updated_baseline(lab, tmp_path, replacement):
    lab.setup(tmp_path)
    source = tmp_path / "raw/synthetic_eeg.csv"
    source.write_text(source.read_text().replace("0,-4,-3", replacement), encoding="utf-8")
    rebaseline(lab, tmp_path)
    result = lab.run(tmp_path)
    assert result["status"] == "failed"
    assert result["failed_stage"] == "validation"


def test_source_change_detected_by_baseline(lab, tmp_path):
    lab.setup(tmp_path)
    source = tmp_path / "raw/synthetic_eeg.csv"
    source.write_bytes(source.read_bytes().replace(b"0,-4,-3", b"0,-5,-3"))
    result = lab.run(tmp_path)
    assert result["status"] == "failed"
    assert "digest differs" in result["error"]


def test_saved_candidate_is_checked_before_publication(lab, tmp_path, monkeypatch):
    lab.setup(tmp_path)
    original = lab.atomic_write

    def corrupt_candidate(path, payload):
        if Path(path).name == "candidate.csv":
            lines = payload.decode().splitlines()
            fields = lines[1].split(",")
            fields[1] = "nan"
            lines[1] = ",".join(fields)
            payload = ("\n".join(lines) + "\n").encode()
        original(path, payload)

    monkeypatch.setattr(lab, "atomic_write", corrupt_candidate)
    result = lab.run(tmp_path)
    assert result["status"] == "failed"
    assert result["failed_stage"] == "qc"
    assert result["output_path"] is None
    assert not list((tmp_path / "runs").rglob("centered_eeg.csv"))


def test_input_snapshots_and_provenance_digests(lab, tmp_path):
    lab.setup(tmp_path)
    result = lab.run(tmp_path)
    assert result["status"] == "success"
    snapshots = tmp_path / "runs" / result["run_id"] / "inputs"
    for name, field in [("source.csv", "input_sha256"), ("metadata.json", "metadata_sha256"),
                        ("pipeline.json", "config_sha256")]:
        assert lab.digest(snapshots / name) == result[field]
    assert lab.digest(SCRIPT) == result["script_sha256"]
    assert lab.digest(tmp_path / result["output_path"]) == result["output_sha256"]
    assert [event["stage"] for event in result["stages"] if event["status"] == "completed"] == [
        "snapshot", "validation", "transform", "qc", "publication"]


def test_failure_has_nonzero_cli_exit(lab, tmp_path):
    lab.setup(tmp_path)
    edit_json(tmp_path / "config/metadata.json", "units", "invalid")
    process = subprocess.run([sys.executable, str(SCRIPT), "--work-dir", str(tmp_path),
                              "--run-only"], capture_output=True, text=True)
    assert process.returncode == 1
    assert json.loads(process.stdout)["status"] == "failed"


def test_unrelated_nonempty_directory_is_not_initialized(lab, tmp_path):
    (tmp_path / "notes.txt").write_text("keep this")
    with pytest.raises(ValueError, match="fresh"):
        lab.setup(tmp_path)
    assert not (tmp_path / "raw").exists()


def test_missing_input_records_snapshot_failure(lab, tmp_path):
    lab.setup(tmp_path)
    (tmp_path / "raw/synthetic_eeg.csv").unlink()
    result = lab.run(tmp_path)
    assert result["status"] == "failed"
    assert result["failed_stage"] == "snapshot"
    assert (tmp_path / result["manifest_path"]).is_file()


def test_json_array_is_rejected_as_metadata(lab, tmp_path):
    lab.setup(tmp_path)
    (tmp_path / "config/metadata.json").write_text("[]", encoding="utf-8")
    result = lab.run(tmp_path)
    assert result["status"] == "failed"
    assert "JSON object" in result["error"]
