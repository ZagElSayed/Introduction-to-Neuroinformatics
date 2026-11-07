"""NeuroBridge Phase XX: invented-data, review-only teaching simulator.

Standard library only. No clinical model, physical commands, network service,
authentication system, probability calibrator, or automatic drift detector.
"""
from __future__ import annotations
import copy
import hashlib
import html
import json
import math
from pathlib import Path
import random
import statistics
import sys
from datetime import datetime, timezone
import uuid

SEED = 2801
SCHEMA = {"rate_hz":128, "channels":["toy-left","toy-right"],
          "samples_per_channel":256, "units":"arbitrary", "recipe":"capstone-v1"}
NOW = 1000.0  # invented seconds in one virtual clock domain, not a host clock
MAX_AGE = 5.0
MAX_CLOCK_UNCERTAINTY = 0.05


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False,
                                    separators=(",", ":")).encode()).hexdigest()


def make_fixture(seed=SEED):
    rng = random.Random(seed)
    records, labels = [], {}
    for person in range(24):
        partition = "development" if person < 12 else "validation" if person < 18 else "evaluation"
        pid = f"invented-{person:02d}"
        for label in (0, 1):
            rid = f"{pid}-window-{label}"
            phase, gain = rng.random()*2*math.pi, rng.uniform(.8,1.2)
            signals = [[gain*math.sin(2*math.pi*6*t/128+phase+c*.3)
                        + rng.gauss(0, .08 if label == 0 else .8)
                        for t in range(256)] for c in range(2)]
            records.append({"record_id":rid,"participant_id":pid,"partition":partition,
                "schema":copy.deepcopy(SCHEMA),"observed_at":NOW-2,
                "available_at":NOW-1,"clock_uncertainty":.01,
                "quality_state":"eligible","signals":signals})
            labels[rid] = label
    return {"seed":seed,"records":records,"labels":labels,
            "scope":"invented noise recipes, not neurological labels"}


def audit_splits(records):
    seen, people = set(), {}
    for row in records:
        if row["record_id"] in seen:
            raise ValueError("duplicate_record_id")
        seen.add(row["record_id"])
        if row["partition"] not in {"development","validation","evaluation"}:
            raise ValueError("unknown_partition")
        pid = row["participant_id"]
        if pid in people and people[pid] != row["partition"]:
            raise ValueError("participant_overlap")
        people[pid] = row["partition"]
    return {p:{"people":sum(v == p for v in people.values()),
               "records":sum(r["partition"] == p for r in records)}
            for p in ("development","validation","evaluation")}


def signal_problem(row):
    if row.get("schema") != SCHEMA:
        return "schema_mismatch"
    signals = row.get("signals")
    if not isinstance(signals, list) or len(signals) != 2:
        return "channel_count"
    for channel in signals:
        if not isinstance(channel, list) or len(channel) != 256:
            return "missing_or_invalid_channel"
        if any(isinstance(v, bool) or not isinstance(v, (int,float))
               or not math.isfinite(v) for v in channel):
            return "nonfinite_or_invalid_sample"
    return None


def feature(row):
    problem = signal_problem(row)
    if problem:
        raise ValueError(problem)
    return sum((v-u)**2 for ch in row["signals"] for u,v in zip(ch,ch[1:]))/(2*255)


def fit_baseline(fixture):
    audit_splits(fixture["records"])
    development = [r for r in fixture["records"] if r["partition"] == "development"]
    groups = [[feature(r) for r in development if fixture["labels"][r["record_id"]] == y]
              for y in (0,1)]
    if not all(groups):
        raise ValueError("both_development_labels_required")
    low, high = map(statistics.mean, groups)
    if not low < high:
        raise ValueError("recipe_direction_not_supported")
    artifact = {"kind":"adjacent_difference_threshold","threshold":(low+high)/2,
        "schema":copy.deepcopy(SCHEMA),"fit_ids":[r["record_id"] for r in development],
        "fit_people":sorted({r["participant_id"] for r in development}),
        "intended_use":"invented_quality_review","feature_units":"arbitrary-unit squared",
        "uncertainty":"not estimated; no probability output"}
    return {**artifact,"model_id":digest(artifact)}


def model_problem(model):
    payload = {k:v for k,v in model.items() if k != "model_id"}
    return model.get("model_id") != digest(payload) or model.get("schema") != SCHEMA


def infer(row, model, role="reviewer", network_available=True, requested_model=None,
          now=NOW):
    """In-process virtual request. Declared role/network flags are teaching inputs."""
    result = {"trace_id":uuid.uuid4().hex,"record_id":row["record_id"],
        "participant_id":row["participant_id"],"model_id":model.get("model_id"),
        "intended_use":"invented_quality_review","status":"abstained",
        "prediction":None,"feature":None,"reason":None,
        "uncertainty":"not estimated","simulated_action":"hold_for_review",
        "clock_domain":"virtual seconds","request_at":now}
    def refuse(reason):
        result["reason"] = reason
        return result
    if role != "reviewer":
        return refuse("role_denied")
    if not network_available:
        return refuse("simulated_network_unavailable")
    if model_problem(model) or requested_model not in (None, model["model_id"]):
        return refuse("model_version_or_digest_mismatch")
    problem = signal_problem(row)
    if problem:
        return refuse(problem)
    times = [row.get(k) for k in ("observed_at","available_at","clock_uncertainty")]+[now]
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in times):
        return refuse("invalid_time")
    observed, available, clock, _ = times
    if clock < 0 or clock > MAX_CLOCK_UNCERTAINTY:
        return refuse("clock_uncertainty")
    if observed > available or available > now or observed > now:
        return refuse("time_order_or_availability")
    if now-observed > MAX_AGE:
        return refuse("stale_record")
    if row.get("quality_state") != "eligible":
        return refuse("declared_quality_hold")
    value = feature(row)
    prediction = int(value > model["threshold"])
    result.update({"status":"accepted","prediction":prediction,"feature":value,
                   "simulated_action":"technical_review" if prediction else "continue_review_pipeline"})
    return result


