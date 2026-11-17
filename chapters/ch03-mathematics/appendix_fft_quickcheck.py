"""Appendix A known-answer FFT example: synthetic data, not clinical EEG."""
import numpy as np

fs_hz = 250.0
n_samples = 500
amplitude_uv = 20.0
frequency_hz = 10.0

time_s = np.arange(n_samples) / fs_hz
signal_uv = amplitude_uv * np.sin(
    2 * np.pi * frequency_hz * time_s
)
recording_uv = signal_uv[np.newaxis, :]
assert recording_uv.shape == (1, n_samples)

centered_uv = recording_uv - recording_uv.mean(
    axis=-1, keepdims=True
)
spectrum = np.fft.rfft(centered_uv, axis=-1)
frequencies_hz = np.fft.rfftfreq(
    n_samples, d=1.0 / fs_hz
)
# Exclude DC when locating the oscillatory peak.
peak_bin = 1 + np.argmax(np.abs(spectrum[0, 1:]))
peak_hz = frequencies_hz[peak_bin]
peak_amplitude_uv = (
    2 * np.abs(spectrum[0, peak_bin]) / n_samples
)
assert np.isclose(peak_hz, 10.0)
assert np.isclose(peak_amplitude_uv, 20.0)
print(peak_hz, peak_amplitude_uv)
