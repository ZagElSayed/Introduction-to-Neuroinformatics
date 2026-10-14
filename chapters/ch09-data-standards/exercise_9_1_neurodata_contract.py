"""Synthetic CSV-to-TSV conversion with integrity and meaning checks.

This local teaching contract is deliberately narrower than BIDS. No real
participants, clinical de-identification, EEG, MRI, or BIDS certification.
"""
import argparse
import csv
import hashlib
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path

VERSION = "1.1"
SUBJECT = "sub-001"
SESSION = "ses-01"
PREFIX = f"{SUBJECT}_{SESSION}_task-gonogo"
SOURCE = "source/Study_P01_task.csv"
EVENTS = f"export/{SUBJECT}/{SESSION}/beh/{PREFIX}_events.tsv"
SIDECAR = EVENTS.replace(".tsv", ".json")
CODE_MAP = {"G": "go", "N": "nogo"}
TIME_ORIGIN = "first stored task data point"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def read_json(path):
    def reject(value):
        raise ValueError(f"Nonstandard JSON constant: {value}")
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)


def table(path, fields, rows):
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)


def read_table(path, delimiter, fields):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream, delimiter=delimiter)
        if reader.fieldnames != fields:
            raise ValueError(f"Expected columns {fields}")
        rows = list(reader)
    if not rows or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise ValueError("Empty table or inconsistent row width")
    return rows


def number(value):
    value = float(value)
    if not math.isfinite(value):
        raise ValueError("Event times must be finite")
    return value


def convert(source):
    """Interpret the declared source contract; negative onsets are allowed.

    BIDS allows events before the first stored sample. This synthetic source
    also permits negative onsets; duration is zero for impulse-like events.
    """
    rows = read_table(source, ",", ["time_ms", "code"])
    result = []
    for row in rows:
        if row["code"] not in CODE_MAP:
            raise ValueError("Unknown source event code")
        result.append({"onset": number(row["time_ms"]) / 1000,
                       "duration": 0.0, "trial_type": CODE_MAP[row["code"]]})
    return result


def build(output_dir, force=False):
    root = Path(output_dir)
    if root.exists() and any(root.iterdir()) and not force:
        raise ValueError("Output is not empty; choose a new directory or use --force for this synthetic demo")
    (root / "source").mkdir(parents=True, exist_ok=True)
    event_dir = (root / EVENTS).parent
    event_dir.mkdir(parents=True, exist_ok=True)
    (root / SOURCE).write_text("time_ms,code\n500,G\n2000,N\n3500,G\n", encoding="utf-8")
    write_json(root / "source/source_contract.json", {
        "time_ms": {"Units": "ms", "TimeOrigin": TIME_ORIGIN},
        "code": {"Levels": CODE_MAP}, "synthetic_only": True})
    table(root / EVENTS, ["onset", "duration", "trial_type"], convert(root / SOURCE))
    table(root / "export/participants.tsv", ["participant_id", "group"],
          [{"participant_id": SUBJECT, "group": "synthetic"}])
    write_json(root / "export/participants.json", {
        "group": {"Description": "Teaching cohort label", "Levels": {"synthetic": "No human records"}}})
    write_json(root / "export/dataset_description.json", {
        "Name": "Chapter 9 synthetic behavioral event teaching example",
        "BIDSVersion": "1.11.2", "DatasetType": "raw",
        "GeneratedBy": [{"Name": "chapter9 teaching generator", "Version": VERSION}]})
    write_json(root / SIDECAR, {
        "onset": {"Description": f"Event onset in seconds from the {TIME_ORIGIN}", "Units": "s"},
        "duration": {"Description": "Impulse-like event duration", "Units": "s"},
        "trial_type": {"Description": "Go/no-go task event", "Levels": {"go": "respond", "nogo": "withhold"}}})
    (root / "export/README").write_text(
        "Synthetic BIDS-inspired behavioral events only. Not a complete BIDS dataset.\n"
        "No corresponding task recording is supplied; formal compliance is not established.\n",
        encoding="utf-8")
    tracked = [SOURCE, "source/source_contract.json", EVENTS, SIDECAR,
               "export/participants.tsv", "export/participants.json", "export/dataset_description.json", "export/README"]
    manifest = {
        "contract_version": VERSION, "synthetic_only": True,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "participant_id": SUBJECT, "session": SESSION,
        "source_path": SOURCE, "target_path": EVENTS,
        "conversion": {"source_unit": "ms", "target_unit": "s", "factor": 0.001,
                       "time_origin": TIME_ORIGIN, "code_map": CODE_MAP, "tool_version": VERSION},
        "files": [{"path": p, "sha256": sha256(root / p)} for p in tracked]}
    write_json(root / "manifest.json", manifest)
    return validate(root)


