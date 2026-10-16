# Chapter 15 — Network and Graph-Theoretic Brain Models

Start with **[FIRST_STEPS.md](FIRST_STEPS.md)**. It explains the vocabulary and follows one small graph through the calculations in the book. CS, IT, medical, and neurology students complete the same computational work, with complementary interpretation questions.

## Two learning levels

- **Level 1:** a standard-library synthetic exercise. It teaches graph definitions, threshold sensitivity, ties, confounds, and reproducible outputs. No EEG download or third-party runtime package is needed for the exercise itself.
- **Level 2:** [REAL_NETWORK_PROTOCOL.md](REAL_NETWORK_PROTOCOL.md) describes the additional requirements for a real or instructor-provided connectivity matrix. It is a protocol, not a claim that the toy script estimates physiological connectivity.

The six-node weighted matrix and the added three-edge weight changes are invented. They are not measured EEG/MEG relationships, anatomical connections, or a biophysical simulation of volume conduction. Anatomical-sounding labels in the toy are placeholders, not a validated atlas. The separate numbered worked graph is the book's triangle-and-chain example; do not confuse it with the weighted baseline.

## Run locally from the repository root

```bash
python chapters/ch15-brain-networks/exercise_15_1_graph_sensitivity.py --output-dir outputs/ch15/run01
```

Use a new or empty directory. The script refuses to overwrite a populated run. It compares two illustrative conditions at three requested densities: 20%, 40%, and 60%. This yields six network comparisons and 36 node-level rows. It records `review_required` and `accepted: false`; numerical success does not grant scientific acceptance.

For local verification when pytest is installed:

```bash
python -m pytest -q tests/test_chapter15_lab.py
```

Tests are supplied for local execution. Runtime and test success must be confirmed on the local machine; no executed result is asserted here.

## What to inspect

| File | Contents and interpretation |
| --- | --- |
| `worked_example.json` | The book's numbered binary graph, hop distances, metrics, and hand-calculated reference fractions. |
| `graph_sensitivity.csv` | Six condition/density comparisons, all degree-hub ties, degree, full strength, and retained strength. List fields are JSON arrays inside CSV cells. |
| `node_metrics.csv` | One row per condition, density, and node index: degree, both strength definitions, clustering, and degree-hub membership. Match the zero-based index to the node order in the report. |
| `graph_derivatives.json` | Each full weighted matrix and binary adjacency, metrics, distances, and node order. Distances use `-1` for unreachable nodes. |
| `graph_report.json` | Configuration, software/code identity, run UUID/time, artifact hashes, limitations, and pending-review status. The report does not hash itself. |

The legacy `strength` field is **unthresholded weighted node strength**. `retained_strength` sums weights on the retained graph. The legacy singular `hub_by_degree` is the first listed member of a tie; `hubs_by_degree` lists every maximum-degree node. A maximum-degree node in this toy is not a clinical hub.

## Reproducibility conventions

The matrix is symmetric, finite, nonnegative, and has a zero diagonal. Density applies to unique undirected pairs. The script ranks pairs by descending weight, resolves ties by ascending pair indices, and retains `max(1, round(density * possible_pairs))` edges. Python rounding is nearest integer with half-to-even ties. Record realized density. Boundary ties can depend on node order.

Clustering is the average of local binary coefficients, including zeros for degree below two. Efficiency averages reciprocal **unweighted hop distances over all distinct pairs**; unreachable pairs contribute zero. It is not a weighted shortest-path calculation. Strength on the full matrix stays fixed across densities within a condition; retained strength can change.

Numerical artifacts can be compared between runs. Run IDs and timestamps intentionally change. Configuration and artifact hashes identify what was actually analyzed and saved.

## Assignment (100 points)

1. **Vocabulary and worked graph (20):** Explain nodes, edges, matrix rows, zeros versus missing values, and structural/functional/effective connectivity. Reproduce the numbered example's degrees, clustering at node 1, and distance from node 2 to node 6.
2. **Threshold sensitivity (20):** Compare requested/realized density, components, clustering, efficiency, and both strength definitions. Explain rounding and boundary ties.
3. **Hub stability (15):** Report every maximum-degree tie. Compare conditions and densities; explain why the rank is not a stable anatomical title.
4. **Confound reasoning (15):** Explain what the altered weights demonstrate and what they cannot simulate. Relate common input, reference, source leakage, and artifact QC to real connectivity.
5. **Inference and interpretation (15):** Propose a hypothesis-matched null, independent statistical unit, and multiplicity policy for a real study. Write a four-sentence finding with an explicit limitation.
6. **Reproducible handoff (15):** Submit the five outputs, a comparison table or plot, and a short interpretation. Explain review status, hashes, and how to preserve the original while revising a run.

**Medical/neurology track:** State what an observed metric would and would not support in a proposed clinical use. **CS/IT track:** State the data contract and how matrix semantics, graph representation, and algorithm choice affect the result. Both tracks do the calculations and execute the exercise locally.

## Limits

The script does not estimate correlation, coherence, imaginary coherency, tractography, directed influence, weighted shortest paths, communities, null distributions, cohort statistics, or biomarkers. It supports the beginner mechanics; the advanced protocol specifies the additional evidence and implementation needed for measured data.
