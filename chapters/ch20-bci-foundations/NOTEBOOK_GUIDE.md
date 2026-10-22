# Three steps from EEG data to a BCI software prototype

| Stage | Learn | Keep |
|---|---|---|
| 1. Decode | T1/T2 semantics; six features; run-separated fitting | Source hashes, channel/units/rate contract, training/validation counts |
| 2. Replay | Causal stateful filtering; past-only buffer; score-to-command policy | Cursor trajectory, policy reasons, processing times, exposure denominators |
| 3. Challenge | Dropped samples, virtual packet delay, flat channel; held-out evaluation | Fault logs, inhibition checks, final configuration and report |

Open locally or in Colab:

1. [Notebook 01](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch20-bci-foundations/01_decode_public_eeg.ipynb) · [Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch20-bci-foundations/01_decode_public_eeg.ipynb)
2. [Notebook 02](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch20-bci-foundations/02_replay_and_command_policy.ipynb) · [Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch20-bci-foundations/02_replay_and_command_policy.ipynb)
3. [Notebook 03](https://github.com/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch20-bci-foundations/03_faults_and_validation.ipynb) · [Colab](https://colab.research.google.com/github/ZagElSayed/Introduction-to-Neuroinformatics/blob/main/chapters/ch20-bci-foundations/03_faults_and_validation.ipynb)

Each notebook can build its own experiment. Locally it prefers the adjacent helper; Colab retrieves the helper at an immutable source commit and checks its SHA-256 before import. Local edits remain visible through the helper checksum in every manifest. The bootstrap commit identifies the helper, not a claim about runtime results.

R04 trains, R08 develops/validates, and R12 is opened for final evaluation only after choices are frozen. The final-test cell intentionally requires setting `FROZEN=True`. That pause records a scientific decision, not a software installation step. No labels or cue identity are passed into the replay decoder or command policy; labels are used afterward for audit.

Model scores are not calibrated intent probabilities; three overlapping updates are not independent evidence. T0 is instructed rest, not an unrestricted idle benchmark. `processing_ms` excludes sensor/display hardware and includes no physical feedback measurement. Read [REPLAY_CONTRACT.md](REPLAY_CONTRACT.md) before interpreting a rate or latency.
