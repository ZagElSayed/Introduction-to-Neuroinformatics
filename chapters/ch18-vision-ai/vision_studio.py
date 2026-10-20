"""Chapter 18 public-data teaching studio. No downloads or training on import.

Run through the guided notebooks. This is a retrospective recording-condition
experiment, not a diagnostic or artifact-removal system. Student-run outputs
are evidence to inspect, not precomputed book results.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import io
import json
import platform
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

PALETTE = {"navy": "#142D4E", "teal": "#167D91", "violet": "#7556A8",
           "amber": "#D87C36", "coral": "#D65473"}
CONTRACT = {
    "dataset": "EEG Motor Movement/Imagery Dataset", "release": "1.0.0",
    "doi": "10.13026/C28G6P", "license": "Open Data Commons Attribution License v1.0",
    "source_url": "https://physionet.org/content/eegmmidb/1.0.0/",
    "channels": ["O1", "Oz", "O2"], "runs": {"1": "eyes_open", "2": "eyes_closed"},
    "sampling_rate_hz": 64, "samples": 256, "max_windows_per_run": 10,
    "first_window_start_s": 4, "window_duration_s": 4,
    "filter": "2-30 Hz fourth-order Butterworth IIR, zero phase, within recording",
    "reference": "preserve acquisition reference; no rereferencing",
    "power": "one-sided density; symmetric Hann, 64 samples, hop 16; segment mean removed",
    "channel_reduction": "mean of channel power matrices, not power of averaged waveform",
    "frequencies_hz": [2, 30], "power_unit": "microvolt^2/Hz", "db_reference": 1.0,
    "db_floor": 1e-12, "db_bounds": [-20.0, 40.0],
    "image": "64x64 uint8 grayscale, nearest resize; highest frequency at top",
    "target": "recording condition: 0 eyes open, 1 eyes closed",
    "limitations": "run order and condition are confounded; no diagnostic claim",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def versions():
    result = {"python": platform.python_version()}
    for package in ["numpy", "scipy", "mne", "matplotlib", "pandas", "Pillow",
                    "scikit-learn", "tensorflow", "ipywidgets"]:
        try:
            result[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            result[package] = "not installed"
    return result


def power_map(window_uv, fs=64):
    """[channels, 256] microvolts -> mean channel PSD [29 frequencies, 13 times]."""
    x = np.asarray(window_uv, dtype=np.float64)
    if x.shape != (3, 256) or not np.isfinite(x).all() or fs != 64:
        raise ValueError("Expected finite O1/Oz/O2 microvolts with shape (3,256), fs=64.")
    frames = np.lib.stride_tricks.sliding_window_view(x, 64, axis=-1)[:, ::16, :]
    frames = frames - frames.mean(axis=-1, keepdims=True)
    taper = np.hanning(64)  # symmetric Hann, explicitly matches the chapter equation
    fft = np.fft.rfft(frames * taper, axis=-1)
    density = abs(fft) ** 2 / (fs * np.sum(taper ** 2))
    density[..., 1:-1] *= 2  # DC/Nyquist have no distinct negative-frequency partner
    f = np.fft.rfftfreq(64, 1 / fs)
    keep = (f >= 2) & (f <= 30)
    power = density.mean(axis=0)[:, keep].T
    times = (np.arange(frames.shape[1]) * 16 + 32) / fs  # segment centers
    return power, f[keep], times


def render_power(power, bounds=(-20.0, 40.0)):
    """Numeric PSD -> undecorated pixels. Bounds are prespecified, not cohort fitted."""
    low, high = map(float, bounds)
    if not np.isfinite([low, high]).all() or low >= high:
        raise ValueError("Display bounds must be finite and increasing.")
    db = 10 * np.log10(np.maximum(power, 1e-12) / 1.0)
    q = np.rint(255 * np.clip((db - low) / (high - low), 0, 1)).astype(np.uint8)
    pixels = np.asarray(Image.fromarray(np.flipud(q)).resize(
        (64, 64), Image.Resampling.NEAREST))
    return pixels, db


def prepare_public_data(subjects, output_dir, cache_dir="eeg_cache"):
    """Download when explicitly called; fail on missing channels/short recordings."""
    import mne
    output = Path(output_dir)
    if (output / "dataset.npz").exists():
        raise FileExistsError("Use a fresh output directory to preserve earlier evidence.")
    output.mkdir(parents=True, exist_ok=True)
    cache = Path(cache_dir).resolve()
    cache.mkdir(parents=True, exist_ok=True)
    waves, maps, images, rows = [], [], [], []
    contract_hash = sha256(json.dumps(CONTRACT, sort_keys=True).encode())
    for subject in subjects:
        for run, label in [(1, 0), (2, 1)]:
            paths = mne.datasets.eegbci.load_data(
                int(subject), [run], path=str(cache), update_path=False, verbose=False)
            if len(paths) != 1:
                raise ValueError("Expected one EDF file per requested run.")
            source = Path(paths[0])
            source_hash = sha256(source.read_bytes())
            raw = mne.io.read_raw_edf(source, preload=True, verbose=False)
            original_fs = float(raw.info["sfreq"])
            mne.datasets.eegbci.standardize(raw)
            raw.pick(CONTRACT["channels"])
            raw.reorder_channels(CONTRACT["channels"])
            raw.filter(2., 30., method="iir", iir_params={"order": 4, "ftype": "butter"},
                       phase="zero", verbose=False)
            raw.resample(64, verbose=False)
            data_uv = raw.get_data() * 1e6  # MNE returns volts
            for j in range(10):
                start = (4 + j * 4) * 64
                wave = data_uv[:, start:start + 256]
                if wave.shape != (3, 256):
                    raise ValueError(f"Short recording S{subject:03d}R{run:02d}; do not skip silently.")
                power, f, t = power_map(wave)
                pixel, _ = render_power(power)
                derivative_id = f"S{subject:03d}_R{run:02d}_W{j:02d}"
                image_dir = output / "images"
                image_dir.mkdir(exist_ok=True)
                png_path = image_dir / f"{derivative_id}.png"
                Image.fromarray(pixel).save(png_path)
                rows.append({"array_row": len(rows), "derivative_id": derivative_id, "participant": int(subject),
                             "run": run, "window": j, "label": label,
                             "condition": ["eyes_open", "eyes_closed"][label],
                             "source_url": f"https://physionet.org/files/eegmmidb/1.0.0/S{subject:03d}/S{subject:03d}R{run:02d}.edf",
                             "source_sha256": source_hash, "original_fs_hz": original_fs,
                             "resampled_start_sample": start, "window_start_s": start / 64,
                             "waveform_sha256": sha256(wave.astype("<f8").tobytes()),
                             "power_sha256": sha256(power.astype("<f8").tobytes()),
                             "png_sha256": sha256(png_path.read_bytes()),
                             "pixel_sha256": sha256(pixel.tobytes()),
                             "contract_sha256": contract_hash,
                             "renderer_version": "ch18-public-studio-v1"})
                waves.append(wave); maps.append(power); images.append(pixel)
    np.savez_compressed(output / "dataset.npz", waves=np.array(waves), power=np.array(maps),
                        pixels=np.array(images), f=f, t=t)
    pd.DataFrame(rows).to_csv(output / "manifest.csv", index=False)
    write_json(output / "contract.json", CONTRACT)
    write_json(output / "environment.json", versions())
    return load_data(output)


def load_data(output_dir):
    output = Path(output_dir)
    with np.load(output / "dataset.npz", allow_pickle=False) as z:
        data = {k: z[k] for k in z.files}
    data["manifest"] = pd.read_csv(output / "manifest.csv")
    manifest = data["manifest"]
    if len(manifest) != len(data["pixels"]) or not np.array_equal(
            manifest.array_row.to_numpy(), np.arange(len(manifest))):
        raise ValueError("Manifest rows no longer align with the numeric arrays.")
    for i, row in manifest.iterrows():
        checks = [(data["pixels"][i].tobytes(), row.pixel_sha256),
                  (data["waves"][i].astype("<f8").tobytes(), row.waveform_sha256),
                  (data["power"][i].astype("<f8").tobytes(), row.power_sha256)]
        if any(sha256(value) != expected for value, expected in checks):
            raise ValueError(f"Derivative hash mismatch at row {i}.")
    return data


def show_views(data, index=0, bounds=(-20, 40), cmap="viridis"):
    row = data["manifest"].iloc[index]
    power = data["power"][index]
    pixel, db = render_power(power, bounds)
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.3), constrained_layout=True)
    for channel, wave in zip(CONTRACT["channels"], data["waves"][index]):
        axes[0].plot(np.arange(256) / 64, wave, label=channel, lw=.8)
    axes[0].set(xlabel="Seconds within window", ylabel="Microvolts", title="Measured waveform")
    axes[0].legend(fontsize=8)
    plot = axes[1].pcolormesh(data["t"], data["f"], db, shading="nearest", cmap=cmap,
                             vmin=bounds[0], vmax=bounds[1])
    fig.colorbar(plot, ax=axes[1], label="dB re 1 microvolt²/Hz")
    axes[1].set(xlabel="Segment center (s)", ylabel="Hz", title="Numerical PSD, displayed")
    axes[2].imshow(pixel, cmap="gray", vmin=0, vmax=255)
    axes[2].set(title="Undecorated 64×64 model pixels", xlabel="Pixel column", ylabel="Pixel row")
    fig.suptitle(f"{row.derivative_id}: {row.condition} — teaching display; not model input decoration",
                 color=PALETTE["navy"])
    plt.show()
    return fig


def make_model(seed=18):
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    inputs = tf.keras.Input((64, 64, 1), name="grayscale")
    x = tf.keras.layers.Conv2D(8, 3, padding="same", activation="relu")(inputs)
    x = tf.keras.layers.AveragePooling2D(2)(x)
    x = tf.keras.layers.Conv2D(16, 3, padding="same", activation="relu", name="visual_features")(x)
    x = tf.keras.layers.AveragePooling2D(2)(x)
    x = tf.keras.layers.Flatten()(x)
    x = tf.keras.layers.Dense(16, activation="relu")(x)
    score = tf.keras.layers.Dense(1, name="condition_logit")(x)
    model = tf.keras.Model(inputs, score)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                  loss=tf.keras.losses.BinaryCrossentropy(from_logits=True))
    return model


def probabilities(model, pixels):
    import tensorflow as tf
    x = np.asarray(pixels, dtype=np.float32)[..., None] / 255
    return tf.math.sigmoid(model(x, training=False)).numpy().ravel()


def score_by_person_condition(frame, probability):
    from sklearn.metrics import accuracy_score, roc_auc_score, brier_score_loss
    z = frame[["participant", "label"]].copy()
    z["probability"] = probability
    grouped = z.groupby(["participant", "label"], as_index=False).probability.mean()
    return grouped, {"accuracy": float(accuracy_score(grouped.label, grouped.probability >= .5)),
                     "roc_auc": float(roc_auc_score(grouped.label, grouped.probability)),
                     "brier": float(brier_score_loss(grouped.label, grouped.probability))}


def train_studio(data_dir, seed=18, epochs=15):
    """Single fixed participant split; test evaluation is saved once, not used for tuning."""
    import tensorflow as tf
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    output = Path(data_dir)
    if (output / "model.keras").exists():
        raise FileExistsError("This run already has a model; create a fresh directory for a new experiment.")
    data = load_data(output)
    m = data["manifest"]
    expected = set(range(1, 13))
    if set(m.participant) != expected:
        raise ValueError("The default experiment requires subjects 1–12, without silent exclusions.")
    groups = {"train": list(range(1, 9)), "validation": [9, 10], "test": [11, 12]}
    ids = {name: np.flatnonzero(m.participant.isin(people)) for name, people in groups.items()}
    m["split"] = [next(k for k, v in groups.items() if p in v) for p in m.participant]
    m.to_csv(output / "manifest.csv", index=False)
    x = data["pixels"].astype(np.float32)[..., None] / 255
    y = m.label.to_numpy(dtype=np.float32)
    tf.keras.utils.set_random_seed(seed)
    tf.config.experimental.enable_op_determinism()
    model = make_model(seed)
    callback = tf.keras.callbacks.EarlyStopping(monitor="val_loss", mode="min", patience=3,
                                               min_delta=0., restore_best_weights=True)
    history = model.fit(x[ids["train"]], y[ids["train"]], batch_size=16,
                        validation_data=(x[ids["validation"]], y[ids["validation"]]),
                        epochs=epochs, callbacks=[callback], verbose=2)
    model.save(output / "model.keras")
    # Fixed numerical comparator: mean log alpha and broad-band PSD, then training-only scaling.
    f = data["f"]
    feat = np.column_stack([10 * np.log10(np.maximum(
        data["power"][:, (f >= low) & (f <= high), :].mean(axis=(1, 2)), 1e-12))
        for low, high in [(8, 12), (2, 30)]])
    baseline = make_pipeline(StandardScaler(), LogisticRegression(C=1., max_iter=1000, random_state=seed))
    baseline.fit(feat[ids["train"]], y[ids["train"]])
    p = probabilities(model, data["pixels"])
    bp = baseline.predict_proba(feat)[:, 1]
    np.savez_compressed(output / "baseline.npz", mean=baseline[0].mean_, scale=baseline[0].scale_,
                        coef=baseline[1].coef_, intercept=baseline[1].intercept_)
    report = {"seed": seed, "epoch_limit": epochs, "batch_size": 16, "splits": groups,
              "selection": "minimum validation BCE; patience=3; min_delta=0; restore weights",
              "best_epoch": int(np.argmin(history.history["val_loss"]) + 1),
              "executed_epochs": len(history.history["loss"]), "parameters": model.count_params(),
              "aggregation": "mean probability within participant and condition; threshold=0.5",
              "independent_test_people": 2, "test_condition_summaries": 4,
              "limitations": "fixed run order; small cohort; exploratory validation; no clinical inference"}
    for name in ["validation", "test"]:
        ix = ids[name]
        grouped, metrics = score_by_person_condition(m.iloc[ix], p[ix])
        grouped.to_csv(output / f"{name}_person_condition_predictions.csv", index=False)
        report[name] = metrics
        _, report[name + "_numeric_baseline"] = score_by_person_condition(m.iloc[ix], bp[ix])
    preds = m[["derivative_id", "participant", "run", "label", "split"]].copy()
    preds["cnn_probability"] = p; preds["baseline_probability"] = bp
    preds.to_csv(output / "predictions.csv", index=False)
    # Add clean training loss to distinguish it from stochastic in-training batch losses.
    pd.DataFrame(history.history).to_csv(output / "training_curves.csv", index=False)
    report["selected_clean_train_loss"] = float(model.evaluate(x[ids["train"]], y[ids["train"]], verbose=0))
    reloaded = tf.keras.models.load_model(output / "model.keras")
    report["reload_max_probability_difference"] = float(np.max(abs(probabilities(reloaded, data["pixels"]) - p)))
    report["model_sha256"] = sha256((output / "model.keras").read_bytes())
    report["environment"] = versions()
    write_json(output / "report.json", report)
    write_json(output / "split_manifest.json", groups)
    write_json(output / "model_card.json", {"intended_use": "teaching recording-condition classification",
        "input": CONTRACT, "output": "sigmoid of eyes-closed logit; not recalibrated",
        "evidence": report, "resume": "Selected weights are restored but optimizer state may be from the final epoch; full training resumption is not established",
        "clinical_use": False, "artifact_rejection": False})
    return report


def gradcam(model, pixels, target=1):
    """Coarse Grad-CAM of class-1 logit or its negative for class 0."""
    import tensorflow as tf
    if target not in (0, 1):
        raise ValueError("Target must be 0 (open) or 1 (closed).")
    probe = tf.keras.Model(model.inputs, [model.get_layer("visual_features").output, model.output])
    x = tf.convert_to_tensor(np.asarray(pixels, np.float32)[None, ..., None] / 255)
    with tf.GradientTape() as tape:
        features, logits = probe(x, training=False)
        score = logits[:, 0] if target == 1 else -logits[:, 0]
    grads = tape.gradient(score, features)
    weights = tf.reduce_mean(grads, axis=(1, 2), keepdims=True)
    cam = tf.nn.relu(tf.reduce_sum(weights * features, axis=-1))[0].numpy()
    return cam / max(float(cam.max()), 1e-12)


def occlusion_grid(model, pixels, tile=16):
    """4x4 replacement sensitivity; 128/255 is intensity midpoint, not mean physiology."""
    pixel = np.asarray(pixels, dtype=np.uint8)
    base = float(probabilities(model, pixel[None])[0])
    variants = []
    for y in range(0, 64, tile):
        for x in range(0, 64, tile):
            q = pixel.copy(); q[y:y + tile, x:x + tile] = 128
            variants.append(q)
    diff = base - probabilities(model, np.array(variants))
    return diff.reshape(64 // tile, 64 // tile)


def quality_flags(pixel):
    x = np.asarray(pixel)
    return {"shape_ok": x.shape == (64, 64), "dtype_ok": x.dtype == np.uint8,
            "low_endpoint_fraction": float(np.mean(x == 0)),
            "high_endpoint_fraction": float(np.mean(x == 255)),
            "constant_image": bool(np.ptp(x) == 0),
            "interpretation": "descriptive renderer checks, not validated physiological QC"}


def inspect_example(data_dir, index, target=1, neighbors=3):
    """Validation-only inspection. Retrieval gallery contains training rows only."""
    import tensorflow as tf
    output = Path(data_dir)
    data = load_data(output); m = data["manifest"]
    if "split" not in m or m.iloc[index].split != "validation":
        raise ValueError("Use validation examples for exploratory tool inspection, not protected test rows.")
    saved_report = json.loads((output / "report.json").read_text())
    if sha256((output / "model.keras").read_bytes()) != saved_report["model_sha256"]:
        raise ValueError("Model differs from the evaluated artifact recorded in report.json.")
    model = tf.keras.models.load_model(output / "model.keras")
    pixel = data["pixels"][index]
    cam = gradcam(model, pixel, target)
    occ = occlusion_grid(model, pixel)
    embedder = tf.keras.Model(model.inputs, model.get_layer("visual_features").output)
    train = np.flatnonzero(m.split == "train")
    ids = np.r_[index, train]
    embeddings = embedder(data["pixels"][ids, ..., None].astype(np.float32) / 255,
                         training=False).numpy().reshape(len(ids), -1)
    embeddings /= np.maximum(np.linalg.norm(embeddings, axis=1, keepdims=True), 1e-12)
    similarity = embeddings[1:] @ embeddings[0]
    chosen = train[np.argsort(-similarity)[:neighbors]]
    p = float(probabilities(model, pixel[None])[0])
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5), constrained_layout=True)
    axes[0].imshow(pixel, cmap="gray", vmin=0, vmax=255)
    axes[0].set_title(f"Validation input; P(closed)={p:.3f}")
    axes[1].imshow(pixel, cmap="gray", vmin=0, vmax=255)
    axes[1].imshow(cam, extent=(-.5, 63.5, 63.5, -.5), cmap="magma", alpha=.55,
                   interpolation="bilinear", vmin=0, vmax=1)
    axes[1].set_title(f"Coarse Grad-CAM, target {target}")
    vmax = max(float(abs(occ).max()), 1e-6)
    image = axes[2].imshow(occ, cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    axes[2].set_title("P(closed) before − after replacement")
    fig.colorbar(image, ax=axes[2])
    figure_id = str(m.iloc[index].derivative_id) + f"_target{target}"
    fig.savefig(output / f"inspection_{figure_id}.png", dpi=150, bbox_inches="tight")
    plt.show()
    fig2, ax2 = plt.subplots(1, neighbors, figsize=(3 * neighbors, 3), squeeze=False)
    for ax, row_id in zip(ax2.ravel(), chosen):
        ax.imshow(data["pixels"][row_id], cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"Training gallery\n{m.iloc[row_id].derivative_id}", fontsize=9)
    fig2.savefig(output / f"gallery_{figure_id}.png", dpi=150, bbox_inches="tight")
    plt.show()
    record = {"derivative_id": str(m.iloc[index].derivative_id), "split": "validation",
              "probability_eyes_closed": p, "attribution_target": int(target),
              "model_sha256": sha256((output / "model.keras").read_bytes()),
              "pixel_sha256": sha256(pixel.tobytes()), "quality": quality_flags(pixel),
              "nearest_training_derivatives": m.iloc[chosen].derivative_id.tolist(),
              "retrieval": "cosine similarity of flattened trained convolutional features",
              "occlusion_replacement": "16x16 pixels set to 128; not a brain intervention",
              "decision": "review_required", "generated_by_vlm": False}
    write_json(output / "last_validation_inspection.json", record)
    return record


def check_review_response(response, derivative_id, panel_ids):
    """Schema/evidence-reference guard, not a claim validator or VLM call."""
    required = {"derivative_id", "category", "evidence_panels", "review_status"}
    if not isinstance(response, dict) or set(response) != required:
        raise ValueError("Review response must contain exactly the four declared fields.")
    if response["derivative_id"] != derivative_id:
        raise ValueError("Wrong derivative reference.")
    if response["category"] not in {"eyes_open_candidate", "eyes_closed_candidate", "defer"}:
        raise ValueError("Unsupported category.")
    refs = response["evidence_panels"]
    if not isinstance(refs, list) or not all(isinstance(x, str) for x in refs):
        raise ValueError("Evidence references must be a list of strings.")
    if not set(refs).issubset(set(panel_ids)) or response["review_status"] != "pending":
        raise ValueError("Unsupported evidence reference or bypassed review.")
    return True
