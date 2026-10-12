import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest
import torch

PATH = Path(__file__).parents[1]/'chapters/ch17-deep-learning/exercise_17_1_deep_pipeline.py'
spec = importlib.util.spec_from_file_location('chapter17', PATH)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def small_config():
    return dict(lab.DEFAULT,participants=24,windows=2,epochs=3,patience=2)


def test_split_and_training_statistics():
    x,y,g = lab.generate(small_config())
    split = lab.partition(y,g,17,True)
    for a,b in [('train','validation'),('train','test'),('validation','test')]:
        assert not set(g[split[a]]) & set(g[split[b]])
    assert sorted(np.concatenate(list(split.values()))) == list(range(len(y)))
    mean,scale = lab.normalize_fit(x[split['train']])
    assert mean.shape == scale.shape == (1,2,1)
    np.testing.assert_allclose(((x[split['train']]-mean)/scale).mean(axis=(0,2)),0,atol=1e-6)
    naive = lab.partition(y,g,17,False)
    assert set(g[naive['train']]) & set(g[naive['test']])


def test_shape_and_loss_gradient():
    model = lab.CompactCNN()
    assert model(torch.zeros(5,2,128)).shape == (5,)
    z = torch.tensor([0.0],requires_grad=True)
    torch.nn.BCEWithLogitsLoss()(z,torch.ones(1)).backward()
    assert z.grad.item() == pytest.approx(-0.5)


def test_test_data_cannot_select_checkpoint():
    config = small_config()
    x,y,g = lab.generate(config)
    split = lab.partition(y,g,17,True)
    mean,scale = lab.normalize_fit(x[split['train']])
    normalized = (x-mean)/scale
    first = lab.train_cnn(normalized,y,split,config)
    altered = normalized.copy(); altered[split['test']] = 999
    changed_labels = y.copy(); changed_labels[split['test']] = 1-y[split['test']]
    second = lab.train_cnn(altered,changed_labels,split,config)
    assert first[2:4] == second[2:4]
    for key in first[1]:
        assert torch.equal(first[1][key],second[1][key])
    assert first[3] == min(first[2],key=lambda c:c['validation_loss'])['epoch']


def test_config_reproduction_and_saved_checkpoints(tmp_path):
    first = lab.run(tmp_path/'a',small_config())
    config = json.loads((tmp_path/'a/config.json').read_text())
    second = lab.run(tmp_path/'b',config)
    assert first['data_sha256'] == second['data_sha256']
    assert (tmp_path/'a/predictions.csv').read_bytes() == (tmp_path/'b/predictions.csv').read_bytes()
    assert (tmp_path/'a/split_manifest.json').read_bytes() == (tmp_path/'b/split_manifest.json').read_bytes()
    assert first['experiments']['grouped_participants']['participant_metrics'] == second['experiments']['grouped_participants']['participant_metrics']
    assert all((tmp_path/'a'/name).exists() for name in first['artifact_sha256'])
    for k in ('naive_rows','grouped_participants'):
        assert (tmp_path/f'a/{k}_curves.csv').read_bytes() == (tmp_path/f'b/{k}_curves.csv').read_bytes()


def test_invalid_configuration():
    for change in ({'participants':23},{'device':'mps'},{'learning_rate':0},{'signal':float('inf')},{'epochs':True}):
        with pytest.raises(ValueError):
            lab.validate(dict(lab.DEFAULT,**change))
