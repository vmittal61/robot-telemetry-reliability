# Robot Telemetry Reliability & Anomaly Detection

A practical robotics analytics project exploring unusual operating episodes and network responsiveness through telemetry-style data.

## What it does
- Flags episodes for engineering review using interpretable rules over idle ratio, jerk RMS, tracking error and packet loss.
- Uses Isolation Forest to surface unusual combinations of telemetry signals without fitting to the demo labels.
- Collects public HTTP endpoint round-trip time and reports p50, p95 and p99 latency.

## Repository structure
```
data/sample_episodes.csv
src/
  analyze_episodes.py
  collect_latency.py
  analyze_latency.py
  generate_demo_data.py
tests/test_demo_data.py
reports/                 # generated outputs
```

## Setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Analyse robot episodes
```bash
python src/analyze_episodes.py
``
Reads 360 synthetic demonstration episodes and creates:
- `reports/episode_flags.csv` — rule flags, Isolation Forest flags, anomaly score and review flag.
- `reports/episode_summary.txt` — episode and flag counts.
- `reports/rule_flag_counts.png` — counts by rule-triggered pattern.
- `reports/idle_vs_jerk.png` — relationship between two telemetry signals and review status.

The detector is fitted only on telemetry features. The `demo_anomaly_label` column is intentionally not used in training.

## 2. Collect HTTP latency
```bash
python src/collect_latency.py --interval 60 --hours 2
``
Samples three public endpoints, recording UTC timestamp, endpoint, status code, request round-trip time and request errors. Stop with Ctrl+C; collected rows are flushed to disk.

Analyse the measurements:
```bash
python src/analyze_latency.py
``
Creates endpoint-level percentiles, hourly p50/p95 summaries and `reports/latency_over_time.png`.

## Interview preparation
See [INTERVIEW_NOTES.md](INTERVIEW_NOTES.md) for definitions of the telemetry features, Isolation Forest rationale, percentile interpretation and limitations to explain accurately.

## Data and limitations
The bundled episode data is **synthetic** and intended to demonstrate the analysis workflow. It is not real robot telemetry and does not establish performance or safety of any robot. The latency collector must be run to create measurements; the repository does not claim measured latency results.

Public HTTP round-trip time is not end-to-end robot command latency. A deployed robot control path also includes middleware, queues, compute, control-loop scheduling and actuation. The endpoints are public services, not guaranteed geographically fixed robot data centres.

Rule thresholds and Isolation Forest's 12% contamination setting are illustrative. A flag means "review this episode", not "confirmed fault". Validate thresholds and model behaviour against labelled system logs and engineering review before operational use.
