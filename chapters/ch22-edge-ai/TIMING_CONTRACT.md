# Timing contract — ch22-timing-v1

## Scope and units

This is a discrete-event **virtual timing model** with a small synthetic computation. Every `*_ms` field is assigned virtual time, not a duration measured on the host. No sleep, actual concurrency, device, radio, physical feedback, or trained model is present. Host Python version and helper SHA-256 identify the code context without turning its output into a hardware benchmark.

## Input and evidence interval

- Four deterministic sinusoidal channels at 100 Hz: channel `c` has frequency `7+c` Hz and value `sin(2*pi*(7+c)*t/1000)` at timestamp `t` ms.
- Samples start at 10 ms. A `deque(maxlen=40)` retains 40 multichannel samples. Every two additional samples form another window after the first full window.
- Each window has nominal support `(source_ms-400, source_ms]`; oldest and newest sample timestamps differ by 390 ms. Source times begin at 400 ms and advance by 20 ms.
- Default `n_windows=80`; window IDs are zero-based 0–79. The four features are mean squares, not band-power estimates or validated biomarkers. Their mean is thresholded at 0.5 to form a toy binary proposal, not a probability or clinical state.
- The core computes these numerical values directly in Python; the scheduler separately assigns hypothetical processing costs. No scientific accuracy endpoint or ground-truth labels are defined.

## Timing and service

Normal arrival is `source_ms+5`. Deadline is `source_ms+100`. All timestamps share one exact virtual domain: there is no clock mapping uncertainty in this exercise. Real clocks require mapping and an uncertainty account.

One worker executes one job nonpreemptively. Normal service is 6 ms preprocessing, 8 ms inference-like work, 2 ms release evaluation, and 4 ms virtual output, totaling 20 ms. Costs are fixed assumptions. `start_ms`, `pre_end_ms`, `infer_end_ms`, `gate_ms`, and `finish_ms` record these boundaries. `finish_ms` is the modeled output endpoint; rejected work has a modeled completion but no released command. The release rule reserves the four output milliseconds by checking this endpoint against expiry.

Completion precedes arrival on a tie. After completion the worker may dispatch already-waiting work before processing an arrival at that same time. This ordering is a deterministic modeling convention, not a property of an operating system.

## Queue policies

Capacity counts **waiting windows only**, excluding the running job. It is a positive integer. Both policies are bounded and leave running work untouched.

- `fifo`: take the first waiting arrival. If full, reject the new arrival with `overflow_drop_new`.
- `latest`: dispatch the waiting window with newest source time. If full, a newer arrival replaces the waiting window with oldest source time (`superseded`); an arrival no newer than that oldest window is rejected (`older_arrival_drop`). This is not LIFO cancellation of running work.

The notebook's main comparison is FIFO capacity 8 versus latest capacity 1. It changes two factors; a matched-capacity comparison is provided to investigate policy alone. Either can lose useful events. The generator retains all expected records for teaching accounting; the queue's bound is not a claim that all application memory is bounded by that capacity.

## Scenarios

| Scenario | Assigned events |
|---|---|
| `nominal` | Ordinary arrivals, valid quality, 8-ms inference cost. |
| `overload` | IDs 20–29 have 80-ms inference cost; arrival schedule is unchanged. |
| `faults` | Same overload plus ID 8 missing, ID 12 arrival at source+130 ms, and ID 15 quality false. |

These are **window-level** events, not lost individual EEG samples. No raw-signal gap handling, filter state reset, wireless stack, cloud service, or thermal model is implemented. Inference budget defaults to 40 ms. A call that exceeds it still occupies the worker for its full assigned cost, then receives `inference_timeout` at completion. There is no independent watchdog or early cancellation.

## Admission, release, and rejection priorities

At arrival: reject invalid quality, then already-expired evidence; otherwise apply queue capacity/policy. At dispatch: reject a window already expired before starting. Equality with the deadline is not expired, although later completion can still be late.

At completion: reject inference cost above its budget, then output after the deadline, then source time no newer than the last released result. Otherwise release binary command 0 or 1 and update the last released source time. These statuses are mutually exclusive terminal reasons. A job can finish late and have timeout as its terminal reason; the separate `completed_late` count exposes that overlap.

Rejection sets no new command (`command=None`). It does not hold, stop, or reset a physical device and does not define a clinical fallback. There are no human permissions, manual-stop scenario, model replacement, or configuration race events in this core. Those are development extensions.

## Metrics and denominators

Every expected window has one final status, including the missing ID. `status_counts` sums to `expected_windows`. Waiting and outcome events are separate records, so counting events is not counting terminal windows.

- `completed_jobs`: jobs with a modeled finish timestamp, including timeout and late completions.
- `completed_age_p50_ms`, p95, p99: nearest-rank percentiles of `finish_ms-source_ms` for completed jobs only; `None` for an empty completion set. These are not host measurements or all-window outcomes.
- `completed_late`: completed jobs whose modeled finish exceeds expiry, regardless of terminal reason.
- `on_time_release_fraction`: released windows divided by all expected windows.
- `no_on_time_release_fraction`: its complement. Missing, invalid, replaced, dropped, expired, timed-out, or out-of-order work is not thereby labeled completed-late.
- `max_waiting`: largest observed waiting count, not total in-flight jobs, memory usage, or archival size.

The helper reports no learned-task accuracy, calibration, real memory peak, real energy, wall-clock throughput, clinical outcome, or hard real-time guarantee.

## Student audit and bundle

`audit` checks final accounting, event queue bounds, release ordering, deadlines, inference budgets, and no command for rejected records. It is a student-run invariant check, not an independent validation of its generator or hardware. No run results are supplied.

`save_bundle` writes a unique JSON file with finite JSON values and a SHA-256 sidecar. The receipt identifies bytes; it is not an authenticated signature, access control, or immutable storage. Preserve baseline identity before extending the code and explicitly label new versions and claims.

## Optional measured extension

Replace assigned costs with instrumented processing and define input, release, and output events. Use a host-local monotonic counter for elapsed durations, map source clocks if different, synchronize asynchronous device completion where required, and report observation counts. A host return event is not measured display onset. Use a task-valid neural dataset and held-out evaluation if claiming neural-decoder quality. Quantization requires a real transformed artifact and task re-evaluation; energy and physical timing require corresponding instruments.
