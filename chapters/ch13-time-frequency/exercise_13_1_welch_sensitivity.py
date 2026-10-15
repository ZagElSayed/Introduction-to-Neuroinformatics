"""Chapter 13: transparent synthetic PSD, zero-padding, and time-frequency controls.

Standard library, direct DFT (not FFT). No human EEG, wavelet fitting, baseline
inference, aperiodic model, or statistical group comparison is performed.
"""
import argparse
import csv
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import platform
import uuid

FS = 128
VERSION = "2.0"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def valid_fs(fs):
    if isinstance(fs, bool) or not isinstance(fs, (int, float)) or not math.isfinite(fs) or fs <= 0:
        raise ValueError("fs must be finite and positive")


def signal(fs=FS, duration=4.0):
    valid_fs(fs)
    if fs <= 44 or isinstance(duration, bool) or not math.isfinite(duration) or duration <= 0 or round(fs*duration) < 4:
        raise ValueError("simulation requires fs > 44 Hz and positive finite duration")
    return [12*math.sin(2*math.pi*10*i/fs) + 4*math.sin(2*math.pi*22*i/fs) +
            1.5*math.sin(2*math.pi*3*i/fs) for i in range(round(fs*duration))]


def hann(length):
    if type(length) is not int or length < 4 or length % 2:
        raise ValueError("segment length must be an even integer >= 4")
    # Symmetric Hann: explicitly different from a periodic/DFT-even Hann.
    return [0.5-0.5*math.cos(2*math.pi*j/(length-1)) for j in range(length)]


