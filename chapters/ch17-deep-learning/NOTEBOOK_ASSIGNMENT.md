# Chapter 17: make it learn, then explain it — 100 points

Use [NOTEBOOK_GUIDE.md](NOTEBOOK_GUIDE.md) to open the five supplied notebooks. All code is provided. Your work is to predict what will happen, inspect actual results, explain the learned representations, and preserve the evidence. Complete [NOTEBOOK_REFLECTION.md](NOTEBOOK_REFLECTION.md) as your report.

| Activity | Points | Required explanation and evidence |
| --- | ---: | --- |
| CNN | 20 | Trace 28×28×1 → 26×26×8 → 13×13×8 and the remaining layers; verify 80 first-layer parameters. Inspect one learned filter and one digit mistake or uncertain prediction. Preserve curves and selected epoch. |
| RNN / GRU | 15 | Explain 28 rows × 28 inputs, hidden state, order, and gating. Compare one SimpleRNN/GRU alternative using validation; distinguish this image-row construction from physiological time. |
| Transformer | 15 | Explain 49 patches, 32 features, position encoding, two 16-dimensional heads, residual paths, and 2,401 score pairs per head. Show the patch grid. Explain why the network is an encoder-style classifier, not a language model. |
| Autoencoder | 15 | Compare clean, artificially corrupted and reconstructed images; report noisy-input and reconstruction MSE. Explain 16 latent coordinates, the encoder/decoder, and why reconstruction need not preserve clinically meaningful signal. |
| Public EEG | 20 | Audit train/validation/test people, run-specific task labels, epoch-to-person provenance, training-only normalization, each test person's task accuracy and the classical comparison. Explain limitations of the two-person test. |
| Evidence and reflection | 15 | Save selected configurations, split IDs, notebook/source version, environment, curves, task evidence, selected weights hash, and a concise claim/limitations statement. Distinguish exploratory validation from protected final testing. |

## Before each run

Write one prediction. Read the default controls and inspect the model recipe. Run the supplied cells in order. Make one declared validation-based change rather than editing many parameters. If you repeat a test after exploring results, label that evidence exploratory; do not claim an unbiased test of a winner selected from it. Do not require every model or seed to improve.

## Interpret the tasks honestly

- MNIST is public handwritten-digit data. The loader provides official source arrays but no writer identities; do not describe its subset as an EEG participant split.
- The autoencoder uses artificial pixel corruption and clean digit targets, not clinically established EEG artifact removal.
- In the EEG notebook, each person has both imagery classes. Score task epochs and summarize per person; do not turn the labels into one diagnosis per person.
- The existing synthetic PyTorch pipeline is a separate advanced engineering track. Its participant-level artificial target and aggregation rule differ from this measured motor-imagery task.

## Submit

Commit your authored reflection and configuration records under `submissions/ch17/student-id/` (replace `student-id` with your course identifier). Include the source commit and notebook names. Keep raw downloads, generated output directories, executed notebook outputs, and model binaries out of Git. Provide requested plots/reports through the course submission platform; retain all artifacts locally. Record weight and source-file hashes without uploading models or raw EEG.

Notebook outputs are initially empty. Report what actually happened in your environment, including failures or non-improvement. A source/shape check is not an executed model result. Clinical validation and authorization remain absent.
