"""Chapter 8: reproducible synthetic Go/No-Go event protocol and QC.
Synthetic timestamps are software logs, not validated physical display onsets.
"""
import argparse
import csv
import json
import random
from pathlib import Path

FIELDS = ["trial_id", "condition", "stimulus_code", "planned_onset_s", "software_onset_s",
          "reference_onset_s", "response", "correct", "reaction_time_s"]


def generate(seed=8, trials=48):
    if trials < 40:
        raise ValueError("At least 40 trials required")
    rng = random.Random(seed)
    conditions = (["go"] * (trials // 2)) + (["nogo"] * (trials - trials // 2))
    rng.shuffle(conditions)
    result = []
    for i, condition in enumerate(conditions):
        planned = 1.0 + i * 1.5
        onset = planned + rng.uniform(-0.012, 0.012)
        responded = (rng.random() < (0.9 if condition == "go" else 0.1))
        rt = round(rng.uniform(0.23, 0.69), 4) if responded else ""
        result.append({"trial_id": f"T{i+1:03d}", "condition": condition,
                       "stimulus_code": "G" if condition == "go" else "N",
                       "planned_onset_s": round(planned, 4),
                       "software_onset_s": round(onset, 4),
                       "reference_onset_s": round(onset, 4),
                       "response": "key" if responded else "",
                       "correct": int(responded == (condition == "go")),
                       "reaction_time_s": rt})
    return result


def validate(events, reference, offset_threshold_s=0.05):
    ids = [row["trial_id"] for row in events]
    duplicates = len(ids) - len(set(ids))
    missing = len(set(reference) - set(ids))
    mismatched = []
    implausible_rt = []
    for row in events:
        tid = row["trial_id"]
        if tid in reference and abs(float(row["software_onset_s"]) - reference[tid]) > offset_threshold_s:
            mismatched.append(tid)
        rt = row["reaction_time_s"]
        if rt != "" and not 0.15 <= float(rt) <= 1.5:
            implausible_rt.append(tid)
    return {"n_trials": len(events), "duplicate_trial_ids": duplicates,
            "missing_reference_trials": missing, "onset_mismatch_trial_ids": mismatched,
            "implausible_reaction_time_trial_ids": implausible_rt,
            "task_accuracy": sum(int(row["correct"]) for row in events) / len(events) if events else None}


def write_tsv(path, events):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(events)


def run(output_dir, seed=8, trials=48):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    original = generate(seed, trials)
    shifted = [dict(row) for row in original]
    for row in shifted:
        row["software_onset_s"] = round(row["software_onset_s"] + 0.1, 4)
    reference = {row["trial_id"]: float(row["reference_onset_s"]) for row in original}
    write_tsv(out / "events.tsv", original)
    write_tsv(out / "events_offset_100ms.tsv", shifted)
    qc = {"baseline": validate(original, reference), "injected_offset": validate(shifted, reference)}
    metadata = {"source": "synthetic teaching data, not human recordings",
                "participant_id": "sub-demo01", "session_id": "ses-01",
                "task": "simulated Go/No-Go", "seed": seed, "trials": trials,
                "event_code_definitions": {"G": "go", "N": "nogo"},
                "units": {"onset": "seconds", "reaction_time": "seconds"},
                "timing_warning": "Software timestamps are not physical display onset; validate hardware timing separately",
                "software": "Python standard library", "version": "1.0",
                "display_refresh_hz": "unknown (synthetic; no physical display)",
                "event_columns": {field: field.replace("_", " ") for field in FIELDS}}
    (out / "task_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (out / "qc_report.json").write_text(json.dumps(qc, indent=2), encoding="utf-8")
    return qc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/ch08")
    parser.add_argument("--seed", type=int, default=8)
    parser.add_argument("--trials", type=int, default=48)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir, args.seed, args.trials), indent=2))


if __name__ == "__main__":
    main()
