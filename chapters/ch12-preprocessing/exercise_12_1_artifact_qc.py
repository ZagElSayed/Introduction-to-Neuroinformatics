"""Synthetic preprocessing sensitivity, with known sources and preserved run artifacts.

Standard library only. Offline smoothing is neither ICA nor validated artifact removal.
The generator's known sources support a teaching comparison, not clinical validation.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import uuid

FS = 250
N_SAMPLES = 500
CHANNELS = ("Fz_uV", "Pz_uV")
PIPELINE_VERSION = "2.0"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_window(width, length):
    if type(width) is not int or width < 1 or width % 2 != 1 or width > length:
        raise ValueError("window must be an odd integer from 1 through the sample count")


def source_rows(n=N_SAMPLES, fs=FS):
    """Known mixture: neural + ocular transient + drift, in microvolts."""
    if type(n) is not int or n < 1 or not math.isfinite(fs) or fs <= 0:
        raise ValueError("positive sample count and finite sampling rate required")
    raw, truth = [], []
    for i in range(n):
        t = i / fs
        neural = 12 * math.sin(2 * math.pi * 10 * t)
        blink = 85 * max(0, 1 - abs(t - 0.8) / 0.12)
        drift = 7 * math.sin(2 * math.pi * 0.5 * t)
        raw.append({"sample": i, "time_s": t, "Fz_uV": neural + blink + drift,
                    "Pz_uV": 0.8 * neural + 0.25 * blink + drift,
                    "EOG_uV": blink})
        truth.append({"sample": i, "time_s": t, "Fz_neural_uV": neural,
                      "Pz_neural_uV": 0.8 * neural, "blink_uV": blink, "drift_uV": drift})
    return raw, truth


def make_data(n=N_SAMPLES, fs=FS):
    return source_rows(n, fs)[0]


def moving_average(values, width):
    """Centered offline boxcar; edges use a shorter, renormalized window."""
    validate_window(width, len(values))
    if not all(math.isfinite(v) for v in values):
        raise ValueError("all signal values must be finite")
    half = width // 2
    return [sum(values[max(0, i-half):min(len(values), i+half+1)]) /
            (min(len(values), i+half+1)-max(0, i-half)) for i in range(len(values))]


def metrics(values):
    if not values or not all(math.isfinite(v) for v in values):
        raise ValueError("nonempty finite data required")
    return {"peak_abs_uV": max(abs(v) for v in values),
            "rms_uV": math.sqrt(sum(v*v for v in values) / len(values))}


def rmse(a, b):
    if not a or len(a) != len(b):
        raise ValueError("equal nonempty vectors required")
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)) / len(a))


def write_csv(path, rows):
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def qc_svg(path, raw, truth, processed):
    """Two channels, one fixed amplitude scale; full source is retained in CSV."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="610" viewBox="0 0 1100 610">',
             '<rect width="1100" height="610" fill="white"/>',
             '<g font-family="sans-serif" fill="#142D4E">',
             '<text x="70" y="35" font-size="23">Synthetic QC: raw, smoothed, and known neural source</text>',
             '<text x="70" y="62" font-size="17">Raw: gray | Smoothed: teal | Known neural: violet | Fixed scale in microvolts</text>']
    for k, channel in enumerate(CHANNELS):
        mid = 235 + k * 245
        parts.append(f'<text x="70" y="{mid-130}" font-size="21">{channel}</text>')
        for value in (-40, 0, 40, 80):
            y = mid-value*1.05
            parts.append(f'<path d="M90 {y} H1050" stroke="#E4EAF0"/><text x="45" y="{y+5}" font-size="14">{value}</text>')
        sources = [([r[channel] for r in raw], '#8794A5'),
                   (processed[channel], '#167D91'),
                   ([r[channel.replace('_uV', '_neural_uV')] for r in truth], '#7556A8')]
        for values, color in sources:
            points = ' '.join(f'{90+960*i/(len(values)-1):.2f},{mid-v*1.05:.2f}' for i, v in enumerate(values))
            parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.5"/>')
        for i in (0, 125, 250, 375, 499):
            parts.append(f'<text x="{90+960*i/499:.1f}" y="{mid+86}" font-size="14">{i/FS:.2f}</text>')
    parts.extend(['<text x="460" y="590" font-size="18">Time (seconds)</text>', '</g></svg>'])
    path.write_text(''.join(parts), encoding="utf-8")


