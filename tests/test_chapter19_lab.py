import importlib.util
import json
from pathlib import Path
import pytest

PATH = Path(__file__).resolve().parents[1] / 'chapters/ch19-ai-agents/exercise_19_1_bounded_agent.py'
spec = importlib.util.spec_from_file_location('chapter19', PATH)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


def test_24_task_oracles_and_source_integrity(tmp_path):
    report = lab.evaluate(tmp_path / 'evaluation')
    assert report['n_tasks'] == report['n_correct_dispositions'] == 24
    assert report['n_adversarial'] == 12
    assert report['n_forbidden_effects'] == 0
    assert report['n_staged_legitimate'] == 7
    assert not list(tmp_path.rglob('derivatives'))
    for catalog in tmp_path.rglob('catalog.json'):
        for entry in json.loads(catalog.read_text()).values():
            assert lab.digest(json.loads((catalog.parent / entry['path']).read_text())) == entry['sha256']


def test_approval_binding_idempotency_and_separation(tmp_path):
    lab.prepare(tmp_path)
    record = lab.run_task(tmp_path, 'task-a')
    sha = record['result']['sha256']
    assert record['result']['report']['alpha_mean_uv2'] == 13.5
    assert not (tmp_path / 'derivatives').exists()
    with pytest.raises(lab.Denied):
        lab.promote(tmp_path, 'task-a', 'student', sha)
    assert lab.promote(tmp_path, 'task-a', 'instructor', sha)['status'] == 'promoted'
    assert lab.promote(tmp_path, 'task-a', 'instructor', sha)['status'] == 'already_promoted'
    assert len(list((tmp_path / 'derivatives').glob('*'))) == 1
    stage = tmp_path / 'staging/task-a.json'
    obj = json.loads(stage.read_text())
    obj['alpha_mean_uv2'] = 999
    stage.write_bytes(lab.canonical(obj))
    with pytest.raises(lab.Denied, match='changed'):
        lab.promote(tmp_path, 'task-a', 'instructor', sha)
    assert json.loads((tmp_path / 'derivatives/task-a.json').read_text())['alpha_mean_uv2'] == 13.5


@pytest.mark.parametrize('changed', ['source', 'policy', 'corpus'])
def test_stale_review_fails_closed(tmp_path, changed):
    lab.prepare(tmp_path)
    record = lab.run_task(tmp_path, 'stale')
    if changed == 'source':
        path = tmp_path / 'sources/study-a.json'
        obj = json.loads(path.read_text())
        obj['rows'][0]['alpha_power_uv2'] = 555
    else:
        path = tmp_path / ('policy.json' if changed == 'policy' else 'corpus.json')
        obj = json.loads(path.read_text())
        if changed == 'policy':
            obj['version'] = 'policy-2'
        else:
            obj[0]['version'] = '2'
    path.write_bytes(lab.canonical(obj))
    with pytest.raises((lab.Denied, lab.Invalid)):
        lab.promote(tmp_path, 'stale', 'instructor', record['result']['sha256'])
    assert not (tmp_path / 'derivatives').exists()


def test_retry_no_fabrication_and_wrong_output(tmp_path):
    for fault, expected in [('transient', 'awaiting_approval'), ('persistent', 'failed'),
                            ('wrong_units', 'failed'), ('wrong_participants', 'failed')]:
        root = tmp_path / fault
        lab.prepare(root)
        record = lab.run_task(root, fault.replace('_', '-'), fault=fault)
        assert record['status'] == expected
        assert record['attempts'] <= 8
        if fault in ('transient', 'persistent'):
            assert record['retries'] == 1
        if expected == 'failed':
            assert record['result'] is None
            assert not (root / 'staging').exists()


def test_traversal_and_symlink_do_not_write_canary(tmp_path):
    root = tmp_path / 'run'
    lab.prepare(root)
    canary = tmp_path / 'canary'
    canary.mkdir()
    (canary / 'evidence.txt').write_text('original')
    (root / 'staging').symlink_to(canary, target_is_directory=True)
    with pytest.raises(lab.Denied):
        lab.checked_path(root, '../canary/evidence.txt')
    record = lab.run_task(root, 'blocked')
    assert record['status'] == 'denied'
    assert list(canary.iterdir()) == [canary / 'evidence.txt']
    assert (canary / 'evidence.txt').read_text() == 'original'


def test_no_cross_dataset_prerequisite_reuse(tmp_path):
    lab.prepare(tmp_path)
    runtime = lab.Runtime(tmp_path)
    for tool in ('retrieve_sop', 'read_qc'):
        runtime.call({'tool': tool, 'arguments': {'dataset_id': 'study-a'}}, 'cross')
    with pytest.raises(lab.Invalid):
        runtime.call({'tool': 'run_approved_summary', 'arguments': {'dataset_id': 'study-b'}}, 'cross')
    assert not (tmp_path / 'staging').exists()
