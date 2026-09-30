"""Create latency and throughput charts from measurements.csv."""

import csv
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).parent
rows = list(csv.DictReader((ROOT / "measurements.csv").open(encoding="utf-8")))
rows = [row for row in rows if row["p95_ms"]]
if not rows:
    raise SystemExit("measurements.csv has no completed rows")

for scenario in sorted({row["scenario"] for row in rows}):
    selected = [row for row in rows if row["scenario"] == scenario]
    labels = [f"{row['cache_mode']} / {row['vus']}" for row in selected]
    x = range(len(labels))
    figure, axes = plt.subplots(1, 2, figsize=(12, 4))
    axes[0].plot(list(x), [float(row["throughput_rps"]) for row in selected], marker="o")
    axes[0].set_title(f"{scenario}: throughput")
    axes[0].set_ylabel("RPS")
    axes[1].plot(list(x), [float(row["p50_ms"]) for row in selected], marker="o", label="p50")
    axes[1].plot(list(x), [float(row["p95_ms"]) for row in selected], marker="o", label="p95")
    axes[1].plot(list(x), [float(row["p99_ms"]) for row in selected], marker="o", label="p99")
    axes[1].set_title(f"{scenario}: latency percentiles")
    axes[1].set_ylabel("milliseconds")
    axes[1].legend()
    for axis in axes:
        axis.set_xticks(list(x), labels, rotation=45, ha="right")
        axis.grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(ROOT / f"{scenario}-metrics.png", dpi=150)
