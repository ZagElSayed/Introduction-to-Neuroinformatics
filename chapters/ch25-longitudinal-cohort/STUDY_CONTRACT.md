# Study contract: ch25-cohort-v1

## Question and scope

Investigate whether optional imaging adds information to a transparent predictor of a fabricated 90-day binary event, while preserving which input information was available at the index encounter. This is a synthetic information-engineering exercise with adult-like ages, not a model of any disorder or a clinical study.

The default seed is 2501. `make_fixture(n_per_cohort=80, seed=2501)` permits 20–120 participants per cohort. It uses a local seeded pseudorandom generator and returns an in-memory SQLite connection. Record Python version, parameters, exact helper hash, and the exported fixture; do not assume bit-identical reproduction across all future runtimes.

## Entities and clocks

- Person: invented ID, site, cohort, artificial G1/G2 group, age at the single index.
- Encounter: participant, relative day, and history/recent/index role.
- Acquisition: encounter, modality, device, observed day, available day, quality flag, and missingness reason.
- Derivative: acquisition, numeric value or explicit absence, arbitrary units, and recipe.
- Medication: participant, nominal start/stop, available day, and toy-agent identity.
- Outcome: one observed binary reference per participant, observation and availability times, and versioned definition.

Each participant has three encounters. Two neural derivatives precede index, at index−30 and index−3; their availability days are index−29 and index−1. A future derivative at index+1 becomes available at index+2 and equals +5 or −5 according to the generated outcome. It is an intentional leakage trap, never a permitted feature.

Some MRI values are observed at index−1 but available at index+5. Others are observed at index−20 and available at index−10, or explicitly marked not measured. Missingness varies by artificial group and site. Every 13th participant within each cohort has both pre-index neural acquisitions marked poor quality. A future high-quality derivative must not rescue that participant's eligibility at index.

Every third participant has a toy medication starting index−7 but recorded as available index+3. These entries must not appear as known at index. This fixture demonstrates late documentation, not treatment effects.

The device identifier is `toy-device-<site>`; device and site are inseparable by design. Neural and imaging values are generated arbitrary numbers; no real acquisition or device performance is simulated.

## Cohort construction

There is exactly one index encounter per person. The as-of feature view admits a usable derivative only if:

1. Its observation lies in the closed interval [index−45, index].
2. Its available day is no later than index.
3. Its quality flag is true and its value is present.

The latest eligible acquisition per modality is selected, ordered by observation day and acquisition ID. Selected input references retain observation time, availability time, device, units, and recipe. This is a specified tie rule, not a universal rule for clinical records.

The required neural feature determines technical eligibility. Optional MRI absence remains `None` plus a reason and a `mri_missing` indicator. Known supplied missingness reasons are retained where available. These checks do not implement a clinical eligibility assessment or an unfamiliar-input detector. Age is a generated index attribute; it is not used as a timeless age in a repeated-index study.

## Outcome and partitions

The outcome is fabricated from latent neural/imaging quantities and a site-specific intercept using a Bernoulli draw. G1/G2 are artificial alternating labels, not demographics. Site shifts alter conditional event probabilities and MRI availability; this is not a controlled pure-prevalence-shift experiment. Outcomes are observed at index+90 and available at index+105. There is no censoring, competing risk, incomplete reference, or clinical adjudication.

Development index days start at 0, calibration at 365, and external at 730, with successive people one day apart. IDs are disjoint. Even at the maximum 120 participants/cohort, the prior cohort's last outcome is available before the next cohort's earliest index. This supports a reconstructed fit/freeze chronology; no prospective study was performed. Site and period change together, so their separate effects are not identified.

Reference labels are retrieved separately with `reference_labels`; feature construction and cards do not use them. Raw fixture and reference exports deliberately contain outcomes for assessment and reproducibility. Do not pass them as prediction features.

## Models and evaluation

Fit only eligible development records. The basic model uses age and neural value; the multimodal model adds MRI and its missingness indicator. Compute means and population standard deviations from observed development values only. Missing optional features use the development mean; zero standard deviation uses scale one. A wholly absent training feature uses mean zero and scale one, an explicit teaching fallback that should prompt discussion.

The ridge logistic optimizer starts weights at zero, uses 400 full-batch gradient steps, learning rate 0.1, and penalty 0.02 on non-intercept weights. Hyperparameters are fixed teaching choices, not optimized settings or convergence guarantees. Predictions use a bounded numerical sigmoid and the stored preprocessing configuration. No calibration mapping is fitted. A candidate probability is not automatically a reliable individual risk estimate.

Inspect the calibration cohort without changing models or policies. Evaluate the two frozen candidates externally at a prespecified 0.50 cutoff, with equality positive. This cutoff is not a clinical recommendation. Metrics are conditional on eligible people; pair them with all-person coverage and exclusion reasons. AUC uses half credit for tied event/non-event pairs. Brier is mean squared probability error, not pure calibration. Five equal-width calibration bins return `None` for empty-bin frequencies. No confidence intervals or individual risk intervals are supplied; explain that limitation rather than inventing them.

Compare missing-MRI stress results on the same eligible external participants. Artificially removing imaging is not equivalent to natural missingness. A predeclared comparison is descriptive evaluation, not evidence that a revised candidate selected after inspecting external outcomes will generalize.

## Export and limits

Exports use a new UTC timestamped directory without overwriting existing bundles. They preserve the normalized SQL fixture, extracted cohort, reference outcomes separately, model parameters, model-specific cards, summaries, environment metadata, and byte receipts. A card's SHA-256 identifies the serialized model configuration relative to a trusted reference; it does not authenticate an actor or make the output immutable.

The studio has no real EEG, imaging, clinical endpoint, identity system, authorization service, EHR connector, individual uncertainty interval, treatment-effect estimate, or clinical-impact evaluation. Those require additional data, expertise, and appropriate governance and evaluation.
