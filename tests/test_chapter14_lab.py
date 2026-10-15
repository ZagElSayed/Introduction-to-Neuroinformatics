"""Chapter 14 linear inverse sensitivity lab tests."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
import math
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"chapters/ch14-source-localization/exercise_14_1_inverse_sensitivity.py"

def load():
    spec=importlib.util.spec_from_file_location("ch14",SCRIPT)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def test_nonuniqueness_and_optimality():
    m=load()
    y=m.forward(m.G,m.TRUE_SOURCE)
    assert y==[1.0,0.2]
    alternate=[a+b for a,b in zip(m.TRUE_SOURCE,m.NULL_VECTOR)]
    assert m.forward(m.G,m.NULL_VECTOR)==pytest.approx([0,0],abs=1e-14)
    assert m.forward(m.G,alternate)==pytest.approx(y,abs=1e-14)
    assert alternate != list(m.TRUE_SOURCE)
    norms, residuals=[],[]
    for lam in (.01,.1,1):
        estimate=m.inverse(m.G,y,lam)
        assert m.inverse(m.G,m.forward(m.G,alternate),lam)==pytest.approx(estimate)
        residual=[a-b for a,b in zip(m.forward(m.G,estimate),y)]
        # Independent first-order optimality condition for the stated objective.
        gradient=[sum(row[i]*r for row,r in zip(m.G,residual))+lam*estimate[i] for i in range(3)]
        assert gradient==pytest.approx([0,0,0],abs=1e-12)
        assert sum(a*b for a,b in zip(estimate,m.NULL_VECTOR))==pytest.approx(0,abs=1e-12)
        norms.append(m.norm(estimate));residuals.append(m.norm(residual))
    assert norms[0]>norms[1]>norms[2]
    assert residuals[0]<residuals[1]<residuals[2]

def test_resolution_columns_and_model_mismatch():
    m=load()
    k=m.inverse_operator(m.G,.1)
    resolution=m.multiply(k,m.G)
    for j in range(3):
        basis=[float(i==j) for i in range(3)]
        recovered=m.inverse(m.G,m.forward(m.G,basis),.1)
        assert [row[j] for row in resolution]==pytest.approx(recovered)
    k_alt=m.inverse_operator(m.ALTERED_G,.1)
    assumed=m.multiply(k_alt,m.ALTERED_G)
    effective=m.multiply(k_alt,m.G)
    assert any(abs(a-b)>1e-5 for r,s in zip(assumed,effective) for a,b in zip(r,s))

def test_run_evidence_and_preservation(tmp_path):
    m=load();report=m.run(tmp_path)
    assert len(report['results'])==12
    assert report['nonuniqueness_sensor_difference_l2']<1e-12
    assert report['review_status']=='review_required'
    assert report['accepted_as_neurally_valid'] is False
    assert {r['data_case'] for r in report['results']}=={'noiseless','fixed_sensor_perturbation'}
    assert all(math.isfinite(r['source_error_l2']) and r['source_error_l2']>=0 for r in report['results'])
    for name,digest in report['artifacts_sha256'].items():
        assert m.digest(tmp_path/name)==digest
    matrices=json.loads((tmp_path/'resolution_matrices.json').read_text())
    assert len(matrices)==6
    previous=(tmp_path/'source_inverse_report.json').read_bytes()
    with pytest.raises(FileExistsError):m.run(tmp_path)
    assert (tmp_path/'source_inverse_report.json').read_bytes()==previous

def test_invalid_inputs():
    m=load()
    for lam in (0,-1,float('nan'),float('inf'),True):
        with pytest.raises(ValueError):m.inverse(m.G,[1,.2],lam)
    for gain in ([],[[]],[[1,2],[1]],[[1,float('nan')],[2,3]]):
        with pytest.raises(ValueError):m.inverse(gain,[1,.2],.1)
    with pytest.raises(ValueError):m.forward(m.G,[1,0])
    with pytest.raises(ValueError):m.inverse(m.G,[1,float('inf')],.1)
    with pytest.raises(ValueError):m.multiply([[1,2]],[[1,2]])
    with pytest.raises(ValueError):m.solve([[1,2],[2,4]],[1,2])

def test_cli(tmp_path):
    r=subprocess.run([sys.executable,str(SCRIPT),"--output-dir",str(tmp_path)],
                     capture_output=True,text=True,check=True,timeout=30)
    report=json.loads(r.stdout)
    assert report["lead_field_shape"]==[2,3]
    assert len(report["results"])==12
    assert len(report['artifacts_sha256'])==4
    assert (tmp_path/"inverse_sensitivity.csv").exists()
    assert (tmp_path/"source_inverse_report.json").exists()

