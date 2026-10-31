from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "sample_episodes.csv"
REPORT_DIR = ROOT / "reports"

FEATURES = [
    "duration_s", "mean_speed_mps", "speed_std_mps", "idle_ratio",
    "jerk_rms", "tracking_error_m", "packet_loss_ratio", "motor_temp_c",
]


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    required = set(FEATURES + ["episode_id", "timestamp"])
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    if df[FEATURES].isna().any().any():
        raise ValueError("Telemetry features contain missing values; clean them first.")

    # Illustrative rules; tune using actual system limits and reviewed logs.
    df["flag_idle"] = df["idle_ratio"] >= 0.40
    df["flag_jerk"] = df["jerk_rms"] >= 2.00
    df["flag_tracking"] = df["tracking_error_m"] >= 0.12
    df["flag_network"] = df["packet_loss_ratio"] >= 0.10
    rule_columns = ["flag_idle", "flag_jerk", "flag_tracking", "flag_network"]
    df["rule_flag"] = df[rule_columns].any(axis=1)

    X_scaled = StandardScaler().fit_transform(df[FEATURES])
    detector = IsolationForest(n_estimators=200, contamination=0.12, random_state=42)
    detector.fit(X_scaled)
    df["iforest_flag"] = detector.predict(X_scaled) == -1
    df["anomaly_score"] = -detector.score_samples(X_scaled)
    df["review_flag"] = df["rule_flag"] | df["iforest_flag"]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(REPORT_DIR / "episode_flags.csv", index=False)
    summary = (
        f"Total episodes: {len(df)}\n"
        f"Rule-based flags: {int(df['rule_flag'].sum())}\n"
        f"Isolation Forest flags: {int(df['iforest_flag'].sum())}\n"
        f"Combined review queue: {int(df['review_flag'].sum())}\n"
        "Synthetic demo labels are not used to train the detector.\n"
    )
    (REPORT_DIR / "episode_summary.txt").write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    main()
