"""Verify Chapter 7 extension using generated synthetic inputs."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / "chapters/ch07-wearables"


def test_remote_monitoring_audit(tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "audit"
    subprocess.run([sys.executable, str(LAB / "exercise_7_1_multimodal_timeline.py"),
                    "--output-dir", str(source)], cwd=ROOT, check=True, capture_output=True)
    result = subprocess.run([sys.executable, str(LAB / "exercise_7_2_remote_monitoring.py"),
                             "--input-dir", str(source), "--output-dir", str(target)],
                            cwd=ROOT, check=True, capture_output=True, text=True)
    report = json.loads(result.stdout)
    assert report["source"] == "synthetic, not clinical"
    assert report["engineering"]["hypothetical_ecg_ppg_eda_imu_raw_bytes_per_second"] == 1050
    assert report["engineering"]["hypothetical_12_minute_outage_payload_bytes"] == 756000
    assert report["engineering"]["hypothetical_100_participants_30_days_payload_bytes"] == 90720000000
    assert {55.0, 56.0, 57.0}.issubset(set(report["coverage"]["excluded_window_start_s"]))
    assert (target / "quality_windows.csv").is_file()
    assert (target / "engineering_audit.json").is_file()
