"""Chapter 15: deterministic synthetic graph threshold and common-source sensitivity."""
import argparse
import csv
import hashlib
import json
import math
import platform
import uuid
from datetime import datetime, timezone
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
    if not math.isfinite(density) or not 0<density<=1:
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

def validate_graph(g):
    n=len(g)
    if n<3 or any(len(row)!=n for row in g):
        raise ValueError("binary graph must be square with at least 3 nodes")
    for i in range(n):
        if g[i][i]!=0:
            raise ValueError("graph self-loops are excluded")
        for j in range(n):
            if g[i][j] not in (0,1) or g[i][j]!=g[j][i]:
                raise ValueError("graph must be binary and symmetric")


def metrics(a,g):
    validate(a)
    validate_graph(g)
    if len(a)!=len(g):
        raise ValueError("matrix and graph node counts must agree")
    n=len(g)
    degree=[sum(row) for row in g]
    strength=[sum(row) for row in a]
    retained_strength=[sum(a[i][j]*g[i][j] for j in range(n)) for i in range(n)]
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
            "degree":degree,"strength":strength,"retained_strength":retained_strength,
            "clustering":clustering,"distances":all_dist,
            "edge_count":sum(degree)//2,
            "hubs_by_degree":[i for i,k in enumerate(degree) if k==max(degree)]}

def worked_example():
    """The binary graph in the chapter; not the invented weighted baseline."""
    graph=[[0]*6 for _ in range(6)]
    edges=((0,1),(0,2),(0,3),(1,2),(3,4),(4,5))
    for i,j in edges:
        graph[i][j]=graph[j][i]=1
    return {"node_ids":[1,2,3,4,5,6],
            "edges_one_based":[[i+1,j+1] for i,j in edges],
            "adjacency":graph,"metrics":metrics(graph,graph),
            "expected_by_hand":{"degree":[3,2,2,2,2,1],"density":0.4,
                                "mean_clustering_fraction":"7/18",
                                "global_efficiency_fraction":"19/30"},
            "distance_convention":"-1 denotes unreachable; zero only for self distance"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def run(output_dir):
    out=Path(output_dir)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise FileExistsError("Use a new or empty output directory; earlier runs are preserved")
    original=matrix()
    confounded=[row[:] for row in original]
    # Deliberately altered weights, not estimated connectivity or a physical mixing model.
    for i in range(3):
        for j in range(i+1,3):
            confounded[i][j]=confounded[j][i]=min(1.0,original[i][j]+0.3)
    records=[]
    node_rows=[]
    derivatives=[]
    for name,a in (("baseline",original),("common_source_surrogate",confounded)):
        for density in (0.2,0.4,0.6):
            g=threshold(a,density)
            stats=metrics(a,g)
            hubs=[NODES[i] for i in stats["hubs_by_degree"]]
            records.append({"condition":name,"requested_density":density,
                            "actual_density":stats["density"],"edge_count":stats["edge_count"],
                            "components":stats["components"],
                            "mean_clustering":stats["mean_clustering"],
                            "global_efficiency":stats["global_efficiency"],
                            "hub_by_degree":hubs[0],"hubs_by_degree":hubs,
                            "degree":stats["degree"],"strength":stats["strength"],
                            "retained_strength":stats["retained_strength"]})
            for i,node in enumerate(NODES):
                node_rows.append({"condition":name,"requested_density":density,
                                  "actual_density":stats["density"],"node_id":node,
                                  "degree":stats["degree"][i],
                                  "full_weighted_strength":stats["strength"][i],
                                  "retained_weighted_strength":stats["retained_strength"][i],
                                  "clustering":stats["clustering"][i],
                                  "is_degree_hub":node in hubs})
            derivatives.append({"condition":name,"requested_density":density,
                                "node_ids":NODES,"weighted_matrix":a,
                                "binary_adjacency":g,"metrics":stats})
    out.mkdir(parents=True,exist_ok=True)
    for name,rows in (("graph_sensitivity.csv",records),("node_metrics.csv",node_rows)):
        with (out/name).open("w",newline="",encoding="utf-8") as f:
            writer=csv.DictWriter(f,fieldnames=list(rows[0]))
            writer.writeheader()
            for row in rows:
                writer.writerow({k:json.dumps(v) if isinstance(v,list) else v for k,v in row.items()})
    write_json(out/"graph_derivatives.json",derivatives)
    write_json(out/"worked_example.json",worked_example())
    configuration={"requested_densities":[0.2,0.4,0.6],
                   "threshold_rule":"descending weight; ties by ascending pair indices",
                   "edge_count_rule":"max(1, round(density * possible_edges)); round is half-to-even",
                   "node_order":NODES,"diagonal":"zero; no self-loops",
                   "graph_type":"simple undirected binary graph after thresholding",
                   "weights":"invented nonnegative symmetric values in [0,1]",
                   "distance":"unweighted hop count; unreachable pairs contribute zero efficiency",
                   "clustering":"mean of local coefficients; include zero for degree below two",
                   "strength":"full matrix, before thresholding",
                   "retained_strength":"weighted sum over the thresholded edge set",
                   "hub_ties":"report all; legacy hub_by_degree is first-listed only"}
    config_bytes=json.dumps(configuration,sort_keys=True,separators=(",",":")).encode()
    report={"schema_version":2,"synthetic":True,"run_id":str(uuid.uuid4()),
            "created_utc":datetime.now(timezone.utc).isoformat(),
            "software":{"python":platform.python_version(),"script_sha256":digest(__file__)},
            "configuration":configuration,"configuration_sha256":hashlib.sha256(config_bytes).hexdigest(),
            "nodes":NODES,"original_matrix":original,"confounded_matrix":confounded,"results":records,
            "edge_definition":"invented symmetric weights, not measured neural connectivity",
            "confound":"artificially increased three-node weights; illustrative only",
            "interpretation_warning":"Graph changes cannot establish brain interactions or clinical biomarkers",
            "review_status":"review_required","accepted":False,
            "qc":{"finite_symmetric_weights":True,"zero_diagonal":True,
                  "limitations":["No measured signals or real atlas","No cohort or inferential statistics",
                                 "No community detection or weighted shortest paths"]},
            "artifacts_sha256":{name:digest(out/name) for name in
                                ("graph_sensitivity.csv","node_metrics.csv", "graph_derivatives.json","worked_example.json")},
            "output_sha256":digest(out/"graph_sensitivity.csv")}
    write_json(out/"graph_report.json",report)
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

