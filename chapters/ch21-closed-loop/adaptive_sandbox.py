"""Chapter 21: dimensionless feedback-control sandbox, Python 3.11+.

No neural recordings, patient model, device interface, or stimulation prescription.
Students run this module themselves. Authoring checks do not execute it.
"""
from dataclasses import asdict, dataclass
from pathlib import Path
import hashlib
import json
import math
import random
import uuid

VERSION = "ch21-sandbox-1.0"


@dataclass(frozen=True)
class Config:
    steps: int = 240
    seed: int = 21
    a: float = 0.96
    drift: float = 0.04
    action_effect: float = 0.08
    delay_steps: int = 2
    target: float = 0.60
    target_half_width: float = 0.15
    ema_alpha: float = 0.25
    initial_gain: float = 1.0
    gain_min: float = 0.50
    gain_max: float = 2.0
    gain_step: float = 0.10
    adapt_every_valid: int = 20
    adapt_deadband: float = 0.05
    max_action: float = 1.0
    max_change: float = 0.10
    max_age: float = 0.50
    recovery_samples: int = 3

    def __post_init__(self):
        for value in asdict(self).values():
            if isinstance(value, (int, float)) and not math.isfinite(value):
                raise ValueError("Configuration values must be finite.")
        if (type(self.steps) is not int or self.steps < 200 or
                type(self.seed) is not int or
                type(self.delay_steps) is not int or self.delay_steps < 0):
            raise ValueError("Use at least 200 steps, an integer seed and nonnegative integer delay.")
        if not (0 <= self.a < 1 and self.action_effect > 0 and self.drift >= 0):
            raise ValueError("Invalid toy process.")
        if not (0 < self.ema_alpha <= 1 and
                0 < self.gain_min <= self.initial_gain <= self.gain_max and
                self.gain_step > 0 and self.target_half_width > 0):
            raise ValueError("Invalid estimator or gain settings.")
        if (type(self.adapt_every_valid) is not int or self.adapt_every_valid < 1 or
                type(self.recovery_samples) is not int or self.recovery_samples < 1 or
                min(self.max_action, self.max_change, self.max_age) <= 0 or
                self.adapt_deadband < 0):
            raise ValueError("Invalid supervisor or adaptation settings.")


def clip(value, low, high):
    return min(high, max(low, value))


class Controller:
    """Receives measurement/age/stop only; never receives the latent toy state."""
    def __init__(self, cfg, adaptive):
        self.cfg, self.adaptive = cfg, bool(adaptive)
        self.estimate = None
        self.previous = 0.0
        self.gain = cfg.initial_gain
        self.ready_count = 0
        self.errors = []

    def step(self, measurement, age, stop=False):
        cfg = self.cfg
        gain_used = self.gain
        issue = ("manual_stop" if stop else
                 "missing" if measurement is None else
                 "nonfinite" if not math.isfinite(measurement) else
                 "stale" if not math.isfinite(age) or age < 0 or age > cfg.max_age else
                 "amplitude" if abs(measurement) > 3.0 else None)
        if issue:
            self.estimate = None
            self.ready_count = 0
            self.errors.clear()
            self.previous = 0.0
            return {"mode": "STOPPED" if stop else "FALLBACK", "reason": issue,
                    "estimate": None, "proposed": None, "delivered": 0.0,
                    "gain_used": gain_used, "gain_next": self.gain,
                    "adapted": False, "limited": False}
        self.estimate = (measurement if self.estimate is None else
                         cfg.ema_alpha * measurement + (1 - cfg.ema_alpha) * self.estimate)
        self.ready_count += 1
        if self.ready_count < cfg.recovery_samples:
            self.previous = 0.0
            return {"mode": "WARMUP", "reason": "fresh_samples", "estimate": self.estimate,
                    "proposed": None, "delivered": 0.0, "gain_used": gain_used,
                    "gain_next": self.gain, "adapted": False, "limited": False}
        error = self.estimate - cfg.target  # Positive action lowers this toy state.
        proposed = self.gain * error
        bounded = clip(proposed, 0.0, cfg.max_action)
        delivered = clip(bounded, max(0.0, self.previous - cfg.max_change),
                          min(cfg.max_action, self.previous + cfg.max_change))
        self.previous = delivered
        adapted = False
        if self.adaptive:
            self.errors.append(error)
            if len(self.errors) == cfg.adapt_every_valid:
                mean_error = sum(self.errors) / len(self.errors)
                direction = (1 if mean_error > cfg.adapt_deadband else
                             -1 if mean_error < -cfg.adapt_deadband else 0)
                self.gain = clip(self.gain + direction * cfg.gain_step,
                                 cfg.gain_min, cfg.gain_max)
                adapted = self.gain != gain_used
                self.errors.clear()
        return {"mode": "ACTIVE", "reason": "eligible", "estimate": self.estimate,
                "proposed": proposed, "delivered": delivered, "gain_used": gain_used,
                "gain_next": self.gain, "adapted": adapted,
                "limited": not math.isclose(proposed, delivered, abs_tol=1e-12)}


