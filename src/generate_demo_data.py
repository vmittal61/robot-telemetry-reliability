"""Generate deterministic synthetic telemetry episodes for demonstration."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(42)
n = 360
idle = np.clip(rng.beta(2, 12, n), 0, 0.8)
jerk = np.clip(rng.lognormal(np.log(0.85), 0.35, n), 0.2, 3.0)
speed_std = np.clip(rng.normal(0.13, 0.045, n), 0.02, 0.35)
tracking = np.clip(rng.normal(0.035, 0.018, n), 0.002, 0.15)
packet_loss = np.clip(rng.beta(1.2, 35, n), 0, 0.25)
temperature = rng.normal(48, 6, n)
demo_label = np.zeros(n, dtype=int)

for index in rng.choice(n, 48, replace=False):
    demo_label[index] = 1
    mode = rng.integers(0, 4)
    if mode == 0:
        idle[index] = rng.uniform(0.45, 0.85)
    elif mode == 1:
        jerk[index] = rng.uniform(2.2, 4.2)
        speed_std[index] = rng.uniform(0.28, 0.5)
    elif mode == 2:
        tracking[index] = rng.uniform(0.13, 0.3)
    else:
        packet_loss[index] = rng.uniform(0.12, 0.35)
        temperature[index] = rng.uniform(65, 82)

df = pd.DataFrame({
    "episode_id": [f"EP{i:04d}" for i in range(1, n + 1)],
    "timestamp": pd.date_range("2026-10-20 08:00", periods=n, freq="12min").astype(str),
    "duration_s": rng.uniform(25, 180, n).round(2),
    "mean_speed_mps": np.clip(rng.normal(0.72, 0.16, n), 0.12, 1.2).round(3),
    "speed_std_mps": speed_std.round(3),
    "idle_ratio": idle.round(3),
    "jerk_rms": jerk.round(3),
    "tracking_error_m": tracking.round(4),
    "packet_loss_ratio": packet_loss.round(3),
    "motor_temp_c": temperature.round(1),
    "demo_anomaly_label": demo_label,
})
path = ROOT / "data" / "sample_episodes.csv"
path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(path, index=False)
print(f"Wrote {len(df)} synthetic episodes to {path}")
