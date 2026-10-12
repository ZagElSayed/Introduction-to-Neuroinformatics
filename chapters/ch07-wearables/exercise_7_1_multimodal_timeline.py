"""Chapter 7: reproducible synthetic ECG, accelerometry, event synchronization and QC.

No clinical data. Time is in seconds, ECG in mV, acceleration in m/s^2.
Requires numpy and matplotlib only.
"""
import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def generate(seed=42, duration=120.0, clock_offset=0.250):
    """Generate independent clocks; ECG device timestamps are offset from reference."""
    rng = np.random.default_rng(seed)
    fs_ecg, fs_imu = 250.0, 50.0
    t_ecg_ref = np.arange(int(duration * fs_ecg)) / fs_ecg
    t_imu = np.arange(int(duration * fs_imu)) / fs_imu
    beat_times = np.arange(0.65, duration - 0.3, 0.83)
    # Narrow synthetic R-peaks, slow baseline, and measurement noise.
    ecg = 0.04 * np.sin(2 * np.pi * 0.22 * t_ecg_ref)
    ecg += rng.normal(0, 0.018, t_ecg_ref.size)
    for beat in beat_times:
        left = max(0, int((beat - 0.05) * fs_ecg))
        right = min(len(ecg), int((beat + 0.05) * fs_ecg) + 1)
        ecg[left:right] += 0.95 * np.exp(-0.5 * ((t_ecg_ref[left:right] - beat) / 0.012) ** 2)
    active = (t_imu >= 40) & (t_imu < 80)
    acceleration = rng.normal(0, 0.12, (len(t_imu), 3))
    acceleration[:, 2] += 9.81
    acceleration[active, 0] += 1.8 * np.sin(2 * np.pi * 1.7 * t_imu[active])
    acceleration[active, 1] += 1.2 * np.cos(2 * np.pi * 1.7 * t_imu[active])
    # Known transport loss on IMU, not missing physiological zeros.
    missing = (t_imu >= 55) & (t_imu < 58)
    acceleration[missing] = np.nan
    return {
        "ecg_t_device": t_ecg_ref + clock_offset,
        "ecg_t_reference": t_ecg_ref,
        "ecg_mv": ecg,
        "imu_t_reference": t_imu,
        "accel_mps2": acceleration,
        "imu_valid": ~missing,
        "beat_times_reference": beat_times,
        "events": [(40.0, "activity_start"), (80.0, "activity_end")],
        "clock_offset_seconds": clock_offset,
        "seed": seed,
    }


def _write_csv(path, headers, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def analyze(data, output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    t_ecg = data["ecg_t_reference"]
    t_imu = data["imu_t_reference"]
    accel = data["accel_mps2"]
    valid = data["imu_valid"]
    magnitude = np.linalg.norm(accel, axis=1)
    beats = data["beat_times_reference"]
    rr = np.diff(beats)
    bpm = 60 / rr
    # Heart rate at beat midpoint; only measured within the supported beat interval.
    beat_mid = (beats[1:] + beats[:-1]) / 2
    grid = np.arange(1.0, int(t_imu[-1]), 1.0)
    heart_rate = np.interp(grid, beat_mid, bpm, left=np.nan, right=np.nan)
    activity = np.full(len(grid), np.nan)
    coverage = np.zeros(len(grid))
    for i, start in enumerate(grid):
        in_window = (t_imu >= start) & (t_imu < start + 1)
        coverage[i] = valid[in_window].mean() if in_window.any() else 0.0
        if coverage[i] >= 0.8:
            activity[i] = np.nanmean(magnitude[in_window])
    _write_csv(out / "ecg_native.csv", ["device_time_s", "reference_time_s", "ecg_mV"],
               zip(data["ecg_t_device"], t_ecg, data["ecg_mv"]))
    _write_csv(out / "imu_native.csv", ["reference_time_s", "ax_mps2", "ay_mps2", "az_mps2", "valid"],
               ((t, *a, int(v)) for t, a, v in zip(t_imu, accel, valid)))
    _write_csv(out / "events.csv", ["reference_time_s", "event"], data["events"])
    _write_csv(out / "analysis_table.csv",
               ["reference_time_s", "heart_rate_bpm", "accel_magnitude_mean_mps2", "imu_coverage_fraction"],
               zip(grid, heart_rate, activity, coverage))
    # Event-centered means demonstrate a known 250-ms offset error.
    event = data["events"][0][0]
    half_width = 0.15
    corrected = np.abs(t_ecg - event) < half_width
    uncorrected = np.abs(data["ecg_t_device"] - event) < half_width
    means = {"corrected_ecg_mean_mV": float(data["ecg_mv"][corrected].mean()),
             "uncorrected_ecg_mean_mV": float(data["ecg_mv"][uncorrected].mean())}
    fig, axes = plt.subplots(3, 1, figsize=(11, 8), sharex=True)
    axes[0].plot(t_ecg, data["ecg_mv"], lw=0.5)
    axes[0].set_ylabel("ECG (mV)")
    axes[1].plot(t_imu, magnitude, lw=0.6)
    axes[1].set_ylabel("Acceleration (m/s²)")
    axes[2].plot(grid, heart_rate, label="Heart rate (bpm)")
    axes[2].set_ylabel("Heart rate (bpm)")
    axes[2].set_xlabel("Reference time (s)")
    for ax in axes:
        for time, _ in data["events"]:
            ax.axvline(time, ls="--", lw=1, color="black")
        ax.axvspan(55, 58, alpha=0.12, color="red")
    fig.tight_layout()
    fig.savefig(out / "multimodal_timeline.png", dpi=150)
    plt.close(fig)
    summary = {
        "source": "synthetic, not clinical", "seed": data["seed"],
        "duration_seconds": float(t_ecg[-1] + 1 / 250),
        "ecg_sampling_hz": 250, "imu_sampling_hz": 50,
        "ecg_clock_offset_seconds": data["clock_offset_seconds"],
        "clock_correction": "reference_time_s = device_time_s - ecg_clock_offset_seconds",
        "imu_missing_interval_seconds": [55, 58],
        "imu_coverage_fraction": float(valid.mean()),
        "derived_table_hz": 1,
        "quality_rule": "mean acceleration is NaN if <80% of samples in one-second bin are valid",
        "ecg_beat_source": "synthetic generator ground-truth beats; not an R-peak detector",
        "event_centered_example": means,
        "caveats": ["No physiological forward model", "Heart rate uses known synthetic beat times",
                    "Correlation and activity summaries are not diagnoses"],
    }
    (out / "metadata.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/ch07")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    result = analyze(generate(seed=args.seed), args.output_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
