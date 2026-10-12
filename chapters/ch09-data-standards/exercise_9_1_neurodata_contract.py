"""Chapter 9: synthetic neurodata inventory, BIDS-inspired export, and validation."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_table(path, fields, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)

def build(output_dir):
    root = Path(output_dir)
    raw = root / "source"
    target = root / "export"
    raw.mkdir(parents=True, exist_ok=True)
    target.mkdir(parents=True, exist_ok=True)
    source = raw / "Study_P01_task.csv"
    source.write_text("time_s,code\n0.5,G\n2.0,N\n3.5,G\n", encoding="utf-8")
    (raw / "Study_P01_notes.txt").write_text("Synthetic session; no human identifiers.\n", encoding="utf-8")
    subject = "sub-001"
    events_dir = target / subject / "ses-01" / "func"
    events_dir.mkdir(parents=True, exist_ok=True)
    events = events_dir / f"{subject}_ses-01_task-gonogo_events.tsv"
    write_table(events, ["onset", "duration", "trial_type"], [
        {"onset": "0.5", "duration": "0", "trial_type": "go"},
        {"onset": "2.0", "duration": "0", "trial_type": "nogo"},
        {"onset": "3.5", "duration": "0", "trial_type": "go"}])
    write_table(target / "participants.tsv", ["participant_id", "group"], [{"participant_id": subject, "group": "synthetic"}])
    (target / "dataset_description.json").write_text(json.dumps({
        "Name": "Chapter 9 synthetic event teaching example",
        "BIDSVersion": "1.10.0", "DatasetType": "raw",
        "GeneratedBy": [{"Name": "chapter9 teaching generator", "Version": "1.0"}]}, indent=2), encoding="utf-8")
    dictionary = {"onset": {"Description": "Synthetic event onset", "Units": "s"},
                  "duration": {"Description": "Synthetic event duration", "Units": "s"},
                  "trial_type": {"Description": "Synthetic event code", "Levels": {"go": "respond", "nogo": "withhold"}}}
    (events_dir / f"{subject}_ses-01_task-gonogo_events.json").write_text(json.dumps(dictionary, indent=2), encoding="utf-8")
    inventory = [{"source_path": str(source.relative_to(root)), "source_sha256": sha256(source),
                  "target_path": str(events.relative_to(root)), "participant_id": subject,
                  "session": "ses-01", "transformation": "synthetic example mapping; not raw signal conversion",
                  "tool_version": "1.0", "status": "mapped"}]
    (root / "manifest.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    return validate(root)

def validate(root):
    root = Path(root)
    export = root / "export"
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    errors = []
    try:
        desc = json.loads((export / "dataset_description.json").read_text(encoding="utf-8"))
        if not all(k in desc for k in ("Name", "BIDSVersion", "DatasetType")):
            errors.append("dataset_description missing required teaching fields")
    except (OSError, ValueError):
        errors.append("dataset_description missing or invalid JSON")
    for entry in manifest:
        source = root / entry["source_path"]
        target = root / entry["target_path"]
        if not source.is_file() or sha256(source) != entry["source_sha256"]:
            errors.append("source checksum mismatch or missing")
        if not target.is_file():
            errors.append("mapped target missing")
        if not entry["participant_id"].startswith("sub-"):
            errors.append("invalid coded subject label")
        if target.is_file():
            with target.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream, delimiter="\t"))
            for row in rows:
                try:
                    if float(row["onset"]) < 0 or float(row["duration"]) < 0:
                        errors.append("negative event time")
                except (KeyError, ValueError):
                    errors.append("invalid event time")
    report = {"teaching_dataset": True, "bids_compliant": "not established; run official BIDS validator separately",
              "mapped_objects": len(manifest), "errors": errors, "passed_local_checks": not errors,
              "scientific_audit_required": True}
    (root / "validation_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/ch09")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(validate(args.output_dir) if args.validate_only else build(args.output_dir), indent=2))

if __name__ == "__main__":
    main()
