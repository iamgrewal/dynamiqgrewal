#!/usr/bin/env python3
"""
Evaluate Canary

Observability Agent canary health evaluation for AI-augmented CI/CD.

Usage:
    python3 evaluate-canary.py --service my-service --canary-weight 10 \
        --prometheus-url http://prometheus:9090 --confidence-threshold 0.8
"""

import argparse
import json
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error


@dataclass
class SLOThreshold:
    metric: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    def is_satisfied(self, value: float) -> bool:
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True


@dataclass
class MetricResult:
    metric: str
    value: float
    threshold: SLOThreshold
    satisfied: bool
    severity: str  # OK, WARNING, CRITICAL


def query_prometheus(url: str, query: str) -> Optional[float]:
    """Query Prometheus and return single value."""
    try:
        endpoint = f"{url}/api/v1/query"
        params = f"?query={query}"
        full_url = f"{endpoint}{params}"

        req = urllib.request.Request(full_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

            if data.get("status") != "success":
                return None

            results = data.get("data", {}).get("result", [])
            if not results:
                return None

            return float(results[0].get("value", [None, 0])[1])
    except (urllib.error.URLError, json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error querying Prometheus: {e}", file=sys.stderr)
        return None


def evaluate_canary(
    prometheus_url: str,
    service: str,
    canary_weight: int,
    slo_thresholds: List[SLOThreshold],
    duration_minutes: int = 5
) -> Dict[str, Any]:
    """Evaluate canary health against SLO thresholds."""

    results: List[MetricResult] = []
    failing_slos: List[Dict[str, Any]] = []

    for slo in slo_thresholds:
        # Build query based on metric type
        if slo.metric == "request-success-rate":
            query = f'''
                sum(rate(http_requests_total{{service="{service}",variant="canary",status!~"5.."}}[{duration_minutes}m])) /
                sum(rate(http_requests_total{{service="{service}",variant="canary"}}[{duration_minutes}m])) * 100
            '''
        elif slo.metric == "request-duration-p99":
            query = f'''
                histogram_quantile(0.99,
                    sum(rate(http_request_duration_seconds_bucket{{service="{service}",variant="canary"}}[{duration_minutes}m])) by (le)
                ) * 1000
            '''
        elif slo.metric == "request-duration-p50":
            query = f'''
                histogram_quantile(0.50,
                    sum(rate(http_request_duration_seconds_bucket{{service="{service}",variant="canary"}}[{duration_minutes}m])) by (le)
                ) * 1000
            '''
        elif slo.metric == "error-rate":
            query = f'''
                sum(rate(http_requests_total{{service="{service}",variant="canary",status=~"5.."}}[{duration_minutes}m])) /
                sum(rate(http_requests_total{{service="{service}",variant="canary"}}[{duration_minutes}m])) * 100
            '''
        else:
            continue

        value = query_prometheus(prometheus_url, query)

        if value is None:
            results.append(MetricResult(
                metric=slo.metric,
                value=-1,
                threshold=slo,
                satisfied=False,
                severity="CRITICAL"
            ))
            failing_slos.append({
                "metric": slo.metric,
                "value": None,
                "threshold": {"min": slo.min_value, "max": slo.max_value},
                "severity": "CRITICAL",
                "reason": "Unable to fetch metric"
            })
            continue

        satisfied = slo.is_satisfied(value)

        # Determine severity
        if satisfied:
            severity = "OK"
        elif slo.max_value is not None and value > slo.max_value * 1.1:
            severity = "CRITICAL"
        elif slo.min_value is not None and value < slo.min_value * 0.9:
            severity = "CRITICAL"
        else:
            severity = "WARNING"

        result = MetricResult(
            metric=slo.metric,
            value=value,
            threshold=slo,
            satisfied=satisfied,
            severity=severity
        )
        results.append(result)

        if not satisfied:
            failing_slos.append({
                "metric": slo.metric,
                "value": value,
                "threshold": {"min": slo.min_value, "max": slo.max_value},
                "severity": severity
            })

    # Calculate confidence score
    if not results:
        confidence = 0.0
    else:
        satisfied_count = sum(1 for r in results if r.satisfied)
        confidence = satisfied_count / len(results)

        # Reduce confidence for any CRITICAL issues
        critical_count = sum(1 for r in results if r.severity == "CRITICAL")
        if critical_count > 0:
            confidence *= (1 - 0.3 * critical_count)

    # Make decision
    decision = "ROLLBACK" if confidence < 0.8 else "PROMOTE"

    return {
        "service": service,
        "canary_weight": canary_weight,
        "duration_minutes": duration_minutes,
        "results": [
            {
                "metric": r.metric,
                "value": r.value,
                "threshold_min": r.threshold.min_value,
                "threshold_max": r.threshold.max_value,
                "satisfied": r.satisfied,
                "severity": r.severity
            }
            for r in results
        ],
        "failing_slos": failing_slos,
        "confidence_score": round(confidence, 3),
        "decision": decision,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


def create_decision_log(canary_result: Dict[str, Any]) -> Dict[str, Any]:
    """Create structured decision log for canary analysis."""

    return {
        "decision_id": str(uuid.uuid4()),
        "timestamp": canary_result["timestamp"],
        "decision_type": "CANARY_PROMOTION",
        "agent_id": "observability-agent",
        "agent_version": "1.0.0",
        "model": "observability-agent-v1",
        "trust_tier": "T2",

        "input": {
            "service": canary_result["service"],
            "canary_weight": canary_result["canary_weight"],
            "duration_minutes": canary_result["duration_minutes"]
        },

        "analysis": {
            "metrics_evaluated": len(canary_result["results"]),
            "slos_failing": len(canary_result["failing_slos"]),
            "results": canary_result["results"]
        },

        "policy_evaluation": {
            "policy": "canary-health",
            "result": "allow" if canary_result["decision"] == "PROMOTE" else "deny",
            "confidence_threshold": 0.8
        },

        "confidence_score": canary_result["confidence_score"],
        "decision": canary_result["decision"],

        "action_taken": {
            "rollback_triggered": canary_result["decision"] == "ROLLBACK",
            "notification_sent": True
        },

        "human_override": False,
        "override_reason": None
    }


def main():
    parser = argparse.ArgumentParser(description="Evaluate canary deployment health")
    parser.add_argument("--service", type=str, required=True, help="Service name")
    parser.add_argument("--canary-weight", type=int, default=10, help="Current canary weight percentage")
    parser.add_argument("--prometheus-url", type=str, default="http://localhost:9090")
    parser.add_argument("--confidence-threshold", type=float, default=0.8)
    parser.add_argument("--duration-minutes", type=int, default=5)
    parser.add_argument("--log-dir", type=str, default=".ai-cicd/logs")
    parser.add_argument("--output", type=str, help="Output file for decision log")

    args = parser.parse_args()

    # Default SLO thresholds
    slo_thresholds = [
        SLOThreshold("request-success-rate", min_value=99.9),
        SLOThreshold("request-duration-p99", max_value=200),
        SLOThreshold("request-duration-p50", max_value=50),
        SLOThreshold("error-rate", max_value=0.1),
    ]

    # Evaluate canary
    result = evaluate_canary(
        prometheus_url=args.prometheus_url,
        service=args.service,
        canary_weight=args.canary_weight,
        slo_thresholds=slo_thresholds,
        duration_minutes=args.duration_minutes
    )

    # Create decision log
    decision_log = create_decision_log(result)

    # Output
    output = {
        "canary_evaluation": result,
        "decision_log": decision_log
    }

    if args.output:
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
    else:
        print(json.dumps(output, indent=2))

    # Exit with error code if rollback recommended
    if result["decision"] == "ROLLBACK":
        sys.exit(1)


if __name__ == "__main__":
    main()
