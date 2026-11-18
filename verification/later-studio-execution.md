# Later-chapter execution review — 17 November 2026

This is bounded execution evidence, not a full scientific certification. Baseline:
companion main `79f3cc366a7f021711c22446c2117f54bb6dff50`, plus the Chapter 23
reference and the Chapter 20 filter-description correction in this change.
The correction changes metadata only: coefficients and algorithms are unchanged.
The JSON record contains notebook/helper SHA-256 values, package versions,
executed/skipped cell indices, gate outcomes, and selected observed results.

## Method and scope

`tools/verify_studios.py` executes supplied code cells sequentially in separate
Python processes and temporary chapter copies. Matplotlib uses the Agg backend;
IPython display calls are available. This tests code-cell execution, not a Jupyter
kernel, Colab environment, browser interface, clean package installation or all
platforms. Installation cells are explicitly skipped and listed. Notebooks remain
unexecuted in the repository. No external LLM server was enabled or tested.

The supplied default configurations were retained without tuning. Default Chapter
20 notebook 03 and Chapter 21 deliberately stop at their freeze gate. Separate
`frozen` author-verification runs explicitly freeze those unchanged configurations
before evaluating the supplied final cases; their results must not be used to
redesign the same evaluated procedure. This does not freeze a student's own
subsequent design. Optional Chapter 27 CPU PyTorch execution was separately enabled;
no GPU, external weights or foundation-model replication is demonstrated.
Chapter 22's exact pinned helper was staged locally and its digest checked by the
notebook. Its default virtual simulator ran; hardware extensions did not.

Observed outcomes: **14 distinct notebooks, 17 execution modes: 15 completed and
2 stopped at their expected freeze gates; no failed execution modes.**

| Notebook | Mode | Observed status |
| --- | --- | --- |
| `chapters/ch19-ai-agents/notebooks/01_understand_the_loop.ipynb` | default | passed |
| `chapters/ch19-ai-agents/notebooks/02_build_an_analysis_assistant.ipynb` | default | passed |
| `chapters/ch19-ai-agents/notebooks/03_evaluate_and_review.ipynb` | default | passed |
| `chapters/ch21-closed-loop/01_bounded_adaptive_control.ipynb` | default | expected_freeze_gate |
| `chapters/ch21-closed-loop/01_bounded_adaptive_control.ipynb` | frozen | passed |
| `chapters/ch22-edge-ai/01_edge_timing_studio.ipynb` | default | passed |
| `chapters/ch24-biomarker-validation/01_biomarker_validation_studio.ipynb` | default | passed |
| `chapters/ch25-longitudinal-cohort/01_longitudinal_cohort_studio.ipynb` | default | passed |
| `chapters/ch26-personalization/personalization_studio.ipynb` | default | passed |
| `chapters/ch27-foundation-models/foundation_model_studio.ipynb` | default | passed |
| `chapters/ch27-foundation-models/foundation_model_studio.ipynb` | torch | passed |
| `chapters/ch28-capstone/capstone_studio.ipynb` | default | passed |
| `chapters/ch20-bci-foundations/01_decode_public_eeg.ipynb` | default | passed |
| `chapters/ch20-bci-foundations/02_replay_and_command_policy.ipynb` | default | passed |
| `chapters/ch20-bci-foundations/03_faults_and_validation.ipynb` | default | expected_freeze_gate |
| `chapters/ch20-bci-foundations/03_faults_and_validation.ipynb` | frozen | passed |
| `chapters/ch23-distributed-platform/01_event_ledger.ipynb` | default | passed |

## Public-data BCI findings

Actual PhysioNet EEG Motor Movement/Imagery version 1.0.0 EDF files were downloaded
for S001 R04/R08/R12 and cached locally. These were not mocked. The fixed pipeline
uses C3/Cz/C4, 160 Hz, causal filtering, two-second windows, and the specified
quality gates. Only **5 training, 10 validation and 11 test trials** were eligible.
Class order is left/right imagery; confusion rows are true labels, columns predicted:

| Role | Run | Eligible trials | Confusion | Balanced accuracy |
| --- | --- | ---: | --- | ---: |
| Training | R04 | 5 | `[[4,0],[0,1]]` | 1.0000 |
| Validation | R08 | 10 | `[[4,2],[3,1]]` | 0.4583 |
| Frozen test | R12 | 11 | `[[6,0],[4,1]]` | 0.6000 |

The perfect training score is not evidence of generalization. The small eligible
sets, poor validation, asymmetric test confusion and single participant limit
interpretation. No useful live control, participant transfer, session transfer,
calibration, clinical performance, or statistical evidence of above-chance
performance is established. Continuous replay windows overlap; they are not
independent trials. Instructed rest is only the notebook's declared rest proxy.
Host processing times in the JSON are incidental measurements in this environment,
not sensor-to-actuator latency or a real-time deadline guarantee.

| File | SHA-256 |
| --- | --- |
| S001R04.edf | `3d161f88e1c00632585287d2ce584c2bc0f08862438eb255ea8723e00fac693d` |
| S001R08.edf | `358fb5189220725141968ae285fbe9e3f36210b834ffba71d940af308e3aca68` |
| S001R12.edf | `2b281c9b687b4c4176e83251d74743721f2d6ebd76656a972a3b9c44d9d88cd5` |

Observed packages: NumPy 2.3.5, SciPy 1.17.0, MNE 1.13.2,
scikit-learn 1.8.0, Matplotlib 3.10.8, IPython 9.16.1 and PyTorch 2.6.0+cpu.
Python and SQLite versions for the Chapter 23 reference are exported in its
own report. This is an observed environment, not a tested dependency lockfile.

## Chapter 23 reference

The local synthetic experiment produced 12 attempts, 9 unique archive rows,
and 7 monitor admissions for 10 opportunities. Receiver restart preserved
receipts and duplicate handling. Tests independently force archive insertion to
fail after receipt insertion and check that the receipt is rolled back. They
also cover schema/type bounds, unauthorized scope, changed content under an
existing identity, expiry equality, future events, older events and stale status.
No physical crash, network, broker, concurrent connection, authenticated device,
sender spool or persistent monitor is tested. These remain explicit extensions.

## Reproduction

From the repository root, in an environment with the selected notebooks' packages:

```sh
python tools/verify_studios.py --output verification-run --frozen --torch
python tools/verify_studios.py --output bci-verification-run --chapters 20 --real-data --data-cache /absolute/path/to/bci_data --frozen
python -m pytest tests -q
```

The BCI cache must use the MNE EEGBCI directory layout, with the three actual EDFs
under `MNE-eegbci-data/files/eegmmidb/1.0.0/S001/`; the notebook downloader populates
this layout. Each output directory must be new. Core helpers in later studios
can use only the standard library even though this general notebook runner uses
Matplotlib/IPython. Installation itself was not tested by the runner.

Regression result: **126 tests and 18 subtests passed**. Two environment warnings
were retained: an installed AnyIO pytest-plugin deprecation, and joblib falling
back to logical-core count because physical-core discovery was unavailable.
Neither was a scientific-output discrepancy. No test was disabled to pass.

Sources for corrected method descriptions: [SciPy 1.17 Butterworth design](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.signal.butter.html),
[SciPy forward–backward filtering](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.signal.filtfilt.html),
[Python 3.11 transaction context manager](https://docs.python.org/3.11/library/sqlite3.html#how-to-use-the-connection-context-manager),
and [SQLite conflict behavior](https://www.sqlite.org/lang_conflict.html).
