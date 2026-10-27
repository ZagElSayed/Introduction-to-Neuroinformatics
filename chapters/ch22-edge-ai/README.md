# Chapter 22 — Edge timing studio

Start with an explicit timing contract, make a small worker fall behind, and explain which outputs remain useful. The core runs with Python 3.11+ and the standard library. It uses no human data, neural network framework, hardware actuator, network service, or GPU.

The numbers are **virtual times assigned by a model**, not measured Python execution or edge-device performance. The synthetic feature threshold is a toy workload, not an EEG decoder or calibrated probability. Run the notebook to obtain your own results; no output has been precomputed.

## Start locally

Download this folder from the repository, keep its files together, and open `01_edge_timing_studio.ipynb`. If needed, create an environment and install the optional notebook dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-notebooks.txt
python -m jupyterlab
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead. The helper itself needs no pip packages. You can also use an ordinary Python session from this directory:

```python
import edge_timing as lab
run = lab.simulate(lab.Config(policy="latest", capacity=1, scenario="faults"))
print(run["summary"])
print(lab.audit(run))
print(lab.save_bundle(run))
```

The notebook includes a hash-checked bootstrap for Colab, pinned to the baseline helper commit. It writes to a dedicated `ch22_baseline` directory and checks an existing file before using it. Keep extensions in a separate version or directory. A byte hash supports reproducibility; it does not authenticate a device or certify the code.

## Learn in stages

1. Read [TIMING_CONTRACT.md](TIMING_CONTRACT.md). Draw the source-to-output path and distinguish the 400-ms evidence interval, 20-ms hop, and 100-ms deadline.
2. Run the nominal model and inspect one record. All simulated events share a virtual clock.
3. Compare bounded FIFO capacity eight with latest-window capacity one under overload. Then hold capacity constant to study replacement alone.
4. Add missing, delayed, and invalid windows. Inspect the status for every expected opportunity.
5. Plot completed-job ages together with release coverage and rejection counts. A faster conditional percentile is not a complete performance claim.
6. Run the student consistency checks and save a unique JSON bundle and receipt. Explain what these checks do and do not establish.

Follow the [100-point assignment](ASSIGNMENT.md) for the final report. A measured decoder, quantized artifact, actual device output, energy experiment, or cloud-disconnection experiment is an optional extension; none is implemented by the virtual core.

## Connection to Chapters 20 and 21

Chapter 20 supplies a causal EEG replay interface, and Chapter 21 separates observations, proposals, releases, and delayed effects. This studio isolates **runtime timing and queue semantics**. It does not import either previous helper, rerun human recordings, or stimulate a person. To combine them later, preserve source identity and timestamps, measure the new path, and state which timing values have become observations rather than assumptions.

## Files

- `edge_timing.py`: bounded-history signal generator, deterministic event scheduler, status accounting, virtual-record audit, and JSON saving.
- `01_edge_timing_studio.ipynb`: guided notebook, with empty outputs and execution counts.
- `TIMING_CONTRACT.md`: complete virtual semantics and evidence limits.
- `ASSIGNMENT.md`: deliverables, assessment criteria, and extension boundaries.
- `requirements-notebooks.txt`: optional notebook and plotting dependencies.

The teaching material has been statically inspected. The notebook, simulator, audit, and hardware extensions have not been executed as part of authoring. Students must run and inspect them before reporting outcomes.
