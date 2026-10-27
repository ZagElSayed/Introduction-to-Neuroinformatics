# Chapter 22 assignment — 100 points

Build a Timing and Edge-Readiness Bundle that another student can inspect. The required work uses the synthetic virtual core. A hardware or neural-model extension may deepen the study, but the rubric does not require buying a device or accessing human data.

## Deliverables

1. A short timing contract naming source, support, hop, arrival, service, deadline, and output events. Distinguish nominal duration from oldest/newest timestamp span.
2. An annotated nominal record, overloaded record, and rejected or missing record, with the causal reason for each outcome.
3. FIFO-capacity-8 and latest-capacity-1 comparisons under nominal, overload, and faults; then one matched-capacity comparison under a declared scenario.
4. All-window terminal counts and coverage beside completed-job percentiles. Plot a trace or queue events and explain the denominator of every metric.
5. Student-run audit output, saved JSON and receipt, helper identity, configurations, and a concise report of limitations and one justified extension.

Run the baseline before changing it. Predict at least two effects in writing before examining the comparisons, and preserve predictions that proved wrong. Do not select only the configuration or scenario that produces the most attractive percentile. No particular policy is expected to win all objectives.

## Rubric

| Criterion | Points | Evidence expected |
|---|---:|---|
| Timing and signal contract | 20 | Correct support/hop/deadline distinction; named endpoints; virtual versus measured time clearly separated; window-level fault semantics understood. |
| Queue experiment and causal reasoning | 20 | Reproducible baseline comparisons; explicit capacity difference; matched-capacity follow-up; explanation of non-cancellable running work, replacement, and expiry. |
| Metrics and complete accounting | 20 | Terminal statuses sum to expected windows; percentiles use completed jobs; coverage includes missing/dropped/rejected work; timeout versus late overlap interpreted. |
| Trace, audit, and reproducibility | 20 | Annotated decisions; student-run checks; retained configurations, helper identity, output bundles and receipts; no interpretation of hashes as authentication. |
| Engineering report and extension | 20 | Balanced findings with tradeoffs and no invented hardware or clinical results; a feasible next test identifying what evidence it would add. |

Strong work explains mechanisms rather than merely pasting a summary. Partial credit reflects correct implementation descriptions without complete evidence or limitations. A report that calls assigned virtual milliseconds a measured device benchmark cannot receive full marks for the timing or reporting criteria.

## Optional extensions

Choose one coherent question: capacity versus replacement policy; a measured host decoder; a real quantized model with held-out task evaluation; a version-compatible fallback transition; instrumented output timing; or sustained memory/energy/thermal measurement. Keep the baseline and record a new source identity. Report unmeasured quantities as unmeasured. A hypothetical change in assigned inference cost is a sensitivity study, not successful quantization.

## Report prompts

- Why can a 400-ms window meet a 100-ms newest-sample deadline after startup?
- What would change if the requirement were event-to-physical-effect time?
- Can better conditional p99 coexist with worse coverage or missed transient evidence?
- Which parts of this model would need replacement for live sensing or an actuator?
- What additional data or instrumentation would support the next claim?
