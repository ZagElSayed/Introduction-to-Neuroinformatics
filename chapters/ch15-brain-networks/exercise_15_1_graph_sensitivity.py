"""Chapter 15: deterministic synthetic graph threshold and common-source sensitivity."""
import argparse
import csv
import hashlib
import json
import math
from collections import deque
from pathlib import Path

NODES=("Frontal","Central","Parietal","Temporal","Occipital","Midline")

def matrix():
    n=len(NODES)
    return [[0.0 if i==j else round(0.12+0.71/(1+abs(i-j))+0.03*((i+j)%3),5)
             for j in range(n)] for i in range(n)]

def validate(a):
    n=len(a)
    if n<3 or any(len(row)!=n for row in a):
        raise ValueError("square matrix with at least 3 nodes required")
    for i in range(n):
        if abs(a[i][i])>1e-12:
            raise ValueError("diagonal must be zero")
        for j in range(n):
            if not math.isfinite(a[i][j]) or not 0<=a[i][j]<=1 or abs(a[i][j]-a[j][i])>1e-12:
                raise ValueError("weights must be finite, symmetric, and in [0,1]")

def threshold(a, density):
    validate(a)
    if not 0<density<=1:
        raise ValueError("density must be in (0,1]")
    n=len(a)
    edges=sorted(((a[i][j],i,j) for i in range(n) for j in range(i+1,n)),
                 key=lambda item:(-item[0],item[1],item[2]))
    count=max(1,round(density*len(edges)))
    graph=[[0]*n for _ in range(n)]
    for _,i,j in edges[:count]:
        graph[i][j]=graph[j][i]=1
    return graph

def distances(graph,source):
    n=len(graph)
    d=[-1]*n
    d[source]=0
    q=deque([source])
    while q:
        u=q.popleft()
        for v,edge in enumerate(graph[u]):
            if edge and d[v]<0:
                d[v]=d[u]+1
                q.append(v)
    return d

def metrics(a,g):
    n=len(g)
    degree=[sum(row) for row in g]
    strength=[sum(row) for row in a]
    clustering=[]
    for i in range(n):
        neighbors=[j for j in range(n) if g[i][j]]
        k=len(neighbors)
        triangles=sum(g[u][v] for p,u in enumerate(neighbors) for v in neighbors[p+1:])
        clustering.append(2*triangles/(k*(k-1)) if k>1 else 0.0)
    all_dist=[distances(g,i) for i in range(n)]
    efficiency=sum(1/d for i in range(n) for j,d in enumerate(all_dist[i]) if i!=j and d>0)/(n*(n-1))
    remaining=set(range(n))
    components=0
    while remaining:
        start=next(iter(remaining))
        reached={i for i,d in enumerate(all_dist[start]) if d>=0}
        remaining-=reached
        components+=1
    return {"density":sum(degree)/(n*(n-1)),"components":components,
            "mean_clustering":sum(clustering)/n,"global_efficiency":efficiency,
            "degree":degree,"strength":strength,"clustering":clustering}

def run(output_dir):
    out=Path(output_dir)
    out.mkdir(parents=True,exist_ok=True)
    original=matrix()
    # A synthetic shared-signal surrogate: increase weights among three nodes.
    confounded=[row[:] for row in original]
    for i in range(3):
        for j in range(i+1,3):
            confounded[i][j]=confounded[j][i]=min(1.0,original[i][j]+0.3)
    records=[]
    for name,a in (("baseline",original),("common_source_surrogate",confounded)):
        for density in (0.2,0.4,0.6):
            g=threshold(a,density)
            stats=metrics(a,g)
            records.append({"condition":name,"requested_density":density,
                            "actual_density":stats["density"],"components":stats["components"],
                            "mean_clustering":stats["mean_clustering"],
                            "global_efficiency":stats["global_efficiency"],
                            "hub_by_degree":NODES[max(range(len(NODES)),key=lambda i:stats["degree"][i])],
                            "degree":stats["degree"],"strength":stats["strength"]})
    with (out/"graph_sensitivity.csv").open("w",newline="",encoding="utf-8") as f:
        fields=("condition","requested_density","actual_density","components",
                "mean_clustering","global_efficiency","hub_by_degree","degree","strength")
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader()
        for row in records:
            w.writerow(row)
    report={"synthetic":True,"nodes":NODES,"original_matrix":original,
            "confounded_matrix":confounded,"results":records,
            "edge_definition":"invented symmetric weights, not measured neural connectivity",
            "confound":"artificially increased three-node weights; illustrative only",
            "interpretation_warning":"Graph changes cannot be interpreted as brain interactions or clinical biomarkers",
            "output_sha256":hashlib.sha256((out/"graph_sensitivity.csv").read_bytes()).hexdigest()}
    (out/"graph_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="outputs/ch15")
    args=p.parse_args()
    result=run(args.output_dir)
    print(json.dumps({"synthetic":result["synthetic"],"nodes":len(result["nodes"]),
                      "comparisons":len(result["results"]),"output_sha256":result["output_sha256"]},indent=2))

if __name__=="__main__":
    main()
