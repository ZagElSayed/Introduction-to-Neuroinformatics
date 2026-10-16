# First steps: read, calculate, explain

A brain graph is a representation of specified evidence. It is not a photograph of wiring and is not the same thing as an artificial neural network.

| Word | First explanation | Question to ask |
| --- | --- | --- |
| Signal | Measurements varying over time | Which recording, units, reference, and quality controls? |
| Node | One defined unit, such as a sensor or region | Which atlas/label, order, coverage, and aggregation? |
| Edge | A relationship estimated between two units | Anatomical evidence, dependence, or model-based influence? |
| Weight | The number assigned to an edge | What formula, sign, scale, and uncertainty? |
| Adjacency matrix | A table of relationships indexed by node | Which labels correspond to its rows and columns? |
| Metric | A summary of the constructed graph | Which definition and graph type? |

Activation, dependence between signals, and topology of the resulting network are different questions. Two regions responding to one event can be dependent without directly driving one another. A negative correlation is not evidence of an inhibitory synapse.

## 1. Draw this small graph

There are six numbered nodes. Join these pairs:

`(1,2), (1,3), (1,4), (2,3), (4,5), (5,6)`.

Nodes 1, 2, and 3 form a triangle. A chain continues from 1 through 4 and 5 to 6. The numbers are teaching labels, not anatomical locations.

The adjacency rows, in node order 1 through 6, are:

| Node | Row |
| --- | --- |
| 1 | `0 1 1 1 0 0` |
| 2 | `1 0 1 0 0 0` |
| 3 | `1 1 0 0 0 0` |
| 4 | `1 0 0 0 1 0` |
| 5 | `0 0 0 1 0 1` |
| 6 | `0 0 0 0 1 0` |

Read one row aloud. Symmetry means each edge appears twice in the array, but remains one undirected edge. The diagonal is zero because this graph excludes self-loops. An absent retained edge is not the same as a failed or uncomputed measurement.

## 2. Count degree and density

The row sums are **3, 2, 2, 2, 2, 1**. Their sum is 12, so there are six unique edges. Six nodes have 15 possible undirected pairs. Density is therefore `6/15 = 0.4`.

If node 1's three retained weights were 0.8, 0.6, and 0.2, its degree would remain 3 and retained strength would be 1.6. Original full-matrix strength can include weak edges later discarded by a threshold. Neither strength is signal amplitude or power.

## 3. Count clustering

Node 1 has neighbors 2, 3, and 4. Their three possible pairs are 2–3, 2–4, and 3–4. Only the first pair has an edge, so clustering is **1/3**. Nodes 2 and 3 each have clustering 1. Nodes 4, 5, and 6 have clustering 0 under the convention that degree below two gives zero.

The mean is `(1/3 + 1 + 1)/6 = 7/18`, approximately 0.389. This is mean local clustering. Transitivity weights the triplets differently and is 3/7 in this graph; do not interchange the names or formulas.

## 4. Walk paths and interpret efficiency

A shortest route from 2 to 6 is `2 → 1 → 4 → 5 → 6`: four hops, contributing 1/4 to the reciprocal-distance average. Across all pairs, binary global efficiency is **19/30**, approximately 0.633. It describes graph routes, not measured transmission speed through axons.

Remove edge 4–5 on your drawing. Nodes 5 and 6 are now disconnected from the others. Unreachable pairs contribute zero to efficiency and stay in the denominator. Dropping them answers a different question.

For positive weighted edges, a declared strength-to-length rule may give different routes than hop count. This lab deliberately uses binary hop count; it does not implement weighted path lengths.

## 5. Compare two meanings of hub

Node 1 has the largest degree, 3. Node 4 has degree 2, but lies on all six shortest routes between `{1,2,3}` and `{5,6}`. Its undirected normalized betweenness is `6/10 = 0.6`. Node 1 also has betweenness 0.6. There is a tie under that metric, even though their degrees differ.

The script reports degree-hub ties. It does not calculate betweenness; the example above is a hand calculation to distinguish definitions.

## 6. Run and inspect the teaching outputs

Follow the command in the README. Open `worked_example.json` first; it corresponds to the numbered graph above. The sensitivity experiment uses a **different**, invented weighted baseline with placeholder names and two conditions. Do not expect its degrees to equal the worked graph at every density.

Then inspect one row in `graph_sensitivity.csv` and its full array in `graph_derivatives.json`. Match the node indices to `graph_report.json`. Use `node_metrics.csv` to compare full versus retained strength. List every highest-degree tie rather than choosing the first name as a uniquely important region.

## 7. Explain a threshold before using it

An absolute threshold retains weights above a stated value; density may differ between people. A proportional threshold retains a stated fraction of pairs; their weight scale may differ between people. Neither choice solves edge uncertainty.

In six nodes, a requested 25% means 3.75 edges. With the lab's rounding rule, four edges would give realized density 4/15, approximately 0.267. The default experiment uses 20%, 40%, and 60%. Equal-weight boundaries use node-index order, so they require sensitivity review.

## 8. Interpret a finding in four sentences

1. Define the measurement, nodes, and edge formula.
2. State the graph construction and metric.
3. Report the comparison and sensitivity to reasonable alternatives.
4. State what cannot be concluded.

A fictional report might say: “We compared a declared alpha-band dependence estimate between regional source signals. We computed degree over predeclared densities. The frontal ranking changed after artifact review. This does not establish a disease-specific hub.”

For a medical or neurology perspective, ask whether a stable group finding would help a stated decision in a new patient. For a CS/IT perspective, ask whether the same inputs and configuration reproduce the result. Both questions matter.

## Self-check answers

- Does a functional edge prove a direct anatomical connection? **No.**
- Are ten windows from each of 20 people equivalent to 200 independent participants? **No.**
- Can a network change when only the threshold changes? **Yes.**
- Can graph visualization prove causality? **No.**
- Why keep the matrix, labels, and configuration? **They define what the graph and its metrics actually mean.**

Continue to `REAL_NETWORK_PROTOCOL.md` only after explaining these ideas and completing the local exercise.
