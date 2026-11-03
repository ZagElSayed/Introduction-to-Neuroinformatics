# Chapter 26: Precision neurology and personalization studio

Follow one invented longitudinal study from a frozen personal baseline to held-out prediction, then inspect a **separate randomized utility experiment** and a bounded software-gain state machine. The exercise teaches information handling and evidence boundaries. It models no neurological disorder and supports no clinical action.

Read [STUDY_CONTRACT.md](STUDY_CONTRACT.md), open [personalization_studio.ipynb](personalization_studio.ipynb), then complete [ASSIGNMENT.md](ASSIGNMENT.md). The notebook is supplied without outputs; execute it yourself and interpret your results. The helper was inspected statically during authoring; simulator and notebook execution were not performed by the authoring assistant.

Use Python 3.11 or later. All calculations in `precision_studio.py` use the standard library. For the notebook interface and optional plot, install the packages listed in `requirements-notebooks.txt` in your own environment. Run the notebook from this directory so its local helper import resolves. No patient data, GPU, account, or service is required.

```python
from precision_studio import make_fixture, build_rows, fit_risk, evaluate_risk
fixture = make_fixture(seed=2601)
rows, baselines = build_rows(fixture)
model = fit_risk(rows, fixture["references"], personal=True)
report = evaluate_risk(rows, fixture["references"], model, "validation")
```

The workflow has seven investigations:

1. Inspect cohort membership, observation time, availability time, and future references.
2. Compare two shared predictors using raw versus personal-reference features.
3. Trace insufficient baselines, firmware changes, and latent physical changes.
4. Compare risk and estimated positive net utility under a maximum selection budget.
5. Separate proposed, permitted, and delivered abstract gain values.
6. Inject faults and inspect the persistent firmware freeze.
7. Export and interpret a reconstructable evidence bundle.

Both prediction models use the same eligible windows, including the baseline-readiness requirement, for a matched representation comparison. The raw model is therefore not an independent demonstration of operation without a personal baseline. Model fitting, reference construction, and evaluation are distinct steps. Validation and evaluation people can supply their own pre-decision unlabeled reference observations; their outcomes never fit the predictors or utility cells. Do not tune after inspecting evaluation results and still describe that result as untouched.

The utility experiment's `baseline_risk` is a constructed ranking variable, **not** an output of the longitudinal predictor. Utility-cell contrasts are estimated from randomized development observations. Oracle values are available only because this is a simulation and are used for a labeled scoring reference. There is no guarantee that a finite-sample fitted policy outperforms a risk ranking.

`decide_gain` changes an abstract parameter in `[0,1]`, with maximum step `0.1`. Its default permission is false. Explicitly pass each returned `next_state` to carry gain and freeze history forward. A Boolean teaching flag is not an authentication mechanism; numeric clipping is not a proof of physical safety. No requalification or automatic reset is implemented.

`export_bundle` creates a new timestamped `outputs/precision-*` directory. It writes separate observations, outcomes, randomized observations, simulator truth, models, reports, decisions, and a manifest. `sha256.json` covers the other exported files, not itself. The receipt supports byte comparisons; it supplies no authentication or immutability. No numerical results or clinical performance claims are supplied in advance.
