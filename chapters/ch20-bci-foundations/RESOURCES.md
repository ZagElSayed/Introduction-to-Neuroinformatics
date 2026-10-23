# Primary resources

- [PhysioNet EEG Motor Movement/Imagery Dataset, v1.0.0](https://physionet.org/content/eegmmidb/1.0.0/): authoritative source, event meanings, attribution, and license. DOI: 10.13026/C28G6P. Cite Schalk (2009), the BCI2000 paper (Schalk et al., 2004), and the PhysioNet resource citation requested on the dataset page. The page currently requests Pollard et al. (2026), DOI 10.1038/s44360-026-00096-z.
- [MNE EEGBCI loader](https://mne.tools/stable/generated/mne.datasets.eegbci.load_data.html): supported runs and cache/download interface.
- [MNE motor-imagery example](https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html): a more advanced spatial-filter baseline. This studio uses a simpler causal band-power route and different runs/labels; do not copy the example's hands/feet mapping here.
- [SciPy sosfilt](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.sosfilt.html): SOS filtering with state passed between chunks.
- [SciPy Welch](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.welch.html): spectral density and window conventions.
- [scikit-learn common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html): train-only fitting and pipelines.
- [BCI2000](https://www.bci2000.org/): a modular BCI research platform discussed in the book; not required for these notebooks.

Use documentation matching the installed versions. These are source links and learning resources, not measured results from this studio.
