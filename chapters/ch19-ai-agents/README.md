# Chapter 19: AI Agents and Intelligent Neuroinformatics Automation

Build a small analysis assistant you can inspect. Start with a structured request, let a bounded runtime call five Python tools, calculate a synthetic spectral summary, and inspect the trajectory before recording a review.

## Start here

The core uses **Python 3.10+ and the standard library**. No GPU, API key, external model, or data download is required for the baseline in a local clone. Jupyter/Colab is needed only for notebooks. All signals are synthetic; there are no participant records or diagnostic predictions.

1. Open [the notebook guide](NOTEBOOK_GUIDE.md) and follow notebooks 01–03.
2. Alternatively, from this directory run `python run_demo.py --dataset toy_good`.
3. Try `python run_demo.py --dataset toy_missing_units` and compare the stop reason.
4. Run `python run_demo.py --evaluate --output agent_outputs` to generate the 20-case evaluation table in your environment.

These are student-run commands. The authored materials were checked statically; runtime results and timings are not claimed in advance.

## What you build

| Component | Implementation |
|---|---|
| Task | A fixed synthetic EEG spectral-summary request scoped to one dataset ID |
| Tools | `read_metadata`, `read_recipe`, `read_qc`, `compute_alpha`, `stage_report` |
| Planner | Deterministic baseline; replaceable proposal callback for experiments |
| Policy | Allowed dataset IDs, tool prerequisites, exact arguments, call budget |
| Verification | Source identity, approved recipe, finite JSON, power bounds, spectral energy consistency, staged-file readback and hash |
| State | Verified tool results, statuses, explicit errors, per-call trajectory |
| Output | A staged JSON report, run log, and separately authored local review record |

The baseline is a **conditional workflow**, not an LLM reasoning experiment. An LLM planner can propose the same small JSON call after a student builds an adapter; the optional `ollama_planner.py` adapter targets a separately installed local Ollama server and local model. Tool results remain data rather than policy. The runtime checks proposals regardless of who selected them.

## Scientific recipe

One synthetic channel contains 256 samples at 128 Hz (two seconds), with known 10-Hz and 22-Hz sinusoids plus seeded noise, in declared illustrative microvolt units. Subtract the whole-window mean, apply a symmetric Hann window, and compute a full-window one-sided density periodogram. Double interior positive-frequency bins, retaining DC and Nyquist undoubled. Frequency spacing is 0.5 Hz. Sum density bins whose centers satisfy 8 ≤ f ≤ 12 Hz and multiply by 0.5 Hz, yielding an illustrative alpha-band power in µV². Check total spectral energy against the direct window-weighted time-domain energy. This explicit O(N²) calculation favors inspectability for 256 samples; use vetted numerical libraries for real workloads. This recipe differs from Chapter 18's image renderer.

Recipe checks reject missing/wrong units, unsupported sampling rate or length, constant data, and nonfinite/nonnumeric samples. They are **eligibility checks**, not validated clinical EEG QC. Alpha power is a computed descriptor, not evidence of a cognitive state or diagnosis.

## Artifacts and limits

`agent_outputs/staging/` contains reports with pending review; `runs/` contains trajectories; `reviews/` contains separate review decisions tied to a confirmed report hash. Re-running creates a new run ID. The runtime does not delete source data, promote reports to final derivatives, contact others, or retrain a model. A read tool can retry once; writes are not automatically retried. Long-running external tools would additionally need timeouts and job-level cancellation.

Local Python path checks and proposal validation are teaching controls, **not an operating-system sandbox or identity provider**. The proposer callback is trusted Python running in the same process; use the JSON interface across a properly isolated service boundary for an untrusted planner. A typed reviewer name records an educational decision; it does not authenticate a real approver. The baseline's handling of a malicious annotation does not establish that an LLM resists prompt injection.

See [ASSIGNMENT.md](ASSIGNMENT.md), [REFLECTION.md](REFLECTION.md), and [RESOURCES.md](RESOURCES.md). All ten textbook figures remain conceptual teaching anchors; the notebooks implement selected components.

## Optional local LLM planner

Notebook 02 includes an opt-in cell for `ollama_planner.py`. Install Ollama separately using its official instructions and select an installed local model appropriate to your machine. Set `ENABLE_LLM = True` and enter its exact name. The adapter sends synthetic state to `127.0.0.1:11434/api/chat`, requests a schema-shaped JSON proposal, and returns it to the same runtime. No model is downloaded or called by default. No particular hardware, model success, or latency is promised. Use a local runtime; a hosted Colab kernel cannot reach your laptop's loopback address.

Retain the adapter trace, Ollama version, and installed model identity/digest. Temperature zero does not guarantee identical trajectories. Request timeouts and bounded response size limit a call, while the runtime limits total attempts; deployment still needs stronger process and service isolation. The optional adapter has received static checks only.
