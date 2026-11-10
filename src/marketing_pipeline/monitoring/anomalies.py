from __future__ import annotations

from collections import defaultdict
from statistics import mean, pstdev
from typing import Any


def detect_anomalies(rows: list[dict[str, Any]], metric: str = "spend",
                     threshold: float = 2.0) -> list[dict[str, Any]]:
    """Flag per-source values more than threshold standard deviations from baseline."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows: groups[row["source"]].append(row)
    anomalies = []
    for source, items in groups.items():
        values = [float(item[metric]) for item in items]
        baseline, sigma = mean(values), pstdev(values)
        if sigma == 0: continue
        for item, value in zip(items, values):
            z = abs(value - baseline) / sigma
            if z > threshold:
                anomalies.append({"event_date": item["event_date"], "source": source,
                                  "metric": metric, "observed_value": value,
                                  "baseline_value": round(baseline, 2),
                                  "severity": "high" if z >= 3 else "medium",
                                  "description": f"{metric} z-score {z:.2f} exceeds {threshold:.1f}"})
    return anomalies