@lru_cache(maxsize=8)
def dft_basis(length, nfft):
    return [(tuple(math.cos(2*math.pi*k*j/nfft) for j in range(length)),
             tuple(-math.sin(2*math.pi*k*j/nfft) for j in range(length)))
            for k in range(nfft//2+1)]


def periodogram(segment, fs, nfft=None):
    valid_fs(fs)
    length = len(segment)
    window = hann(length)
    nfft = length if nfft is None else nfft
    if type(nfft) is not int or nfft < length or nfft % 2:
        raise ValueError("nfft must be even and at least the segment length")
    if not all(math.isfinite(x) for x in segment):
        raise ValueError("finite samples required")
    mean = sum(segment)/length
    tapered = [(x-mean)*w for x, w in zip(segment, window)]
    weight_energy = sum(w*w for w in window)
    power = []
    for k, (cosine, sine) in enumerate(dft_basis(length, nfft)):
        re = sum(x*c for x, c in zip(tapered, cosine))
        im = sum(x*v for x, v in zip(tapered, sine))
        factor = 1 if k in (0, nfft//2) else 2
        power.append(factor*(re*re+im*im)/(fs*weight_energy))
    return [k*fs/nfft for k in range(len(power))], power


def starts_for(x, length, overlap):
    hann(length)  # Check the declared taper length before any output is written.
    if length > len(x) or not all(math.isfinite(v) for v in x):
        raise ValueError("enough finite samples required")
    if isinstance(overlap, bool) or not math.isfinite(overlap) or not 0 <= overlap < 1:
        raise ValueError("overlap fraction must be finite and in [0, 1)")
    noverlap = math.floor(length*overlap)
    hop = length-noverlap
    return list(range(0, len(x)-length+1, hop)), hop


def welch_psd(x, fs, segment_length, overlap=0.5, nfft=None):
    valid_fs(fs)
    starts, _ = starts_for(x, segment_length, overlap)
    accumulated = None
    for start in starts:
        freq, power = periodogram(x[start:start+segment_length], fs, nfft)
        if accumulated is None:
            accumulated = [0.0]*len(power)
        accumulated = [a+p for a, p in zip(accumulated, power)]
    return freq, [p/len(starts) for p in accumulated], len(starts)


def bandpower(freq, psd, low, high):
    if len(freq) != len(psd) or len(freq) < 2 or not 0 <= low < high <= freq[-1]:
        raise ValueError("equal vectors and a valid band within Nyquist required")
    if not all(math.isfinite(v) for v in freq+psd) or min(psd) < 0:
        raise ValueError("finite frequencies and nonnegative finite PSD required")
    df = freq[1]-freq[0]
    if df <= 0 or any(not math.isclose(b-a, df, rel_tol=1e-9, abs_tol=1e-12) for a, b in zip(freq, freq[1:])):
        raise ValueError("uniform increasing frequency grid required")
    return sum(p for f, p in zip(freq, psd) if low <= f < high)*df


def stft_power(x, fs, length, hop):
    valid_fs(fs)
    hann(length)
    if type(hop) is not int or hop < 1 or length > len(x) or not all(math.isfinite(v) for v in x):
        raise ValueError("positive integer hop and sufficient finite samples required")
    frames = []
    for start in range(0, len(x)-length+1, hop):
        freq, power = periodogram(x[start:start+length], fs)
        frames.append({"start_sample": start, "stop_sample_exclusive": start+length,
                       "center_time_s": (start+(length-1)/2)/fs, "psd": power})
    return freq, frames


def write_csv(path, header, rows):
    with path.open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(header)
        writer.writerows(rows)


def plot_psd(path, estimates):
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620">',
             '<rect width="1100" height="620" fill="white"/>', '<g font-family="sans-serif" fill="#142D4E">',
             '<text x="70" y="40" font-size="24">Same synthetic signal, three estimator configurations</text>',
             '<text x="70" y="72" font-size="17">PSD in microvolts squared / Hz; logarithmic vertical axis; display floor 1e-8</text>']
    for value in (-8, -6, -4, -2, 0, 2):
        y = 480-(value+8)*34
        parts.append(f'<path d="M90 {y} H1050" stroke="#E0E6EE"/><text x="40" y="{y+5}" font-size="15">1e{value}</text>')
    for idx, (name, freq, power) in enumerate(estimates):
        color = ('#167D91', '#7556A8', '#D87C36')[idx]
        points = ' '.join(f'{90+24*f:.2f},{480-(math.log10(max(p,1e-8))+8)*34:.2f}' for f, p in zip(freq,power) if f <= 40)
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.6"/>')
        parts.append(f'<text x="{70+idx*345}" y="545" fill="{color}" font-size="17">{name}</text>')
    for f in (0, 10, 20, 30, 40):
        parts.append(f'<text x="{90+24*f}" y="510" font-size="16">{f}</text>')
    parts.extend(['<text x="490" y="590" font-size="20">Frequency (Hz)</text>', '</g></svg>'])
    path.write_text(''.join(parts), encoding="utf-8")


def plot_tfr(path, estimates, hop=16):
    maximum = max(p for _, freq, frames in estimates for frame in frames for f, p in zip(freq, frame["psd"]) if f <= 40)
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="760">',
             '<rect width="1100" height="760" fill="white"/>', '<g font-family="sans-serif" fill="#142D4E">',
             '<text x="70" y="35" font-size="24">Known 10-Hz burst: window duration changes temporal smearing</text>',
             '<text x="70" y="65" font-size="17">Common color scale: -60 to 0 dB relative to the plot maximum; not baseline normalization</text>',
             '<text x="70" y="90" font-size="17">Gray margins have no full-window estimate; grid step is 0.125 s, not temporal resolution</text>']
    for row, (length, freq, frames) in enumerate(estimates):
        top = 140+row*285
        parts.append(f'<text x="70" y="{top-15}" font-size="21">{length/FS:g}-s symmetric Hann window; frequency in Hz</text>')
        parts.append(f'<rect x="90" y="{top}" width="960" height="220" fill="#EDF1F5"/>')
        df = FS/length
        for frame in frames:
            x = 90+120*(frame["center_time_s"]-hop/(2*FS))
            for f, p in zip(freq, frame["psd"]):
                if f > 40:
                    break
                lo, hi = max(0, f-df/2), min(40, f+df/2)
                y = top+220*(40-hi)/40
                level = max(0, min(1, (10*math.log10(max(p/maximum,1e-30))+60)/60))
                color = '#%02x%02x%02x' % tuple(round(255*(1-level)+c*level) for c in (22,125,145))
                parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{120*hop/FS:.2f}" height="{220*(hi-lo)/40:.2f}" fill="{color}"/>')
        for f in (0, 10, 20, 30, 40):
            parts.append(f'<text x="48" y="{top+220*(40-f)/40+5}" font-size="15">{f}</text>')
        for time in (0, 2, 4, 6, 8):
            parts.append(f'<text x="{90+120*time}" y="{top+244}" font-size="15">{time}</text>')
        for time in (3, 5):
            parts.append(f'<path d="M{90+120*time} {top} v220" stroke="#D65473" stroke-dasharray="4 4"/>')
    for step in range(60):
        level = step/59
        color = '#%02x%02x%02x' % tuple(round(255*(1-level)+c*level) for c in (22,125,145))
        parts.append(f'<rect x="{540+step*6}" y="686" width="6" height="14" fill="{color}"/>')
    parts.extend(['<text x="475" y="699" font-size="14">-60 dB</text>',
                  '<text x="910" y="699" font-size="14">0 dB</text>'])
    parts.extend(['<text x="70" y="725" font-size="18">Time (s); dashed markers: constructed burst support 3-5 s. No repeated trials or inference.</text>', '</g></svg>'])
    path.write_text(''.join(parts), encoding="utf-8")


def run(output_dir, fs=FS):
    if fs != FS or isinstance(fs, bool):
        raise ValueError("the companion run fixes fs at 128 Hz; helpers accept other valid rates")
    root = Path(output_dir)
    if root.exists() and (not root.is_dir() or any(root.iterdir())):
        raise FileExistsError("use a new or empty directory; previous runs are preserved")
    x = signal()
    burst_rows = []
    for i in range(8*FS):
        t = i/FS
        envelope = 0.5*(1-math.cos(math.pi*(t-3))) if 3 <= t < 5 else 0.0
        burst = 10*envelope*math.sin(2*math.pi*10*t)
        background = 1.5*math.sin(2*math.pi*3*t)+2*math.sin(2*math.pi*22*t)
        burst_rows.append((i, t, background+burst, burst, envelope))
    config = {"fs_hz": FS, "signal_units": "microvolts", "stationary_duration_s": 4,
              "burst_duration_s": 8, "taper": "symmetric Hann, denominator L-1",
              "detrend": "segment mean before taper", "sidedness": "one-sided",
              "scaling": "density", "welch_overlap_fraction": 0.5,
              "welch_configs": [[128,128],[256,256],[128,512]], "stft_hop_samples": 16,
              "stft_segment_lengths": [128,256], "padding": "none for observed frames",
              "band_integration": "uniform-bin rectangle sum; low inclusive, high exclusive",
              "alpha_band_hz": [8,13], "relative_denominator_hz": [1,40]}
    root.mkdir(parents=True, exist_ok=True)
    write_csv(root/'stationary_signal.csv', ['sample','time_s','signal_uV'], ((i,i/FS,v) for i,v in enumerate(x)))
    write_csv(root/'burst_signal.csv', ['sample','time_s','signal_uV','known_burst_uV','known_envelope'], burst_rows)
    reports, estimates, artifact_names = [], [], ['stationary_signal.csv','burst_signal.csv']
    for length, nfft in config["welch_configs"]:
        freq, power, count = welch_psd(x, FS, length, nfft=nfft)
        name = f'welch_{length}_nfft_{nfft}.csv'
        write_csv(root/name, ['frequency_hz','psd_uV2_per_hz'], zip(freq,power))
        artifact_names.append(name)
        df = FS/nfft
        window = hann(length)
        starts, hop = starts_for(x,length,0.5)
        weighted_energy = []
        for start in starts:
            values=x[start:start+length]
            mean=sum(values)/length
            weighted_energy.append(sum(((v-mean)*w)**2 for v,w in zip(values,window))/sum(w*w for w in window))
        alpha = bandpower(freq,power,8,13)
        total = bandpower(freq,power,1,40)
        peak=max((i for i,f in enumerate(freq) if 8<=f<13),key=lambda i:power[i])
        reports.append({"segment_samples": length, "segment_seconds": length/FS, "nfft": nfft,
                        "frequency_spacing_hz": df, "unpadded_spacing_hz": FS/length,
                        "hop_samples": hop, "overlap_samples": length-hop, "segments_averaged":count,
                        "unused_tail_samples": len(x)-(starts[-1]+length),
                        "equivalent_noise_bandwidth_hz": FS*sum(w*w for w in window)/sum(window)**2,
                        "alpha_peak_hz": freq[peak], "peak_interpretation": "maximum bin in declared range, not a fitted oscillatory peak",
                        "alpha_power_uV2": alpha, "total_1_40hz_power_uV2": total,
                        "relative_alpha": alpha/total if total>0 else None,
                        "full_grid_integral_uV2": sum(power)*df,
                        "mean_taper_weighted_detrended_energy_uV2": sum(weighted_energy)/len(weighted_energy),
                        "psd_file": name})
        estimates.append((f'L={length}, nfft={nfft}',freq,power))
    tfr_reports, tfr_estimates = [], []
    for length in (128,256):
        freq,frames=stft_power([r[2] for r in burst_rows],FS,length,16)
        name=f'stft_{length}.csv'
        write_csv(root/name,['start_sample','stop_sample_exclusive','center_time_s','frequency_hz','psd_uV2_per_hz'],
                  ((frame['start_sample'],frame['stop_sample_exclusive'],frame['center_time_s'],f,p)
                   for frame in frames for f,p in zip(freq,frame['psd'])))
        artifact_names.append(name)
        tfr_reports.append({"segment_samples":length,"segment_seconds":length/FS,
                            "frequency_spacing_hz":FS/length,"frame_count":len(frames),
                            "frame_step_s":16/FS,"first_center_s":frames[0]['center_time_s'],
                            "last_center_s":frames[-1]['center_time_s'],"padding":"none",
                            "center_convention":"mean time of first and last sample in frame",
                            "power_file":name})
        tfr_estimates.append((length,freq,frames))
    plot_psd(root/'psd_comparison.svg',estimates)
    plot_tfr(root/'tfr_comparison.svg',tfr_estimates)
    artifact_names.extend(['psd_comparison.svg','tfr_comparison.svg'])
    report={"pipeline_version":VERSION,"synthetic":True,"fs_hz":FS,"duration_s":len(x)/FS,
            "run_id":str(uuid.uuid4()),"created_at_utc":datetime.now(timezone.utc).isoformat(),
            "python_version":platform.python_version(),"script_sha256":sha256(__file__),
            "configuration":config,"configuration_sha256":hashlib.sha256(json.dumps(config,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            "known_frequencies_hz":[3,10,22],"known_stationary_peak_amplitudes_uV":[1.5,12,4],
            "analytic_stationary_mean_square_uV2":81.125,
            "sample_mean_square_uV2":sum(v*v for v in x)/len(x),
            "psd_units":"uV^2/Hz","comparisons":reports,"time_frequency":tfr_reports,
            "burst_truth":{"support_s":[3,5],"center_s":4,"frequency_hz":10,"peak_envelope_amplitude_uV":10},
            "review_status":"review_required","accepted_as_neurally_valid":False,
            "artifacts_sha256":{name:sha256(root/name) for name in artifact_names},
            "interpretation_warning":"Deterministic synthetic examples do not establish neural generators, statistical variance reduction, event-related inference or clinical validity; no wavelet or periodic/aperiodic model fitted"}
    (root/'spectral_report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',default='outputs/ch13/run01')
    args=parser.parse_args()
    print(json.dumps(run(args.output_dir),indent=2,allow_nan=False))


if __name__=='__main__':
    main()
