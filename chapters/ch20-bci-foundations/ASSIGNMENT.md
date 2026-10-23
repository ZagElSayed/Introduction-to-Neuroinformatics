# Chapter 20 assignment: a replayable EEG controller (100 points)

Submit the three notebooks with your observed outputs, saved JSON receipts, and a concise BCI system card. Your grade depends on valid reasoning and traceable behavior, not a high accuracy.

| Criterion | Points | Full-credit evidence |
|---|---:|---|
| Data and physiological contract | 20 | Correct S001 runs/labels, channel order, volts/µV distinction, source hashes, and a defensible account of what motor imagery labels represent |
| Decoder and evaluation split | 20 | Train-only scaling/fitting; trial counts/confusion and balanced accuracy; R08 development and frozen R12 protocol; no overlapping-window independence claim |
| Replay and command policy | 20 | Stateful causal filter, past-window buffer, naive/gated trajectories, score/dwell/refractory explanations, bounded cursor, and limitations of no-control inference |
| Fault and timing investigation | 20 | Explain all three injections and detected events, show inhibition/warm-up behavior, distinguish sample/virtual/processing clocks, and report latency limits honestly |
| Report, provenance, and reflection | 20 | Rates with correct denominators/coverage, accepted counts and conditional accuracy, complete versioned artifacts, and a system card that separates replay from live/clinical claims |

For each criterion, partial credit reflects which required evidence is present and scientifically defensible; unsupported claims or missing artifacts cannot earn full credit. Zero credit in a criterion means no assessable evidence for it. No participant study, live headset session, flickering stimulus, physical actuation, or stimulation is part of this assignment.

Before final R12 evaluation, record your frozen configuration and the reason for any R08-driven change. If you already used R12 to select a change, say so and replace the independent-test claim with an exploratory result; propose a fresh evaluation design.

The system card must state: intended teaching use; source and label contract; train/validation/test units; feature/filter/model versions; policy and QC limits; evidence produced; fault recovery rules; timing actually measured; remaining limitations; and the next experiment needed for live BCI evidence.
