# Chapter 17 — Deep Learning for Neural Data

Train a compact temporal CNN, audit its information boundary and preserve the exact validation-selected inference checkpoint. This laboratory completes NeuroBridge Phase IX and builds on Chapter 16's independent-unit evaluation.

## Scientific contract

The baseline is **synthetic EEG-like waveforms**, not measured EEG, a validated head model or clinical diagnoses. It generates 48 artificial participants with six windows each, two ordered channels, 128 samples per window and sampling rate 64 Hz. An invented participant label changes the amplitude of an 8-Hz sinusoid; an 18-Hz component, participant-specific channel offsets and noise add variation. This intentionally simple generator does not establish a clinical decoding result.

Input shape is `[batch, 2, time]`, dtype float32. The network is `Conv1d(2,8,9,padding=4) → ReLU → AvgPool1d(2) → Conv1d(8,16,5,padding=2) → ReLU → global average pool → Linear(16,1)`. It has 825 parameters and **is not EEGNet**. The output is a logit; training uses `BCEWithLogitsLoss`, while evaluation applies sigmoid. Channel mixing preserves fixed order without asserting a 2-D scalp layout.

## Install and execute

From the repository root with Python 3.11 or newer, use a virtual environment:

```bash
python -m pip install -r requirements.txt
python -m pip install 'torch>=2.2,<3' --index-url https://download.pytorch.org/whl/cpu
python chapters/ch17-deep-learning/exercise_17_1_deep_pipeline.py --config chapters/ch17-deep-learning/config.json --output-dir outputs/ch17
python -m pytest -q tests/test_chapter17_lab.py
python chapters/ch17-deep-learning/exercise_17_1_deep_pipeline.py --config outputs/ch17/config.json --output-dir outputs/ch17-reproduced
```

Alternatively install `-r chapters/ch17-deep-learning/requirements.txt`; this includes the repository dependencies plus PyTorch. The explicit CPU command avoids unnecessary GPU packages for the teaching baseline. If an accelerator is needed, choose its installation from [PyTorch's official selector](https://pytorch.org/get-started/locally/). CUDA execution is optional and not asserted as equivalent to CPU; an unavailable requested CUDA device fails explicitly.

Every key in `config.json` is required. Participants must be even and at least 24, windows at least two, channels exactly two, samples at least 64, and sampling rate exactly 64 Hz. Epochs, patience and batch size are positive integers; seed is nonnegative. Learning rate is positive; decay, augmentation noise and signal amplitude are finite nonnegative numbers. `device` is `cpu` or `cuda`. These restrictions make the feature and synthetic target contract explicit.

## Evaluation boundary

The grouped experiment allocates half the participants to training, one quarter to validation and one quarter to test, stratified by the artificial participant label (integer rounding applies). Per-channel mean and standard deviation use training rows only. Noise augmentation operates on normalized training mini-batches only. Both plotted losses use clean unaugmented inputs. AdamW fits weights; validation BCE selects the checkpoint and controls patience; the selected checkpoint is reloaded before test inference.

The deliberately invalid row experiment has the same nominal architecture and training recipe, but related windows can occur in all three partitions. It answers a different question from prediction in unseen participants. Its score is not valid evidence for participant generalization. Do not assume that leakage always increases a score or that the same architecture receives exactly the same optimization trajectory when partition sizes differ.

Report row metrics for audit and **participant metrics from one mean test probability per person**. The 0.5 threshold and aggregation rule are fixed before evaluation. The classical baseline uses fixed `C=1` logistic regression on per-channel mean, variability and 7–9-Hz Fourier-power features, with training-only feature scaling and the same grouped training/test rows. These power features are illustrative uncalibrated Fourier summaries, not physical-unit PSD estimates. No nested architecture search or probability recalibration is implemented. Reliability and Brier score assess probabilities; average precision differs from trapezoidal PR-AUC.

Channel occlusion replaces normalized channel 1 with zero (the training mean), then records mean absolute probability change. This may create an unfamiliar input and is a model sensitivity probe, not a causal neural experiment or a realistic missing-channel simulation.

## Derivatives

| Artifact | Purpose |
| --- | --- |
| `config.json` | Complete reusable experiment specification |
| `split_manifest.json` | Row and participant assignments for all three partitions and both experiments |
| `predictions.csv` | Mean test probabilities and labels per participant |
| `naive_rows_curves.csv`, `grouped_participants_curves.csv` | Clean training/validation loss for each executed epoch |
| `naive_rows_checkpoint.pt`, `grouped_participants_checkpoint.pt` | Selected state dictionaries, normalization, config and best epoch |
| `evaluation.png` | Learning curves, reliability and same-participant model comparison |
| `deep_report.json` | Metrics, overlaps, timing, parameter count, versions, device and hashes |
| `model_card.md` | Input schema, intended use, limitations and persistence rules |

The script verifies checkpoint reload predictions. An inference checkpoint is not a resumable training checkpoint: optimizer, scheduler, RNG and sampler position are not saved. Load only trusted checkpoints. Keep outputs untracked.

CPU runs request deterministic algorithms and one thread. Reproduction means matching source, config, software versions and hardware context; split/prediction/curve comparisons are meaningful in that environment. Runtime, serialized bytes and cross-version/device results are not promised identical. Record an exact dependency lock for durable experiments; the supplied requirements define ranges.

## Assignment — 100 points

1. **Tensor and target contract (15):** Explain shapes, sampling rate, label construction, channel ordering and the distinction between signal epochs and training epochs.
2. **Partition and preprocessing audit (20):** Verify grouped train/validation/test identity disjointness; contrast row overlaps. Explain train-only normalization and augmentation inheritance.
3. **Learning and checkpointing (20):** Interpret the curves, lowest validation loss, patience and selected checkpoint. Explain why changing test data must not select a different model.
4. **Evaluation and classical comparison (15):** Compare participant discrimination, threshold errors and Brier score with the fixed logistic model. Interpret the reliability plot and tiny held-out cohort limitations.
5. **Sensitivity (15):** Run a copied configuration with another seed or augmentation-noise value to a separate directory; compare checkpoint selection and probability changes. Discuss channel occlusion and computational cost without claiming neural mechanism.
6. **Reproduction and GitHub reflection (15):** Re-run saved config; compare splits, predictions and curves; submit code/config commit, plots, model card, derivative hashes and a reflection linking NeuroBridge upstream provenance. Keep recordings and generated derivatives outside Git.

## Graduate extension

Add participant-aware outer evaluation and put architecture choice, normalization, augmentation policy, checkpoint selection and any calibration inside the development boundary. Compare raw waveforms and spectrograms, or compact CNN and attention, with the same participants and a prespecified compute budget. Quantify seed variability separately from participant sampling uncertainty. Add a resume checkpoint and a scientifically justified perturbation. Audit unlabeled pretraining overlap before making unseen-participant claims.

Optional measured-data extension: [PhysioNet EEG Motor Movement/Imagery v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI [10.13026/C28G6P](https://doi.org/10.13026/C28G6P), under its stated Open Data Commons Attribution License v1.0. Follow release attribution and run/event documentation; labels are motor tasks, not diagnoses. Preserve run timing and participant IDs, specify any resampling and channel subset, and adapt splitting/aggregation for within-person task labels. The synthetic baseline does not download or analyze this release.

References: [EEGNet original paper](https://arxiv.org/abs/1611.08024), [PyTorch Conv1d](https://docs.pytorch.org/docs/stable/generated/torch.nn.Conv1d.html), [logits loss](https://docs.pytorch.org/docs/stable/generated/torch.nn.BCEWithLogitsLoss.html), and [reproducibility guidance](https://docs.pytorch.org/docs/stable/notes/randomness.html).
