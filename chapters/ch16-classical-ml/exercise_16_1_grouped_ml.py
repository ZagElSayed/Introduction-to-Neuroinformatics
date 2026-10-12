"""Synthetic repeated-measures ML: educational labels, never clinical EEG."""
import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path

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
from sklearn.metrics import (accuracy_score, average_precision_score, brier_score_loss,
                             confusion_matrix, f1_score, precision_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
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
    people, first = np.unique(groups, return_index=True)
    labels = y[first]
    if any(len(np.unique(y[groups == person])) != 1 for person in people):
        raise ValueError('This participant-target demonstration requires one label per person')
    splitter = StratifiedKFold(folds, shuffle=True, random_state=seed)
    return [(np.flatnonzero(np.isin(groups, people[a])),
             np.flatnonzero(np.isin(groups, people[b])))
            for a, b in splitter.split(people, labels)]


def metrics(y, p):
    predicted = (p >= 0.5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return dict(accuracy=accuracy_score(y, predicted), sensitivity=tp/(tp+fn),
                specificity=tn/(tn+fp), precision=precision_score(y, predicted, zero_division=0),
                f1=f1_score(y, predicted, zero_division=0), roc_auc=roc_auc_score(y, p),
                average_precision=average_precision_score(y, p), brier=brier_score_loss(y, p))


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
    out.mkdir(parents=True, exist_ok=True)
    x, y, groups = generate(config)
    ids = np.arange(len(y))
    train, test = train_test_split(ids, test_size=0.3, stratify=y, random_state=config['seed'])
    naive = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=1))
    naive.fit(x[train], y[train])
    report = dict(data_kind='synthetic educational repeated feature vectors; not EEG', config=config,
                  naive_row_knn=dict(metrics=metrics(y[test], naive.predict_proba(x[test])[:, 1]),
                                     overlapping_participants=len(set(groups[train]) & set(groups[test]))),
                  nested={}, software=dict(python=platform.python_version(), numpy=np.__version__,
                                          sklearn=sklearn.__version__, joblib=joblib.__version__))
    manifest = dict(naive=dict(train_rows=train.tolist(), test_rows=test.tolist()), outer=[])
    predictions, all_results = [], {}
    outer = group_splits(y, groups, config['outer_folds'], config['seed'])
    for name, (pipeline, grid) in candidates(config['seed']).items():
        p = np.zeros(len(y))
        fold_results = []
        for fold, (train, test) in enumerate(outer):
            inner = group_splits(y[train], groups[train], config['inner_folds'], config['seed']+fold+1)
            if name == 'dummy':
                fitted = clone(pipeline).fit(x[train], y[train])
                best = {}
            else:
                search = GridSearchCV(pipeline, grid, cv=inner, scoring='roc_auc', n_jobs=1, error_score='raise')
                search.fit(x[train], y[train])
                fitted, best = search.best_estimator_, search.best_params_
            p[test] = fitted.predict_proba(x[test])[:, 1]
            people = np.unique(groups[test])
            py = np.array([y[groups == g][0] for g in people])
            pp = np.array([p[(groups == g) & np.isin(ids, test)].mean() for g in people])
            fold_results.append(dict(fold=fold, best_params=best, participant_metrics=metrics(py, pp)))
            if name == 'dummy':
                manifest['outer'].append(dict(fold=fold, train_rows=train.tolist(), test_rows=test.tolist(),
                    train_participants=np.unique(groups[train]).tolist(), test_participants=people.tolist(),
                    inner=[dict(train_rows=train[a].tolist(), validation_rows=train[b].tolist()) for a,b in inner]))
        people = np.unique(groups)
        py = np.array([y[groups == g][0] for g in people])
        pp = np.array([p[groups == g].mean() for g in people])
        report['nested'][name] = dict(pooled_participant_metrics=metrics(py, pp), folds=fold_results)
        all_results[name] = (py, pp)
        predictions.extend(dict(model=name, participant=int(g), target=int(label), probability=float(prob))
                           for g, label, prob in zip(people, py, pp))
    # Fixed logistic family: tuning uses grouped folds on all available development data.
    # This deployment-shaped artifact has no independent prospective validation.
    pipeline, grid = candidates(config['seed'])['logistic']
    search = GridSearchCV(pipeline, grid, cv=outer, scoring='roc_auc', n_jobs=1, error_score='raise')
    search.fit(x, y)
    joblib.dump(search.best_estimator_, out/'development_logistic.joblib')
    for filename, obj in [('config.json', config), ('split_manifest.json', manifest)]:
        (out/filename).write_text(json.dumps(obj, indent=2, sort_keys=True)+'\n')
    with (out/'predictions.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')
    colors = ['#142D4E', '#167D91', '#7556A8', '#D87C36']
    for (name, (py, pp)), color in zip(all_results.items(), colors):
        fraction, predicted = calibration_curve(py, pp, n_bins=5)
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
        '\nReported nested estimates use one mean probability per held-out participant. Inner tuning uses row ROC-AUC; equal repeats give equal participant row weights but do not make rows independent.\n'
        '\nAverage precision is reported, not trapezoidal PR-AUC. Threshold 0.5 and aggregation by mean were fixed before evaluation.\n'
        '\nReliability is assessed, not recalibrated. Fold spread is descriptive, not a confidence interval. Pooled OOF rankings combine separate fitted models.\n'
        '\nThe serialized logistic model is tuned/refit on all development data; nested predictions came from other fitted models. No external validation or site study is performed.\n'
        '\nNever load untrusted joblib files. Reproduction requires matching software versions as well as config and source.\n')
    report['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report['feature_sha256'] = hashlib.sha256(x.tobytes()).hexdigest()
    report['artifact_sha256'] = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(out.iterdir())
                                  if f.name in ['config.json','split_manifest.json','predictions.csv','evaluation.png','model_card.md','development_logistic.joblib']}
    (out/'ml_report.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('outputs/ch16'))
    args = parser.parse_args()
    run(args.output_dir, json.loads(args.config.read_text()) if args.config else None)
