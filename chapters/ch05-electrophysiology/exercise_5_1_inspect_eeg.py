"""Chapter 5 reproducible exercise: inspect one public EEG EDF recording.

Requires MNE, NumPy, and Matplotlib from the companion repository requirements.
Usage:
    python exercise_5_1_inspect_eeg.py --edf /path/to/S001R01.edf --output-dir outputs/ch05
This exercise never modifies its input recording and makes no clinical diagnosis.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np


def run(edf: Path, output_dir: Path, seconds: float = 20.0) -> None:
    if not edf.is_file():
        raise FileNotFoundError(f"EDF recording not found: {edf}")
    if seconds <= 0:
        raise ValueError("seconds must be positive")
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = mne.io.read_raw_edf(str(edf), preload=False, verbose="ERROR")
    sfreq = float(raw.info["sfreq"])
    duration = raw.n_times / sfreq
    picks = mne.pick_types(raw.info, eeg=True, exclude=[])
    if len(picks) == 0:
        raise ValueError("The EDF does not contain EEG channels recognized by MNE.")
    selected = picks[: min(6, len(picks))]
    stop = min(int(seconds * sfreq), raw.n_times)
    if stop < 2:
        raise ValueError("Recording is too short for analysis.")
    signals, times = raw[selected, :stop]
    signals_uv = signals * 1e6  # MNE converts EEG channels to SI volts

    fig, axes = plt.subplots(len(selected), 1, figsize=(11, max(5, 1.5 * len(selected))), sharex=True)
    axes = np.atleast_1d(axes)
    for ax, channel, values in zip(axes, (raw.ch_names[i] for i in selected), signals_uv):
        ax.plot(times, values, linewidth=0.6)
        ax.set_ylabel(f"{channel}\n(µV)")
    axes[-1].set_xlabel("Time (s)")
    fig.suptitle("Raw EEG excerpt — inspect, do not diagnose")
    fig.tight_layout()
    fig.savefig(output_dir / "raw_segment.png", dpi=160)
    plt.close(fig)

    # Welch PSD uses the first selected excerpt; direct FFT segment count is explicit.
    from scipy.signal import welch
    fig, ax = plt.subplots(figsize=(10, 5))
    nperseg = min(stop, max(16, int(2 * sfreq)))
    for channel, values in zip((raw.ch_names[i] for i in selected), signals):
        freqs, power = welch(values, fs=sfreq, nperseg=nperseg)
        mask = (freqs >= 0.5) & (freqs <= min(45.0, sfreq / 2))
        ax.plot(freqs[mask], 10 * np.log10(np.maximum(power[mask] * 1e12, 1e-20)), label=channel)
    ax.set(xlabel="Frequency (Hz)", ylabel="Power spectral density (dB re 1 µV²/Hz)",
           title="Welch PSD (illustrative research analysis)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(output_dir / "psd.png", dpi=160)
    plt.close(fig)

    montage = raw.get_montage()
    summary = {
        "source_file": edf.name,
        "dataset": "PhysioNet EEG Motor Movement/Imagery v1.0.0 (S001R01 recommended)",
        "sampling_rate_hz": sfreq,
        "duration_seconds": duration,
        "total_channel_count": len(raw.ch_names),
        "eeg_channel_count": len(picks),
        "selected_eeg_channels": [raw.ch_names[i] for i in selected],
        "annotation_count": len(raw.annotations),
        "annotation_descriptions": sorted(set(raw.annotations.description.tolist())),
        "montage_available": montage is not None,
        "analyzed_excerpt_seconds": float(times[-1]) if len(times) else 0,
        "welch_nperseg": nperseg,
        "mne_version": mne.__version__,
        "notes": [
            "Artifact identification needs physiological and acquisition context.",
            "These figures are educational and do not support clinical diagnoses.",
            "The original EDF was read but not modified.",
        ],
    }
    (output_dir / "recording_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Figures and summary saved in {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--edf", required=True, type=Path, help="Local path to the original public EDF")
    parser.add_argument("--output-dir", default=Path("outputs/ch05-exercise-5-1"), type=Path)
    parser.add_argument("--seconds", default=20.0, type=float)
    args = parser.parse_args()
    run(args.edf, args.output_dir, args.seconds)


if __name__ == "__main__":
    main()
