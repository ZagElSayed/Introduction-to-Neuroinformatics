# Chapter 19 — AI Agents and Autonomous Neuroinformatics Systems

NeuroBridge Phase XI adds a governed orchestration layer. This offline lab models a scientific request: retrieve an approved SOP, verify synthetic participant-level QC/alpha-power derivatives, and stage a descriptive summary for separate review. It uses a **deterministic planner stub**, not an LLM. No API key, download, network, clinical recording, or model is required.

## Learning goals

Trace a proposed call through schema checks, caller/dataset authorization, execution, scientific verification, and a terminal disposition. Distinguish a denied proposal from an executed forbidden effect. Bind review to exact artifact and input revisions; detect stale review; bound retries; preserve evidence instead of inventing results after failure.

## Setup and exact commands

From the repository root, use Python 3.11+:

```bash
python -m pip install 'pytest>=7,<10'
python -m pytest -q tests/test_chapter19_lab.py
python chapters/ch19-ai-agents/exercise_19_1_bounded_agent.py evaluate --output-dir outputs/ch19-evaluation
python chapters/ch19-ai-agents/exercise_19_1_bounded_agent.py demo --output-dir outputs/ch19-demo
```

Each output directory must be new. Existing files are never overwritten. Choose a new suffix for repeat runs. The script itself uses only Python's standard library.

The demo ends `awaiting_approval`; inspect `outputs/ch19-demo/staging/demo.json` and `trajectories/demo.json`. Record the staged artifact SHA-256 shown in the demo's result. After reviewing, replace the placeholder in this **separate** command:

```bash
python chapters/ch19-ai-agents/exercise_19_1_bounded_agent.py approve --workspace outputs/ch19-demo --task-id demo --reviewer instructor --expected-sha256 REVIEWED_SHA256
```

Promotion writes `derivatives/demo.json` and an approval record. Repeating the identical approval returns `already_promoted`. Reviewer names simulate a trusted identity; they do not authenticate the person running the command. A model cannot invoke promotion through the four-tool registry. A production service must enforce that separation through real identities, service permissions, and authenticated review.

## Data and scientific contract

The repository's script is the public data source: it generates two six-participant derivative fixtures, version `synthetic-1`. No external data or participant information is included. Each fixture contains sampling rate 128 Hz, band 8–12 Hz, units `uV^2`, six unique synthetic IDs, QC flags, and deterministic positive values. The mean is **13.5 uV²** for study A and **17.5 uV²** for study B. These numbers are hand-constructed derivatives, not power computed from real or simulated waveforms, and not evidence of disease or treatment effects. Sampling rate and units are contract-check fixtures. Chapter 13 owns actual PSD estimation.

These are original synthetic fixtures generated for this textbook; no third-party recordings or data license applies. The repository currently has no LICENSE file, so do not assume that public availability grants unrestricted code redistribution. Cite the textbook chapter, this script's repository revision, and `neurobridge-agent-lab-1.0`. For a real-data extension, use the separately licensed [PhysioNet EEG Motor Movement/Imagery Database v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/) and its acquisition notes in earlier labs. The dataset DOI is 10.13026/C28G6P and its data license is Open Data Commons Attribution v1.0. Cite Schalk (2009), the BCI2000 paper, and PhysioNet as requested on that page. Retain its license and provenance; do not copy protected data into Git. No external dataset is used by the default lab.

## Architecture and artifacts

The registered tools are `list_datasets`, `retrieve_sop`, `read_qc`, and `run_approved_summary`. Exact-key/type validators implement these small schemas; `tool_schemas.json` exports their JSON Schema descriptions. Dataset IDs map to trusted catalog entries, never model-supplied paths. `read_qc` checks source hashes, participant coverage, units, recipe, and finite nonnegative values. Staging requires verified retrieval and QC **for the same dataset**. Its numerical values are computed from verified source rows, not supplied by the planner.

