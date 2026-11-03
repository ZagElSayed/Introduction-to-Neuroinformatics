"""Synthetic precision-neurology teaching tools. No clinical control or inference."""
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import math
import platform
import random

VERSION = "ch26-precision-v1"
BASELINE_DAYS = tuple(range(10))
FIT_CUTOFF = 60


def sigmoid(x):
    return 1 / (1 + math.exp(-max(-35, min(35, x))))


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, allow_nan=False).encode()).hexdigest()


def make_fixture(n_per_cohort=60, seed=2601):
    """Three invented, disjoint person cohorts in successive calendar periods."""
    if type(n_per_cohort) is not int or not 24 <= n_per_cohort <= 120:
        raise ValueError("n_per_cohort must be an integer in [24,120]")
    rng = random.Random(seed)
    people, observations, references, trial, oracle = [], [], {}, [], {}
    for cohort, offset in [("development", 0), ("validation", 120), ("evaluation", 240)]:
        for i in range(n_per_cohort):
            pid = f"{cohort[0]}-{i:03d}"
            group = "G1" if i % 2 == 0 else "G2"
            person = dict(pid=pid, cohort=cohort, offset=offset, group=group)
            people.append(person)
            level, sigma = rng.gauss(5, 1.5), rng.uniform(.35, .65)
            latent = []
            for day in range(37):
                sleep = int(rng.random() < .3)
                shift = 1.6 if i % 3 == 0 and day >= 22 else 0.0
                physical = shift + rng.gauss(0, sigma)
                latent.append((physical, sleep))
                firmware = "v2" if i % 4 == 0 and day >= 20 + i % 3 else "v1"
                value = level + physical + (2.5 if firmware == "v2" else 0)
                if i % 11 == 0 and day == 18:
                    value = None
                now = offset + day
                observations.append(dict(rid=f"{pid}:{day}", pid=pid, day=day,
                    observed=now, available=now + (3 if i % 7 == 0 and day == 18 else 0),
                    value=value, sleep=sleep, quality_ok=not (i % 17 == 0 and day in (7,8,9,19)),
                    device="toy-wrist", firmware=firmware, recipe="toy-measure-v1", units="arbitrary"))
            for day in range(10,35):
                physical, sleep = latent[day+1]
                references[f"{pid}:{day}"] = dict(value=int(rng.random() < sigmoid(-.5+.9*physical+.5*sleep)),
                    observed=offset+day+1, available=offset+day+3, definition="invented-next-day-event")
            # Separate randomized utility experiment; this is not the risk model's endpoint.
            risk = (.8 if group == "G1" else .2) + rng.uniform(-.04,.04)
            burden = .4 if (i//2) % 2 == 0 else 2.5
            tau = (.5 if group == "G1" else 2.0) - burden
            mu0 = 3 + 2*risk
            y0 = mu0 + rng.gauss(0,.4)
            action = int(rng.random() < .5)
            trial.append(dict(pid=pid, cohort=cohort, group=group, burden=burden,
                              baseline_risk=risk, assigned_action=action, observed_utility=y0+action*tau))
            oracle[pid] = dict(mu0=mu0, net_effect=tau, y0=y0, y1=y0+tau)
    return dict(version=VERSION, seed=seed, n_per_cohort=n_per_cohort, people=people,
                observations=observations, references=references, randomized_trial=trial, oracle=oracle)


def fit_baseline(person, records):
    """Frozen descriptive population SD (divisor n), from days 0..9 only."""
    cutoff = person["offset"]+10
    rows = [r for r in records if r["pid"] == person["pid"] and r["day"] in BASELINE_DAYS
            and r["observed"] <= cutoff and r["available"] <= cutoff and r["quality_ok"]
            and r["device"] == "toy-wrist" and r["firmware"] == "v1" and r["recipe"] == "toy-measure-v1"
            and r["units"] == "arbitrary" and r["value"] is not None and math.isfinite(r["value"])]
    result = dict(pid=person["pid"], version="baseline-v1", device="toy-wrist", firmware="v1", recipe="toy-measure-v1",
                  units="arbitrary", cutoff=cutoff, source_ids=[r["rid"] for r in rows], n=len(rows))
    if len(rows) < 8:
        return dict(result, status="insufficient_baseline", mean=None, sd=None)
    mean = sum(r["value"] for r in rows)/len(rows)
    sd = math.sqrt(sum((r["value"]-mean)**2 for r in rows)/len(rows))
    return dict(result, mean=mean, sd=sd, status="ready" if sd >= .05 else "insufficient_baseline")


def snapshot(person, record, baseline, index=None):
    """Validate the explicitly requested current observation, without stale fallback."""
    index = person["offset"]+record["day"] if index is None else index
    row = dict(pid=person["pid"], cohort=person["cohort"], rid=record["rid"], day=record["day"],
               index=index, source=dict(record), baseline_hash=digest(baseline), baseline=dict(baseline),
               value=None, z=None, sleep=None, status="eligible", reason=None)
    if record["pid"] != person["pid"] or baseline["pid"] != person["pid"]:
        reason = "identity_mismatch"
    elif record["observed"] != index:
        reason = "timestamp_mismatch"
    elif record["available"] > index:
        reason = "not_yet_available"
    elif not record["quality_ok"]:
        reason = "quality_failed"
    elif record["value"] is None or not math.isfinite(record["value"]):
        reason = "missing_or_invalid_value"
    elif baseline["status"] != "ready" or baseline["cutoff"] > index:
        reason = "insufficient_baseline"
    elif (record["device"],record["firmware"],record["recipe"],record["units"]) != (baseline["device"],baseline["firmware"],baseline["recipe"],baseline["units"]):
        reason = "measurement_version_changed"
    else:
        row.update(value=record["value"], z=(record["value"]-baseline["mean"])/baseline["sd"], sleep=record["sleep"])
        reason = "outside_toy_domain" if abs(row["z"]) > 8 else None
    if reason:
        row.update(status="freeze" if reason == "measurement_version_changed" else "needs_review", reason=reason)
    return row


def build_rows(fixture):
    by_person = {p["pid"]:[] for p in fixture["people"]}
    for record in fixture["observations"]:
        by_person[record["pid"]].append(record)
    rows, baselines = [], {}
    for person in fixture["people"]:
        records = by_person[person["pid"]]
        baseline = fit_baseline(person, records)
        baselines[person["pid"]] = baseline
        rows.extend(snapshot(person,r,baseline) for r in records if 10 <= r["day"] < 35)
    return rows, baselines


def fit_risk(rows, references, personal=False):
    """Ridge logistic teaching fit, development people and mature references only."""
    field = "z" if personal else "value"
    chosen = [r for r in rows if r["cohort"] == "development" and r["status"] == "eligible"
              and r["index"] <= FIT_CUTOFF and references[r["rid"]]["available"] <= FIT_CUTOFF]
    if not chosen:
        raise ValueError("No eligible development observations")
    fields = (field, "sleep")
    means = [sum(r[f] for r in chosen)/len(chosen) for f in fields]
    scales = [math.sqrt(sum((r[f]-m)**2 for r in chosen)/len(chosen)) or 1.0 for f,m in zip(fields,means)]
    xs = [[1]+[(r[f]-m)/s for f,m,s in zip(fields,means,scales)] for r in chosen]
    weights = [0.0]*3
    for _ in range(300):
        grad = [0.0]*3
        for r,x in zip(chosen,xs):
            error = sigmoid(sum(w*v for w,v in zip(weights,x))) - references[r["rid"]]["value"]
            for j in range(3):
                grad[j] += error*x[j]/len(chosen)
        weights = [w-.1*(g+(.02*w if j else 0)) for j,(w,g) in enumerate(zip(weights,grad))]
    return dict(version="risk-personal-v1" if personal else "risk-population-v1", fields=fields,
                means=means, scales=scales, weights=weights, fit_cutoff=FIT_CUTOFF,
                fit_ids=[r["rid"] for r in chosen], uncertainty="No individual interval supplied; not clinically calibrated.")


def predict(row, model):
    if row["status"] != "eligible":
        return None
    x = [1]+[(row[f]-m)/s for f,m,s in zip(model["fields"],model["means"],model["scales"])]
    return sigmoid(sum(w*v for w,v in zip(model["weights"],x)))


def evaluate_risk(rows, references, model, cohort):
    selected = [r for r in rows if r["cohort"] == cohort]
    pairs = [(predict(r,model), references[r["rid"]]["value"]) for r in selected if r["status"] == "eligible"]
    pos, neg = [p for p,y in pairs if y], [p for p,y in pairs if not y]
    auc = (sum((p>q)+.5*(p==q) for p in pos for q in neg)/(len(pos)*len(neg))) if pos and neg else None
    bins = []
    for j in range(5):
        b = [(p,y) for p,y in pairs if min(4,int(p*5)) == j]
        bins.append(dict(lower=j/5, upper=(j+1)/5, n=len(b),
                         predicted=sum(p for p,y in b)/len(b) if b else None,
                         observed=sum(y for p,y in b)/len(b) if b else None))
    return dict(cohort=cohort, n_windows=len(selected), n_people=len({r["pid"] for r in selected}),
                eligible=len(pairs), n_eligible_people=len({r["pid"] for r in selected if r["status"] == "eligible"}),
                coverage=len(pairs)/len(selected) if selected else None,
                brier=sum((p-y)**2 for p,y in pairs)/len(pairs) if pairs else None, auc=auc, calibration=bins,
                limits="Repeated windows are dependent; no intervals or person-level calibration established.")


def fit_effect_cells(trial):
    """Randomized group/burden cell mean differences; not individual causal effects."""
    cells = {}
    for row in trial:
        if row["cohort"] == "development":
            key = f'{row["group"]}|{row["burden"]}'
            cells.setdefault(key, {0:[],1:[]})[row["assigned_action"]].append(row["observed_utility"])
    return {key:dict(n0=len(v[0]),n1=len(v[1]),effect=(sum(v[1])/len(v[1])-sum(v[0])/len(v[0])) if v[0] and v[1] else None)
            for key,v in cells.items()}


def compare_policies(trial, cells, oracle, cohort="evaluation", budget_fraction=.25):
    """At-most-budget policies evaluated with known simulator truth, not clinical data."""
    if not 0 <= budget_fraction <= 1:
        raise ValueError("budget_fraction must be in [0,1]")
    rows = [r for r in trial if r["cohort"] == cohort]
    budget = int(len(rows)*budget_fraction)
    rankings = {
        "baseline_risk": sorted(rows,key=lambda r:(-r["baseline_risk"],r["pid"])),
        "estimated_net_utility": sorted([r for r in rows if (cells.get(f'{r["group"]}|{r["burden"]}',{}).get("effect") or 0)>0],
             key=lambda r:(-cells[f'{r["group"]}|{r["burden"]}']["effect"],r["pid"])),
        "oracle_net_utility": sorted([r for r in rows if oracle[r["pid"]]["net_effect"]>0],
             key=lambda r:(-oracle[r["pid"]]["net_effect"],r["pid"]))}
    out = {}
    for name, ranked in rankings.items():
        selected = {r["pid"] for r in ranked[:budget]}
        out[name] = dict(budget=budget, selected=sorted(selected), n_selected=len(selected),
            known_expected_utility=sum(oracle[r["pid"]]["mu0"]+(oracle[r["pid"]]["net_effect"] if r["pid"] in selected else 0) for r in rows)/len(rows) if rows else None)
    return out


@dataclass(frozen=True)
class Limits:
    version: str = "toy-gain-limits-v1"
    lower: float = 0.0
    upper: float = 1.0
    max_step: float = .1

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.lower,self.upper,self.max_step)) or self.lower >= self.upper or self.max_step <= 0:
            raise ValueError("Invalid toy limits")


