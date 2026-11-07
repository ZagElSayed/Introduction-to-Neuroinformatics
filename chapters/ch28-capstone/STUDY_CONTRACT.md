# Study contract — Chapter 28 capstone

## Intended use and information boundary

This is a standard-library, in-process teaching simulator for **invented quality-review recipes**. It studies traceability and specified fault responses. It establishes no neurological construct, artifact-reference validity, treatment effect, device safety, production security, or clinical benefit. No actual network, hardware, API server, authentication service, or cloud resource is used.

## Data and labels

- Seed: **2801**. There are **24 invented people**, partitioned before fitting: 12 development, six validation, six evaluation.
- Two independently constructed records per person yield **48 records**. The fixture does not model longitudinal physiological change or hospital transport.
- Two channels (`toy-left`, `toy-right`), 128 Hz, two seconds, 256 samples per channel, arbitrary units, recipe `capstone-v1`.
- Each channel contains a 6 Hz sinusoid with shared record-level phase/gain and a channel phase offset. Gaussian noise standard deviation is 0.08 for label 0 or 0.8 for label 1. Phase and gain vary across records.
- Labels denote the assigned recipe. They are stored separately and enter development fitting or offline evaluation, never the inference request.
- The split audit checks known participant IDs, repeated record IDs, and declared partitions. It is not a waveform-duplicate or re-identification detector.

## Fitting and evaluation

The feature is the sum of squared adjacent-sample differences over both channels divided by `2 * 255`. Its unit is arbitrary-unit squared. The threshold is the midpoint of the two **development-label group mean features**. If the expected group ordering is absent, fitting rejects the recipe instead of silently reversing the intended mapping.

All 12 development people provide fitting labels. Validation and evaluation do not select the threshold, an operating rule, or any model setting. There is no fitted normalizer, neural model, probability calibrator, or confidence estimate. A model ID hashes its canonical JSON payload excluding that ID. IDs identify compatible bytes within the exercise, not a trusted origin.

Metrics are reported separately for all three partitions. Accuracy uses accepted records; coverage uses all intended records. Person counts accompany record counts. Repeated records remain dependent; there are no confidence intervals, subgroup claims, calibrated probabilities, site-transport results, clinical outcomes, or promised performance. Once evaluation results affect redesign, they are development evidence for that redesign.

## Virtual request contract

`NOW=1000.0` is an invented time in seconds, not host time. Default observations are at 998 s and availability at 999 s. Maximum age is 5 s; maximum declared clock uncertainty is 0.05 s. Equality is accepted. Timestamps must be finite, correctly ordered, and available by the request time; negative uncertainty is invalid.

The helper checks, in order: declared role; simulated network flag; artifact digest/schema and requested version; signal schema/shape/finite samples; timing; declared quality state. It returns the first failing reason. Exact schema equality rejects unsupported units/rates/recipes without conversion. Missing channels reject rather than being filled. A quality hold is explicit metadata, not inferred physiology or an automatic drift alarm.

Accepted predictions produce simulated `technical_review` or `continue_review_pipeline` labels. Refusals have status `abstained`, no prediction or feature, a reason, and simulated `hold_for_review`. These are research labels, never physical commands or clinical decisions. UUID trace IDs change across calls. No request-latency or device-deadline measurement is implemented.

## Fault scenarios and restoration

Ten request scenarios change missing-channel data, age, future availability, clock uncertainty, units, a non-finite sample, declared quality, role, network availability, or requested model ID. A separate audit introduces cross-partition participant overlap with a new record ID. A final restored request reuses the original eligible input.

Inspect observed results after execution. The flags do not prove a real access-control or network boundary; the overlap check is not a security test. Restoration is stateless request behavior, not incident memory, independent safety supervision, physical failover, or approval of a changed release. These are future implementation and evaluation questions.

## Export and provenance

Each export creates a new directory. It contains records, labels, model, report, fault results, manifest, local HTML evidence card, and receipt. The manifest records seed, schema, virtual policy, Python version, and helper SHA-256. The receipt hashes other exported files and excludes itself. It supports byte comparison but not trusted distribution, tamper-proof storage, or privacy protection. If an adversary can replace the receipt and files, matching hashes do not authenticate them.

Host timestamps, UUIDs, and trace IDs make repeated exports nonidentical. Reconstruct inputs and decisions from the saved records and frozen model rather than expecting a byte-identical rerun. Preserve a first export, modify only a copy for the receipt exercise, and record which comparison changed.

## Authoring and future studies

The authors inspected source, structure, and cross-file consistency without executing the helper or notebook. Students run and report their own observations. A public-data adapter, new feature/model, uncertainty method, or real service is a separately specified extension with new evidence obligations. An implementation or prospective-study proposal must not be described as an executed clinical study.
