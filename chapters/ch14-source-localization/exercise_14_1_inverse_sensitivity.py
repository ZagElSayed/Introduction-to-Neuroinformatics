"""Chapter 14: synthetic, small-dimensional source inverse sensitivity lab.

All values are dimensionless. This is not an anatomical EEG/MEG forward model.
No covariance estimation, physical coordinates, beamforming or clinical validation.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from datetime import datetime, timezone
import platform
import uuid

G = ((1.0, 0.4, 0.1), (0.2, 0.8, 0.4))
TRUE_SOURCE = (1.0, 0.0, 0.0)
ALTERED_G = ((0.85, 0.50, 0.15), (0.28, 0.72, 0.45))
NULL_VECTOR = (0.08, -0.38, 0.72)
VERSION = '2.0'

def finite(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)

def matrix(a):
    if not a or not a[0] or any(len(row) != len(a[0]) for row in a):
        raise ValueError('nonempty rectangular matrix required')
    if not all(finite(v) for row in a for v in row):
        raise ValueError('finite numeric matrix entries required')
    return len(a), len(a[0])

def vector(x, length):
    if len(x) != length or not all(finite(v) for v in x):
        raise ValueError('matching vector length and finite entries required')

def transpose(a):
    matrix(a)
    return list(map(list, zip(*a)))

def multiply(a, b):
    if matrix(a)[1] != matrix(b)[0]:
        raise ValueError('matrix dimensions do not match')
    return [[sum(x*y for x,y in zip(row,col)) for col in transpose(b)] for row in a]

def solve(a, b):
    # Small dense teaching solver, not a production numerical implementation.
    if matrix(a) != (len(b), len(b)):
        raise ValueError('square system and matching vector required')
    vector(b, len(b))
    n = len(b)
    scale = max(abs(v) for row in a for v in row)
    aug = [list(map(float, row)) + [float(b[i])] for i,row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col,n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) <= 1e-12*scale:
            raise ValueError("Singular matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        d = aug[col][col]
        aug[col] = [v/d for v in aug[col]]
        for r in range(n):
            if r != col:
                scale = aug[r][col]
                aug[r] = [v-scale*w for v,w in zip(aug[r],aug[col])]
    return [row[-1] for row in aug]

def inverse(g, y, lam):
    vector(y, matrix(g)[0])
    if not finite(lam) or lam <= 0:
        raise ValueError("Regularization must be finite and positive")
    # Objective: ||y-Gj||^2 + lam*||j||^2; identity noise/source weights.
    # This coefficient is not a universal substitute for MNE's lambda2.
    # Ridge/MNE-like estimate G^T (G G^T + lambda I)^-1 y
    gt = transpose(g)
    ggt = multiply(g,gt)
    a = [[ggt[i][j]+(lam if i==j else 0) for j in range(len(ggt))] for i in range(len(ggt))]
    z = solve(a,y)
    return [sum(gt[i][j]*z[j] for j in range(len(y))) for i in range(len(gt))]

def forward(g,j):
    vector(j, matrix(g)[1])
    return [sum(a*b for a,b in zip(row,j)) for row in g]

def inverse_operator(g, lam):
    m, _ = matrix(g)
    columns = [inverse(g, [float(i == k) for i in range(m)], lam) for k in range(m)]
    return transpose(columns)

def norm(x):
    return math.sqrt(sum(v*v for v in x))

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_csv(path, rows):
    with path.open('x', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

def plot_diagnostics(path, results, resolution):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650">',
             '<rect width="1200" height="650" fill="white"/><g font-family="sans-serif" fill="#142D4E">',
             '<text x="45" y="40" font-size="25">Sensor fit does not guarantee the true source vector</text>',
             '<text x="45" y="76" font-size="18">Dimensionless teaching model; nominal lead field and noiseless observations</text>',
             '<text x="65" y="125" font-size="22">Source amplitudes</text>',
             '<text x="695" y="125" font-size="22">Resolution R = K G, lambda = 0.1</text>']
    for level in (-.25, 0, .5, 1):
        y = 440-260*level
        parts.append(f'<path d="M75 {y} H555" stroke="#CDD8E5"/><text x="20" y="{y+5}" font-size="16">{level:g}</text>')
    curves = [('Known truth', TRUE_SOURCE, '#142D4E')]
    selected = [r for r in results if r['data_case'] == 'noiseless' and r['model'] == 'nominal']
    for row, color in zip(selected, ('#167D91', '#7556A8', '#D87C36')):
        curves.append((f"lambda = {row['lambda']:g}", [row[f'source_{i}'] for i in (1, 2, 3)], color))
    for k, (label, values, color) in enumerate(curves):
        points = ' '.join(f'{115+i*195},{440-260*v:.2f}' for i, v in enumerate(values))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for i, value in enumerate(values):
            parts.append(f'<circle cx="{115+i*195}" cy="{440-260*value:.2f}" r="4" fill="{color}"/>')
        parts.append(f'<text x="{65+(k%2)*260}" y="{565+(k//2)*30}" font-size="18" fill="{color}">{label}</text>')
    for i in range(3):
        parts.append(f'<text x="{88+i*195}" y="535" font-size="17">S{i+1}</text>')
    for i, row in enumerate(resolution):
        for j, value in enumerate(row):
            intensity = min(1, abs(value))
            target = (22, 125, 145) if value >= 0 else (214, 84, 115)
            color = '#%02x%02x%02x' % tuple(round(255*(1-intensity)+v*intensity) for v in target)
            parts.append(f'<rect x="{740+110*j}" y="{180+110*i}" width="110" height="110" fill="{color}" stroke="#CDD8E5"/>')
            parts.append(f'<text x="{769+110*j}" y="{241+110*i}" font-size="22">{value:.3f}</text>')
    for i in range(3):
        parts.append(f'<text x="{780+110*i}" y="167" font-size="19">S{i+1}</text><text x="695" y="{244+110*i}" font-size="19">S{i+1}</text>')
    parts.extend(['<text x="695" y="550" font-size="18">Columns: spread from each true source.</text>',
                  '<text x="695" y="580" font-size="18">Rows: contributions to each estimate.</text>',
                  '<text x="695" y="610" font-size="18">Signed coefficients; not probabilities.</text>', '</g></svg>'])
    path.write_text(''.join(parts), encoding='utf-8')

def run(output_dir):
    root = Path(output_dir)
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise FileExistsError('use a new or empty directory; earlier runs are preserved')
    y = forward(G, TRUE_SOURCE)
    alternate = [a+b for a, b in zip(TRUE_SOURCE, NULL_VECTOR)]
    alternate_y = forward(G, alternate)
    noise = (0.02, -0.01)  # Fixed perturbation, not sampled stochastic noise.
    config = {'units': 'dimensionless', 'nominal_gain': G, 'altered_gain': ALTERED_G,
              'true_source': TRUE_SOURCE, 'null_vector': NULL_VECTOR,
              'fixed_sensor_perturbation': noise, 'lambdas': [0.01, 0.1, 1.0],
              'objective': 'squared sensor residual + lambda * squared source L2 norm',
              'noise_weighting': 'identity; covariance is not estimated',
              'source_weighting': 'identity; no orientation or depth model'}
    results, matrices = [], []
    for name, g in (('nominal', G), ('perturbed_lead_field', ALTERED_G)):
        for lam in config['lambdas']:
            operator = inverse_operator(g, lam)
            matrices.append({'model': name, 'lambda': lam, 'inverse_operator': operator,
                             'assumed_resolution': multiply(operator, g),
                             'effective_resolution_under_true_gain': multiply(operator, G)})
            for case, observed in (('noiseless', y), ('fixed_sensor_perturbation', [a+b for a, b in zip(y, noise)])):
                estimate = inverse(g, observed, lam)
                residual = norm([a-b for a, b in zip(forward(g, estimate), observed)])
                results.append({'model': name, 'data_case': case, 'lambda': lam,
                                **{f'source_{i+1}': v for i, v in enumerate(estimate)},
                                'residual_l2': residual, 'relative_sensor_residual': residual/norm(observed),
                                'source_error_l2': norm([a-b for a, b in zip(estimate, TRUE_SOURCE)]),
                                'source_norm_l2': norm(estimate),
                                'peak_source_index': 1+max(range(3), key=lambda i: abs(estimate[i]))})
    root.mkdir(parents=True, exist_ok=True)
    write_csv(root/'inverse_sensitivity.csv', results)
    write_csv(root/'nonunique_sources.csv', [
        {'source_vector': name, **{f'source_{i+1}': v for i, v in enumerate(j)},
         'sensor_1': sensors[0], 'sensor_2': sensors[1]}
        for name, j, sensors in (('truth', TRUE_SOURCE, y), ('truth_plus_null', alternate, alternate_y))])
    (root/'resolution_matrices.json').write_text(json.dumps(matrices, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    nominal_r = next(r['assumed_resolution'] for r in matrices if r['model'] == 'nominal' and r['lambda'] == .1)
    plot_diagnostics(root/'inverse_diagnostics.svg', results, nominal_r)
    artifacts = ['inverse_sensitivity.csv', 'nonunique_sources.csv', 'resolution_matrices.json', 'inverse_diagnostics.svg']
    report = {'pipeline_version': VERSION, 'synthetic': True, 'lead_field_shape': [2, 3],
              'rank_limit': 'at most 2; 3 source amplitudes; nominal row rank is 2',
              'run_id': str(uuid.uuid4()), 'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'python_version': platform.python_version(), 'script_sha256': digest(__file__),
              'configuration': config,
              'configuration_sha256': hashlib.sha256(json.dumps(config, sort_keys=True, separators=(',', ':')).encode()).hexdigest(),
              'observed_sensors': y, 'true_source': TRUE_SOURCE, 'alternate_source': alternate,
              'nonuniqueness_sensor_difference_l2': norm([a-b for a, b in zip(y, alternate_y)]),
              'method': 'L2 Tikhonov/ridge, dual solution', 'results': results,
              'review_status': 'review_required', 'accepted_as_neurally_valid': False,
              'model_perturbation': 'illustrative gain change; no physical coordinate displacement',
              'artifacts_sha256': {name: digest(root/name) for name in artifacts},
              'warning': 'Truth-based source error and effective resolution require known simulated truth; a fixed perturbation gives no confidence interval, population inference or clinical validation'}
    (root/'source_inverse_report.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="outputs/ch14/run01")
    args=p.parse_args()
    print(json.dumps(run(args.output_dir),indent=2,allow_nan=False))

if __name__=="__main__":
    main()