def decide_gain(row, state=None, release_allowed=False, limits=Limits()):
    """Toy software gain only. No drug, stimulation, or clinical action is produced."""
    if type(release_allowed) is not bool:
        raise ValueError("release_allowed must be an explicit boolean teaching flag")
    state = dict(state or dict(gain=.3, frozen=False))
    if not limits.lower <= state["gain"] <= limits.upper:
        raise ValueError("Previous gain outside envelope; no command")
    reason = row["reason"]
    frozen = state["frozen"] or row["status"] == "freeze"
    proposal = permitted = delivered = None
    if frozen:
        status, reason = "frozen", reason or "explicit_requalification_required"
    elif row["status"] != "eligible":
        status = "needs_review"
    else:
        proposal = state["gain"]+(.15 if abs(row["z"])>1.5 else 0)
        permitted = max(limits.lower, min(limits.upper, max(state["gain"]-limits.max_step, min(state["gain"]+limits.max_step,proposal))))
        status = "released" if release_allowed else "not_authorized"
        if release_allowed:
            delivered = permitted
    next_state = dict(gain=delivered if delivered is not None else state["gain"], frozen=frozen)
    return dict(pid=row["pid"], rid=row["rid"], index=row["index"], baseline_hash=row["baseline_hash"],
                policy="toy-software-gain-v1", limits=asdict(limits), proposed=proposal, permitted=permitted,
                delivered=delivered, status=status, reason=reason, next_state=next_state,
                purpose="Abstract gain in a teaching program; no safety or clinical validation.")


