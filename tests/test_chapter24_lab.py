"""Known-answer metrics and scientific boundaries for the synthetic Chapter 24 lab."""
from copy import deepcopy
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'chapters/ch24-biomarker-validation/biomarker_validation.py'
spec = importlib.util.spec_from_file_location('chapter24_lab', HELPER)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class BiomarkerValidationTests(unittest.TestCase):
    def setUp(self):
        self.rows = lab.make_dataset()
        self.cal = [r for r in self.rows if r['cohort'] == 'calibration']
        self.external = [r for r in self.rows if r['cohort'] == 'external']
        self.mapping = lab.fit_calibrator(self.cal)

    def test_split_people_and_outcome_availability(self):
        cohorts = [[r for r in self.rows if r['cohort'] == c]
                   for c in ('development', 'calibration', 'external')]
        self.assertEqual(len(self.rows), 720)
        self.assertEqual(len({r['subject_id'] for r in self.rows}), 720)
        for earlier, later in zip(cohorts, cohorts[1:]):
            self.assertLess(max(r['outcome_available_day'] for r in earlier),
                            min(r['prediction_day'] for r in later))
        with self.assertRaises(ValueError):
            lab.fit_calibrator(self.external)

    def test_known_confusion_counts_and_abstention_denominator(self):
        rows = []
        for i, (outcome, score) in enumerate([(1, .9), (1, .5), (0, .6), (0, .1)]):
            rows.append(dict(self.external[i], outcome=outcome, score=score,
                             quality_ok=True, supported_input=True))
        # Equality is positive. One TP, FP, FN and TN at .6.
        report = lab.evaluate(rows, .6)
        for k in ('tp', 'fp', 'fn', 'tn'):
            self.assertEqual(report[k], 1)
        for k in ('sensitivity', 'specificity', 'ppv', 'npv'):
            self.assertEqual(report[k], .5)
        self.assertAlmostEqual(report['brier'], .1575)
        self.assertAlmostEqual(report['net_benefit_eligible'], -.125)
        # An abstention must reduce coverage without becoming a false negative.
        rows.append(dict(rows[0], subject_id='excluded', score=None))
        gated = lab.evaluate(rows, .6)
        self.assertEqual(gated['n_total'], 5)
        self.assertEqual(gated['n_eligible'], 4)
        self.assertEqual(gated['coverage'], .8)
        self.assertEqual(gated['fn'], report['fn'])
        self.assertEqual(gated['net_benefit_eligible'], report['net_benefit_eligible'])

    def test_ties_and_undefined_metrics(self):
        self.assertEqual(lab.roc_auc([1, 0], [.5, .5]), .5)
        self.assertEqual(lab.average_precision([1, 0], [.5, .5]), .5)
        self.assertIsNone(lab.roc_auc([1, 1], [.2, .8]))
        self.assertIsNone(lab.average_precision([0, 0], [.2, .8]))
        self.assertIsNone(lab.ratio(0, 0))
        excluded = [dict(self.external[0], score=None)]
        report = lab.evaluate(excluded, .25)
        for key in ('sensitivity', 'specificity', 'ppv', 'npv', 'brier', 'net_benefit_eligible'):
            self.assertIsNone(report[key])

    def test_prevalence_and_bayesian_known_answer(self):
        # Sensitivity .9, specificity .8, prevalence .1: 9 TP / (9 TP + 18 FP).
        self.assertAlmostEqual(lab.prevalence_scenario(.9, .8, .1)['ppv'], 1/3)
        self.assertAlmostEqual(lab.prevalence_scenario(.9, .8, .1)['npv'], 72/73)
        prior_odds = .2/.8
        self.assertAlmostEqual(prior_odds*6/(1+prior_odds*6), .6)

    def test_future_outcomes_do_not_change_prediction_cards(self):
        before = lab.result_card(self.external[0], 'sensitive', self.mapping)
        altered = dict(self.external[0], outcome=1-self.external[0]['outcome'],
                       outcome_available_day=99999)
        self.assertEqual(before, lab.result_card(altered, 'sensitive', self.mapping))
        self.assertNotIn('outcome', before)
        self.assertNotIn('outcome_available_day', before)
        abstain = lab.result_card(dict(altered, score=None), 'sensitive', self.mapping)
        self.assertEqual(abstain['category'], 'insufficient_evidence')
        self.assertIsNone(abstain['synthetic_estimate'])

    def test_bootstrap_is_reproducible_and_keeps_mapping_fixed(self):
        before = deepcopy(self.mapping)
        one = lab.bootstrap_brier(self.external, self.mapping, repeats=40)
        two = lab.bootstrap_brier(self.external, self.mapping, repeats=40)
        self.assertEqual(one, two)
        self.assertLessEqual(one['lower'], one['upper'])
        self.assertEqual(self.mapping, before)

    def test_bundle_digest_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = lab.save_bundle(self.rows, self.mapping, tmp)
            first = (a/'bundle.json').read_bytes()
            b = lab.save_bundle(self.rows, self.mapping, tmp)
            self.assertNotEqual(a, b)
            self.assertEqual((a/'bundle.json').read_bytes(), first)
            self.assertEqual((a/'sha256.txt').read_text().split()[0], sha256(first).hexdigest())
            bundle = json.loads(first)
            self.assertEqual(len(bundle['prediction_cards']), 240)
            self.assertTrue(all('outcome' not in c for c in bundle['prediction_cards']))
            bad = deepcopy(self.mapping)
            bad['fit_subjects'].append(self.external[0]['subject_id'])
            with self.assertRaises(ValueError):
                lab.save_bundle(self.rows, bad, tmp)


if __name__ == '__main__':
    unittest.main()
