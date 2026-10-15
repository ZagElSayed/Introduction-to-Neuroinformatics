"""Numerical invariants and run preservation; supplied for local pytest execution."""
import csv
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT/'chapters/ch13-time-frequency/exercise_13_1_welch_sensitivity.py'


def load():
    spec=importlib.util.spec_from_file_location('ch13',SCRIPT)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_parseval_padding_and_amplitude():
    m=load()
    x=[3*math.sin(2*math.pi*7.25*j/128)+.02*j for j in range(128)]
    window=m.hann(128)
    mean=sum(x)/len(x)
    expected=sum(((v-mean)*w)**2 for v,w in zip(x,window))/sum(w*w for w in window)
    f,p=m.periodogram(x,128)
    fp,pp=m.periodogram(x,128,512)
    assert sum(p)*(f[1]-f[0]) == pytest.approx(expected,rel=1e-10,abs=1e-10)
    assert sum(pp)*(fp[1]-fp[0]) == pytest.approx(expected,rel=1e-10,abs=1e-10)
    assert pp[::4] == pytest.approx(p,rel=1e-10,abs=1e-10)
    _,doubled=m.periodogram([2*v for v in x],128)
    assert doubled == pytest.approx([4*v for v in p],rel=1e-10,abs=1e-10)
    _,zero=m.periodogram([3.0]*128,128)
    assert max(zero)==0


def test_run_evidence_and_full_frame_timing(tmp_path):
    m=load()
    report=m.run(tmp_path)
    a,b,padded=report['comparisons']
    assert [r['segments_averaged'] for r in (a,b,padded)]==[7,3,7]
    assert [r['frequency_spacing_hz'] for r in (a,b,padded)]==[1,.5,.25]
    assert [r['unpadded_spacing_hz'] for r in (a,b,padded)]==[1,.5,1]
    assert all(r['alpha_peak_hz']==10 for r in (a,b,padded))
    assert report['sample_mean_square_uV2']==pytest.approx(81.125)
    for r in (a,b,padded):
        assert r['full_grid_integral_uV2']==pytest.approx(r['mean_taper_weighted_detrended_energy_uV2'],rel=1e-10)
        assert r['alpha_power_uV2']>0 and 0<r['relative_alpha']<1
    assert report['review_status']=='review_required'
    assert report['accepted_as_neurally_valid'] is False
    assert [r['frame_count'] for r in report['time_frequency']]==[57,49]
    for r in report['time_frequency']:
        assert r['frame_step_s']==.125
        assert r['first_center_s']==(r['segment_samples']-1)/(2*128)
        with (tmp_path/r['power_file']).open(newline='') as stream:
            row=next(csv.DictReader(stream))
        assert int(row['start_sample'])==0
        assert int(row['stop_sample_exclusive'])==r['segment_samples']
    for name,digest in report['artifacts_sha256'].items():
        assert m.sha256(tmp_path/name)==digest
    previous=(tmp_path/'spectral_report.json').read_bytes()
    with pytest.raises(FileExistsError):m.run(tmp_path)
    assert (tmp_path/'spectral_report.json').read_bytes()==previous


def test_cli_and_invalid_inputs(tmp_path):
    result=subprocess.run([sys.executable,str(SCRIPT),'--output-dir',str(tmp_path)],
                          capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)['synthetic'] is True
    m=load()
    for rate in (0,-1,float('nan'),float('inf'),True):
        with pytest.raises(ValueError):m.welch_psd([0.0]*128,rate,64)
    for length in (0,3,11,130,True):
        with pytest.raises(ValueError):m.welch_psd([0.0]*128,128,length)
    for overlap in (-.1,1,float('nan')):
        with pytest.raises(ValueError):m.welch_psd([0.0]*128,128,64,overlap)
    with pytest.raises(ValueError):m.periodogram([0.0]*128,128,64)
    with pytest.raises(ValueError):m.periodogram([float('nan')]*128,128)
    with pytest.raises(ValueError):m.bandpower([0,1,3],[1,1,1],0,2)
