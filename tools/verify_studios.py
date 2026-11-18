"""Author verification of later companion notebooks in isolated Python processes.

This executes code cells, not a Jupyter kernel or browser. Installation cells are
reported as skipped. Default freeze gates must stop as designed. --frozen adds
separate runs with the supplied default configuration explicitly frozen; no
parameters are selected from final outcomes. --torch adds the optional CPU toy.
An external model service is never enabled. All notebook/helper bytes remain
unchanged. Requires the packages specified by the selected notebooks.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout, redirect_stderr
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
LATER = (19, 20, 21, 22, 23, 24, 25, 26, 27, 28)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def child(task):
    notebook = Path(task['notebook'])
    chapter = next(p for p in notebook.parents if p.parent.name == 'chapters')
    report = {'notebook': str(notebook.relative_to(ROOT)), 'mode': task['mode'],
              'notebook_sha256': digest(notebook), 'executed_code_cells': [],
              'skipped_install_cells': [], 'status': 'failed'}
    started = time.perf_counter()
    try:
        with tempfile.TemporaryDirectory(prefix='neuro-studio-review-') as td:
            dest = Path(td)/chapter.name
            shutil.copytree(chapter, dest, ignore=shutil.ignore_patterns('__pycache__','outputs','*_outputs','bci_data'))
            working = dest/notebook.relative_to(chapter).parent
            os.chdir(working)
            sys.path[:0] = [str(working), str(dest)]
            # These notebooks intentionally require an exact pinned local helper.
            if chapter.name.startswith('ch22'):
                pin = working/'ch22_baseline'; pin.mkdir(exist_ok=True)
                shutil.copy2(dest/'edge_timing.py', pin/'edge_timing.py')
            if chapter.name.startswith('ch20'):
                if not task.get('data_cache'):
                    raise RuntimeError('Chapter 20 requires --data-cache for its actual public EDF files')
                (working/'bci_data').symlink_to(Path(task['data_cache']).resolve(), target_is_directory=True)
            import matplotlib
            matplotlib.use('Agg')
            from IPython.display import display
            namespace = {'__name__':'__main__', 'display':display}
            cells = json.loads(notebook.read_text())['cells']
            report['helper_sha256'] = {str(p.relative_to(dest)):digest(p) for p in sorted(dest.rglob('*.py'))}
            with Path(task['console']).open('w') as output, redirect_stdout(output), redirect_stderr(output):
                for index, cell in enumerate(cells):
                    if cell['cell_type'] != 'code':
                        continue
                    source = ''.join(cell['source'])
                    if source.lstrip().startswith('%pip'):
                        report['skipped_install_cells'].append(index)
                        continue
                    if task['mode'] == 'frozen':
                        source = source.replace('FROZEN = False', 'FROZEN = True')
                    if task['mode'] == 'torch':
                        source = source.replace('RUN_TORCH = False', 'RUN_TORCH = True')
                    try:
                        exec(compile(source, f'{notebook.name}:cell-{index}', 'exec'), namespace)
                    except RuntimeError as exc:
                        if task.get('expect_freeze_gate') and str(exc).startswith(('Freeze the configuration','Document and freeze')):
                            report['status'] = 'expected_freeze_gate'
                            report['gate_cell'] = index
                            report['gate_reason'] = str(exc)
                            break
                        raise
                    report['executed_code_cells'].append(index)
                else:
                    report['status'] = 'passed'
                # Preserve small interpretable outcomes, not every simulator row.
                summaries = {}
                for name in ('run','fixed','adaptive','faulted','nominal','fifo','latest','faults','clean'):
                    value = namespace.get(name)
                    if isinstance(value,dict):
                        if isinstance(value.get('summary'),dict):summaries[name] = value['summary']
                        elif 'status' in value:summaries[name] = {k:value[k] for k in ('status','reason') if k in value}
                for name in ('offline_test','validation','evaluation','utility_comparison','audit_result'):
                    value = namespace.get(name)
                    if isinstance(value,dict):summaries[name] = value
                if isinstance(namespace.get('experiment'),dict):
                    summaries['bci_manifest'] = namespace['experiment']['manifest']
                if isinstance(namespace.get('neural_report'),dict):
                    summaries['neural_report'] = namespace['neural_report']
                if chapter.name.startswith('ch23') and isinstance(namespace.get('report'),dict):
                    summaries['event_ledger'] = namespace['report']
                rows = namespace.get('rows')
                if chapter.name.startswith('ch19') and isinstance(rows,list):
                    summaries['expected_case_matches'] = all(r.get('matches_expected',False) for r in rows)
                    assert summaries['expected_case_matches'], 'Agent fixture outcome mismatch'
                report['observations'] = summaries
            assert digest(notebook) == report['notebook_sha256'], 'Original notebook bytes changed'
    except Exception as exc:
        report['status'] = 'failed'
        report['error'] = f'{type(exc).__name__}: {exc}'
        report['traceback'] = traceback.format_exc()
    report['elapsed_seconds'] = time.perf_counter()-started
    versions = {}
    for package in ('numpy','scipy','mne','scikit-learn','matplotlib','torch','ipython'):
        try:versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:pass
    report['versions'] = versions
    Path(task['result']).write_text(json.dumps(report,indent=2,default=str))
    return 0 if report['status'] in ('passed','expected_freeze_gate') else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--data-cache',type=Path)
    parser.add_argument('--real-data',action='store_true')
    parser.add_argument('--chapters',type=int,nargs='+',choices=LATER,default=list(LATER))
    parser.add_argument('--frozen',action='store_true')
    parser.add_argument('--torch',action='store_true')
    parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--timeout',type=int,default=180)
    args = parser.parse_args()
    out = args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    tasks = []
    for number in args.chapters:
        if number == 20 and not args.real_data:continue
        for folder in sorted((ROOT/'chapters').glob(f'ch{number:02}-*')):
            for nb in sorted(folder.rglob('*.ipynb')):
                modes = ['default']
                if args.frozen and ((number==20 and nb.name.startswith('03_')) or number==21):modes.append('frozen')
                if args.torch and number==27:modes.append('torch')
                for mode in modes:
                    name = f'ch{number:02}-{nb.stem}-{mode}'
                    tasks.append({'notebook':str(nb.resolve()),'mode':mode,
                                  'expect_freeze_gate':mode == 'default' and (number == 21 or (number == 20 and nb.name.startswith('03_'))),
                                  'console':str(out/(name+'.log')),'result':str(out/(name+'.json')),
                                  'data_cache':str(args.data_cache.resolve()) if args.data_cache else None})
    env = os.environ.copy();env.update({'MPLBACKEND':'Agg','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','CUDA_VISIBLE_DEVICES':''})
    def run(task):
        try:
            result = subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child',json.dumps(task)],env=env,
                                    stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=args.timeout)
            path = Path(task['result'])
            if path.is_file():return json.loads(path.read_text())
            return {'notebook':task['notebook'],'mode':task['mode'],'status':'failed','error':result.stdout[-2000:]}
        except subprocess.TimeoutExpired:
            return {'notebook':task['notebook'],'mode':task['mode'],'status':'failed','error':'Review timeout'}
    reports = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for report in pool.map(run,tasks):
            reports.append(report)
            print(report['notebook'],report['mode'],report['status'],report.get('error',''),flush=True)
    (out/'summary.json').write_text(json.dumps(reports,indent=2,default=str))
    return int(any(r['status']=='failed' for r in reports))


if __name__ == '__main__':
    if len(sys.argv)>2 and sys.argv[1]=='--child':raise SystemExit(child(json.loads(sys.argv[2])))
    raise SystemExit(main())
