"""Synthetic repeated-measures ML: educational labels, never clinical EEG."""
import argparse
import csv
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from sklearn.base import clone
from sklearn.calibration import calibration_curve
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, average_precision_score,
                             confusion_matrix, f1_score, precision_score, roc_auc_score)
from sklearn.model_selection import ParameterGrid, StratifiedKFold, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

DEFAULT = dict(seed=16, participants=60, repeats=6, outer_folds=3,
               inner_folds=3, signal=0.6, fingerprint_scale=5.0)


def validate(config):
    if set(config) != set(DEFAULT):
        raise ValueError('Configuration must contain exactly: ' + ', '.join(DEFAULT))
    for key in ('seed', 'participants', 'repeats', 'outer_folds', 'inner_folds'):
        if type(config[key]) is not int:
            raise ValueError(key + ' must be an integer')
    n, k, inner = config['participants'], config['outer_folds'], config['inner_folds']
    if config['seed'] < 0 or n < 24 or n % 2 or config['repeats'] < 2:
        raise ValueError('Use a nonnegative seed, even participants >=24, repeats >=2')
    if k < 2 or inner < 2 or n // 2 < k or n // 2 - int(np.ceil(n / (2*k))) < inner:
        raise ValueError('Too few participants per class for the requested nested folds')
    for key in ('signal', 'fingerprint_scale'):
        if isinstance(config[key], bool) or not isinstance(config[key], (float, int)) or not np.isfinite(config[key]) or config[key] < 0:
            raise ValueError(key + ' must be finite and nonnegative')
    return config


def generate(config):
    rng = np.random.default_rng(config['seed'])
    n, r = config['participants'], config['repeats']
    labels = rng.permutation(np.tile([0, 1], n // 2))
    groups = np.repeat(np.arange(n), r)
    y = labels[groups]
    physiological = rng.normal(size=(n, 4))
    physiological[:, 0] += config['signal'] * (2 * labels - 1)
    features = physiological[groups] + rng.normal(0, 0.15, (n*r, 4))
    # Stable synthetic identity coordinates make memorization easy in a row split.
    # They have no label relationship for a previously unseen participant.
    fingerprints = config['fingerprint_scale'] * np.eye(n)[groups]
    return np.column_stack([features, fingerprints]), y, groups


def group_splits(y, groups, folds, seed):
    y, groups = np.asarray(y), np.asarray(groups)
    if y.ndim != 1 or groups.ndim != 1 or len(y) != len(groups) or not len(y):
        raise ValueError('Targets and participant IDs must be aligned nonempty vectors')
    if type(folds) is not int or folds < 2:
        raise ValueError('Use at least two participant-stratified folds')
    people, first = np.unique(groups, return_index=True)
    labels = y[first]
    if any(len(np.unique(y[groups == person])) != 1 for person in people):
        raise ValueError('This participant-target demonstration requires one label per person')
    classes, counts = np.unique(labels, return_counts=True)
    if not np.array_equal(classes, [0, 1]) or counts.min() < folds:
        raise ValueError('Each binary class needs at least one participant per fold')
    splitter = StratifiedKFold(folds, shuffle=True, random_state=seed)
    return [(np.flatnonzero(np.isin(groups, people[a])),
             np.flatnonzero(np.isin(groups, people[b])))
            for a, b in splitter.split(people, labels)]


def participant_predictions(y, p, groups):
    """One target and mean held-out probability per participant, in sorted ID order."""
    y, p, groups = np.asarray(y), np.asarray(p), np.asarray(groups)
    if any(a.ndim != 1 for a in (y, p, groups)) or not len(y) or not (len(y) == len(p) == len(groups)):
        raise ValueError('Targets, probabilities and groups must align')
    people = np.unique(groups)
    if any(len(np.unique(y[groups == g])) != 1 for g in people):
        raise ValueError('Aggregation requires one target per participant')
    return (people, np.array([y[groups == g][0] for g in people]),
            np.array([p[groups == g].mean() for g in people]))


def select_parameters(pipeline, grid, x, y, groups, splits):
    """Tune mean inner-fold participant ROC-AUC; refit on supplied development rows.

    All split indices are relative to x/y/groups passed here. Equal score ties
    retain the first ParameterGrid candidate. No outer-test rows enter this call.
    """
    results = []
    for params in ParameterGrid(grid):
        scores = []
        for train, validation in splits:
            if set(groups[train]) & set(groups[validation]):
                raise ValueError('Participant overlap in parameter-selection split')
            fitted = clone(pipeline).set_params(**params).fit(x[train], y[train])
            probabilities = fitted.predict_proba(x[validation])[:, 1]
            _, target, predicted = participant_predictions(y[validation], probabilities, groups[validation])
            scores.append(float(roc_auc_score(target, predicted)))
        if not scores:
            raise ValueError('Parameter selection requires validation folds')
        results.append(dict(params=params, fold_participant_roc_auc=scores,
                            mean_participant_roc_auc=float(np.mean(scores))))
    best = max(results, key=lambda item: item['mean_participant_roc_auc'])
    fitted = clone(pipeline).set_params(**best['params']).fit(x, y)
    return fitted, best['params'], results


def metrics(y, p):
    y, p = np.asarray(y), np.asarray(p)
    if y.ndim != 1 or p.ndim != 1 or len(y) != len(p) or not len(y):
        raise ValueError('Metrics require aligned nonempty target and probability vectors')
    if not np.isin(y, [0, 1]).all() or not np.isfinite(p).all() or ((p < 0) | (p > 1)).any():
        raise ValueError('Use binary targets and finite probabilities in [0, 1]')
    predicted = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    both_classes = len(np.unique(y)) == 2
    return dict(
        accuracy=accuracy_score(y, predicted),
        sensitivity=float(tp/(tp+fn)) if tp+fn else None,
        specificity=float(tn/(tn+fp)) if tn+fp else None,
        precision=precision_score(y, predicted, zero_division=0),
        f1=f1_score(y, predicted, zero_division=0),
        roc_auc=roc_auc_score(y, p) if both_classes else None,
        average_precision=average_precision_score(y, p) if tp+fn else None,
        brier=float(np.mean((p-y)**2)), threshold=0.5,
        confusion=dict(tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp)),
        observations=int(len(y)))



def candidates(seed):
    return {
        'dummy': (make_pipeline(StandardScaler(), DummyClassifier(strategy='prior')), {}),
        'logistic': (make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)),
                     {'logisticregression__C': [0.1, 1.0]}),
        'knn': (make_pipeline(StandardScaler(), KNeighborsClassifier()),
                {'kneighborsclassifier__n_neighbors': [1, 3]}),
        'forest': (make_pipeline(StandardScaler(), RandomForestClassifier(n_estimators=60, random_state=seed, n_jobs=1)),
                   {'randomforestclassifier__max_depth': [3, None]})}


