"""Chapter 22 timing studio: virtual queue model, not a device benchmark.

Python 3.11+, standard library only. No sleep, network, human data, or actuator.
All *_ms values in simulate() are assigned virtual times, not host measurements.
"""
from collections import Counter, deque
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from math import ceil, sin, pi
import platform
from pathlib import Path
from uuid import uuid4

VERSION = "ch22-timing-v1"


@dataclass(frozen=True)
class Config:
    policy: str = "latest"
    capacity: int = 1  # waiting windows; excludes the one running job
    n_windows: int = 80
    deadline_ms: int = 100  # relative to newest sample / window end
    inference_timeout_ms: int = 40
    scenario: str = "faults"  # nominal, overload, or faults

    def __post_init__(self):
        if self.policy not in {"fifo", "latest"}:
            raise ValueError("policy must be fifo or latest")
        if self.scenario not in {"nominal", "overload", "faults"}:
            raise ValueError("unknown scenario")
        if any(type(v) is not int or v <= 0 for v in (
            self.capacity, self.n_windows, self.deadline_ms,
            self.inference_timeout_ms)):
            raise ValueError("counts and budgets must be positive integers")


def make_windows(n_windows):
    """Four channels, 100 Hz, 40-sample history, 2-sample hop.

    A window ending at t has support (t-400,t], with samples 10 ms apart.
    Features are exact mean squares of toy sinusoids, not EEG biomarkers.
    """
    ring = deque(maxlen=40)
    windows = []
    for sample in range(40 + 2 * (n_windows - 1)):
        t = (sample + 1) * 10
        row = [sin(2 * pi * (7 + channel) * t / 1000)
               for channel in range(4)]
        ring.append(row)
        if len(ring) == 40 and (sample + 1 - 40) % 2 == 0:
            features = [sum(row[c] ** 2 for row in ring) / 40
                        for c in range(4)]
            windows.append({"id": len(windows), "window_start_ms": t - 400,
                            "source_ms": t, "features": features})
    return windows


def percentile(values, q):
    """Nearest-rank percentile of completed jobs only; None if empty."""
    if not values:
        return None
    return sorted(values)[max(0, ceil(q * len(values)) - 1)]