def validate(root):
    root = Path(root).resolve()
    errors = []
    checks = []
    manifest = None

    def check(layer, name, operation):
        try:
            operation()
            checks.append({"layer": layer, "check": name, "passed": True})
        except (OSError, ValueError, TypeError, KeyError, IndexError, UnicodeError, csv.Error) as exc:
            errors.append(f"{name}: {exc}")
            checks.append({"layer": layer, "check": name, "passed": False})

    def require(condition, message):
        if not condition:
            raise ValueError(message)

    def safe_path(relative):
        require(isinstance(relative, str) and not Path(relative).is_absolute(), "Expected relative path")
        p = (root / relative).resolve()
        require(p.is_relative_to(root), "Path escapes dataset root")
        return p

    def manifest_check():
        nonlocal manifest
        manifest = read_json(root / "manifest.json")
        require(isinstance(manifest, dict), "Manifest must be an object")
        require(manifest.get("contract_version") == VERSION and manifest.get("synthetic_only") is True,
                "Unsupported teaching contract")
        require(manifest.get("participant_id") == SUBJECT and manifest.get("session") == SESSION,
                "Participant/session mismatch")
        require(manifest.get("source_path") == SOURCE and manifest.get("target_path") == EVENTS,
                "Unexpected source/target linkage")
        files = manifest["files"]
        require(isinstance(files, list) and len(files) == 8, "Incomplete file inventory")
        paths = [item["path"] for item in files]
        require(len(set(paths)) == len(paths), "Duplicate inventory paths")
        require(set(paths) == {SOURCE, "source/source_contract.json", EVENTS, SIDECAR,
                              "export/participants.tsv", "export/participants.json", "export/dataset_description.json", "export/README"},
                "Unexpected file inventory")
        for item in files:
            safe_path(item["path"])
            digest = item["sha256"]
            require(isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdef" for c in digest),
                    "Invalid SHA-256 reference")

    check("structure", "manifest", manifest_check)
    if checks[-1]["passed"]:
        for entry in manifest["files"]:
            check("integrity", entry["path"], lambda e=entry: require(
                sha256(safe_path(e["path"])) == e["sha256"], "checksum mismatch"))

    def metadata_check():
        desc = read_json(root / "export/dataset_description.json")
        require(isinstance(desc, dict) and isinstance(desc.get("Name"), str) and bool(desc["Name"]), "Invalid dataset name")
        require(desc.get("BIDSVersion") == "1.11.2" and desc.get("DatasetType") == "raw", "Unexpected teaching dataset description")
        require(desc["GeneratedBy"][0]["Version"] == VERSION, "Generator version mismatch")
        participants = read_table(root / "export/participants.tsv", "\t", ["participant_id", "group"])
        require(participants == [{"participant_id": SUBJECT, "group": "synthetic"}], "Participant linkage mismatch")
        sidecar = read_json(root / SIDECAR)
        require(sidecar["onset"]["Units"] == "s" and sidecar["duration"]["Units"] == "s", "Time unit mismatch")
        require(sidecar["onset"]["Description"] == f"Event onset in seconds from the {TIME_ORIGIN}", "Time-origin definition mismatch")
        require(sidecar["trial_type"]["Levels"] == {"go": "respond", "nogo": "withhold"}, "Trial dictionary mismatch")
        source = read_json(root / "source/source_contract.json")
        require(source["time_ms"] == {"Units": "ms", "TimeOrigin": TIME_ORIGIN} and source["code"]["Levels"] == CODE_MAP,
                "Source meaning mismatch")

    check("semantics", "metadata and observation linkage", metadata_check)

    def event_check():
        rows = read_table(root / EVENTS, "\t", ["onset", "duration", "trial_type"])
        for row in rows:
            number(row["onset"])
            require(number(row["duration"]) >= 0, "Negative duration")
            require(row["trial_type"] in CODE_MAP.values(), "Unknown trial type")

    check("structure", "event columns and values", event_check)

    def preservation_check():
        require(manifest is not None, "Missing manifest")
        require(manifest["conversion"] == {"source_unit": "ms", "target_unit": "s", "factor": 0.001,
                    "time_origin": TIME_ORIGIN, "code_map": CODE_MAP, "tool_version": VERSION}, "Conversion contract mismatch")
        expected = convert(root / SOURCE)
        actual = read_table(root / EVENTS, "\t", ["onset", "duration", "trial_type"])
        require(len(expected) == len(actual), "Source/target event count mismatch")
        for a, e in zip(actual, expected):
            require(number(a["onset"]) == e["onset"] and number(a["duration"]) == e["duration"]
                    and a["trial_type"] == e["trial_type"], "Source-to-target meaning mismatch")

    check("semantics", "conversion preservation", preservation_check)
    report = {"teaching_dataset": True, "contract_version": VERSION,
              "bids_compliant": "not established; no corresponding task recording; use official BIDS validation for real datasets",
              "checks": checks, "errors": errors, "passed_local_checks": not errors,
              "scientific_audit_required": True, "governance_review": "not established by this synthetic validator"}
    root.mkdir(parents=True, exist_ok=True)
    write_json(root / "validation_report.json", report)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs/ch09")
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--force", action="store_true", help="Explicitly regenerate known synthetic demo files")
    args = parser.parse_args()
    if args.force and args.validate_only:
        parser.error("--force applies only to generation")
    try:
        report = validate(args.output_dir) if args.validate_only else build(args.output_dir, args.force)
    except (OSError, ValueError) as exc:
        print(json.dumps({"passed_local_checks": False, "errors": [str(exc)]}, indent=2))
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["passed_local_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
