"""Chapter 12: synthetic EEG artifact QC and transparent preprocessing demonstration.
Educational simulation only: not clinical EEG and not a replacement for MNE/ICA review.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def make_data(n=500, fs=250):
    rows = []
    for i in range(n):
        t = i / fs
        neural = 12 * math.sin(2 * math.pi * 10 * t)
        blink = 85 * max(0, 1 - abs(t - 0.8) / 0.12)
        drift = 7 * math.sin(2 * math.pi * 0.5 * t)
        rows.append({"time_s": round(t, 6), "Fz_uV": round(neural + blink + drift, 6),
                     "Pz_uV": round(0.8 * neural + 0.25 * blink + drift, 6),
                     "EOG_uV": round(blink, 6), "event": "stimulus" if i == 250 else ""})
    return rows

def moving_average(x, width):
    if width < 1 or width % 2 != 1:
        raise ValueError("width must be a positive odd integer")
    half = width // 2
    return [sum(x[max(0, i-half):min(len(x), i+half+1)]) /
            (min(len(x), i+half+1)-max(0, i-half)) for i in range(len(x))]

def run(output_dir, window=11):
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    raw = root / "synthetic_raw.csv"
    rows = make_data()
    with raw.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    signals = {ch: [r[ch] for r in rows] for ch in ("Fz_uV", "Pz_uV")}
    # Moving average illustrates smoothing, NOT a validated EEG band-pass or artifact remover.
    processed = {ch: moving_average(values, window) for ch, values in signals.items()}
    derivative = root / "synthetic_smoothed.csv"
    with derivative.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time_s", "Fz_smoothed_uV", "Pz_smoothed_uV"])
        for i, r in enumerate(rows):
            writer.writerow([r["time_s"], round(processed["Fz_uV"][i], 6),
                             round(processed["Pz_uV"][i], 6)])
    def metrics(values):
        return {"peak_abs_uV": max(abs(x) for x in values),
                "rms_uV": math.sqrt(sum(x*x for x in values)/len(values))}
    report = {"synthetic": True, "sampling_rate_hz": 250, "n_samples": len(rows),
              "processing": "centered moving average; illustrative only",
              "window_samples": window, "window_duration_ms": window / 250 * 1000,
              "raw_metrics": {k: metrics(v) for k, v in signals.items()},
              "derivative_metrics": {k: metrics(v) for k, v in processed.items()},
              "known_artifact": "simulated frontal blink centered at 0.8 s",
              "scientific_warning": "Smoothing may distort transients and attenuate neural activity; no artifact removal or ICA performed",
              "input_sha256": sha256(raw), "output_sha256": sha256(derivative),
              "pipeline_version": "1.0"}
    (root / "qc_provenance.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", default="outputs/ch12")
    p.add_argument("--window", type=int, default=11)
    a = p.parse_args()
    print(json.dumps(run(a.output_dir, a.window), indent=2))

if __name__ == "__main__":
    main()
