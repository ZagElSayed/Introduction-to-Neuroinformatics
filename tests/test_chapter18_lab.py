import importlib.util
import json
import hashlib
from pathlib import Path
import numpy as np
import pytest
from PIL import Image

PATH=Path(__file__).parents[1]/'chapters/ch18-vision-ai/exercise_18_1_render_audit.py'
spec=importlib.util.spec_from_file_location('chapter18',PATH);lab=importlib.util.module_from_spec(spec);spec.loader.exec_module(lab)

def small(): return dict(lab.DEFAULT,participants=24,windows=2,epochs=2,image_size=32)

def test_psd_normalization_and_contract():
    c=small();x,_,y,g=lab.generate(c);p=lab.power_maps(x,c)
    assert p.shape==(48,33,7)
    n=c['segment'];w=np.hanning(n);segment=x[:,:n]-x[:,:n].mean(axis=1,keepdims=True)
    expected=(segment**2*w**2).sum(axis=1)/(w@w)
    np.testing.assert_allclose(p[:,:,0].sum(axis=1)*(c['sampling_rate']/n),expected,rtol=1e-6)
    image=lab.render(p[0],c);assert image.shape==(32,32) and image.dtype==np.uint8
    split=lab.grouped_split(y,g,18)
    for a,b in [('train','validation'),('train','test'),('validation','test')]:assert not set(g[split[a]])&set(g[split[b]])

def test_lossless_manifest_and_reproduction(tmp_path):
    a,b=tmp_path/'a',tmp_path/'b'
    first=lab.run(a,small());second=lab.run(b,json.loads((a/'config.json').read_text()))
    assert first['lossless_control']==dict(file_bytes_differ=True,decoded_pixels_equal=True,prediction_equal=True)
    assert first['shortcut_control']['label_recoverable_from_corner']==1
    assert (a/'predictions.csv').read_bytes()==(b/'predictions.csv').read_bytes()
    assert (a/'split_manifest.json').read_bytes()==(b/'split_manifest.json').read_bytes()
    manifest=json.loads((a/'image_manifest.json').read_text());assert len(manifest)==48
    for item in manifest:
        image=np.array(Image.open(a/item['path']))
        assert image.shape==(32,32)
        assert item['png_sha256']==hashlib.sha256((a/item['path']).read_bytes()).hexdigest()
        assert item['decoded_pixel_sha256']==hashlib.sha256(image.tobytes()).hexdigest()
        assert item['split'] in ('train','validation','test')
        assert item['source_row']>=0 and item['mode']=='L'
    assert first['cnn']==second['cnn']

def test_test_data_cannot_select_checkpoint():
    import torch
    c=small();x,_,y,g=lab.generate(c);pixels=np.stack([lab.render(p,c) for p in lab.power_maps(x,c)])
    split=lab.grouped_split(y,g,18);first=lab.train(pixels,y,split,c)
    altered=pixels.copy();altered[split['test']]=0
    labels=y.copy();labels[split['test']]=1-labels[split['test']]
    second=lab.train(altered,labels,split,c)
    assert first[2:]==second[2:]
    for key in first[1]:assert torch.equal(first[1][key],second[1][key])

def test_reject_bad_rendering_config():
    for change in ({'db_max':-50},{'segment':300},{'hop':0},{'signal':float('nan')},{'epochs':True}):
        with pytest.raises(ValueError):lab.validate(dict(lab.DEFAULT,**change))
