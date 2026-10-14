"""Synthetic, context-aware policy decisions; not production enforcement.

Principal and approval registries are trusted *fixtures*, not authentication.
The request cannot grant itself a role, purpose approval, or export permission.
"""
import argparse
import csv
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

POLICY_VERSION = "2.0"
AS_OF = "2026-01-01T12:00:00+00:00"  # Explicit simulated policy clock.
ROLES = {
    "clinician": ["read_raw", "read_derivative"],
    "analyst": ["read_derivative"],
    "collaborator": [],
    "workflow_service": ["read_raw", "write_derivative"],
    "data_steward": ["read_raw", "read_derivative", "export_derivative", "view_audit"],
}
ASSETS = [
    {"asset_id": "raw-eeg", "classification": "restricted", "owner": "hospital", "project": "study-A", "retention": "institution-defined"},
    {"asset_id": "derivative-table", "classification": "controlled", "owner": "study", "project": "study-A", "retention": "institution-defined"},
    {"asset_id": "identity-linkage", "classification": "highly_restricted", "owner": "hospital", "project": "study-A", "retention": "institution-defined"},
    {"asset_id": "audit-log", "classification": "restricted", "owner": "security", "project": "study-A", "retention": "institution-defined"},
]
RESOURCE_ACTIONS = {
    "raw-eeg": ["read_raw"],
    "derivative-table": ["read_derivative", "write_derivative", "export_derivative"],
    "identity-linkage": [],  # Relinking is intentionally outside this exercise's grants.
    "audit-log": ["view_audit"],
}


def principal(role, expires="2026-12-31T00:00:00+00:00", active=True):
    return {"role": role, "authenticated": True, "active": active,
            "project": "study-A", "purposes": ["approved-research"], "expires": expires}


PRINCIPALS = {
    "clinician-01": principal("clinician"), "analyst-01": principal("analyst"),
    "collaborator-01": principal("collaborator"), "service-01": principal("workflow_service"),
    "steward-01": principal("data_steward"),
    "expired-01": principal("analyst", expires="2025-12-31T00:00:00+00:00"),
    "revoked-01": principal("analyst", active=False),
}
EXPORT_APPROVALS = [{"actor_id": "steward-01", "resource": "derivative-table", "action": "export_derivative",
                     "project": "study-A", "purpose": "approved-research",
                     "destination": "approved-enclave", "active": True,
                     "expires": "2026-12-31T00:00:00+00:00"}]
SCENARIOS = [
    {"threat": "stolen analyst credentials", "impact": ["confidentiality"], "prevent": "MFA and least privilege", "detect": "unusual access review", "respond": "revoke session and investigate scope", "residual_risk": "valid-session abuse"},
    {"threat": "public storage misconfiguration", "impact": ["confidentiality"], "prevent": "private defaults and export controls", "detect": "configuration monitoring", "respond": "restrict exposure and assess disclosures", "residual_risk": "copies already obtained"},
    {"threat": "malicious or unapproved processing image", "impact": ["integrity"], "prevent": "approved digest, build review, and validation", "detect": "version and reference-output checks", "respond": "pause release and identify affected outputs", "residual_risk": "trusted build compromise or missed scientific defect"},
    {"threat": "accidental export", "impact": ["confidentiality"], "prevent": "purpose and destination approval", "detect": "export audit review", "respond": "contain further sharing and follow institutional process", "residual_risk": "recipient retention"},
    {"threat": "model service outage", "impact": ["availability", "clinical safety"], "prevent": "tested continuity plan", "detect": "availability and stale-result indicators", "respond": "mark unavailable and invoke defined human fallback", "residual_risk": "delay or limited fallback capacity"},
]


def timestamp(value):
    if not isinstance(value, str):
        raise ValueError("Timestamp must be a string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp needs a timezone")
    return parsed.astimezone(timezone.utc)


def evaluate(request, principals=None, export_approvals=None, as_of=AS_OF):
    """Decide using simulated trusted registries, never caller-supplied roles."""
    principals = PRINCIPALS if principals is None else principals
    approvals = EXPORT_APPROVALS if export_approvals is None else export_approvals
    role = None

    def result(allowed, reason):
        return {"decision": "allow" if allowed else "deny", "reason": reason,
                "actor_role": role, "policy_version": POLICY_VERSION, "policy_as_of": as_of}

    required = {"actor_id", "action", "resource", "project", "purpose"}
    if not isinstance(request, dict) or not required <= set(request) or set(request) - required - {"destination"}:
        return result(False, "invalid_request_schema")
    if any(not isinstance(value, str) or not value.strip() for value in request.values()):
        return result(False, "invalid_request_value")
    try:
        now = timestamp(as_of)
        actor = principals.get(request["actor_id"])
        if not isinstance(actor, dict) or actor.get("authenticated") is not True:
            return result(False, "identity_not_verified")
        role = actor.get("role")
        if actor.get("active") is not True:
            return result(False, "identity_inactive")
        if timestamp(actor.get("expires")) <= now:
            return result(False, "approval_expired")
        asset = next((asset for asset in ASSETS if asset["asset_id"] == request["resource"]), None)
        if asset is None:
            return result(False, "unknown_resource")
        if request["project"] != actor.get("project") or request["project"] != asset["project"]:
            return result(False, "project_not_permitted")
        if not isinstance(actor.get("purposes"), list) or request["purpose"] not in actor["purposes"]:
            return result(False, "purpose_not_permitted")
        if role not in ROLES or request["action"] not in ROLES[role]:
            return result(False, "role_action_not_permitted")
        if request["action"] not in RESOURCE_ACTIONS[request["resource"]]:
            return result(False, "resource_action_not_permitted")
        if request["action"] == "export_derivative":
            for approval in approvals:
                if (isinstance(approval, dict) and approval.get("active") is True and
                    all(approval.get(key) == request.get(key) for key in required | {"destination"}) and
                    timestamp(approval.get("expires")) > now):
                    return result(True, "approved_export")
            return result(False, "export_not_approved")
        if "destination" in request:
            return result(False, "destination_not_applicable")
        return result(True, "all_required_conditions_met")
    except (ValueError, TypeError, AttributeError, KeyError):
        return result(False, "invalid_policy_context")


