import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/latency_measurements.csv")
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if not input_path.exists():
        raise SystemExit(f"{input_path} not found. Run src/collect_latency.py first.")

    df = pd.read_csv(input_path)
    df["round_trip_ms"] = pd.to_numeric(df["round_trip_ms"], errors="coerce")
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["round_trip_ms", "timestamp_utc"])
    if df.empty:
        raise SystemExit("No valid latency measurements were found.")

    summary = df.groupby("endpoint")["round_trip_ms"].agg(
        samples="count", mean_ms="mean",
        p50_ms=lambda x: x.quantile(0.50),
        p95_ms=lambda x: x.quantile(0.95),
        p99_ms=lambda x: x.quantile(0.99), max_ms="max",
    ).round(2)
    df["hour_utc"] = df["timestamp_utc"].dt.floor("h")
    hourly = df.groupby(["endpoint", "hour_utc"])["round_trip_ms"].agg(
        samples="count", p50_ms=lambda x: x.quantile(0.50),
        p95_ms=lambda x: x.quantile(0.95),
    ).reset_index()

    report_dir = ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(report_dir / "latency_percentiles.csv")
    hourly.to_csv(report_dir / "latency_hourly.csv", index=False)
    ax = df.groupby(["timestamp_utc", "endpoint"])["round_trip_ms"].mean().unstack().plot(
        figsize=(10, 5), marker=".", title="HTTP round-trip time over time"
    )
    ax.set_xlabel("Timestamp (UTC)")
    ax.set_ylabel("Round-trip time (ms)")
    plt.tight_layout()
    plt.savefig(report_dir / "latency_over_time.png", dpi=160)
    print(summary.to_string())
    print(f"Reports saved to {report_dir}")


if __name__ == "__main__":
    main()
