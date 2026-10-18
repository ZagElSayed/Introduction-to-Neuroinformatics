# Chapter 17 notebook studio

Start with a prediction, run the supplied cells, inspect what happened, and explain it. You do not have to write a training loop. Each notebook contains its complete code and can run independently of the others. The existing PyTorch synthetic lab remains a separate advanced track.

## Open in Colab or Jupyter

| Notebook | What you will do | Hosted notebook |
| --- | --- | --- |
| [01 — CNN](notebooks/01_cnn_mnist.ipynb) | Learn stroke detectors; inspect filters and digit mistakes | [Open in Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch17-deep-learning/notebooks/01_cnn_mnist.ipynb) |
| [02 — RNN and GRU](notebooks/02_rnn_mnist.ipynb) | Read image rows as a sequence; inspect a learned running summary | [Open in Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch17-deep-learning/notebooks/02_rnn_mnist.ipynb) |
| [03 — Transformer](notebooks/03_transformer_mnist.ipynb) | Turn patches into tokens; trace position, attention, and residuals | [Open in Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch17-deep-learning/notebooks/03_transformer_mnist.ipynb) |
| [04 — Autoencoder](notebooks/04_autoencoder_mnist.ipynb) | Compress and reconstruct digits with artificial noise | [Open in Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch17-deep-learning/notebooks/04_autoencoder_mnist.ipynb) |
| [05 — Public EEG](notebooks/05_public_eeg_cnn.ipynb) | Decode motor-imagery epochs from held-out people; compare a classical model | [Open in Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch17-deep-learning/notebooks/05_public_eeg_cnn.ipynb) |

Colab: open a notebook, save your own copy, keep the default CPU setting, and run its cells from top to bottom. Setup cells install missing packages into that notebook environment. Expand collapsed cells whenever you want to inspect the implementation. Download the generated run directory and your notebook before ending the session. Free resources are variable; a GPU or uninterrupted runtime is not guaranteed. See [Google's FAQ](https://research.google.com/colaboratory/faq.html).

Local alternative, from the repository root in a Python 3.11 virtual environment:

```text
python -m pip install -r chapters/ch17-deep-learning/requirements-notebooks.txt
python -m jupyterlab
```

Open `chapters/ch17-deep-learning/notebooks/`. Generated paths are relative to the notebook kernel's working directory. Each run prints its unique output directory. Internet is needed for the initial public-data download and missing packages. If a package installation requires a kernel restart, restart and rerun from the beginning. Downloaded data are cached, so later runs need not download them again.

## One familiar dataset, four different ideas

The first four notebooks use **real public MNIST images**, not synthetic digits or neurodata. [Keras documents the loader and license](https://keras.io/api/datasets/mnist/): original training 60,000 images, original test 10,000; copyright Yann LeCun and Corinna Cortes, CC BY-SA 3.0. Retain attribution and follow that dataset's terms when redistributing images or derivatives.

The default subset uses 500 training and 100 validation images per digit from the official training array, plus 100 per digit from the official test array: 5,000/1,000/1,000 total. The split seed and saved source-array indices match across notebooks. Writer identities are not supplied by this loader. Thus the exercise demonstrates image-level classification or reconstruction, **not unseen-person neurophysiological validation**.

CNN, RNN/GRU, and Transformer notebooks classify ten categories using logits and cross-entropy. The autoencoder instead receives noisy images and reconstructs clean images with MSE. Digit labels only stratify its subset and color an optional latent-coordinate plot. Classification accuracy and reconstruction MSE answer different questions and cannot rank all four architectures on one shared task.

## Now make the neuroscience connection

Notebook 05 uses [PhysioNet EEG Motor Movement/Imagery v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/), DOI [10.13026/C28G6P](https://doi.org/10.13026/C28G6P), under the release's stated Open Data Commons Attribution License v1.0. Attribute Schalk and the PhysioNet release. MNE's [documented run mapping](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html) identifies runs **4, 8, 12 as imagined left/right hand movement**.

| Contract | Declared notebook choice |
| --- | --- |
| People | 1–9, three runs each; no private recordings |
| Split | Train 1–5, validation 6–7, test 8–9 |
| Labels | T1 → 0 left-hand imagery; T2 → 1 right-hand imagery |
| Inputs | C3, Cz, C4; original acquisition reference retained |
| Processing | Per-recording 1–40 Hz filter; first 2 seconds from each selected cue; epoch resampling from 160 to 64 Hz with anti-aliasing |
| Tensor | Keras `[epochs, 128 samples, 3 channels]` |
| Learned normalization | Per-channel mean/SD from training epochs only |
| Selection | Validation loss and early stopping |
| Comparison | Small temporal CNN versus fixed logistic regression on simple Fourier summaries, same train/test people |
| Scoring | Epoch targets retained; each test person's epoch accuracy, then macro mean across the two people |
| Intended interpretation | Retrospective task decoding; no causal streaming or diagnostic claim |

The loader may drop annotated bad/boundary epochs; inspect the printed label table and saved epoch manifest. Source files, event samples, participant IDs, source-file hashes, and preprocessing choices are preserved. Windows from the same person are related; two test people remain two people, regardless of epoch count. Do not average varying task labels into a single participant diagnosis.

## What to change, and what to keep protected

Read each notebook's controls. Defaults are deliberately small. Explore one declared change using validation: CNN filter count, SimpleRNN versus GRU, Transformer dimensions, or autoencoder bottleneck/noise. A Transformer embedding dimension must remain compatible with its positional encoding and heads; the provided default fixes 32 dimensions and two 16-dimensional heads. The EEG participant sets and label contract stay fixed for the introductory assignment.

Do not repeatedly inspect test scores to choose settings and then call the winning score an independent estimate. A fresh test claim needs a further protected evaluation. No accuracy, MSE improvement, GPU availability, or timing result is guaranteed. A surprising result should start an investigation of shapes, targets, optimization and evidence.

## Evidence and execution status

Each run saves configuration, source-array/split IDs, history, selected weights, available task plots/predictions, versions, and hashes. The EEG notebook additionally saves epoch provenance and normalization. The autoencoder saves reconstructions rather than classifier predictions. `report.json` records `review_required` and `accepted: false`, and hashes existing companion artifacts rather than itself.

Retain the notebook architecture with weights; a weights file alone cannot recreate the model or resume the exact optimizer trajectory. Generated run directories and raw downloads belong outside Git. Use course-platform attachments for requested evidence and commit authored reflections/configurations. See [NOTEBOOK_ASSIGNMENT.md](NOTEBOOK_ASSIGNMENT.md) and [NOTEBOOK_REFLECTION.md](NOTEBOOK_REFLECTION.md).

These notebook sources have been checked statically. They contain no prefilled outputs and have **not been executed by the authoring assistant**. Run them locally or in your own Colab runtime and retain any errors and observed results. Static parsing does not establish runtime compatibility or model performance.
