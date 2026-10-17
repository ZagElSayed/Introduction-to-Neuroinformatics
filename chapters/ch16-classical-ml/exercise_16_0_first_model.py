"""First ML model: invented features, one row per artificial person.

Run from the repository root:
python chapters/ch16-classical-ml/exercise_16_0_first_model.py

This introductory single split teaches the operations. It is not the full
nested repeated-measures experiment in exercise_16_1_grouped_ml.py.
"""
import random

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


# 1. Build a tiny, reproducible teaching table: 40 people, two features each.
# X is the input table; y contains invented labels, not diagnoses.
rng = random.Random(16)
y = [0, 1] * 20
rng.shuffle(y)
X = []
for label in y:
    feature_a = rng.gauss(0, 1) + 0.7 * (2 * label - 1)
    feature_b = rng.gauss(0, 1)
    X.append([feature_a, feature_b])

# 2. Reserve whole people before fitting anything.
# Each row is a distinct person here: 30 train, 10 test.
train_ids, test_ids = train_test_split(
    list(range(40)), test_size=0.25, stratify=y, random_state=16)
X_train = [X[i] for i in train_ids]
X_test = [X[i] for i in test_ids]
y_train = [y[i] for i in train_ids]
y_test = [y[i] for i in test_ids]

# 3. Define the complete prediction procedure.
# The scaler learns its mean/SD from training rows when fit() is called.
model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))

# 4. Learn using only the 30 development participants.
model.fit(X_train, y_train)

# 5. Apply the fitted procedure to the 10 unseen participants.
probabilities = model.predict_proba(X_test)[:, 1]
predictions = (probabilities >= 0.5).astype(int)

# 6. Inspect probabilities and errors; compare against training prevalence.
baseline = DummyClassifier(strategy='prior').fit(X_train, y_train)
baseline_p = baseline.predict_proba(X_test)[:, 1]
print('Synthetic teaching data; positive label is invented.')
print('Train people:', len(train_ids), '| Test people:', len(test_ids))
print('person  target  probability  class_at_0.5')
for person, target, probability, prediction in zip(
        test_ids, y_test, probabilities, predictions):
    print(f'{person:>6}  {target:>6}  {probability:>11.3f}  {prediction:>12}')

tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
print('Counts:', dict(tn=int(tn), fp=int(fp), fn=int(fn), tp=int(tp)))
print(f'Model accuracy: {accuracy_score(y_test, predictions):.3f}')
print(f'Baseline accuracy: {accuracy_score(y_test, baseline.predict(X_test)):.3f}')
print(f'Model Brier error: {brier_score_loss(y_test, probabilities):.3f}')
print(f'Baseline Brier error: {brier_score_loss(y_test, baseline_p):.3f}')
print('One small teaching split: do not tune choices from these test results.')
print('Next: exercise_16_1_grouped_ml.py for repeated rows and nested evaluation.')
