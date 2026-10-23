# Simulation contract — Chapter 21

Version: `ch21-sandbox-1.0`. Read alongside `adaptive_sandbox.py`.

## Process and timing

At tick t, the simulator obtains y[t] = x[t] + observation_noise[t], calls the controller, issues u[t], applies u[t-delay_steps], and advances:

x[t+1] = a*x[t] + drift - action_effect*u[t-delay_steps] + disturbance[t] + process_noise[t].

Defaults: 240 ticks, x[0]=1, a=0.96, drift=0.04, action_effect=0.08, delay_steps=2. Prehistory actions are zero. Disturbance is 0.015 during ticks 80–119 and zero otherwise. Process noise has standard deviation 0.01; observation noise 0.04. A seeded Python Random generator draws both full sequences in a fixed order before rollout, so policies with the same seed share exogenous draws. Their later states and measurements can differ.

All quantities are dimensionless or virtual timing quantities. Ticks are not physiological seconds. The age field is a scripted input, without queue dynamics, network measurement, operating-system scheduling, or wall-clock pacing.

## Information boundary

Controller.step receives measurement, age, and stop only. It never receives the latent state, future noise, disturbance schedule, or an outcome label. Audit-only state and exogenous values remain in the simulator's row records.

This scalar process is a chosen model, not neural data or a model fitted to a patient. A changed policy must rerun the process for a counterfactual outcome inside that model. Reusing an old measurement trace reconstructs decisions on an old trajectory only.

## Estimation and fixed policy

The first valid measurement initializes the estimate; later values use EMA alpha=0.25. Three consecutive valid observations are required for ACTIVE mode, including the initial valid observation. Thus the first two are WARMUP. The smoother has no calibrated uncertainty estimate.

Target=0.60, target half-width=0.15. Proposed action = gain*(estimate-target). Positive action lowers the toy state. The fixed gain is 1.0. ACTIVE requests are clipped to [0,1], then limited to a change of 0.10 from the previous issued action.

## Bounded gain adaptation

The adaptive variant begins at gain 1.0. Every 20 eligible ACTIVE estimated errors, it takes their mean. Above +0.05 it increases gain by 0.10; below -0.05 it decreases by 0.10; otherwise it leaves gain unchanged. Gains are clipped to [0.50,2.0]. A revised gain affects subsequent decisions; gain_used and gain_next are separate row fields.

The rule is a deterministic teaching heuristic, not a contextual bandit, RL optimizer, or guaranteed improvement. It does not change supervisor bounds and does not use latent audit state. Correlated errors do not become 20 independent observations.

## Eligibility, faults, stop, recovery

Invalid conditions: missing measurement, nonfinite measurement, invalid/negative/over-limit age, or measurement magnitude above 3.0. Default maximum age is 0.50 virtual units. These checks are not validated EEG artifact detection.

With faults=True:
- Tick 40: measurement is missing.
- Tick 80: age becomes 0.75.
- Tick 120: measurement becomes 5.0 (artifact proxy).
- Ticks 160–164: manual stop is asserted.

Priority: manual stop before other measurement issues. Invalid input returns FALLBACK; stop returns STOPPED. Both issue zero immediately, clear estimator/readiness/partial error block, and retain bounded gain. Their immediate zero **overrides the normal slew limit**. On valid resumption, the first two observations are WARMUP; the third is eligible for ACTIVE mode.

Earlier actions continue through the delay history. Zero issued output does not imply instant zero applied action or instant state recovery. No claim is made that this fallback is suitable for a real intervention.

## Records and metrics

Rows retain tick, input/age/stop/fault, mode/reason, estimate, proposed and issued action (field name delivered), delayed applied action, gain used/next, adaptation/limiting flags, and audit-only process values. Here delivered means issued to a virtual actuator, not measured physical delivery.

Summary denominators include all steps for latent mean absolute error and target-band fraction. Active coverage is separate. Other fields include normalized action sum, total variation (including changes from initial zero and emergency fallback), limited-step count, gain updates, and warmup/fallback/stop counts. Limited means proposal differed from issue; it does not necessarily mean a hardware fault. Toy burden is not electrical energy, clinical dose, or harm.

Development seeds: 21–23. Final seeds: 121–125 after procedural freeze. The default final set changes noise realizations while retaining process and fault schedules; claims remain within that scenario family. New delay/dynamics experiments need declared development and held-out scenarios.

## Reconstruction and storage

reconstruct repeats controller decisions from saved observations/configuration and matching helper version. audit compares the decision fields, checks action/gain bounds, requires non-ACTIVE outputs to be zero, and checks slew in ACTIVE mode. It does not independently validate the biological process, physical device, or clinical envelope.

save_bundle writes a unique JSON file, rejecting nonfinite JSON values, and returns its SHA-256. The receipt identifies content; it does not authenticate a user or make storage immutable. Preserve config, helper identity, inputs, environment, outputs, and observed audit results together.

## Evidence limit

AST/syntax and contract inspection were performed during authoring; no simulator or notebook was executed. Students must run and report their own results. Even passing numerical checks does not establish analytical stability, real-time deadlines, a neural biomarker, human learning, device protection, or clinical benefit.
