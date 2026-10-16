# Level 2 — Protocol for measured or instructor-provided networks

This is an advanced protocol, not an implemented connectivity estimator in the synthetic script. Use licensed, appropriately governed data and record installed software versions. No particular clinical marker or diagnostic cutoff is established by this assignment.

1. **State the question.** Define the intended use, comparison, independent statistical unit, primary metric or edge hypothesis, time/frequency interval, and what would count as a stable finding. Distinguish activation, functional dependence, and directed model-based influence.
2. **Identify the inputs.** Preserve participant/session IDs, preprocessing and source-model identity, reference/projections, channel exclusions, artifact/motion QC, sampling, available epochs/windows, and acquisition context. A reviewed source estimate does not automatically validate its connectivity.
3. **Define nodes.** Store atlas/version, node order and coverage, sensor versus source representation, parcel aggregation, orientation/sign conventions, and missing-parcel policy. Do not encode an absent parcel as a row of biological zeros. Match node identities across participants before comparing matrices.
4. **Specify the edge formula.** Record estimator, sign/direction convention, frequency/time definition, averaging units, rank/normalization where relevant, and uncertainty. For electrophysiology, declare common-source/leakage strategy and its limitations. Preserve unthresholded results and pair indices, including whether compact or triangular storage contains uncomputed entries.
5. **Check software semantics.** Distinguish coherency, magnitude, and magnitude-squared coherence. In MNE-Connectivity, consult the installed `spectral_connectivity_epochs` definition: `coh` uses coherency magnitude, while `cohy` retains the complex quantity. Do not transfer a magnitude-squared cutoff unchanged to a magnitude output. Epoch-level estimators require the repetitions and stationarity assumptions in their documentation; one unaveraged normalized Fourier product does not establish reliable coupling.
6. **Validate the matrix contract.** Check shape, node labels/order, finite/missing values, expected range, diagonal, symmetry when expected, and signedness. Directed matrices need a stated row/column direction. Preserve failed cases with reasons rather than silently symmetrizing, taking absolute values, or filling missing edges.
7. **Create graph derivatives.** Choose weighted versus binary and directed versus undirected representations. Specify absolute/proportional/statistical threshold, density rounding and boundary ties, negative-edge treatment, and component handling. Save full connectivity separately. Equal proportional density can retain edges of different reliability and can conceal a global weight-scale change.
8. **Compute defined metrics.** Keep strength and path cost separate. For positive weights, any strength-to-length transformation is an explicit modeling choice; signed or missing weights need different handling. Report whether strength uses the full or retained matrix, whether clustering is mean local clustering or transitivity, and how unreachable pairs enter efficiency. NetworkX `global_efficiency` ignores edge weights. Record metric normalization and all hub ties. If using communities, record algorithm, resolution, seed, and partition stability; keep display layouts separate from analysis topology.
9. **Test sensitivity and alternatives.** Compare justified thresholds, node definitions, estimators, and preprocessing choices. For a common-input demonstration using real time series, add or model a shared signal in a separate copied dataset and recompute the estimator; simply increasing matrix entries is only a graph surrogate. Assess reliability rather than assuming that a sharper map or larger metric is better. Dynamic windows share samples when overlapping and need an appropriate stationary/surrogate comparison.
10. **Match nulls and statistics to the claim.** Graph rewiring, time-series surrogates, and group-label permutations test different hypotheses. State what each null preserves. Respect participant, repeated-session, site, family, and paired-condition structure as appropriate. Define multiplicity across tested edges/bands/windows/metrics. NBS provides connected-component evidence under its procedure, not significance for every edge in that component. Train/test partitions must separate participants; fit data-driven feature, threshold, and nuisance choices inside training folds.
11. **Review and export.** Save node metadata, regional inputs or their identities, complete connectivity, graph derivatives, metrics, uncertainty/sensitivity results, configuration, software/code/input hashes, and the reviewer decision. Preserve pending, held/excluded, and accepted states. Changing only layout need not alter graph metrics; changing threshold rebuilds graphs/metrics; changing regional representation or estimator rebuilds dependent connectivity and graphs. New analysis choices require new run identities.
12. **Write the finding.** State nodes/edges, graph/metric, comparison/uncertainty, and the supported interpretation with alternatives. A group association does not supply a diagnostic threshold. Predictive performance, calibration, and added value for a declared clinical decision require separate validation.

## Minimum submission

- A machine-readable input and graph contract with node order and missingness policy.
- Full connectivity, each analyzed graph, metric definitions/results, and QC.
- A threshold/estimator sensitivity comparison and hypothesis-matched statistical plan.
- Provenance and review decision, including failed or non-comparable cases.
- A four-sentence interpretation and an explicit statement of the intended use and limitations.

## Primary reading

- [MNE-Connectivity spectral definitions and epoch assumptions](https://mne.tools/mne-connectivity/stable/generated/mne_connectivity.spectral_connectivity_epochs.html)
- [NetworkX global efficiency and ignored edge weights](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.efficiency_measures.global_efficiency.html)
- [NetworkX betweenness conventions](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html)
- [Rubinov and Sporns: graph measures and interpretation](https://doi.org/10.1016/j.neuroimage.2009.10.003)
- [Friston: functional and effective connectivity](https://doi.org/10.1089/brain.2011.0008)
- [Nolte and colleagues: imaginary coherency](https://doi.org/10.1016/j.clinph.2004.04.029)
- [Zalesky, Fornito, and Bullmore: NBS](https://doi.org/10.1016/j.neuroimage.2010.06.041)
- [Hindriks and colleagues: sliding-window inference](https://doi.org/10.1016/j.neuroimage.2015.11.055)
