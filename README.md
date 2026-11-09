# Introduction-to-Neuroinformatics

Student resources for *Introduction to Neuroinformatics: Data, Computational Models, Intelligent Systems, and Neuroscience*, by Zag ElSayed and Ernest Pedapati.

Start with the [Student Quickstart](docs/STUDENT_QUICKSTART.md), then open the guide for your chapter. Each guide specifies its own data, environment, commands, and assignment; requirements differ across activities. The [book manuscript](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics-Book) contains the scientific explanation and chapter context.

## Find your chapter

| Chapter | Topic | Resources |
| --- | --- | --- |
| 1 | Neuroinformatics within Computational Neuroscience | [Chapter guide](chapters/ch01-foundations/README.md) |
| 2 | Neurobiological Foundations for Computational Modeling | [Chapter guide](chapters/ch02-neurobiology/README.md) |
| 3 | Mathematical Foundations for Brain Data | [Chapter guide](chapters/ch03-mathematics/README.md) |
| 4 | Information Technology Foundations and Tools for Neuroinformatics | [Chapter guide](chapters/ch04-it-foundations/README.md) |
| 5 | Electrophysiological Signals: EEG, MEG, and ECoG | [Chapter guide](chapters/ch05-electrophysiology/README.md) |
| 6 | Neuroimaging and Multimodal Data | [Chapter guide](chapters/ch06-neuroimaging/README.md) |
| 7 | Peripheral, Behavioral, and Wearable Signals | [Chapter guide](chapters/ch07-wearables/README.md) |
| 8 | Experimental Design and Cognitive Paradigms | [Chapter guide](chapters/ch08-experimental-design/README.md) |
| 9 | Neurodata Formats, Standards, and Metadata | [Chapter guide](chapters/ch09-data-standards/README.md) |
| 10 | Neuroinformatics Data Pipelines, Infrastructure, and Workflows | [Chapter guide](chapters/ch10-data-pipelines/README.md) |
| 11 | Ethical, Legal, Privacy, and Governance Considerations in Neuroinformatics | [Chapter guide](chapters/ch11-ethics-governance/README.md) |
| 12 | Neural Signal Preprocessing and Artifact Modeling | [Chapter guide](chapters/ch12-preprocessing/README.md) |
| 13 | Time–Frequency and Spectral Analysis | [Chapter guide](chapters/ch13-time-frequency/README.md) |
| 14 | Source Localization and Spatial Modeling | [Chapter guide](chapters/ch14-source-localization/README.md) |
| 15 | Network and Graph-Theoretic Brain Models | [Chapter guide](chapters/ch15-brain-networks/README.md) |
| 16 | Classical Machine Learning for Neuroinformatics | [Chapter guide](chapters/ch16-classical-ml/README.md) |
| 17 | Deep Learning for Neural Data | [Chapter guide](chapters/ch17-deep-learning/README.md) |
| 18 | Vision-Based AI for Neural Signal Interpretation | [Chapter guide](chapters/ch18-vision-ai/README.md) |
| 19 | AI Agents and Intelligent Neuroinformatics Automation | [Chapter guide](chapters/ch19-ai-agents/README.md) |
| 20 | Foundations of Brain–Computer Interfaces | [Chapter guide](chapters/ch20-bci-foundations/README.md) |
| 21 | Closed-Loop and Adaptive Neurotechnology | [Chapter guide](chapters/ch21-closed-loop/README.md) |
| 22 | Real-Time Neuroinformatics Systems and Edge AI | [Chapter guide](chapters/ch22-edge-ai/README.md) |
| 23 | Cloud, Edge, and Cyber-Physical Systems for Neurotechnology | [Manuscript lab](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics-Book/blob/main/chapters/ch23.tex) · companion pack pending |
| 24 | Computational Biomarkers and Clinical Decision Support | [Chapter guide](chapters/ch24-biomarker-validation/README.md) |
| 25 | Neuroinformatics Applications in Brain Disorders | [Chapter guide](chapters/ch25-longitudinal-cohort/README.md) |
| 26 | Precision Neurology and Personalized Neurotechnology | [Chapter guide](chapters/ch26-personalization/README.md) |
| 27 | Generative AI and Foundation Models for Neuroscience | [Chapter guide](chapters/ch27-foundation-models/README.md) |
| 28 | The Future of Neuroinformatics: From Brain Data to Intelligent Neurotechnology | [Chapter guide](chapters/ch28-capstone/README.md) |

Chapter 23's exercise is currently provided in the manuscript. Its dedicated student pack has not yet been added. The remaining links identify available guides, not a certification that every exercise has been execution-verified. Follow each guide's stated verification status and report your own observed results.

## Selected laboratory introductions

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
