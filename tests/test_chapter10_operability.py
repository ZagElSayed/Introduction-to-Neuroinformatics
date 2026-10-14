"""Local behavioral checks for the synthetic operability and recovery exercise."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch10-data-pipelines/exercise_10_2_operability_audit.py"


@pytest.fixture
def modules():
    spec = importlib.util.spec_from_file_location("ch10_operability", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, module.load_pipeline()


def test_catalog_and_restore_rerun(modules, tmp_path):
    audit, pipeline = modules
    work, output = tmp_path / "work", tmp_path / "audit"
    pipeline.setup(work)
    reference = pipeline.run(work)
    result = audit.audit(work, output)
    assert result["status"] == "success"
    assert result["run_directories_observed"] == 1
    assert result["numerically_eligible_outputs"] == 1
    assert result["recovery_derivative_matches"] is True
    restored = json.loads((output / "recovery_verification.json").read_text())
    assert restored["restored_output_sha256"] == reference["output_sha256"]
    assert (output / "catalog.sqlite").is_file()
    assert len(list((work / "runs").iterdir())) == 1  # Original history remains unchanged.


def test_expected_failure_is_retained_but_not_eligible(modules, tmp_path):
    audit, pipeline = modules
    work = tmp_path / "work"
    pipeline.setup(work)
    pipeline.run(work)
    meta = work / "config/metadata.json"
    value = json.loads(meta.read_text())
    del value["units"]
    meta.write_text(json.dumps(value))
    pipeline.run(work)
    result = audit.audit(work, tmp_path / "audit")
    assert result["status"] == "success"  # An auditable failed attempt is expected evidence.
    assert result["declared_failures"] == 1
    assert result["numerically_eligible_outputs"] == 1
    assert result["run_directories_observed"] == 2


def test_corrupt_derivative_is_not_eligible(modules, tmp_path):
    audit, pipeline = modules
    work = tmp_path / "work"
    pipeline.setup(work)
    reference = pipeline.run(work)
    (work / reference["output_path"]).write_text("changed")
    result = audit.audit(work, tmp_path / "audit")
    assert result["status"] == "failed"
    assert result["invalid_or_incomplete_evidence"] == 1
    assert result["numerically_eligible_outputs"] == 0
    assert result["recovery_checked"] is False


def test_orphaned_run_is_visible_and_latest_summary_is_not_counted(modules, tmp_path):
    audit, pipeline = modules
    work = tmp_path / "work"
    pipeline.setup(work)
    pipeline.run(work)
    (work / "runs/orphaned_attempt").mkdir()
    result = audit.audit(work, tmp_path / "audit")
    assert result["status"] == "failed"
    assert result["run_directories_observed"] == 2
    assert result["invalid_or_incomplete_evidence"] == 1
    assert result["numerically_eligible_outputs"] == 1


def test_audit_never_overwrites_existing_results(modules, tmp_path):
    audit, pipeline = modules
    work, output = tmp_path / "work", tmp_path / "audit"
    pipeline.setup(work)
    pipeline.run(work)
    audit.audit(work, output)
    with pytest.raises(ValueError, match="fresh"):
        audit.audit(work, output)
    with pytest.raises(ValueError, match="outside"):
        audit.audit(work, work / "audit")


def test_nonfinite_manifest_remains_an_auditable_failure(modules, tmp_path):
    audit, pipeline = modules
    work, output = tmp_path / "work", tmp_path / "audit"
    pipeline.setup(work)
    record = pipeline.run(work)
    manifest = work / record["manifest_path"]
    # 1e999 is legal JSON numeric syntax but overflows Python float to infinity.
    text = manifest.read_text().replace('"runtime_seconds": ' + str(record["runtime_seconds"]),
                                        '"runtime_seconds": 1e999')
    manifest.write_text(text)
    result = audit.audit(work, output)
    assert result["status"] == "failed"
    assert result["invalid_or_incomplete_evidence"] == 1
    assert (output / "evidence_checks.json").is_file()
