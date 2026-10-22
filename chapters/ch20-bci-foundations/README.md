# Chapter 20: Foundations of Brain–Computer Interfaces

Build a decoder, replay a stream, separate scores from commands, and inspect failure behavior. Start with [three guided notebooks](NOTEBOOK_GUIDE.md), then the [100-point assignment](ASSIGNMENT.md).

The public-data route uses PhysioNet EEGMMIDB S001 R04/R08/R12 (imagined left/right fist). It is hardware-free: Python 3.11+, a CPU, Jupyter or Colab, and public downloads. No EEG headset, GPU, API key, flicker, participant recruitment, or stimulation is needed.

| Notebook | Main outcome |
|---|---|
| [01](01_decode_public_eeg.ipynb) | Source/run contract, causal band-power baseline, train/validation manifest |
| [02](02_replay_and_command_policy.ipynb) | R08 causal replay, bounded virtual cursor, argmax vs gated commands |
| [03](03_faults_and_validation.ipynb) | Gap/stale/flat-channel faults, fail-stop inspection, frozen R12 evaluation |

Local setup from this folder:
```bash
python -m venv .venv
# Activate .venv using your platform's instructions.
python -m pip install -r requirements-notebooks.txt jupyterlab
python -m jupyter lab
```
On Windows, activate with `.venv\Scripts\activate`; on macOS/Linux use `source .venv/bin/activate`.

Run cells in order. The loader downloads only the three specified EDFs when not cached and preserves the originals. Outputs are unique JSON files under `bci_outputs/`. The helpers do not run when this guide is read.

The checked-in notebooks have empty outputs. Materials were statically reviewed; no runtime performance is asserted. Package ranges are compatibility targets, not a tested lockfile; record installed versions. See the [exact replay contract](REPLAY_CONTRACT.md), [reflection](REFLECTION.md), and [primary resources](RESOURCES.md).

This is recorded-data software replay. It does not establish spontaneous-intent decoding, physical feedback timing, user learning, clinical efficacy, or an operational device safety case. The independent safety supervisor and live timing validation discussed in the book are further engineering work.