def run(output_dir, config=None):
    config = validate(dict(DEFAULT) if config is None else config)
    out = Path(output_dir)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise FileExistsError('Use a new or empty output directory; preserve prior runs')
    out.mkdir(parents=True, exist_ok=True)
    x, y, groups = generate(config)
    ids = np.arange(len(y))
    train, test = train_test_split(ids, test_size=0.3, stratify=y, random_state=config['seed'])
    naive = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))
    naive.fit(x[train], y[train])
    report = dict(schema_version=2, run_id=str(uuid4()), created_utc=datetime.now(timezone.utc).isoformat(),
                  review_status='review_required', accepted=False,
                  data_kind='synthetic educational repeated feature vectors; not EEG', config=dict(config),
                  inner_objective='mean inner-fold participant ROC-AUC after within-person probability averaging',
                  aggregation='mean row probability per participant', decision_threshold=0.5,
                  naive_row_knn=dict(metrics=metrics(y[test], naive.predict_proba(x[test])[:, 1]),
                                     overlapping_participants=len(set(groups[train]) & set(groups[test]))),
                  nested={}, software=dict(python=platform.python_version(), numpy=np.__version__,
                                          sklearn=sklearn.__version__, joblib=joblib.__version__,
                                          matplotlib=matplotlib.__version__))
    manifest = dict(naive=dict(train_rows=train.tolist(), test_rows=test.tolist()), outer=[])
    predictions, all_results = [], {}
    outer = group_splits(y, groups, config['outer_folds'], config['seed'])
    for name, (pipeline, grid) in candidates(config['seed']).items():
        p = np.zeros(len(y))
        fold_results = []
        for fold, (train, test) in enumerate(outer):
            inner = group_splits(y[train], groups[train], config['inner_folds'], config['seed']+fold+1)
            fitted, best, selection = select_parameters(pipeline, grid, x[train], y[train], groups[train], inner)
            p[test] = fitted.predict_proba(x[test])[:, 1]
            people, py, pp = participant_predictions(y[test], p[test], groups[test])
            fold_results.append(dict(fold=fold, best_params=best, inner_selection=selection,
                                     participant_metrics=metrics(py, pp)))
            if name == 'dummy':
                manifest['outer'].append(dict(fold=fold, train_rows=train.tolist(), test_rows=test.tolist(),
                    train_participants=np.unique(groups[train]).tolist(), test_participants=people.tolist(),
                    inner=[dict(train_rows=train[a].tolist(), validation_rows=train[b].tolist()) for a,b in inner]))
        people, py, pp = participant_predictions(y, p, groups)
        report['nested'][name] = dict(pooled_participant_metrics=metrics(py, pp), folds=fold_results)
        all_results[name] = (py, pp)
        predictions.extend(dict(model=name, participant=int(g), target=int(label), probability=float(prob))
                           for g, label, prob in zip(people, py, pp))
    # Fixed logistic family: tuning uses grouped folds on all available development data.
    # This deployment-shaped artifact has no independent prospective validation.
    pipeline, grid = candidates(config['seed'])['logistic']
    refitted, best, selection = select_parameters(pipeline, grid, x, y, groups, outer)
    report['development_refit'] = dict(family='logistic', best_params=best, selection=selection,
                                      independent_performance_estimate=False)
    joblib.dump(refitted, out/'development_logistic.joblib')
    contract = dict(feature_names=['physiology_'+str(i+1) for i in range(4)] +
                    ['synthetic_identity_'+str(i) for i in range(config['participants'])],
                    rows=int(x.shape[0]), columns=int(x.shape[1]), dtype=str(x.dtype),
                    target='invented binary participant label', positive_class=1,
                    groups='participant IDs; one target per person', missing_values='none generated',
                    identity_warning='Artificial one-hot participant basis; not a deployable feature schema')
    (out/'input_contract.json').write_text(json.dumps(contract, indent=2, sort_keys=True)+'\n')
    with (out/'row_manifest.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['row_id', 'participant', 'target'])
        writer.writeheader()
        writer.writerows(dict(row_id=int(i), participant=int(g), target=int(label))
                         for i, g, label in zip(ids, groups, y))
    for filename, obj in [('config.json', config), ('split_manifest.json', manifest)]:
        (out/filename).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')
    with (out/'predictions.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    report['reliability'] = {}
    colors = ['#142D4E', '#167D91', '#7556A8', '#D87C36']
    for (name, (py, pp)), color in zip(all_results.items(), colors):
        fraction, predicted = calibration_curve(py, pp, n_bins=5)
        counts = np.bincount(np.searchsorted(np.linspace(0, 1, 6)[1:-1], pp), minlength=5)
        report['reliability'][name] = dict(requested_bins=5, strategy='uniform',
            nonempty_bin_counts=counts[counts > 0].tolist(),
            mean_probability=predicted.tolist(), observed_fraction=fraction.tolist())
        axes[0].plot(predicted, fraction, 'o-', label=name, color=color)
    axes[0].plot([0,1], [0,1], '--', color='gray')
    axes[0].set(xlabel='Mean predicted probability', ylabel='Observed positive fraction', title='Participant OOF reliability')
    axes[0].legend()
    axes[1].bar(list(all_results), [metrics(*v)['roc_auc'] for v in all_results.values()], color=colors)
    axes[1].set(ylim=(0,1), ylabel='ROC-AUC', title='Participant OOF discrimination')
    fig.savefig(out/'evaluation.png', dpi=180)
    plt.close(fig)
    (out/'model_card.md').write_text('# Synthetic teaching model\n\nIntended use: study leakage and nested validation. No patient-care use.\n'
        '\nInputs: four invented physiology-like features plus synthetic identity coordinates. Labels are balanced artificial participant labels.\n'
        '\nBoth inner tuning and outer evaluation aggregate row probabilities by participant. Inner selection maximizes mean fold participant ROC-AUC; first ParameterGrid candidate wins ties.\n'
        '\nAverage precision is reported, not trapezoidal PR-AUC. Threshold 0.5 and aggregation by mean were fixed before evaluation.\n'
        '\nReliability is assessed, not recalibrated. Fold spread is descriptive, not a confidence interval. Pooled OOF rankings combine separate fitted models.\n'
        '\nThe serialized logistic model is tuned/refit on all development data; nested predictions came from other fitted models. No external validation or site study is performed.\n'
        '\nRun status is review_required with accepted: false. Never overwrite an earlier run; use a new output directory.\n'
        '\nUndefined single-class ROC-AUC is null; sensitivity/specificity with no relevant class are null. Precision and F1 use zero_division=0.\n'
        '\nNever load untrusted joblib files. Reproduction requires matching software versions as well as config and source.\n')
    report['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['feature_sha256'] = hashlib.sha256(x.tobytes()).hexdigest()
    report['target_sha256'] = hashlib.sha256(y.tobytes()).hexdigest()
    report['groups_sha256'] = hashlib.sha256(groups.tobytes()).hexdigest()
    report['config_sha256'] = hashlib.sha256(json.dumps(config, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    report['artifact_sha256'] = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())
                                  if f.name in ['config.json','split_manifest.json','predictions.csv','evaluation.png','model_card.md','development_logistic.joblib','input_contract.json','row_manifest.csv']}
    (out/'ml_report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/ch16/run01'))
    args = parser.parse_args()
    run(args.output_dir, json.loads(args.config.read_text()) if args.config else None)

