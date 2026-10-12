"""Chapter 10: deterministic synthetic EEG-like pipeline with integrity and QC checks."""
import argparse
import csv
import hashlib
import json
import platform
import time
from pathlib import Path

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def setup(root):
    root = Path(root)
    for folder in ("raw", "derivatives", "logs", "config", "manifests"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    source = root / "raw" / "synthetic_eeg.csv"
    if not source.exists():
        with source.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["sample", "Cz_uV", "Pz_uV"])
            for i in range(40):
                writer.writerow([i, round((i % 9) - 4, 3), round((i % 7) - 3, 3)])
    metadata = root / "config" / "metadata.json"
    if not metadata.exists():
        metadata.write_text(json.dumps({"sampling_rate_hz": 250, "units": "uV",
                                        "source": "synthetic", "channels": ["Cz", "Pz"]}, indent=2))
    config = root / "config" / "pipeline.json"
    if not config.exists():
        config.write_text(json.dumps({"pipeline_version": "1.0", "qc_max_abs_mean_uV": 1e-9}, indent=2))
    return root

def run(root):
    root = Path(root)
    source = root / "raw" / "synthetic_eeg.csv"
    meta_path = root / "config" / "metadata.json"
    config_path = root / "config" / "pipeline.json"
    output = root / "derivatives" / "centered_eeg.csv"
    provenance_path = root / "manifests" / "provenance.json"
    started = time.perf_counter()
    try:
        metadata = json.loads(meta_path.read_text())
        config = json.loads(config_path.read_text())
        if metadata.get("units") != "uV" or not isinstance(metadata.get("sampling_rate_hz"), (int, float)) or metadata["sampling_rate_hz"] <= 0:
            raise ValueError("Required sampling rate or units missing/invalid")
        with source.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
        if not rows or not all(set(["sample", "Cz_uV", "Pz_uV"]).issubset(r) for r in rows):
            raise ValueError("Missing EEG-like columns or rows")
        values = [[float(row[ch]) for ch in ("Cz_uV", "Pz_uV")] for row in rows]
        means = [sum(v[j] for v in values) / len(values) for j in range(2)]
        centered = [[v[j] - means[j] for j in range(2)] for v in values]
        with output.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["sample", "Cz_centered_uV", "Pz_centered_uV"])
            for row, value in zip(rows, centered):
                writer.writerow([row["sample"], *[format(x, ".12g") for x in value]])
        qc = {"sample_count": len(rows), "channel_means_after_centering_uV":
              [sum(v[j] for v in centered) / len(centered) for j in range(2)]}
        if any(abs(x) > config["qc_max_abs_mean_uV"] for x in qc["channel_means_after_centering_uV"]):
            raise ValueError("Centered mean exceeds QC threshold")
        status = "success"
        error = None
    except (OSError, ValueError, KeyError, TypeError) as exc:
        status, error = "failed", str(exc)
        qc = {}
        if output.exists():
            output.unlink()
    record = {"status": status, "error": error, "input_sha256": digest(source) if source.exists() else None,
              "metadata_sha256": digest(meta_path) if meta_path.exists() else None,
              "config_sha256": digest(config_path) if config_path.exists() else None,
              "output_sha256": digest(output) if status == "success" else None,
              "pipeline_version": "1.0", "python_version": platform.python_version(),
              "runtime_seconds": round(time.perf_counter() - started, 6), "qc": qc}
    provenance_path.parent.mkdir(parents=True, exist_ok=True)
    provenance_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    return record

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--work-dir", default="outputs/ch10")
    parser.add_argument("--run-only", action="store_true")
    args = parser.parse_args()
    if not args.run_only:
        setup(args.work_dir)
    result = run(args.work_dir)
    print(json.dumps(result, indent=2))
    if result["status"] != "success":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
