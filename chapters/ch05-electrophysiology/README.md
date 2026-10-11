# Chapter 5 — Electrophysiology: EEG, MEG, and ECoG

Companion exercises for *Introduction to Neuroinformatics: Data, Computational Models, and Neuroscience*.

## Start here

**Exercise 5.1 — Inspect a real EEG recording.** Use a public eyes-open baseline recording from the [PhysioNet EEG Motor Movement/Imagery dataset (version 1.0.0)](https://physionet.org/content/eegmmidb/1.0.0/), subject **S001**, run **R01**, file **S001R01.edf**. Dataset DOI: [10.13026/C28G6P](https://doi.org/10.13026/C28G6P). A short research baseline is not a clinical diagnostic record.

The executable Python script is [exercise_5_1_inspect_eeg.py](exercise_5_1_inspect_eeg.py). It reads the original recording, reports recording properties, plots raw channels and a Welch power spectral density, and saves a machine-readable quality-control summary. It does **not** perform automatic artifact rejection or diagnose abnormalities.

### Install and run

From the repository root, install the dependencies in `requirements.txt`. Then download `S001R01.edf` from the source above to your own computer and run:

```bash
python chapters/ch05-electrophysiology/exercise_5_1_inspect_eeg.py --edf /path/to/S001R01.edf --output-dir outputs/ch05-exercise-5-1
```

Replace `/path/to/S001R01.edf` with the real local path. Keep `outputs/` and recordings out of version control. The script uses a noninteractive matplotlib backend so it also works on remote machines.

### Student tasks

1. Report the sampling rate, recording duration, channel count, and any recorded events or annotations.
2. Examine a 20-second EEG interval; identify potentially unusual or contaminated portions **as hypotheses**, not diagnoses.
3. Inspect the available electrode montage or clearly state why positions could not be visualized.
4. Plot and describe each selected channel's power spectral density. Discuss frequency structure without equating spectral peaks to a medical condition.
5. Create a quality-control log: suspect channels, annotated intervals, missing metadata, and possible causes of contamination.
6. Verify that your processed outputs do not overwrite the original EDF. Include code version, selected channels, time interval, and PSD parameters in the report.

**Graduate extension (Exercise 5.2):** On copies of the loaded recording, compare two re-reference strategies that are valid for the available electrode montage. Evaluate resulting signal plots and power estimates, explain why reference choice affects interpretation, and preserve all preprocessing parameters. Do not automatically label any choice a universally correct reference.

### Expected output and assessment

The starter script writes `recording_summary.json`, `raw_segment.png`, and `psd.png`. Submit those along with a brief report explaining measurement units, acquisition context, artifact uncertainty, and the limits of inference. Award credit for reproducibility and interpretation, not merely for producing plots.

### Data governance

The PhysioNet dataset is hosted and maintained by its original provider. Verify its current access terms, citation, and permitted educational use on the source page. **No patient-level recordings are mirrored or committed here**, even when publicly accessible. Never upload identifiable clinical EEG to public repositories, notebooks, or AI tools. This is research education, not diagnostic software.
