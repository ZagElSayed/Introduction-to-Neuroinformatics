"""Chapter 11: synthetic access governance and audit evidence demonstration.
Not a production authorization engine; policies are illustrative only.
"""
import argparse
import csv
import json
from pathlib import Path

ROLES = {
    "clinician": {"read_raw", "read_derivative"},
    "analyst": {"read_derivative"},
    "collaborator": set(),
    "workflow_service": {"read_raw", "write_derivative"},
    "data_steward": {"read_raw", "read_derivative", "export_derivative", "view_audit"},
}
ASSETS = [
    {"asset_id": "raw-eeg", "classification": "restricted", "owner": "hospital", "retention": "per policy"},
    {"asset_id": "derivative-table", "classification": "controlled", "owner": "study", "retention": "per policy"},
    {"asset_id": "identity-linkage", "classification": "highly_restricted", "owner": "hospital", "retention": "per policy"},
    {"asset_id": "audit-log", "classification": "restricted", "owner": "security", "retention": "per policy"},
]
SCENARIOS = [
    {"threat": "stolen analyst credentials", "impact": "confidentiality", "control": "MFA and least privilege", "residual_risk": "session compromise"},
    {"threat": "public storage misconfiguration", "impact": "confidentiality", "control": "private defaults and policy checks", "residual_risk": "configuration drift"},
    {"threat": "malicious container", "impact": "integrity", "control": "signed images and scanning", "residual_risk": "supply-chain bypass"},
    {"threat": "accidental export", "impact": "confidentiality", "control": "deny by default and approval", "residual_risk": "authorized misuse"},
    {"threat": "model service outage", "impact": "availability", "control": "fail closed and incident plan", "residual_risk": "clinical workflow delay"},
]

def decide(role, action, resource):
    if role not in ROLES or resource not in {a["asset_id"] for a in ASSETS}:
        return False
    if resource == "identity-linkage":
        return False  # deliberately outside this demo's granted permissions
    if resource == "audit-log":
        return role == "data_steward" and action == "view_audit"
    if resource == "raw-eeg":
        return action == "read_raw" and role in ("clinician", "workflow_service", "data_steward")
    if resource == "derivative-table":
        return action in ROLES[role] and action in ("read_derivative", "write_derivative", "export_derivative")
    return False

def run(output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "asset_inventory.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(ASSETS[0]))
        writer.writeheader()
        writer.writerows(ASSETS)
    (out / "threat_model.json").write_text(json.dumps(SCENARIOS, indent=2), encoding="utf-8")
    (out / "role_policy.json").write_text(json.dumps({k: sorted(v) for k, v in ROLES.items()}, indent=2), encoding="utf-8")
    attempts = [
        ("analyst", "read_derivative", "derivative-table"),
        ("analyst", "read_raw", "raw-eeg"),
        ("collaborator", "export_derivative", "derivative-table"),
        ("data_steward", "view_audit", "audit-log"),
        ("workflow_service", "write_derivative", "derivative-table"),
        ("data_steward", "read_raw", "identity-linkage"),
    ]
    audit = [{"event_id": f"evt-{i:03d}", "actor_role": role, "action": action,
              "resource": resource, "decision": "allow" if decide(role, action, resource) else "deny",
              "correlation_id": "synthetic-run-001", "timestamp": f"2026-01-01T00:00:{i:02d}Z"}
             for i, (role, action, resource) in enumerate(attempts, 1)]
    (out / "audit_events.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
    summary = {"events": len(audit), "allowed": sum(e["decision"] == "allow" for e in audit),
               "denied": sum(e["decision"] == "deny" for e in audit),
               "threat_scenarios": len(SCENARIOS), "identity_linkage_access": "denied in demonstration",
               "clinical_use": "not suitable", "real_identity_or_phi": False}
    (out / "governance_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/ch11")
    args = parser.parse_args()
    print(json.dumps(run(args.output_dir), indent=2))

if __name__ == "__main__":
    main()
