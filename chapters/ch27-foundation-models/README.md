# Chapter 27: neural representations and grounded research assistance

Start small: inspect the records and token contract, run an interpretable baseline,
then decide whether self-supervised pretraining earns its additional complexity.
The second exercise retrieves authorized teaching passages and checks their anchors.
No patient data, external model service, API key, GPU, or downloaded weights are needed.

Read [STUDY_CONTRACT.md](STUDY_CONTRACT.md), open
[foundation_model_studio.ipynb](foundation_model_studio.ipynb), and submit the
[100-point assignment](ASSIGNMENT.md). All notebook outputs are intentionally empty.
The materials were reviewed statically; students must execute and assess the results.

## Local setup

Use Python 3.11 or later. In this chapter folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-notebooks.txt
jupyter lab
```

On Windows use `.venv\Scripts\activate` to activate the environment.
The core helper uses only the standard library; Jupyter is an interface dependency.
The optional neural experiment requires PyTorch:

```bash
python -m pip install -r requirements-torch.txt
```

PyTorch wheels depend on operating system and Python version. If pip cannot resolve
a wheel, use the [official installation selector](https://pytorch.org/get-started/locally/)
with CPU selected. Installation needs network access; the exercises then run offline.
Record the installed Python/PyTorch versions and your environment lock or package list.
No runtime, performance, or cross-platform reproducibility result is claimed here.

## Two routes through the notebook

1. **Core:** generate invented waveforms; audit participant splits; fit development-only
   normalization; inspect 32 channel-time tokens; fit two fixed-frequency features
   plus logistic regression; investigate faults; retrieve passages; export the bundle.
2. **Optional neural experiment:** set `RUN_TORCH = True` after installing PyTorch.
   Compare a random frozen encoder, masked-pretrained frozen encoder, and supervised
   encoder from the same initialization and labeled development subset.

The tiny encoder has 16-dimensional tokens, one transformer block, two attention heads,
and no dropout. It pretrains on 12 invented development people, masking 10/32 patches
per example, then compares classifiers using six labeled development people by default.
It is a teaching experiment, **not a foundation model** or replication of BrainBERT,
BIOT, LaBraM, or EEGPT. The fixed-frequency baseline is deliberately well suited to
the invented target. Pretraining need not improve its downstream task.

## What the evidence exercise implements

The passages are author-written toy documents, not clinical guidance or paper excerpts.
Role/status filtering happens before lexical ranking. Claim checking recognizes an
exact passage match or asks for human review. It does not implement an LLM, semantic
entailment, a production identity provider, RAG generation, or general injection defense.
The quarantined attack is pre-labelled; successfully excluding it does not demonstrate
automatic prompt-injection detection. No retrieved text is executed.

## Artifacts and interpretation

Each export creates a new folder beneath `outputs/`. The core bundle contains records,
separate fabricated labels, a normalizer with fit IDs, reports, evidence, a manifest,
and a hash receipt. Optional model states are added with their hash in the same receipt.
The receipt supports byte comparison, not authentication or tamper-proof storage.
Do not load an untrusted checkpoint. Do not commit generated output folders or environments.

Use the exported predictions for your own person-level uncertainty analysis. Default
metrics are descriptive accuracy at 0.5, Brier score, and five reliability bins; no
confidence intervals, calibrated probabilities, clinical utility, or external transfer
are established. The final cohort is unseen in pretraining and fitting, but comes from
the same invented recipe, so it is not a test of hospital or disease generalization.

## Original research and documentation

- [BrainBERT, ICLR 2023](https://openreview.net/forum?id=xmcYx_reUn6)
- [BIOT, NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/f6b30f3e2dd9cb53bbf2024402d02295-Abstract-Conference.html)
- [LaBraM, ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/47393e8594c82ce8fd83adc672cf9872-Abstract-Conference.html)
- [EEGPT, NeurIPS 2024](https://papers.nips.cc/paper_files/paper/2024/hash/4540d267eeec4e5dbd9dae9448f0b739-Abstract-Conference.html)
- [PyTorch transformer API](https://docs.pytorch.org/docs/stable/generated/torch.nn.TransformerEncoder.html)
- [PyTorch reproducibility notes](https://docs.pytorch.org/docs/stable/notes/randomness.html)

Inspect each paper's own corpus, evaluation, code, weights, and licensing before reuse.
Availability of a repository does not establish rights to all associated data or weights.
