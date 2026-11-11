# BCI Neuromorphic Car

End-to-end pipeline from raw EEG to hardware: extracts motor-imagery features from the
BCI Competition IV 2a recording with MNE-Python, converts them to signed Q1.15 fixed
point, and streams them through a SystemVerilog feature reader with a self-checking
testbench.

## Repository layout

```
BCI_Neuromorphic_Car/
├── dataset/                # A01T.gdf goes here (not tracked, see dataset/README.md)
├── python/
│   ├── inspect_eeg.py      # Prints sampling rate, channels, events of the recording
│   ├── extract_features.py # 8-30 Hz filter -> epochs -> 22 log-variance features
│   └── convert_to_fixed.py # Normalize to [-1,1] -> signed Q1.15 -> binary .mem
├── rtl/
│   ├── eeg_feature_reader.sv     # Streams 22 signed 16-bit features from a .mem file
│   └── eeg_feature_reader_tb.sv  # Self-checking bench (PASS/FAIL on all 22 features)
├── test_vectors/           # eeg_features.npy/.txt, eeg_features_fixed.txt/.mem
└── BCI_Neuromorphic_Car/   # Vivado project (BCI_Neuromorphic_Car.xpr)
```

Vivado build artifacts (`.cache`, `.hw`, `.runs`, `.sim`, `.ip_user_files`, logs,
waveforms) and Python virtualenvs are gitignored.

## Data pipeline

1. **Get the dataset** — download `A01T.gdf` from the
   [BCI Competition IV dataset 2a](https://www.bbci.de/competition/iv/) page and place it
   in `dataset/` (33 MB, not stored in git).

2. **Inspect the recording**

   ```powershell
   python python/inspect_eeg.py
   ```

3. **Extract features**

   ```powershell
   python python/extract_features.py
   ```

   Loads the GDF, keeps the 22 EEG channels (EOG excluded), band-pass filters 8–30 Hz
   (motor-imagery band), epochs the four cue labels (769–772) over 0.5–2.5 s after the
   cue, and computes one log-variance feature per channel → `test_vectors/eeg_features.npy`
   and `.txt`.

4. **Convert to fixed point**

   ```powershell
   python python/convert_to_fixed.py
   ```

   Normalizes the vector to `[-1, 1]`, quantizes to signed **Q1.15**, and writes
   `test_vectors/eeg_features_fixed.mem` — 16-bit two's-complement binary strings ready
   for Verilog `$readmemb`.

## Hardware verification (Vivado)

1. Open `BCI_Neuromorphic_Car/BCI_Neuromorphic_Car.xpr` in Vivado.
2. Run behavioral simulation of `eeg_feature_reader_tb`.
3. The bench releases reset, asserts `start`, and prints every streamed feature. It ends
   with `PASS: All 22 EEG features were read.` when the reader delivers all 22 values.

### RTL interface

| Port | Direction | Description |
|------|-----------|-------------|
| `clk`, `rst`, `start` | in | 100 MHz clock, sync reset, begin streaming |
| `feature_out[15:0]` | out | Signed Q1.15 feature (one channel per cycle) |
| `feature_valid` | out | Pulse when `feature_out` is valid |
| `done` | out | High after the last of `CHANNELS` features |

Parameters: `CHANNELS = 22`, `WIDTH = 16`, `MEM_FILE` (defaults to the checked-in
`test_vectors/eeg_features_fixed.mem`).

> **Note:** the RTL and Python scripts use absolute paths (`C:\BCI_Neuromorphic_Car\...`).
> Adjust them if your checkout lives elsewhere.

## Requirements

- Python 3.13 with `mne` and `numpy` (`pip install mne numpy`)
- AMD Vivado for synthesis/simulation
