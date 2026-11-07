# Chapter 28 — NeuroBridge capstone studio

Build a small, inspectable research system. Follow an invented neural-like recording through a fitted baseline, a virtual request, deliberate faults, and an evidence card. The reward is a result another reader can reconstruct and a next study you can defend.

Start with [STUDY_CONTRACT.md](STUDY_CONTRACT.md), open [capstone_studio.ipynb](capstone_studio.ipynb), and complete the [100-point assignment](ASSIGNMENT.md). The helper [capstone_studio.py](capstone_studio.py) uses only Python 3.11+ standard-library modules. No patient files, headset, GPU, cloud account, API key, downloaded model, or physical intervention is involved.

## Setup

Clone or download the repository, then open a terminal **inside `chapters/ch28-capstone/`**. Create a virtual environment:

```sh
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\activate` in Windows Command Prompt. Install the optional notebook interface and launch it:

```sh
python -m pip install -r requirements-notebooks.txt
python -m jupyterlab
```

Installation needs package access; the exercise itself needs no network service. Select the environment's Python kernel. Keep the notebook beside the helper, restart the kernel, and run from the top. All submitted notebook outputs are initially empty. Authors performed static inspection only; students execute and interpret their own results. No measured accuracy, latency, or fault outcome is supplied in advance.

## What you build

1. Inspect 24 invented people, 48 records, schemas, labels, and participant partitions.
2. Fit one transparent threshold using development data and save its fitting IDs.
3. Evaluate held-out records and report both accepted-record accuracy and coverage.
4. Inspect declared role, clock, schema, model-version, and quality boundaries.
5. Run ten request fault cases, one participant-overlap audit, and a restored request.
6. Export a new evidence bundle and open its local HTML research card.
7. Change a copied report, compare the receipt, and defend a bounded next study.

There is no trained neural encoder here; Chapter 27 provides that optional experiment. This capstone focuses on the connections around an inspectable baseline. The broader Phase XX architecture is a design target, not implemented infrastructure.

## Read outputs precisely

`accepted` means the virtual request passed the implemented checks. It does not mean the recording is clinically valid. `prediction=1` identifies the high-noise fixture recipe according to the fitted threshold; it is not a diagnosis. `uncertainty` is explicitly not estimated, and no probability is returned. Refusals contain no prediction and a simulated hold-for-review label. No function transmits commands or alters a device.

Role and network flags are supplied inputs, not production identity or network tests. The drift example is a declared quality hold, not detected drift. Restoring the original request demonstrates restored-input behavior in a stateless function, not a persistent incident-recovery system. A model digest and receipt allow byte comparison, not authentication or immutability.

## Reuse and extension

Run the default protocol before changing it, preserve the original output directory, and report any redesign as a new study. Real recordings require rights, acquisition-aware conversion, new reference judgments, and independent evaluation. A real service also requires evaluated identity, permissions, timing, failure handling, monitoring, and deployment controls. No automated update or deployment is part of the studio.
