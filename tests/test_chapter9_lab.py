"""Behavioral tests for the Chapter 9 contract; unittest and pytest compatible."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "chapters/ch09-data-standards/exercise_9_1_neurodata_contract.py"
spec = importlib.util.spec_from_file_location("chapter9", SCRIPT)
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class Chapter9Contract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        lab.build(self.root)

    def errors(self):
        return "\n".join(lab.validate(self.root)["errors"])

    def edit_events(self, old, new):
        p = self.root / lab.EVENTS
        p.write_text(p.read_text().replace(old, new), encoding="utf-8")

    def rehash(self):
        p = self.root / "manifest.json"
        data = lab.read_json(p)
        for item in data["files"]:
            item["sha256"] = lab.sha256(self.root / item["path"])
        lab.write_json(p, data)

    def test_conversion_and_manifest(self):
        rows = lab.read_table(self.root / lab.EVENTS, "\t", ["onset", "duration", "trial_type"])
        self.assertEqual([float(r["onset"]) for r in rows], [.5, 2., 3.5])
        self.assertEqual([r["trial_type"] for r in rows], ["go", "nogo", "go"])
        report = lab.validate(self.root)
        self.assertTrue(report["passed_local_checks"])
        self.assertTrue(report["bids_compliant"].startswith("not established"))
        self.assertEqual(len(lab.read_json(self.root / "manifest.json")["files"]), 8)

    def test_cli_returns_failure_for_corruption(self):
        p = self.root / lab.SOURCE
        p.write_text(p.read_text() + "4000,N\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--output-dir", str(self.root), "--validate-only"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["passed_local_checks"])

    def test_generation_preserves_existing_work_without_force(self):
        with self.assertRaisesRegex(ValueError, "not empty"):
            lab.build(self.root)
        self.assertTrue(lab.build(self.root, force=True)["passed_local_checks"])

    def test_source_checksum_detects_change(self):
        p = self.root / lab.SOURCE
        p.write_bytes(p.read_bytes() + b"\n")
        self.assertIn("checksum mismatch", self.errors())

    def test_target_checksum_detects_change(self):
        self.edit_events("0.5", "0.6")
        self.assertIn("checksum mismatch", self.errors())

    def test_meaning_check_survives_rebaselined_hash(self):
        self.edit_events("0.5", "500.0")
        self.rehash()  # Deliberately show why a hash reference is not scientific proof.
        errors = self.errors()
        self.assertNotIn("checksum mismatch", errors)
        self.assertIn("Source-to-target meaning mismatch", errors)

    def test_nonfinite_times_are_rejected(self):
        for value in ("nan", "inf", "-inf"):
            with self.subTest(value=value):
                lab.build(self.root, force=True)
                self.edit_events("0.5", value)
                self.assertIn("finite", self.errors())

    def test_unknown_event_type_is_rejected(self):
        self.edit_events("go\n", "unknown\n")
        self.assertIn("Unknown trial type", self.errors())

    def test_negative_duration_is_rejected(self):
        self.edit_events("0.0", "-1.0")
        self.assertIn("Negative duration", self.errors())

    def test_negative_onset_can_be_valid(self):
        p = self.root / lab.SOURCE
        p.write_text(p.read_text().replace("500,G", "-500,G", 1), encoding="utf-8")
        lab.table(self.root / lab.EVENTS, ["onset", "duration", "trial_type"], lab.convert(p))
        self.rehash()
        self.assertTrue(lab.validate(self.root)["passed_local_checks"])

    def test_missing_columns_and_empty_tables(self):
        for contents in ("duration\ttrial_type\n0\tgo\n", "onset\tduration\ttrial_type\n"):
            with self.subTest(contents=contents):
                (self.root / lab.EVENTS).write_text(contents, encoding="utf-8")
                self.assertIn("event columns and values", self.errors())

    def test_sidecar_unit_mismatch_even_with_matching_hash(self):
        p = self.root / lab.SIDECAR
        data = lab.read_json(p)
        data["onset"]["Units"] = "ms"
        lab.write_json(p, data)
        self.rehash()
        self.assertIn("Time unit mismatch", self.errors())

    def test_malformed_or_missing_manifest_is_reported(self):
        p = self.root / "manifest.json"
        for contents in ("{", "[]", '{"contract_version": "1.1", "synthetic_only": true}'):
            with self.subTest(contents=contents):
                p.write_text(contents, encoding="utf-8")
                self.assertFalse(lab.validate(self.root)["passed_local_checks"])
        p.unlink()
        self.assertFalse(lab.validate(self.root)["passed_local_checks"])

    def test_bad_json_constants_are_rejected(self):
        (self.root / lab.SIDECAR).write_text('{"onset": NaN}', encoding="utf-8")
        self.assertIn("Nonstandard JSON constant", self.errors())

    def test_wrong_participant_is_rejected(self):
        p = self.root / "export/participants.tsv"
        p.write_text(p.read_text().replace("sub-001", "sub-002"), encoding="utf-8")
        self.rehash()
        self.assertIn("Participant linkage mismatch", self.errors())

    def test_missing_metadata_is_reported(self):
        (self.root / lab.SIDECAR).unlink()
        self.assertIn("metadata and observation linkage", self.errors())

    def test_invalid_manifest_digest_is_rejected(self):
        p = self.root / "manifest.json"
        data = lab.read_json(p)
        data["files"][0]["sha256"] = "x" * 64
        lab.write_json(p, data)
        self.assertIn("Invalid SHA-256 reference", self.errors())


if __name__ == "__main__":
    unittest.main()