def simulate(cfg=Config(), adaptive=False, faults=False):
    """Closed-loop rollout; common exogenous draws across policies for a given seed."""
    rng = random.Random(cfg.seed)
    process_noise = [rng.gauss(0, 0.01) for _ in range(cfg.steps)]
    observation_noise = [rng.gauss(0, 0.04) for _ in range(cfg.steps)]
    controller = Controller(cfg, adaptive)
    state, actions, rows = 1.0, [], []
    for tick in range(cfg.steps):
        measurement = state + observation_noise[tick]
        age, stop, injected = 0.0, False, None
        if faults and tick == 40:
            measurement, injected = None, "missing"
        elif faults and tick == 80:
            age, injected = 0.75, "stale"
        elif faults and tick == 120:
            measurement, injected = 5.0, "artifact_proxy"
        if faults and 160 <= tick < 165:
            stop, injected = True, "manual_stop"
        decision = controller.step(measurement, age, stop)
        action = decision["delivered"]
        actions.append(action)
        applied_index = tick - cfg.delay_steps
        applied = actions[applied_index] if applied_index >= 0 else 0.0
        disturbance = 0.015 if 80 <= tick < 120 else 0.0
        next_state = (cfg.a * state + cfg.drift - cfg.action_effect * applied +
                      disturbance + process_noise[tick])
        rows.append({"tick": tick, "measurement": measurement, "age": age,
                     "stop": stop, "injected": injected, **decision,
                     "audit_state": state, "applied": applied,
                     "process_noise": process_noise[tick],
                     "observation_noise": observation_noise[tick],
                     "disturbance": disturbance, "next_audit_state": next_state})
        state = next_state
    active = [r for r in rows if r["mode"] == "ACTIVE"]
    all_mae = sum(abs(r["audit_state"] - cfg.target) for r in rows) / len(rows)
    in_band = sum(abs(r["audit_state"] - cfg.target) <= cfg.target_half_width for r in rows)
    summary = {"steps": len(rows), "active_steps": len(active),
               "active_coverage": len(active) / len(rows),
               "all_step_latent_mae": all_mae,
               "all_step_time_in_band_fraction": in_band / len(rows),
               "normalized_action_sum": sum(actions),
               "action_total_variation": sum(abs(actions[i] - (actions[i-1] if i else 0))
                                             for i in range(len(actions))),
               "fallback_steps": sum(r["mode"] == "FALLBACK" for r in rows),
               "stopped_steps": sum(r["mode"] == "STOPPED" for r in rows),
               "warmup_steps": sum(r["mode"] == "WARMUP" for r in rows),
               "limited_steps": sum(r["limited"] for r in rows),
               "gain_updates": sum(r["adapted"] for r in rows)}
    return {"version": VERSION, "config": asdict(cfg), "adaptive": bool(adaptive),
            "faults": bool(faults), "summary": summary, "rows": rows,
            "claim": "Dimensionless toy simulation only; no physiological or clinical validation."}


def reconstruct(bundle):
    """Recompute decision fields from saved observations, not counterfactual outcomes."""
    if bundle["version"] != VERSION:
        raise ValueError("Use the matching helper version.")
    cfg = Config(**bundle["config"])
    controller = Controller(cfg, bundle["adaptive"])
    decisions = [controller.step(r["measurement"], r["age"], r["stop"])
                 for r in bundle["rows"]]
    return decisions


def audit(bundle):
    """Student-run checks of invariants; not a hardware or clinical safety case."""
    cfg = Config(**bundle["config"])
    rebuilt = reconstruct(bundle)
    previous = 0.0
    for row, decision in zip(bundle["rows"], rebuilt):
        for key, value in decision.items():
            if row[key] != value:
                raise AssertionError(f"Decision reconstruction differs at {row['tick']}: {key}")
        u = row["delivered"]
        if not 0 <= u <= cfg.max_action:
            raise AssertionError("Action bound violated.")
        if not cfg.gain_min <= row["gain_next"] <= cfg.gain_max:
            raise AssertionError("Gain bound violated.")
        if row["mode"] != "ACTIVE" and u != 0:
            raise AssertionError("Inhibited step has nonzero output.")
        if row["mode"] == "ACTIVE" and abs(u - previous) > cfg.max_change + 1e-12:
            raise AssertionError("Normal-operation slew limit violated.")
        # Fallback/stop may jump straight to zero; this exception is part of the toy contract.
        previous = u
    return {"decision_reconstruction": True, "bounds_and_modes": True,
            "checked_steps": len(rebuilt)}


def save_bundle(bundle, directory="ch21_outputs"):
    """Unique JSON artifact plus content receipt; no authentication or immutable storage."""
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"ch21_{uuid.uuid4().hex}.json"
    payload = json.dumps(bundle, sort_keys=True, indent=2, allow_nan=False).encode("utf-8")
    with path.open("xb") as handle:
        handle.write(payload)
    return {"path": str(path), "sha256": hashlib.sha256(payload).hexdigest()}
