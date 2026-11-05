# Assignment: make representation reuse and evidence traceable (100 points)

Submit your executed notebook, an evidence bundle, and a 1,200–1,800-word interpretation.
Disclose the Python environment, hardware, seed, changed settings, and any failed cells.
Do not invent outputs or report toy results as neurological findings.

| Task | Points | Evidence required |
|---|---:|---|
| Explain the question and independence boundary | 15 | Person/session/window counts; split audit; why this is not hospital transfer |
| Trace the tokenizer and scaling | 20 | 32-token calculation; one token's channel/time origin; fit IDs; missing-channel mask and rejected schema |
| Evaluate a transparent baseline | 15 | Fixed-frequency features, development fit, separate validation/final metrics, reliability-bin interpretation |
| Investigate failures | 15 | Missing channel, unsupported rate/units, non-finite samples, all missing; explain mask versus reject |
| Audit retrieved evidence | 15 | Authorized anchors, excluded passages, exact match versus paraphrase needing review, limits of curated quarantine |
| Reconstruct and interpret the bundle | 20 | Files/versions/digests, repeated-person dependence, limitations and a next experiment; no unsupported claims |

## Optional neural extension (discuss within the same submission)

Run the PyTorch cell after installing the optional dependency. Compare all four methods
on the same labeled people. Report pretraining loss alongside downstream Brier/accuracy;
neither demonstrates the other. Account for extra pretraining compute. Preserve model
states and per-record predictions. A worse pretrained probe is an interpretable result,
not an excuse to tune on the final cohort.

The optional extension is not required for full core credit: students without PyTorch
can explain the code's representation and fitting boundaries, propose a preregistered
comparison, and explicitly state that no neural result was measured.

## Graduate extension

Choose one: implement a person-cluster bootstrap of the paired difference in Brier
scores; compare label budgets while freezing the final cohort; add a declared montage
conversion and assess it; or introduce semantic claim review with an openly licensed
language model and a separate reference set. Report any additional permissions,
dependencies, model licenses, data use, compute, and uncertainty. The core toy retriever
is not a reference-standard semantic verifier. Do not include identifiable data.
