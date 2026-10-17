# Your first model: understand, code, inspect

Start here if machine learning is new. This lesson uses one row per artificial person and a single protected split. Then move to repeated rows and nested validation in the main lab.

## The idea in one sentence

Give the computer examples of inputs and recorded labels, let it learn a rule from one set of people, then inspect its predictions for other people.

The clinical intuition is a weighted checklist. In logistic regression the computer learns the weights; it does not decide whether the label, study design or clinical use is appropriate.

## Run the first model

Use the environment setup in [MED_NEURO_WALKTHROUGH.md](MED_NEURO_WALKTHROUGH.md). From the repository root, run one command with that environment's Python:

```text
python chapters/ch16-classical-ml/exercise_16_0_first_model.py
```

On Windows without environment activation, replace `python` with `.\.venv\Scripts\python.exe`. On macOS/Linux use `.venv/bin/python`. The script prints results in the terminal and writes no output files. No runtime result is asserted in these instructions.

## Follow the six code blocks

| Block | What you understand | What the code does |
| --- | --- | --- |
| 1. Table | One person has two input numbers and one label | Creates `X` (40 × 2) and `y` (40 labels) |
| 2. Split | Learning and testing use different people | Reserves 30 people for training and 10 for testing |
| 3. Model | Scaling and classification are one procedure | Creates a scaler → logistic model pipeline |
| 4. Fit | Weights and scaling are learned from training data | Calls `model.fit(X_train, y_train)` |
| 5. Predict | New people receive outputs from the fitted rule | Calls `predict_proba(X_test)` and selects class-1 probability |
| 6. Inspect | A probability, a class and an error count differ | Prints participant predictions, a confusion matrix and baseline comparisons |

The input values and binary labels are invented. Feature A contains an artificial label-related shift; feature B is noise. Neither feature is measured EEG. The table has one row per person, so row splitting is also person splitting **in this lesson only**.

## Read the core code aloud

```python
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
model.fit(X_train, y_train)
probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.5).astype(int)
```

- `make_pipeline(...)`: put transformations and the classifier in order.
- `fit(...)`: learn scaling and weights from training examples.
- `predict_proba(...)`: return a probability for each class. `[:, 1]` takes the class-1 column for every test row.
- `>= 0.5`: apply the fixed teaching threshold. `astype(int)` turns true/false into 1/0.

In the printed table, `person` identifies the held-out person, `target` is the recorded invented label, `probability` is the model output and `class_at_0.5` is the thresholded decision. A displayed probability of 0.7 is not a person's probability of disease.

## Do three small coding tasks

1. **Trace an output:** choose one printed person. Identify its row in `X_test`, label in `y_test`, probability and predicted class. State whether it is a true/false positive/negative.
2. **Inspect a prespecified threshold:** before looking at a new result, change `0.5` to `0.7` in a copy of the script. Update the printed heading too. Explain why class calls and accuracy can change while probabilities and Brier error stay unchanged. This is a demonstration, not test-set threshold optimization.
3. **Learn where to make changes:** identify the lines controlling the sample size, invented signal, seed, split and model. Explain which changes would create a new experiment requiring fresh evaluation. Do not repeatedly tune them to improve this small test set.

Accuracy counts correct class calls. Brier error averages squared probability errors; smaller is better for that evaluated set. The dummy baseline uses training prevalence. You should compare against it, without assuming the logistic model must win on every small split.

## Move forward only when you can explain the operations

You should be able to explain `X`, `y`, training, testing, `fit`, probability, threshold and baseline in ordinary words. Then open [FIRST_STEPS.md](FIRST_STEPS.md) and run `exercise_16_1_grouped_ml.py`. That experiment adds six rows per person, artificial identity coordinates, multiple families, participant-level aggregation and nested tuning. Its purpose is to show why the simple split in this first lesson cannot be copied unchanged into a repeated-measures study.

The optional measured-data redesign comes later in [REAL_DATA_PROTOCOL.md](REAL_DATA_PROTOCOL.md). This lesson establishes the coding pattern; it does not implement patient-CSV ingestion, EEG extraction or clinical validation.
