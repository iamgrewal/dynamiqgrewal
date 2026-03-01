#!/usr/bin/env python3
"""
Log Decision

Appends AI decision to audit log in JSON format for SOC 2/ISO 27001 compliance.

Usage:
    python3 log-decision.py --decision-id uuid --decision-type PR_REVIEW \
        --agent-id pr-code-reviewer --confidence 0.87 --decision APPROVE \
        --input pr-context.json --output decision-log.jsonl
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def load_input(input_path: str) -> Dict[str, Any]:
    """Load input context from file."""
    try:
        with open(input_path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input: {e}", file=sys.stderr)
        return {}


def create_decision_log(
    decision_type: str,
    agent_id: str,
    agent_version: str,
    model: str,
    trust_tier: str,
    confidence: float,
    decision: str,
    input_context: Dict[str, Any],
    analysis: Dict[str, Any],
    policy_evaluation: Dict[str, Any],
    action_taken: Dict[str, Any],
    human_override: bool = False,
    override_reason: Optional[str] = None
) -> Dict[str, Any]:
    """Create structured decision log entry."""

    return {
        "decision_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "decision_type": decision_type,
        "agent_id": agent_id,
        "agent_version": agent_version,
        "model": model,
        "trust_tier": trust_tier,

        "input": {
            "pr_number": input_context.get("pr_number"),
            "repository": input_context.get("repository"),
            "files_changed": len(input_context.get("changes", {}).get("files", [])),
            "lines_added": input_context.get("changes", {}).get("new_lines", 0),
            "lines_deleted": input_context.get("changes", {}).get("deleted_lines", 0)
        },

        "analysis": analysis,

        "policy_evaluation": policy_evaluation,

        "confidence_score": confidence,
        "decision": decision,

        "action_taken": action_taken,

        "human_override": human_override,
        "override_reason": override_reason,

        "audit": {
            "schema_version": "1.0.0",
            "compliance": ["SOC2", "ISO27001"],
            "retention_years": 3 if trust_tier == "T3" else 1
        }
    }


def append_to_log(decision: Dict[str, Any], log_dir: str) -> str:
    """Append decision to daily log file."""
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create daily log file
    today = datetime.utcnow().strftime("%Y-%m-%d")
    log_file = log_path / f"decisions-{today}.jsonl"

    # Append as JSONL
    with open(log_file, "a") as f:
        f.write(json.dumps(decision) + "\n")

    return str(log_file)


def main():
    parser = argparse.ArgumentParser(description="Log AI decision for compliance")
    parser.add_argument("--decision-id", type=str, help="Existing decision ID (generates new if not provided)")
    parser.add_argument("--decision-type", type=str, required=True,
                       choices=["PR_REVIEW", "SECURITY_GATE", "CANARY_PROMOTION", "ROLLBACK", "TEST_TRIAGE"])
    parser.add_argument("--agent-id", type=str, required=True)
    parser.add_argument("--agent-version", type=str, default="1.0.0")
    parser.add_argument("--model", type=str, default="claude-sonnet-4-5-20250929")
    parser.add_argument("--trust-tier", type=str, default="T1", choices=["T0", "T1", "T2", "T3"])
    parser.add_argument("--confidence", type=float, required=True)
    parser.add_argument("--decision", type=str, required=True)
    parser.add_argument("--input", type=str, help="Path to input context JSON")
    parser.add_argument("--analysis", type=str, help="Path to analysis JSON")
    parser.add_argument("--policy-result", type=str, help="Path to policy evaluation JSON")
    parser.add_argument("--action", type=str, help="Path to action taken JSON")
    parser.add_argument("--log-dir", type=str, default=".ai-cicd/logs")
    parser.add_argument("--human-override", action="store_true")
    parser.add_argument("--override-reason", type=str)

    args = parser.parse_args()

    # Load inputs
    input_context = load_input(args.input) if args.input else {}
    analysis = load_input(args.analysis) if args.analysis else {}
    policy_evaluation = load_input(args.policy_result) if args.policy_result else {"allow": True, "deny": []}
    action_taken = load_input(args.action) if args.action else {}

    # Create decision log
    decision = create_decision_log(
        decision_type=args.decision_type,
        agent_id=args.agent_id,
        agent_version=args.agent_version,
        model=args.model,
        trust_tier=args.trust_tier,
        confidence=args.confidence,
        decision=args.decision,
        input_context=input_context,
        analysis=analysis,
        policy_evaluation=policy_evaluation,
        action_taken=action_taken,
        human_override=args.human_override,
        override_reason=args.override_reason
    )

    # Override ID if provided
    if args.decision_id:
        decision["decision_id"] = args.decision_id

    # Append to log
    log_file = append_to_log(decision, args.log_dir)

    # Output
    output = {
        "decision_id": decision["decision_id"],
        "logged_to": log_file,
        "timestamp": decision["timestamp"]
    }
    print(json.dumps(output))


if __name__ == "__main__":
    main()
