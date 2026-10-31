# Interview Notes

## 30-second project explanation
"I built a small telemetry analytics pipeline for robot operating episodes. It uses simple engineering rules to flag interpretable behaviours such as excessive idle time, jerk, tracking error and packet loss, and Isolation Forest to identify unusual combinations across several signals. Separately, I wrote a collector for public HTTP endpoint round-trip time and an analysis script for p50, p95 and p99. The bundled episode data is synthetic, so I treat the outputs as a demonstration of the method rather than evidence from a real robot."

## What is an episode?
For this project, one row represents one bounded robot operating segment or task run. A real system would define episode boundaries from task-start/task-end events, a mission identifier, or a state transition. The example CSV is synthetic.

## Telemetry features
- **Idle ratio:** fraction of an episode spent idle or near zero commanded/actual motion.
- **Jerk RMS:** root-mean-square jerk; jerk is the rate of change of acceleration. High jerk can correspond to abrupt motion, but the acceptable level depends on platform and task.
- **Tracking error:** difference between desired and measured position/trajectory.
- **Packet-loss ratio:** fraction of transmitted packets that were not received.
- **Speed variation:** standard deviation of speed during the episode.
- **Motor temperature:** a contextual signal that may help identify thermal stress.

## Why rules plus Isolation Forest?
Rules are transparent and easy to explain. They identify known suspicious conditions, but independent thresholds can miss combinations that are unusual together. Isolation Forest is an unsupervised tree-based method that tends to isolate rare, different points in fewer splits. It can surface multivariate outliers without anomaly labels, but it can also flag harmless rare behaviour. The union of both sets forms a **review queue**, not a fault diagnosis.

## Why not train on demo labels?
The demo labels were artificially assigned to produce examples of abnormal-looking signals. They are not ground-truth annotations from robotics engineers. Training or reporting validation metrics against them would create a misleading impression of model quality. The detector deliberately ignores that column.

## Why p50, p95 and p99?
- **p50:** typical midpoint latency.
- **p95:** 95% of observed requests completed at or below this value.
- **p99:** highlights the slowest tail of the observed requests.

Average latency can hide occasional long delays. Tail latency matters in interactive systems because sporadic delays can make responses feel inconsistent. Percentiles become noisy with small samples, so longer collection windows and enough samples are needed before drawing conclusions.

## What exactly does the latency collector measure?
It measures elapsed time around a synchronous HTTP GET request using a monotonic high-resolution timer. The result includes client-to-endpoint network travel and server/request handling as observed from the machine running the script. It is **not** a measurement of robot command-to-actuation latency or a controlled comparison of geographic regions. Public endpoints may route to changing CDN edges, and results depend on local network conditions, DNS, TLS, server load and the collection machine.

## Honest limitations to say out loud
- The bundled 360 episodes are synthetic; there are no real robot logs in this repository.
- Rule thresholds and the Isolation Forest contamination fraction are illustrative choices, not validated operating limits.
- Anomaly flags need manual review by someone who understands the robot and task.
- Public HTTP latency is only a network/request experiment, not robot-control latency.
- A two-hour, once-per-minute run gives a limited sample; p99 estimates are especially unstable with small sample counts.

## Questions to prepare for
1. How would you define episode boundaries from a real robot log?
2. What is the difference between acceleration and jerk?
3. Why standardise features before this model? Standardisation makes the feature magnitudes comparable in the pipeline; tree-based Isolation Forest is generally less scale-sensitive than distance-based models.
4. What causes false positives? Rare but valid manoeuvres, task differences, sensor noise, bad thresholds or a mismatch between the training/demo distribution and real operation.
5. How would you improve it with real data? Collect timestamped logs, define operating modes, annotate incidents with domain experts, tune thresholds by task, evaluate precision/recall on a held-out labelled set, and monitor drift.
