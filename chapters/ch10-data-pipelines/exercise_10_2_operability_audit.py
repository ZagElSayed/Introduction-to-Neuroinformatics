"""Index synthetic run evidence and perform a local restore-and-rerun drill.

Read-only with respect to the Exercise 10.1 workspace. Writes a fresh audit
workspace. This is not independent backup, production authorization, or an
RPO/RTO compliance test. Uses only Python's standard library.
"""
import argparse
import csv
import importlib.util
import json
import math
import shutil
import sqlite3
import time
from datetime import datetime, timezone
from contextlib import closing
from pathlib import Path

SCRIPT = Path(__file__).with_name("exercise_10_1_reproducible_pipeline.py")
SNAPSHOTS = [
    ("source.csv", "input_sha256", "raw/synthetic_eeg.csv"),
    ("metadata.json", "metadata_sha256", "config/metadata.json"),
    ("pipeline.json", "config_sha256", "config/pipeline.json"),
    ("source_baseline.json", "baseline_sha256", "manifests/source_baseline.json"),
]


def load_pipeline():
    spec = importlib.util.spec_from_file_location("ch10_pipeline", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_manifest(pipeline, payload):
    value = pipeline.read_json(payload)
    pending = [value]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
        elif isinstance(item, float) and not math.isfinite(item):
            raise ValueError("Non-finite number in execution evidence")
    return value


def inspect_run(pipeline, root, directory):
    """Check per-run evidence, without trusting the mutable latest-run summary."""
    record = {}
    issues = []
    artifacts = []
    try:
        manifest = directory / "provenance.json"
        record = read_manifest(pipeline, manifest.read_bytes())
        if record.get("run_id") != directory.name:
            raise ValueError("Run ID differs from its directory")
        if record.get("manifest_path") != manifest.relative_to(root).as_posix():
            raise ValueError("Manifest path differs from its recorded location")
        status = record.get("status")
        if status not in ("success", "failed"):
            raise ValueError("Run is not in a recognized terminal state")
        if record.get("pipeline_version") != pipeline.VERSION:
            raise ValueError("Unsupported pipeline version")
        if record.get("script_sha256") != pipeline.digest(SCRIPT):
            raise ValueError("Reference code differs; resolve the version before this drill")
        runtime = pipeline.finite_number(record.get("runtime_seconds"), "runtime_seconds")
        if runtime < 0:
            raise ValueError("Negative runtime")
        events = [pipeline.read_json(line.encode())
                  for line in (directory / "events.jsonl").read_text().splitlines() if line]
        if not events or events != record.get("stages"):
            raise ValueError("Stage events are missing or differ from the manifest")
        for name, field, _ in SNAPSHOTS:
            path = directory / "inputs" / name
            expected = record.get(field)
            if expected is None:
                if status == "success" or path.exists():
                    raise ValueError("Missing snapshot digest")
                continue  # Snapshot-stage failures may precede capture of an input.
            if not path.is_file() or pipeline.digest(path) != expected:
                raise ValueError("Input snapshot digest mismatch: " + name)
            artifacts.append((name, path.relative_to(root).as_posix(), expected))
        output = directory / "derivatives/centered_eeg.csv"
        if status == "success":
            if record.get("error") is not None:
                raise ValueError("Successful run contains an error")
            if record.get("output_path") != output.relative_to(root).as_posix():
                raise ValueError("Unexpected output location")
            if pipeline.digest(output) != record.get("output_sha256"):
                raise ValueError("Output digest mismatch")
            saved = pipeline.parse_samples(output.read_bytes(), pipeline.OUTPUT_COLUMNS)
            source = pipeline.parse_samples((directory / "inputs/source.csv").read_bytes(), pipeline.COLUMNS)
            config = pipeline.read_json((directory / "inputs/pipeline.json").read_bytes())
            tolerance = pipeline.finite_number(config.get("qc_max_abs_mean_uV"), "QC tolerance")
            if tolerance < 0 or len(saved) != len(source):
                raise ValueError("Invalid QC tolerance or sample count")
            means = [math.fsum(pair[j] for pair in saved) / len(saved) for j in range(2)]
            qc = record.get("qc")
            if not isinstance(qc, dict) or qc.get("passed") is not True:
                raise ValueError("No passing numerical QC record")
            if qc.get("sample_count") != len(saved) or qc.get("qc_max_abs_mean_uV") != tolerance:
                raise ValueError("QC count or tolerance differs from the artifact/configuration")
            if qc.get("channel_means_after_centering_uV") != means:
                raise ValueError("Recorded QC means differ from saved output")
            if any(abs(value) > tolerance for value in means):
                raise ValueError("Saved output fails centering QC")
            source_means = [math.fsum(pair[j] for pair in source) / len(source) for j in range(2)]
            expected = [[float(format(pair[j] - source_means[j], ".12g"))
                         for j in range(2)] for pair in source]
            if saved != expected:
                raise ValueError("Output does not match the declared transformation")
            completed = [event.get("stage") for event in events if event.get("status") == "completed"]
            if completed != ["snapshot", "validation", "transform", "qc", "publication"]:
                raise ValueError("Required stages did not complete in order")
            artifacts.append(("centered_eeg.csv", record["output_path"], record["output_sha256"]))
        else:
            if not record.get("error") or not record.get("failed_stage"):
                raise ValueError("Failure reason or stage missing")
            if output.exists() or record.get("output_path") is not None or record.get("output_sha256") is not None:
                raise ValueError("Failed attempt contains a published output")
            if events[-1].get("status") != "failed" or events[-1].get("stage") != record["failed_stage"]:
                raise ValueError("Failure event does not match the manifest")
    except (OSError, ValueError, TypeError, KeyError, OverflowError, AttributeError, csv.Error) as exc:
        issues.append(str(exc))
    return {"run_id": directory.name, "record": record, "evidence_ok": not issues,
            "issues": issues, "artifacts": artifacts}


def restore_drill(pipeline, root, selected, destination):
    """Package one verified success; restore it and recompute its derivative."""
    started = time.perf_counter()
    run_id = selected["run_id"]
    original = root / "runs" / run_id
    package = destination / "backup_package"
    shutil.copytree(original, package)
    for original_file in original.rglob("*"):
        if original_file.is_file():
            relative = original_file.relative_to(original)
            if pipeline.digest(original_file) != pipeline.digest(package / relative):
                raise ValueError("Package differs from reference evidence")
    restored = destination / "restored_workspace"
    for name, _, relative in SNAPSHOTS:
        target = restored / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(package / "inputs" / name, target)
    rerun = pipeline.run(restored)
    report = {
        "reference_run_id": run_id,
        "reference_output_sha256": selected["record"]["output_sha256"],
        "restored_run_id": rerun["run_id"],
        "rerun_status": rerun["status"],
        "restored_output_sha256": rerun["output_sha256"],
        "derivative_matches": rerun["status"] == "success" and
                              rerun["output_sha256"] == selected["record"]["output_sha256"],
        "drill_elapsed_seconds": round(time.perf_counter() - started, 6),
        "scope": "Local synthetic copy/restore/rerun; not independent backup or outage timing",
    }
    pipeline.save_json(destination / "recovery_verification.json", report)
    return report


def audit(work_dir, output_dir):
    pipeline = load_pipeline()
    root, destination = Path(work_dir).resolve(), Path(output_dir).resolve()
    if not (root / "runs").is_dir():
        raise ValueError("No Exercise 10.1 run history found")
    if destination == root or root in destination.parents:
        raise ValueError("Audit output must be outside the input workspace")
    if destination.exists() and any(destination.iterdir()):
        raise ValueError("Choose a fresh, empty --output-dir")
    destination.mkdir(parents=True, exist_ok=True)
    directories = sorted(path for path in (root / "runs").iterdir() if path.is_dir())
    checks = [inspect_run(pipeline, root, path) for path in directories]
    with closing(sqlite3.connect(destination / "catalog.sqlite")) as connection, connection:
        connection.execute("CREATE TABLE runs (run_id TEXT PRIMARY KEY, status TEXT, evidence_ok INTEGER, "
                           "qc_passed INTEGER, output_path TEXT, output_sha256 TEXT)")
        connection.execute("CREATE TABLE artifacts (run_id TEXT REFERENCES runs(run_id), kind TEXT, "
                           "relative_path TEXT, sha256 TEXT)")
        connection.execute("PRAGMA foreign_keys=ON")
        for check in checks:
            record = check["record"]
            status = record.get("status")
            status = status if status in ("success", "failed") else "incomplete"
            connection.execute("INSERT INTO runs VALUES (?,?,?,?,?,?)", (
                check["run_id"], status, int(check["evidence_ok"]),
                int(check["evidence_ok"] and status == "success"),
                record.get("output_path") if check["evidence_ok"] else None,
                record.get("output_sha256") if check["evidence_ok"] else None))
            for kind, path, sha in check["artifacts"]:
                connection.execute("INSERT INTO artifacts VALUES (?,?,?,?)", (check["run_id"], kind, path, sha))
        eligible = [dict(zip(("run_id", "output_path", "output_sha256"), row)) for row in
                    connection.execute("SELECT run_id, output_path, output_sha256 FROM runs "
                                       "WHERE status='success' AND evidence_ok=1 AND qc_passed=1 ORDER BY run_id")]
    pipeline.save_json(destination / "eligible_artifacts.json", eligible)
    pipeline.save_json(destination / "evidence_checks.json", checks)
    recovery = None
    if eligible:
        selected = next(check for check in checks if check["run_id"] == eligible[0]["run_id"])
        recovery = restore_drill(pipeline, root, selected, destination)
    invalid = sum(not check["evidence_ok"] for check in checks)
    summary = {
        "status": "success" if checks and not invalid and recovery and recovery["derivative_matches"] else "failed",
        "observed_utc": datetime.now(timezone.utc).isoformat(),
        "denominator": "All run directories present in this workspace at audit collection",
        "run_directories_observed": len(checks),
        "declared_successes": sum(check["record"].get("status") == "success" for check in checks),
        "declared_failures": sum(check["record"].get("status") == "failed" for check in checks),
        "invalid_or_incomplete_evidence": invalid,
        "numerically_eligible_outputs": len(eligible),
        "recovery_checked": recovery is not None,
        "recovery_derivative_matches": bool(recovery and recovery["derivative_matches"]),
        "limitations": "Synthetic numerical eligibility only; no production authorization, clinical QC, "
                       "independent failure domain, CPU/GPU monitoring, or RPO/RTO guarantee",
    }
    pipeline.save_json(destination / "operability_summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default="outputs/ch10")
    parser.add_argument("--output-dir", default="outputs/ch10-audit")
    args = parser.parse_args()
    try:
        result = audit(args.work_dir, args.output_dir)
    except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
        result = {"status": "failed", "error": str(exc), "evidence_incomplete": True}
    print(json.dumps(result, indent=2, allow_nan=False))
    if result["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
