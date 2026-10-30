"""Chapter 24 synthetic validation studio; Python 3.11+, standard library only.

No EEG, diagnosis, clinical recommendation, fitted predictor, or validated probability.
Authoring validation is static; students must execute and inspect their own results.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import random
import platform

VERSION = "ch24-validation-v1"
SEED = 2401
POLICIES = {"sensitive": 0.25, "selective": 0.60}
CALIBRATION_BINS = 5


def make_dataset(n_per_cohort: int = 240, seed: int = SEED) -> list[dict]:
    """One synthetic row/person; disjoint A/development, B/calibration, C/external.

    Candidate score is deliberately distorted from the generating risk. Synthetic
    grouping and site effects illustrate evaluation, not demographic biology.
    """
    if type(n_per_cohort) is not int or not 10 <= n_per_cohort <= 300:
        raise ValueError("n_per_cohort must be an integer from 10 to 300")
    rng = random.Random(seed)
    rows = []
    for cohort, site, offset, day in [
        ("development", "A", 0.0, 0),
        ("calibration", "B", -0.35, 365),
        ("external", "C", -0.70, 730),
    ]:
        for i in range(n_per_cohort):
            group = "G1" if i % 2 == 0 else "G2"
            z = rng.gauss(0.0, 1.0)
            risk = 1.0 / (1.0 + math.exp(-(-0.6 + offset + 1.2*z)))
            # Label is generated, never used as an input to an individual score.
            outcome = int(rng.random() < risk)
            score = min(0.99, max(0.01, math.sqrt(risk)))
            quality = rng.random() >= (0.08 if group == "G1" else 0.20)
            supported = rng.random() >= 0.06
            score_present = rng.random() >= 0.04
            rows.append({
                "subject_id": f"{site}-{i:04d}", "cohort": cohort, "site": site,
                "group": group, "prediction_day": day+i,
                "outcome_available_day": day+i+30,
                "outcome": outcome, "score": score if score_present else None,
                "quality_ok": quality, "supported_input": supported,
                "source_id": f"synthetic-{site}-{i:04d}",
                "model_version": "fixed-toy-score-v1", "schema": "prediction.v1",
                "generator_seed": seed, "generator_n_per_cohort": n_per_cohort,
            })
    return rows


def eligibility(row: dict) -> str:
    """Prespecified technical gates, not an out-of-distribution detector."""
    if row["score"] is None:
        return "missing_score"
    if not row["quality_ok"]:
        return "poor_quality"
    if not row["supported_input"]:
        return "unsupported_input"
    return "eligible"


def fit_calibrator(rows: list[dict], bins: int = CALIBRATION_BINS) -> dict:
    """Smoothed histogram mapping fitted ONLY on the calibration cohort.

    Equal-width score bins; (events+1)/(n+2); empty bins use midpoint.
    This simple mapping need not be monotone or improve external calibration.
    """
    if not rows or any(r["cohort"] != "calibration" for r in rows):
        raise ValueError("Fit only on the reserved calibration cohort")
    if type(bins) is not int or bins < 2:
        raise ValueError("bins must be an integer >= 2")
    usable = [r for r in rows if eligibility(r) == "eligible"]
    values, counts = [], []
    for b in range(bins):
        part = [r for r in usable if min(int(r["score"]*bins), bins-1) == b]
        counts.append(len(part))
        values.append((sum(r["outcome"] for r in part)+1)/(len(part)+2)
                      if part else (b+0.5)/bins)
    return {"version": "histogram-laplace-v1", "bins": bins,
            "values": values, "counts": counts,
            "fit_subjects": [r["subject_id"] for r in usable]}


def probability(row: dict, calibrator: dict | None = None) -> float:
    if eligibility(row) != "eligible":
        raise ValueError("No numerical output for an ineligible row")
    score = row["score"]
    if calibrator is None:
        return score
    return calibrator["values"][min(int(score*calibrator["bins"]), calibrator["bins"]-1)]


def ratio(a: float, b: float) -> float | None:
    return a/b if b else None


def roc_auc(y: list[int], p: list[float]) -> float | None:
    """Pairwise ROC-AUC; half credit for ties; undefined with one outcome class."""
    pos = [v for label, v in zip(y, p) if label == 1]
    neg = [v for label, v in zip(y, p) if label == 0]
    return ratio(sum((a > b)+0.5*(a == b) for a in pos for b in neg), len(pos)*len(neg))


def average_precision(y: list[int], p: list[float]) -> float | None:
    """Non-interpolated, grouped-tie average precision; not trapezoidal PR-AUC."""
    positives = sum(y)
    if not positives:
        return None
    tp = fp = 0
    area = 0.0
    for value in sorted(set(p), reverse=True):
        labels = [label for label, score in zip(y, p) if score == value]
        added = sum(labels)
        tp += added
        fp += len(labels)-added
        area += (added/positives)*(tp/(tp+fp))
    return area


def calibration_table(y: list[int], p: list[float], bins: int = 5) -> list[dict]:
    result = []
    for b in range(bins):
        ix = [i for i, v in enumerate(p) if min(int(v*bins), bins-1) == b]
        result.append({"lower": b/bins, "upper": (b+1)/bins, "n": len(ix),
                       "mean_prediction": ratio(sum(p[i] for i in ix), len(ix)),
                       "event_fraction": ratio(sum(y[i] for i in ix), len(ix))})
    return result


def evaluate(rows: list[dict], threshold: float, calibrator: dict | None = None) -> dict:
    if not 0 < threshold < 1:
        raise ValueError("threshold must be inside (0,1)")
    used = [r for r in rows if eligibility(r) == "eligible"]
    y = [r["outcome"] for r in used]
    p = [probability(r, calibrator) for r in used]
    tp = sum(label == 1 and score >= threshold for label, score in zip(y, p))
    fp = sum(label == 0 and score >= threshold for label, score in zip(y, p))
    fn = sum(label == 1 and score < threshold for label, score in zip(y, p))
    tn = sum(label == 0 and score < threshold for label, score in zip(y, p))
    n = len(used)
    weight = threshold/(1-threshold)
    return {"n_total": len(rows), "n_eligible": n, "coverage": ratio(n, len(rows)),
            "status_counts": dict(Counter(eligibility(r) for r in rows)),
            "threshold": threshold, "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "sensitivity": ratio(tp, tp+fn), "specificity": ratio(tn, tn+fp),
            "ppv": ratio(tp, tp+fp), "npv": ratio(tn, tn+fn),
            "roc_auc": roc_auc(y, p), "average_precision": average_precision(y, p),
            "brier": ratio(sum((score-label)**2 for label, score in zip(y, p)), n),
            "calibration": calibration_table(y, p),
            "net_benefit_eligible": ratio(tp-fp*weight, n),
            "all_positive_eligible": ratio(sum(y)-(n-sum(y))*weight, n),
            "all_negative_eligible": 0.0 if n else None}


def prevalence_scenario(sensitivity: float, specificity: float, prevalence: float) -> dict:
    """Algebraic scenario holding sensitivity/specificity fixed; not transport validation."""
    if not all(0 <= v <= 1 for v in (sensitivity, specificity, prevalence)):
        raise ValueError("Inputs must be in [0,1]")
    return {"prevalence": prevalence,
            "ppv": ratio(sensitivity*prevalence,
                         sensitivity*prevalence+(1-specificity)*(1-prevalence)),
            "npv": ratio(specificity*(1-prevalence),
                         specificity*(1-prevalence)+(1-sensitivity)*prevalence)}


def bootstrap_brier(rows: list[dict], calibrator: dict | None = None,
                    repeats: int = 400, seed: int = 2402) -> dict:
    """Percentile resampling across eligible subjects in this one-site fixture.

    Conditions on the already fitted mapping; excludes its estimation uncertainty.
    Does not estimate between-site uncertainty or provide an individual risk interval.
    """
    used = [r for r in rows if eligibility(r) == "eligible"]
    if len(used) < 2 or type(repeats) is not int or repeats < 20:
        raise ValueError("Need >=2 eligible subjects and >=20 repeats")
    errors = [(probability(r, calibrator)-r["outcome"])**2 for r in used]
    rng = random.Random(seed)
    samples = sorted(sum(rng.choice(errors) for _ in errors)/len(errors) for _ in range(repeats))
    return {"lower": samples[math.ceil(.025*repeats)-1],
            "upper": samples[math.ceil(.975*repeats)-1], "repeats": repeats,
            "scope": "eligible-subject Brier, fixed mapping, one synthetic site"}


def result_card(row: dict, policy: str, calibrator: dict | None = None) -> dict:
    """Prediction-time export excludes the subsequently observed outcome."""
    threshold = POLICIES[policy]
    status = eligibility(row)
    value = probability(row, calibrator) if status == "eligible" else None
    return {"schema": "research-card.v1", "subject_id": row["subject_id"],
            "source_id": row["source_id"], "site": row["site"],
            "prediction_day": row["prediction_day"], "status": status,
            "quality_ok": row["quality_ok"], "supported_input": row["supported_input"],
            "model_version": row["model_version"], "studio_version": VERSION,
            "preprocessing_version": "not-applicable-synthetic-v1",
            "calibration_version": calibrator["version"] if calibrator else "none",
            "calibration_artifact_sha256": hashlib.sha256(
                json.dumps(calibrator, sort_keys=True, allow_nan=False).encode("utf-8")
            ).hexdigest() if calibrator else None,
            "policy": policy, "threshold": threshold, "synthetic_estimate": value,
            "category": ("flagged" if value >= threshold else "not_flagged")
                        if value is not None else "insufficient_evidence",
            "uncertainty": "No validated individual risk interval supplied",
            "intended_use": "Synthetic research teaching only; no patient-care action"}


def save_bundle(rows: list[dict], calibrator: dict, directory: str = "outputs") -> Path:
    """Create a new bundle directory without overwriting an existing run."""
    external = [r for r in rows if r["cohort"] == "external"]
    if {r["subject_id"] for r in external} & set(calibrator["fit_subjects"]):
        raise ValueError("Calibration/external overlap")
    settings = {(r["generator_seed"], r["generator_n_per_cohort"]) for r in rows}
    if len(settings) != 1:
        raise ValueError("Save one coherent generated fixture")
    generator_seed, n_per_cohort = settings.pop()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    dest = Path(directory)/f"{VERSION}-{stamp}"
    dest.mkdir(parents=True, exist_ok=False)
    content = {"version": VERSION, "generator_seed": generator_seed,
               "generator_n_per_cohort": n_per_cohort,
               "limits": "Synthetic cohort; no clinical validation or impact evaluation",
               "manifest": {"rows": len(rows), "policies": POLICIES,
                            "python_version": platform.python_version(),
                            "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                            "subject_order": [r["subject_id"] for r in rows]},
               "calibrator": calibrator,
               "evaluation_rows": rows,
               "external": {name: evaluate(external, t, calibrator) for name, t in POLICIES.items()},
               "prediction_cards": [result_card(r, "sensitive", calibrator) for r in external]}
    payload = json.dumps(content, indent=2, sort_keys=True, allow_nan=False).encode("utf-8")
    (dest/"bundle.json").write_bytes(payload)
    (dest/"sha256.txt").write_text(hashlib.sha256(payload).hexdigest()+"  bundle.json\n")
    return dest
