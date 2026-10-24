# Chapter 21: Closed-loop and adaptive neurotechnology

Build an inspectable feedback controller using a **dimensionless synthetic process**. Compare a fixed policy with a bounded gain-update rule, inject measurement faults, inspect stop/recovery, and reconstruct every decision.

Start with [the guided notebook](01_bounded_adaptive_control.ipynb), the [simulation contract](SIMULATION_CONTRACT.md), and the [100-point assignment](ASSIGNMENT.md). No human data, headset, GPU, API key, network-connected device, or stimulation is used. The helper uses Python's standard library. Matplotlib is needed only for plots.

## Local setup

Use Python 3.11 or later in a virtual environment. From this folder:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-notebooks.txt
python -m jupyterlab
```

On Windows, activate with `.venv\Scripts\activate`. Open `01_bounded_adaptive_control.ipynb` and use the environment's kernel.

## Colab

[Open the notebook in Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch21-closed-loop/01_bounded_adaptive_control.ipynb). Its first cell fetches a pinned helper only when absent, verifies the expected SHA-256, and loads it. Read the contract and assignment from this folder before starting.

Verified baseline helper revision: [f6e8f3b](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics/blob/f6e8f3bdaeb88b551a7217071074f0526b781a59/chapters/ch21-closed-loop/adaptive_sandbox.py).
SHA-256: `3e3eaf24f573d3621c5ffea1a6595c6f9671f8c2feda7178b81c6f748d07936d`.

The digest identifies content relative to the expected baseline, not the operator or an authorization decision. Keep the baseline intact; version any extension separately.

## What you will do

1. Explain a hidden-state model and causal estimator.
2. Compare fixed proportional control with a bounded adaptive gain.
3. Distinguish proposed, issued, and delayed applied actions.
4. Challenge missing/stale input, an artifact proxy, manual stop, and recovery.
5. Audit decision reconstruction and specified numerical invariants.
6. Freeze the procedure before evaluating final seeds.
7. Report tracking, burden, coverage, variability, and limits.

No precomputed performance is supplied. Notebook outputs and execution counts are empty. The authoring review parsed code and inspected the contract; it did not run the simulation, notebook, or audit. Obtain and report your observed results when you run the exercise.

A recorded-data replay cannot reveal the biological outcome of an action that was never delivered. This model-based simulation generates new synthetic outcomes under a changed policy, but does not validate its response model against a person.

## Resources

- [Chapter 20 replay studio](../ch20-bci-foundations/README.md): the preceding command-policy exercise.
- [Åström and Murray, Feedback Systems](https://authors.library.caltech.edu/records/yzs24-xsx88): control foundations.
- [Oehrn et al., 2024 adaptive-DBS feasibility trial](https://doi.org/10.1038/s41591-024-03196-z): read the actual clinical design and its scope.
- [CRED-nf checklist](https://doi.org/10.1093/brain/awaa009): neurofeedback evaluation and reporting.

The toy coefficients and action limits are not physiological parameters or a stimulation prescription.
