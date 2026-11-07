# Introduction-to-Neuroinformatics

## Chapter 16: classical machine learning

Start with the [Chapter 16 guide](chapters/ch16-classical-ml/README.md), then follow the [assignment and rubric](chapters/ch16-classical-ml/ASSIGNMENT.md). The chapter uses synthetic data to teach participant-aware evaluation and a traceable NeuroBridge prediction workflow.

## Chapter 17: deep learning notebook studio

Explore CNNs, RNN/GRU, Transformers, and autoencoders through [five guided public-data notebooks](chapters/ch17-deep-learning/NOTEBOOK_GUIDE.md), then connect the architectures to real EEG motor-imagery recordings. Code, Colab links, local Jupyter setup, and [reflection-based assignments](chapters/ch17-deep-learning/NOTEBOOK_ASSIGNMENT.md) are provided.

## Chapter 19: AI agents and intelligent automation

Build an inspectable analysis assistant with [three guided notebooks](chapters/ch19-ai-agents/NOTEBOOK_GUIDE.md), a standard-library Python runtime, synthetic EEG, and 20 student-run evaluation cases. Start without a GPU or API key, then optionally connect a local LLM planner through the same tool and verification boundary. See the [chapter guide](chapters/ch19-ai-agents/README.md) and [assignment](chapters/ch19-ai-agents/ASSIGNMENT.md).

## Chapter 20: brain–computer interfaces

Build a hardware-free, causal EEG replay controller with [three guided notebooks](chapters/ch20-bci-foundations/NOTEBOOK_GUIDE.md). Learn run-separated decoding, bounded cursor commands, fault inhibition, and honest timing/coverage metrics using public PhysioNet recordings. See the [chapter guide](chapters/ch20-bci-foundations/README.md), [replay contract](chapters/ch20-bci-foundations/REPLAY_CONTRACT.md), and [100-point assignment](chapters/ch20-bci-foundations/ASSIGNMENT.md).

## Chapter 21: closed-loop and adaptive neurotechnology

Build a dimensionless feedback simulator with a fixed controller, bounded gain adaptation, fault/stop/recovery logic, and decision reconstruction. Start with the [chapter guide](chapters/ch21-closed-loop/README.md) and [guided notebook](chapters/ch21-closed-loop/01_bounded_adaptive_control.ipynb), then follow the [simulation contract](chapters/ch21-closed-loop/SIMULATION_CONTRACT.md) and [100-point assignment](chapters/ch21-closed-loop/ASSIGNMENT.md). No human recordings, stimulation hardware, GPU, or API key are required.

## Chapter 22: real-time systems and edge AI

Make a bounded streaming pipeline fall behind and explain its deadline, freshness, queue, and coverage behavior with the [edge timing studio](chapters/ch22-edge-ai/README.md). The [guided notebook](chapters/ch22-edge-ai/01_edge_timing_studio.ipynb), [timing contract](chapters/ch22-edge-ai/TIMING_CONTRACT.md), and [100-point assignment](chapters/ch22-edge-ai/ASSIGNMENT.md) use a standard-library virtual model, with an optional host measurement adapter. Assigned virtual times are explicitly separated from measured device performance. No headset, human data, GPU, or API key is required.

## Chapter 24: computational biomarkers and clinical decision support

Build an inspectable validation dashboard with the [chapter guide](chapters/ch24-biomarker-validation/README.md) and [guided notebook](chapters/ch24-biomarker-validation/01_biomarker_validation_studio.ipynb). The standard-library synthetic studio separates development, calibration, and external cohorts; compares fixed threshold policies; reports calibration, coverage, subgroup outcomes, and scoped uncertainty; and exports research cards and evidence bundles. Read the [study contract](chapters/ch24-biomarker-validation/STUDY_CONTRACT.md) and [100-point assignment](chapters/ch24-biomarker-validation/ASSIGNMENT.md). It demonstrates evaluation mechanics, not a validated EEG biomarker or clinical benefit. Materials were statically inspected; students run and assess their own results.

## Chapter 25: disorder-aware longitudinal cohorts

Build a point-in-time cohort with the [chapter guide](chapters/ch25-longitudinal-cohort/README.md) and [guided notebook](chapters/ch25-longitudinal-cohort/01_longitudinal_cohort_studio.ipynb). The standard-library SQLite studio preserves observation and availability times, exposes deliberate leakage traps, fits transparent development-only models, examines missing-modality robustness, and exports research evidence. Read the [study contract](chapters/ch25-longitudinal-cohort/STUDY_CONTRACT.md) and [100-point assignment](chapters/ch25-longitudinal-cohort/ASSIGNMENT.md). All records are synthetic; the studio does not establish clinical validity or benefit. Materials were inspected statically; students run and assess their own results.

## Chapter 26: precision neurology and personalization

Follow a frozen personal reference into held-out prediction, then inspect a separate randomized utility experiment and bounded software-gain release states with the [chapter guide](chapters/ch26-personalization/README.md) and [guided notebook](chapters/ch26-personalization/personalization_studio.ipynb). Read the [study contract](chapters/ch26-personalization/STUDY_CONTRACT.md) and [100-point assignment](chapters/ch26-personalization/ASSIGNMENT.md). The standard-library helper uses invented records, separates future references and simulator truth, exposes measurement-version freezes, and exports inspectable bundles. Materials were inspected statically; students execute and interpret their own results. No clinical validity or treatment benefit is established.

## Chapter 27: generative AI and foundation-model services

Begin with the [chapter guide](chapters/ch27-foundation-models/README.md) and [guided notebook](chapters/ch27-foundation-models/foundation_model_studio.ipynb). The standard-library core traces invented signal schemas, participant-safe normalization, a fixed-frequency baseline, faults, and authorized passage retrieval. An optional CPU PyTorch experiment compares random, masked-pretrained, and supervised tiny encoders without claiming to train a foundation model. Read the [study contract](chapters/ch27-foundation-models/STUDY_CONTRACT.md) and [100-point assignment](chapters/ch27-foundation-models/ASSIGNMENT.md). No patient data, GPU, API key, external model service, or downloaded weights are required. Materials were inspected statically; students execute and interpret their own results.

## Chapter 28: NeuroBridge capstone — build, break, and defend

Complete the [chapter guide](chapters/ch28-capstone/README.md) and [guided notebook](chapters/ch28-capstone/capstone_studio.ipynb). The standard-library teaching simulator links invented neural-like records, a development-fitted baseline, virtual request boundaries, fault scenarios, and a local research evidence card. Read the [study contract](chapters/ch28-capstone/STUDY_CONTRACT.md) and [100-point assignment](chapters/ch28-capstone/ASSIGNMENT.md). No real network, authentication service, physical control, or clinical validity is demonstrated. Materials were inspected statically; students execute and defend their own results and a bounded next study.
