# Study contract: a bounded Chapter 27 teaching experiment

## Question and target

Does masked pretraining change a frozen encoder's ability to distinguish two invented
waveform recipes, compared with the same randomly initialized encoder and a transparent
fixed-frequency baseline? This is not a neurological endpoint, diagnostic classifier,
foundation-model scaling experiment, or measurement of human physiology.

## Fixture and independence

Default seed: 2701. There are 24 invented people: 12 development, six validation,
six final evaluation. Each has two sessions, each with two non-overlapping four-second
windows. Total: 96 records. Labels alternate within each person's records so both
classes occur per person. Class 0 has a dominant 6-Hz component; class 1 has a dominant
14-Hz component. Noise, a 20-Hz component, gain, phase, and person offsets add variation.
Units are arbitrary and channel names are `toy-left`, `toy-right`.

Participant membership is assigned before generating windows. All splits use the same
invented recipe: no external hospital, disease, clinical outcome, device-transfer,
temporal-generalization, or independent biological validation is represented.
`split_audit` catches repeated record IDs and persons spanning partitions; it is not a
near-duplicate waveform detector or cross-database identity resolution system.

## Schema and tokenizer

128 Hz, 512 samples/channel, two ordered channels, `toy-common` reference, fixture-v1.
Each patch contains 32 samples (0.25 s); each record has 16 patches/channel, 32 tokens.
No padding or resampling is implemented. A declared missing channel uses `None` and
becomes zero tokens with validity false. Attention and pooling exclude invalid tokens.
All channels missing, unsupported schema/rate/units, non-finite values, and wrong
sample counts are rejected. Zero is not a substitute for declaring missingness.

Normalization uses a channel mean and descriptive standard deviation from all eligible
development records, with divisor equal to the number of values. It is then frozen for
validation and final evaluation. This is dataset-level scaling, not the personal
baseline of Chapter 26. Fit IDs accompany the normalizer.

## Optional neural experiment

CPU only; 16-dimensional embeddings; one transformer block; two heads; feed-forward
width 32; dropout zero; mean pooling over valid tokens. Channel and patch-position
embeddings are learned. Each pretraining step hides exactly 10 valid whole patches
per default record (31.25%); reconstruction loss uses only hidden sample values.
Defaults: 30 full-batch pretraining steps, Adam learning rate .003; 40 full-batch
classifier steps, Adam .01. These are fixed teaching schedules, not tuned optima.
Random/probe/scratch variants start from copies of one initial model. Probes train only
their linear head; the scratch variant updates the encoder and head. All 12 development
people contribute unlabeled pretraining inputs; the first six development IDs supply
labels for every classifier. The two-feature logistic baseline uses those same labels,
300 full-batch gradient steps, rate .3, a learned intercept, and no fitted feature scaling.

Validation is reported separately; no automatic tuning/early stopping uses it. Final
evaluation is excluded from normalization, pretraining, and supervised fitting. If you
change a recipe after reading final results, treat that cohort as development evidence
and create another independent final cohort. Total training compute is not matched:
the pretrained method receives an additional pretraining budget. No performance ordering
is promised. Seeds do not ensure bitwise identity across versions and platforms.

## Reporting and evidence exercise

Metrics describe pooled windows: accuracy at 0.5, Brier score, and five equal-width
positive-class probability bins. Empty bins have null means. Repeated records within
people are not independent; no default uncertainty interval is produced. Checkpoint
states, fit IDs, per-record predictions, schedules, timings, parameter count, versions,
and limitations are retained. Timings are local wall-clock measurements when students
run the code, not GPU utilization, energy, or an end-to-end deployment benchmark.

The core evidence exercise filters a tiny author-written collection by role and status,
then ranks token overlap. It checks source IDs and exact passage equality only.
Paraphrase, contradiction, missing sources, stale guidance, and scientific applicability
require review. Role strings and curated quarantine flags are teaching metadata, not
security controls or automatic attack detection. No language model, generation,
external retrieval, or clinical recommendation is implemented.

## Execution and export

Authoring inspection is static. Notebook code has not been executed on the user's
behalf. Students must report installation failures, results, null effects, and deviations.
The core export contains JSON artifacts and source/record manifests. Optional checkpoint
export adds a `.pt` file and its digest to the receipt. Digests support byte comparison,
not authenticity, privacy guarantees, immutability, or clinical validity.