def request(actor="analyst-01", action="read_derivative", resource="derivative-table", **extra):
    return {"actor_id": actor, "action": action, "resource": resource,
            "project": "study-A", "purpose": "approved-research", **extra}


def cases():
    return [
        ("approved analyst read", request(), "allow"),
        ("analyst raw access", request(action="read_raw", resource="raw-eeg"), "deny"),
        ("collaborator export", request(actor="collaborator-01", action="export_derivative", destination="approved-enclave"), "deny"),
        ("steward audit", request(actor="steward-01", action="view_audit", resource="audit-log"), "allow"),
        ("workflow writes derivative", request(actor="service-01", action="write_derivative"), "allow"),
        ("identity relinking", request(actor="steward-01", action="read_raw", resource="identity-linkage"), "deny"),
        ("unknown identity", request(actor="unknown"), "deny"),
        ("wrong purpose", request(purpose="unapproved-marketing"), "deny"),
        ("wrong project", request(project="study-B"), "deny"),
        ("expired approval", request(actor="expired-01"), "deny"),
        ("revoked identity", request(actor="revoked-01"), "deny"),
        ("approved export", request(actor="steward-01", action="export_derivative", destination="approved-enclave"), "allow"),
        ("unapproved destination", request(actor="steward-01", action="export_derivative", destination="unapproved-store"), "deny"),
        ("forged role", request(role="data_steward"), "deny"),
    ]


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def run(output_dir):
    out = Path(output_dir)
    if out.exists() and any(out.iterdir()):
        raise ValueError("Choose a fresh, empty --output-dir to preserve earlier audit evidence")
    out.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex
    with (out / "asset_inventory.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(ASSETS[0]))
        writer.writeheader()
        writer.writerows(ASSETS)
    policy = {"version": POLICY_VERSION, "roles": ROLES, "resource_actions": RESOURCE_ACTIONS,
              "principals": PRINCIPALS, "export_approvals": EXPORT_APPROVALS,
              "policy_as_of": AS_OF, "trust_source": "synthetic server-side fixtures; not real identity verification"}
    policy_digest = hashlib.sha256(json.dumps(policy, sort_keys=True).encode()).hexdigest()
    save(out / "role_policy.json", policy)
    save(out / "threat_model.json", SCENARIOS)
    requests, audit = [], []
    for i, (name, payload, expected) in enumerate(cases(), 1):
        answer = evaluate(payload)
        requests.append({"case": name, "request": payload, "expected": expected})
        audit.append({"event_id": f"{run_id}-{i:03d}", "actor_id": payload.get("actor_id"),
                      "action": payload.get("action"), "resource": payload.get("resource"),
                      "project": payload.get("project"), "purpose": payload.get("purpose"),
                      "destination": payload.get("destination"), **answer,
                      "correlation_id": run_id, "policy_sha256": policy_digest,
                      "observed_utc": datetime.now(timezone.utc).isoformat(),
                      "matches_expected": answer["decision"] == expected})
    save(out / "synthetic_requests.json", requests)
    save(out / "audit_events.json", audit)
    summary = {"status": "success" if all(event["matches_expected"] for event in audit) else "failed",
               "run_id": run_id, "events": len(audit),
               "allowed": sum(event["decision"] == "allow" for event in audit),
               "denied": sum(event["decision"] == "deny" for event in audit),
               "expectation_mismatches": sum(not event["matches_expected"] for event in audit),
               "threat_scenarios": len(SCENARIOS), "policy_version": POLICY_VERSION,
               "policy_sha256": policy_digest, "policy_as_of": AS_OF,
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "identity_linkage_access": "not granted", "clinical_use": "not suitable",
               "real_identity_or_phi": False, "audit_store": "ordinary local JSON, not tamper-resistant"}
    save(out / "governance_summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs/ch11")
    args = parser.parse_args()
    try:
        result = run(args.output_dir)
    except (OSError, ValueError, TypeError) as exc:
        result = {"status": "failed", "error": str(exc)}
    print(json.dumps(result, indent=2))
    if result["status"] != "success":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
