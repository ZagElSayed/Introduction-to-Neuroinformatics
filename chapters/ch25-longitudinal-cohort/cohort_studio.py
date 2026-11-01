"""Synthetic point-in-time cohort authoring exercise; no clinical model or EHR adapter."""
import hashlib
import json
import math
import platform
import random
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

VERSION = "ch25-cohort-v1"
HORIZON = 90
BASE_FEATURES = ("age", "neural")
MULTIMODAL_FEATURES = ("age", "neural", "mri", "mri_missing")
SCHEMA = """
CREATE TABLE Meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE Person(pid TEXT PRIMARY KEY, site TEXT NOT NULL, cohort TEXT NOT NULL,
                    group_code TEXT NOT NULL, age REAL NOT NULL);
CREATE TABLE Encounter(eid TEXT PRIMARY KEY, pid TEXT NOT NULL REFERENCES Person(pid),
                       day INTEGER NOT NULL, role TEXT NOT NULL);
CREATE TABLE Acquisition(aid TEXT PRIMARY KEY, eid TEXT NOT NULL REFERENCES Encounter(eid),
    modality TEXT NOT NULL, device TEXT NOT NULL, observed_day INTEGER NOT NULL, available_day INTEGER NOT NULL,
    quality_ok INTEGER NOT NULL CHECK(quality_ok IN (0,1)), missing_reason TEXT);
CREATE TABLE Derivative(did TEXT PRIMARY KEY, aid TEXT NOT NULL REFERENCES Acquisition(aid),
    value REAL, units TEXT NOT NULL, recipe TEXT NOT NULL);
CREATE TABLE Medication(mid TEXT PRIMARY KEY, pid TEXT NOT NULL REFERENCES Person(pid),
    start_day INTEGER NOT NULL, stop_day INTEGER, available_day INTEGER NOT NULL, agent TEXT NOT NULL);
CREATE TABLE Outcome(oid TEXT PRIMARY KEY, pid TEXT UNIQUE NOT NULL REFERENCES Person(pid),
    observed_day INTEGER NOT NULL, available_day INTEGER NOT NULL,
    value INTEGER NOT NULL CHECK(value IN (0,1)), definition TEXT NOT NULL);
"""


def sigmoid(value):
    value = max(-35.0, min(35.0, value))
    return 1.0 / (1.0 + math.exp(-value))


def make_fixture(n_per_cohort=80, seed=2501):
    """Return an in-memory normalized SQLite fixture; all identities are invented."""
    if type(n_per_cohort) is not int or not 20 <= n_per_cohort <= 120:
        raise ValueError("n_per_cohort must be an integer from 20 to 120")
    rng = random.Random(seed)
    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO Meta VALUES (?,?)", [
        ("version", VERSION), ("seed", str(seed)), ("n_per_cohort", str(n_per_cohort))])
    for cohort, site, offset, shift in [
        ("development", "A", 0, 0.0), ("calibration", "B", 365, -.25),
        ("external", "C", 730, -.5)]:
        for i in range(n_per_cohort):
            pid = f"{site}-{i:03d}"
            index = offset + i
            group = "G1" if i % 2 == 0 else "G2"
            age = rng.uniform(18, 80)
            neural = rng.gauss(0, 1)
            imaging = rng.gauss(0, 1)
            y = int(rng.random() < sigmoid(-.7 + shift + .85 * neural + .55 * imaging))
            db.execute("INSERT INTO Person VALUES (?,?,?,?,?)", (pid, site, cohort, group, age))
            for role, day in [("history", index - 30), ("recent", index - 3), ("index", index)]:
                db.execute("INSERT INTO Encounter VALUES (?,?,?,?)", (pid + '-' + role, pid, day, role))

            def add(name, encounter, modality, day, available, value, quality=1, reason=None):
                aid = pid + '-' + name
                db.execute("INSERT INTO Acquisition VALUES (?,?,?,?,?,?,?,?)",
                           (aid, pid + '-' + encounter, modality, "toy-device-" + site,
                            day, available, quality, reason))
                db.execute("INSERT INTO Derivative VALUES (?,?,?,?,?)",
                           (aid + '-d', aid, value, "arbitrary", "synthetic-feature-v1"))

            quality = int(i % 13 != 0)
            add("eeg-old", "history", "EEG", index - 30, index - 29,
                neural + rng.gauss(0, .4), quality)
            add("eeg-recent", "recent", "EEG", index - 3, index - 1,
                neural + rng.gauss(0, .2), quality)
            # Deliberate future-information trap. This value must never enter an as-of feature.
            add("eeg-future", "index", "EEG", index + 1, index + 2, 5.0 if y else -5.0)
            if i % 7 == 0:
                add("mri-late", "index", "MRI", index - 1, index + 5, imaging)
            elif rng.random() < (.2 if group == "G1" else .4) + (.1 if site == "C" else 0):
                add("mri-absent", "history", "MRI", index - 20, index - 10,
                    None, 1, "not_measured")
            else:
                add("mri-ready", "history", "MRI", index - 20, index - 10, imaging)
            if i % 3 == 0:
                db.execute("INSERT INTO Medication VALUES (?,?,?,?,?,?)",
                           (pid + '-med', pid, index - 7, None, index + 3, "toy-agent"))
            db.execute("INSERT INTO Outcome VALUES (?,?,?,?,?,?)",
                       (pid + '-out', pid, index + HORIZON, index + 105, y, "synthetic-event-90d-v1"))
    db.commit()
    return db


