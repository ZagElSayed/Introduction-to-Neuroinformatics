"""Chapter 14 linear inverse sensitivity lab tests."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"chapters/ch14-source-localization/exercise_14_1_inverse_sensitivity.py"

def load():
    spec=importlib.util.spec_from_file_location("ch14",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_forward_and_regularization():
    m=load()
    y=m.forward(m.G,m.TRUE_SOURCE)
    assert y==[1.0,0.2]
    a=m.inverse(m.G,y,0.01)
    b=m.inverse(m.G,y,1.0)
    assert len(a)==3
    assert sum(x*x for x in b)<sum(x*x for x in a)

def test_cli(tmp_path):
    r=subprocess.run([sys.executable,str(SCRIPT),"--output-dir",str(tmp_path)],
                     capture_output=True,text=True,check=True,timeout=30)
    report=json.loads(r.stdout)
    assert report["lead_field_shape"]==[2,3]
    assert len(report["results"])==6
    assert len(report["output_sha256"])==64
    assert (tmp_path/"inverse_sensitivity.csv").exists()
    assert (tmp_path/"source_inverse_report.json").exists()
