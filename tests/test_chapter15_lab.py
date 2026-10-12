"""Chapter 15 synthetic graph checks."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"chapters/ch15-brain-networks/exercise_15_1_graph_sensitivity.py"

def load():
    spec=importlib.util.spec_from_file_location("ch15",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_graph_metrics_and_validation():
    m=load()
    a=m.matrix()
    m.validate(a)
    g=m.threshold(a,0.4)
    stats=m.metrics(a,g)
    assert len(stats["degree"])==len(m.NODES)
    assert 0<stats["density"]<1
    assert 0<=stats["global_efficiency"]<=1
    bad=[row[:] for row in a]
    bad[0][1]=2
    try:
        m.validate(bad)
        assert False,"Invalid matrix must fail"
    except ValueError:
        pass

def test_cli(tmp_path):
    p=subprocess.run([sys.executable,str(SCRIPT),"--output-dir",str(tmp_path)],
                     capture_output=True,text=True,check=True,timeout=30)
    summary=json.loads(p.stdout)
    assert summary["comparisons"]==6
    report=json.loads((tmp_path/"graph_report.json").read_text())
    assert len(report["results"])==6
    assert report["original_matrix"]!=report["confounded_matrix"]
    assert len(summary["output_sha256"])==64

def test_threshold_density_and_disconnected_efficiency():
    m=load()
    a=m.matrix()
    g=m.threshold(a,0.2)
    stats=m.metrics(a,g)
    assert sum(stats["degree"])==6  # three undirected edges
    assert abs(stats["density"]-0.2)<1e-12
    assert stats["components"]>=1
    assert all(0<=c<=1 for c in stats["clustering"])
    # Strength is intentionally computed on the unthresholded weighted matrix.
    assert stats["strength"]==[sum(row) for row in a]

def test_invalid_density_and_matrix():
    m=load()
    a=m.matrix()
    for density in (0,1.01):
        try:
            m.threshold(a,density)
            assert False,"Invalid density should fail"
        except ValueError:
            pass
    bad=[row[:] for row in a]
    bad[0][1]=float("nan")
    try:
        m.validate(bad)
        assert False,"NaN should fail validation"
    except ValueError:
        pass