def evaluate(fixture, model):
    rows = [{**infer(r,model),"partition":r["partition"],
             "label":fixture["labels"][r["record_id"]]} for r in fixture["records"]]
    metrics = {}
    for partition in ("development","validation","evaluation"):
        intended = [r for r in rows if r["partition"] == partition]
        accepted = [r for r in intended if r["status"] == "accepted"]
        metrics[partition] = {"people":len({r["participant_id"] for r in intended}),
            "records":len(intended),"accepted":len(accepted),
            "coverage":len(accepted)/len(intended) if intended else None,
            "accuracy_on_accepted":sum(r["prediction"] == r["label"] for r in accepted)/len(accepted) if accepted else None,
            "uncertainty":"descriptive repeated-window summary; no confidence interval"}
    return {"predictions":rows,"metrics":metrics}


def fault_study(fixture, model):
    source = next(r for r in fixture["records"] if r["partition"] == "evaluation")
    rows = []
    cases = ["missing_channel","stale","future_availability","clock_uncertainty",
             "units","nonfinite","declared_drift","denied_role","network_loss","model_mismatch"]
    for case in cases:
        row, options = copy.deepcopy(source), {}
        if case == "missing_channel":row["signals"][0] = None
        elif case == "stale":row["observed_at"] = NOW-20
        elif case == "future_availability":row["available_at"] = NOW+1
        elif case == "clock_uncertainty":row["clock_uncertainty"] = .2
        elif case == "units":row["schema"]["units"] = "microvolt"
        elif case == "nonfinite":row["signals"][0][0] = float("nan")
        elif case == "declared_drift":row["quality_state"] = "review_required"
        elif case == "denied_role":options["role"] = "visitor"
        elif case == "network_loss":options["network_available"] = False
        else:options["requested_model"] = "unapproved-version"
        rows.append({"case":case,"response":infer(row,model,**options)})
    overlap = copy.deepcopy(source)
    overlap.update({"record_id":"invented-overlap-copy","partition":"development"})
    try:
        audit_splits(fixture["records"]+[overlap])
        outcome = "not_rejected"
    except ValueError as error:
        outcome = str(error)
    rows.append({"case":"participant_overlap","audit_outcome":outcome})
    rows.append({"case":"restored_original_request","response":infer(source,model)})
    return rows


def evidence_card(model, report):
    text = json.dumps({"scope":"invented quality-review recipes; research teaching only",
        "model_id":model["model_id"],"fit_people":model["fit_people"],
        "metrics":report["metrics"],"limits":["no diagnosis or treatment","no calibrated probabilities",
        "no real network, identity, drift detection, or hardware recovery","no clinical-impact evidence"]},indent=2)
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>NeuroBridge research evidence card</title><body style="max-width:900px;margin:3rem auto;font:18px system-ui;color:#142D4E"><h1>NeuroBridge Phase XX</h1><p>Inspect the evidence before expanding the claim.</p><pre style="white-space:pre-wrap;background:#F5F8FC;padding:1.5rem">'+html.escape(text)+'</pre></body></html>'


def export_bundle(fixture, model, report, faults, destination="outputs"):
    folder = Path(destination)/("capstone_"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")+"_"+uuid.uuid4().hex[:8])
    folder.mkdir(parents=True,exist_ok=False)
    manifest = {"seed":fixture["seed"],"schema":SCHEMA,"virtual_now":NOW,
        "max_age_seconds":MAX_AGE,"max_clock_uncertainty_seconds":MAX_CLOCK_UNCERTAINTY,
        "python":sys.version,"helper_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "scope":fixture["scope"],"not_executed_by_authors":"students execute and interpret their own results"}
    payloads = {"records.json":fixture["records"],"labels.json":fixture["labels"],
        "model.json":model,"report.json":report,"faults.json":faults,"manifest.json":manifest}
    for name,value in payloads.items():
        (folder/name).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    (folder/"evidence_card.html").write_text(evidence_card(model,report),encoding="utf-8")
    hashes = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(folder.iterdir())}
    (folder/"receipt.json").write_text(json.dumps(hashes,indent=2)+"\n",encoding="utf-8")
    return folder


def verify_receipt(folder):
    folder = Path(folder)
    hashes = json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
    return {name:(folder/name).is_file() and hashlib.sha256((folder/name).read_bytes()).hexdigest() == expected
            for name,expected in hashes.items()}
