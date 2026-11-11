from pathlib import Path
import numpy as np

BASE = Path(r"C:\BCI_Neuromorphic_Car")
INPUT = BASE / "test_vectors" / "eeg_features.npy"
OUTPUT = BASE / "test_vectors"

if not INPUT.exists():
    raise FileNotFoundError(
        f"Missing {INPUT}. Run extract_features.py first."
    )

features = np.load(INPUT).astype(np.float64)

if features.shape != (22,):
    raise ValueError(
        f"Expected 22 EEG features, received {features.shape}"
    )

if not np.all(np.isfinite(features)):
    raise ValueError("Features contain NaN or infinity.")

# Normalize the feature vector to [-1, 1].
maximum = np.max(np.abs(features))

if maximum == 0:
    normalized = np.zeros_like(features)
else:
    normalized = features / maximum

# Signed Q1.15 representation: scale by 32767.
fixed = np.round(normalized * 32767).astype(np.int16)

# Save decimal values for inspection.
np.savetxt(
    OUTPUT / "eeg_features_fixed.txt",
    fixed,
    fmt="%d"
)

# Save 16-bit two's-complement binary strings for Verilog.
with open(OUTPUT / "eeg_features_fixed.mem", "w") as f:
    for value in fixed:
        f.write(f"{int(value) & 0xFFFF:016b}\n")

print("Feature count:", len(fixed))
print("Fixed-point format: signed Q1.15")
print("Fixed-point values:")
print(fixed)
print("\nCreated:")
print(OUTPUT / "eeg_features_fixed.txt")
print(OUTPUT / "eeg_features_fixed.mem")