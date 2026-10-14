"""Local behavioral tests; policy fixtures do not authenticate real callers."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch11-ethics-governance/exercise_11_1_policy_audit.py"


@pytest.fixture
def lab():
    spec = importlib.util.spec_from_file_location("ch11", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_all_declared_decision_cases(lab):
    for name, request, expected in lab.cases():
        assert lab.evaluate(request)["decision"] == expected, name


@pytest.mark.parametrize("patch", [
    {"actor_id": "unknown"}, {"project": "study-B"}, {"purpose": "other"},
    {"actor_id": "expired-01"}, {"actor_id": "revoked-01"},
    {"resource": "unknown"}, {"role": "data_steward"}, {"purpose": None},
    {"action": "export_derivative"},
])
def test_context_changes_do_not_inherit_baseline_allow(lab, patch):
    assert lab.evaluate(lab.request())["decision"] == "allow"
    assert lab.evaluate(lab.request(**patch))["decision"] == "deny"


def test_missing_context_and_false_authentication_deny(lab):
    request = lab.request()
    del request["project"]
    assert lab.evaluate(request)["reason"] == "invalid_request_schema"
    identities = copy.deepcopy(lab.PRINCIPALS)
    identities["analyst-01"]["authenticated"] = False
    assert lab.evaluate(lab.request(), principals=identities)["decision"] == "deny"
    identities["analyst-01"]["authenticated"] = "true"
    assert lab.evaluate(lab.request(), principals=identities)["decision"] == "deny"


def test_expiry_boundary_and_malformed_timestamp_deny(lab):
    identities = copy.deepcopy(lab.PRINCIPALS)
    identities["analyst-01"]["expires"] = lab.AS_OF
    assert lab.evaluate(lab.request(), principals=identities)["decision"] == "deny"
    identities["analyst-01"]["expires"] = "not-a-date"
    assert lab.evaluate(lab.request(), principals=identities)["reason"] == "invalid_policy_context"
    assert lab.evaluate(lab.request(), as_of="2026-01-01T12:00:00")["decision"] == "deny"


def test_read_permission_does_not_authorize_export(lab):
    request = lab.request(actor="steward-01", action="export_derivative", destination="approved-enclave")
    assert lab.evaluate(request)["decision"] == "allow"
    assert lab.evaluate(request, export_approvals=[])["decision"] == "deny"
    approval = copy.deepcopy(lab.EXPORT_APPROVALS)
    approval[0]["expires"] = lab.AS_OF
    assert lab.evaluate(request, export_approvals=approval)["decision"] == "deny"
    approval[0]["expires"] = "2026-12-31T00:00:00+00:00"
    approval[0]["active"] = False
    assert lab.evaluate(request, export_approvals=approval)["decision"] == "deny"


def test_invalid_resource_action_and_identity_linking_deny(lab):
    assert lab.evaluate(lab.request(actor="steward-01", action="view_audit", resource="raw-eeg"))["decision"] == "deny"
    assert lab.evaluate(lab.request(actor="steward-01", action="read_raw", resource="identity-linkage"))["decision"] == "deny"


def test_cli_exports_consistent_evidence(tmp_path):
    process = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
                             capture_output=True, text=True, check=True)
    summary = json.loads(process.stdout)
    assert summary["status"] == "success"
    assert summary["expectation_mismatches"] == 0
    events = json.loads((tmp_path / "audit_events.json").read_text())
    assert summary["events"] == len(events) == summary["allowed"] + summary["denied"]
    assert all(event["policy_sha256"] == summary["policy_sha256"] for event in events)
    assert all(event["correlation_id"] == summary["run_id"] for event in events)
    assert all(event["reason"] and event["policy_as_of"] for event in events)
    assert (tmp_path / "synthetic_requests.json").is_file()
    assert {event["decision"] for event in events} == {"allow", "deny"}
    again = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
                            capture_output=True, text=True)
    assert again.returncode == 1
    assert json.loads((tmp_path / "governance_summary.json").read_text()) == summary
