"""Chapter 13 Welch PSD educational checks."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"chapters/ch13-time-frequency/exercise_13_1_welch_sensitivity.py"

def load():
    spec=importlib.util.spec_from_file_location("ch13",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_welch_peak_and_resolution(tmp_path):
    m=load()
    report=m.run(tmp_path)
    a,b=report["comparisons"]
    assert a["frequency_spacing_hz"]==1.0
    assert b["frequency_spacing_hz"]==0.5
    assert a["alpha_peak_hz"]==10.0
    assert b["alpha_peak_hz"]==10.0
    assert a["alpha_power_uV2"]>0
    assert (tmp_path/"spectral_report.json").exists()

def test_cli_and_invalid_length(tmp_path):
    result=subprocess.run([sys.executable,str(SCRIPT),"--output-dir",str(tmp_path)],
                          capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)["synthetic"]
    m=load()
    try:
        m.welch_psd([0]*10,128,11)
        assert False,"odd length should fail"
    except ValueError:
        pass
