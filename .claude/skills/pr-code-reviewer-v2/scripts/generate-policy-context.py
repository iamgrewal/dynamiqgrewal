#!/usr/bin/env python3
"""
Generate OPA Policy Context

Generates JSON context for Open Policy Agent evaluation from PR data.

Usage:
    python3 generate-policy-context.py --pr 1234 --repo org/repo > pr-context.json
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


def run_gh_command(args: List[str]) -> Optional[Dict]:
    """Run a gh CLI command and return parsed JSON output."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout) if result.stdout else None
    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e.stderr}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        return None


def get_pr_data(repo: str, pr_number: int) -> Dict[str, Any]:
    """Fetch PR data from GitHub."""
    pr = run_gh_command([
        "api",
        f"repos/{repo}/pulls/{pr_number}"
    ])
    return pr or {}


def get_pr_files(repo: str, pr_number: int) -> List[Dict]:
    """Fetch list of files changed in PR."""
    files = run_gh_command([
        "api",
        f"repos/{repo}/pulls/{pr_number}/files"
    ])
    return files or []


def get_pr_reviews(repo: str, pr_number: int) -> List[Dict]:
    """Fetch PR reviews."""
    reviews = run_gh_command([
        "api",
        f"repos/{repo}/pulls/{pr_number}/reviews"
    ])
    return reviews or []


def analyze_changes(files: List[Dict]) -> Dict[str, Any]:
    """Analyze file changes for risk patterns."""
    auth_patterns = ['auth', 'login', 'password', 'token', 'session', 'jwt', 'oauth']
    crypto_patterns = ['crypto', 'encrypt', 'decrypt', 'hash', 'cipher', 'key']
    pii_patterns = ['email', 'phone', 'address', 'ssn', 'name', 'dob']
    access_patterns = ['permission', 'role', 'rbac', 'acl', 'policy']

    changes = {
        "files": [],
        "new_lines": 0,
        "deleted_lines": 0,
        "new_test_lines": 0,
        "auth_modified": False,
        "crypto_modified": False,
        "pii_modified": False,
        "access_control_modified": False,
        "risk_level": "low"
    }

    for f in files:
        filename = f.get("filename", "").lower()
        changes["files"].append(f.get("filename"))
        changes["new_lines"] += f.get("additions", 0)
        changes["deleted_lines"] += f.get("deletions", 0)

        # Check for test files
        if "test" in filename or "spec" in filename:
            changes["new_test_lines"] += f.get("additions", 0)

        # Check for sensitive patterns
        for pattern in auth_patterns:
            if pattern in filename:
                changes["auth_modified"] = True
                break

        for pattern in crypto_patterns:
            if pattern in filename:
                changes["crypto_modified"] = True
                break

        for pattern in pii_patterns:
            if pattern in filename:
                changes["pii_modified"] = True
                break

        for pattern in access_patterns:
            if pattern in filename:
                changes["access_control_modified"] = True
                break

    # Calculate risk level
    risk_score = 0
    if changes["auth_modified"]:
        risk_score += 3
    if changes["crypto_modified"]:
        risk_score += 3
    if changes["pii_modified"]:
        risk_score += 2
    if changes["access_control_modified"]:
        risk_score += 2
    if changes["new_lines"] > 500:
        risk_score += 1

    if risk_score >= 5:
        changes["risk_level"] = "high"
    elif risk_score >= 2:
        changes["risk_level"] = "medium"
    else:
        changes["risk_level"] = "low"

    return changes


def analyze_reviews(reviews: List[Dict]) -> Dict[str, Any]:
    """Analyze PR reviews for approvals."""
    review = {
        "approvals": [],
        "security_approved": False,
        "dpo_approved": None,
        "compliance_approved": None
    }

    for r in reviews:
        if r.get("state") == "APPROVED":
            review["approvals"].append(r.get("user", {}).get("login", "unknown"))

        # Check for security team approval (would need team mapping)
        # This is a placeholder - real implementation would check team membership

    return review


def detect_dependencies(repo: str, pr_number: int) -> List[Dict]:
    """Detect dependency changes in PR."""
    dependencies = []

    # This would integrate with dependency scanning tools
    # Placeholder implementation

    return dependencies


def run_security_scan(repo: str, pr_number: int) -> Dict[str, Any]:
    """Run security scan on PR."""
    scan = {
        "secrets_detected": False,
        "sql_injection_risks": [],
        "command_injection_risks": [],
        "outdated_dependencies": []
    }

    # This would integrate with security scanning tools
    # Placeholder implementation

    return scan


def get_coverage_metrics(repo: str, pr_number: int) -> Dict[str, float]:
    """Get test coverage metrics."""
    coverage = {
        "line_coverage": 0.0,
        "branch_coverage": 0.0,
        "critical_path_coverage": 0.0
    }

    # This would integrate with coverage tools
    # Placeholder implementation

    return coverage


def get_quality_metrics(repo: str, pr_number: int) -> Dict[str, int]:
    """Get code quality metrics."""
    metrics = {
        "cyclomatic_complexity": 0,
        "todo_count": 0
    }

    # This would integrate with quality analysis tools
    # Placeholder implementation

    return metrics


def generate_context(repo: str, pr_number: int) -> Dict[str, Any]:
    """Generate full policy context for OPA evaluation."""
    pr_data = get_pr_data(repo, pr_number)
    files = get_pr_files(repo, pr_number)
    reviews = get_pr_reviews(repo, pr_number)

    changes = analyze_changes(files)
    review_status = analyze_reviews(reviews)
    dependencies = detect_dependencies(repo, pr_number)
    scan = run_security_scan(repo, pr_number)
    coverage = get_coverage_metrics(repo, pr_number)
    metrics = get_quality_metrics(repo, pr_number)

    context = {
        "pr_number": pr_number,
        "repository": repo,
        "author": pr_data.get("user", {}).get("login", "unknown"),
        "branch": pr_data.get("head", {}).get("ref", "unknown"),

        "changes": changes,
        "dependencies": dependencies,
        "scan": scan,
        "coverage": coverage,
        "metrics": metrics,
        "review": review_status,

        "gates": {
            "unit_tests": "pending",
            "integration_tests": "pending",
            "security_scan": "passed" if not scan["secrets_detected"] else "failed",
            "code_review": "approved" if len(review_status["approvals"]) >= 2 else "pending"
        },

        "deployment": {
            "environment": "staging",
            "min_approvals": 2,
            "canary_enabled": False
        },

        "thresholds": {
            "min_line_coverage": 80,
            "max_complexity": 15,
            "max_todos": 10
        },

        "change_freeze": {
            "active": False
        },

        "recent_deployments": [],

        "generated_at": datetime.utcnow().isoformat()
    }

    return context


def main():
    parser = argparse.ArgumentParser(description="Generate OPA policy context for PR")
    parser.add_argument("--pr", type=int, required=True, help="PR number")
    parser.add_argument("--repo", type=str, required=True, help="Repository (org/repo)")
    parser.add_argument("--output", type=str, help="Output file (default: stdout)")

    args = parser.parse_args()

    context = generate_context(args.repo, args.pr)

    output = json.dumps(context, indent=2)

    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)


if __name__ == "__main__":
    main()
