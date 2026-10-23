# Data, computation, control, and evaluation contract

## Source and split
PhysioNet EEGMMIDB version 1.0.0; S001 runs 04/08/12 only. T0=instructed rest, T1=imagined left fist, T2=imagined right fist for these runs. R04 trains; R08 is development/validation; R12 is the final locked run. No cross-participant or cross-session generalization is established. Loader checks a 160-Hz sample rate, zero sample origin, C3/Cz/C4 availability, finite values, and known annotations. MNE returns volts; no silent resampling or unit guessing. Selected channels retain the recording reference; no learned rereferencing or artifact removal is fitted.

## Causal computation
Fourth-order Butterworth 7–30-Hz bandpass in SOS form; zero initial filter state per run and after a discontinuity. The offline trial path filters a run forward once; replay retains SOS state between 40-sample (250-ms) chunks. No backward/zero-phase filter or future samples are used. The bounded rolling buffer retains at most 320 samples (2 s) after each update. Reset requires a fresh complete window before inference. Real hardware may need an additional empirically specified settling interval.

Six features: C3/Cz/C4 × 8–12 and 13–30 Hz, flattened channel-first. A 320-sample symmetric Hann window, mean removal, one-segment Welch density, 0.5-Hz bins, inclusive band edges, and bin sum × df yield V²; a floor of 1e-30 precedes log10. This convention is explicit, not an assertion that inclusive boundaries or those bands are universally optimal. StandardScaler and binary logistic regression (C=1, max_iter=1000) fit R04 only. One [.5,2.5)-s segment per eligible task cue is used for trial-level scores.

## Command policy and QC
Replay knows no task labels until after its command is decided. A two-class model cannot infer a genuine no-control class. Gating uses the maximum model score ≥ .70, three consecutive same-class updates, and a 1-s refractory period; no command=0, left=-1, right=+1. The first to third overlapping updates are 0.5 s apart, and they are correlated. Scores are not empirically calibrated confidence in intent.

Packet QC rejects nonfinite data, absolute amplitude above 150 µV in a selected channel, or any selected channel's standard deviation below 1 nV in the packet. These teaching values are neither validated artifact thresholds nor a medical safety specification. Stale virtual packets (> .50 s age), sample-index gaps, and failed QC reset filter, buffer, and dwell evidence, discard the current chunk, and inhibit both comparators. The refractory time is retained. Both comparators update a local cursor bounded to [-10,10]; there is no physical actuator.

## Faults and clocks
Development injections: drop one 40-sample chunk beginning at 20 s; add .75 s virtual arrival delay at 30 s; flatten C3 for one chunk at 40 s. A dropped packet is recognized on the next observed sample-index discontinuity. The virtual arrival clock never decreases; queued packets may arrive at the stalled clock until recorded time catches up. This simplified simulation does not model a full transport stack, reorder buffer, or real network.

`sample_time` is the last sample's time in the source file. `arrival_time` is simulated. `processing_ms` is measured local wall time for valid chunks from filtering through feature computation, inference, and both cursor updates, excluding audit-label lookup and log serialization. It is not acquisition-to-feedback latency, user response time, or a hard-deadline guarantee. No pacing sleep or live feedback loop is implemented.

## Scoring units and limits
Trial-level balanced accuracy uses one feature window per task cue. Continuous task-window accuracy uses only valid windows wholly inside a single T1/T2 interval; correlated windows are not independent trials. Conditional task-command accuracy includes only emitted commands with wholly task windows; report accepted count as well. Neither metric measures target acquisition or user task success.

The instructed-rest command proxy includes commands at valid updates whose complete feature window is wholly within one T0 interval. Its denominator is the sum of those updates' durations, in seconds (`scored_rest_seconds`), not the sum of overlapping two-second windows. Warm-up, invalid, and transition-spanning windows are excluded. Also report total `rest_annotation_seconds` and eligible rest-window count so reduced coverage cannot be mistaken for successful idle behavior. This endpoint-exposure convention does not establish real-world false activations during spontaneous no-control periods. No ITR is computed from replay windows.

## Provenance and artifacts
Every saved bundle has a unique filename and SHA-256 receipt. It retains source-file hashes, ordered channels, units/rate, filter coefficients, feature recipe, split, scaler/model coefficients and class order, policy configuration, package versions, helper hash, trajectory, status reasons, and faults. Source data are not overwritten. JSON captures final evidence; there is no durable mid-run checkpoint, authenticated approval, OS sandbox, or production cancellation service. Notebook outputs are intentionally empty until students run them.
