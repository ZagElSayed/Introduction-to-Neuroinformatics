# Chapter 24 — Biomarker validation studio

Turn a score into an inspectable evaluation: define who is eligible, freeze calibration and thresholds, examine performance with its denominators, and explain what remains unknown about clinical use.

The core uses Python 3.11+ and the standard library. It needs no human data, EEG recording, EHR access, GPU, or network service. The score, sites, groups, and outcomes are synthetic. This studio supplies evaluation mechanics, not a validated biomarker or clinical recommendation.

## Start

Keep this folder's files together and open `01_biomarker_validation_studio.ipynb`. For local notebooks, optional dependencies can be installed in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-notebooks.txt
python -m jupyterlab
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. In Colab, open the notebook and upload `biomarker_validation.py` to the same runtime working directory before running its import cell. The helper needs no installation. Do not upload patient records into this teaching workflow.

The same core works in an ordinary Python session from this directory:

```python
import biomarker_validation as lab
rows = lab.make_dataset()
calibration = [r for r in rows if r["cohort"] == "calibration"]
external = [r for r in rows if r["cohort"] == "external"]
mapping = lab.fit_calibrator(calibration)
print(lab.evaluate(external, lab.POLICIES["sensitive"], mapping))
print(lab.save_bundle(rows, mapping))
```

## Read before running

[STUDY_CONTRACT.md](STUDY_CONTRACT.md) specifies the generator, simulated calendar, split boundaries, eligibility, mapping, metrics, and uncertainty limits. The default is 720 independent synthetic people across three disjoint cohort/site combinations. The mapping is fitted only on site B; site C remains the external fixture.

Follow [ASSIGNMENT.md](ASSIGNMENT.md) for the 100-point report. The notebook covers raw and mapped outputs, a development-derived constant baseline, calibration diagrams, subgroup coverage, fixed-threshold comparisons, decision curves, prevalence arithmetic, a scoped bootstrap interval, and research-card export.

Important distinctions:

- The support flag is a fixture condition, not an implemented out-of-distribution detector.
- Average precision is reported explicitly; it is not interchangeable with trapezoidal PR-AUC.
- Net benefit and classification metrics are conditional on eligible records. The full workflow also needs an evaluated pathway for abstentions.
- The bootstrap concerns a population Brier score with a fixed mapping, not an individual patient's uncertainty.
- Synthetic site differences do not demonstrate real transportability or treatment benefit.
- A digest identifies bytes and does not authenticate them.

## Files and connection to NeuroBridge

- `biomarker_validation.py`: fixture, eligibility, calibration, metrics, bootstrap, cards, and export.
- `01_biomarker_validation_studio.ipynb`: guided notebook with empty outputs and execution counts.
- `STUDY_CONTRACT.md`: complete assumptions and evidence boundaries.
- `ASSIGNMENT.md`: deliverables and rubric.
- `requirements-notebooks.txt`: optional notebook/plotting packages.

Chapter 23 supplied distributed records and outcome boundaries. This studio does not import or pretend to implement its transport or identity mechanisms. It adds the distinction between source data, a score, calibration, a threshold policy, a prediction-time card, and later evaluation evidence. A real-data, clinical integration, prospective study, or treatment-effect extension needs a separate justified plan.

The code and notebook have been statically inspected only. No results are precomputed. Students must run, inspect, and document their own results before drawing conclusions.
