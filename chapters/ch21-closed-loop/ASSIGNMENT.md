# Chapter 21 assignment — 100 points

Build a small, inspectable feedback loop and defend the claim its evidence supports. Start with the guided notebook and SIMULATION_CONTRACT.md. No minimum accuracy, tracking score, or adaptive advantage is required.

| Criterion | Points | Evidence expected |
|---|---:|---|
| Process and measurement | 20 | Explain causal tick order, units, response sign, hidden-state boundary, smoothing, initialization, and the distinction from recorded-data replay. |
| Controller and adaptation | 20 | Trace a proposal through bounds/slew to issue and delayed application; explain gain updates, deadband, valid blocks, and parameters that stay fixed. |
| Fixed/adaptive comparison | 20 | Document development choices, freeze the procedure, retain per-seed final results, report all-step outcomes, active coverage, burden, variation, and tradeoffs without selecting favorable rollouts. |
| Faults and reconstruction | 20 | Report injected faults, modes, stop/recovery, pending actions, student-run audit outcomes, exact decision reconstruction, and unique bundle receipts. Explain what each check can and cannot establish. |
| Scientific report and system card | 20 | Connect observed findings to the declared question, disclose limitations and model assumptions, preserve versions, and propose a justified next experiment. |

For each category, full credit requires correct reasoning, observed artifacts, and a coherent explanation. Mostly correct work with one substantial omission earns 12–17; partial or inconsistent work 5–11; unsupported claims or absent evidence 0–4. Strong analysis of a poor-performing controller can earn full credit.

## Submit

- Notebook with your observed outputs and a separately versioned implementation if you extended it.
- Configuration and helper identity, development notes, procedural freeze record, and final scenario manifest.
- Per-rollout metric table including unsuccessful runs; plots identifying measurements, estimates, latent audit state, issued/applied actions, and gain.
- One normal-decision trace and one fault/stop/recovery trace.
- Saved JSON bundles with receipts and reported audit outcomes.
- A short scientific report and the system card below.

The starter notebook intentionally keeps outputs empty and FROZEN=False. The final cell requires your documented freeze. Do not describe authoring-time AST checks as successful simulation tests.

## System card template

1. Intended teaching use and prohibited interpretations.
2. Process equation, coefficients, virtual timing, response direction, and uncertainty in biological transfer.
3. Measurement interface, estimator, eligibility, initialization, and resets.
4. Fixed policy and adaptive rule, state, update schedule, bounds, and gain versions.
5. Supervisor, stop/fallback priority, slew exception, and recovery.
6. Scenario scope, development/final seeds, metrics and denominators.
7. Observed comparison, variability, failures, and burden.
8. Provenance, storage, reconstruction, and missing security controls.
9. Claims supported and at least four claims not supported.
10. Next experiment and the specific new claim it would address.

## Reflection

- Why can matching noise seeds produce different later measurements under different policies?
- Which metrics use latent audit information, and why is it excluded from decisions?
- What happens to pending actions after a stop?
- How could adaptation optimize tracking while increasing another burden?
- Why is a file checksum different from authorization?
- What evidence would be required for a human biomarker, physical latency, or clinical-benefit claim?