def build_cohort(db):
    """One index encounter/person, using observations AND availability at/before index."""
    records = []
    indices = db.execute("""SELECT p.*, e.eid, e.day AS index_day FROM Person p
        JOIN Encounter e USING(pid) WHERE e.role='index' ORDER BY p.pid""").fetchall()
    for person in indices:
        row = dict(person)
        index = row["index_day"]
        candidates = [dict(r) for r in db.execute("""SELECT a.*, d.did, d.value, d.units, d.recipe
            FROM Acquisition a JOIN Encounter e USING(eid) JOIN Derivative d USING(aid)
            WHERE e.pid=? ORDER BY a.observed_day,a.aid""", (row["pid"],))]
        provenance = {}
        features = {"age": row["age"]}
        reasons = {}
        for modality, field in [("EEG", "neural"), ("MRI", "mri")]:
            items = [r for r in candidates if r["modality"] == modality]
            usable = [r for r in items if index - 45 <= r["observed_day"] <= index
                      and r["available_day"] <= index and r["quality_ok"]
                      and r["value"] is not None]
            chosen = usable[-1] if usable else None
            features[field] = chosen["value"] if chosen else None
            if chosen:
                provenance[field] = {k: chosen[k] for k in
                    ("aid", "did", "device", "observed_day", "available_day", "units", "recipe")}
                reasons[field] = "observed"
            elif any(r["observed_day"] <= index < r["available_day"] and r["value"] is not None for r in items):
                reasons[field] = "not_yet_available"
            elif any(r["observed_day"] <= index and not r["quality_ok"] for r in items):
                reasons[field] = "poor_quality"
            else:
                supplied = [r["missing_reason"] for r in items if r["observed_day"] <= index
                            and r["available_day"] <= index and r["missing_reason"]]
                reasons[field] = supplied[-1] if supplied else "not_measured_or_usable"
        features["mri_missing"] = float(features["mri"] is None)
        row["features"] = features
        row["missingness"] = reasons
        row["provenance"] = provenance
        row["status"] = "eligible" if features["neural"] is not None else "insufficient_evidence"
        row["known_medications"] = [r[0] for r in db.execute("""SELECT agent FROM Medication
            WHERE pid=? AND start_day<=? AND available_day<=?
            AND (stop_day IS NULL OR stop_day>?)""", (row["pid"], index, index, index))]
        records.append(row)
    return records


def reference_labels(db, records):
    """Retrospective evaluation labels are separate from prediction-time features/cards."""
    labels = {r["pid"]: r["value"] for r in db.execute("SELECT pid,value FROM Outcome")}
    return [labels[r["pid"]] for r in records]


def fit_baseline(records, labels, multimodal=False):
    """Ridge logistic teaching model. Fit preprocessing and weights on development only."""
    if len(records) != len(labels) or not records:
        raise ValueError("aligned, nonempty records and labels required")
    if any(r["cohort"] != "development" or r["status"] != "eligible" for r in records):
        raise ValueError("fit only eligible development records")
    if any(type(y) is not int or y not in (0, 1) for y in labels):
        raise ValueError("binary integer labels required")
    names = MULTIMODAL_FEATURES if multimodal else BASE_FEATURES
    means, scales = {}, {}
    for name in names:
        observed = [r["features"][name] for r in records if r["features"][name] is not None]
        means[name] = sum(observed) / len(observed) if observed else 0.0
        scales[name] = (math.sqrt(sum((v-means[name])**2 for v in observed)/len(observed))
                        if observed else 1.0) or 1.0
    model = {"features": list(names), "means": means, "scales": scales,
             "weights": [0.0] * (len(names)+1), "fit_pids": [r["pid"] for r in records],
             "version": "ridge-logistic-v1", "steps": 400, "learning_rate": .1, "ridge": .02}
    xx = [_vector(r, model) for r in records]
    weights = model["weights"]
    for _ in range(model["steps"]):
        gradients = [0.0] * len(weights)
        for vec, y in zip(xx, labels):
            residual = sigmoid(sum(w*v for w,v in zip(weights,vec))) - y
            for j, v in enumerate(vec):
                gradients[j] += residual*v/len(xx)
        for j in range(len(weights)):
            weights[j] -= .1*(gradients[j]+(.02*weights[j] if j else 0))
    return model


