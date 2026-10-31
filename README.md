# Robot Telemetry Reliability & Anomaly Detection

A practical robotics analytics project that explores abnormal operating episodes and network responsiveness using telemetry-style data.

## Project goals
- Identify episodes that may need engineering review using interpretable telemetry rules.
- Detect unusual combinations of operating signals with Isolation Forest.
- Measure public HTTP endpoint round-trip time and compare median and tail latency (p50, p95, p99).

## Repository layout
```
data/
  sample_episodes.csv
src/
  analyze_episodes.py
  collect_latency.py
  analyze_latency.py
reports/
requirements.txt
```

## Setup
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## 1. Episode analysis
```bash
python src/analyze_episodes.py
``
Reads the included 360-row demonstration dataset and writes:
- `reports/episode_flags.csv`
- `reports/episode_summary.txt`

The pipeline checks idle ratio, jerk RMS, tracking error and packet loss with transparent rules, then applies Isolation Forest to scaled telemetry features. The synthetic demo labels are not used to fit the detector.

## 2. HTTP latency collection
```bash
python src/collect_latency.py --interval 60 --hours 2
``
The collector samples three public endpoints, records UTC timestamps, status codes, request round-trip milliseconds and request errors. Stop early with Ctrl+C; completed samples are flushed to disk.

Then run:
```bash
python src/analyze_latency.py
``
This creates endpoint-level percentiles, hourly p50/p95 summaries and a time-series plot under `reports/`.

## Data and interpretation
**The bundled episode data is synthetic**, generated to exercise the analysis workflow. It is not real robot telemetry and does not establish the performance or safety of any robot. The latency collector has to be run to create actual network measurements; no latency results are pre-claimed.

Public HTTP round-trip time is not the same as end-to-end robot command latency. A real robot control path also includes middleware, queues, compute, control-loop scheduling and actuation.

Rule thresholds and Isolation Forest's contamination setting are starting points for exploration. Flags are review candidates, not confirmed faults. Validate thresholds and model behaviour with labelled logs and engineering review before operational use.