Each fixture folder contains `sources/`, `catalog.json`, `policy.json`, `corpus.json`, `tool_schemas.json`, and a trajectory. Successful requests also create `staging/`. A separate authorized review is required for `derivatives/` and `approvals/`. Policy and corpus hashes, source hashes, result hashes, named tool events, denial/failure reasons, attempt counts, retries, and latency support inspection. `evaluation.csv`, `evaluation_report.json`, and `agent_card.md` summarize the exercise. Logs contain no hidden model reasoning.

Retrieval is a registered-document lookup with document IDs, versions, and hashes; it is **not** embedding search or an implemented RAG generator. The hostile-document case retrieves malicious text and then explicitly supplies a compromised deletion proposal. This demonstrates capability enforcement under that proposal, not that a model ignored the instruction. Summaries are structured artifacts, not generated clinical narratives.

## Evaluation and interpretation

The 24 tasks cover six ordinary summaries, nine malformed/forbidden proposals, wrong-study access, unknown identity, one transient failure, one persistent failure, wrong units, wrong participant coverage, missing evidence, budget exhaustion, and indirect injection. There are 12 adversarial fixtures. Seven legitimate tasks should stage verified summaries, 12 tasks should be denied, four should fail without staging, and one should exhaust its attempt budget. The expected means and terminal outcomes are checked independently; source integrity and absence of agent-created final derivatives are inspected.

Report correct-disposition count separately from legitimate-task completion, forbidden effects, and recovery. A safe refusal is correct for a forbidden request, but fails an authorized task if unwarranted. One recovered transient fault is **1/1 scripted case**, not an estimated population recovery rate. All 24 passing is fixture coverage, not a clinical validation or a security guarantee. Deterministic fixtures cannot support a binomial population confidence claim. Timing is local, variable, excludes setup, and is incomparable with live-model token/compute cost.

## Assignment (100 points)

1. **Contracts and trace (20):** run the tests and evaluation; annotate one staged and one denied trajectory. Identify which component proposed, authorized, executed, and verified each step.
2. **Scientific evidence (20):** independently calculate both means; inspect participant IDs, units, recipe, source and corpus hashes. Explain what the synthetic numbers cannot establish.
3. **Failure and budgets (20):** compare transient, persistent, missing-evidence, and looping tasks. Demonstrate that failure is explicit and no report is fabricated; state the attempt/retry denominators.
4. **Review integrity (20):** review and promote the demo, repeat the approval, and use a new demo folder to show that changing a staged byte or source/policy/corpus revision rejects stale review. Include the failed and successful records.
5. **Evaluation and agent card (20):** submit source revision, evaluation table, traces, tool schemas, policy, approval evidence, agent card, and a short reflection. Add a control diagram showing the agent's staging boundary and the reviewer's promotion boundary.

## Graduate extension

Replace the planner stub with a pinned local model over synthetic data only. Keep the runtime validators and tool permissions intact. Compare it with the stub and a fixed workflow on held-out tasks, repeated trials, and matched budgets. Report forbidden proposals separately from effects, evidence support, unnecessary denials, safe completion, retry recovery, latency distributions, and actual token cost. A multi-agent variant must justify specialization and use typed versioned handoffs; shared-model agreement is not independent replication. Do not weaken controls to make an attack demonstration appear more dramatic.

## Practical limits

This is a single-process educational reference, **not a hardened sandbox or clinical service**. Local policy/corpus/catalog files are trust anchors; a process that can rewrite them or the script can defeat the controls. Path containment rejects traversal and existing symlinks, but does not eliminate adversarial filesystem races. Exclusive file creation and content matching illustrate idempotency, but promotion plus logging is not a crash-safe cross-file transaction. There is no real authentication, signed audit ledger, approval expiration, time budget, OS isolation, external job reconciliation, or cancellation service. Production systems need these controls according to their intended use. Preserve staging/final separation even in an extension.