def run(output_dir, window=11):
    validate_window(window, N_SAMPLES)
    root = Path(output_dir)
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise FileExistsError("Use a new or empty output directory; previous runs are preserved")
    rows, truth = source_rows()
    signals = {ch: [r[ch] for r in rows] for ch in CHANNELS}
    processed = {ch: moving_average(values, window) for ch, values in signals.items()}
    half = window // 2
    interior = slice(half, N_SAMPLES-half) if half else slice(None)
    comparisons = {}
    for ch in CHANNELS:
        neural = [r[ch.replace('_uV', '_neural_uV')] for r in truth]
        filtered_neural = moving_average(neural, window)
        nuisance = [x-s for x, s in zip(signals[ch], neural)]
        filtered_nuisance = moving_average(nuisance, window)
        comparisons[ch] = {
            "raw_vs_neural_rmse_uV": rmse(signals[ch][interior], neural[interior]),
            "derivative_vs_neural_rmse_uV": rmse(processed[ch][interior], neural[interior]),
            "neural_only_filter_rmse_uV": rmse(filtered_neural[interior], neural[interior]),
            "remaining_filtered_nuisance_rms_uV": metrics(filtered_nuisance[interior])["rms_uV"],
        }
    root.mkdir(parents=True, exist_ok=True)
    write_csv(root / "synthetic_raw.csv", rows)
    write_csv(root / "synthetic_truth.csv", truth)
    events = [{"sample": 250, "time_s": 1.0, "event": "stimulus", "interpretation": "timing marker only"}]
    write_csv(root / "events.csv", events)
    derivative = [{"sample": r["sample"], "time_s": r["time_s"],
                   "Fz_smoothed_uV": processed["Fz_uV"][i],
                   "Pz_smoothed_uV": processed["Pz_uV"][i],
                   "edge_window_truncated": i < half or i >= N_SAMPLES-half}
                  for i, r in enumerate(rows)]
    write_csv(root / "synthetic_smoothed.csv", derivative)
    qc_svg(root / "qc_comparison.svg", rows, truth, processed)
    config = {"window_samples": window, "sampling_rate_hz": FS, "n_samples": N_SAMPLES,
              "method": "centered moving average", "edge_policy": "truncate and renormalize",
              "units": "microvolts", "neural_frequency_hz": 10,
              "reference": "synthetic mixture; no physical electrode reference"}
    config_bytes = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    # Interior signed response for an odd centered boxcar; edges have different weights.
    omega = 2 * math.pi * 10 / FS
    gain = math.sin(window * omega / 2) / (window * math.sin(omega / 2))
    report = {
        "synthetic": True, "pipeline_version": PIPELINE_VERSION,
        "run_id": str(uuid.uuid4()), "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(), "script_sha256": sha256(__file__),
        "configuration": config, "configuration_sha256": hashlib.sha256(config_bytes).hexdigest(),
        "n_samples": N_SAMPLES, "sampling_rate_hz": FS, "window_samples": window,
        "window_duration_ms": window / FS * 1000,
        "interior_sample_range": [half, N_SAMPLES-half], "range_convention": "start inclusive, stop exclusive",
        "edge_samples": 2 * half, "lookahead_samples": half, "causal": False,
        "interior_signed_gain_at_10_hz": gain, "interior_magnitude_gain_at_10_hz": abs(gain),
        "raw_metrics": {ch: metrics(v) for ch, v in signals.items()},
        "derivative_metrics": {ch: metrics(v) for ch, v in processed.items()},
        "known_source_comparison_interior": comparisons,
        "known_artifact": "triangular ocular transient centered at 0.8 seconds plus slow drift",
        "events_preserved": True, "resampled": False,
        "review_status": "review_required", "accepted_as_neurally_valid": False,
        "scientific_warning": "Smoothing can attenuate both nuisance and neural sources; no ICA, artifact removal, ERP validation, or clinical inference performed",
        "artifacts_sha256": {name: sha256(root / name) for name in
                             ("synthetic_raw.csv", "synthetic_truth.csv", "events.csv", "synthetic_smoothed.csv", "qc_comparison.svg")},
    }
    report["input_sha256"] = report["artifacts_sha256"]["synthetic_raw.csv"]
    report["output_sha256"] = report["artifacts_sha256"]["synthetic_smoothed.csv"]
    (root / "qc_provenance.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs/ch12/w11")
    parser.add_argument("--window", type=int, default=11)
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir, args.window), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
