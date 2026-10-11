"""Notebook smoke tests for Chapters 1-5.

Synthetic notebooks run directly. Real-EDF notebooks run against an in-memory,
synthetic MNE RawArray through a temporary read_raw_edf test double; this
validates Python paths and plotting, NOT the actual PhysioNet EDF content.
"""
import ast
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mne
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS = [
    ("ch01-foundations", "01_eeg_first_look.ipynb"),
    ("ch02-neurobiology", "02_neural_signals.ipynb"),
    ("ch03-mathematics", "03_sampling_spectrum.ipynb"),
    ("ch04-it-foundations", "04_provenance_pipeline.ipynb"),
    ("ch05-electrophysiology", "05_inspect_real_eeg.ipynb"),
]


def synthetic_eeg():
    """Deterministic fixture in volts, not actual patient data."""
    sfreq = 160.0
    times = np.arange(0, 25, 1 / sfreq)
    data = np.stack([
        (15e-6 * np.sin(2 * np.pi * (8 + i) * times))
        for i in range(6)
    ])
    info = mne.create_info(
        [f"EEG{i+1}" for i in range(6)],
        sfreq=sfreq,
        ch_types=["eeg"] * 6,
    )
    return mne.io.RawArray(data, info, verbose="ERROR")


def test_notebook_structure_and_execution():
    for chapter, filename in NOTEBOOKS:
        path = ROOT / "chapters" / chapter / filename
        notebook = json.loads(path.read_text(encoding="utf-8"))
        assert notebook["nbformat"] == 4
        code_cells = [c for c in notebook["cells"] if c["cell_type"] == "code"]
        assert code_cells, f"No executable code: {path}"
        with tempfile.TemporaryDirectory() as folder:
            cwd = os.getcwd()
            os.chdir(folder)
            try:
                namespace = {"__name__": "__main__"}
                # A dummy path satisfies the notebooks' local-file precondition.
                # MNE's EDF loader is patched to return known synthetic signals.
                if chapter in {"ch01-foundations", "ch05-electrophysiology"}:
                    Path("S001R01.edf").touch()
                with patch.object(plt, "show", lambda: None):
                    with patch.object(mne.io, "read_raw_edf", side_effect=lambda *a, **k: synthetic_eeg()):
                        for cell in code_cells:
                            code = "".join(cell["source"])
                            ast.parse(code, filename=str(path))
                            exec(compile(code, str(path), "exec"), namespace)
                if chapter == "ch04-it-foundations":
                    output = Path("outputs/ch04/provenance.json")
                    assert output.is_file()
                    record = json.loads(output.read_text(encoding="utf-8"))
                    assert record["source"] == "synthetic, not clinical"
                    assert len(record["source_array_sha256"]) == 64
            finally:
                plt.close("all")
                os.chdir(cwd)


def test_assignments_and_readmes_present():
    for chapter, _ in NOTEBOOKS:
        folder = ROOT / "chapters" / chapter
        assignment = (folder / "ASSIGNMENT.md").read_text(encoding="utf-8")
        assert "Grading rubric" in assignment
        assert "Troubleshooting" in assignment
        assert "Graduate extension" in assignment
        assert (folder / "README.md").is_file()
