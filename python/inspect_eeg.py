from pathlib import Path
import mne

file_path = Path(
    r"C:\BCI_Neuromorphic_Car\dataset\A01T.gdf"
)

if not file_path.exists():
    raise FileNotFoundError(
        f"EEG file not found: {file_path}"
    )

raw = mne.io.read_raw_gdf(
    str(file_path),
    preload=True,
    verbose="ERROR"
)

print("Sampling frequency:", raw.info["sfreq"], "Hz")
print("Total channels:", len(raw.ch_names))
print("Duration:", round(raw.times[-1], 2), "seconds")
print("Channel names:", raw.ch_names)

print("\nAnnotations:")
print(raw.annotations)

events, event_id = mne.events_from_annotations(raw)

print("\nEvent labels:")
print(event_id)

print("\nFirst 20 events:")
print(events[:20])

print("\nEEG inspection completed.")