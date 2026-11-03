# Study contract — ch26-precision-v1

## Purpose and claims

This is an invented information-handling exercise. It demonstrates temporal eligibility, personal references, shared prediction, randomized group contrasts, and explicit software release states. It is not an N-of-1 clinical trial, a SMART, a digital twin, a validated dynamic treatment regime, or a neurological disease simulator. The longitudinal and randomized experiments have different outcomes and must be interpreted separately.

## People, windows, and time

Default seed: `2601`. Default cohort size: 60 people each in development, validation, and evaluation; permitted sizes: 24–120 each. IDs are disjoint (`d-*`, `v-*`, `e-*`), with calendar offsets 0, 120, and 240. Each person has observations on relative days 0–36; decision rows use days 10–34. A person, rather than a window, is the independent sampling unit in this fixture. Repeated windows remain dependent observations.

Each observation includes `observed`, `available`, source identifier, person, device, firmware, recipe, units, quality flag, value, and a sleep indicator. The requested current record must have observation time exactly equal to the decision index and availability no later than that index. There is no substitution of a previous observation. Input dictionaries represent the declared synthetic schema; this compact helper is not a general ingestion validator for arbitrary files.

## Personal reference

Candidate days: 0–9; reference cutoff: cohort offset + 10. Include only available, finite, quality-eligible measurements from `toy-wrist`, firmware `v1`, recipe `toy-measure-v1`, units `arbitrary`. At least eight observations and descriptive SD ≥ 0.05 are required. SD uses divisor n. Failed references are explicitly insufficient. Successful references are frozen; later firmware changes do not trigger silent rebuilding. Current device, firmware, recipe, and units must match the reference.

The personal feature is `(value - frozen_mean) / frozen_sd`. It describes deviation under a compatible measurement contract, not disease probability. A toy absolute deviation > 8 is outside the declared domain. It is not a clinical threshold. Both raw and personal predictors use the same reference-eligible subset for a matched comparison.

## Longitudinal outcome and prediction

A fabricated next-day binary event uses the next day's generated latent physical state and sleep indicator. It is observed at index + 1 and becomes available at index + 3. The learner receives the current measurement and current sleep indicator only. Labels reside in `references`, outside the snapshot feature objects. The mechanism includes persistent latent physical shifts for some people, firmware-induced measurement offsets for others, missingness, delays, and quality faults. These mechanisms can overlap.

Two shared logistic fits use raw value plus sleep, or personal z plus sleep. Development decisions and reference availability must be no later than calendar cutoff 60. Feature means/scales use eligible development data only. The teaching optimizer uses 300 batch updates, learning rate 0.1, and L2 coefficient 0.02 excluding the intercept. It provides no convergence or optimality guarantee, no person-specific classifier, and no clinical calibration claim.

Validation and evaluation use the frozen models, with their own eligible pre-decision unlabeled personal baselines. Assessment occurs offline after references mature. Report all and eligible windows, all and eligible people, coverage, Brier score, AUC (undefined without both classes), and five equal-width calibration bins (undefined means in empty bins). No confidence intervals, individual calibration, decision-threshold optimization, or causal conclusion is supplied. A valid analysis must describe person-level dependence and eligibility losses.

## Separate one-step randomized utility experiment

Each person contributes one independent randomized observation, with action 0 or 1 assigned at probability 0.5. G1 has supplied baseline risk near 0.8 and gross utility effect 0.5; G2 has risk near 0.2 and gross effect 2.0. Burden is 0.4 or 2.5; net effect is gross effect minus burden. Expected comparator utility is `3 + 2 * baseline_risk`; observed utility adds a mean-zero noise term and, for action 1, the net effect. These are invented utility units, not disease probabilities validated in patients or treatment doses.

Development observations estimate action-1 minus action-0 mean utility in group/burden cells. Retain both arm counts; no contrast is available if either arm is empty. No confidence interval or individual causal identification is provided. The policy uses these frozen cell estimates on evaluation people. `baseline_risk` is a supplied variable in this experiment, not a longitudinal-model output.

At most `floor(0.25 * n)` people may be selected. Risk ranking selects the top budget; estimated utility ranking selects only positive estimated contrasts, up to budget. A separately labeled oracle ranks positive known net effects. Ties use person ID. Report selected counts because policies may use different amounts of the maximum budget. Known expected utility averages the constructed comparator expectation plus net effect for selected people. Potential outcomes and the oracle never enter fitting or deployable ranking features. Oracle scoring is a simulation-only reference.

## Abstract gain and fault handling

Initial gain: 0.3. Fixed envelope: [0,1], maximum step 0.1. An eligible absolute z > 1.5 proposes +0.15; otherwise it proposes the current gain. The limiter clips the proposal. Delivery requires explicit Boolean `release_allowed=True`; default false. This flag teaches permission handling and does not authenticate anybody. Pass `next_state` to preserve history. No stimulation, medication, or clinical command exists.

Invalid input generally yields `needs_review`. A measurement-version mismatch yields snapshot `freeze`, which becomes a latched `frozen` decision state. A subsequent eligible observation does not clear that latch. The helper implements no requalification/reset service. The six documented fault injections modify missing value, firmware, availability, extreme value, observation timestamp, or quality. Person `e-004`, day 18, provides the pre-change reference example.

## Export and reporting

`export_bundle` saves a new directory with models, reports, decisions, observations, reference outcomes, randomized trial, oracle, manifest, and a receipt hashing all other files. The manifest records seed, cohort size, Python version, and helper digest. Hashes support comparison, not authentication, confidentiality, or immutable storage. Record your own execution environment and results. No execution or numerical performance verification was performed during assistant authoring.
