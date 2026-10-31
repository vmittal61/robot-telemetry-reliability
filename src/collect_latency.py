import argparse
import csv
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ENDPOINTS = {
    "cloudflare": "https://www.cloudflare.com/cdn-cgi/trace",
    "google": "https://www.google.com/generate_204",
    "httpbin": "https://httpbin.org/get",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect public HTTP endpoint round-trip measurements.")
    parser.add_argument("--interval", type=float, default=60)
    parser.add_argument("--hours", type=float, default=2)
    parser.add_argument("--timeout", type=float, default=10)
    parser.add_argument("--output", default="data/latency_measurements.csv")
    args = parser.parse_args()
    if min(args.interval, args.hours, args.timeout) <= 0:
        parser.error("interval, hours and timeout must be positive")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["timestamp_utc", "endpoint", "url", "status_code", "round_trip_ms", "error"]
    deadline = time.monotonic() + args.hours * 3600
    print(f"Sampling {len(ENDPOINTS)} endpoints every {args.interval:g}s for {args.hours:g}h. Ctrl+C stops safely.")

    with output.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        if output.stat().st_size == 0:
            writer.writeheader()
        try:
            while time.monotonic() < deadline:
                cycle_start = time.monotonic()
                for name, url in ENDPOINTS.items():
                    stamp = datetime.now(timezone.utc).isoformat()
                    start = time.perf_counter()
                    status_code, error = "", ""
                    try:
                        response = requests.get(url, timeout=args.timeout)
                        status_code = response.status_code
                    except requests.RequestException as exc:
                        error = type(exc).__name__
                    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
                    writer.writerow({
                        "timestamp_utc": stamp, "endpoint": name, "url": url,
                        "status_code": status_code, "round_trip_ms": elapsed_ms, "error": error,
                    })
                    handle.flush()
                    print(stamp, name, elapsed_ms, "ms", status_code or error)
                remaining = args.interval - (time.monotonic() - cycle_start)
                if remaining > 0:
                    time.sleep(remaining)
        except KeyboardInterrupt:
            print("\nCollection stopped; saved measurements are retained.")


if __name__ == "__main__":
    main()
