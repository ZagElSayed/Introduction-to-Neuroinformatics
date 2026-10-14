"""Create isolated corruption examples; preserve baseline evidence and reports."""
import argparse
import json
import shutil
from pathlib import Path
import exercise_9_1_neurodata_contract as lab


def demonstrate(output_dir):
    root = Path(output_dir)
    if root.exists() and any(root.iterdir()):
        raise ValueError("Choose an empty directory for the failure demonstrations")
    baseline = root / "baseline"
    lab.build(baseline)
    summary = []
    for name in ("source_change", "unit_metadata", "unknown_trial", "nonfinite_time", "meaning_with_rehashed_target"):
        case = root / name
        shutil.copytree(baseline, case)
        if name == "source_change":
            p = case / lab.SOURCE
            p.write_bytes(p.read_bytes() + b"\n")
        elif name == "unit_metadata":
            p = case / lab.SIDECAR
            data = lab.read_json(p)
            data["onset"]["Units"] = "ms"
            lab.write_json(p, data)
        else:
            p = case / lab.EVENTS
            old, new = {"unknown_trial": ("go\n", "unknown\n"),
                        "nonfinite_time": ("0.5", "nan"),
                        "meaning_with_rehashed_target": ("0.5", "500.0")}[name]
            p.write_text(p.read_text().replace(old, new), encoding="utf-8")
        if name == "meaning_with_rehashed_target":
            manifest = lab.read_json(case / "manifest.json")
            shutil.copy(case / "manifest.json", case / "manifest_before_rehash.json")
            for entry in manifest["files"]:
                if entry["path"] == lab.EVENTS:
                    entry["sha256"] = lab.sha256(case / lab.EVENTS)
            lab.write_json(case / "manifest.json", manifest)
        report = lab.validate(case)
        summary.append({"case": name, "expected_failure_detected": not report["passed_local_checks"], "errors": report["errors"]})
    lab.write_json(root / "failure_summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs/ch09-failures")
    args = parser.parse_args()
    try:
        result = demonstrate(args.output_dir)
    except (OSError, ValueError) as exc:
        print(str(exc))
        return 1
    print(json.dumps(result, indent=2))
    return 0 if all(case["expected_failure_detected"] for case in result) else 1


if __name__ == "__main__":
    raise SystemExit(main())
