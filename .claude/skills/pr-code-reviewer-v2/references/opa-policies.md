# Open Policy Agent (OPA) Policy Reference

Policy-as-code guardrails for AI-augmented CI/CD pipelines.

## Overview

OPA policies define hard constraints that AI agents cannot override. These policies are evaluated before any AI recommendation is acted upon.

## Policy Structure

```
policies/
├── security.rego      # Security hard constraints
├── deployment.rego    # Deployment gate policies
├── quality.rego       # Quality gate policies
└── compliance.rego    # Compliance requirements
```

## Security Policy

### security.rego

```rego
package cicd.security

import future.keywords.if

# Default deny
default allow := false

# Allow if no deny rules trigger
allow if {
    not deny
}

# Deny rules - these BLOCK deployment regardless of AI recommendation

# Deny if critical CVEs exist in dependencies
deny contains msg if {
    input.dependencies[_].cves[_].severity == "CRITICAL"
    msg := sprintf("Critical CVE found in dependency %s: %s", [
        input.dependencies[_].name,
        input.dependencies[_].cves[_].id
    ])
}

# Deny if secrets are detected in code
deny contains msg if {
    input.scan.secrets_detected == true
    msg := "Hardcoded secrets detected in codebase. Deployment blocked."
}

# Deny if authentication changes lack security review
deny contains msg if {
    input.changes.auth_modified == true
    input.review.security_approved == false
    msg := "Authentication changes require security team approval."
}

# Deny if encryption changes lack security review
deny contains msg if {
    input.changes.crypto_modified == true
    input.review.security_approved == false
    msg := "Cryptographic changes require security team approval."
}

# Deny if SQL injection patterns detected
deny contains msg if {
    input.scan.sql_injection_risks[_]
    msg := sprintf("SQL injection risk detected in %s", [
        input.scan.sql_injection_risks[_].file
    ])
}

# Deny if command injection patterns detected
deny contains msg if {
    input.scan.command_injection_risks[_]
    msg := sprintf("Command injection risk detected in %s", [
        input.scan.command_injection_risks[_].file
    ])
}

# Warning rules - these don't block but are logged

warning contains msg if {
    input.dependencies[_].cves[_].severity == "HIGH"
    msg := sprintf("High severity CVE in dependency %s: %s", [
        input.dependencies[_].name,
        input.dependencies[_].cves[_].id
    ])
}

warning contains msg if {
    input.scan.outdated_dependencies[_]
    msg := sprintf("Outdated dependency: %s", [
        input.scan.outdated_dependencies[_].name
    ])
}
```

## Deployment Policy

### deployment.rego

```rego
package cicd.deployment

import future.keywords.if

default allow := false

allow if {
    not deny
    all_gates_passed
}

# All required gates must pass
all_gates_passed if {
    input.gates.unit_tests == "passed"
    input.gates.integration_tests == "passed"
    input.gates.security_scan == "passed"
    input.gates.code_review == "approved"
}

# Deny deployment to production without canary
deny contains msg if {
    input.deployment.environment == "production"
    input.deployment.canary_enabled == false
    input.changes.risk_level == "high"
    msg := "High-risk changes require canary deployment to production."
}

# Deny deployment during change freeze
deny contains msg if {
    input.deployment.environment == "production"
    input.change_freeze.active == true
    not input.change_freeze.exception_granted
    msg := sprintf("Change freeze active: %s. No deployments allowed.", [
        input.change_freeze.reason
    ])
}

# Deny deployment without required approvals
deny contains msg if {
    count(input.review.approvals) < input.deployment.min_approvals
    msg := sprintf("Insufficient approvals: %d required, %d provided", [
        input.deployment.min_approvals,
        count(input.review.approvals)
    ])
}

# Deny deployment if previous deployment failed recently
deny contains msg if {
    input.deployment.environment == "production"
    input.recent_deployments[_].status == "failed"
    time.now_ns() - time.parse_rfc3339_ns(input.recent_deployments[_].timestamp) < 3600000000000
    msg := "Recent deployment failure detected. Wait 1 hour before retry."
}
```

## Quality Policy

### quality.rego