def _vector(record, model):
    if record["status"] != "eligible":
        raise ValueError("no ordinary prediction for insufficient evidence")
    vals = [1.0]
    for name in model["features"]:
        val = record["features"][name]
        val = model["means"][name] if val is None else val
        vals.append((val-model["means"][name])/model["scales"][name])
    return vals


def predict(records, model):
    """Return candidate probabilities; calibration is not guaranteed."""
    return [sigmoid(sum(w*v for w,v in zip(model["weights"],_vector(r,model)))) for r in records]


def metrics(labels, probabilities, threshold=.5):
    if len(labels) != len(probabilities) or not labels:
        raise ValueError("nonempty, aligned evaluation inputs required")
    if not 0 <= threshold <= 1:
        raise ValueError("threshold must lie in [0,1]")
    if any(y not in (0,1) for y in labels) or any(not math.isfinite(p) or not 0<=p<=1 for p in probabilities):
        raise ValueError("binary labels and finite probabilities required")
    pairs = list(zip(labels,probabilities))
    tp=sum(y==1 and p>=threshold for y,p in pairs);fp=sum(y==0 and p>=threshold for y,p in pairs)
    fn=sum(y==1 and p<threshold for y,p in pairs);tn=sum(y==0 and p<threshold for y,p in pairs)
    positives=[p for y,p in pairs if y];negatives=[p for y,p in pairs if not y]
    ratio=lambda a,b:a/b if b else None
    auc=(sum((p>q)+.5*(p==q) for p in positives for q in negatives)/(len(positives)*len(negatives))
         if positives and negatives else None)
    calibration=[]
    for k in range(5):
        group=[(y,p) for y,p in pairs if min(int(p*5),4)==k]
        calibration.append({"bin": k, "n":len(group),
            "predicted":sum(p for y,p in group)/len(group) if group else None,
            "observed":sum(y for y,p in group)/len(group) if group else None})
    return {"n":len(labels),"tp":tp,"fp":fp,"fn":fn,"tn":tn,"roc_auc":auc,
        "brier":sum((p-y)**2 for y,p in pairs)/len(pairs),"threshold":threshold,
        "sensitivity":ratio(tp,tp+fn),"specificity":ratio(tn,tn+fp),
        "ppv":ratio(tp,tp+fp),"npv":ratio(tn,tn+fn),"calibration":calibration}


def research_card(record, model):
    return {"schema":"ch25-research-card-v1","pid":record["pid"],"site":record["site"],
        "index_day":record["index_day"],"horizon_days":HORIZON,"status":record["status"],
        "candidate_probability":predict([record],model)[0] if record["status"]=="eligible" else None,
        "missingness":record["missingness"],"input_provenance":record["provenance"],
        "studio_version":VERSION,"model_version":model["version"],
        "model_sha256":hashlib.sha256(json.dumps(model,sort_keys=True,allow_nan=False).encode()).hexdigest(),
        "uncertainty":"No validated individual interval; calibration and transport not established.",
        "intended_use":"Synthetic cohort research exercise; no clinical advice or action."}


def export_bundle(db, records, models, summaries, root="outputs"):
    """Create a new research bundle, including SQL, exact configuration, and byte receipts."""
    dest=Path(root)/datetime.now(timezone.utc).strftime("cohort-%Y%m%dT%H%M%S%fZ")
    dest.mkdir(parents=True,exist_ok=False)
    source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    documents={"cohort.json":records,"models.json":models,"summaries.json":summaries,
        "research_cards.json":{name:[research_card(r,model) for r in records]
                               for name,model in models.items()},
        "manifest.json":{"fixture":dict(db.execute("SELECT key,value FROM Meta")),
        "python":platform.python_version(),"helper_sha256":source_hash,
        "index_pids":[r["pid"] for r in records],"horizon_days":HORIZON,
        "limits":"Synthetic data; one index per person; no censoring, clinical integration, or impact evaluation."},
        "reference_outcomes.json":[dict(r) for r in db.execute("SELECT * FROM Outcome ORDER BY pid")]}
    for name,obj in documents.items():
        (dest/name).write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False),encoding="utf-8")
    (dest/"fixture.sql").write_text('\n'.join(db.iterdump()),encoding="utf-8")
    receipts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(dest.iterdir())}
    (dest/"sha256.json").write_text(json.dumps(receipts,indent=2),encoding="utf-8")
    return str(dest)
