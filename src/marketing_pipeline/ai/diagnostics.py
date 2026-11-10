from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def parse_logs(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    events = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try: events.append(json.loads(line))
        except json.JSONDecodeError:
            events.append({"level": "ERROR", "message": "Malformed log line",
                           "line_number": line_number, "error_type": "LogParseError"})
    return events


def deterministic_diagnostic(events: list[dict[str, Any]]) -> dict[str, Any]:
    levels = Counter(e.get("level", "UNKNOWN") for e in events)
    errors = [e for e in events if e.get("level") in {"ERROR", "CRITICAL"}]
    warnings = [e for e in events if e.get("level") == "WARNING"]
    sources_seen = sorted({e["source"] for e in events if e.get("source")})
    expected = {"google_ads", "meta_ads", "ga4", "crm"}
    missing_sources = sorted(expected - set(sources_seen))
    findings = []
    for item in errors[-10:]:
        findings.append({"severity": "high", "category": item.get("error_type", "pipeline_error"),
                         "evidence": item.get("message", "Unknown error"),
                         "recommended_action": "Inspect the named stage and rerun idempotently after correction."})
    if missing_sources:
        findings.append({"severity": "medium", "category": "missing_source_logs",
                         "evidence": f"No extraction events found for: {', '.join(missing_sources)}",
                         "recommended_action": "Confirm connector scheduling and date window."})
    status = "critical" if errors else ("warning" if warnings or missing_sources else "healthy")
    return {"generated_at": datetime.now(UTC).isoformat(), "mode": "deterministic_fallback",
            "status": status, "event_counts": dict(levels), "sources_seen": sources_seen,
            "findings": findings or [{"severity": "info", "category": "no_errors",
                                      "evidence": "No error events detected.",
                                      "recommended_action": "Continue scheduled monitoring."}]}


def enhance_with_claude(report: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    """Optional AI review. Raw credentials are never logged or placed in the prompt."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key: return report
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        response = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"), max_tokens=700,
            system="You are a data pipeline reliability reviewer. Return JSON only with keys summary, risks, next_actions. Do not invent evidence.",
            messages=[{"role": "user", "content": json.dumps({"fallback_report": report,
                       "recent_sanitized_events": events[-30:]}, default=str)}])
        text = response.content[0].text
        report["ai_review"] = json.loads(text)
        report["mode"] = "claude_enhanced"
    except Exception as exc:  # noqa: BLE001 - safe degradation is the feature boundary
        report["ai_enhancement_error"] = type(exc).__name__
        report["mode"] = "deterministic_fallback_after_ai_error"
    return report


def diagnose(path: Path, use_ai: bool = True) -> dict[str, Any]:
    events = parse_logs(path)
    report = deterministic_diagnostic(events)
    return enhance_with_claude(report, events) if use_ai else report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, default=Path("logs/pipeline.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("logs/diagnostic_summary.json"))
    parser.add_argument("--no-ai", action="store_true")
    args = parser.parse_args()
    result = diagnose(args.log, not args.no_ai)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__": main()