```rego
package cicd.quality

import future.keywords.if

default allow := false

allow if {
    not deny
}

# Deny if test coverage below threshold
deny contains msg if {
    input.coverage.line_coverage < input.thresholds.min_line_coverage
    msg := sprintf("Line coverage %.1f%% below threshold %.1f%%", [
        input.coverage.line_coverage,
        input.thresholds.min_line_coverage
    ])
}

# Deny if new code lacks tests
deny contains msg if {
    input.changes.new_lines > 50
    input.changes.new_test_lines == 0
    msg := sprintf("New code (%d lines) requires tests", [input.changes.new_lines])
}

# Deny if complexity exceeds threshold
deny contains msg if {
    input.metrics.cyclomatic_complexity > input.thresholds.max_complexity
    msg := sprintf("Cyclomatic complexity %d exceeds threshold %d", [
        input.metrics.cyclomatic_complexity,
        input.thresholds.max_complexity
    ])
}

# Deny if TODO/FIXME count exceeds limit
deny contains msg if {
    input.metrics.todo_count > input.thresholds.max_todos
    msg := sprintf("Too many TODOs (%d). Max allowed: %d", [
        input.metrics.todo_count,
        input.thresholds.max_todos
    ])
}

# Warning for low coverage on critical paths
warning contains msg if {
    input.coverage.critical_path_coverage < 90
    msg := sprintf("Critical path coverage %.1f%% below 90%%", [
        input.coverage.critical_path_coverage
    ])
}
```

## Compliance Policy

### compliance.rego

```rego
package cicd.compliance

import future.keywords.if

default allow := false

allow if {
    not deny
}

# SOC 2 Requirements

# Deny if PII handling changes lack DPO review
deny contains msg if {
    input.changes.pii_modified == true
    input.review.dpo_approved == false
    msg := "PII handling changes require Data Protection Officer approval."
}

# Deny if data retention changes lack compliance review
deny contains msg if {
    input.changes.data_retention_modified == true
    input.review.compliance_approved == false
    msg := "Data retention changes require compliance team approval."
}

# ISO 27001 Requirements

# Deny if access control changes lack security review
deny contains msg if {
    input.changes.access_control_modified == true
    input.review.security_approved == false
    msg := "Access control changes require security team approval."
}

# Deny if audit logging is disabled
deny contains msg if {
    input.changes.audit_logging_disabled == true
    msg := "Audit logging cannot be disabled."
}

# GDPR Requirements

# Deny if data export functionality is removed
deny contains msg if {
    input.changes.data_export_removed == true
    msg := "Data export functionality (GDPR right to portability) cannot be removed."
}

# Deny if data deletion functionality is removed
deny contains msg if {
    input.changes.data_deletion_removed == true
    msg := "Data deletion functionality (GDPR right to erasure) cannot be removed."
}
```

## Input Context Schema

### pr-context.json

```json
{
  "pr_number": 1234,
  "repository": "org/repo",
  "author": "developer",
  "branch": "feature/new-auth",

  "changes": {
    "files": ["auth/login.ts", "auth/middleware.ts"],
    "new_lines": 150,
    "deleted_lines": 30,
    "new_test_lines": 80,
    "auth_modified": true,
    "crypto_modified": false,
    "pii_modified": false,
    "access_control_modified": true,
    "risk_level": "high"
  },

  "dependencies": [
    {
      "name": "lodash",
      "version": "4.17.21",
      "cves": []
    }
  ],

  "scan": {
    "secrets_detected": false,
    "sql_injection_risks": [],
    "command_injection_risks": [],
    "outdated_dependencies": []
  },

  "coverage": {
    "line_coverage": 85.5,
    "branch_coverage": 78.2,
    "critical_path_coverage": 92.0
  },

  "metrics": {
    "cyclomatic_complexity": 12,
    "todo_count": 3
  },

  "review": {
    "approvals": ["reviewer1", "reviewer2"],
    "security_approved": false,
    "dpo_approved": null,
    "compliance_approved": null
  },

  "gates": {
    "unit_tests": "passed",
    "integration_tests": "passed",
    "security_scan": "passed",
    "code_review": "pending"
  },

  "deployment": {
    "environment": "staging",
    "min_approvals": 2,
    "canary_enabled": false
  },

  "thresholds": {
    "min_line_coverage": 80,
    "max_complexity": 15,
    "max_todos": 10
  },

  "change_freeze": {
    "active": false
  },

  "recent_deployments": []
}
```

## Policy Evaluation

### CLI

```bash
# Evaluate single policy
opa eval -d policies/security.rego -i pr-context.json "data.cicd.security"

# Evaluate all policies
opa eval -d policies/ -i pr-context.json "data.cicd"

# Get all deny messages
opa eval -d policies/ -i pr-context.json "data.cicd.security.deny"

# Get all warnings
opa eval -d policies/ -i pr-context.json "data.cicd.security.warning"
```

### Integration

```python
import subprocess
import json

def evaluate_policies(context: dict) -> dict:
    """Evaluate OPA policies against PR context."""
    result = subprocess.run([
        "opa", "eval",
        "-d", "policies/",
        "-i", "/dev/stdin",
        "data.cicd"
    ], input=json.dumps(context), capture_output=True, text=True)

    evaluation = json.loads(result.stdout)

    return {
        "allow": evaluation.get("allow", False),
        "deny": evaluation.get("deny", []),
        "warning": evaluation.get("warning", [])
    }
```
