import importlib.util
import json
from pathlib import Path
import numpy as np
import pytest

PATH = Path(__file__).parents[1] / 'chapters/ch16-classical-ml/exercise_16_1_grouped_ml.py'
spec = importlib.util.spec_from_file_location('chapter16', PATH)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def test_nested_boundaries():
    x, y, groups = lab.generate(lab.DEFAULT)
    seen = []
    for train, test in lab.group_splits(y, groups, 3, 16):
        assert not set(groups[train]) & set(groups[test])
        seen.extend(test)
        for a, b in lab.group_splits(y[train], groups[train], 3, 17):
            assert not set(groups[train[a]]) & set(groups[train[b]])
            assert not set(train[a]) & set(test)
            assert not set(train[b]) & set(test)
    assert sorted(seen) == list(range(len(y)))


def test_reproduction_and_artifacts(tmp_path):
    config = dict(lab.DEFAULT, participants=24, repeats=3, outer_folds=2, inner_folds=2)
    a, b = tmp_path/'a', tmp_path/'b'
    first = lab.run(a, config)
    second = lab.run(b, json.loads((a/'config.json').read_text()))
    assert first['nested'] == second['nested']
    assert (a/'predictions.csv').read_bytes() == (b/'predictions.csv').read_bytes()
    assert (a/'split_manifest.json').read_bytes() == (b/'split_manifest.json').read_bytes()
    assert first['naive_row_knn']['overlapping_participants'] > 0
    assert set(first['artifact_sha256']) == {'config.json', 'split_manifest.json', 'predictions.csv', 'evaluation.png', 'model_card.md', 'development_logistic.joblib'}
    changed = dict(config, signal=2.0)
    x1, _, _ = lab.generate(config)
    x2, _, _ = lab.generate(changed)
    assert not np.array_equal(x1, x2)


def test_reject_invalid_config():
    for update in ({'participants': 23}, {'outer_folds': 99}, {'signal': float('nan')}, {'repeats': True}):
        with pytest.raises(ValueError):
            lab.validate(dict(lab.DEFAULT, **update))
    with pytest.raises(ValueError):
        lab.validate({'seed': 1})


def test_metrics_known_predictions():
    m = lab.metrics(np.array([0,0,1,1]), np.array([0.1,0.2,0.8,0.9]))
    assert m['roc_auc'] == 1
    assert m['sensitivity'] == m['specificity'] == 1
    assert m['brier'] == pytest.approx(0.025)
