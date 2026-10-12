"""Chapter 13: reproducible synthetic spectral estimation using Python standard library."""
import argparse
import csv
import json
import math
from pathlib import Path

def signal(fs=128, duration=4.0):
    n = round(fs * duration)
    return [12*math.sin(2*math.pi*10*i/fs) + 4*math.sin(2*math.pi*22*i/fs) +
            1.5*math.sin(2*math.pi*3*i/fs) for i in range(n)]

def welch_psd(x, fs, segment_length, overlap=0.5):
    if segment_length < 4 or segment_length > len(x) or segment_length % 2:
        raise ValueError("segment_length must be even, >=4, and <= signal length")
    if not 0 <= overlap < 1:
        raise ValueError("overlap must be between 0 and 1")
    hop = max(1, round(segment_length*(1-overlap)))
    window = [0.5-0.5*math.cos(2*math.pi*i/(segment_length-1)) for i in range(segment_length)]
    norm = fs*sum(w*w for w in window)
    bins = segment_length//2 + 1
    psd = [0.0]*bins
    count = 0
    for start in range(0, len(x)-segment_length+1, hop):
        segment = x[start:start+segment_length]
        mean = sum(segment)/len(segment)
        tapered = [(v-mean)*w for v,w in zip(segment,window)]
        for k in range(bins):
            real = sum(v*math.cos(2*math.pi*k*j/segment_length) for j,v in enumerate(tapered))
            imag = -sum(v*math.sin(2*math.pi*k*j/segment_length) for j,v in enumerate(tapered))
            value = (real*real+imag*imag)/norm
            if k != 0 and k != segment_length//2:
                value *= 2
            psd[k] += value
        count += 1
    return [k*fs/segment_length for k in range(bins)], [v/count for v in psd], count

def bandpower(freq, psd, low, high):
    if len(freq)<2:
        raise ValueError("PSD too short")
    df = freq[1]-freq[0]
    return sum(p for f,p in zip(freq,psd) if low <= f < high)*df

def run(output_dir, fs=128):
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    x = signal(fs)
    reports = []
    for nperseg in (128,256):
        freq, power, count = welch_psd(x,fs,nperseg)
        filename = root / f"welch_{nperseg}.csv"
        with filename.open("w",newline="",encoding="utf-8") as stream:
            w=csv.writer(stream)
            w.writerow(["frequency_hz","psd_uV2_per_hz"])
            w.writerows((round(f,5),round(p,9)) for f,p in zip(freq,power))
        peak_idx=max((i for i,f in enumerate(freq) if 8<=f<=13),key=lambda i:power[i])
        reports.append({"segment_samples":nperseg,"segment_seconds":nperseg/fs,
                        "frequency_spacing_hz":fs/nperseg,"segments_averaged":count,
                        "alpha_peak_hz":freq[peak_idx],"alpha_power_uV2":bandpower(freq,power,8,13),
                        "total_1_40hz_power_uV2":bandpower(freq,power,1,40)})
    report={"synthetic":True,"fs_hz":fs,"duration_s":len(x)/fs,
            "known_frequencies_hz":[3,10,22],"psd_units":"uV^2/Hz",
            "method":"one-sided Welch periodogram, Hann taper, mean detrend, 50% overlap",
            "comparisons":reports,
            "interpretation_warning":"Band power includes spectral leakage and is not direct evidence of a neural generator"}
    (root/"spectral_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output-dir",default="outputs/ch13")
    args=p.parse_args()
    print(json.dumps(run(args.output_dir),indent=2))

if __name__=="__main__":
    main()
