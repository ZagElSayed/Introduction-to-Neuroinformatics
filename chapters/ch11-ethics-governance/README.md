# Chapter 11 — Govern NeuroBridge

A **synthetic policy evaluator**, not authentication, enforcement, institutional approval, or a clinical system. Python 3.10+; the exercise uses the standard library. Source has been reviewed, but this revision's exercise and tests have **not been run**.

The revised evaluator checks identity state, project, purpose, grant expiry, role/action, resource/action, and destination-specific export approval. The caller cannot supply a role or an approval flag to grant itself permission. Trusted registries are local fixtures that simulate authoritative server-side context; they do not verify a real person.

## Run locally

From the repository root:

```bash
cd chapters/ch11-ethics-governance
python exercise_11_1_policy_audit.py --output-dir ../../outputs/ch11
```

Use a fresh output directory, including when upgrading an older lab. Existing nonempty directories are rejected so an earlier decision history is not overwritten. Use a different directory for each experiment. No real participant files, passwords, tokens, names, or clinical data are needed.

For optional tests, return to the repository root:

```bash
python -m pip install pytest
python -m pytest -q tests/test_chapter11_lab.py
```

No GitHub execution is required. Record only local outcomes you actually observe.

## Read the artifacts

| Artifact | What it describes |
|---|---|
| `asset_inventory.csv` | Four synthetic resources, classifications, owners, projects, retention dependencies |
| `role_policy.json` | Policy version, role/resource rules, trusted principal and export-approval fixtures |
| `synthetic_requests.json` | Fourteen cases with separate requests and expected decisions |
| `threat_model.json` | Five scenarios with impacts, prevention, detection, response, and residual risk |
| `audit_events.json` | Decisions, reason codes, actor/resource references, purpose/project, policy identity, and correlation ID |
| `governance_summary.json` | Observed allow/deny counts, expectation mismatches, policy/code identity, and scope limitations |

`policy_as_of` is the fixed simulated clock `2026-01-01T12:00:00+00:00`. `observed_utc` is when your script actually evaluated a case. An expiry equal to the simulated decision time is expired. These example grant lifetimes are policy choices, not a claim that every research authorization must expire after a fixed interval.

The supplied cases are designed for **4 allow and 10 deny decisions**; verify that locally. Expected answers are used only for comparison after evaluation, never to choose the policy result. An expected denial does not make the exercise fail. An unexpected result makes summary status `failed` and command exit status 1. Ordinary filesystem errors can leave incomplete evidence; do not infer success from folder existence.

The policy digest hashes the sorted-key JSON representation used in the source, not the formatted bytes of `role_policy.json`. It identifies fixture content, not an authenticated or tamper-resistant policy authority. A UUID links one run's audit events; the evaluator does not perform a real read, write, or export. An allow decision is not evidence that the operation completed.

## Trace one request

1. Check the request schema; unknown authority-bearing fields such as `role` are rejected.
2. Resolve `actor_id` in the simulated trusted principal registry.
3. Require verified/active identity state and an unexpired grant.
4. Match resource and principal project, and check the approved purpose.
5. Require both role/action and resource/action permission.
6. For export, require a matching active, unexpired approval for that actor, action, resource, purpose, project, and destination.
7. Return allow/deny with a reason and retain the decision context.

The identity-linkage resource intentionally has no granted action. A real institution can have an approved relinking workflow; it is outside these grants. Unknown identities, missing context, wrong projects/purposes, expired or revoked grants, incompatible actions, and unapproved exports are denied.

## Assignment — 100 points

1. **Assets and classification (15):** Explain why raw EEG, derivatives, identity mapping, and audit records have different protection needs. Identify a responsible owner and retention dependencies. Distinguish pseudonymization from a formal de-identification determination.
2. **Policy decisions (25):** Trace the fourteen cases using evidence and reason codes. Explain why verified identity or a permissive role alone is insufficient. Compare an allowed derivative read with unapproved purpose, wrong project, and expired grant. Explain the separate export approval.
3. **Boundary and negative checks (15):** In isolated experiments, test a forged role, missing purpose/project, false authentication context, approval at its expiry boundary, revoked export approval, and an incompatible resource/action. Record actual outcomes and add one meaningful local test. Do not treat changing trusted fixtures as something an untrusted client may do.
4. **Threat and privacy reasoning (20):** Expand one scenario with asset, actor or accidental cause, entry point, trust boundary, CIA consequence, preventive/detective control, containment, scientific verification, residual risk, and owner. Explain why a signed container or encrypted export can still violate the intended method or data-use conditions.
5. **Audit and accountability (15):** Link requests, decisions, policy version/digest, reason, observed time, simulated time, and correlation ID. Identify sensitive fields to exclude. Explain why ordinary JSON and hashes do not create an authentic tamper-resistant audit trail, and why a decision log differs from completed-operation evidence.
6. **Clinical/AI governance (10):** Complete the model/intended-use and safe-state portions of the governance template. Cover unavailable service, unsupported input, unapproved version, stale results, and human escalation. Explain which institutional permissions and technical enforcement are absent from the lab.

## GitHub submission and handoff

Submit your implementation commit, six small synthetic artifacts, a trust-boundary diagram, a decision-trace report, a negative-case demonstration, and a completed [GOVERNANCE_TEMPLATE.md](GOVERNANCE_TEMPLATE.md). Include Python version, local verification command and actual outcome, unresolved issues, and the distinction between implemented simulation and proposed production controls. Exclude credentials, environments, caches, and clinical data.

The template supports NeuroBridge Milestone 3: policy authority, scope, owner, enforcement points, audit responsibilities, model governance, incident response, and residual risk. It does not issue an IRB, legal, security, or clinical approval.

## Limits and further work

The program has no real identity provider, session/token verification, external policy service, enforcement gateway, encryption/key management, secure audit store, participant-level consent database, distributed revocation, or clinical integration. Its project-level purpose restriction is simpler than participant-level data-use governance. Every access route would need enforcement in a production system; a dashboard-only check is insufficient.

For a graduate extension, design three-site controlled-enclave or federated computation governance. Address model/update leakage, site and participant restrictions, versioned policy, stale approvals, downstream copies, incident ownership, and verification of intended use. Raw-data locality alone does not eliminate privacy risk.

See [RESOURCES.md](RESOURCES.md) for primary readings and connections to the chapter.
