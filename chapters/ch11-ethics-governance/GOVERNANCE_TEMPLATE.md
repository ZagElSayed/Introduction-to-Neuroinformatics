# NeuroBridge Phase III — Governance Handoff

Use hypothetical/synthetic content only. This is a design and evidence template, not approval to use data or deploy clinical software.

## Purpose, authority, and scope

| Field | Your entry |
|---|---|
| Intended use and excluded uses | |
| Population, study/project, resources | |
| Data owner / scientific lead / policy authority | |
| Applicable institutional determination and governing documents | |
| Consent / authorization / data-use dependencies | |
| Approval version, validity, review/revocation route | |
| Participant-level restrictions not modeled by the teaching code | |

## Data, identities, and boundaries

List raw recordings, derivatives, identity linkage, audit records, and model artifacts. State sensitivity, necessary fields, ownership, storage locations, recipients, and retention dependencies. Draw identity, data, compute, and institutional boundaries. Do not include actual identifiers or secrets.

Describe the actual identity-verification mechanism required in production. For the lab, state explicitly that trusted principal records are fixtures. Separate subject identifiers from credentials.

## Policy and enforcement

| Actor/function | Action/resource | Purpose/project | Additional conditions | Enforcement point | Owner |
|---|---|---|---|---|---|
| Analyst | | | | | |
| Workflow service | | | | | |
| Data steward | | | | | |
| External collaborator | | | | | |

Document unknown/missing-context behavior, grant expiry, revocation, destination-specific export approval, and why request fields cannot create their own authority. Identify alternative access paths that a dashboard-only check would miss. Explain how decisions and completed operations are linked but separately evidenced.

## Privacy and change in permitted use

Describe data minimization, necessary linkage, approved outputs, copy tracking, and review of small/rare groups. For withdrawal or changed permission, identify affected data and the authorized decision process for future use, existing copies, derivatives, and retention obligations. Do not promise universal deletion that the architecture cannot support.

## Threat scenario and residual risk

| Field | Your entry |
|---|---|
| Asset / actor or accidental cause / entry point | |
| Trust boundary / confidentiality, integrity, availability impact | |
| Preventive control / detective evidence | |
| Containment / scientific verification / recovery | |
| Residual risk / uncertainty / responsible reviewer | |

If using a likelihood × impact priority score, state the scales and assumptions. It is not a measured probability or authorization override.

## Model and human oversight

Specify intended use, input requirements, model/code version, validation population, calibration/subgroup limitations, owner, monitoring, and change-control process. Define visible safe states for unavailable service, unsupported input, stale output, and unexpected versions. Identify who has authority and sufficient information to intervene.

## Audit and incident route

Record event/correlation IDs, actor/action/resource references, project/purpose, decision/reason, policy version, and relevant timing. State who can access/review audit evidence, how integrity and retention would be protected, and what must not be logged. Local JSON does not implement those protections.

Name the incident lead and relevant scientific, privacy/security, and clinical owners. Document containment, evidence preservation, affected-version/output reconciliation, verified recovery, notification through institutional processes, and the decision to resume use.

## Local verification record

List only commands actually run, Python version, observed decisions, negative-case outcomes, and unresolved failures. Link your code commit, synthetic artifacts, diagram, and report. Mark unexecuted checks **not run**. Distinguish implemented evaluator behavior from proposed production enforcement and institutional approval.
