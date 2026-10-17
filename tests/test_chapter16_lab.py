import importlib.util
import hashlib
import json
from pathlib import Path
import numpy as np
import pytest
from sklearn.base import BaseEstimator, ClassifierMixin

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
    assert set(first['artifact_sha256']) == {'config.json', 'split_manifest.json', 'predictions.csv', 'evaluation.png', 'model_card.md', 'development_logistic.joblib', 'input_contract.json', 'row_manifest.csv'}
    for filename, digest in first['artifact_sha256'].items():
        assert hashlib.sha256((a/filename).read_bytes()).hexdigest() == digest
    assert first['run_id'] != second['run_id']
    assert first['accepted'] is False
    assert first['review_status'] == 'review_required'
    for bins in first['reliability'].values():
        assert sum(bins['nonempty_bin_counts']) == 24
        assert len(bins['nonempty_bin_counts']) == len(bins['mean_probability']) == len(bins['observed_fraction'])
    contract = json.loads((a/'input_contract.json').read_text())
    assert (contract['rows'], contract['columns']) == (72, 28)
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


class ColumnProbabilityClassifier(ClassifierMixin, BaseEstimator):
    """Deterministic scores isolate the participant versus row objective."""
    def __init__(self, column=0):
        self.column = column

    def fit(self, x, y):
        self.classes_ = np.array([0, 1])
        return self

    def predict_proba(self, x):
        p = x[:, self.column]
        return np.column_stack([1-p, p])


def test_selection_uses_participant_ranking_not_row_ranking():
    # Candidate 0 wins on rows (AUC .75 versus .25), but loses after
    # participant averaging (AUC 0 versus 1). Unequal repeats expose the distinction.
    x = np.array([[0, 0], [0, .6], [0, .6], [1, .6], [.2, .5], [0, 0], [1, 1]])
    y = np.array([0, 0, 0, 0, 1, 0, 1])
    groups = np.array([0, 0, 0, 0, 1, 2, 3])
    splits = [(np.array([5, 6]), np.arange(5))]
    _, best, scores = lab.select_parameters(ColumnProbabilityClassifier(), {'column': [0, 1]}, x, y, groups, splits)
    assert best == {'column': 1}
    assert [s['mean_participant_roc_auc'] for s in scores] == [0, 1]


def test_participant_aggregation_and_target_contract():
    ids, targets, p = lab.participant_predictions(np.array([1, 1, 0]), np.array([.2, .8, .4]), np.array([9, 9, 4]))
    assert ids.tolist() == [4, 9]
    assert targets.tolist() == [0, 1]
    assert p.tolist() == pytest.approx([.4, .5])
    with pytest.raises(ValueError):
        lab.participant_predictions(np.array([0, 1]), np.array([.1, .9]), np.array([4, 4]))


def test_single_class_and_invalid_probabilities():
    m = lab.metrics(np.array([0, 0]), np.array([.1, .2]))
    assert m['roc_auc'] is None and m['sensitivity'] is None
    assert m['average_precision'] is None
    for p in ([float('nan'), .5], [-.1, .5], [1.1, .5]):
        with pytest.raises(ValueError):
            lab.metrics(np.array([0, 1]), np.array(p))


def test_existing_run_is_preserved(tmp_path):
    out = tmp_path/'preserved'
    out.mkdir()
    marker = out/'existing.txt'
    marker.write_text('retain this run')
    with pytest.raises(FileExistsError):
        lab.run(out)
    assert marker.read_text() == 'retain this run'


def test_reject_inconsistent_participant_labels():
    with pytest.raises(ValueError):
        lab.group_splits(np.array([0, 1, 0, 1]), np.array([0, 0, 1, 2]), 2, 16)

