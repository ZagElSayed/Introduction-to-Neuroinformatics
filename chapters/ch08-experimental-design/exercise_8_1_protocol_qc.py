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
    """Report quality flags without deleting or modifying any observations.

    The timing and RT limits are teaching parameters, not validated
    instrument specifications or universal physiological thresholds.
    """
    import math
    if not math.isfinite(offset_threshold_s) or offset_threshold_s < 0:
        raise ValueError("Offset threshold must be finite and non-negative")
    if any(not math.isfinite(float(v)) for v in reference.values()):
        raise ValueError("Reference timestamps must be finite")
    ids = [row.get("trial_id", "") for row in events]
    duplicates = len(ids) - len(set(ids))
    missing = len(set(reference) - set(ids))
    unexpected = sorted(set(ids) - set(reference))
    mismatched, implausible_rt, schema_errors, inconsistent = [], [], [], []
    behavior_correct = []
    expected_codes = {"go": "G", "nogo": "N"}

    for index, row in enumerate(events):
        tid = row.get("trial_id", "")
        def flag(field, reason):
            schema_errors.append({"row": index + 1, "trial_id": tid,
                                  "field": field, "reason": reason})
        for field in FIELDS:
            if field not in row:
                flag(field, "missing required column")
        if not isinstance(tid, str) or not tid.strip():
            flag("trial_id", "non-empty string required")
        condition = row.get("condition")
        code = row.get("stimulus_code")
        if condition not in expected_codes:
            flag("condition", "expected go or nogo")
        if code not in ("G", "N"):
            flag("stimulus_code", "unknown event code")
        elif condition in expected_codes and code != expected_codes[condition]:
            flag("stimulus_code", "code does not match condition")

        numbers = {}
        for field in ("planned_onset_s", "software_onset_s", "reference_onset_s"):
            try:
                value = float(row.get(field))
                if not math.isfinite(value) or value < 0:
                    raise ValueError
                numbers[field] = value
            except (TypeError, ValueError, OverflowError):
                flag(field, "finite non-negative seconds required")
        if tid in reference and "software_onset_s" in numbers:
            if abs(numbers["software_onset_s"] - float(reference[tid])) > offset_threshold_s:
                mismatched.append(tid)

        response = row.get("response")
        rt = row.get("reaction_time_s")
        if response not in ("", "key"):
            flag("response", "expected blank or key")
        if response == "key":
            try:
                value = float(rt)
                if not math.isfinite(value):
                    raise ValueError
                if not 0.15 <= value <= 1.5:
                    implausible_rt.append(tid)
            except (TypeError, ValueError, OverflowError):
                flag("reaction_time_s", "response requires finite reaction time")
        elif response == "" and rt != "":
            flag("reaction_time_s", "withheld response requires blank reaction time")

        if condition in expected_codes and response in ("", "key"):
            computed = int((response == "key") == (condition == "go"))
            behavior_correct.append(computed)
            try:
                recorded = float(row.get("correct"))
                if not math.isfinite(recorded) or recorded not in (0, 1):
                    raise ValueError
                if recorded != computed:
                    inconsistent.append(tid)
            except (TypeError, ValueError, OverflowError):
                flag("correct", "expected binary 0 or 1")

    return {"n_trials": len(events), "duplicate_trial_ids": duplicates,
            "missing_reference_trials": missing, "unexpected_trial_ids": unexpected,
            "onset_mismatch_trial_ids": mismatched,
            "implausible_reaction_time_trial_ids": implausible_rt,
            "schema_errors": schema_errors,
            "inconsistent_correctness_trial_ids": inconsistent,
            "behavior_evaluable_rows": len(behavior_correct),
            "task_accuracy": (sum(behavior_correct) / len(behavior_correct)
                              if behavior_correct else None)}


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
                "software": "Python standard library", "version": "1.1",
                "display_refresh_hz": "unknown (synthetic; no physical display)",
                "qc_thresholds": {"offset_s": 0.05, "reaction_time_s": [0.15, 1.5],
                                  "scope": "synthetic teaching parameters; not hardware specifications"},
                "order_note": "balanced condition counts with randomized trial order, not AB/BA counterbalancing",
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
