# Chapter 18 — Visual EEG review tool reflection

Name / date / authored commit:

Notebook source commit or ref; exact helper SHA-256; environment; run directory:

## 1. Predict → run → inspect → explain

My initial prediction about one display change:

What changed in pixels, and what stayed the same in the source recording:

## 2. Representation and lineage (20 points)

Derivative ID and source EDF hash:

Window/channel/unit contract; 29×13 derivation; time-coordinate convention:

Power averaging, dB reference/bounds, clipping, resizing, and lost information:

PNG bytes versus decoded pixels result:

## 3. Boundaries and labels (20 points)

Participant sets and overlap audit:

Run-to-label mapping and run-order limitation:

Window count versus independent participants; test summary unit:

## 4. Model evidence (20 points)

CNN shapes/logit/loss; selected and stopped epochs:

Numerical baseline features and training-only fit:

CNN and comparator results; selected clean-training loss versus batch curve:

Limits of two test people; how I avoided test-driven iteration:

## 5. Tool inspection (25 points)

Validation derivative / model hash / attribution target:

Heatmap layer/resolution and what interpolation cannot add:

Replacement rule and signed output change:

Training-gallery retrieval and why similarity is not diagnosis:

QC flags and randomized-parameter comparison, including constant-map handling:

## 6. Evidence and review (15 points)

Linked model, manifests, source/config, package versions, saved figures, report, and latest review record:

Invalid panel-reference check and what passing a schema cannot establish:

Required human review; what the tool does not authorize:

My next scientifically justified experiment and evaluation plan:
