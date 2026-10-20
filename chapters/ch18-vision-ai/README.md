# Chapter 18 — Vision-Based AI for Neural Signal Interpretation

Start with the **[public-data notebook studio](NOTEBOOK_GUIDE.md)**: three guided Colab/Jupyter notebooks turn real resting EEG into images, train a small recording-condition CNN, and build an interactive visual review tool. All code is supplied. Use the **[notebook assignment](NOTEBOOK_ASSIGNMENT.md)** and **[reflection template](NOTEBOOK_REFLECTION.md)** for the introductory route. No paid API, pretrained weights, or GPU is required. See the guide for public-data licensing, source provenance, participant boundaries, and the limits of this small demonstration.

The material below is the **advanced synthetic PyTorch rendering-audit track**, with its separate 100-point rubric. Its no-VLM and measured-data-extension statements refer to that executable; the new public notebook route supplies its own measured resting-condition experiment and Grad-CAM/retrieval tool.


Audit the entire waveform → numeric derivative → image → prediction chain. Complete NeuroBridge Phase X by preserving a visual representation contract and distinguishing file encoding, candidate nuisance shifts and actual source changes.

## Data and scientific contract

This is an offline **synthetic educational experiment**, not measured EEG or clinical diagnosis. The generator creates 48 artificial participants, four windows each, one channel, 256 samples per window and sampling rate 128 Hz. An invented participant label changes the amplitude of a 10-Hz sinusoid; a 22-Hz component and noise form the background. No raw clinical data, pretrained model or VLM API is used.

The renderer uses 64-sample symmetric Hann tapers, 32-sample hops, per-segment mean detrending and one-sided power-density normalization. Each window yields a 33-frequency × 7-time matrix. Power units are arbitrary-unit²/Hz. Log power is relative to one arbitrary-unit²/Hz, floored at 1e-12, mapped using fixed -40 to -5 dB bounds, clipped, quantized to 8-bit grayscale and resized with nearest-neighbor interpolation to 64×64 pixels. Low frequencies appear at the bottom. Enlargement does not create additional frequency/time resolution. Frequency coordinates and segment start samples remain in the numeric derivative.

Baseline PNGs contain no axes, text or labels. The complete config is hashed and manifests link every image to its original waveform row and participant. Fixed rendering bounds are prespecified; bounds estimated from a cohort would need training-only fitting. The CNN consumes normalized pixel arrays `[batch,1,height,width]`, not the decorated audit montage or image filenames.

## Install and run

From the repository root with Python 3.11 or newer:

```bash
python -m pip install -r requirements.txt 'Pillow>=10,<13'
python -m pip install 'torch>=2.2,<3' --index-url https://download.pytorch.org/whl/cpu
python chapters/ch18-vision-ai/exercise_18_1_render_audit.py --config chapters/ch18-vision-ai/config.json --output-dir outputs/ch18
python -m pytest -q tests/test_chapter18_lab.py
python chapters/ch18-vision-ai/exercise_18_1_render_audit.py --config outputs/ch18/config.json --output-dir outputs/ch18-reproduced
```

Alternatively install the chapter's `requirements.txt`; it includes repository dependencies plus PyTorch and Pillow. Use an exact environment lock for durable experiments. The report records installed versions; cross-version image encoding and model numerics are not guaranteed identical.

All config keys are required. Participants must be even and >=24, windows >=2, seed nonnegative, sampling rate exactly 128, segment >=16 and no greater than the recording length, hop between one and segment length, image size >=16, epochs positive. Display bounds are finite and ordered; signal strength is finite/nonnegative and learning rate finite/positive. The baseline device is CPU.

## Model and evaluation

Participants are stratified into train/validation/test partitions (approximately half/quarter/quarter, with integer rounding). The compact CNN uses Conv2d(1,8,3), ReLU, average pooling, Conv2d(8,8,3), ReLU, 4×4 adaptive pooling and a linear logit head: 793 parameters. The coarse spatial grid retains some frequency/time position. Training uses BCEWithLogitsLoss and fixed AdamW settings; the checkpoint minimizes validation loss across the configured epochs. Test inputs cannot select the checkpoint. Inference checkpoint reload is verified; optimizer resume state is not stored.

A fixed-C logistic baseline uses numerical mean 8–12-Hz power with training-only feature scaling and the same grouped train/test rows. CNN and classical metrics average window probabilities per held-out participant at a fixed 0.5 threshold. Accuracy, ROC-AUC and Brier are reported; probability calibration is assessed, not fitted. One small synthetic split and seed supplies no clinical evidence or uncertainty interval. A strong numerical baseline may outperform the vision model; investigate representation and optimization before drawing broader conclusions.

## Controls and perturbations

| Test | What it establishes |
| --- | --- |
| PNG compression 0 versus 9 | File bytes differ; decoded pixels and deterministic predictions must be identical |
| JPEG quality 45 | Lossy quantization can change pixels; record prediction/metric changes |
| Bilinear downsample/upsample | Resampling can blur or alter representation details; it is not automatically benign |
| Gamma 1.2 | A monotonic display remapping tests dependence on intensity encoding |
| Target-coded corner | An intentionally invalid label leak makes the target directly recoverable; it is not used for fitting |
| Remove simulated 10-Hz component | Source information changes before rendering; this is not merely formatting and not a neural causal experiment |

The corner reader proves label information exists in that constructed image; it does not prove the trained CNN relied on the corner. The three rendering perturbations are candidate nuisances, not guaranteed invariances. Report pixel-change fraction, mean absolute probability change and participant metrics. A small average change can hide individual failures. Do not tune rendering choices using the test outcomes.

## Derivatives

| Artifact | Purpose |
| --- | --- |
| `source_waveforms.npz` | Synthetic waveform arrays, labels, participant IDs and sampling rate |
| `numeric_power_maps.npz` | Floating-point power matrices, frequency coordinates and segment starts |
| `config.json` | Complete reusable generator/renderer/training specification |
| `images/*.png` | Undecorated grayscale model inputs |
| `image_manifest.json` | Source row, participant, split, renderer/config/source/file/pixel hashes, shape/mode and units |
| `split_manifest.json` | Three-part row and participant assignments |
| `vision_checkpoint.pt` | Validation-selected model weights and configuration |
| `predictions.csv`, `training_curves.csv` | Window predictions and clean training/validation losses |
| `render_audit.png` | Display montage of reference, perturbed and deliberately invalid controls |
| `vision_report.json`, `model_card.md` | Metrics, controls, software versions, hashes and limitations |

Keep generated outputs untracked. Hashes identify content, not scientific validity. CPU deterministic algorithms and one thread are requested. Matching environment/source/config should reproduce splits, pixels, predictions and curves; cross-version byte identity is not promised. Load only trusted checkpoints.

## Assignment — 100 points

1. **Numerical-to-pixel contract (20):** Verify the one-sided PSD normalization, dimensions, physical coordinate mapping, dB reference, fixed bounds, clipping and quantization. Explain why upsampling creates no additional information.
2. **Lineage and split audit (20):** Verify source/file/pixel hashes and participant separation. Trace one prediction back through its image, power map and waveform row.
3. **Model comparison (15):** Compare participant-level CNN and numeric-feature logistic outputs under the same boundaries. Discuss representation losses, optimization and the small cohort.
4. **Robustness interpretation (20):** Interpret all controls and three candidate rendering shifts. Distinguish exact encoding equivalence from invariance hypotheses and true source changes.
5. **Reproduction and sensitivity (15):** Re-run saved config and compare splits, pixels, predictions and curves. Run another seed or justified display range in a separate output directory without choosing a favorable test result.
6. **GitHub reflection (10):** Submit a source/config commit, manifests, audit figure, model card and a reflection linking NeuroBridge measurement, renderer and model provenance. Keep restricted data and generated derivatives outside Git.

## Graduate and measured-data extensions

Compare signal-domain and image-domain models using the same participants; add nested representation selection, site-held-out evaluation or attribution sanity checks. For VLM assistance, define a strict category/abstention schema, validate referenced evidence panels, assess prompts/candidate labels and calibration, and keep human decisions reversible. No VLM confidence or generated rationale substitutes for empirical validation. These extensions are not implemented by the baseline.

Optional measured-data source: [PhysioNet EEG Motor Movement/Imagery v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI [10.13026/C28G6P](https://doi.org/10.13026/C28G6P), under its stated Open Data Commons Attribution License v1.0. Follow release attribution and task/event definitions; no diagnostic labels are supplied. Preserve channel/run selection, sampling rate, preprocessing and participant IDs. Adapt the synthetic one-label-per-person split/aggregation contract for within-person task labels. The executable does not download this release.

References: [PNG specification](https://www.w3.org/TR/png-3/), [CLIP original paper](https://arxiv.org/abs/2103.00020), [Grad-CAM](https://arxiv.org/abs/1610.02391), and [saliency sanity checks](https://arxiv.org/abs/1810.03292).

