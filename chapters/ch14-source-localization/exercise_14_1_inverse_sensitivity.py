"""Chapter 14: synthetic, small-dimensional source inverse sensitivity lab.

This is linear algebra teaching data, not a realistic anatomical EEG/MEG forward model.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

G = ((1.0, 0.4, 0.1), (0.2, 0.8, 0.4))
TRUE_SOURCE = (1.0, 0.0, 0.0)

def transpose(a):
    return list(map(list, zip(*a)))

def multiply(a, b):
    return [[sum(x*y for x,y in zip(row,col)) for col in transpose(b)] for row in a]

def solve(a, b):
    n = len(b)
    aug = [list(map(float, row)) + [float(b[i])] for i,row in enumerate(a)]
    for col in range(n):
        pivot = max(range(col,n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-12:
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
    if lam <= 0:
        raise ValueError("Regularization must be positive")
    # Ridge/MNE-like estimate G^T (G G^T + lambda I)^-1 y
    gt = transpose(g)
    ggt = multiply(g,gt)
    a = [[ggt[i][j]+(lam if i==j else 0) for j in range(len(ggt))] for i in range(len(ggt))]
    z = solve(a,y)
    return [sum(gt[i][j]*z[j] for j in range(len(y))) for i in range(len(gt))]

def forward(g,j):
    return [sum(a*b for a,b in zip(row,j)) for row in g]

def run(output_dir):
    root=Path(output_dir)
    root.mkdir(parents=True,exist_ok=True)
    y=forward(G,TRUE_SOURCE)
    # An intentionally perturbed gain matrix is a numerical model-error surrogate,
    # not a geometrically calibrated 5-mm coregistration error.
    altered=((0.85,0.50,0.15),(0.28,0.72,0.45))
    results=[]
    for model_name,g in (("nominal",G),("perturbed_lead_field",altered)):
        for lam in (0.01,0.1,1.0):
            j=inverse(g,y,lam)
            predicted=forward(g,j)
            residual=math.sqrt(sum((a-b)**2 for a,b in zip(predicted,y)))
            results.append({"model":model_name,"lambda":lam,
                            "source_1":j[0],"source_2":j[1],"source_3":j[2],
                            "residual_l2":residual,"peak_source_index":1+max(range(3),key=lambda i:abs(j[i]))})
    with (root/"inverse_sensitivity.csv").open("w",newline="",encoding="utf-8") as stream:
        w=csv.DictWriter(stream,fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)
    report={"synthetic":True,"lead_field_shape":[2,3],
            "rank_limit":"at most 2; 3 unknown source amplitudes",
            "observed_sensors":y,"true_source":TRUE_SOURCE,
            "method":"L2 Tikhonov/ridge, dual solution",
            "model_perturbation":"illustrative gain-matrix change; not physical coordinate displacement",
            "results":results,
            "warning":"Small residual does not establish anatomical accuracy or unique source recovery"}
    manifest=root/"source_inverse_report.json"
    manifest.write_text(json.dumps(report,indent=2),encoding="utf-8")
    report["output_sha256"]=hashlib.sha256((root/"inverse_sensitivity.csv").read_bytes()).hexdigest()
    manifest.write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="outputs/ch14")
    args=p.parse_args()
    print(json.dumps(run(args.output_dir),indent=2))

if __name__=="__main__":
    main()
