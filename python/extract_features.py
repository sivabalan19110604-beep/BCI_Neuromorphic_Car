
from pathlib import Path
import numpy as np
import mne

DATA = Path(r"C:\BCI_Neuromorphic_Car\dataset\A01T.gdf")
OUTPUT = Path(r"C:\BCI_Neuromorphic_Car\test_vectors")

if not DATA.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA}")

OUTPUT.mkdir(parents=True, exist_ok=True)

# Load recording and retain EEG channels only.
raw = mne.io.read_raw_gdf(
    str(DATA), preload=True, verbose="ERROR"
)
raw.pick(picks="eeg", exclude="bads")
raw.pick(
    picks=[
        ch for ch in raw.ch_names
        if ch not in ["EOG-left", "EOG-central", "EOG-right"]
    ]
)
print("EEG channels:", len(raw.ch_names))
print("Sampling rate:", raw.info["sfreq"], "Hz")

# Retain the motor-imagery frequency band.
raw.filter(8.0, 30.0, verbose="ERROR")

# Read the event markers.
events, event_id = mne.events_from_annotations(raw)

print("\nAvailable event labels:", event_id)

# Select the four actual motor-imagery cue labels.
cue_labels = {"769", "770", "771", "772"}
selected_ids = {
    label: code
    for label, code in event_id.items()
    if label.split("/")[-1] in cue_labels
}

if len(selected_ids) != 4:
    raise RuntimeError(
        f"Expected 4 motor-imagery cue labels; found {selected_ids}"
    )

selected = events[
    np.isin(events[:, 2], list(selected_ids.values()))
]

if len(selected) == 0:
    raise RuntimeError("No motor-imagery trials found.")

# Extract a 2-second window starting 0.5 s after the cue.
epochs = mne.Epochs(
    raw,
    selected,
    event_id=selected_ids,
    tmin=0.5,
    tmax=2.5,
    baseline=None,
    preload=True,
    reject_by_annotation=True,
    verbose="ERROR"
)

if len(epochs) == 0:
    raise RuntimeError("No valid EEG trials remain.")

# Select the first valid trial.
trial = epochs.get_data()[0]  # 22 channels x samples

# Compute one log-variance feature per EEG channel.
variance = np.var(trial, axis=1)
features = np.log(np.maximum(variance, 1e-20))

np.save(OUTPUT / "eeg_features.npy", features)
np.savetxt(
    OUTPUT / "eeg_features.txt",
    features,
    fmt="%.10f"
)

# Save the selected trial's actual cue label.
trial_code = int(epochs.events[0, 2])
trial_label = next(
    label for label, code in selected_ids.items()
    if code == trial_code
)

print("\n===== FEATURE EXTRACTION RESULT =====")
print("Valid trials:", len(epochs))
print("Selected trial label:", trial_label)
print("Feature vector shape:", features.shape)
print("Feature vector:")
print(features)
print("\nSaved:")
print(OUTPUT / "eeg_features.txt")
print(OUTPUT / "eeg_features.npy")
