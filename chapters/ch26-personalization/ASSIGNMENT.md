# Assignment: Can another reader reconstruct the personalization claim?

Submit your executed notebook, an annotated study contract, the exported bundle, and a 1,200–1,800 word interpretation. Preserve the default run, label any additional seed runs, and report your own results. Never describe a synthetic observation as patient evidence. Total: 100 points.

| Investigation | Required evidence | Points |
|---|---|---:|
| Calendar and cohort contract | Person counts, disjoint IDs, baseline/decision/label times; one delayed-input trace; fields legitimately available at decision time | 15 |
| Representation comparison | Frozen raw/personal models; validation and reserved evaluation reports; coverage, all/eligible people, Brier, AUC and calibration counts; dependence and undefined quantities explained | 20 |
| Baseline and measurement compatibility | Reference source IDs, mean/SD convention, insufficient case, physical versus firmware shift, why a z score is not a diagnosis | 15 |
| Risk versus net utility | Development randomized cell counts/contrasts; three evaluation rankings under the same maximum budget; selected counts and oracle-scored expected utility; no conflation with longitudinal risk | 20 |
| Gain states and injected faults | Proposal/permission/delivery trace, six fault reasons, persistent freeze on a later eligible record, explicit recovery boundary | 20 |
| Reconstructable export and interpretation | Manifest and receipt scope, separated future references/oracle, limitations and evidence needed beyond simulation | 10 |

For the prediction comparison, identify the final evaluation procedure before inspecting its results. If you change any rule after inspection, label the resulting comparison exploratory. Explain why a shared model with personal-reference inputs is different from fitting an unconstrained classifier for every person. Do not claim individual calibration from pooled calibration bins.

For the randomized experiment, explain what random assignment contributes and what sparse cell counts leave uncertain. Distinguish a conditional average contrast from a directly observed individual effect. If an estimated policy performs poorly, diagnose the information and uncertainty rather than changing the seed until it wins. The oracle is a teaching reference unavailable in ordinary practice.

For the gain workflow, include a default no-release decision and an explicitly permitted decision on the same eligible row. Preserve returned state. Show that the changed-firmware freeze survives an otherwise eligible subsequent snapshot. Explain the evidence and authorization needed for actual requalification; setting a Boolean to false is not such evidence.

Close with two proposed extensions: one measurement-validation study and one prospective evaluation of a specified decision. Name the target population, outcome/horizon, comparator, permitted adaptation, review responsibility, and stopping conditions. Design the study; do not invent clinical thresholds or treatment schedules.