def fault_cases(person, record, baseline):
    changes = {"missing":{"value":None}, "firmware":{"firmware":"unqualified-v2"},
               "delayed":{"available":person["offset"]+record["day"]+3}, "extreme":{"value":1e6},
               "timestamp":{"observed":person["offset"]+record["day"]+1}, "quality":{"quality_ok":False}}
    return {name:snapshot(person,dict(record,**change),baseline) for name,change in changes.items()}


def export_bundle(fixture, models, reports, decisions, output_dir="outputs"):
    """New timestamped folder, separate oracle/reference files, SHA-256 comparison receipt."""
    destination = Path(output_dir)/datetime.now(timezone.utc).strftime("precision-%Y%m%dT%H%M%S%fZ")
    destination.mkdir(parents=True,exist_ok=False)
    payloads = {"models.json":models,"reports.json":reports,"decisions.json":decisions,
                "synthetic_observations.json":fixture["observations"],"reference_outcomes.json":fixture["references"],
                "randomized_trial.json":fixture["randomized_trial"],"simulator_oracle.json":fixture["oracle"],
                "manifest.json":dict(version=VERSION,seed=fixture["seed"],n_per_cohort=fixture["n_per_cohort"],
                    python=platform.python_version(),helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    purpose="Synthetic information-handling exercise; not clinical evidence.")}
    for name,obj in payloads.items():
        (destination/name).write_text(json.dumps(obj,indent=2,sort_keys=True,allow_nan=False),encoding="utf-8")
    receipt = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(destination.iterdir())}
    (destination/"sha256.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
    return str(destination)
