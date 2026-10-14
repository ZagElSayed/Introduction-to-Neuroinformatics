"""Synthetic pipeline: validated inputs, per-run evidence, and candidate publication.

Teaching only: single-process local execution, no cache, scheduler, production
permissions, clinical QC, or crash-durable distributed commit protocol.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import platform
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

VERSION = "2.0"
COLUMNS = ["sample", "Cz_uV", "Pz_uV"]
OUTPUT_COLUMNS = ["sample", "Cz_centered_uV", "Pz_centered_uV"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_write(path, payload):
    """Replace one local file using a temporary file in the same directory.

    This does not promise power-loss durability or a multi-file transaction.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(payload)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def save_json(path, value):
    atomic_write(path, (json.dumps(value, indent=2, allow_nan=False) + "\n").encode("utf-8"))


def reject_constant(value):
    raise ValueError("Non-finite JSON number: " + value)


def read_json(payload):
    value = json.loads(payload.decode("utf-8"), parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value


def finite_number(value, name, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(name + " must be a number")
    if not math.isfinite(value) or (positive and value <= 0):
        raise ValueError(name + " must be finite" + (" and positive" if positive else ""))
    return value


def setup(root):
    """Initialize a fresh synthetic workspace; never repair an existing one."""
    root = Path(root)
    marker = root / "manifests/source_baseline.json"
    if marker.is_file():
        return root
    if root.exists() and any(root.iterdir()):
        raise ValueError("Nonempty workspace without a baseline; choose a fresh --work-dir")
    root.mkdir(parents=True, exist_ok=True)
    for folder in ("raw", "config", "manifests", "runs"):
        (root / folder).mkdir(exist_ok=True)
    text = io.StringIO(newline="")
    writer = csv.writer(text, lineterminator="\n")
    writer.writerow(COLUMNS)
    for i in range(40):
        writer.writerow([i, (i % 9) - 4, (i % 7) - 3])
    source = root / "raw/synthetic_eeg.csv"
    atomic_write(source, text.getvalue().encode("utf-8"))
    save_json(root / "config/metadata.json", {
        "sampling_rate_hz": 250, "units": "uV", "source": "synthetic",
        "channels": ["Cz", "Pz"],
    })
    save_json(root / "config/pipeline.json", {
        "pipeline_version": VERSION, "qc_max_abs_mean_uV": 1e-9,
    })
    save_json(marker, {"lab": "ch10", "pipeline_version": VERSION,
                       "source_sha256": digest(source)})
    return root


def parse_samples(payload, columns):
    reader = csv.DictReader(io.StringIO(payload.decode("utf-8"), newline=""))
    if reader.fieldnames != columns:
        raise ValueError("Unexpected CSV column names or order")
    values = []
    for index, row in enumerate(reader):
        if set(row) != set(columns) or any(value is None for value in row.values()):
            raise ValueError("Malformed CSV row")
        if row["sample"] != str(index):
            raise ValueError("Sample indices must be contiguous integers starting at zero")
        pair = [float(row[name]) for name in columns[1:]]
        if not all(math.isfinite(value) for value in pair):
            raise ValueError("Samples must be finite")
        values.append(pair)
    if len(values) < 2:
        raise ValueError("At least two samples are required")
    return values


def run(root):
    root = Path(root)
    run_id = uuid.uuid4().hex
    run_dir = root / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    events = []
    stage = "snapshot"
    candidate = run_dir / "candidate.csv"
    output = run_dir / "derivatives/centered_eeg.csv"
    record = {
        "run_id": run_id, "pipeline_version": VERSION,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(), "platform": platform.platform(),
        "script_sha256": digest(__file__), "status": "running", "error": None,
        "input_sha256": None, "metadata_sha256": None, "config_sha256": None,
        "output_sha256": None, "output_path": None, "qc": {},
        "manifest_path": (run_dir / "provenance.json").relative_to(root).as_posix(),
    }

    def event(status):
        events.append({"stage": stage, "status": status,
                       "timestamp_utc": datetime.now(timezone.utc).isoformat()})

    try:
        event("started")
        snapshots = {}
        for name, path, key in (
            ("source.csv", root / "raw/synthetic_eeg.csv", "input_sha256"),
            ("metadata.json", root / "config/metadata.json", "metadata_sha256"),
            ("pipeline.json", root / "config/pipeline.json", "config_sha256"),
            ("source_baseline.json", root / "manifests/source_baseline.json", "baseline_sha256"),
        ):
            payload = path.read_bytes()
            snapshots[name] = payload
            record[key] = hashlib.sha256(payload).hexdigest()
            atomic_write(run_dir / "inputs" / name, payload)
        event("completed")
        stage = "validation"
        event("started")
        baseline = read_json(snapshots["source_baseline.json"])
        if baseline.get("lab") != "ch10" or baseline.get("pipeline_version") != VERSION:
            raise ValueError("Unsupported workspace baseline")
        if record["input_sha256"] != baseline.get("source_sha256"):
            raise ValueError("Source digest differs from the recorded baseline")
        metadata = read_json(snapshots["metadata.json"])
        config = read_json(snapshots["pipeline.json"])
        if metadata.get("units") != "uV" or metadata.get("channels") != ["Cz", "Pz"]:
            raise ValueError("Required units or channel labels missing/invalid")
        if metadata.get("source") != "synthetic":
            raise ValueError("Only the synthetic teaching source is supported")
        finite_number(metadata.get("sampling_rate_hz"), "sampling_rate_hz", positive=True)
        if config.get("pipeline_version") != VERSION:
            raise ValueError("Unsupported pipeline configuration version")
        tolerance = finite_number(config.get("qc_max_abs_mean_uV"), "QC tolerance")
        if tolerance < 0:
            raise ValueError("QC tolerance must be nonnegative")
        values = parse_samples(snapshots["source.csv"], COLUMNS)
        event("completed")
        stage = "transform"
        event("started")
        means = [math.fsum(pair[j] for pair in values) / len(values) for j in range(2)]
        text = io.StringIO(newline="")
        writer = csv.writer(text, lineterminator="\n")
        writer.writerow(OUTPUT_COLUMNS)
        for i, pair in enumerate(values):
            centered = [pair[j] - means[j] for j in range(2)]
            if not all(math.isfinite(value) for value in centered):
                raise ValueError("Non-finite transformed sample")
            writer.writerow([i, *[format(value, ".12g") for value in centered]])
        atomic_write(candidate, text.getvalue().encode("utf-8"))
        event("completed")
        stage = "qc"
        event("started")
        saved = parse_samples(candidate.read_bytes(), OUTPUT_COLUMNS)
        after = [math.fsum(pair[j] for pair in saved) / len(saved) for j in range(2)]
        record["qc"] = {"sample_count": len(saved), "qc_max_abs_mean_uV": tolerance,
                        "channel_means_after_centering_uV": after,
                        "evaluated_on": "serialized_candidate", "passed": False}
        if len(saved) != len(values) or any(abs(value) > tolerance for value in after):
            raise ValueError("Serialized candidate fails centering QC")
        record["qc"]["passed"] = True
        event("completed")
        stage = "publication"
        event("started")
        output.parent.mkdir(parents=True, exist_ok=True)
        os.replace(candidate, output)
        record["output_sha256"] = digest(output)
        record["output_path"] = output.relative_to(root).as_posix()
        event("completed")
        record["status"] = "success"
    except (OSError, ValueError, TypeError, KeyError, OverflowError, csv.Error) as exc:
        record["status"] = "failed"
        record["error"] = str(exc)
        record["failed_stage"] = stage
        event("failed")
        # An attempt never deletes an earlier run's output.
        if output.exists():
            output.unlink()
        record["output_sha256"] = None
        record["output_path"] = None
    finally:
        if candidate.exists():
            candidate.unlink()
    record["finished_utc"] = datetime.now(timezone.utc).isoformat()
    record["runtime_seconds"] = round(time.perf_counter() - started, 6)
    record["stages"] = events
    save_json(run_dir / "provenance.json", record)
    atomic_write(run_dir / "events.jsonl", "".join(
        json.dumps(item, allow_nan=False) + "\n" for item in events).encode("utf-8"))
    # Latest-attempt convenience copy; unique per-run records retain the history.
    save_json(root / "manifests/provenance.json", record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", default="outputs/ch10")
    parser.add_argument("--run-only", action="store_true")
    args = parser.parse_args()
    try:
        if not args.run_only:
            setup(args.work_dir)
        result = run(args.work_dir)
    except (OSError, ValueError) as exc:
        # Filesystem failures can prevent creation of the evidence itself.
        result = {"status": "failed", "error": str(exc), "evidence_incomplete": True}
    print(json.dumps(result, indent=2, allow_nan=False))
    if result["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
