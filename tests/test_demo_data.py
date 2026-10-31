from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
df = pd.read_csv(ROOT / "data" / "sample_episodes.csv")
required = {
    "episode_id", "timestamp", "duration_s", "mean_speed_mps", "speed_std_mps",
    "idle_ratio", "jerk_rms", "tracking_error_m", "packet_loss_ratio",
    "motor_temp_c", "demo_anomaly_label",
}
assert len(df) == 360, f"Expected 360 demo episodes, found {len(df)}"
assert required.issubset(df.columns)
assert df["episode_id"].is_unique
assert int(df["demo_anomaly_label"].sum()) == 48
assert not df[list(required - {"episode_id", "timestamp"})].isna().any().any()
print("Telemetry demo dataset checks passed.")
