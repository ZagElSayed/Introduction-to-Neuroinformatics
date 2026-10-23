"""Chapter 20: causal, hardware-free EEG replay. Student-run teaching code.

No device driver, live user feedback, therapeutic claim, or validated artifact QC.
Dataset: PhysioNet EEGMMIDB 1.0.0, S001 R04/R08/R12 only.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import importlib.metadata
import json
import math
import time
import uuid

import mne
import numpy as np
from scipy.signal import butter, sosfilt, welch
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, confusion_matrix
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class Config:
    subject: int = 1
    train_run: int = 4
    validation_run: int = 8
    test_run: int = 12
    channels: tuple[str, ...] = ("C3", "Cz", "C4")
    fs: float = 160.0
    window_samples: int = 320
    chunk_samples: int = 40
    threshold: float = 0.70
    dwell_updates: int = 3
    refractory_s: float = 1.0
    max_age_s: float = 0.50
    max_abs_v: float = 150e-6
    min_channel_std_v: float = 1e-9
    cursor_limit: int = 10

    def __post_init__(self):
        if (self.subject, self.train_run, self.validation_run, self.test_run) != (1, 4, 8, 12):
            raise ValueError("This teaching contract is S001 R04/R08/R12; extend explicitly.")
        if self.channels != ("C3", "Cz", "C4") or self.fs != 160.0:
            raise ValueError("Preserve the documented channel/rate contract.")
        if self.window_samples != 320 or self.chunk_samples != 40:
            raise ValueError("Use the fixed 2-s window and 0.25-s update in this edition.")
        if not 0.5 <= self.threshold <= 1 or self.dwell_updates < 1:
            raise ValueError("Invalid score threshold or dwell count.")
        if min(self.refractory_s, self.max_age_s, self.max_abs_v,
               self.min_channel_std_v, self.cursor_limit) <= 0:
            raise ValueError("Policy limits must be positive.")


def file_hash(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def filter_design(cfg):
    return butter(4, [7, 30], btype="bandpass", fs=cfg.fs, output="sos")


def features(window, cfg):
    """Past 2 s -> six log10 band-density integrals in fixed channel/band order.

    Mean removal and symmetric Hann taper use only the available window.
    FFT density uses volts**2/Hz; inclusive bin sums multiply by df (0.5 Hz).
    """
    if window.shape != (3, cfg.window_samples) or not np.isfinite(window).all():
        raise ValueError("Invalid feature window.")
    freqs, psd = welch(window, fs=cfg.fs, window=np.hanning(cfg.window_samples),
                      nperseg=cfg.window_samples, noverlap=0, nfft=cfg.window_samples,
                      detrend="constant", scaling="density", axis=-1)
    df = float(freqs[1] - freqs[0])
    powers = np.stack([psd[:, (freqs >= lo) & (freqs <= hi)].sum(axis=1) * df
                       for lo, hi in ((8, 12), (13, 30))], axis=1)
    return np.log10(np.maximum(powers, 1e-30)).ravel()


def raw_quality(block, cfg):
    """Illustrative packet checks; not physiological artifact validation."""
    if not np.isfinite(block).all():
        return "nonfinite"
    if np.max(np.abs(block)) > cfg.max_abs_v:
        return "amplitude_limit"
    if np.any(np.std(block, axis=1) < cfg.min_channel_std_v):
        return "flat_channel"
    return None


def load_runs(cfg=Config(), data_dir="bci_data"):
    """Downloads only the three documented public EDFs when not cached."""
    paths = mne.datasets.eegbci.load_data(
        cfg.subject, [cfg.train_run, cfg.validation_run, cfg.test_run],
        path=str(Path(data_dir).resolve()), update_path=False, verbose=False)
    if len(paths) != 3:
        raise ValueError("The source contract requires exactly three run files.")
    runs = {}
    for run, path in zip((cfg.train_run, cfg.validation_run, cfg.test_run), paths):
        raw = mne.io.read_raw_edf(path, preload=True, verbose=False)
        mne.datasets.eegbci.standardize(raw)
        if raw.first_samp != 0 or raw.info["sfreq"] != cfg.fs:
            raise ValueError("Unexpected sample origin or sampling rate; do not silently resample.")
        if any(ch not in raw.ch_names for ch in cfg.channels):
            raise ValueError("Required channel missing.")
        # MNE returns EEG in volts. No learned rereferencing or artifact fit.
        data = raw.get_data(picks=list(cfg.channels))
        if data.shape[0] != 3 or not np.isfinite(data).all():
            raise ValueError("Invalid EEG input.")
        intervals = []
        for onset, duration, description in zip(raw.annotations.onset,
                                                raw.annotations.duration,
                                                raw.annotations.description):
            if description not in {"T0", "T1", "T2"}:
                raise ValueError("Unexpected annotation; inspect the source contract.")
            a = max(0, int(round(float(onset) * cfg.fs)))
            b = min(data.shape[1], int(round((float(onset) + float(duration)) * cfg.fs)))
            if b > a:
                intervals.append((a, b, {"T0": 0, "T1": 1, "T2": 2}[description]))
        if not intervals:
            raise ValueError("No task intervals found.")
        runs[run] = {"data": data, "intervals": intervals,
                     "source": {"run": run, "file": Path(path).name,
                                "sha256": file_hash(path), "units": "V",
                                "channels": list(cfg.channels), "sfreq": cfg.fs}}
    return runs


def trial_features(record, cfg):
    """One [.5, 2.5)-s window per task cue; causal full-run filtering."""
    filtered = sosfilt(filter_design(cfg), record["data"], axis=-1)
    x, y = [], []
    for a, b, label in record["intervals"]:
        if label == 0:
            continue
        start = a + int(0.5 * cfg.fs)
        end = start + cfg.window_samples
        if end > b or end > filtered.shape[1]:
            continue
        if raw_quality(record["data"][:, start:end], cfg) is not None:
            continue
        x.append(features(filtered[:, start:end], cfg))
        y.append(label)
    if not x or set(y) != {1, 2}:
        raise ValueError("Both imagery classes need eligible trials; inspect QC and annotations.")
    return np.asarray(x), np.asarray(y)


def build_experiment(cfg=Config(), data_dir="bci_data"):
    runs = load_runs(cfg, data_dir)
    split = {run: trial_features(record, cfg) for run, record in runs.items()
             if run != cfg.test_run}
    model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000,
                                                               random_state=20))
    model.fit(*split[cfg.train_run])
    if list(model.classes_) != [1, 2]:
        raise ValueError("Class order changed.")
    scores = {}
    for role, run in (("train", cfg.train_run), ("validation", cfg.validation_run)):
        x, y = split[run]
        pred = model.predict(x)
        scores[role] = {"run": run, "n_trials": len(y),
                        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
                        "confusion_1_left_2_right": confusion_matrix(y, pred, labels=[1, 2]).tolist()}
    scaler, classifier = model.steps[0][1], model.steps[1][1]
    manifest = {"dataset": "https://physionet.org/content/eegmmidb/1.0.0/",
                "config": asdict(cfg), "sources": [r["source"] for r in runs.values()],
                "label_contract": {"T0": "instructed rest", "T1": "imagine left fist",
                                   "T2": "imagine right fist"},
                "split": "R04 train; R08 validation; R12 locked test; one participant, run-separated",
                "features": "C3/Cz/C4 x inclusive 8-12,13-30 Hz bin-density integrals; log10 V^2",
                "filter": {"method": "causal Butterworth order 4 bandpass 7-30 Hz",
                           "sos": filter_design(cfg).tolist(), "initial_state": "zero per run/reset"},
                "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(),
                "model_coef": classifier.coef_.tolist(), "model_intercept": classifier.intercept_.tolist(),
                "classes": model.classes_.tolist(), "scores": scores,
                "versions": {p: importlib.metadata.version(p)
                             for p in ("numpy", "scipy", "mne", "scikit-learn")},
                "helper_sha256": file_hash(__file__)}
    return {"config": cfg, "runs": runs, "model": model, "manifest": manifest}


class CommandPolicy:
    """Uncalibrated score gate, consecutive updates, refractory time; not intent detection."""
    def __init__(self, cfg):
        self.cfg = cfg
        self.last_command_time = -math.inf
        self.reset_evidence()

    def reset_evidence(self):
        self.candidate, self.streak = None, 0

    def step(self, scores, now):
        label = int(np.argmax(scores)) + 1
        if float(np.max(scores)) < self.cfg.threshold:
            self.reset_evidence()
            return 0, "uncertain"
        self.streak = self.streak + 1 if label == self.candidate else 1
        self.candidate = label
        if self.streak < self.cfg.dwell_updates:
            return 0, "accumulating"
        if now - self.last_command_time < self.cfg.refractory_s:
            return 0, "refractory"
        self.last_command_time = now
        self.reset_evidence()
        return (-1 if label == 1 else 1), "command"


def audit_label(intervals, start, end):
    """Called AFTER command selection; labels never enter the policy/decoder."""
    matches = [label for a, b, label in intervals if a <= start and end <= b]
    return matches[0] if len(matches) == 1 else None


def held_out_metrics(experiment):
    """Evaluate R12 only after the feature/model/policy choices have been frozen."""
    cfg = experiment["config"]
    x, y = trial_features(experiment["runs"][cfg.test_run], cfg)
    pred = experiment["model"].predict(x)
    return {"run": cfg.test_run, "n_trials": len(y),
            "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
            "confusion_1_left_2_right": confusion_matrix(y, pred, labels=[1, 2]).tolist()}


def replay(experiment, faults=False, run=None):
    """Accelerated virtual-clock replay; only a bounded local cursor is affected.

    Faults: one dropped chunk at 20 s, one stale chunk at 30 s, one flat
    channel chunk at 40 s. No wall-clock pacing or physical feedback measurement.
    """
    cfg, model = experiment["config"], experiment["model"]
    run = cfg.validation_run if run is None else run
    if run not in experiment["runs"]:
        raise ValueError("Run not loaded.")
    record = experiment["runs"][run]
    data, n = record["data"], record["data"].shape[1]
    sos = filter_design(cfg)
    zi = np.zeros((len(sos), 3, 2))
    ring = np.empty((3, 0))
    policy, rows, events = CommandPolicy(cfg), [], []
    expected, cursor, naive_cursor, arrival_clock = 0, 0, 0, 0.0
    for start in range(0, n, cfg.chunk_samples):
        end = min(start + cfg.chunk_samples, n)
        if faults and start == int(20 * cfg.fs):
            events.append({"kind": "injected_drop", "sample": start})
            continue
        sample_time = (end - 1) / cfg.fs
        delay = 0.75 if faults and start == int(30 * cfg.fs) else 0.0
        # A delayed packet stalls the virtual arrival clock; queued packets cannot
        # arrive before it. This is a simulation, not measured network latency.
        arrival_time = max(arrival_clock, sample_time + delay)
        arrival_clock = arrival_time
        age = arrival_time - sample_time
        block = data[:, start:end].copy()
        if faults and start == int(40 * cfg.fs):
            block[0] = 0.0
        issue = None
        if start != expected:
            issue = "sample_gap"
        expected = end
        if age > cfg.max_age_s:
            issue = "stale_packet"
        issue = issue or raw_quality(block, cfg)
        if issue:
            zi.fill(0); ring = np.empty((3, 0)); policy.reset_evidence()
            events.append({"kind": issue, "sample": start})
            rows.append({"sample_end": end, "sample_time": sample_time,
                         "arrival_time": arrival_time, "status": issue,
                         "command": 0, "naive_command": 0, "cursor": cursor,
                         "naive_cursor": naive_cursor, "processing_ms": None,
                         "audit_label": None})
            # Discard this chunk; collect a completely fresh 2-s window after reset.
            continue
        tick = time.perf_counter()
        filtered, zi = sosfilt(sos, block, axis=-1, zi=zi)
        ring = np.concatenate((ring, filtered), axis=1)[:, -cfg.window_samples:]
        if ring.shape[1] < cfg.window_samples:
            rows.append({"sample_end": end, "sample_time": sample_time,
                         "arrival_time": arrival_time, "status": "warming_up",
                         "command": 0, "naive_command": 0, "cursor": cursor,
                         "naive_cursor": naive_cursor, "processing_ms": None,
                         "audit_label": None})
            continue
        vector = features(ring, cfg)
        scores = model.predict_proba(vector[None])[0]
        predicted = int(model.classes_[int(np.argmax(scores))])
        command, status = policy.step(scores, arrival_time)
        naive = -1 if predicted == 1 else 1
        cursor = int(np.clip(cursor + command, -cfg.cursor_limit, cfg.cursor_limit))
        naive_cursor = int(np.clip(naive_cursor + naive, -cfg.cursor_limit, cfg.cursor_limit))
        processing_ms = 1000 * (time.perf_counter() - tick)
        # Annotation access occurs only now, for retrospective evaluation.
        truth = audit_label(record["intervals"], end - cfg.window_samples, end)
        rows.append({"sample_end": end, "window_start": end - cfg.window_samples,
                     "sample_time": sample_time, "arrival_time": arrival_time,
                     "status": status, "scores_left_right": scores.tolist(),
                     "predicted": predicted, "command": command, "naive_command": naive,
                     "cursor": cursor, "naive_cursor": naive_cursor,
                     "processing_ms": processing_ms, "audit_label": truth,
                     "update_duration_s": (end - start) / cfg.fs})
    task = [r for r in rows if r.get("audit_label") in (1, 2)]
    rest = [r for r in rows if r.get("audit_label") == 0]
    rest_seconds = sum(b - a for a, b, label in record["intervals"] if label == 0) / cfg.fs
    times = [r["processing_ms"] for r in rows if r["processing_ms"] is not None]
    scored_rest_seconds = sum(r["update_duration_s"] for r in rest)
    accepted = [r for r in task if r["command"] != 0]
    summary = {"run": run, "faults_injected": bool(faults), "decision_rows": len(rows),
               "valid_prediction_windows": len(times), "task_windows": len(task),
               "task_window_accuracy": (sum(r["predicted"] == r["audit_label"] for r in task) / len(task)
                                        if task else None),
               "task_commands": len(accepted),
               "conditional_task_command_accuracy": (sum((1 if r["command"] == -1 else 2) == r["audit_label"]
                                                          for r in accepted) / len(accepted) if accepted else None),
               "rest_annotation_seconds": rest_seconds, "eligible_rest_windows": len(rest),
               "scored_rest_seconds": scored_rest_seconds,
               "gated_commands": sum(r["command"] != 0 for r in rows),
               "naive_commands": sum(r["naive_command"] != 0 for r in rows),
               "rest_proxy_commands_per_min": (60 * sum(r["command"] != 0 for r in rest) / scored_rest_seconds
                                                if scored_rest_seconds else None),
               "rest_proxy_naive_per_min": (60 * sum(r["naive_command"] != 0 for r in rest) / scored_rest_seconds
                                             if scored_rest_seconds else None),
               "processing_ms_median": float(np.median(times)) if times else None,
               "processing_ms_p95": float(np.percentile(times, 95)) if times else None,
               "event_counts": {kind: sum(e["kind"] == kind for e in events)
                                for kind in sorted({e["kind"] for e in events})},
               "claim": "Causal software replay; overlapping windows; rest proxy; no live BCI validation"}
    return {"rows": rows, "events": events, "summary": summary,
            "config": asdict(cfg), "manifest": experiment["manifest"]}


def save_bundle(payload, output_dir="bci_outputs"):
    """Unique local artifact; preserve source recordings and prior runs."""
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / ("bci_" + uuid.uuid4().hex + ".json")
    path.write_text(json.dumps(payload, indent=2, allow_nan=False), encoding="utf-8")
    return {"path": str(path), "sha256": file_hash(path)}
