"""Chapter 11 deny-by-default and audit tests."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch11-ethics-governance/exercise_11_1_policy_audit.py"

def load():
    spec = importlib.util.spec_from_file_location("ch11", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_deny_by_default():
    m = load()
    assert m.decide("analyst", "read_derivative", "derivative-table")
    assert not m.decide("analyst", "read_raw", "raw-eeg")
    assert not m.decide("collaborator", "export_derivative", "derivative-table")
    assert not m.decide("data_steward", "read_raw", "identity-linkage")
    assert not m.decide("unknown", "read_derivative", "derivative-table")

def test_cli_audit(tmp_path):
    result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(tmp_path)],
                            capture_output=True, text=True, check=True, timeout=30)
    summary = json.loads(result.stdout)
    assert summary["events"] == 6
    assert summary["allowed"] == 3
    assert summary["denied"] == 3
    assert summary["threat_scenarios"] >= 5
    audit = json.loads((tmp_path / "audit_events.json").read_text())
    assert {e["decision"] for e in audit} == {"allow", "deny"}
    assert all("correlation_id" in e and "timestamp" in e for e in audit)