def simulate(config=Config()):
    """Single nonpreemptive worker; completion precedes arrival on a tie.

    FIFO drops a new arrival when full. Latest evicts the waiting window
    with oldest source time if the new window is newer; it never cancels
    running work. A detected inference timeout does not free this worker
    early: the modeled call is non-cancellable and completes its full cost.
    """
    windows = make_windows(config.n_windows)
    records = [dict(w, deadline_ms=w["source_ms"] + config.deadline_ms,
                    arrival_ms=None, start_ms=None, pre_end_ms=None,
                    infer_end_ms=None, gate_ms=None, finish_ms=None,
                    status=None, score=None, command=None, quality=True)
               for w in windows]
    arrivals = []
    faults = config.scenario == "faults"
    for r in records:
        if faults and r["id"] == 8:
            r["status"] = "missing"
            continue
        delay = 130 if faults and r["id"] == 12 else 5
        r["arrival_ms"] = r["source_ms"] + delay
        r["quality"] = not (faults and r["id"] == 15)
        arrivals.append((r["arrival_ms"], r["id"]))
    arrivals.sort()
    pending, running, index, now, max_waiting = [], None, 0, 0, 0
    last_source = -1
    events = []

    def note(kind, row):
        events.append({"time_ms": now, "id": row["id"], "event": kind,
                       "waiting": len(pending)})

    while index < len(arrivals) or pending or running is not None:
        next_arrival = arrivals[index][0] if index < len(arrivals) else float("inf")
        next_finish = running["finish_ms"] if running is not None else float("inf")
        if running is None and pending:
            # Choose arrival order or newest source time among waiting jobs.
            position = (max(range(len(pending)), key=lambda j: pending[j]["source_ms"])
                        if config.policy == "latest" else 0)
            row = pending.pop(position)
            if now > row["deadline_ms"]:
                row["status"] = "expired_before_start"
                note(row["status"], row)
                continue
            infer_ms = (80 if config.scenario != "nominal" and 20 <= row["id"] <= 29
                        else 8)
            row.update(start_ms=now, pre_end_ms=now + 6,
                       infer_end_ms=now + 6 + infer_ms,
                       gate_ms=now + 6 + infer_ms + 2,
                       finish_ms=now + 6 + infer_ms + 2 + 4)
            running = row
            note("start", row)
            continue
        now = min(next_arrival, next_finish)
        if next_finish <= next_arrival:
            row = running
            running = None
            row["score"] = sum(row["features"]) / 4
            # This threshold is a toy computation, not a calibrated probability.
            proposed = int(row["score"] >= 0.5)
            if row["infer_end_ms"] - row["pre_end_ms"] > config.inference_timeout_ms:
                row["status"] = "inference_timeout"
            elif row["finish_ms"] > row["deadline_ms"]:
                row["status"] = "late_completion"
            elif row["source_ms"] <= last_source:
                row["status"] = "old_result"
            else:
                row["status"], row["command"] = "released", proposed
                last_source = row["source_ms"]
            note(row["status"], row)
        else:
            row = records[arrivals[index][1]]
            index += 1
            if not row["quality"]:
                row["status"] = "invalid_quality"
            elif now > row["deadline_ms"]:
                row["status"] = "expired_at_arrival"
            elif len(pending) < config.capacity:
                pending.append(row)
            elif config.policy == "fifo":
                row["status"] = "overflow_drop_new"
            else:
                oldest = min(range(len(pending)), key=lambda j: pending[j]["source_ms"])
                if row["source_ms"] > pending[oldest]["source_ms"]:
                    evicted = pending.pop(oldest)
                    evicted["status"] = "superseded"
                    note("superseded", evicted)
                    pending.append(row)
                else:
                    row["status"] = "older_arrival_drop"
            max_waiting = max(max_waiting, len(pending))
            note(row["status"] or "enqueue", row)

    completed = [r for r in records if r["finish_ms"] is not None]
    ages = [r["finish_ms"] - r["source_ms"] for r in completed]
    counts = dict(sorted(Counter(r["status"] for r in records).items()))
    released = counts.get("released", 0)
    summary = {"expected_windows": len(records), "completed_jobs": len(completed),
               "status_counts": counts, "max_waiting": max_waiting,
               "on_time_release_fraction": released / len(records),
               "no_on_time_release_fraction": 1 - released / len(records),
               "completed_late": sum(r["finish_ms"] > r["deadline_ms"] for r in completed),
               "completed_age_p50_ms": percentile(ages, .50),
               "completed_age_p95_ms": percentile(ages, .95),
               "completed_age_p99_ms": percentile(ages, .99)}
    return {"version": VERSION, "clock": "virtual_ms_not_host_time",
            "helper_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
            "host_python": platform.python_version(),
            "config": asdict(config), "summary": summary,
            "records": records, "events": events}


def audit(bundle):
    """Student-run consistency checks, not a real-time or device certificate."""
    rows, cfg = bundle["records"], bundle["config"]
    assert len(rows) == cfg["n_windows"]
    assert all(r["status"] is not None for r in rows)
    assert sum(bundle["summary"]["status_counts"].values()) == len(rows)
    assert all(0 <= e["waiting"] <= cfg["capacity"] for e in bundle["events"])
    prior = -1
    for r in sorted((r for r in rows if r["status"] == "released"),
                    key=lambda r: r["finish_ms"]):
        assert r["quality"] and r["finish_ms"] <= r["deadline_ms"]
        assert r["infer_end_ms"] - r["pre_end_ms"] <= cfg["inference_timeout_ms"]
        assert r["source_ms"] > prior
        assert r["command"] in {0, 1}
        prior = r["source_ms"]
    assert all(r["command"] is None for r in rows if r["status"] != "released")
    return {"checked": len(rows), "scope": "virtual record invariants only"}


def save_bundle(bundle, directory="runs"):
    """Unique local file; receipt detects byte changes, not identity or immutability."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(bundle, indent=2, sort_keys=True, allow_nan=False).encode()
    path = directory / ("ch22-" + uuid4().hex + ".json")
    path.write_bytes(payload)
    digest = sha256(payload).hexdigest()
    path.with_suffix(".sha256").write_text(digest + "  " + path.name + "\n")
    return {"path": str(path), "sha256": digest}
