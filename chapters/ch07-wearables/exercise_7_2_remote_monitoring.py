"""Chapter 7 extension: quality-aware monitoring and engineering audit (synthetic only)."""
import argparse
import csv
import json
from pathlib import Path


def rows(path):
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def audit(input_dir, output_dir):
    source = Path(input_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = json.loads((source / "metadata.json").read_text(encoding="utf-8"))
    table = rows(source / "analysis_table.csv")
    if meta.get("source") != "synthetic, not clinical":
        raise ValueError("Only the Chapter 7 synthetic teaching dataset is supported")
    required = {"reference_time_s", "heart_rate_bpm", "accel_magnitude_mean_mps2", "imu_coverage_fraction"}
    if not table or not required.issubset(table[0]):
        raise ValueError("Missing expected 1-Hz analysis fields")
    windows = []
    for item in table:
        coverage = float(item["imu_coverage_fraction"])
        if not 0 <= coverage <= 1:
            raise ValueError("Coverage must be between 0 and 1")
        t = float(item["reference_time_s"])
        windows.append({"reference_time_s": t, "imu_coverage_fraction": coverage,
                        "quality_status": "usable" if coverage >= 0.8 else "exclude",
                        "candidate_feature_eligible": coverage >= 0.8})
    # 16-bit channels: ECG 250 Hz, PPG 100 Hz, EDA 25 Hz, 3-axis IMU 50 Hz.
    rate_bytes_s = (250 + 100 + 25 + 3 * 50) * 2
    outage_s = 12 * 60
    raw_buffer_bytes = rate_bytes_s * outage_s
    excluded = [w for w in windows if w["quality_status"] == "exclude"]
    result = {
        "source": "synthetic, not clinical",
        "purpose": "engineering feasibility and feature-quality audit, not diagnosis",
        "input_provenance": {"seed": meta["seed"], "ecg_clock_offset_seconds": meta["ecg_clock_offset_seconds"],
                             "native_ecg_hz": meta["ecg_sampling_hz"], "native_imu_hz": meta["imu_sampling_hz"]},
        "coverage": {"total_windows": len(windows), "excluded_windows": len(excluded),
                     "usable_windows": len(windows) - len(excluded),
                     "excluded_window_start_s": [w["reference_time_s"] for w in excluded]},
        "engineering": {"hypothetical_ecg_ppg_eda_imu_raw_bytes_per_second": rate_bytes_s,
                        "hypothetical_12_minute_outage_payload_bytes": raw_buffer_bytes,
                        "hypothetical_8_hour_payload_bytes": rate_bytes_s * 8 * 3600,
                        "hypothetical_100_participants_30_days_payload_bytes": rate_bytes_s * 8 * 3600 * 100 * 30,
                        "excluded_overhead": ["timestamps", "metadata", "encryption", "headers", "filesystem", "retransmission", "EEG"]},
        "interpretation": {"transport_gap_vs_sensor_gap": "Buffered network outages need not cause missing samples; electrode detachment can cause invalid measurements even when packets arrive.",
                           "biomarker_status": "exploratory features only; no clinical validity established",
                           "quality_rule": "Exclude IMU-derived candidate features if 1-second coverage is below 0.8"},
    }
    with (out / "quality_windows.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(windows[0]))
        writer.writeheader()
        writer.writerows(windows)
    (out / "engineering_audit.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="outputs/ch07")
    parser.add_argument("--output-dir", default="outputs/ch07/audit")
    args = parser.parse_args()
    print(json.dumps(audit(args.input_dir, args.output_dir), indent=2))


if __name__ == "__main__":
    main()
